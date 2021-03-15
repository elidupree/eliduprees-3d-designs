import math

from pyocct_system import *
initialize_system (globals())


wall_thickness = 0.6

# extra leeway for rigid parts that need to fit into a slot, so that printing irregularities don't make them not fit.
# we generally want to rely on slightly springy parts rather than exact sizing; with a perfect fabrication process, I would use 0.0 for this. The positive number exists to compensate for my diagonal printing process adding some unnecessary thickness
contact_leeway = 0.4

strong_filter_length = 151.9
strong_filter_width = 101
strong_filter_depth_without_seal = 14
strong_filter_seal_depth_expanded = 2
strong_filter_seal_squish_distance = 0.5
strong_filter_seal_depth_squished = strong_filter_seal_depth_expanded - strong_filter_seal_squish_distance
strong_filter_depth_with_seal = strong_filter_depth_without_seal + strong_filter_seal_depth_squished
strong_filter_rim_inset = 6
strong_filter_airspace_wall_inset = strong_filter_rim_inset

fan_thickness = 28
fan_width = 79.7
fan_length = 78.9
fan_exit_width = 26
fan_exit_length = 8
fan_intake_circle_measured_radius = 24.4
fan_intake_circle_center_from_front = 40.3
fan_intake_circle_center_from_left = 44
fan_intake_circle_center_to_back = fan_length - fan_intake_circle_center_from_front
fan_intake_circle_center_to_right = fan_width - fan_intake_circle_center_from_left

plenty_airspace = 11

battery_thickness = 27.8
battery_width = 85.5
battery_length = 144.2
battery_cord_diameter = 3.5
battery_socket_diameter = 11.4
battery_socket_length = 38.2

fan_cord_socket_slit_width = 15
fan_cord_socket_slit_length = 40

CPAP_outer_radius = (22/2)
CPAP_inner_radius = CPAP_outer_radius-wall_thickness

lots = 500

min_corner_radius_inner = wall_thickness*0.5
min_corner_radius_outer = wall_thickness*1.5

skirt_flare_distance = 5


strong_filter_size = Vector (
  strong_filter_length,
  strong_filter_width,
  strong_filter_depth_with_seal
)
strong_filter_min = Point (0, 0, 0)
strong_filter_max = strong_filter_min + strong_filter_size
strong_filter_center = strong_filter_min + (strong_filter_size/2)
strong_filter_seal_bottom = strong_filter_max[2] - strong_filter_seal_depth_squished

fan_exit_center = Point(strong_filter_center[0], strong_filter_center[1], strong_filter_min [2] - plenty_airspace)
fan_exit_size = vector (fan_exit_width, fan_thickness, 0)


# only go one third of the way down, so there's a small airgap, meaning that any leakage around the intake side of the filter will be released into the unfiltered air instead of sneaking forward into the air that should be filtered
strong_filter_cover_depth = strong_filter_depth_with_seal/3

corner_transforms = [
    Mirror(Origin),
    Mirror(Back),
    Transform(),
    Mirror(Right),
  ]

def approximate_edges(edges):
  result = []
  for edge in edges:
    curve, start, finish = edge.curve()
    for parameter in subdivisions (start, finish, amount = 9)[1:]:
      result.append (curve.value (parameter))
  return result

@run_if_changed
def make_strong_filter_to_CPAP_wall():
  filter_inset = vector(xy= strong_filter_airspace_wall_inset)
  center_to_corner = (strong_filter_size).projected_perpendicular (Up)/2
  center_to_inset = center_to_corner - filter_inset
  base_point = strong_filter_center.projected(Plane(Origin, Up))
  upstep = 5
  
  flat_before_upstep_vertex = Vertex (-strong_filter_airspace_wall_inset - 6, 0, 7)
  upstep_vertex = Vertex (-strong_filter_airspace_wall_inset - 1, 0, 5)
  inset_vertex = Vertex (-strong_filter_airspace_wall_inset, 0, 0)
  corner_vertex = Vertex (contact_leeway - 0.6, 0, 0)
  cover_vertex = Vertex (contact_leeway + 0.4, 0, -strong_filter_cover_depth)
  skirt_vertex = Vertex (skirt_flare_distance, 0, -strong_filter_depth_with_seal)
  profile = approximate_edges(FilletedEdges([
    flat_before_upstep_vertex,
    (upstep_vertex, min_corner_radius_inner + 3),
    (inset_vertex, min_corner_radius_outer + 1),
    (corner_vertex, min_corner_radius_inner),
    (cover_vertex, min_corner_radius_outer + 10),
    skirt_vertex,
  ])[1:])
  
  
  rim = approximate_edges(FilletedEdges([
    (base_point + center_to_corner@corner_trans, min_corner_radius_inner)
    for corner_trans in corner_transforms
  ], loop = True))
  inset_rim = approximate_edges(FilletedEdges([
    (base_point + center_to_inset@corner_trans, min_corner_radius_inner)
    for corner_trans in corner_transforms
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
  #extra_faces = [Face (wire).complemented() for wire in ClosedFreeWires (face)]
  #preview (Shell ([face] + extra_faces))
  #solid = Solid (Shell ([face] + extra_faces))
  #preview (solid)
  #preview(Offset(face, wall_thickness, tolerance = 0.01))
  
  #preview (face)
  
  #thick = thicken_solid(solid, [f for f in solid.faces() if all_equal(v[2] for v in f.vertices())], wall_thickness)
  thick = Offset(face, wall_thickness, tolerance = 0.01, fill = True)
  half_thick = Intersection(thick, HalfSpace(strong_filter_center, Left))
  mirrored = half_thick @ Mirror(Axes(strong_filter_center, Right))
  #preview (thick)
  #preview (half_thick)
  combined = Compound(half_thick, mirrored)
  save ("strong_filter_to_CPAP_wall", combined@Translate (0, 0, strong_filter_max[2]))
#preview(strong_filter_to_CPAP_wall)

@run_if_changed
def make_strong_filter_output_part():
  '''inset = vector(strong_filter_airspace_wall_inset, strong_filter_airspace_wall_inset, 0)
  rect_min = strong_filter_min + inset
  rect_max = strong_filter_max - inset
  
  expansion = vector (wall_thickness, wall_thickness, 0)
  
  outer_box = Box (
    strong_filter_output_part_bottom_corner,
    strong_filter_max + vector (all = wall_thickness)
  )
  
  filter_cut_box = Box (strong_filter_min, strong_filter_max)
  hole_cut_box = Box (rect_min, rect_max + Up*lots)
  
  edge_walls = Difference (outer_box, [filter_cut_box, hole_cut_box])'''
  
  save ("strong_filter_output_part", strong_filter_to_CPAP_wall)



@run_if_changed
def make_fan_to_strong_filter():
  filter_inset = vector(xy= strong_filter_airspace_wall_inset)
  center_to_corner = (strong_filter_size).projected_perpendicular (Up)/2
  center_to_inset = center_to_corner - filter_inset
  center_to_mid = vector(50, 20, 0)
    
  spines = []
  for corner in corner_transforms:
    bottom = fan_exit_center [2]-(fan_exit_length - contact_leeway)
    mid = fan_exit_center [2]
    spines.append ([
      (fan_exit_center + (fan_exit_size/2 + vector(xy=contact_leeway - 0.2))@corner),
      (fan_exit_center + (fan_exit_size/2 + vector(xy=contact_leeway + 0.2))@corner).with_z(bottom),
      (strong_filter_center + (center_to_mid)@corner).with_z (bottom),
      (strong_filter_center + (center_to_inset + vector(xy=wall_thickness - 2))@corner).with_z (mid),
      (strong_filter_center + (center_to_inset + vector(xy=wall_thickness))@corner).with_z (strong_filter_min [2] - wall_thickness),
      (strong_filter_center + (center_to_corner + vector(xy=wall_thickness + contact_leeway - 0.4))@corner).with_z (strong_filter_min [2] - wall_thickness),
      (strong_filter_center + (center_to_corner + vector(xy=wall_thickness + contact_leeway + 0.4))@corner).with_z (strong_filter_min [2] + strong_filter_cover_depth),
    ])
  print("a")
  print ("\n".join(repr(a) for a in spines[0]))
  sections = [Wire(points, loop=True) for points in zip (*spines)]
  lofts = [Loft (pair[::-1], ruled = True) for pair in
    [sections[0:2], sections[2:4], sections[3:5], sections[5:7]]
  ]
  loft_faces = [face for loft in lofts for face in loft.faces()]
  #preview (sections)
  faces = loft_faces + [
    Face(sections[2], holes=sections[1].complemented()),
    Face(sections[5], holes=sections[4].complemented()),
  ]
  #preview (faces)
  pointy_shell = Shell(faces)
  #preview (pointy_shell)
  
  def loft_verticals(index):
    return [edge for edge in lofts [index].edges() if not all_equal (vertex [2] for vertex in edge.vertices())]
  shell = Fillet (pointy_shell,
    [(edge, min_corner_radius_outer) for edge in sections[1].edges()]
    + [(edge, 10) for edge in sections[2].edges()]
    + [(edge, 5) for edge in sections[3].edges()]
    + [(edge, min_corner_radius_inner) for edge in sections[4].edges()]
    + [(edge, min_corner_radius_outer) for edge in sections[5].edges()]
    + [(edge, min_corner_radius_inner) for edge in loft_verticals (0)]
    + [(edge, 15) for edge in loft_verticals (1)]
    + [(edge, min_corner_radius_outer, 5) for edge in loft_verticals (2)]
    + [(edge, min_corner_radius_outer) for edge in loft_verticals (3)]
  )
  preview(shell)
  #preview(shell, Offset (shell, wall_thickness, ))
  solid = Offset (shell, wall_thickness, fill = True)
  
  save ("fan_to_strong_filter_part", solid)
  #save_STEP ("fan_to_strong_filter_part_pointy_shell", pointy_shell)
  #save_STEP ("fan_to_strong_filter_part", solid)
  preview (solid, strong_filter_output_part)
  


'''@cached_STL
def strong_filter_output_part_mesh():
  return strong_filter_output_part
'''

rotate_to_diagonal_radians = math.atan(math.sqrt(2))
rotate_to_diagonal = Rotate(Axis(Origin, Direction(1, -1, 0)), radians=rotate_to_diagonal_radians)

@run_if_changed
def make_strong_filter_output_part_FDM_printable():
  #bottom_faces = [face for face in strong_filter_to_CPAP_wall.faces() if face.bounds().max() [2] < 1]
  bottom_corner = Point(
    -skirt_flare_distance-wall_thickness*0.5,
    -skirt_flare_distance-wall_thickness*0.5,
    strong_filter_min[2]
  )
  transform = Translate(bottom_corner, Origin) @ rotate_to_diagonal
  part = strong_filter_output_part @ transform
  
  extra_wall_length = 60

  """parts = [part]
  for bottom_face in bottom_faces:
    print(bottom_face.bounds().min(), bottom_face.bounds().max())
    support = Extrude (bottom_face@transform, Down*40)
    '''support = Intersection (support, Box(
      Point(-extra_wall_length, -extra_wall_length, 0),
      Point(extra_wall_length, extra_wall_length, lots),
    ))'''
    parts.append(support)"""
  
  
  foo = (bottom_corner + Right*extra_wall_length) @ transform
  bar = (bottom_corner + Back*extra_wall_length) @ transform
  baz = (bottom_corner + (Back + Right)*extra_wall_length) @ transform
  
  plane = Plane(Origin, Up)
  profile = Wire([
    Origin,
    foo.projected(plane),
    baz.projected(plane),
    bar.projected(plane),
  ], loop = True).offset2D(-0.2).offset2D(0.4, fill=True)
  
  limiter = HalfSpace(bottom_corner, Down) @ transform
  limiter2 = HalfSpace(foo, Direction(-1,-1,-1.1))
  
  support = profile.extrude(Up*lots).intersection(limiter).intersection(limiter2)
  #preview(part, support, foo, bar, baz, Origin)
  combined = Compound (part, support)
  test = combined .intersection(HalfSpace(Point(14, 0, 0), Left)@transform)
  save("strong_filter_output_part_FDM_printable", combined)
  save_STL("strong_filter_output_part_FDM_printable", combined)
  save("strong_filter_output_part_FDM_printable_test", test)
  save_STL("strong_filter_output_part_FDM_printable_test", test)
  

preview(strong_filter_output_part_FDM_printable_test)
