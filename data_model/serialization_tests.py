import cProfile
import os
import traceback
from typing import List

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
    print("running test " + fn.__name__)

    store = sqlite_store.SqliteStore(db_file)
    try:
        cProfile.runctx("fn(store)", globals(), locals())
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
    assert (store[a] is not a)
    try:
        store[b]
        raise RuntimeError("should fail")
    except KeyError:
        pass


@test
def t3(store: KeyValueStore):
    for l in range(15, 21):
        aaa = make_ca(b"a"*l)
        bbb = make_ca(b"b"*l)
        store[aaa] = bbb
        assert (store[aaa] is bbb), f"failed at pass 1, length {l}"
    for l in range(15, 21):
        aaa = make_ca(b"a"*l)
        bbb = make_ca(b"b"*l)
        assert (store[aaa] is bbb), f"failed at pass 2, length {l}"


various_values = [[make_ca(b"a"*l) for l in [5,20]]]
for depth in range(2):
    lists = [[]]
    for l in range(0, 2):
        old_lists = lists
        lists = lists.copy()
        for l in old_lists:
            for v in various_values[-1]:
                lists.append(l + [v])
    dicts = [{}]
    for l in range(0, 1):
        old_dicts = dicts
        dicts = dicts.copy()
        for d in old_dicts:
            for k in various_values[-1]:
                for v in various_values[-1]:
                    if k not in d:
                        new = d.copy()
                        new[k] = v
                        dicts.append(new)
    various_values.append(various_values[-1] + [make_ca(x) for x in lists + dicts])
print([len(v) for v in various_values])

@test
def tOneTransaction(store: KeyValueStore):
    value = make_ca(various_values[2])
    store[value] = value
    assert (store[value] is value)


@test
def t4(store: KeyValueStore):
    keys = various_values[2]
    values = keys
    for k,v in zip(keys,values):
        store[k] = v
        assert (store[k] is v), f"failed at pass 1, {k} = {v}"
    print("  done with pass 1")
    for k,v in zip(keys,values):
        assert (store[k] is v), f"failed at pass 2, {k} = {v}"
    print("  done with pass 2")
    for k,v in zip(keys,values):
        del store[k]
        try:
            store[k]
            raise RuntimeError("should fail")
        except KeyError:
            pass
    print("  done with pass 3")
    values = keys[1:]+keys[:1]
    for k,v in zip(keys,values):
        store[k] = v
        assert (store[k] is v), f"failed at pass 3, {k} = {v}"
        assert (store[k] is not k), f"failed at pass 3.2, {k} = {v}"
    print("  done with pass 4")


if failures > 0:
    print(f"Finished with {failures} failures")
else:
    print("All passed!")