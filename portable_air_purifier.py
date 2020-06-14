CPAP_outer_radius = 21.5/2


def make_portable_air_purifier (wall_thickness):
  
  # maybe 0.2 is the correct value, but err on the side of loose for a while because it's easier to test it if it's too loose than if it's too tight
  tight_leeway = 0.4
  
  strong_filter_length = 151.9 + tight_leeway*2
  strong_filter_width = 101 + tight_leeway*2
  strong_filter_depth_without_seal = 14 + tight_leeway*2
  strong_filter_seal_depth_expanded = 2
  strong_filter_seal_squished_distance = 0.5
  strong_filter_seal_depth_squished = strong_filter_seal_depth_expanded - strong_filter_seal_squished_distance
  
  strong_filter_rim_inset = 5
  airspace = 5
  zigzag_depth = wall_thickness*1.2
  
  fan_thickness = 28 + tight_leeway*2
  fan_width = 79.7 + tight_leeway*2
  fan_length = 78.9 + tight_leeway*2
  fan_exit_width = 26 + tight_leeway*2
  fan_exit_length = 8
  
  fan_body_left_x = 90
  
  
  strong_filter_bottom_z = 0
  strong_filter_seal_bottom_z = strong_filter_bottom_z + strong_filter_depth_without_seal
  strong_filter_seal_top_z = strong_filter_seal_bottom_z + strong_filter_seal_depth_squished
  strong_filter_holder_top_z = strong_filter_seal_top_z + wall_thickness
  fan_holder_bottom_z = strong_filter_seal_bottom_z + airspace
  fan_bottom_z = fan_holder_bottom_z + wall_thickness + zigzag_depth
  fan_top_z = fan_bottom_z + fan_thickness
  fan_center_z = (fan_bottom_z+fan_top_z)/2

  
  strong_filter_front_y = 0
  strong_filter_back_y = strong_filter_front_y + strong_filter_width
  fan_front_y = strong_filter_front_y
  fan_back_y = fan_front_y + fan_width
  fan_exit_front_y = fan_back_y - fan_exit_width
  
  strong_filter_left_x = 0
  strong_filter_right_x = strong_filter_left_x + strong_filter_length
  strong_filter_center_x = (strong_filter_left_x + strong_filter_right_x)/2
  fan_exit_left_x = fan_body_left_x - fan_exit_length
  
  CPAP_inner_radius = CPAP_outer_radius-wall_thickness
  
  
  strong_filter_box = box (
    bounds (strong_filter_left_x, strong_filter_right_x),
    bounds (strong_filter_front_y - wall_thickness, strong_filter_back_y),
    bounds (strong_filter_bottom_z, strong_filter_seal_top_z),
  )
  strong_filter_holder_box = box (
    bounds (strong_filter_left_x - wall_thickness, strong_filter_right_x + wall_thickness),
    bounds (strong_filter_front_y - wall_thickness, strong_filter_back_y + wall_thickness),
    bounds (strong_filter_bottom_z - wall_thickness, strong_filter_seal_top_z + wall_thickness),
  )
  strong_filter_airspace = box (
    bounds (strong_filter_left_x + strong_filter_rim_inset, strong_filter_right_x - strong_filter_rim_inset),
    bounds (strong_filter_front_y + strong_filter_rim_inset, strong_filter_back_y - strong_filter_rim_inset),
    bounds (strong_filter_bottom_z - airspace, strong_filter_seal_bottom_z + airspace),
  )
  strong_filter_push_hole = box (
    centered (25, on=strong_filter_center_x),
    centered(500),
    bounds (strong_filter_bottom_z, strong_filter_seal_top_z),
  )
  
  fan_to_filter_profile_inner_wire = FreeCAD_shape_builder(zigzag_length_limit = 6, zigzag_depth = zigzag_depth).build ([
    start_at (strong_filter_left_x, strong_filter_seal_top_z + wall_thickness),
    horizontal_to (strong_filter_right_x),
    vertical_to (fan_holder_bottom_z),
    horizontal_to (fan_body_left_x - wall_thickness - zigzag_depth-0.01),
    vertical_to (fan_top_z),
    horizontal_to (fan_exit_left_x),
    bezier([
      (fan_exit_left_x - 20, fan_top_z),
      (fan_exit_left_x - 20, fan_center_z),
      (fan_exit_left_x - 20, fan_bottom_z),
      (fan_exit_left_x - 40, fan_bottom_z),
    ]),
    horizontal_to (strong_filter_left_x),
    close(),
  ]).as_xz().to_wire()
  
  exit_profile_inner_wire = FreeCAD_shape_builder(zigzag_length_limit = 6, zigzag_depth = zigzag_depth).build ([
    start_at (strong_filter_left_x + strong_filter_rim_inset, strong_filter_bottom_z),
    vertical_to (strong_filter_bottom_z - airspace),
    horizontal_to (strong_filter_right_x - strong_filter_rim_inset),
    vertical_to (strong_filter_bottom_z),
    close(),
  ]).as_xz().to_wire()
  
  fan_to_filter_profile_outer_wire = fan_to_filter_profile_inner_wire.makeOffset2D(wall_thickness, join=2)
  exit_profile_outer_wire = exit_profile_inner_wire.makeOffset2D(wall_thickness, join=2)
  
  fan_to_filter_solid = fan_to_filter_profile_outer_wire.to_face().fancy_extrude (vector (0, 1, 0), bounds (strong_filter_front_y - wall_thickness, strong_filter_back_y + wall_thickness))
  fan_to_filter_airspace = fan_to_filter_profile_inner_wire.to_face().fancy_extrude (vector (0, 1, 0), bounds (strong_filter_front_y, strong_filter_back_y))
  
  exit_solid = exit_profile_outer_wire.to_face().fancy_extrude (vector (0, 1, 0), bounds (strong_filter_front_y + strong_filter_rim_inset - wall_thickness, strong_filter_back_y - strong_filter_rim_inset + wall_thickness))
  exit_airspace = exit_profile_inner_wire.to_face().fancy_extrude (vector (0, 1, 0), bounds (strong_filter_front_y + strong_filter_rim_inset, strong_filter_back_y - strong_filter_rim_inset))
  
  CPAP_build_list = [
    start_at(CPAP_inner_radius, 0),
    vertical_to(20),
    bezier([
      (CPAP_inner_radius, 35),
      (25, 50),
      (25, 100),
    ]),
  ]
  CPAP_inner_wire = FreeCAD_shape_builder().build (CPAP_build_list).as_xz().to_wire()
  CPAP_foo = 30
  
  rotate_to_diagonal_angle = math.atan(math.sqrt(2))*360/math.tau
  bottom_corner = vector(strong_filter_right_x + wall_thickness, strong_filter_back_y + wall_thickness, strong_filter_bottom_z - wall_thickness)
  def rotated_to_diagonal (foo):
    return foo.rotated(vector(), vector(1, -1, 0), rotate_to_diagonal_angle)
  def CPAP_transformed (foo):
    return rotated_to_diagonal (foo.translated(vector(-CPAP_foo, -CPAP_foo, 0))).translated(bottom_corner).cut(box(centered(500), centered(500), bounds(strong_filter_bottom_z, 500)))
  
  CPAP_airspace = FreeCAD_shape_builder().build (CPAP_build_list+[
    horizontal_to (0),
    vertical_to(0),
    close(),
  ]).as_xz().to_wire().to_face().revolve (vector(), vector (0, 0, 1), 360)
  CPAP_airspace = CPAP_transformed (CPAP_airspace)
  
  CPAP_solid = CPAP_inner_wire.makeOffset2D(wall_thickness, fill=True).revolve (vector(), vector (0, 0, 1), 360).cut(box(centered(500), centered(500), bounds(-500, 0)))
  CPAP_solid = CPAP_transformed (CPAP_solid)
  
  artifical_support = rotated_to_diagonal (box (
    bounds (-8, 3),
    bounds (-8, 3),
    bounds (0, 20),
  )).translated (bottom_corner)
  
  
  fan_exit_box = box (
    bounds (fan_exit_left_x, fan_body_left_x),
    bounds (fan_exit_front_y, fan_back_y),
    bounds (fan_bottom_z, fan_top_z),
  )
  fan_exit_holder = box (
    bounds (fan_exit_left_x, fan_body_left_x),
    bounds (fan_exit_front_y - wall_thickness, fan_back_y + wall_thickness),
    bounds (fan_bottom_z - wall_thickness, fan_top_z + wall_thickness),
  )
  
  foo = fan_to_filter_solid.fuse([
    exit_solid,
    CPAP_solid,
    artifical_support
  ]).cut([
    fan_to_filter_airspace,
    exit_airspace,
    CPAP_airspace,
  ]).fuse([
    fan_exit_holder.common(fan_to_filter_solid),
    strong_filter_holder_box,
  ]).cut([
    fan_exit_box,
    strong_filter_box,
    strong_filter_airspace,
    strong_filter_push_hole,
  ]).rotated(vector(), vector(1, -1, 0), -rotate_to_diagonal_angle)
  
  show (foo, "foo")

def run(g):
  for key, value in g.items():
    globals()[key] = value
  make_portable_air_purifier(wall_thickness = 0.5)
  
  
  