import inspect
import numbers

import FreeCAD
import Part

from forbiddenfruit import curse

def document():
  return FreeCAD.activeDocument()
def vector(*arguments):
  return FreeCAD.Vector (*arguments)
  
def width (argument):
    if isinstance (argument, numbers.Number):
      return argument
    return argument.width()
  
def minimum (argument):
    if isinstance (argument, numbers.Number):
      return 0
    return argument.minimum()
    
def box (*arguments, origin = vector()):
  if len (arguments) == 1:
    arguments = arguments*3
  if len (arguments) != 3:
    raise InputError ("box() must take either 1 or 3 arguments")
  
  result = Part.makeBox (*[width (argument) for argument in arguments])
  result.translate (origin + vector (*[minimum (argument) for argument in arguments]))
  return result

def fancy_extrude (input, direction, range_argument = 1):
  result = input.extrude (direction*width (range_argument))
  result.translate (direction*minimum (range_argument))
  return result
  

class centered():
  def __init__(self, width, on = 0):
    self._width = width
    self.on = on
  def width (self):
    return self._width
  def minimum (self):
    return self.on - self._width/2

class bounds():
  def __init__(self, min, max):
    self.min = min
    self.max = max
  def width (self):
    return self.max - self.min
  def minimum (self):
    return self.min

operations_to_make_applied_version_of = [
  ("translate", "translated"),
  ("scale", "scaled"),
  ("rotate", "rotated"),
  ("reverse", "reversed"),
  ("mirror", "mirrored"),
]

for operation_name, applied_name in operations_to_make_applied_version_of:
  def applied (self,*arguments,**keyword_arguments):
    result = self.copy()
    result.translate (*arguments)
    return result
  globals() [applied_name] = applied

def curse_freecad_types():
  for value in vars (Part).values():
    if inspect.isclass (value):
      part_class = value
      for operation_name, applied_name in operations_to_make_applied_version_of:
        curse (part_class, applied_name, globals() [applied_name])
      curse (part_class, "to_face", lambda part: Part.Face (part))
      curse (part_class, "fancy_extrude", fancy_extrude)
  
  curse (Part.Shape, "to_wire", lambda part: Part.Wire (part.Edges))
  curse (FreeCAD.Vector, "copy", lambda v: v + vector())
  curse (FreeCAD.Vector, "normalized", lambda v: v.copy().normalize())

