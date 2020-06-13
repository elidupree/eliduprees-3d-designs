CPAP_outer_radius = 21.5/2


def make_portable_air_purifier (wall_thickness):
  strong_filter_length = 150
  strong_filter_width = 100
  strong_filter_depth_without_seal = 14
  strong_filter_seal_depth_expanded = 2
  strong_filter_seal_squished_distance = 0.5
  strong_filter_seal_depth_squished = strong_filter_seal_depth_expanded - strong_filter_seal_squished_distance
  
  strong_filter_rim_inset = 5
  airspace = 5
  
  fan_thickness = 28
  fan_width = 79.7
  fan_length = 78.9
  fan_exit_width = 26
  fan_exit_length = 8
  
  fan_body_left_x = 90
  
  
  strong_filter_bottom_z = 0
  strong_filter_seal_bottom_z = strong_filter_bottom_z + strong_filter_depth_without_seal
  strong_filter_seal_top_z = strong_filter_seal_bottom_z + strong_filter_seal_depth_squished
  strong_filter_holder_top_z = strong_filter_seal_top_z + wall_thickness
  fan_holder_bottom_z = strong_filter_seal_bottom_z + airspace
  fan_bottom_z = fan_holder_bottom_z + wall_thickness
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
  
  fan_to_filter_profile_inner_wire = FreeCAD_shape_builder().build ([
    start_at (strong_filter_left_x, strong_filter_seal_top_z + wall_thickness),
    horizontal_to (strong_filter_right_x),
    vertical_to (fan_holder_bottom_z),
    horizontal_to (fan_body_left_x - wall_thickness),
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
  
  fan_to_filter_profile_outer_wire = fan_to_filter_profile_inner_wire.makeOffset2D(wall_thickness)
  
  fan_to_filter_solid = fan_to_filter_profile_outer_wire.to_face().fancy_extrude (vector (0, 1, 0), bounds (strong_filter_front_y - wall_thickness, strong_filter_back_y + wall_thickness))
  fan_to_filter_airspace = fan_to_filter_profile_inner_wire.to_face().fancy_extrude (vector (0, 1, 0), bounds (strong_filter_front_y, strong_filter_back_y))
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
  
  foo = strong_filter_holder_box.fuse([
    fan_to_filter_solid,
  ]).cut([
    strong_filter_box,
    strong_filter_airspace,
    strong_filter_push_hole,
    fan_to_filter_airspace,
  ]).fuse([
    fan_exit_holder,
  ]).cut([
    fan_exit_box,
  ])
  
  show (foo, "foo")

def run(g):
  for key, value in g.items():
    globals()[key] = value
  make_portable_air_purifier(wall_thickness = 0.5)
  
  
  