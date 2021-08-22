import math

from pyocct_system import *
initialize_system (globals())


wall_thickness = 0.8
plate_thickness = 1.8


CPAP_outer_radius = 21.5/2
CPAP_inner_radius = CPAP_outer_radius - wall_thickness

fan_exit_width = 24.8
fan_exit_length = 53

plate_width_left = 12
plate_width_right = 14
plate_width_front = 1.8
plate_width_back = 3.9
plate_length_total = plate_width_left + plate_width_right + fan_exit_length
plate_width_total = plate_width_front + plate_width_back + fan_exit_width


def CPAP_hoops(base, direction):
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
  #o2 = o2 @ Translate(jiggle)
  interior = Compound(i1, i2)
  wall = Compound(o1.cut(interior), o2.cut(interior))
  save ("fan_to_CPAP", wall)
  save ("fan_to_CPAP_interior", interior)
  
@run_if_changed
def make_support():
  corner = Point(0,0,33)
  lots = 100
  uncut = Face(Wire([
    corner,
    corner + Vector(0,lots,-lots),
    corner + Vector(0,lots,lots),
    corner + Vector(0,-lots,lots),
    corner + Vector(0,-lots,-lots),
  ], loop = True)).extrude(Right*wall_thickness, centered=True)
  support = Intersection(uncut, fan_to_CPAP_interior)
  save ("support", support)

@run_if_changed
def make_plate():
  plate = Vertex(
    -fan_exit_length/2 - plate_width_left,
    -fan_exit_width/2 - plate_width_front,
    0
  ).extrude(Right*plate_length_total).extrude(Back*plate_width_total).extrude(Up*plate_thickness)
  
  hole = (Vertex(Origin)
    .extrude(Right*(fan_exit_length), centered=True)
    .extrude(Back*(fan_exit_width), centered=True)
    .extrude(Up*100, centered=True))
  
  reinforcement_base = (Vertex(Origin+Up*plate_thickness)
      .extrude(Right*(fan_exit_length+plate_thickness*2), centered=True)
      .extrude(Back*(fan_exit_width+plate_thickness*2), centered=True)
      .outer_wire())
  
  reinforcement_top = (Vertex(Origin+Up*10)
      .extrude(Right*(fan_exit_length+wall_thickness*1.8), centered=True)
      .extrude(Back*(fan_exit_width+wall_thickness*1.8), centered=True)
      .outer_wire())
  
  reinforcement = Loft([reinforcement_base, reinforcement_top], solid=True)
  
  plate = Compound(
    plate.cut(hole),
    reinforcement.cut(hole),
  )
  save ("plate", plate)
  adapter_with_plate = Compound(fan_to_CPAP, plate, support)
  save("adapter_with_plate", adapter_with_plate)
  save_STL("adapter_with_plate", adapter_with_plate)
  

preview(adapter_with_plate)