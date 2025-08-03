"""

Our serialization format is literally just de-duplicated JSON, because anything else would be scope creep. If you want to represent any other object, just represent it as JSON somehow.

Serialized-objects that contain deduplicated objects represent the references as 21 base64 characters (126 bits).

Any object has 2 serializable forms: "serializable-value", which is the whole JSON form of "the object but all subobjects are replaced with serializable-usages"; and "serializable-usage", which is either
* if the whole JSON form of the object is smaller than that of a reference, the whole JSON form;
* otherwise, a string that's 21 base64 characters of the siphash128 of the serializable-value.

Thus, when you're deserializing a container, you don't need a special marker to tell whether an inner string is a reference or not - you can just check how big it is.

Clearly, we don't need deduplicated-storage for things smaller than a reference. For things as large as a reference, we store them in a SQLite database, which is primarily a mapping from references to values.

The database also includes a reference count for each stored object. The database also contains mutable cells that map one value to another - typically used as a cache mapping a thunk to its output. These "mutable cell" values are the sole persistent objects that won't be garbage-collected, and hold entries in reference-counts. This file is not responsible for defining conventions around what you use the mutable cells for; rather, this file merely provides an interface to a database, and representations of the stored objects.

This file's responsibilities include:
 * Defining classes for serialization and for the JSON container typesresponsibility is to enforce per-key read-write locking of the mutable cells: you can't change or delete one while any process is holding a reference to it. (It's intended for users to load values lazily, so

"""
import json
import os
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
    def __init__(self):
        self._cached_serializable_usage = None
        self._cached_serializable_value = None
        self._cached_serialized_value = None
        self._cached_serialized_usage = None
        self._saved = False

    def _serializable_value(self):
        return self
    
    def serializable_value(self):
        if self._cached_serializable_value is None:
            self._cached_serializable_value = self._serializable_value()
        return self._cached_serializable_value

    def serialized_value(self):
        if self._cached_serialized_value is None:
            self._cached_serialized_value = self._serializable_value()
        return self._serializable_value()

    def serializable_usage(self):
        if self._cached_serializable_usage is None:
            sv = self.serialized_value()
            if len(sv) < 21+2:
                self._cached_serializable_usage = self.serializable_value()
            else:
                self._cached_serializable_usage = b64encode(siphash_128(key=siphash_key, data=sv.encode('ascii')))[:21]
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


def remove_global_persistent_map_entry(key: Serializable):

def save_global_persistent_map_entry(key: Serializable, value: Serializable):
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




class SerializableList(Serializable, list):
    # def __init__(self, items: typing.List[Serializable]):
    #     super().__init__(self)
    #     self.items = items

    def _serializable_value(self):
        return [x.serializable_usage() for x in self]



def serializable_value(x):
    if type(x) is list:
        return [serializable_usage(y) for y in x]
    if type(x) is dict:
        return {serializable_usage(k): serializable_usage(v) for k,v in x.items()}
    return x

siphash_key = bytes.fromhex("78ca81054e1df045447cd7d48958de7d")
def hashid_of_serializable_value(x):
    return siphash_128(key=siphash_key, data=json.dumps(x))

def serializable_usage(x):
    use_
    # don't json.dumps giant objects; hardcode the fact that
    if (type(x) is list or type(x) is dict):
        return {serializable_usage(k): serializable_usage(v) for k,v in x.items()}
    jsonstr = json.dumps(x)