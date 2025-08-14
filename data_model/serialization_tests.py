import os
import traceback

import sqlite_store
from storage_api import KeyValueStore, make_ca, CA

db_file = "e3d_serialization_tests_db.db"
failures = 0
def cleanup():
    try:
        os.remove(db_file)
    except FileNotFoundError:
        pass

def test(fn):
    cleanup()
    print("running test" + fn.__name__)

    store = sqlite_store.SqliteStore(db_file)
    try:
        fn(store)
    except:
        global failures
        failures += 1
        traceback.print_exc()
    cleanup()

@test
def t1(store: KeyValueStore):
    pass

@test
def t2(store: KeyValueStore):
    a: CA = make_ca(b"a")
    b: CA = make_ca(b"b")
    store[a] = b
    assert (store[a] is b)

@test
def t3(store: KeyValueStore):
    a18 = make_ca(b"a"*18)
    a19 = make_ca(b"a"*19)
    a20 = make_ca(b"a"*20)
    b18 = make_ca(b"b"*18)
    b19 = make_ca(b"b"*19)
    b20 = make_ca(b"b"*20)
    store[a18] = b18
    assert (store[a18] == b18)
    store[a19] = b19
    assert (store[a19] == b19)
    store[a20] = b20
    assert (store[a18] == b18)
    assert (store[a19] == b19)
    assert (store[a20] == b20)

if failures > 0:
    print(f"Finished with {failures} failures")
else:
    print("All passed!")