CPAP_target_outer_radius = 21.5/2


def make_portable_air_purifier (wall_design_thickness, wall_observed_thickness):
  '''
  TODO:
  make the seal edges slant at the edge so they don't catch on the foam as you push the filter in
  make sure the open edge has a reinforcing wall
  possibly make the open edge be one of the short edges
  surround the fan properly (including, probably, a snap-in wall to close it after it's inserted)
  make pre-filter slot
  make battery slot, guides for cord, probably a catch to hold the battery in
  
  known unresolved issues:
  pre-filter slot should accommodate multiple thicknesses of prefilter; how?
  prefilter slot must have a way to insert prefilter
  
  '''
  
  wall_expansion = (wall_observed_thickness - wall_design_thickness)/2
  
  # extra leeway in addition to the wall expansion, for rigid parts that need to fit into a slot, so that printing irregularities don't make them not fit
  tight_leeway = 0.15
  
  strong_filter_length = 151.9 + tight_leeway*2
  strong_filter_width = 101 + tight_leeway*2
  strong_filter_depth_without_seal = 14
  strong_filter_seal_depth_expanded = 2
  strong_filter_seal_squish_distance = 0.5
  strong_filter_seal_depth_squished = strong_filter_seal_depth_expanded - strong_filter_seal_squish_distance
  
  strong_filter_rim_inset = 6
  airspace = 5
  zigzag_depth = wall_observed_thickness*1.2
  zigzag_length_limit = 10
  min_zigzag_wall_thickness = zigzag_depth + wall_observed_thickness/math.cos(math.atan(zigzag_depth/zigzag_length_limit))
  max_zigzag_wall_thickness = zigzag_depth + wall_observed_thickness/math.cos(math.atan(zigzag_depth/(zigzag_length_limit/2)))
  print (f"max_zigzag_wall_thickness = {max_zigzag_wall_thickness}; difference from naive guess = {max_zigzag_wall_thickness - (zigzag_depth + wall_observed_thickness)}; difference from min = {max_zigzag_wall_thickness - min_zigzag_wall_thickness}")
  
  fan_thickness = 28 + tight_leeway*2
  fan_width = 79.7 + tight_leeway*2
  fan_length = 78.9 + tight_leeway*2
  fan_exit_width = 26 + tight_leeway*2
  fan_exit_length = 8
  
  
  strong_filter_holder_plate_design_height = strong_filter_seal_squish_distance + tight_leeway + wall_design_thickness
  
  
  strong_filter_bottom_z = 0
  strong_filter_seal_bottom_z = strong_filter_bottom_z + strong_filter_depth_without_seal
  strong_filter_seal_top_z = strong_filter_seal_bottom_z + strong_filter_seal_depth_squished
  strong_filter_holder_top_z = strong_filter_seal_top_z + wall_observed_thickness
  fan_holder_bottom_z = strong_filter_seal_bottom_z + airspace
  fan_bottom_z = fan_holder_bottom_z + max_zigzag_wall_thickness
  fan_top_z = fan_bottom_z + fan_thickness
  fan_center_z = (fan_bottom_z+fan_top_z)/2

  
  strong_filter_front_y = 0
  strong_filter_back_y = strong_filter_front_y + strong_filter_width
  fan_back_y = strong_filter_back_y + wall_observed_thickness - max_zigzag_wall_thickness
  fan_front_y = fan_back_y - fan_length
  fan_body_front_y = fan_front_y + fan_exit_length
  
  strong_filter_left_x = 0
  strong_filter_right_x = strong_filter_left_x + strong_filter_length
  strong_filter_center_x = (strong_filter_left_x + strong_filter_right_x)/2
  fan_right_x = strong_filter_right_x - strong_filter_rim_inset/2 - max_zigzag_wall_thickness/2
  fan_left_x = fan_right_x - fan_width
  fan_exit_right_x = fan_left_x + fan_exit_width
  
  CPAP_design_inner_radius = CPAP_target_outer_radius - wall_expansion - wall_design_thickness
  
  
  foo = wall_expansion + wall_design_thickness
  
  strong_filter_holder_plate = box (
    bounds (strong_filter_left_x - foo, strong_filter_right_x + foo),
    bounds (strong_filter_front_y - foo, strong_filter_back_y + foo),
    bounds (0, strong_filter_holder_plate_design_height),
  )
  
  strong_filter_holder_plate_cut_profile = FreeCAD_shape_builder().build([
    start_at(strong_filter_right_x - strong_filter_rim_inset/2, 0),
    diagonal_to(strong_filter_right_x - strong_filter_rim_inset + wall_expansion, strong_filter_seal_squish_distance + tight_leeway),
    vertical_to(500),
    horizontal_to(strong_filter_left_x + strong_filter_rim_inset - wall_expansion),
    vertical_to(strong_filter_seal_squish_distance + tight_leeway),
    diagonal_to(strong_filter_left_x + strong_filter_rim_inset/2, 0),
    vertical_to(-500),
    close(),
  ]).as_xz().to_wire().to_face()
  strong_filter_holder_plate_cut_profile_2 = FreeCAD_shape_builder().build([
    start_at(strong_filter_left_x + strong_filter_rim_inset/2, 0),
    diagonal_to(strong_filter_left_x - foo, strong_filter_seal_squish_distance + tight_leeway),
    vertical_to(-500),
    close(),
  ]).as_xz().to_wire().to_face()
  
  strong_filter_holder_plate = strong_filter_holder_plate.cut([
    strong_filter_holder_plate_cut_profile.fancy_extrude(
      vector (0, 1, 0),
      bounds (strong_filter_front_y + strong_filter_rim_inset - wall_expansion,
              strong_filter_back_y - strong_filter_rim_inset + wall_expansion)
    ),
    strong_filter_holder_plate_cut_profile_2.fancy_extrude(
      vector (0, 1, 0),
      centered(500),
    ),
  ])
  
  strong_filter_holder_plate = strong_filter_holder_plate.mirror(vector(strong_filter_center_x, 0, 0), vector(1,0,0))

  strong_filter_holder_plates = [
    strong_filter_holder_plate.translated(vector (0, 0, strong_filter_seal_top_z + wall_expansion)),
    strong_filter_holder_plate.mirror (vector(), vector (0, 0, 1)). translated (vector (0, 0, strong_filter_bottom_z - wall_expansion)),
  ]

  strong_filter_push_hole = box (
    centered (500),
    25,
    bounds (strong_filter_bottom_z - wall_expansion, strong_filter_seal_top_z + wall_expansion),
  )

  foo = wall_expansion + wall_design_thickness
  strong_filter_sides = box (
    bounds (strong_filter_left_x - foo, strong_filter_right_x + foo),
    bounds (strong_filter_front_y - foo, strong_filter_back_y + foo),
    bounds (strong_filter_bottom_z - wall_expansion - strong_filter_holder_plate_design_height, strong_filter_seal_top_z + wall_expansion + strong_filter_holder_plate_design_height),
  ).cut([
  box (
    bounds (strong_filter_left_x - wall_expansion, strong_filter_right_x + 500),
    bounds (strong_filter_front_y - wall_expansion, strong_filter_back_y + wall_expansion),
    centered(500),
  ),
  strong_filter_push_hole.translated(vector(0, strong_filter_front_y - wall_expansion, 0)),
  strong_filter_push_hole.mirror (vector(), vector (0, 1, 0)).translated(vector(0, strong_filter_back_y + wall_expansion, 0)),
  ])
  
  foo = strong_filter_rim_inset/2 + max_zigzag_wall_thickness/2 - wall_expansion
  bar = max_zigzag_wall_thickness - wall_observed_thickness - wall_expansion
  strong_filter_airspace_top_profile_wire = FreeCAD_shape_builder(zigzag_length_limit = zigzag_length_limit, zigzag_depth = zigzag_depth).build ([
    start_at(strong_filter_left_x + foo, strong_filter_front_y + bar),
    horizontal_to (strong_filter_right_x - foo),
    vertical_to (strong_filter_back_y - bar),
    horizontal_to (strong_filter_left_x + foo),
    close()
  ]).to_wire()
  
  foo = 0
  bar = -max_zigzag_wall_thickness
  fan_airspace_extra_top_profile_wire = FreeCAD_shape_builder(zigzag_length_limit = zigzag_length_limit, zigzag_depth = zigzag_depth).build ([
    start_at(fan_left_x - wall_expansion, strong_filter_front_y + bar),
    horizontal_to (strong_filter_right_x - foo),
    vertical_to (strong_filter_back_y - bar),
    horizontal_to (fan_left_x - wall_expansion),
    close()
  ]).to_wire()
  
  strong_filter_airspace_top_shape = strong_filter_airspace_top_profile_wire.to_face().fancy_extrude (vector (0, 0, 1), centered (500))
  strong_filter_airspace_with_wall_top_shape = strong_filter_airspace_top_profile_wire.makeOffset2D(wall_design_thickness, join=2).to_face().fancy_extrude (vector (0, 0, 1), centered (500))
  
  fan_airspace_extra_top_shape = fan_airspace_extra_top_profile_wire.to_face().fancy_extrude (vector (0, 0, 1), centered (500))
  fan_airspace_extra_with_wall_top_shape = fan_airspace_extra_top_profile_wire.makeOffset2D(wall_design_thickness, join=2).to_face().fancy_extrude (vector (0, 0, 1), centered (500))
  
  foo = 0
  bar = airspace + wall_expansion
  strong_filter_airspace_front_profile_wire = FreeCAD_shape_builder(zigzag_length_limit = zigzag_length_limit, zigzag_depth = zigzag_depth).build ([
    start_at(strong_filter_left_x + foo, strong_filter_bottom_z - bar),
    horizontal_to (strong_filter_right_x - foo),
    vertical_to (strong_filter_seal_bottom_z + bar),
    horizontal_to (strong_filter_left_x + foo),
    close()
  ]).as_xz().to_wire()
  
  strong_filter_airspace_front_shape = strong_filter_airspace_front_profile_wire.to_face().fancy_extrude (vector (0, 1, 0), centered (500))
  strong_filter_airspace_with_wall_front_shape = strong_filter_airspace_front_profile_wire.makeOffset2D(wall_design_thickness, join=2).to_face().fancy_extrude (vector (0, 1, 0), centered (500))
  
  filter_exclusion_box =box (
      centered (500),
      centered (500),
      bounds (strong_filter_bottom_z - strong_filter_holder_plate_design_height, strong_filter_seal_top_z + strong_filter_holder_plate_design_height),
    )
  strong_filter_airspace = strong_filter_airspace_top_shape.common (strong_filter_airspace_front_shape)
  strong_filter_airspace_with_wall = strong_filter_airspace_with_wall_top_shape.common (strong_filter_airspace_with_wall_front_shape)
  strong_filter_airspace_wall = strong_filter_airspace_with_wall.cut ([
    strong_filter_airspace, filter_exclusion_box
  ])
  
  fan_airspace_top_shape = strong_filter_airspace_top_shape.common (fan_airspace_extra_top_shape)
  fan_airspace_with_wall_top_shape = strong_filter_airspace_with_wall_top_shape.common (fan_airspace_extra_with_wall_top_shape)
  fan_airspace_wall = fan_airspace_with_wall_top_shape.cut ([
    fan_airspace_top_shape, strong_filter_airspace_front_shape
  ]).common (box (
    centered (500),
    centered (500),
    bounds (strong_filter_seal_top_z, fan_top_z),
  ))
  
  '''
  fan_to_filter_profile_inner_wire = FreeCAD_shape_builder(zigzag_length_limit = zigzag_length_limit, zigzag_depth = zigzag_depth).build ([
    start_at (strong_filter_left_x, strong_filter_seal_top_z),
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
  
  exit_profile_inner_wire = FreeCAD_shape_builder(zigzag_length_limit = zigzag_length_limit, zigzag_depth = zigzag_depth).build ([
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
  ]).rotated(vector(), vector(1, -1, 0), -rotate_to_diagonal_angle)'''
  
  
  fan_exit_airspace = box (
    bounds (-500, fan_exit_right_x + wall_expansion),
    bounds (-500, fan_front_y - wall_expansion),
    bounds (strong_filter_seal_top_z, fan_top_z + wall_expansion),
    
  ).fuse (box (
    bounds (fan_left_x - wall_expansion, fan_exit_right_x + wall_expansion),
    bounds (-500, fan_body_front_y - wall_expansion),
    bounds (fan_bottom_z - wall_expansion, fan_top_z + wall_expansion),
  )).common (fan_airspace_top_shape)
  
  fan_exit_airspace_with_wall = box (
    bounds (-500, fan_exit_right_x + wall_expansion + wall_design_thickness),
    bounds (-500, fan_body_front_y - wall_expansion),
    bounds (strong_filter_seal_top_z, fan_top_z + wall_expansion + wall_design_thickness),
  ).common (fan_airspace_top_shape)
  
  foo = strong_filter_sides.fuse(strong_filter_holder_plates + [
    strong_filter_airspace_wall,
    fan_exit_airspace_with_wall,
    fan_airspace_wall
  ]).cut (fan_exit_airspace)
  
  show (foo, "foo")

def run(g):
  for key, value in g.items():
    globals()[key] = value
  make_portable_air_purifier(wall_design_thickness = 0.5, wall_observed_thickness = 1.0)
  
  
  