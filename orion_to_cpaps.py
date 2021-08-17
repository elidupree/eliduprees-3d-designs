import math

from pyocct_system import *
initialize_system (globals())


wall_thickness = 0.6


CPAP_outer_radius = 21.5/2
CPAP_inner_radius = CPAP_outer_radius - wall_thickness

fan_exit_width = 24
fan_exit_length = 53


def CPAP_hoops(base, direction):
  num = 5
  return [[
    Wire (Edge (Circle (Axes (base + direction*i, direction), radius)))
    for i in subdivisions(0, 25, amount=10)
  ] for radius in [CPAP_inner_radius, CPAP_outer_radius]]
  
def fan_hoops(offset):
  return [
    Vertex(Origin+Up*z)
      .extrude(Right*(fan_exit_length+offset*2), centered=True)
      .extrude(Back*(fan_exit_width+offset*2), centered=True)
      .outer_wire()
  for z in subdivisions(0, 10, amount=5)
]

def fan_to_one_CPAP(offset_dir):
  cinner, couter = CPAP_hoops(Point(0,0,40) + offset_dir*16, Up)
  inner = Loft(
    [a @ Translate(Down*0.001) for a in fan_hoops(0)]
    +[a @ Translate(Up*0.001) for a in cinner], solid=True)
  outer = Loft(fan_hoops(wall_thickness)+couter, solid=True)
  return inner, outer

@run_if_changed
def make_fan_to_CPAP():
  i1, o1 = fan_to_one_CPAP(Left)
  i2, o2 = fan_to_one_CPAP(Right)
  jiggle = Right*0.02 + Back*0.03 + Up*0.0001
  i2 = i2 @ Translate(jiggle)
  o2 = o2 @ Translate(jiggle)
  wall = (Union(o1, o2)).cut(i1).cut(i2)
  save ("fan_to_CPAP", wall)
  
preview(fan_to_CPAP)