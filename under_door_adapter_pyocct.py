import math

from pyocct_system import *
initialize_pyocct_system()

from air_adapters import elidupree_4in_threshold, elidupree_4in_leeway_one_sided, elidupree_4in_intake_inner_radius, elidupree_4in_output_outer_radius


wall_thickness = 1.0
inch = 25.4

def circle_wire(radius, index):
  dirv = Direction(-1, 0, 0) #Direction(-1.3, 0, 1)
  start = Point (-80,0,
                  0 #18
                  - dirv[0]*radius)
  return Wire (Edge (Circle (Axes (start + Vector (dirv)*index*2.5, dirv), radius)))
  
zigzag_depth = 3
curved_zigzag_offset = zigzag_depth*2/3
top = 30 - curved_zigzag_offset

def loop_pairs(points):
  return [(a,b) for a,b in zip(points, points[1:] + points[:1])]
def range_thing(increments, start, end):
  dist = end - start
  factor = 1/(increments - 1)
  return (start + dist*i*factor for i in range(increments))

under_door_half_width = 1 * inch - curved_zigzag_offset
corners = [
  Point (0, -under_door_half_width, curved_zigzag_offset),
  Point (0, under_door_half_width, curved_zigzag_offset),
  Point (0, under_door_half_width, top),
  Point (0, -under_door_half_width, top),
]

@run_if_changed
def under_door_wire():
  points = []
  for a,b in loop_pairs (corners):
    delta = (b - a)
    distance = delta.Magnitude()
    direction = Direction(delta)
    perpendicular = vector (0, - direction [2], direction [1])
    divisions = math.ceil(distance/12)*2 + 1
    for index, position in enumerate ( range_thing (divisions, a,b)):
      offset = 0 if index % 2 == 0 else -zigzag_depth
      if index != 0:
        points.append (position + perpendicular*offset)
  return Wire (Edge (BSplineCurve (points, BSplineDimension (periodic = True))))
# preview(under_door_wire, corners)
def half_shape(dir, radius):
  e4ins = [circle_wire(radius, index) for index in reversed(range (10))]
  loft = Loft (e4ins
    + [under_door_wire@Translate (x, 0, 0) for x in subdivisions(0, 40, amount=5)]
    , solid=True
    )
  # preview(loft, under_door_wire, corners)
  return loft
  #hollow = thicken_solid (solid, solid.Faces()[-2:], wall_thickness)
  # preview(e4ins, loft)
  offset = Offset (loft, wall_thickness,
    tolerance = 0.001,
    fill = True)
  # preview (loft, offset @ Translate (0,0,1))
  print(offset)
  return {
    "loft": loft,
    "offset": offset,
  }


# @run_if_changed
# def intake_half():
#   return half_shape (-1, elidupree_4in_intake_inner_radius)
#
#
# @run_if_changed
# def output_half():
#   return half_shape (1, elidupree_4in_output_outer_radius - wall_thickness)

small_hose_outer_radius = 46/2

@run_if_changed
def symmetric_smaller_hose_version():
  result = half_shape (-1, small_hose_outer_radius + wall_thickness)
  save_STL("under_door_adapter_smaller_hose_half_solid", result, linear_deflection=0.02)
  return result

@run_if_changed
def small_hose_spout():
  join_len = 40
  def cir(z, radius):
    return Wire (Edge (Circle (Axes (Origin + Up*z, Up), radius)))
  loft = Loft (
    [cir(z, small_hose_outer_radius + wall_thickness) for z in subdivisions(0, join_len, amount=5)]
    +
    [cir(radius + join_len, radius) for radius in subdivisions(2*inch, 4*inch, amount=20)]
               , solid=True
               )
  save_STL("small_hose_spout", loft, linear_deflection=0.02)
  preview(loft)
  return loft


@run_if_changed
def small_hose_to_sound_suppressor():
  join_len = 40
  # def cir(z, radius):
  #   return Wire (Edge (Circle (Axes (Origin + Up*z, Up), radius)))
  suppressor_radius = 15.5*inch / math.tau
  mid_len = 40
  a = Origin + Right*(small_hose_outer_radius + wall_thickness)
  c = Origin + Up*(join_len*2+mid_len)
  b = c + Right*suppressor_radius
  profile = Wire(
    [Origin, a, BSplineCurve (
       [a + Up*z for z in subdivisions(0, join_len, amount=4)]
      + [b + Up*z for z in subdivisions(-join_len, 0, amount=4)]
    ), c],
     loop = True)
  # result = Loft (
  #   [cir(z, small_hose_outer_radius + wall_thickness) for z in subdivisions(0, join_len, amount=5)]
  #   +
  #   [cir(join_len+mid_len+z, suppressor_radius) for z in subdivisions(0, join_len, amount=5)]
  #   , solid=True
  # )
  result = Revolve(profile, Up)
  save_STL("small_hose_to_sound_suppressor", result, linear_deflection=0.02)
  export("small_hose_to_sound_suppressor.stl", "small_hose_to_sound_suppressor_1.stl")
  preview(result)
  return result



preview(symmetric_smaller_hose_version)

# preview(intake_half ["offset"])
