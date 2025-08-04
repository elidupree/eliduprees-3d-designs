"""

Our serialization format is literally just de-duplicated JSON, because anything else would be scope creep. If you want to represent any other object, just represent it as JSON somehow.

Serialized-objects that contain deduplicated objects represent the references as 21 base64 characters (126 bits).

Any object has 2 serializable forms: "serializable-value", which is the whole JSON-value of "the object but all subobjects are replaced with serializable-usages"; and "serializable-usage", which is either
* if the whole JSON-*string* of the object is smaller than that of a reference, the whole JSON-*value* of it;
* otherwise, a *string* that's 21 base64 characters of the siphash128 of the serializable-value.

Thus, when you're deserializing a container, you don't need a special marker to tell whether an inner string is a reference or not - you can just check how big it is.

We do extend JSON a little to allow arbitrary objects as keys, by using their serialized-usage as the key. (The client could technically write the strings there themselves, but this system needs to take responsibility for storing the referenced objects.) We also make objects __hash__ as their serialized-usage.

Clearly, we don't need deduplicated-storage for things smaller than a reference. For things as large as a reference, we store them in a SQLite database, which is primarily a mapping from references to values.

The database primarily acts as a key-value store, and also contains all subobjects of existing keys or values, with a reference count for each subobject. This file is not responsible for defining conventions around what you use the key-value store for; rather, this file merely provides an interface to a database, and representations of the stored objects.

This file's responsibilities include:
 * Defining classes for serialization and for the (immutable) JSON container types
 * Defining database transactions that are guaranteed to leave the database with valid reference counts

"""
import json
import os
import re
import sqlite3
import typing
from pathlib import Path

from siphash import siphash_128
from base64 import b64encode
siphash_key = bytes.fromhex("78ca81054e1df045447cd7d48958de7d")

_database_file = Path(os.environ["EPYOCCT_CACHE_DIR"])/"data.db"
_stored_database_connection = None
def _database_connection():
    global _stored_database_connection
    if _stored_database_connection is None:
        _stored_database_connection = sqlite3.connect(_database_file)

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
        return len(self.serialized_value()) >= 21+2

    def serializable_usage(self):
        if self._cached_serializable_usage is None:
            if self.needs_indirection(self):
                self._cached_serializable_usage = b64encode(siphash_128(key=siphash_key, data=self.serialized_value().encode('ascii')))[:21]
            else:
                self._cached_serializable_usage = self.serializable_value()
        return self._cached_serializable_usage

    def serialized_usage(self):
        if self._cached_serialized_usage is None:
            self._cached_serialized_usage = self._serializable_usage()
        return self._serializable_usage()

    def serializable_subobjects(self):
        return []

    def add_unsaved_subobjects_including_self(self, objects):
        if self._saved is False and self not in objects:
            objects.add(self)

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
    setattr(SerializableList, method, forbidden_mutating_operation)


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
    setattr(SerializableDict, method, forbidden_mutating_operation)


_object_cache = {}

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

    if isinstance(s, Serializable):
        s = _object_cache.setdefault(s.serialized_usage(), s)

    return s


def _serialized_usage(x):
    if isinstance(x, Serializable):
        return x.serialized_usage()
    else:
        return json.dumps(x)

def _needs_indirection(x):
    return isinstance(x, Serializable) and x.needs_indirection()


def _store_referents_of_usage(cursor: sqlite3.Cursor, x: Serializable):
    if _needs_indirection(x):
        _store_value(x)

def _store_value(cursor: sqlite3.Cursor, x: Serializable):
    if todo_database_store(x.serializable_usage(), x):
        for y in x.serializable_subobjects():
            if _needs_indirection(y):
                _store_value(cursor, y)


def _load_referent(cursor: sqlite3.Cursor, reference):
    query_result = TODO
    return _load_value(cursor, json.loads(query_result))

def _load_usage(cursor: sqlite3.Cursor, x):
    if type(x) is str and len(x) >= 21:
        return _load_referent(cursor, x)
    else:
        return x

def _load_value(cursor: sqlite3.Cursor, x):
    if type(x) is list:
        x = [_load_usage(cursor, e) for e in x]
    if type(x) is dict:
        x = {_load_usage(cursor, json.loads(k)): _load_usage(cursor, v)} for k,v in x.items()}
    return make_serializable(x)


def _remove_referent(cursor: sqlite3.Cursor, reference):
    if query_result = todo_database_remove(reference):
        _remove_value(cursor, json.loads(query_result))

def _remove_referents_of_usage(cursor: sqlite3.Cursor, x):
    if type(x) is str and len(x) >= 21:
        _remove_referent(cursor, x)

def _remove_value(cursor: sqlite3.Cursor, x):
    if type(x) is list:
        for e in x:
            _remove_referents_of_usage(cursor, e)
    if type(x) is dict:
        for k, v in x.items():
            _remove_referents_of_usage(cursor, json.loads(k))
            _remove_referents_of_usage(cursor, v)


def until_not_rolled_back(operation):
    for _ in range(100):
        try:
            cursor = _database_connection().cursor(isolation_level="DEFERRED")
            operation(cursor)
            cursor.commit()
        except sqlite3.OperationalError as e:
            if e.sqlite_errorname != "SQLITE_CONSTRAINT":
                raise
    raise RuntimeError("DB op failed 100 times, there's probably a bug")

def _remove_key_optimistic(cursor: sqlite3.Cursor, key):
    value_usage = todo_database_remove(_serialized_usage(key))
    _remove_referents_of_usage(json.loads(value_usage))

def _remove_key(key):
    until_not_rolled_back(lambda cursor: _remove_key_optimistic(cursor, key))

def _set_key_value_optimistic(cursor: sqlite3.Cursor, key, value):
    # store the key-value entry itself, _serialized_usage(key) _serialized_usage(value)
    _store_referents_of_usage(cursor, key)
    _store_referents_of_usage(cursor, value)


def _set_key_value(key, value):
    until_not_rolled_back(lambda cursor: _set_key_value_optimistic(cursor, key, value)

    remove_global_persistent_map_entry(key)
    cursor = _database_connection().cursor(isolation_level="DEFERRED")
    new_saved_objects_by_id = {}
    new_saved_parentages = set()
    stack = [key, value]
    # this MAY do unnecessary work if this data is already in the database and the present process just hasn't loaded it,
    # but that's not important and also handling it would make the transactions more complicated because
    # the present process wouldn't have a guarantee that that stuff wouldn't be deleted while it was working.
    while stack:
        x = stack.pop()
        if not x.is_saved() and x not in new_saved_objects_by_id:
            for y in x.serializable_subobjects():
                new_saved_parentages.add((x, y))
                stack.append(y)
    cursor.execute("INSERT INTO global_map VALUES (?, ?)", [(key.serialized_usage(), value.serialized_usage())])
    cursor.execute("INSERT INTO objects_by_id VALUES (?, ?)", new_saved_objects_by_id.items())
    cursor.execute("INSERT INTO parentages (parent, child) VALUES (?, ?)", new_saved_parentages)
    cursor.commit()