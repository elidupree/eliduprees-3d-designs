import datetime
import hashlib
import dis
import inspect
import functools
import itertools
import re
import sys
import os
import os.path
import json
import traceback
import io
import builtins
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
      assert(type (wrapped_object) not in types_not_to_wrap)
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

      if type (value) in [list, tuple]:
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
          c = self.globals [class_name]
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

  def atomic_write_json (file_path, value):
    temp_path = file_path + ".temp"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(temp_path, "w") as file:
      json.dump (value, file)
      file.flush()
      os.fsync(file.fileno())
    os.replace (temp_path, file_path)

  def serialize(path_base, value):
    with_placeholders = Serializer (path_base).serialized (value)
    atomic_write_json (path_base + ".json", with_placeholders)

  def deserialize(g, path_base):
    hasher = hashlib.sha256()
    path = path_base + ".json"
    with open(path) as file:
      with_placeholders = json.load(file)
    with open(path, "rb") as file:
      hasher.update (file.read())

    result = Deserializer (g, path_base, hasher).deserialized (with_placeholders)
    return result, hasher.hexdigest()

  return serialize, deserialize, atomic_write_json


_serialize, _deserialize, _atomic_write_json = _setup_serialization()


##########################################################
###################   Caching system   ###################
##########################################################


_cache_directory = None
_cache_info_by_global_key = {}
_global_location_by_deserialized_object_id = {}

_cache_system_source = inspect.getsource (sys.modules [__name__]) + inspect.getsource (sys.modules ["pyocct_api_wrappers"])
_cache_system_source_hash = hashlib.sha256(_cache_system_source.encode ("utf-8")).hexdigest()

def _initialize_cache_system (cache_directory):
  global _cache_directory

  if _cache_directory is not None:
    raise RuntimeError ("called initialize_pyocct_system more than once")
  
  os.makedirs(os.path.join(cache_directory, "cache_info"), exist_ok=True)

  _cache_directory = cache_directory

def _get_code (value):
  if value is None:
    return None, None
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
  
def _globals_loaded_by_code(code):
  def ignore_predefined_filter(match):
    name = match.group(1)
    return name not in globals() and not hasattr(builtins, name)
  return sorted(set(match.group (1) for match in re.finditer(r"LOAD_GLOBAL\s+\d+\s+\(([^\)]+)\)", code) if ignore_predefined_filter(match)))
def _globals_stored_by_code(code):
  return sorted(set(match.group (1) for match in re.finditer(r"STORE_GLOBAL\s+\d+\s+\(([^\)]+)\)", code)))

def _global_key(g, name):
  """
  :param g: The relevant dictionary-of-globals.
  :param name: The key within that dictionary.
  :return: A key to identify this pair within _cache_info_by_global_key.
  """
  return g["__name__"], name

class _ChecksumOfGlobalError(Exception):
  pass
def _checksum_of_global (g, name, stack = []):
  """
  A checksum for a global value.
  For functions, this hashes together both the code and all globals referenced by the function.
  The result should never be the same for different values, although there's no hard guarantee of this,
  and it depends on the assumption that globals never change after being checked.

  :param g: The relevant dictionary-of-globals.
  :param name: The key within that dictionary.
  :param stack: Other names that led to this, just to prevent infinite recursion.
  :return: A string checksum for g[name].
  """
  #print("checksum called", name)
  key = _global_key(g, name)
  if key in stack:
    raise _ChecksumOfGlobalError(f"the system currently can't handle recursive functions ({key}, {stack})")

  #print(_global_key(g, name))
  in_memory = _cache_info_by_global_key.get(key)
  if in_memory is not None:
    if "checksum" not in in_memory:
      raise _ChecksumOfGlobalError("tried to get checksum of a cache thing that doesn't have one (did you refer to a run_if_changed function?")
    return in_memory ["checksum"]

  if name not in g:
    raise _ChecksumOfGlobalError(f"tried to check current value of `{g['__name__']}.{name}`, but it didn't exist; the system currently can't handle references to global keys that don't exist yet.")
  value = g[name]

  code, code2 = _get_code (value)
  if id(value) in _global_location_by_deserialized_object_id:
    g2, name2 = _global_location_by_deserialized_object_id[id(value)]
    result = _checksum_of_global (g2, name2, stack + [key])
  elif code is None:
    result = repr(value)
    if " object at 0x" in result:
      raise RuntimeError(f"Caching system made a cache dependent on a global ({key}: {result}) which contained a transient pointer; something needs to be fixed")
  else:
    #print(key, code)
    code2 = inspect.getsource (value)
    hasher = hashlib.sha256()
    #hasher.update (code.encode ("utf-8"))
    hasher.update (code2.encode ("utf-8"))
    for name2 in _globals_loaded_by_code (code):
      g2 = vars(sys.modules[value.__module__])
      hasher.update (_checksum_of_global (g2, name2, stack + [key]).encode ("utf-8"))
    result = hasher.hexdigest()
        
  #print(f"Info: decided that output hash of {key} is {result}")
    
  _cache_info_by_global_key[key] = {"checksum": result}
  return result

def _module_cache_path (g):
  if g["__name__"] == "__main__":
    return _cache_directory
  else:
    return os.path.join (_cache_directory, g["__name__"])
def _cache_path_base (g, name):
  return os.path.join (_module_cache_path (g), name)
def _cache_info_path (g, name):
  return _cache_path_base (g, name) + ".cache_info"

  
  
def _stored_cache_info_if_valid (g, name, source_hash):
  info_path = _cache_info_path (g, name)
  try:
    with open(info_path) as file:
      stored = json.load(file)
      if stored["source_hash"] != source_hash:
        return None
      if stored["cache_system_source_hash"] != _cache_system_source_hash:
        return None
      for name2, value in stored["accessed_globals"].items():
        try: 
          if _checksum_of_global (g, name2) != value:
            return None
        except _ChecksumOfGlobalError:
          return None
        
  except (FileNotFoundError, json.decoder.JSONDecodeError, KeyError):
    return None
    
  return stored



_generating_function_context = None

def _load_cache (g, name):
  path = _cache_path_base (g, name)
  
  value, checksum = _deserialize(g, path)
  _cache_info_by_global_key [_global_key(g, name)] = {"checksum": checksum}
  _global_location_by_deserialized_object_id[id(value)] = (g, name)
  return value

_last_finished_ric_function = {"name": "the start of the program", "time": datetime.datetime.now()}
  
def run_if_changed (function):
  function_name = function.__name__
  g = function.__globals__
  key = _global_key(g, function_name)
  print (f"### doing {function_name}() ###")
  
  global _last_finished_ric_function
  seconds = (datetime.datetime.now() - _last_finished_ric_function["time"]).total_seconds()
  if seconds > 0.1:
    print(f"""(It's been {seconds} seconds since {_last_finished_ric_function["name"]}, maybe there's some expensive stuff not wrapped in a @run_if_changed function?)""")
  
  
  code, code2 =_get_code (function)
  #print (code)
  #print(list(_globals_loaded_by_code(code)))
  #print (code2)
  hasher = hashlib.sha256()
  #hasher.update (code.encode ("utf-8")) #note: not included because it includes line numbers
  hasher.update (code2.encode ("utf-8"))
  source_hash = hasher.hexdigest()

  saved_cache_info = _stored_cache_info_if_valid (g, function_name, source_hash)
  stored_globals = _globals_stored_by_code(code)
  
  if saved_cache_info is not None:
    print(f"cached version seems valid, loading it")
    _cache_info_by_global_key [key] = saved_cache_info
  else:
    start_time = datetime.datetime.now()
    print(f"needs update, rerunning… ({start_time})")
    global _generating_function_context
    if _generating_function_context is not None:
      raise RuntimeError ("cache functions cannot call other ones")
    cache_info = {
      "source_hash": source_hash,
      "cache_system_source_hash": _cache_system_source_hash,
      "accessed_globals": {name: _checksum_of_global(g, name) for name in _globals_loaded_by_code(code)},
    }
    _generating_function_context = cache_info
    info_path = _cache_info_path (g, function_name)

    for name in stored_globals:
      if hasattr(g, name):
        raise RuntimeError("run_if_changed functions should not modify pre-existing globals")
  
    # remove the inputs record first so that, in case of the process being terminated, we don't
    #   leave the new mismatched values alongside the old valid inputs;
    # then put the inputs back last so we can't leave the new valid inputs alongside
    #   a broken value
    try:
      os.remove (info_path)
    except FileNotFoundError:
      pass
      
    ##do the main action!
    result = function()

    _serialize(_cache_path_base(g, function_name), result)
    for name in stored_globals:
      _serialize(_cache_path_base(g, name), g[name])
    _generating_function_context = None
    _cache_info_by_global_key [function_name] = cache_info
    _atomic_write_json (info_path, cache_info)
    
    finish_time = datetime.datetime.now()
    print(f"…done with {function_name}()! ({finish_time}, took {(finish_time - start_time)})")

  # note: always reload the cache instead of using the one that was just generated in memory,
  # to make sure it is properly canonicalized
  result = _load_cache (g, function_name)
  for name in stored_globals:
    g[name] = _load_cache (g, name)
  _last_finished_ric_function = {"name": function_name + "()", "time": datetime.datetime.now()}
  return result

class _SaveByName:
  pass
def save (_key, _value = _SaveByName):
  raise RuntimeError("save() is deprecated. Just return values from a run_if_changed function.")

def save_BREP (name, shape):
  shape.write_brep (os.path.join (_cache_directory, name)+".brep")
  
def save_STL (name, shape, **kwargs):
  BuildMesh (shape, **kwargs)
  SaveSTL_raw (os.path.join (_cache_directory, name) + ".stl", shape)
  # note that we haven't implemented reloading STL, so for now, do NOT store it anywhere in the globals
    
def save_STEP (name, shape, **_kwargs):
  SaveSTEP_raw(os.path.join (_cache_directory, name) + ".step", shape)
  
  
########################################################################
########  SVG bureaucracy  #######
########################################################################


def wire_svg_path(wire, color = "black"):
  edges = wire.edges()
  start = edges[0].vertices()[0]
  parts = [f'<path stroke="{color}" d="M {start[0]} {start[1]}']
  for edge in edges:
    end = edge.vertices()[1]
    if (end[0], end[1]) == (start[0], start[1]):
      parts.append(f' Z')
    else:
      parts.append(f' L {end[0]} {end[1]}')
  parts.append(f'" />')
  return "".join(parts)
  
def save_inkscape_svg(name, wires):
  wires = recursive_flatten(wires)
  colors = ["black", "red", "green", "blue"]
  contents = "\n".join([
    wire_svg_path(wire, color) for wire, color in zip(wires, itertools.cycle(colors))
  ])
  filename = os.path.join (_cache_directory, name)+".svg"
  file_data = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!-- Created with Inkscape (http://www.inkscape.org/) -->

<svg
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:cc="http://creativecommons.org/ns#"
 xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns:svg="http://www.w3.org/2000/svg"
 xmlns="http://www.w3.org/2000/svg"
 xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
 xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
 width="8.5in"
 height="11in"
 viewBox="0 0 215.9 279.4"
 version="1.1"
 id="svg8"
 inkscape:version="0.91 r13725"
 sodipodi:docname="'''+filename+'''">
<defs
   id="defs2" />
<sodipodi:namedview
   id="base"
   pagecolor="#ffffff"
   bordercolor="#666666"
   borderopacity="1.0"
   inkscape:pageopacity="0.0"
   inkscape:pageshadow="2"
   inkscape:zoom="0.35"
   inkscape:cx="437.51443"
   inkscape:cy="891.42856"
   inkscape:document-units="mm"
   inkscape:current-layer="layer1"
   showgrid="false"
   inkscape:window-width="1328"
   inkscape:window-height="1022"
   inkscape:window-x="363"
   inkscape:window-y="123"
   inkscape:window-maximized="0"
   units="in" />
<metadata
   id="metadata5">
  <rdf:RDF>
    <cc:Work
       rdf:about="">
      <dc:format>image/svg+xml</dc:format>
      <dc:type
         rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
      <dc:title></dc:title>
    </cc:Work>
  </rdf:RDF>
</metadata>
<g
   inkscape:label="Layer 1"
   inkscape:groupmode="layer"
   id="layer1">
   <g fill="none"
      stroke="rgb(0, 0, 0)"
      stroke-linecap="butt"
      stroke-linejoin="miter"
      stroke-width="1.0"
      transform="scale(1,-1)"
      >
    '''+contents+'''
    </g>
</g>
</svg>'''
  with open(filename, "w") as file:
    file.write(file_data)

def center_vertices_on_letter_paper(vertices):
  if type(vertices) is list:
    v = vertices
    vertices = lambda: v
  offset = vector(
    (215.9 - (max (vertex [0] for vertex in vertices()) + min (vertex [0] for vertex in vertices())))/2,
    (-279.4 - (max (vertex [1] for vertex in vertices()) + min (vertex [1] for vertex in vertices())))/2,
    0,
  )
  for vertex in vertices():
    vertex[0] += offset[0]
    vertex[1] += offset[1]

        
################################################################
###########################  UI  ###############################
################################################################

import argparse

def initialize_pyocct_system (argument_parser = None):
  if argument_parser is None:
    argument_parser = argparse.ArgumentParser()
  parser = argument_parser
  parser.add_argument ("--cache-directory", type=str, required=True)
  parser.add_argument ("--skip-previews", action="store_true")
  parse_result = parser.parse_args()
  
  import __main__
  main_name = os.path.splitext(os.path.basename (__main__.__file__))[0]
  specific_cache_directory = os.path.join (parse_result.cache_directory, main_name)
  
  _initialize_cache_system(specific_cache_directory)
  global skip_previews
  skip_previews = parse_result.skip_previews
  
  announcement =f"####### doing {main_name} #######"
  extra = "#"*len (announcement)
  print (extra)
  print (announcement)
  print (extra)

  return parse_result

  
def preview(*preview_shapes, width=2000, height=1500):
  global _last_preview_start
  seconds = (datetime.datetime.now() - _last_preview_start).total_seconds()
  print(f"""(It's been {seconds} seconds since the start of the program (or last preview))""")
  if skip_previews:
    print (f"Skipping preview of: {preview_shapes}")
  else:
    caller = traceback.extract_stack()[-2]
    print (f"Previewing ({os.path.basename(caller.filename)}:{caller.lineno}): {preview_shapes}")
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
  _last_preview_start = datetime.datetime.now()
    
_last_finished_ric_function = {"name": "the start of the program", "time": datetime.datetime.now()}
_last_preview_start = datetime.datetime.now()