import math
from gcode_stuff.gcode_utils import *
from pyocct_system import *
from face_depthmap_loader import depthmap_sample

def layer_points(z, zbase):
  return [Point(x,depthmap_sample(x, z),z - zbase) for x in range(-100,101)]
def points(layer_height):
  zbase = -100
  z = zbase
  result = []
  while z < 100:
    l = layer_points(z, zbase)
    z += layer_height
    if len(result) % 2 == 0:
      result.append(l)
    else:
      result.append(l[::-1])
  return result

def gcode(line_width, layer_height):
  layers = points(layer_height)
  commands = [
    'G92 E0    ; Set extruder reference point',
    'M106 S255 ; Fan 100%',
  ]
  extrusion = 0
  for l in layers:
    commands.append[fastmove(*l[0])]
    prev = l[0]
    for p in l[1:]:
      extrusion += (p - prev).length() * layer_height * line_width
      commands.append(g1(*p,extrusion))
      prev = p
  return wrap_gcode("\n".join(commands))

print(gcode(0.5, 0.3))

