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
import traceback
import io
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
      def short_frame(frame):
        file,line,_,_ = frame
        file = os.path.basename(file)
        return f"{file}:{line}"
      relevant_frame = []
      for frame in traceback.extract_stack():
        if "pyocct_system.py" in frame[0] or "pyocct_api_wrappers.py" in frame[0]:
          break
        relevant_frame = frame
      print(f"operation {name} took {seconds} seconds ({short_frame(relevant_frame)})")
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

  def apply_wrapper_override(wrapper, on_class, unwrapped_original, override):
    # Don't wrap override methods unless they were already wrapped;
    # calls to those methods should act on the wrapped arguments
    result = override(wrap(unwrapped_original))
    was_wrapped = type(result) is Wrapper
    unwrapped_result = unwrap(result)
    if hasattr(unwrapped_result, "__get__"):
      if on_class:
        result = unwrapped_result.__get__(None, wrapper)
      else:
        result = unwrapped_result.__get__(wrapper, type(wrapper))
        
      if was_wrapped:
        result = wrap(result)
        
    return result
  
  def get_override(inner, name):
    if inspect.isclass(inner):
      result = attribute_overrides.get((inner, name))
      if result is None and inner.__base__ is not None:
        return get_override (inner.__base__, name)
      return result
    else:
      return get_override (inner.__class__, name)
        
  def get_maybe_capitalized(inner, name, *args):
    try:
      return getattr(inner, name)
    except AttributeError as e:
      try:
        return getattr(inner, name.capitalize(), *args)
      except AttributeError:
        raise e
    
  class Wrapper:
    def __init__(self, wrapped_object):
      self.wrapped_object = wrapped_object
    def __call__(self, *args, **kwargs):
      inner = self.wrapped_object
      to_call = inner
      #print(f"calling {inner}, {args}")
      if inspect.isclass(inner):
        override = attribute_overrides.get((inner, "__new__"))
        if override is not None:
          to_call = apply_wrapper_override(self, True, lambda *args, **kwargs: inner(*args, **kwargs), override)
          return watch_time(repr(inner), lambda: wrap(to_call(
            *args, **kwargs)))
          
      return watch_time(repr(inner), lambda: wrap(to_call(
        *(unwrap (value) for value in args),
        **{key: unwrap (value) for key, value in kwargs.items()}
      )))
    def __getattr__(self, name):
      inner = self.wrapped_object
      override = get_override(inner, name)
          
      #print("in getattr", inner, name, getattr(inner, name, None), override)
      if override is None:
        if name.islower():
          inner_attribute = get_maybe_capitalized(inner, name)
        else:
          if get_override(inner, name.lower()) is not None:
            raise RuntimeError("No using lowercase-overridden attributes by their capitalized names")
          inner_attribute = getattr(inner, name)
      else:
        inner_attribute = get_maybe_capitalized(inner, name, None)
      #print("in getattr", inner, name, inner_attribute, override)
      
      #print (inner, name, override)
      if override is not None:
        # hack - treat pybind11_type as type
        on_class = type(inner) is type or type(inner) is type(OCCT.TopoDS.TopoDS_Shape)
        return apply_wrapper_override(self, on_class, inner_attribute, override)
      return wrap(inner_attribute)
    
    # the catchall below SHOULD be able to handle format/str, but
    def __format__(self, format_arguments):
      attr = self.__getattr__("__format__")
      if unwrap(attr) is object.__format__:
        return object.__format__(self.wrapped_object, format_arguments)
      else:
        return attr(format_arguments)
    def __str__(self):
      attr = self.__getattr__("__str__")
      if unwrap(attr) is object.__str__:
        return object.__str__(self.wrapped_object)
      else:
        return attr()
    def __repr__(self):
      if inspect.isclass(self.wrapped_object):
        return object.__repr__(self.wrapped_object)
      
      attr = self.__getattr__("__repr__")
      result = attr()
        
      c = getattr(self.wrapped_object, "__class__")
      if c is not None:
        if (c, "__repr__") in attribute_overrides:
          return result
        
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
    result = value
    if type(result) is Wrapper:
      result = value.wrapped_object
    if type(result) is list:
      result = [unwrap(item) for item in result]
    return result
    
  #attribute_overrides [(OCCT.Exchange.ExchangeBasic, "read_brep")] = lambda original: None
  #attribute_overrides [(OCCT.gp.gp_Vec, "__init__")] = lambda original: None
  
  import pyocct_api_wrappers
  def export(name, value):
    globals()[name] = value
  def override_attribute(c, name, value):
    attribute_overrides [(unwrap(c), name)] = value
  pyocct_api_wrappers.setup(wrap, unwrap, export, override_attribute)
  
  for export in re.findall(r"[\w_]+", "wrap, unwrap"):
    globals() [export] = locals() [export]
  
  
_setup_wrappers()


##########################################################
##################   De/serialization   ##################
##########################################################

class SerializeAsVars:
  pass

def _setup_serialization():
  # just a casual 128 bits of random data so there's no way it would occur by accident
  unique_placeholder = "PLACEHOLDER_d43e642cf620e3fa21378b00c24dd6b4"
  brep_placeholder = "BREP"
  geometry_placeholder = "Geometry"
  vars_placeholder = "vars"
  class_placeholder = "class"
  
  def placeholder (name, data):
    return [unique_placeholder, name, data]
  
  def placeholder_info (value):
    if type (value) is list and len(value) == 3 and value [0] == unique_placeholder:
      return value [1], value [2]
    return None, None

  point2s = ["Point2", "Vector2", "Direction2"]
  point3s = ["Point", "Vector", "Direction"]

  class Serializer:
    def __init__(self, path_base):
      self.path_base = path_base
    
    def relative_path (self, key_path):
      if any ("." in key for key in key_path):
        raise RuntimeError (f"We don't support serializing non-JSON values inside objects with keys that contain `.`, because we use the dot-separated key path as the file path and need it to be unique (Tried to serialize {value} at key path {key_path})")
      return ".".join (key_path)
    def serialized(self, value, key_path = []):
      value = unwrap (value)
      
      if type (value) is dict:
        return {key: self.serialized (inner_value, key_path + [key]) for key, inner_value in value.items()}
        
      if type (value) is list:
        return [self.serialized (inner_value, key_path + [str(key)]) for key, inner_value in enumerate (value)]
      
      relative_path = self.relative_path (key_path + ["brep"])
      file_path = self.path_base + "." + relative_path
      if is_shape (value):
        wrap(value).write_brep (file_path)
        return placeholder (brep_placeholder, relative_path)
      
      if isinstance (value, Curve):
        Edge (value).write_brep (file_path)
        return placeholder (geometry_placeholder, relative_path)
      
      if isinstance (value, Surface):
        Face (value).write_brep (file_path)  
        return placeholder (geometry_placeholder, relative_path)
      
      if isinstance (value, SerializeAsVars):
        return placeholder (vars_placeholder, (value.__class__.__name__, self.serialized (vars (value))))
      
      for p in point2s:
        if isinstance (value, globals()[p]):
          value = wrap(value)
          return placeholder (class_placeholder, (p, (value[0], value[1])))
      
      for p in point3s:
        if isinstance (value, globals()[p]):
          value = wrap(value)
          return placeholder (class_placeholder, (p, (value[0], value[1], value[2])))
      
      if type (value) in [str, int, float, type (None)]:
        return value
        
      raise RuntimeError(f"Couldn't serialize {value} ({type(value)})")
  
  class Deserializer:
    def __init__(self, path_base, hasher):
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
          c = _cache_globals [class_name]
          result = c.__new__(c)
          for key, value in self.deserialized (data).items():
            setattr (result, key, value)
          return result
        
        if name == class_placeholder:
          class_name, data = data
          c = _cache_globals [class_name]
          return c(*data)
          
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
    hasher = hashlib.sha256()
    path = path_base + ".json"
    with open(path) as file:
      with_placeholders = json.load(file)
    with open(path, "rb") as file:
      hasher.update (file.read())
      
    result = Deserializer (path_base, hasher).deserialized (with_placeholders)
    return result, hasher.hexdigest()
    
  for export in re.findall(r"[\w_]+", "serialize, deserialize, atomic_write_json"):
    globals() ["_" + export] = locals() [export]
    

_setup_serialization()


##########################################################
###################   Caching system   ###################
##########################################################


_cache_globals = None
_cache_directory = None
_cache_info_by_global_key = {}

_cache_system_source = inspect.getsource (sys.modules [__name__]) + inspect.getsource (sys.modules ["pyocct_api_wrappers"])
_cache_system_source_hash = hashlib.sha256(_cache_system_source.encode ("utf-8")).hexdigest()

def _initialize_cache_system (cache_globals, cache_directory):
  global _cache_globals
  global _cache_directory
  
  if type (cache_globals) is not dict:
    raise RuntimeError ("called initialize_system without giving globals")
  if _cache_globals is not None:
    raise RuntimeError ("called initialize_system more than once")
  
  os.makedirs(cache_directory, exist_ok=True)
  
  _cache_globals = cache_globals
  _cache_directory = cache_directory

def _get_code (value):
  stream = io.StringIO()
  try:
    dis.dis(value, file = stream)
  except TypeError:
    return None, None
  try:
    code2 = inspect.getsource (value)
  except (TypeError, OSError):
    return None, None
  return stream.getvalue(), code2
  
def _globals_in_code(code):
  def ignore_predefined_filter(match):
    key = match.group(1)
    return key not in globals() and not hasattr(_cache_globals["__builtins__"], key)
  return (match.group (1) for match in re.finditer(r"LOAD_GLOBAL\s+\d+\s+\(([^\)]+)\)", code) if ignore_predefined_filter(match))

class _Recursive:
  pass
class OutputHashError(Exception):
  pass
def _output_hash (key):
  #print("output_hash called", key)
  in_memory = _cache_info_by_global_key.get(key)
  if in_memory is _Recursive:
    raise OutputHashError(f"the system currently can't handle recursive functions ({key})")
  if in_memory is not None:
    if "output_hash" not in in_memory:
      raise OutputHashError("tried to get output hash of a cache thing that doesn't have one (did you refer to a run_if_changed function?")
    return in_memory ["output_hash"]
  
  _cache_info_by_global_key [key] = _Recursive
  
  if key not in _cache_globals:
    raise OutputHashError(f"tried to check current value of `{key}`, but it didn't exist; the system currently can't handle references to global keys that don't exist yet.")  
  value = _cache_globals [key]
  
  code, code2 = _get_code (value)
  if code is None:
    result = repr(value)
    if " object at 0x" in result:
      raise RuntimeError(f"Caching system made a cache dependent on a global ({key}: {result}) which contained a transient pointer; something needs to be fixed")
  else:
    #print(key, code)
    code2 = inspect.getsource (value)
    hasher = hashlib.sha256()
    #hasher.update (code.encode ("utf-8"))
    hasher.update (code2.encode ("utf-8"))
    for key2 in _globals_in_code (code):
      hasher.update (_output_hash (key2).encode ("utf-8"))
    result = hasher.hexdigest()
        
  #print(f"Info: decided that output hash of {key} is {result}")
    
  _cache_info_by_global_key [key] = {"output_hash": result}
  return result

def _path_base (key):
  return os.path.join (_cache_directory, key)
def _info_path (key):
  return _path_base (key) + ".cache_info"

  
  
def _stored_cache_info_if_valid (key, source_hash):
  info_path = _info_path (key)
  try:
    with open(info_path) as file:
      stored = json.load(file)
      if stored["source_hash"] != source_hash:
        return None
      if stored["cache_system_source_hash"] != _cache_system_source_hash:
        return None
      for key2, value in stored["accessed_globals"].items():
        try: 
          if _output_hash (key2) != value:
            return None
        except OutputHashError:
          return None
        
  except (FileNotFoundError, json.decoder.JSONDecodeError, KeyError):
    return None
    
  return stored



_generating_function_context = None

def _load_cache (key):
  path = os.path.join (_cache_directory, key)
  
  value, hash = _deserialize(path)
  _cache_info_by_global_key [key] = {"output_hash": hash}
  _cache_globals [key] = value
  
def run_if_changed (function):
  function_name = function.__name__
  
  print (f"### doing {function_name}() ###")
  code, code2 =_get_code (function)
  #print (code)
  #print(list(_globals_in_code(code)))
  #print (code2)
  hasher = hashlib.sha256()
  #hasher.update (code.encode ("utf-8")) #note: not included because it includes line numbers
  hasher.update (code2.encode ("utf-8"))
  source_hash = hasher.hexdigest()

  stored_info = _stored_cache_info_if_valid (function_name, source_hash)
  
  if stored_info is not None:
    print(f"cached version seems valid, loading it")
    _cache_info_by_global_key [function_name] = stored_info
    for key in stored_info ["saved_globals"]:
      _load_cache (key)
  else:
    start_time = datetime.datetime.now()
    print(f"needs update, rerunning… ({start_time})")
    global _generating_function_context
    if _generating_function_context is not None:
      raise RuntimeError ("cache functions cannot call other ones")
    cache_info = {
      "source_hash": source_hash,
      "cache_system_source_hash": _cache_system_source_hash,
      "accessed_globals": {key: _output_hash(key) for key in _globals_in_code(code)},
      "saved_globals": []
    }
    _generating_function_context = cache_info
    info_path = _info_path (function_name)
  
    # remove the inputs record first so that, in case of the process being terminated, we don't
    #   leave the new mismatched values alongside the old valid inputs;
    # then put the inputs back last so we can't leave the new valid inputs alongside
    #   a broken value
    try:
      os.remove (info_path)
    except FileNotFoundError:
      pass
      
    ##do the main action!
    function()
    
    _generating_function_context = None
    _cache_info_by_global_key [function_name] = cache_info
    _atomic_write_json (info_path, cache_info)
    
    finish_time = datetime.datetime.now()
    print(f"…done with {function_name}()! ({finish_time}, took {(finish_time - start_time)})")

class SaveByName:
  pass
def save (key, value = SaveByName):
  # you can save a global by name:
  if value is SaveByName:
    value = _cache_globals[key]

  _serialize (_path_base (key), value)
  if _generating_function_context is not None:
    _generating_function_context["saved_globals"].append (key)
  
  # note: always reload the cache instead of using the one that was just generated in memory,
  # to make sure it is properly canonicalized
  _load_cache (key)
  
  
def save_STL (key, shape):
  BuildMesh (shape)
  SaveSTL_raw (_path_base (key) + ".stl", shape)
  # note that we haven't implemented reloading STL, so for now, do NOT store it anywhere in the globals
        
################################################################
###########################  UI  ###############################
################################################################

import argparse

def initialize_system (cache_globals, argument_parser = None):
  if argument_parser is None:
    argument_parser = argparse.ArgumentParser()
  parser = argument_parser
  parser.add_argument ("--cache-directory", type=str, required=True)
  parser.add_argument ("--skip-previews", action="store_true")
  parse_result = parser.parse_args()
  
  import __main__
  main_name = os.path.splitext(os.path.basename (__main__.__file__))[0]
  specific_cache_directory = os.path.join (parse_result.cache_directory, main_name)
  
  _initialize_cache_system(cache_globals, specific_cache_directory)
  global skip_previews
  skip_previews = parse_result.skip_previews
  
  announcement =f"####### doing {main_name} #######"
  extra = "#"*len (announcement)
  print (extra)
  print (announcement)
  print (extra)

  return parse_result

  
def preview(*preview_shapes, width=2000, height=1500):
  if skip_previews:
    print (f"Skipping preview of: {preview_shapes}")
  else:
    print (f"Previewing: {preview_shapes}")
    from OCCT.Visualization.QtViewer import ViewerQt
    v = ViewerQt(width=width, height=height)
    for shape in recursive_flatten (preview_shapes):
      if isinstance (shape, Point):
        shape = Vertex (shape)
      if isinstance (shape, Curve):
        shape = Edge (shape)
      if isinstance (shape, Surface):
        shape = Face (shape)
      v.display_shape(unwrap(shape))
    v.start()
  