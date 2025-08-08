"""


Our underlying storage format is basically just deduplicated bencode, because anything else would be scope creep. (Actually a subset of bencode – we don't even care about integers.) Conceptually, the only "values" are
* Arbitrary byte-strings
* Lists of values
* Unordered maps of value -> value

(To represent any other type, you define a conversion between this format and that type)



(TODO: fix this explanation so it doesn't say it hashes the "usual" form, only the flattened one)
De-duplication is done by content-addressing: Since bencode provides a unique binary representation of each value, we can hash that unique binary representation to get a 16-byte unique id for each value - which can be represented as an 19-byte bencode value (`16:` plus the data). We then say: the "id" of any value smaller than 19 bytes of bencode is just itself; the "id" of any 19-byte-or-larger bencode value is such a hash, as a bytestring. (Note that this means an id's id might be a different bytestring; this isn't a problem, but don't get confused about it.) When you actually serialize (or hash!) a list or map, all *sub-values* as large as 19 bytes are replaced by byte-strings containing their id. We call this the "flattened" form.

Because the interesting part about these values is that they are content-addressed, we call them "content-addressed values", or "CA" for short.

Here, we define several interfaces for handling this kind of data:
* Construction of values from Python code, which is interned.
* Backends, which store reference-counted DAGs of such data.
* Conversion between CA values and typed objects.

"""
import re
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Any
from weakref import WeakValueDictionary

import bencode_rs
from siphash import siphash_128

hash_id_byte_length = 16
hash_id_bencode_byte_length = hash_id_byte_length + len(f"{hash_id_byte_length}:")

# random data generated for this use
siphash_key = bytes.fromhex("78ca81054e1df045447cd7d48958de7d")


_object_cache = WeakValueDictionary()

class BencodeValue(ABC):
    pass


class CA(ABC):
    _id_cache: Optional["CA"]
    flattened: Any
    flattened_serialized: bytes

    def __init__(self):
        self.flattened_serialized = bencode_rs.bencode(self.flattened)

    def needs_indirection(self) -> bool:
        return len(self.flattened_serialized) >= hash_id_bencode_byte_length

    def id(self):
        if self._id_cache is None:
            if self.needs_indirection():
                self._id_cache = CAByteString(siphash_128(key=siphash_key, data=self.serialized_value().encode('ascii')))
            else:
                self._id_cache = self.flattened
        return self._id_cache


def forbidden_mutating_operation(*args, **kwargs):
    raise RuntimeError("Mutating an immutable (CA) collection")


class CAByteString(CA, bytes):
    def __init__(self, *args, **kwargs):
        bytes.__init__(self,*args,**kwargs)
        self.flattened = self
        CA.__init__(self)


class CAList(CA, list):
    def __init__(self, *args, **kwargs):
        list.__init__(self,*args,**kwargs)
        self.flattened = [e.id() for e in self]
        CA.__init__(self)


for method in re.finditer(r"[^, ]+", "__setattr__, __delattr__, __setitem__, __delitem__, __iadd__, __imul__, append, extend, insert, remove, pop, clear, sort, reverse"):
    setattr(CAList, method[0], forbidden_mutating_operation)


class CADict(CA, dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self,*args,**kwargs)
        self.flattened = {k.id(): v.id() for k,v in self.items()}
        CA.__init__(self)


for method in re.finditer(r"[^, ]+", "__setattr__, __delattr__, __setitem__, __delitem__, __ior__, clear, pop, popitem, setdefault"):
    setattr(CADict, method[0], forbidden_mutating_operation)


class HashId:
    pass
class HashIdOrData:
    pass


class Backend(ABC):
    @abstractmethod
    def get_subobject_data(self, key: HashId) -> bytes:
        pass

    # @abstractmethod
    # def has_subobject(self, key: HashId) -> bool:
    #     pass

    @abstractmethod
    def store_subobject_data(self, key: HashId, value: bytes):
        pass

    @abstractmethod
    def delete_subobject_data(self, key: HashId):
        pass

    @abstractmethod
    def __getitem__(self, key: bytes, value: bytes):
        pass

    @abstractmethod
    def __setitem__(self, key: bytes, value: bytes):
        pass

    @abstractmethod
    def __delitem__(self, key: bytes):
        pass

class Object:
    pass

TypeRepresentation = None
class TypeRepresentation(ABC):
    @abstractmethod
    def serialize(self, x: Object) -> bytes:
        pass

    @abstractmethod
    def deserialize(self, data: bytes, subobjects: List[Object]) -> Object:
        pass

    @abstractmethod
    def object_references(self, x: Object) -> List[TypeRepresentation, Object]:
        pass

    @abstractmethod
    def data_references(self, data: bytes) -> List[TypeRepresentation, Tuple[HashId]]:
        pass


_object_cache = WeakValueDictionary()


def _get_subobject(backend: Backend, t: TypeRepresentation, key: HashId) -> Object:
    try:
        return _object_cache[(t,key)]
    except KeyError:
        pass

    data = backend.get_subobject_data(key)
    subobjects = [_get_subobject(backend, u, y) for u,y in t.data_references(data)]
    x = t.deserialize(data, subobjects)
    _object_cache[(t, key)] = x
    return x


def _delete_subobject(backend: Backend, t: TypeRepresentation, key: HashId):
    if backend.delete_subobject_data(key):
        data = backend.get_subobject_data(key)
        for u,y in t.data_references(data):
            _delete_subobject(backend, u, y)


def _store_subobject(backend: Backend, t: TypeRepresentation, x: Object):
    data = t.serialize(x)
    if not backend.store_subobject_data(hash(data), data):
        for u,y in t.object_references(x):
            _store_subobject(backend, u, y)
