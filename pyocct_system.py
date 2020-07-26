import datetime
import hashlib
import dis
import functools
import re
import os
import os.path
from OCCT.BOPAlgo import BOPAlgo_Options
from OCCT.Exchange

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
  
  if type (cache_globals) is not dict:
    raise RuntimeError ("called initialize_system without giving globals")
  if _cache_globals is not None:
    raise RuntimeError ("called initialize_system more than once")
  
  _cache_globals = cache_globals
  _cache_directory = cache_directory




def _load_cache (path):
  path = os.path.abspath(path)
  base, ext = os.path.splitext(path)
  
  if ext == ".json":
    with open(path) as file:
      result = json.load(file)
  elif ext == ".brep":
    result = ExchangeBasic.read_brep(path)
  else:
    raise RuntimeError(f"{ext} filetype not currently supported by pyocct_system.load_cache")
  
  return result

def _save_cache (path, value, inputs_path, inputs):
  path = os.path.abspath(path)
  base, ext = os.path.splitext(path)
  
  # remove the inputs record first so that, in case of the process being terminated, we don't
  #   leave the new mismatched values alongside the old valid inputs;
  # then put the inputs back last so we can't leave the new valid inputs alongside
  #   a broken value
  os.remove (inputs_path)
  
  temp_path = base + ".temp"
  if ext == ".json":
    with open(temp_path, "w") as file:
      json.dump (value, file)
      file.flush()
      os.fsync(file.fileno())
  elif ext == ".brep":
    ExchangeBasic.write_brep(value, temp_path)
  else:
    raise RuntimeError(f"{ext} filetype not currently supported by pyocct_system.cached")
    
  os.replace (temp_path, path)
  
  with open(temp_path, "w") as file:
    json.dump (inputs, file)
    file.flush()
    os.fsync(file.fileno())
  os.replace (temp_path, inputs_path)
  
def _globals_in_code(code):
  return (match.group (1) for match in re.finditer(r"LOAD_GLOBAL\s+\d+\s+\(([^\)]+)\)", code))
  
def _was_updated(global_key):
  stored = _cache_info_by_global_key.get(global_key)
  if stored is not None:
    return stored ["was_updated"]
  
  
def _cache_is_valid (inputs_path, source_hash):
  try:
    with open(inputs_path) as file:
      stored_inputs = file.read()
      if stored_inputs["source_hash"] != source_hash:
        return False
      for key, value in stored_inputs["globals"].items():
        cache_info = _cache_info_by_global_key.get(key)
        if cache_info is not None:
          if cache_info["was_updated"]:
            return False
        else:
          if _cache_globals [key] != value:
            return False
        
  except FileNotFoundError:
    return False
    
  return True

def _get_cached(path, generate):
  path = os.path.abspath(path)
  base, ext = os.path.splitext(path)
  code = dis.dis(generate)
  source_hash = hashlib.sha256(code).hexdigest()
  inputs_path = base + ".inputs"
  cache_info = {"was_updated": False}
  if !_cache_is_valid (inputs_path, source_hash):
    cache_info["was_updated"] = True
    new_result = generate()
    inputs = {
      "source_hash": source_hash,
      "globals": {key:_cache_globals [key] for key in _globals_in_code(code)},
    }
    save_cache (path, new_result, inputs_path, inputs)
    
  
  # note: always reload the cache instead of using the one that was just generated in memory,
  # to make sure it is properly canonicalized
  return cache_info, _load_cache (path)
    
    
def cached(path):
  def decorate(generate):
    cache_info, value = _get_cached(path, generate)
    _cache_info_by_global_key[generate.__name__] = cache_info
    return value


      