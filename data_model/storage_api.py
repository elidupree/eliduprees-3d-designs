"""


Our underlying storage format is basically just deduplicated bencode, because anything else would be scope creep. (Actually a sidegrade of bencode – we don't care about integers, and we do support using lists/maps as keys of maps, by giving their serialized forms to bencode when they're used as keys.) Conceptually, the only "values" are
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

from bencodepy import bencode
from siphash import siphash_128

from code_generation import inject_code

hash_id_byte_length = 16
hash_id_bencode_byte_length = hash_id_byte_length + len(f"{hash_id_byte_length}:")

# random data generated for this use
siphash_key = bytes.fromhex("78ca81054e1df045447cd7d48958de7d")


def serialized_id_is_reference(serialized_id: bytes):
    assert len(serialized_id) <= hash_id_bencode_byte_length
    return len(serialized_id) >= hash_id_bencode_byte_length


BencodeValue = Union[bytes, list, dict]


def deserialized_id_is_reference(deserialized_id: BencodeValue):
    if type(deserialized_id) is bytes:
        return len(deserialized_id) >= hash_id_byte_length
    else:
        return False


class CA(ABC):
    _id_cache: Optional["CA"]
    raw_form: BencodeValue
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


def forbidden_mutating_operation(name):
    def f(*args, **kwargs):
        raise RuntimeError(f"using {name} to mutate an immutable (CA) collection")
    f.__name__ = name
    return f


def forward_methods(class_, methods):
    names = [m[0] for m in re.finditer(r"[^, ]+", methods)]
    for name in names:
        assert hasattr(class_, name)
    return "".join(f'''
    def {name}(self, *args, **kwargs):
        return self.data.{name}(*args, **kwargs)''' for name in names)


class CAByteString(CA):
    def __init__(self, *args, **kwargs):
        self.raw_form = self.data = bytes(*args,**kwargs)
        self.serialized = bencode(self.raw_form)
        CA.__init__(self)

    def children(self):
        return []

    def __bytes__(self):
        return self.data

    inject_code(forward_methods(bytes, "__contains__, __getitem__, __iter__, __len__, __format__, __repr__, __str__, __ge__, __le__, __gt__, __lt__, count, index, find, isalpha, isdigit, isascii, islower, isspace, istitle, isupper, startswith, endswith"))
# == Generated code (don't edit this) ==                                   #gen#
    def __contains__(self, *args, **kwargs):                               #gen#
        return self.data.__contains__(*args, **kwargs)                     #gen#
    def __getitem__(self, *args, **kwargs):                                #gen#
        return self.data.__getitem__(*args, **kwargs)                      #gen#
    def __iter__(self, *args, **kwargs):                                   #gen#
        return self.data.__iter__(*args, **kwargs)                         #gen#
    def __len__(self, *args, **kwargs):                                    #gen#
        return self.data.__len__(*args, **kwargs)                          #gen#
    def __format__(self, *args, **kwargs):                                 #gen#
        return self.data.__format__(*args, **kwargs)                       #gen#
    def __repr__(self, *args, **kwargs):                                   #gen#
        return self.data.__repr__(*args, **kwargs)                         #gen#
    def __str__(self, *args, **kwargs):                                    #gen#
        return self.data.__str__(*args, **kwargs)                          #gen#
    def __ge__(self, *args, **kwargs):                                     #gen#
        return self.data.__ge__(*args, **kwargs)                           #gen#
    def __le__(self, *args, **kwargs):                                     #gen#
        return self.data.__le__(*args, **kwargs)                           #gen#
    def __gt__(self, *args, **kwargs):                                     #gen#
        return self.data.__gt__(*args, **kwargs)                           #gen#
    def __lt__(self, *args, **kwargs):                                     #gen#
        return self.data.__lt__(*args, **kwargs)                           #gen#
    def count(self, *args, **kwargs):                                      #gen#
        return self.data.count(*args, **kwargs)                            #gen#
    def index(self, *args, **kwargs):                                      #gen#
        return self.data.index(*args, **kwargs)                            #gen#
    def find(self, *args, **kwargs):                                       #gen#
        return self.data.find(*args, **kwargs)                             #gen#
    def isalpha(self, *args, **kwargs):                                    #gen#
        return self.data.isalpha(*args, **kwargs)                          #gen#
    def isdigit(self, *args, **kwargs):                                    #gen#
        return self.data.isdigit(*args, **kwargs)                          #gen#
    def isascii(self, *args, **kwargs):                                    #gen#
        return self.data.isascii(*args, **kwargs)                          #gen#
    def islower(self, *args, **kwargs):                                    #gen#
        return self.data.islower(*args, **kwargs)                          #gen#
    def isspace(self, *args, **kwargs):                                    #gen#
        return self.data.isspace(*args, **kwargs)                          #gen#
    def istitle(self, *args, **kwargs):                                    #gen#
        return self.data.istitle(*args, **kwargs)                          #gen#
    def isupper(self, *args, **kwargs):                                    #gen#
        return self.data.isupper(*args, **kwargs)                          #gen#
    def startswith(self, *args, **kwargs):                                 #gen#
        return self.data.startswith(*args, **kwargs)                       #gen#
    def endswith(self, *args, **kwargs):                                   #gen#
        return self.data.endswith(*args, **kwargs)                         #gen#
# == End of generated code (don't edit this) ==                            #gen#


class CAList(CA):
    def __init__(self, *args, **kwargs):
        self.data = list(*args, **kwargs)
        for e in self.data:
            assert isinstance(e, CA)
        self.raw_form = [e.raw_form for e in self.data]
        self.serialized = bencode([e.id().raw_form for e in self.data])
        CA.__init__(self)

    def children(self):
        yield from self.data

    def __add__(self, other):
        return CAList(self.data + other.data)
    
    def __mul__(self, other):
        return CAList(self.data * other)

    inject_code(forward_methods(list, "__contains__, __getitem__, __iter__, __len__, __format__, __repr__, __str__, count, index"))
# == Generated code (don't edit this) ==                                   #gen#
    def __contains__(self, *args, **kwargs):                               #gen#
        return self.data.__contains__(*args, **kwargs)                     #gen#
    def __getitem__(self, *args, **kwargs):                                #gen#
        return self.data.__getitem__(*args, **kwargs)                      #gen#
    def __iter__(self, *args, **kwargs):                                   #gen#
        return self.data.__iter__(*args, **kwargs)                         #gen#
    def __len__(self, *args, **kwargs):                                    #gen#
        return self.data.__len__(*args, **kwargs)                          #gen#
    def __format__(self, *args, **kwargs):                                 #gen#
        return self.data.__format__(*args, **kwargs)                       #gen#
    def __repr__(self, *args, **kwargs):                                   #gen#
        return self.data.__repr__(*args, **kwargs)                         #gen#
    def __str__(self, *args, **kwargs):                                    #gen#
        return self.data.__str__(*args, **kwargs)                          #gen#
    def count(self, *args, **kwargs):                                      #gen#
        return self.data.count(*args, **kwargs)                            #gen#
    def index(self, *args, **kwargs):                                      #gen#
        return self.data.index(*args, **kwargs)                            #gen#
# == End of generated code (don't edit this) ==                            #gen#


class CADict(CA):
    def __init__(self, *args, **kwargs):
        self.data = dict(*args, **kwargs)
        for k,v in self.data.items():
            assert isinstance(k, CA)
            assert isinstance(v, CA)
        self.raw_form = {k.serialized: v.raw_form for k,v in self.data.items()}
        # print({k.id().raw_form: v.id().raw_form for k, v in self.data.items()})
        self.serialized = bencode({k.id().serialized: v.id().raw_form for k, v in self.data.items()})
        # print("ok")
        CA.__init__(self)

    def children(self):
        yield from self.data.keys()
        yield from self.data.values()

    inject_code(forward_methods(dict, "__contains__, __getitem__, __iter__, __len__, __format__, __repr__, __str__, get, items, keys, values"))
# == Generated code (don't edit this) ==                                   #gen#
    def __contains__(self, *args, **kwargs):                               #gen#
        return self.data.__contains__(*args, **kwargs)                     #gen#
    def __getitem__(self, *args, **kwargs):                                #gen#
        return self.data.__getitem__(*args, **kwargs)                      #gen#
    def __iter__(self, *args, **kwargs):                                   #gen#
        return self.data.__iter__(*args, **kwargs)                         #gen#
    def __len__(self, *args, **kwargs):                                    #gen#
        return self.data.__len__(*args, **kwargs)                          #gen#
    def __format__(self, *args, **kwargs):                                 #gen#
        return self.data.__format__(*args, **kwargs)                       #gen#
    def __repr__(self, *args, **kwargs):                                   #gen#
        return self.data.__repr__(*args, **kwargs)                         #gen#
    def __str__(self, *args, **kwargs):                                    #gen#
        return self.data.__str__(*args, **kwargs)                          #gen#
    def get(self, *args, **kwargs):                                        #gen#
        return self.data.get(*args, **kwargs)                              #gen#
    def items(self, *args, **kwargs):                                      #gen#
        return self.data.items(*args, **kwargs)                            #gen#
    def keys(self, *args, **kwargs):                                       #gen#
        return self.data.keys(*args, **kwargs)                             #gen#
    def values(self, *args, **kwargs):                                     #gen#
        return self.data.values(*args, **kwargs)                           #gen#
# == End of generated code (don't edit this) ==                            #gen#


_object_cache = WeakValueDictionary()


def interned_ca(x: CA):
    return _object_cache.setdefault(x.id(), x)


def already_available_ca_by_id(id: CA) -> CA:
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