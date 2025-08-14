"""


Our underlying storage format is basically just deduplicated bencode, because anything else would be scope creep. (Actually a subset of bencode – we don't even care about integers.) Conceptually, the only "values" are
* Arbitrary byte-strings
* Lists of values
* Unordered maps of value -> value

(To represent any other type, you define a conversion between this format and that type)

…and, for incremental builds and such, we would like to store any number of intermediate values in space only linear in the time you spent constructing them, i.e. deduplicated. It's most convenient to do this using content-addressing.

So, we say that each value has an "id", with an upper bound on size.
* The serialized form of a bytestring is just a bencode bytestring
* The serialized form of a list or map is a bencode list or map *of ids*

Since bencode provides a unique binary representation of each value, we can hash the serialized form of any value to get a 16-byte hash unique to that value – which can be represented as a 19-byte bencode value (`16:` plus the 16 bytes). For a little more optimization, we then say: for any value which serializes *smaller* than 19 bytes, its id is just itself; for any other value, its id is such a 16-byte bytestring. (That way, it isn't wasteful to have a bunch of nested small lists.)

Because the interesting part about these values is that they are content-addressed, we call them "content-addressed values", or "CA" for short. CA values also __eq__ and __hash__ by the serialized form of their id.

Here, we define several interfaces for handling this kind of data:
* Construction of values from Python code, which is interned.
* Backends, which store reference-counted DAGs of such data.
* Conversion between CA values and typed objects.

"""
import re
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Any, Dict, Mapping, Union, Iterable
from weakref import WeakValueDictionary

import bencode_rs
from siphash import siphash_128

hash_id_byte_length = 16
hash_id_bencode_byte_length = hash_id_byte_length + len(f"{hash_id_byte_length}:")

# random data generated for this use
siphash_key = bytes.fromhex("78ca81054e1df045447cd7d48958de7d")


class CA(ABC):
    _id_cache: Optional["CA"]
    raw_form: Union[bytes, list, dict]
    serialized: bytes

    def __init__(self):
        self._id_cache = None

    def needs_indirection(self) -> bool:
        return len(self.serialized) >= hash_id_bencode_byte_length

    def id(self) -> "CA":
        if self._id_cache is None:
            if self.needs_indirection():
                self._id_cache = CAByteString(siphash_128(key=siphash_key, data=self.serialized))
            else:
                self._id_cache = self
        return self._id_cache

    @abstractmethod
    def children(self):
        return []

    def __eq__(self, other: "CA"):
        return self.id().serialized == other.id().serialized

    def __hash__(self):
        return hash(self.id().serialized)


def forbidden_mutating_operation(*args, **kwargs):
    raise RuntimeError("Mutating an immutable (CA) collection")


class CAByteString(CA):
    def __init__(self, *args, **kwargs):
        self.raw_form = bytes(*args,**kwargs)
        self.serialized = bencode_rs.bencode(self.raw_form)
        CA.__init__(self)

    def children(self):
        return []

    def __getattr__(self, item):
        return self.raw_form.item



class CAList(CA, list):
    def __init__(self, *args, **kwargs):
        list.__init__(self,*args,**kwargs)
        for e in self:
            assert isinstance(e, CA)
        self.raw_form = [e.raw_form for e in self]
        self.serialized = bencode_rs.bencode([e.id().raw_form for e in self])
        CA.__init__(self)

    def children(self):
        yield from self


for method in re.finditer(r"[^, ]+", "__setattr__, __delattr__, __setitem__, __delitem__, __iadd__, __imul__, append, extend, insert, remove, pop, clear, sort, reverse"):
    setattr(CAList, method[0], forbidden_mutating_operation)


class CADict(CA, dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self,*args,**kwargs)
        for k,v in self.items():
            assert isinstance(k, CA)
            assert isinstance(v, CA)
        self.raw_form = {k: v for k,v in self.items()}
        self.serialized = bencode_rs.bencode({k.id().raw_form: v.id().raw_form for k,v in self.items()})
        CA.__init__(self)

    def children(self):
        yield from self.keys()
        yield from self.values()


for method in re.finditer(r"[^, ]+", "__setattr__, __delattr__, __setitem__, __delitem__, __ior__, clear, pop, popitem, setdefault"):
    setattr(CADict, method[0], forbidden_mutating_operation)


_object_cache = WeakValueDictionary()


def interned_ca(x: CA):
    return _object_cache.setdefault(x.id(), x)


def already_interned_ca_by_id(id: CA) -> CA:
    return _object_cache[id]


def make_ca(x: Union[CA, bytes, Iterable[CA], Mapping[CA,CA]]):
    if isinstance(x, CA):
        y = x
    elif type(x) is bytes:
        y = CAByteString(x)
    elif isinstance(x, Mapping):
        y = CADict(x)
    elif isinstance(x, Iterable):
        y = CAList(x)
    else:
        raise RuntimeError("wrong type passed to make_ca")
    return interned_ca(y)


class KeyValueStore(ABC):
    @abstractmethod
    def __getitem__(self, key: CA) -> CA:
        pass

    @abstractmethod
    def __setitem__(self, key: CA, value: CA):
        pass

    @abstractmethod
    def __delitem__(self, key: CA):
        pass

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default


# TypeRepresentation = None
# class TypeRepresentation(ABC):
#     @abstractmethod
#     def serialize(self, x: Object) -> bytes:
#         pass
#
#     @abstractmethod
#     def deserialize(self, data: bytes, subobjects: List[Object]) -> Object:
#         pass
#
#     @abstractmethod
#     def object_references(self, x: Object) -> List[TypeRepresentation, Object]:
#         pass
#
#     @abstractmethod
#     def data_references(self, data: bytes) -> List[TypeRepresentation, Tuple[HashId]]:
#         pass


# _object_cache = WeakValueDictionary()
#
#
# def _get_subobject(backend: Backend, t: TypeRepresentation, key: HashId) -> Object:
#     try:
#         return _object_cache[(t,key)]
#     except KeyError:
#         pass
#
#     data = backend.get_subobject_data(key)
#     subobjects = [_get_subobject(backend, u, y) for u,y in t.data_references(data)]
#     x = t.deserialize(data, subobjects)
#     _object_cache[(t, key)] = x
#     return x
#
#
# def _delete_subobject(backend: Backend, t: TypeRepresentation, key: HashId):
#     if backend.delete_subobject_data(key):
#         data = backend.get_subobject_data(key)
#         for u,y in t.data_references(data):
#             _delete_subobject(backend, u, y)
#
#
# def _store_subobject(backend: Backend, t: TypeRepresentation, x: Object):
#     data = t.serialize(x)
#     if not backend.store_subobject_data(hash(data), data):
#         for u,y in t.object_references(x):
#             _store_subobject(backend, u, y)
