import json
import os
import weakref
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Tuple, Any

from atomicwrites import atomic_write
from siphash import siphash_128

registry = {}

# randomly chosen
siphash_key = bytes.fromhex("78ca81054e1df045447cd7d48958de7d")


def _calculate_persistent_id_of_thunk(fn_id: bytes, fields: dict):
    return siphash_128(key=siphash_key, data=b''.join(fn_id + [v.persistent_id() for v in fields.values()]))


_cache_dir = Path(os.environ["EPYOCCT_CACHE2_DIR"])


# metaclass for
class ReifiedFnType(type):
    def __init__(cls, name, bases, attributes):
        super().__init__(name, bases, attributes)
        cls._members = weakref.WeakValueDictionary()

    def __call__(cls, *args, **kwargs):
        persistent_id = _calculate_persistent_id_of_thunk(cls.persistent_identifier(), result.fields)
        registered = cls._members.get(persistent_id)
        if registered is not None:
            return registered
        try:
            with open(_cache_dir/"by_content"/persistent_id.hex()) as file:
                data = json.load(file)
            return cls(**data["value"])
        except IOError:
            pass
        result = cls.__new__(cls, *args, **kwargs)
        # __init__, like any method that returns a Reified instance, should do the minimum necessary to set self.fields (anything else should be computed-as-needed instead)
        cls.__init__(result, *args, **kwargs)
        registered = cls._members.setdefault(id, result)
        if registered is result:
            result._id = id
        return result



class Reified(ABC):
    @classmethod
    def persistent_identifier(cls):
        return cls.__name__

    @classmethod
    @abstractmethod
    def deserialize(cls):
        pass

    def __new__(cls, *args, **kwargs):
        id = bytes()
        existing = registry.get(id)
        if existing is not None:
            return existing
        super().__new__(cls, *args, **kwargs)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(cls, **kwargs)
        if "__init__" in cls.__dict__:
            raise RuntimeError("Subclasses of Reified must not override __init__ (use  instead)")
        cls.persistent_identifier()


# class DataKind(Enum):

class Serializable(ABC):
    # @abstractmethod
    # def persistent_id(self) -> str:
    #     pass

    @classmethod
    def _deserialize(cls, json_value):
        return json_value

    def _serialize(self):
        return self

    @classmethod
    def deserialize(cls, json_value):
        result = cls._deserialize(json_value)
        rewritten = result.serialize()
        assert (rewritten == json_value), "deserialize-serialize must be id"
        return result

    def serialize(self, value):
        result = self._serialize(value)
        return result


class SerializeAsReference(Serializable):
    @classmethod
    def _deserialize(cls, json_value):
        return ReferenceToSubObject(json_value)

    def _serialize(self):
        return self.persistent_id()


siphash_key_for_str = bytes.fromhex("78ca81054e1df045447cd7d48958de7d")
siphash_key_for_list = bytes.fromhex("7d48c856c1d281b8c38113b8d1693956")
siphash_key_for_dict = bytes.fromhex("ab50be95d4b53000ecdb76f68394daf7")


_persistent_id_cache = {}
def _get_cached_persistent_id(value):
    return _persistent_id_cache.get(value)

_as_json_types = {int: bytes([3]), float: bytes([4]), str: bytes([5])}
def _hashable_data(value):
    if value is None:
        return bytes([0])
    if value is True:
        return bytes([1])
    if value is False:
        return bytes([2])
    if type(value) is int:
        return bytes([3]) + json.dumps(value)
    if type(value) is float:
        return bytes([4]) + json.dumps(value)
    if type(value) is str:
        return bytes([5]) + value.encode()

def _calculate_persistent_id(value):
    if type(value) is str:
        str_bytes = str.encode()
        if len(str_bytes) < 32:
            return bytes([1]) + str_bytes
        return siphash_128(key=siphash_key_for_str, data=str.encode())
    if type(value) is dict:
        items = sorted(value.items())
        return siphash_128(key=siphash_key_for_str, data=b''.join(_calculate_persistent_id(i) for i in items))


def _get_persistent_id(value):
    cached = _get_cached_persistent_id(value)
    if cached is not None:
        return cached
    calculated = _calculate_persistent_id(value)
    _persistent_id_cache[value] = calculated
    return calculated


class Serializer:
    def __init__(self, path_base):
        self.path_base = path_base

    def embed_or_save_and_reference(self, value):
        serialized, can_embed = self.serialized(value)
        if can_embed:
            return serialized
        else:
            #TODO;
            return persistent_id

    def serialized(self, value) -> Tuple[Any, bool]:
        if type(value) is dict:
            return {key: self.embed_or_save_and_reference(inner_value) for key, inner_value in value.items()}, False

        if type(value) is list:
            return [self.embed_or_save_and_reference(inner_value) for inner_value in value], False

        if type(value) is str:
            if len(value.encode()) <= 32:
                return value, True
            else:
                return value, False

        if type(value) in [int, float, type(None)]:
            return value, True

        raise RuntimeError(f"Couldn't serialize {value} ({type(value)})")

class Deserializer:
    def __init__(self, g, path_base, hasher):
        self.globals = g
        self.path_base = path_base
        self.hasher = hasher

    def read_brep (self, relative_path):
        file_path = self.path_base + "." + relative_path
        with open (file_path, "rb") as file:
            self.hasher.update (file.read())
        return read_brep (file_path)

    def deserialized(self, value):
        value = unwrap (value)

        if type (value) is dict:
            return {key: self.deserialized (inner_value) for key, inner_value in value.items()}

        if type (value) is list:
            name, data = placeholder_info (value)
            if name == brep_placeholder:
                return self.read_brep (data)

            if name == geometry_placeholder:
                brep = self.read_brep (data)
                if isinstance (brep, Edge):
                    return brep.curve() [0]
                if isinstance (brep, Face):
                    return brep.surface()
                raise RuntimeError ("unrecognized geometry in cache")

            if name == vars_placeholder:
                class_name, data = data
                try:
                    c = self.globals [class_name]
                except KeyError as e:
                    print(self.globals.keys())
                    raise e
                result = c.__new__(c)
                for k, v in self.deserialized (data).items():
                    setattr (result, k, v)
                return result

            if name == class_placeholder:
                class_name, data = data
                c = self.globals [class_name]
                return c(*data)

            return [self.deserialized (inner_value) for inner_value in value]

        if type (value) in [str, int, float, type (None)]:
            return value

        raise RuntimeError(f"Couldn't deserialize {value} ({type(value)})")


@dataclass(frozen=True)
class ObjectClassSpec:
    persistent_id: str
    fields: Dict[str, ]
    content_backrefs: List[str]
    name_backrefs: List[str]

    def calculate_persistent_id(self) -> str:
        pass


@dataclass(frozen=True)
class ObjectSavedNode:
    type_id: str
    fields: Dict[str, ]
    content_backrefs: List[str]
    name_backrefs: List[str]

    def calculate_persistent_id(self) -> str:
        pass

_object_types = {}
_cached_saved_nodes = {}
_cached_values = {}


def load_saved_node(persistent_id):
    cached = _cached_saved_nodes.get(persistent_id)
    if cached is not None:
        return cached
    with open(_cache_dir/"by_content"/persistent_id.hex()) as file:
        node = json.load(file)
    result = ObjectSavedNode(**node)
    _cached_saved_nodes[persistent_id] = result
    return result

def save_node(node: ObjectSavedNode):
    persistent_id = node.calculate_persistent_id()
    with atomic_write(_cache_dir/"by_content"/persistent_id.hex()) as file:
        json.dump(node.__dict__, file)

def load_saved_value(persistent_id_or_builtin):
    cached = _cached_values.get(persistent_id)
    if cached is not None:
        return cached
    node = load_saved_node(persistent_id)
    ty = _object_types[node.type_id]
    fields = {name: load_saved_value(value_id) for name, value_id in node.fields.items()}
    return ty(**node.fields)





class Thunk(ABC):
    """Interface for abstract base classes whose members are thunks that can be forced to some "value", which can be cached on disk."""
    def __init__(self, thunk_value):
        self._cached_value = None
        self._thunk_id = thunk_value.persistent_id()

    @abstractmethod
    def _force(self):
        """The method to actually *perform* the forcing.

        Subclasses should implement this ... and also, this class's __init_subclass__ will implicitly """

    def force(self):
        if self._cached_value is not None:
            return self._cached_value

        try:
            self._cached_value = load_saved_value(self._thunk_id)
            return self._cached_value
        except (IOError,KeyError):
            pass

        self._cached_value = self._force()
        return self._cached_value
