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

BOPAlgo_Options.SetParallelMode_(True)

def _watch_time(name, func):
  start = datetime.datetime.now()
  result = func()
  finish = datetime.datetime.now()
  duration = finish - start
  seconds = duration.total_seconds()
  if seconds > 0.1:
    print(f"operation {name} took {seconds} seconds")
  return result



class Wrapper:
  def __init__(self, inner, supername = None):
    self.inner = inner
    self.name = inner.__name__
    if supername is not None:
      self.name = supername + self.name
  def __call__(self, *args, **kwargs):
    return watch_time(self.name, lambda: self.inner(*args, **kwargs))
  def __getattr__(self, name):
    inner_attribute = getattr(self.inner)
    if type(inner_attribute) is not Wrapper:
      return Wrapper(inner_attribute, self.name)
    return inner_attribute


_ExchangeBasic = Wrapper(OCCT.Exchange.ExchangeBasic)

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
  return (match.group (1) for match in re.finditer(r"LOAD_GLOBAL\s+\d+\s+\(([^\)]+)\)", code))

class Recursive:
  pass
class OutputHashError(Exception):
  pass
def _output_hash (key):
  #print("output_hash called", key)
  in_memory = _cache_info_by_global_key.get(key)
  if in_memory is Recursive:
    raise OutputHashError("the system currently can't handle recursive functions")
  if in_memory is not None:
    return in_memory ["output_hash"]
  
  _cache_info_by_global_key [key] = Recursive
  
  if key not in _cache_globals:
    raise OutputHashError("the system currently can't handle references to global keys that don't exist yet")  
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
    ExchangeBasic.write_brep(value, temp_path)
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


      