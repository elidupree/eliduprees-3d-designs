"""

Our serialization format is literally just de-duplicated JSON, because anything else would be scope creep. If you want to represent any other object, just represent it as JSON somehow.

Serialized-objects that contain deduplicated objects represent the references as 21 base64 characters (126 bits), representing the ID of the target object.

Any object has 2 serializable forms: "serializable-value", which is the whole JSON-value of "the object but all subobjects are replaced with serializable-usages"; and "serializable-usage", which is either
* if the whole JSON-*string* of the object is smaller than that of an ID, the whole JSON-*value* of it;
* otherwise, a *string* that's 21 base64 characters of the siphash128 of the serializable-value.

Thus, when you're deserializing a container, you don't need a special marker to tell whether an inner string is a reference or not - you can just check how big it is.

We do extend JSON a little to allow arbitrary objects as keys, by using their serialized-usage as the key. (The client could technically write the strings there themselves, but this system needs to take responsibility for storing the referenced objects.) We also make objects __hash__ as their serialized-usage.

Clearly, we don't need deduplicated-storage for things smaller than an ID. For things as large as an ID, we store them in a SQLite database, which is primarily a mapping from IDs to values.

The database primarily acts as a key-value store, and also contains all subobjects of existing keys or values, with a reference count for each subobject. This file is not responsible for defining conventions around what you use the key-value store for; rather, this file merely provides an interface to a database, and representations of the stored objects.

This file's responsibilities include:
 * Defining classes for serialization and for the (immutable) JSON container types
 * Defining database transactions that are guaranteed to leave the database with valid reference counts

"""
import json
import os
import re
import sqlite3
from pathlib import Path
from weakref import WeakValueDictionary

from siphash import siphash_128
from base64 import b64encode
siphash_key = bytes.fromhex("78ca81054e1df045447cd7d48958de7d")

_raw_reference_length = 21
_serialized_reference_length = _raw_reference_length + 2

class Serializable:
    def __init__(self, *args, **kwargs):
        self._cached_serializable_usage = None
        self._cached_serializable_value = None
        self._cached_serialized_value = None
        self._cached_serialized_usage = None
        self._saved = False
        super().__init__(*args, **kwargs)

    def _serializable_value(self):
        return self
    
    def serializable_value(self):
        if self._cached_serializable_value is None:
            self._cached_serializable_value = self._serializable_value()
        return self._cached_serializable_value

    def serialized_value(self):
        if self._cached_serialized_value is None:
            self._cached_serialized_value = json.dumps(self.serializable_value())
        return self._cached_serialized_value

    def needs_indirection(self):
        return len(self.serialized_value()) >= _serialized_reference_length

    def serializable_usage(self):
        if self._cached_serializable_usage is None:
            if self.needs_indirection(self):
                self._cached_serializable_usage = b64encode(siphash_128(key=siphash_key, data=self.serialized_value().encode('ascii')))[:_raw_reference_length]
            else:
                self._cached_serializable_usage = self.serializable_value()
        return self._cached_serializable_usage

    def id(self):
        assert self.needs_indirection(), "shouldn't be calling Serializable.id() unless the object needs indirection"
        return self.serializable_usage()

    def serialized_usage(self):
        if self._cached_serialized_usage is None:
            self._cached_serialized_usage = self._serializable_usage()
        return self._serializable_usage()

    def serializable_subobjects(self):
        return []

    def __hash__(self):
        return hash(self.serialized_usage())



def forbidden_mutating_operation(*args, **kwargs):
    raise RuntimeError("Mutating an immutable (Serializable) collection")


class SerializableStr(Serializable, str):
    pass


class SerializableList(Serializable, list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i,e in enumerate(self):
            self[i] = make_serializable(e)
    # def __init__(self, items: typing.List[Serializable]):
    #     super().__init__(self)
    #     self.items = items

    def _serializable_value(self):
        return [x.serializable_usage() for x in self]

    def serializable_subobjects(self):
        return iter(self)

for method in re.finditer(r"[^, ]+", "__setattr__, __delattr__, __setitem__, __delitem__, __iadd__, __imul__, append, extend, insert, remove, pop, clear, sort, reverse"):
    setattr(SerializableList, method[0], forbidden_mutating_operation)


class SerializableDict(Serializable, dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        items = list(self.items())
        self.clear()
        for k,v in items:
            self[make_serializable(k)] = make_serializable(v)

    def _serializable_value(self):
        return {k.serialized_usage(): v.serializable_usage() for k,v in self.items()}

    def serializable_subobjects(self):
        yield from self.keys()
        yield from self.values()

for method in re.finditer(r"[^, ]+", "__setattr__, __delattr__, __setitem__, __delitem__, __ior__, clear, pop, popitem, setdefault"):
    setattr(SerializableDict, method[0], forbidden_mutating_operation)


_object_cache = WeakValueDictionary()

def _needs_indirection(x):
    return isinstance(x, Serializable) and x.needs_indirection()

def make_serializable(x):
    if type(x) in [type(None), bool, int, float] or isinstance(x, Serializable):
        s = x
    elif type(x) is str:
        s = SerializableStr(x)
    elif type(x) is list:
        s = SerializableList(x)
    elif type(x) is dict:
        s = SerializableDict(x)
    else:
        raise RuntimeError("tried to make unrecognized type serializable")

    if _needs_indirection(s):
        s = _object_cache.setdefault(s.id(), s)

    return s


def _serializable_usage(x):
    if _needs_indirection(x):
        return x.id()
    else:
        return x


def _store_referents_of_usage(cursor: sqlite3.Cursor, x: Serializable):
    if _needs_indirection(x):
        _store_value(x)

def _store_value(cursor: sqlite3.Cursor, x: Serializable):
    cursor.execute("UPDATE values_by_id SET reference_count = reference_count + 1 WHERE id = ?;", [id])
    results = cursor.fetchall()
    assert (len(results) <= 1), "ids are supposed to be unique"
    if len(results) == 0:
        # create the sub-objects first, so that there could never be a query that seized the containing object but not its sub-objects
        for y in x.serializable_subobjects():
            _store_referents_of_usage(cursor, y)
        # now create the main object … though hypothetically we could have raced with another store that also created it. In that case we also need to increase the reference count, so use an upsert here.
        cursor.execute("INSERT INTO values_by_id (id, value, reference_count) VALUES (:id, :value, 1) ON CONFLICT(id) DO UPDATE SET reference_count = reference_count + 1;", {"id":x.id(), "value":json.dumps(x)})
        results = cursor.fetchall()
        assert (len(results) == 1), "we created/updated exactly 1 value"



def _load_by_id(cursor: sqlite3.Cursor, id: str):
    try:
        return _object_cache[id]
    except KeyError:
        pass

    cursor.execute("SELECT value FROM values_by_id WHERE id = ?;", [id])
    results = cursor.fetchall()
    assert (len(results) <= 1), "ids are supposed to be unique"
    assert (len(results) == 1), "any caller of _load_by_id is supposed to have seen a reference that keeps the target alive, so it's an error for the target to be missing. Atomicity of SQLite read-transactions guarantees that there won't be any problems with racing with a deletion. (We expect that _load_by_id isn't called during any write-transactions; unfortunately I don't see the sqlite3 module providing a way to assert that here.)"
    serialized_value_string, = results[0]
    # `_load_value` takes care of making an entry in the object cache, via `make_serializable`
    return _load_value(json.loads(serialized_value_string))

def _load_usage(cursor: sqlite3.Cursor, x):
    if type(x) is str and len(x) >= _raw_reference_length:
        assert (len(x) == _raw_reference_length), "a usage is never a string bigger than an ID"
        return _load_by_id(cursor, x)
    else:
        return x

def _load_value(cursor: sqlite3.Cursor, x):
    if type(x) is list:
        x = [_load_usage(cursor, e) for e in x]
    if type(x) is dict:
        x = {_load_usage(cursor, json.loads(k)): _load_usage(cursor, v) for k,v in x.items()}
    return make_serializable(x)


def _drop_reference_to_id(cursor: sqlite3.Cursor, id):
    cursor.execute("UPDATE values_by_id SET reference_count = reference_count - 1 WHERE id = ? RETURNING reference_count;", [id])
    results = cursor.fetchall()
    assert (len(results) <= 1), "ids are supposed to be unique"
    assert (len(results) == 1), "at the time we call _drop_reference_to_id, the reference we are removing is supposed to be holding the target alive, so it's an error for the target to be missing."
    reference_count, = results[0]
    if reference_count == 0:
        cursor.execute("DELETE values_by_id WHERE reference_count = 0 AND id = ? RETURNING value;", [id])
        results = cursor.fetchall()

        assert (len(results) <= 1), "ids are supposed to be unique"
        # hypothetically we could've raced with another call that recreates the object with the same id; in that case, the other call may assume that we didn't get around to dropping this one (the other call, having found an existing entry and incremented its reference count, is done, regardless of whether that reference count was already >=1).
        if len(results) == 1:
            value_string, = results[0]

            _drop_references_in_value(cursor, json.loads(value_string))

def _drop_references_in_usage(cursor: sqlite3.Cursor, x):
    if type(x) is str and len(x) >= 21:
        assert (len(x) == _raw_reference_length), "a usage is never a string bigger than an ID"
        _drop_reference_to_id(cursor, x)

def _drop_references_in_value(cursor: sqlite3.Cursor, x):
    if type(x) is list:
        for e in x:
            _drop_references_in_usage(cursor, e)
    if type(x) is dict:
        for k, v in x.items():
            _drop_references_in_usage(cursor, json.loads(k))
            _drop_references_in_usage(cursor, v)


# def until_not_rolled_back(operation):
#     for _ in range(100):
#         try:
#             cursor = _database_connection().cursor(isolation_level="DEFERRED")
#             operation(cursor)
#             cursor.commit()
#         except sqlite3.OperationalError as e:
#             if e.sqlite_errorname != "SQLITE_CONSTRAINT":
#                 raise
#     raise RuntimeError("DB op failed 100 times, there's probably a bug")

# def _delete_key(key):
#     until_not_rolled_back(lambda cursor: _delete_key_optimistic(cursor, key))

class KeyValueStore:
    def __init__(self, database_file):
        self._database_connection = None
        self._database_file = database_file

    def _connection(self):
        if self._database_connection is None:
            self._database_connection = sqlite3.connect(self._database_file)
            cursor = self._database_connection.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS values_by_id (id TEXT PRIMARY KEY, value TEXT);")
            cursor.execute("CREATE TABLE IF NOT EXISTS key_value_entries (key TEXT PRIMARY KEY, value TEXT);")
        return self._database_connection


    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __getitem__(self, key):
        cursor = self._connection().cursor()
        cursor.execute("SELECT value FROM key_value_entries WHERE key = ?;", [json.dumps(_serializable_usage(key))])
        results = cursor.fetchall()
        assert (len(results) <= 1), "keys are supposed to be unique"
        if len(results) == 0:
            raise KeyError(key)
        value_usage_string, = results[0]
        return _load_usage(cursor, json.loads(value_usage_string))

    def __delitem__(self, key):
        cursor = self._connection().cursor()
        key_usage = _serializable_usage(key)
        cursor.execute("DELETE key_value_entries WHERE key = ? RETURNING value;", [json.dumps(key_usage)])
        results = cursor.fetchall()
        assert (len(results) <= 1), "keys are supposed to be unique"
        if len(results) == 1:
            value_usage_string, = results[0]
            _drop_references_in_usage(key_usage)
            _drop_references_in_usage(json.loads(value_usage_string))
        self._connection().commit()

    def __setitem__(self, key, value):
        cursor = self._connection().cursor()
        key_usage = _serializable_usage(key)
        value_usage = _serializable_usage(value)
        _store_referents_of_usage(cursor, key_usage)
        _store_referents_of_usage(cursor, value_usage)
        cursor.execute("INSERT OR REPLACE INTO key_value_entries (key, value) VALUES (?, ?);", [json.dumps(key_usage), json.dumps(value_usage)])
        self._connection().commit()


_default_database_file = Path(os.environ["EPYOCCT_CACHE_DIR"])/"data.db"
store = KeyValueStore(_default_database_file)

