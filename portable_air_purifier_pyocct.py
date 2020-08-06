import math

from pyocct_system import *
initialize_system (globals())


wall_thickness = 0.8

# extra leeway in addition to the wall expansion, for rigid parts that need to fit into a slot, so that printing irregularities don't make them not fit.
# 0.15 is a good amount generically, but I happen to know that my diagonal printing process adds about 0.25 on each side as well
tight_leeway = 0.15 + 0.25

strong_filter_length = 151.9
strong_filter_width = 101
strong_filter_depth_without_seal = 14
strong_filter_seal_depth_expanded = 2
strong_filter_seal_squish_distance = 0.5
strong_filter_seal_depth_squished = strong_filter_seal_depth_expanded - strong_filter_seal_squish_distance
strong_filter_depth_with_seal = strong_filter_depth_without_seal + strong_filter_seal_depth_squished
 
fan_thickness = 28 + tight_leeway*2
fan_width = 79.7 + tight_leeway*2
fan_length = 78.9 + tight_leeway*2
fan_exit_width = 26 + tight_leeway*2
fan_exit_length = 8
fan_intake_circle_measured_radius = 24.4
fan_intake_circle_center_from_front = tight_leeway + 40.3
fan_intake_circle_center_from_left = tight_leeway + 44
fan_intake_circle_center_to_back = fan_length - fan_intake_circle_center_from_front
fan_intake_circle_center_to_right = fan_width - fan_intake_circle_center_from_left

battery_thickness = 27.8 + tight_leeway*2
battery_width = 85.5 + tight_leeway*2
battery_length = 144.2 + tight_leeway*2
battery_cord_diameter = 3.5
battery_socket_diameter = 11.4
battery_socket_length = 38.2

fan_cord_socket_slit_width = 15
fan_cord_socket_slit_length = 40

lots = 500

strong_filter_rim_inset = 6
strong_filter_airspace_wall_inset = strong_filter_rim_inset
strong_filter_size = Vector (
  strong_filter_length,
  strong_filter_width,
  strong_filter_depth_with_seal
)
strong_filter_min = Point (0, 0, 0)
strong_filter_max = strong_filter_min + strong_filter_size
strong_filter_center = strong_filter_min + (strong_filter_size/2)
strong_filter_seal_bottom = strong_filter_max[2] - strong_filter_seal_depth_squished

CPAP_outer_radius = (22/2)
CPAP_inner_radius = CPAP_outer_radius-wall_thickness


# only go one third of the way down, so there's a small airgap, meaning that any leakage around the intake side of the filter will be released into the unfiltered air instead of sneaking forward into the air that should be filtered
strong_filter_cover_depth = strong_filter_depth_with_seal/3
  
strong_filter_output_part_bottom_corner = strong_filter_min + vector (
      -wall_thickness,
      -wall_thickness,
      
      strong_filter_depth_with_seal - strong_filter_cover_depth
    )


def approximate_edges(edges):
  result = []
  for edge in edges:
    curve, start, finish = edge.Curve()
    for parameter in subdivisions (start, finish, amount = 9)[1:]:
      result.append (curve.Value (parameter))
  return result

@cached
def strong_filter_to_CPAP_wall():
  wall_inner_radius = wall_thickness*0.5
  wall_outer_radius = wall_thickness*1.5
  filter_inset = vector(all = strong_filter_airspace_wall_inset).projected_perpendicular (Up)
  center_to_corner = (strong_filter_size).projected_perpendicular (Up)/2
  center_to_inset = center_to_corner - filter_inset
  base_point = strong_filter_center.projected(Plane(Origin, Up))
  upstep = 5
  
  flat_before_upstep_vertex = Vertex (-strong_filter_airspace_wall_inset - 6, 0, 7)
  upstep_vertex = Vertex (-strong_filter_airspace_wall_inset - 1, 0, 5)
  inset_vertex = Vertex (-strong_filter_airspace_wall_inset, 0, 0)
  corner_vertex = Vertex (-0.2, 0, 0)
  cover_vertex = Vertex (0.8, 0, -strong_filter_cover_depth)
  skirt_vertex = Vertex (5, 0, -strong_filter_depth_with_seal)
  profile = approximate_edges(FilletedEdges([
    flat_before_upstep_vertex,
    (upstep_vertex, 3),
    (inset_vertex, wall_outer_radius),
    (corner_vertex, wall_inner_radius),
    (cover_vertex, 3),
    skirt_vertex,
  ])[1:])
  
  corners = [
    Mirror(Origin),
    Mirror(Back),
    Transform(),
    Mirror(Right),
  ]
  rim = approximate_edges(FilletedEdges([
    (base_point + center_to_corner@corner_trans, wall_inner_radius)
    for corner_trans in corners
  ], loop = True))
  inset_rim = approximate_edges(FilletedEdges([
    (base_point + center_to_inset@corner_trans, wall_inner_radius)
    for corner_trans in corners
  ], loop = True))
  #preview(Wire((Vertex(a) for a in rim)))
  
  
  right_index = next (index for index, rim_point in enumerate (rim) if abs ((rim_point - base_point) [1]) < 0.01)
  CPAP_center = Point (strong_filter_center[0] - 30, strong_filter_center[1], 0)
  CPAP_bottom_z = 15 - strong_filter_seal_depth_squished
  CPAP_top_z = CPAP_bottom_z + 25
  CPAP_directions = [Right@Rotate (Axis (Origin, Up), radians = radians) for radians in subdivisions (0, math.tau, amount = len (rim) + 1) [: -1]]
  CPAP_directions = CPAP_directions[-right_index:] + CPAP_directions[:-right_index]
  
  CPAP_profile = approximate_edges(FilletedEdges([
    Vertex (CPAP_inner_radius + 10, 0, CPAP_bottom_z-2),
    (Vertex (CPAP_inner_radius+0.5, 0, CPAP_bottom_z), 10),
    Vertex (CPAP_inner_radius, 0, CPAP_top_z),
  ])[1:])
  
  def CPAP_column (direction):
    result = []
    for point in CPAP_profile:
      result.append(CPAP_center + direction*point[0] + Up*point[2])
    
    return result
  
  def placed_profile_point(rim_point, inset_point, profile_point):
    towards_rim = Vector (inset_point, rim_point)/strong_filter_airspace_wall_inset
    return rim_point + towards_rim*profile_point[0] + Up*profile_point[2]
  
  columns = []
  
  for rim_point, inset_point, CPAP_direction in zip (rim, inset_rim, CPAP_directions):
    profile_part = [placed_profile_point (rim_point, inset_point, profile_point) for profile_point in reversed(profile)]
    CPAP_part = CPAP_column (CPAP_direction)
    columns.append (
      profile_part
      + [profile_part[-1] + (CPAP_part[0]-profile_part[-1])/2]
      + CPAP_part
    )
  print ([column [0] for column in columns])
  face = Face(BSplineSurface(columns, u = BSplineDimension (periodic = True)))
  #extra_faces = [Face (wire).Complemented() for wire in ClosedFreeWires (face)]
  #preview (Shell ([face] + extra_faces))
  #solid = Solid (Shell ([face] + extra_faces))
  #preview (solid)
  #preview(Offset(face, wall_thickness, tolerance = 0.01))
  
  preview (face)
  
  #thick = thicken_solid(solid, [f for f in solid.Faces() if all_equal(v[2] for v in f.Vertices())], wall_thickness)
  thick = Offset(face, wall_thickness, tolerance = 0.01, fill = True).Complemented()
  half_thick = Intersection(thick, HalfSpace(strong_filter_center, Left))
  mirrored = half_thick @ Mirror(Axes(strong_filter_center, Right))
  preview (thick)
  preview (half_thick)
  combined = Compound(half_thick, mirrored)
  return combined@Translate (0, 0, strong_filter_max[2])
preview(strong_filter_to_CPAP_wall)

@cached
def strong_filter_output_part():
  inset = vector(strong_filter_airspace_wall_inset, strong_filter_airspace_wall_inset, 0)
  rect_min = strong_filter_min + inset
  rect_max = strong_filter_max - inset
  
  expansion = vector (wall_thickness, wall_thickness, 0)
  
  outer_box = Box (
    strong_filter_output_part_bottom_corner,
    strong_filter_max + vector (all = wall_thickness)
  )
  
  filter_cut_box = Box (strong_filter_min, strong_filter_max)
  hole_cut_box = Box (rect_min, rect_max + Up*lots)
  
  edge_walls = Difference (outer_box, [filter_cut_box, hole_cut_box])
  
  return Compound (edge_walls, strong_filter_to_CPAP_wall)




rotate_to_diagonal_radians = math.atan(math.sqrt(2))
rotate_to_diagonal = Rotate(Axis(Origin, Direction(1, -1, 0)), radians=rotate_to_diagonal_radians)

@cached
def strong_filter_output_part_FDM_printable():
  transform = Translate(strong_filter_output_part_bottom_corner, Origin) @ rotate_to_diagonal
  result = strong_filter_output_part @ transform
  
  extra_wall_length = 60
  extra_wall_vectors = [
    (vector (Right @ rotate_to_diagonal).projected_perpendicular (Up) * extra_wall_length, 1),
    (vector (Back @ rotate_to_diagonal).projected_perpendicular (Up) * extra_wall_length, -1),
  ]
  
  # TODO: make this code less kludgy
  '''inset = (vector (
      wall_thickness,
      wall_thickness,
      0,
  ) @ rotate_to_diagonal).projected_perpendicular (Up)'''
  parts = [result]
  exclusion = Box (
      strong_filter_output_part_bottom_corner,
      strong_filter_max + Up*lots
  ) @ transform
  for offset, side in extra_wall_vectors:
    perpendicular = offset.Cross(Down)*side
    transform = Transform(offset.Normalized(), perpendicular.Normalized())
    print(transform)
    extra_wall = Box(offset.Magnitude(), wall_thickness, extra_wall_length)@transform
    extra_wall = Difference(extra_wall, exclusion)
    parts.append (extra_wall)
  return Compound (parts)
  

preview(strong_filter_output_part_FDM_printable)
