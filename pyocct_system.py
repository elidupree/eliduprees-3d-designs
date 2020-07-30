import datetime
import hashlib
import dis
import inspect
import functools
import re
import sys
import os
import os.path
import json
from OCCT.BOPAlgo import BOPAlgo_Options
import OCCT.Exchange
import OCCT.TopoDS
import OCCT.gp

BOPAlgo_Options.SetParallelMode_(True)


##########################################################
###################   Wrapper system   ###################
##########################################################

def _setup_wrappers():
  def watch_time(name, func):
    start = datetime.datetime.now()
    result = func()
    finish = datetime.datetime.now()
    duration = finish - start
    seconds = duration.total_seconds()
    if seconds > 0.01:
      print(f"operation {name} took {seconds} seconds")
    return result


  attribute_overrides = {}

  def get_name(a):
    if hasattr(a, "__qualname__"):
      return a.__qualname__
    elif hasattr(a, "__name__"):
      return a.__name__
    elif hasattr(a, "__class__"):
      return get_name(a.__class__)
    else:
      return "<object without recognized name attributes>"



  class Wrapper:
    def __init__(self, wrapped_object):
      self.wrapped_object = wrapped_object
    def __call__(self, *args, **kwargs):
      inner = self.wrapped_object
      #print(f"calling {inner}, {args}")
      if inspect.isclass(inner):
        override = attribute_overrides.get((inner, "__new__"))
        if override is not None:
          inner = override(inner).__get__(None, inner)
          
      return watch_time(repr(inner), lambda: wrap(inner(
        *(unwrap (value) for value in args),
        **{key: unwrap (value) for key, value in kwargs.items()}
      )))
    def __getattr__(self, name):
      inner = self.wrapped_object
      if inspect.isclass(inner):
        override = attribute_overrides.get((inner, name))
      else:
        c = getattr(inner, "__class__")
        if c is not None:
          override = attribute_overrides.get((c, name))
          
      #print("in getattr", inner, name, override)
      if override is None:
        inner_attribute = getattr(inner, name)
      else:
        inner_attribute = getattr(inner, name, None)
      #print("in getattr", inner, name, inner_attribute, override)
      
      #print (inner, name, override)
      if override is not None:
        inner_attribute = unwrap (override(inner_attribute))
        if hasattr(inner_attribute, "__get__"):
          # hack - treat pybind11_type as type
          if type(inner) is type or type(inner) is type(OCCT.TopoDS.TopoDS_Shape):
            inner_attribute = inner_attribute.__get__(None, inner)
          else:
            inner_attribute = inner_attribute.__get__(inner, type(inner))
      return wrap(inner_attribute)
    
    # the catchall below SHOULD be able to handle format/str, but
    def __format__(self, format_arguments):
      attr = self.__getattr__("__format__")
      if attr.wrapped_object is object.__format__:
        return object.__format__(self.wrapped_object, format_arguments)
      else:
        return attr(format_arguments)
    def __str__(self):
      attr = self.__getattr__("__str__")
      if attr.wrapped_object is object.__str__:
        return object.__str__(self.wrapped_object)
      else:
        return attr()
    def __repr__(self):
      attr = self.__getattr__("__repr__")
      if attr.wrapped_object is object.__repr__:
        result = object.__repr__(self.wrapped_object)
      else:
        result = attr()
      return f"Wrapper({result} / {str(self)})"
      
    '''def __new__(cls, *args, **kwargs):
      attr = self.__getattr__("__new__")
      attr(*args, **kwargs)'''
      
     
      
  def wrap_special_method (method):
    def method_wrapper(self, *args, **kwargs):
      #print("method called", self.wrapped_object, method, args)
      return self.__getattr__(method)(*args, **kwargs)
    setattr(Wrapper, method, method_wrapper)

  types_not_to_wrap = set([
    Wrapper, str, int, float, bool, type(None)
  ])


  arithmetic = re.findall(r"[\w]+", "add, sub, mul, matmul, truediv, floordiv, div, mod, divmod, pow, lshift, rshift, and, xor, or")
  
  # deliberately left out, at least for now: new, init, del, format, str, repr, getattr, getattribute, setattr, delattr, call
  other_special_methods = re.findall(r"[\w]+", "bytes,lt,le,eq,ne,gt,ge,hash,bool,dir,get,set,delete,set_name, slots, init_subclass, instancecheck, subclasscheck, class_getitem, len, length_hint, getitem, setitem, delitem, missing, iter, next, reversed, contains,neg,pos,abs, invert, complex, int, float, index, round,trunc, floor, ceil, enter, exit, await,aiter,anext,aenter,aexit,")

  special_methods = arithmetic + ["r"+a for a in arithmetic] + ["i"+a for a in arithmetic]+other_special_methods
  for name in special_methods:
    wrap_special_method(f"__{name}__")
    
  def wrap(value):
    if type (value) in types_not_to_wrap:
      return value
    else:
      c = getattr(value, "__class__")
      if c is not None:
        override = attribute_overrides.get((c, "__wrap__"))
        if override is not None:
          override = override(None)
          result = override(value)
          if result is value:
            return Wrapper(value)
          else:
            return wrap(result)
      return Wrapper(value)

  def unwrap(value):
    if type (value) is Wrapper:
      return value.wrapped_object
    else:
      return value
    
  #attribute_overrides [(OCCT.Exchange.ExchangeBasic, "read_brep")] = lambda original: None
  #attribute_overrides [(OCCT.gp.gp_Vec, "__init__")] = lambda original: None
  
  import pyocct_api_wrappers
  def export(name, value):
    globals()[name] = value
  def override_attribute(c, name, value):
    attribute_overrides [(unwrap(c), name)] = value
  pyocct_api_wrappers.setup(wrap, export, override_attribute)
  
  for export in re.findall(r"[\w_]+", "wrap, unwrap"):
    globals() [export] = locals() [export]
  
  
_setup_wrappers()


##########################################################
##################   De/serialization   ##################
##########################################################

def _setup_serialization():
  # just a casual 128 bits of random data so there's no way it would occur by accident
  unique_placeholder = "PLACEHOLDER_d43e642cf620e3fa21378b00c24dd6b4"
  brep_placeholder = "BREP"
  
  def placeholder (name, data):
    return [unique_placeholder, name, data]
  
  def placeholder_info (value):
    if type (value) is list and len(value) == 3 and value [0] == unique_placeholder:
      return value [1], value [2]
    return None, None

  class Serializer:
    def __init__(self, path_base):
      self.path_base = path_base
    
    def serialized(self, value, key_path = []):
      value = unwrap (value)
      
      if type (value) is dict:
        return {key: self.serialized (inner_value, key_path + [key]) for key, inner_value in value.items()}
        
      if type (value) is list:
        return [self.serialized (inner_value, key_path + [str(key)]) for key, inner_value in enumerate (value)]
      
      if is_shape (value):
        value = wrap (value)
        if any ("." in key for key in key_path):
          raise RuntimeError (f"We don't support serializing shapes inside objects with keys that contain `.`, because we use the dot-separated key path as the file path and need it to be unique (Tried to serialize {value} at key path {key_path})")
        file_path = ".".join ([self.path_base] + key_path) + ".brep"
        temp_path = file_path + ".temp"
        value.write_brep (temp_path)
        os.replace (temp_path, file_path)
        return placeholder (brep_placeholder, file_path)
      
      if type (value) in [str, int, float, type (None)]:
        return value
        
      raise RuntimeError(f"Couldn't serialize {value} ({type(value)})")
  
  class Deserializer:
    def __init__(self, path_base):
      self.path_base = path_base
    
    def deserialized(self, value):
      value = unwrap (value)
      
      if type (value) is dict:
        return {key: self.deserialized (inner_value) for key, inner_value in value.items()}
        
      if type (value) is list:
        name, data = placeholder_info (value)
        if name == brep_placeholder:
          return read_brep (data)
        return [self.deserialized (inner_value) for inner_value in value]
      
      if type (value) in [str, int, float, type (None)]:
        return value
      
      raise RuntimeError(f"Couldn't deserialize {value} ({type(value)})")
      
  
  def atomic_write_json (file_path, value):
    temp_path = file_path + ".temp"
    with open(temp_path, "w") as file:
      json.dump (value, file)
      file.flush()
      os.fsync(file.fileno())
    os.replace (temp_path, file_path)
    
  def serialize(path_base, value):
    with_placeholders = Serializer (path_base).serialized (value)
    atomic_write_json (path_base + ".json", with_placeholders)
  
  def deserialize(path_base):
    with open(path_base + ".json") as file:
      with_placeholders = json.load(file)
    return Deserializer (path_base).deserialized (with_placeholders)
    
  for export in re.findall(r"[\w_]+", "serialize, deserialize, atomic_write_json"):
    globals() [export] = locals() [export]
    

_setup_serialization()


##########################################################
###################   Caching system   ###################
##########################################################


_cache_globals = None
_cache_directory = None
_cache_info_by_global_key = {}

_cache_system_source = inspect.getsource (sys.modules [__name__])
_cache_system_source_hash = hashlib.sha256(_cache_system_source.encode ("utf-8")).hexdigest()

def initialize_system (cache_globals, cache_directory):
  global _cache_globals
  global _cache_directory
  
  if type (cache_globals) is not dict:
    raise RuntimeError ("called initialize_system without giving globals")
  if _cache_globals is not None:
    raise RuntimeError ("called initialize_system more than once")
  
  _cache_globals = cache_globals
  _cache_directory = cache_directory


def _globals_in_code(code):
  return (match.group (1) for match in re.finditer(r"LOAD_GLOBAL\s+\d+\s+\(([^\)]+)\)", code) if not hasattr(_cache_globals["__builtins__"], match.group(1)))

class _Recursive:
  pass
class OutputHashError(Exception):
  pass
def _output_hash (key):
  #print("output_hash called", key)
  in_memory = _cache_info_by_global_key.get(key)
  if in_memory is _Recursive:
    raise OutputHashError("the system currently can't handle recursive functions")
  if in_memory is not None:
    return in_memory ["output_hash"]
  
  _cache_info_by_global_key [key] = _Recursive
  
  if key not in _cache_globals:
    raise OutputHashError(f"tried to check current value of `{key}`, but it didn't exist; the system currently can't handle references to global keys that don't exist yet. Current globals: {_cache_globals}")  
  value = _cache_globals [key]
  
  try:
    code = dis.Bytecode(value).dis()
    #print(key, code)
    code2 = inspect.getsource (value)
    hasher = hashlib.sha256()
    #hasher.update (code.encode ("utf-8"))
    hasher.update (code2.encode ("utf-8"))
    for key2 in _globals_in_code (code):
      hasher.update (_output_hash (key2).encode ("utf-8"))
    result = hasher.hexdigest()
  except TypeError:
    result = repr(value)
    
  #print(f"Info: decided that output hash of {key} is {result}")
    
  _cache_info_by_global_key [key] = {"output_hash": result}
  return result

def _info_path (key):
  path = os.path.join (_cache_directory, key)
  return path + ".cache_info"


def _load_cache (key):
  path = os.path.join (_cache_directory, key)
  return deserialize (path)

def _save_cache (key, value, info):
  path = os.path.join (_cache_directory, key)
  info_path = _info_path (key)
  
  # remove the inputs record first so that, in case of the process being terminated, we don't
  #   leave the new mismatched values alongside the old valid inputs;
  # then put the inputs back last so we can't leave the new valid inputs alongside
  #   a broken value
  try:
    os.remove (info_path)
  except FileNotFoundError:
    pass
    
  serialize (path, value)
  atomic_write_json (info_path, info)

  
  
def _cache_is_valid (key, source_hash):
  info_path = _info_path (key)
  try:
    with open(info_path) as file:
      stored = json.load(file)
      if stored["source_hash"] != source_hash:
        return False
      if stored["cache_system_source_hash"] != _cache_system_source_hash:
        return False
      for key2, value in stored["globals"].items():
        try: 
          if _output_hash (key2) != value:
            return False
        except OutputHashError:
          return False
        
  except (FileNotFoundError, json.decoder.JSONDecodeError, KeyError):
    return False
    
  return True

def _get_cached(key, generate):
  print (f"### doing {key} ###")
  code = dis.Bytecode(generate).dis()
  code2 = inspect.getsource (generate)
  #print (code)
  #print(list(_globals_in_code(code)))
  #print (code2)
  hasher = hashlib.sha256()
  #hasher.update (code.encode ("utf-8"))
  hasher.update (code2.encode ("utf-8"))
  source_hash = hasher.hexdigest()
  
  if _cache_is_valid (key, source_hash):
    print(f"cached version seems valid, loading it")
  else:
    start_time = datetime.datetime.now()
    print(f"needs update, generating new version… ({start_time})")
    new_result = generate()
    cache_info = {
      "source_hash": source_hash,
      "cache_system_source_hash": _cache_system_source_hash,
      "globals": {key2: _output_hash(key2) for key2 in _globals_in_code(code)},
    }
    output_hash = hashlib.sha256 (json.dumps (cache_info).encode ("utf-8")).hexdigest()
    cache_info ["output_hash"] = output_hash
    
    _save_cache (key, new_result, cache_info)
    finish_time = datetime.datetime.now()
    print(f"…done! ({finish_time}, took {(finish_time - start_time)})")
    
  
  # note: always reload the cache instead of using the one that was just generated in memory,
  # to make sure it is properly canonicalized
  return _load_cache (key)
    
    
def cached(generate):
  key = generate.__name__
  return _get_cached(key, generate)


      