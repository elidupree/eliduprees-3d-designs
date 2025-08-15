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


def various_values(depth) -> List[CA]:
    results = []
    for l in [5, 20]:
        results.append(make_ca(b"a"*l))
    if depth > 0:
        lists = [[]]
        for l in range(0, 3):
            old_lists = lists
            lists = lists.copy()
            for l in old_lists:
                for v in various_values(depth - 1):
                    lists.append(l + [v])
        dicts = [{}]
        for l in range(0, 2):
            old_dicts = dicts
            dicts = dicts.copy()
            for d in old_dicts:
                for k in various_values(depth - 1):
                    for v in various_values(depth - 1):
                        if k not in d:
                            new = d.copy()
                            new[k] = v
                            dicts.append(new)
        results.extend(make_ca(x) for x in lists + dicts)
    return results

@test
def t4(store: KeyValueStore):
    keys = various_values(2)
    values = keys
    for k,v in zip(keys,values):
        store[k] = v
        assert (store[k] is v), f"failed at pass 1, {k} = {v}"
    for k,v in zip(keys,values):
        assert (store[k] is v), f"failed at pass 2, {k} = {v}"
    for k,v in zip(keys,values):
        del store[k]
        try:
            store[k]
            raise RuntimeError("should fail")
        except KeyError:
            pass
    values = keys[1:]+keys[:1]
    for k,v in zip(keys,values):
        store[k] = v
        assert (store[k] is v), f"failed at pass 3, {k} = {v}"
        assert (store[k] is not k), f"failed at pass 3.2, {k} = {v}"


if failures > 0:
    print(f"Finished with {failures} failures")
else:
    print("All passed!")