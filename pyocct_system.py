import datetime
import hashlib
import dis
import inspect
import functools
import re
import os
import os.path
import json
from OCCT.BOPAlgo import BOPAlgo_Options
import OCCT.Exchange
import OCCT.TopoDS
import OCCT.gp

BOPAlgo_Options.SetParallelMode_(True)


def _setup():
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
      #print(f"calling {inner}")
      return watch_time(repr(inner), lambda: wrap(inner(
        *(unwrap (value) for value in args),
        **{key: unwrap (value) for key, value in kwargs.items()}
      )))
    def __getattr__(self, name):
      inner = self.wrapped_object
      inner_attribute = getattr(inner, name)
      override = attribute_overrides.get((inner, name))
      if override is None:
        c = getattr(inner, "__class__")
        if c is not None:
          override = attribute_overrides.get((c, name))
      #print (inner, name, override)
      if override is not None:
        inner_attribute = override(inner_attribute)
        if hasattr(inner_attribute, "__get__"):
          if type(inner) is type:
            inner_attribute = inner_attribute.__get__(None, inner)
          else:
            inner_attribute = inner_attribute.__get__(inner, type(inner))
      return wrap(inner_attribute)
      
     
      
  def wrap_special_method (method):
    def method_wrapper(self, *args, **kwargs):
      return self.__getattr__(method)(*args, **kwargs)
    setattr(Wrapper, method, method_wrapper)

  types_not_to_wrap = set([
    Wrapper, str, int, float, bool, type(None)
  ])


  arithmetic = re.findall(r"[\w]+", "add, sub, mul, matmul, truediv, floordiv, div, mod, divmod, pow, lshift, rshift, and, xor, or")
  
  # deliberately left out, at least for now: new, init, del, getattr, getattribute, setattr, delattr, call
  other_special_methods = re.findall(r"[\w]+", "str,bytes,format,lt,le,eq,ne,gt,ge,hash,bool,dir,get,set,delete,set_name, slots, init_subclass, instancecheck, subclasscheck, class_getitem, len, length_hint, getitem, setitem, delitem, missing, iter, reversed, contains,neg,pos,abs, invert, complex, int, float, index, round,trunc, floor, ceil, enter, exit, await,aiter,anext,aenter,aexit,")

  special_methods = arithmetic + ["r"+a for a in arithmetic] + ["i"+a for a in arithmetic]+other_special_methods
  for name in special_methods:
    wrap_special_method(f"__{name}__")
    
  def wrap(value):
    if type (value) in types_not_to_wrap:
      return value
    else:
      return Wrapper(value)
  def unwrap(value):
    if type (value) is Wrapper:
      return value.wrapped_object
    else:
      return value
    
  #attribute_overrides [(OCCT.Exchange.ExchangeBasic, "read_brep")] = lambda original: None
  attribute_overrides [(OCCT.gp.gp_Vec, "__init__")] = lambda original: None
  
  import pyocct_api_wrappers
  def export(name, value):
    globals()[name] = value
  def override_attribute(c, name, value):
    attribute_overrides [(c, name)] = value
  pyocct_api_wrappers.setup(wrap, export, override_attribute)
  
  for export in re.findall(r"[\w_]+", "wrap, unwrap"):
    globals() [export] = locals() [export]
  
  
_setup()

_ExchangeBasic = wrap(OCCT.Exchange.ExchangeBasic)


_cache_globals = None
_cache_directory = None
_cache_info_by_global_key = {}

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

def _load_cache (key, kind):
  path = os.path.join (_cache_directory, key)
  
  if kind == "JSON":
    with open(path + ".json") as file:
      result = json.load(file)
  elif kind == "BREP":
    result = _ExchangeBasic.read_brep(path + ".brep")
  else:
    raise RuntimeError(f"{kind} isn't a supported kind for pyocct_system caching")
  
  return result

def _save_cache (key, kind, value, info):
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
    
  temp_path = path + ".temp"
  if kind == "JSON":
    value_path = path + ".json"
    with open(temp_path, "w") as file:
      json.dump (value, file)
      file.flush()
      os.fsync(file.fileno())
  elif kind == "BREP":
    value_path = path + ".brep"
    if type (unwrap (value)) != OCCT.TopoDS.TopoDS_Shape:
      raise RuntimeError(f"BREP caching requires a TopoDS_Shape object, but got `{value}`")
    _ExchangeBasic.write_brep(value, temp_path)
  else:
    raise RuntimeError(f"{ext} filetype not currently supported by pyocct_system.cached")
    
  os.replace (temp_path, value_path)
  
  with open(temp_path, "w") as file:
    json.dump (info, file)
    file.flush()
    os.fsync(file.fileno())
  os.replace (temp_path, info_path)

  

  
  
def _cache_is_valid (key, source_hash):
  info_path = _info_path (key)
  try:
    with open(info_path) as file:
      stored = json.load(file)
      if stored["source_hash"] != source_hash:
        return False
      for key2, value in stored["globals"].items():
        try: 
          if _output_hash (key2) != value:
            return False
        except OutputHashError:
          return False
        
  except (FileNotFoundError, json.decoder.JSONDecodeError):
    return False
    
  return True

def _get_cached(key, kind, generate):
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
      "globals": {key2: _output_hash(key2) for key2 in _globals_in_code(code)},
    }
    output_hash = hashlib.sha256 (json.dumps (cache_info).encode ("utf-8")).hexdigest()
    cache_info ["output_hash"] = output_hash
    
    _save_cache (key, kind, new_result, cache_info)
    finish_time = datetime.datetime.now()
    print(f"…done! ({finish_time}, took {(finish_time - start_time)})")
    
  
  # note: always reload the cache instead of using the one that was just generated in memory,
  # to make sure it is properly canonicalized
  return _load_cache (key, kind)
    
    
def cached(kind):
  def decorate(generate):
    key = generate.__name__
    return _get_cached(key, kind, generate)
  return decorate


      