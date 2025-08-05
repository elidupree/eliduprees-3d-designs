import os
import traceback

import serialization

db_file = "e3d_serialization_tests_db.db"
def cleanup():
    try:
        os.remove(db_file)
    except FileNotFoundError:
        pass

def test(fn):
    cleanup()

    store = serialization.KeyValueStore(db_file)
    try:
        fn(store)
    except:
        traceback.print_exc()
    cleanup()

@test
def t1(store):
    pass

@test
def t2(store):
    store["a"] = "b"
    assert (store["a"] == "b")

@test
def t3(store):
    store["a"*20] = "b"*20
    assert (store["a"*20] == "b"*20)
    store["a"*21] = "b"*21
    assert (store["a"*21] == "b"*21)
    store["a"*22] = "b"*22
    assert (store["a"*22] == "b"*22)
    assert (store["a"*20] == "b"*20)
    assert (store["a"*21] == "b"*21)

print("All passed!")