import os
import sqlite3
from pathlib import Path

from bencode_rs import bdecode

from storage_api import KeyValueStore, CA, already_interned_ca_by_id, make_ca, CAList, CAByteString, CADict


def _store_children(cursor: sqlite3.Cursor, x: CA):
    for child in x.children():
        cursor.execute("INSERT INTO child_references (parent_id, child_id) VALUES (:parent_id, :child_id) ON CONFLICT(id) IGNORE RETURNING 1", {"parent_id":x.id().serialized, "child_id":child.id().serialized})
        results = cursor.fetchall()
        assert (len(results) <= 1), "reference entries are supposed to be unique"
        if len(results) > 0:
            _store_value(cursor, child)


def _store_value(cursor: sqlite3.Cursor, x: CA):
    cursor.execute("INSERT INTO values_by_id (id, value) VALUES (:id, :value) ON CONFLICT(id) DO NOTHING RETURNING 1", {"id":x.id().serialized, "value":x.serialized})
    results = cursor.fetchall()
    assert (len(results) <= 1), "ids are supposed to be unique"
    if len(results) > 0:
        _store_children(cursor, x)


def _load_by_id(cursor: sqlite3.Cursor, id: CA) -> CA:
    try:
        return already_interned_ca_by_id(id)
    except KeyError:
        pass

    cursor.execute("SELECT value FROM values_by_id WHERE id = ?;", [id.serialized])
    results = cursor.fetchall()
    assert (len(results) <= 1), "ids are supposed to be unique"
    assert (len(results) == 1), f"missing value for key `{id}`. any caller of _load_by_id is supposed to have seen a reference that keeps the target alive, so it's an error for the target to be missing. Atomicity of SQLite read-transactions guarantees that there won't be any problems with racing with a deletion. (We expect that _load_by_id isn't called during any write-transactions; unfortunately I don't see the sqlite3 module providing a way to assert that here.)"

    serialized_value, = results[0]
    deserialized = bdecode(serialized_value)

    if type(deserialized) is bytes:
        result = CAByteString(deserialized)
    elif type(deserialized) is list:
        result = CAList(_load_by_id(cursor, e) for e in deserialized)
    elif type(deserialized) is dict:
        result = CADict((_load_by_id(cursor, k), _load_by_id(cursor, v)) for k, v in deserialized.items())
    else:
        raise RuntimeError("bdecode returned wrong type when loading bencode value (somehow there was an integer in the database?)")

    # make_ca also interns the result
    return make_ca(result)


def _check_for_orphan(cursor: sqlite3.Cursor, serialized_id: bytes):
    cursor.execute("SELECT EXISTS (select child_id from child_references where child_id = :id}) OR EXISTS (select key_id from key_value_entries where key_id = :id}) OR EXISTS (select value_id from key_value_entries where value_id = :id});", {"id":serialized_id})
    results = cursor.fetchall()
    assert (len(results) == 1), "query should have one result"
    is_referenced, = results[0]
    if is_referenced == 0:
        cursor.execute("DELETE values_by_id id = ? RETURNING value;", [id])
        cursor.execute("DELETE child_references WHERE id = ? RETURNING value;", [id])
        results = cursor.fetchall()

        assert (len(results) == 1), "supposed to delete one thing"

        serialized_value, = results[0]
        deserialized = bdecode(serialized_value)
        child_ids = []
        if type(deserialized) is list:
            child_ids = deserialized
        elif type(deserialized) is dict:
            child_ids = list(deserialized.keys()) + list(deserialized.values())
        for child_id in child_ids:
            _check_for_orphan(child_id)


class SqliteStore(KeyValueStore):
    def __init__(self, database_file):
        self._database_connection = None
        self._database_file = database_file

    def _connection(self):
        if self._database_connection is None:
            self._database_connection = sqlite3.connect(self._database_file)
            cursor = self._database_connection.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS child_references (parent BLOB, child BLOB, PRIMARY KEY (parent, child));")
            cursor.execute("CREATE TABLE IF NOT EXISTS values_by_id (id BLOB PRIMARY KEY, value BLOB);")
            cursor.execute("CREATE TABLE IF NOT EXISTS key_value_entries (key_id BLOB PRIMARY KEY, value_id BLOB);")
            cursor.execute("CREATE INDEX IF NOT EXISTS reference_parent ON child_references(parent);")
            cursor.execute("CREATE INDEX IF NOT EXISTS reference_child ON child_references(child);")
            cursor.execute("CREATE INDEX IF NOT EXISTS used_as_value ON key_value_entries(value_id);")
        return self._database_connection

    def __getitem__(self, key: CA):
        cursor = self._connection().cursor()
        cursor.execute("SELECT value_id FROM key_value_entries WHERE key_id = ?;", [key.id().serialized])
        results = cursor.fetchall()
        assert (len(results) <= 1), "keys are supposed to be unique"
        if len(results) == 0:
            raise KeyError(key)
        serialized_value_id, = results[0]
        return _load_by_id(cursor, make_ca(bdecode(serialized_value_id)))

    def __delitem__(self, key: CA):
        cursor = self._connection().cursor()
        cursor.execute("DELETE key_value_entries WHERE key = ? RETURNING value;", [key.id().serialized])
        results = cursor.fetchall()
        assert (len(results) <= 1), "keys are supposed to be unique"
        if len(results) == 1:
            serialized_value_id, = results[0]
            _check_for_orphan(cursor, key.id().serialized)
            _check_for_orphan(cursor, serialized_value_id)
        self._connection().commit()

    def __setitem__(self, key: CA, value: CA):
        cursor = self._connection().cursor()
        _store_value(cursor, key)
        _store_value(cursor, value)
        cursor.execute("INSERT OR REPLACE INTO key_value_entries (key_id, value_id) VALUES (?, ?);", [key.id().serialized, value.id().serialized])
        self._connection().commit()


if "EPYOCCT_CACHE_DIR" in os.environ:
    _default_database_file = Path(os.environ["EPYOCCT_CACHE_DIR"])/"data.db"
    store = SqliteStore(_default_database_file)
