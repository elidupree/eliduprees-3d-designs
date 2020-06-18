import inspect
import numbers
import math
import numpy

import FreeCAD
import Part
import Mesh
import FreeCADGui as Gui

from forbiddenfruit import curse

def print(x):
  FreeCAD.Console.PrintMessage (str(x)+"\n")

def document():
  return FreeCAD.activeDocument()

def vector(*arguments, angle = None, length = 1):
  if angle is not None:
    return FreeCAD.Vector (length*math.cos(angle), length*math.sin (angle))
  if len (arguments) > 0 and type(arguments [0]) is Part.Point:
    return FreeCAD.Vector (arguments [0].X, arguments [0].Y, arguments [0].Z)
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

def arc_center (endpoints, radius):
  delta = (endpoints [1] - endpoints [0])/2
  adjacent = delta.Length
  opposite = math.sqrt (radius**2 - adjacent**2)
  return endpoints [0] + delta + vector (- delta [1], delta [0]).normalized()*(opposite*numpy.sign (radius))

def arc_midpoint (endpoints, radius, direction = 1):
  delta = (endpoints [1] - endpoints [0])/2
  adjacent = delta.Length
  #print (radius, adjacent)
  opposite = math.sqrt (radius**2 - adjacent**2)
  return endpoints [0] + delta + vector (- delta [1], delta [0]).normalized()*(opposite*numpy.sign (radius) - radius*direction)

def point_circle_tangent (point, circle, direction = 1):
  center, radius = circle
  delta = point - center
  distance = delta.Length
  angle = math.atan2 (delta [1], delta [0])
  radius = radius*direction
  flip = numpy.sign (radius)
  radius = abs (radius)
  angle_offset = math.acos (radius/distance)
  tangent_angle = angle + angle_offset*flip
  return center + vector (radius*math.cos (tangent_angle), radius*math.sin (tangent_angle))

def circle_circle_tangent_segment (circle_1, circle_2, direction_1 = 1, direction_2 = 1):
  center_1, radius_1 = circle_1
  center_2, radius_2 = circle_2
  radius_1 = radius_1*direction_1
  radius_2 = radius_2*direction_2
  center = (center_1*radius_2 - center_2*radius_1)/(radius_2 - radius_1)
  flip_1 = 1
  flip_2 = 1
  if numpy.sign (radius_1) == numpy.sign (radius_2):
    if abs (radius_1) < abs (radius_2):
      flip_1 = -1
    else:
      flip_2 = -1
  return point_circle_tangent (center, (center_1, - flip_1*radius_1)), point_circle_tangent (center, (center_2, flip_2*radius_2))


def show (shape, name, invisible = False):
  if type(shape) is Mesh.Mesh:
    Mesh.show (shape, name)
  else:
    Part.show (shape, name)
  if invisible:
    Gui.getDocument ("Something").getObject (name).Visibility = False

def show_invisible (shape, name):
  show(shape, name, invisible = True)
  


operations_to_make_applied_version_of = [
  ("translate", "translated"),
  ("scale", "scaled"),
  ("rotate", "rotated"),
  ("reverse", "reversed"),
]

for operation_name, applied_name in operations_to_make_applied_version_of:
  def applied(operation_name, applied_name):
    def applied (self,*arguments,**keyword_arguments):
      result = self.copy()
      #print (operation_name)
      getattr(result, operation_name) (*arguments)
      return result
    return applied
  globals() [applied_name] = applied(operation_name, applied_name)

def curse_freecad_types():
  for value in vars (Part).values():
    if inspect.isclass (value):
      part_class = value
      for operation_name, applied_name in operations_to_make_applied_version_of:
        curse (part_class, applied_name, globals() [applied_name])
      curse (part_class, "to_face", lambda part: Part.Face (part))
      curse (part_class, "fancy_extrude", fancy_extrude)
      curse (part_class, "as_xz", lambda part: part.rotated(vector(), vector (1, 0, 0), 90))
      curse (part_class, "as_yz", lambda part: part.rotated(vector(), vector (0, 1, 0), 90).rotated(vector(), vector (1, 0, 0), 90))
  
  curse (Part.Shape, "to_wire", lambda part: Part.Wire (part.Edges))
  curse (FreeCAD.Vector, "copy", lambda v: v + vector())
  curse (FreeCAD.Vector, "normalized", lambda v: v.copy().normalize())
  curse (FreeCAD.Vector, "angle", lambda v: math.atan2(v[1],v[0]))
  curse (FreeCAD.Vector, "rotated", lambda v, amount: vector (angle = v.angle() + amount, length = v.Length))
