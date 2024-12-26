import math
from gcode_stuff.gcode_utils import *
from pyocct_system import *
from face_depthmap_loader import depthmap_sample
initialize_pyocct_system()

def layer_points(z, zbase):
  result = []
  prev_y = None
  cutoff = 58 - max(0, (z - 8)*0.4)
  def do_cutoff_midpoint(good, xg, bad, xb):
    frac = (good - cutoff)/(good - bad)
    result.append(Point(Between(xg, xb, frac),cutoff,z - zbase))
  for x in range(-100,101):
    y = depthmap_sample(x, z)
    if y is not None:
      if y <= cutoff:
        if prev_y is not None and prev_y > cutoff:
          do_cutoff_midpoint(y, x, prev_y, x-1)
        result.append(Point(x,y,z - zbase))
      elif prev_y is not None and prev_y <= cutoff:
        do_cutoff_midpoint(prev_y, x-1, y, x)
    prev_y = y
  return result
def points(layer_height):
  zbase = -35
  z = zbase
  result = []
  while z < 70:
    l = layer_points(z, zbase - layer_height)
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
  for layer in layers:
    if len(layer) == 0:
      continue
    commands.append(fastmove(*layer[0]))
    prev = layer[0]
    for p in layer[1:]:
      extrusion += (p - prev).length() * layer_height * line_width
      commands.append(g1(*p,extrusion))
      prev = p

  return wrap_gcode("\n".join(commands))

export_string(gcode(0.5, 0.3), "face_depthmap_singlewall.gcode")
print("done!")


