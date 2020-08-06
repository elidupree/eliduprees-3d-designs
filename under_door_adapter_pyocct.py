import math

from pyocct_system import *
initialize_system (globals())

from air_adapters import elidupree_4in_threshold, elidupree_4in_leeway_one_sided, elidupree_4in_intake_inner_radius, elidupree_4in_output_outer_radius


wall_thickness = 0.5

def elidupree_4in_wire(radius, index):
  dirv = Direction(-1.3, 0, 1)
  start = Point (-100,0,18 -dirv[0]*radius)
  return Wire (Edge (Circle (Axes (start + Vector (dirv)*index*2.5, dirv), radius)))
  
zigzag_depth = -3
curved_zigzag_offset = zigzag_depth/3
top =32 - wall_thickness*2 - curved_zigzag_offset

def loop_pairs(points):
  return [(a,b) for a,b in zip(points, points[1:] + points[:1])]
def range_thing(increments, start, end):
  dist = end - start
  factor = 1/(increments - 1)
  return (start + dist*i*factor for i in range(increments))

under_door_half_width = 80
corners = [
  Point (0, -under_door_half_width, curved_zigzag_offset),
  Point (0, under_door_half_width, curved_zigzag_offset),
  Point (0, under_door_half_width, top),
  Point (0, -under_door_half_width, top),
]

@run_if_changed
def make_under_door_wire():
  points = []
  for a,b in loop_pairs (corners):
    delta = (b - a)
    distance = delta.Magnitude()
    direction = Direction(delta)
    perpendicular = vector (0, - direction [2], direction [1])
    divisions = math.ceil(distance/12)*2 + 1
    for index, position in enumerate ( range_thing (divisions, a,b)):
      offset = 0 if index % 2 == 0 else zigzag_depth
      if index != 0:
        points.append (position + perpendicular*offset)
  save ("under_door_wire", Wire (Edge (BSplineCurve (points, BSplineDimension (periodic = True)))))
  
def half_shape(dir, radius):
  e4ins = [elidupree_4in_wire(radius, index) for index in reversed(range (10))]
  loft = Loft (e4ins
    + [under_door_wire@Translate (40*(index-5)/10, 0, 0) for index in range (6)]
    #, solid=True
    )
  #hollow = thicken_solid (solid, solid.Faces()[-2:], wall_thickness)
  offset = Offset (loft, wall_thickness,
    tolerance = 0.001,
    fill = True)
  print(offset)
  return {
    "loft": loft,
    "offset": offset,
  }


@run_if_changed
def make_intake_half():
  save("intake_half", half_shape (-1, elidupree_4in_intake_inner_radius))


@run_if_changed
def make_output_half():
  save("output_half", half_shape (1, elidupree_4in_output_outer_radius - wall_thickness))



preview(intake_half ["offset"])
