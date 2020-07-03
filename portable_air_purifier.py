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
   
  fan_thickness = 28 + tight_leeway*2
  fan_width = 79.7 + tight_leeway*2
  fan_length = 78.9 + tight_leeway*2
  fan_exit_width = 26 + tight_leeway*2
  fan_exit_length = 8
  fan_intake_circle_measured_radius = 24.4
  fan_intake_circle_hole_radius = fan_intake_circle_measured_radius + 2.5
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
  
  strong_filter_rim_inset = 6
  prefilter_rim_inset = 4
  airspace = 5
  zigzag_depth = max(wall_observed_thickness*1.2, 1.2) # make sure to have enough room for the 0.9mm radius wires
  zigzag_length_limit = 10
  min_zigzag_wall_thickness = zigzag_depth + wall_observed_thickness/math.cos(math.atan(zigzag_depth/zigzag_length_limit))
  max_zigzag_wall_thickness = zigzag_depth + wall_observed_thickness/math.cos(math.atan(zigzag_depth/(zigzag_length_limit/2)))
  print (f"max_zigzag_wall_thickness = {max_zigzag_wall_thickness}; difference from naive guess = {max_zigzag_wall_thickness - (zigzag_depth + wall_observed_thickness)}; difference from min = {max_zigzag_wall_thickness - min_zigzag_wall_thickness}")
  beyond_distance = 10 + max_zigzag_wall_thickness
  
  
  strong_filter_holder_plate_design_height = strong_filter_seal_squish_distance + tight_leeway + wall_design_thickness
  
  
  strong_filter_bottom_z = 0
  strong_filter_seal_bottom_z = strong_filter_bottom_z + strong_filter_depth_without_seal
  strong_filter_seal_top_z = strong_filter_seal_bottom_z + strong_filter_seal_depth_squished
  strong_filter_holder_top_z = strong_filter_seal_top_z + wall_observed_thickness
  fan_holder_bottom_z = strong_filter_seal_bottom_z + airspace
  fan_bottom_z = fan_holder_bottom_z + max_zigzag_wall_thickness
  fan_top_z = fan_bottom_z + fan_thickness
  fan_center_z = (fan_bottom_z+fan_top_z)/2
  fan_airspace_top_z = fan_top_z + wall_observed_thickness + airspace
  battery_bottom_z = fan_airspace_top_z + max_zigzag_wall_thickness
  battery_top_z = battery_bottom_z + battery_thickness
  beyond_top_z = battery_top_z + beyond_distance
  beyond_bottom_z = strong_filter_bottom_z - beyond_distance
  

  
  strong_filter_front_y = 0
  strong_filter_back_y = strong_filter_front_y + strong_filter_width
  fan_back_y = strong_filter_back_y + wall_observed_thickness - max_zigzag_wall_thickness
  fan_front_y = fan_back_y - fan_length
  fan_body_front_y = fan_front_y + fan_exit_length
  battery_front_y = strong_filter_front_y - wall_observed_thickness + max_zigzag_wall_thickness
  battery_back_y = battery_front_y + battery_width
  beyond_back_y = strong_filter_back_y + beyond_distance
  beyond_front_y = strong_filter_front_y - beyond_distance
  prefilter_front_y = battery_front_y
  prefilter_back_y = fan_back_y
  fan_intake_circle_center_y = fan_front_y + tight_leeway + 40.3
  
  
  strong_filter_left_x = 0
  strong_filter_right_x = strong_filter_left_x + strong_filter_length
  strong_filter_center_x = (strong_filter_left_x + strong_filter_right_x)/2
  fan_space_right_x = strong_filter_right_x - strong_filter_rim_inset/2 - max_zigzag_wall_thickness/2
  fan_intake_circle_right_x = fan_space_right_x - fan_cord_socket_slit_width - 10 - wall_observed_thickness
  fan_intake_circle_center_x = fan_intake_circle_right_x - fan_intake_circle_hole_radius
  fan_right_x = fan_intake_circle_center_x + fan_intake_circle_center_to_right
  fan_left_x = fan_right_x - fan_width
  fan_exit_right_x = fan_left_x + fan_exit_width
  prefilter_right_x = fan_left_x - max_zigzag_wall_thickness
  battery_right_x = fan_space_right_x
  battery_left_x = battery_right_x - battery_length
  battery_space_left_x = battery_left_x - battery_socket_length
  prefilter_left_x = battery_space_left_x
  beyond_right_x = strong_filter_right_x + beyond_distance
  beyond_left_x = battery_space_left_x - beyond_distance
  
  
  CPAP_design_inner_radius = CPAP_target_outer_radius - wall_expansion - wall_design_thickness
  
  
  displayed_objects = {}
  
  
  
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
  
  #strong_filter_holder_plate = strong_filter_holder_plate.mirror(vector(strong_filter_center_x, 0, 0), vector(1,0,0))

  strong_filter_holder_plates = [
    strong_filter_holder_plate.translated(vector (0, 0, strong_filter_seal_top_z + wall_expansion)),
    strong_filter_holder_plate.mirror (vector(), vector (0, 0, 1)). translated (vector (0, 0, strong_filter_bottom_z - wall_expansion)),
  ]

  strong_filter_push_hole = box (
    centered (500),
    15,
    bounds (strong_filter_bottom_z - wall_expansion, strong_filter_seal_top_z + wall_expansion),
  )

  foo = wall_expansion + wall_design_thickness
  strong_filter_sides = box (
    bounds (strong_filter_left_x - foo, strong_filter_right_x + foo),
    bounds (strong_filter_front_y - foo, strong_filter_back_y + foo),
    bounds (strong_filter_bottom_z - wall_expansion - strong_filter_holder_plate_design_height, strong_filter_seal_top_z + wall_expansion + strong_filter_holder_plate_design_height),
  ).cut([
  box (
    bounds (strong_filter_left_x - 500, strong_filter_right_x + wall_expansion),
    bounds (strong_filter_front_y - wall_expansion, strong_filter_back_y + wall_expansion),
    centered(500),
  ),
  strong_filter_push_hole.translated(vector(0, strong_filter_front_y - wall_expansion, 0)),
  strong_filter_push_hole.mirror (vector(), vector (0, 1, 0)).translated(vector(0, strong_filter_back_y + wall_expansion, 0)),
  ])
  
  class AirspaceWithWall:
    pass
      
  
  class AirspaceProfile(AirspaceWithWall):
    def __init__(self, min_x, min_y, max_x, max_y, dimension = 2):
      self.inner_wire = FreeCAD_shape_builder(zigzag_length_limit = zigzag_length_limit, zigzag_depth = zigzag_depth).build ([
        start_at(min_x, min_y),
        horizontal_to (max_x),
        vertical_to (max_y),
        horizontal_to (min_x),
        close()
      ]).to_wire()
      extrude_direction = vector()
      extrude_direction [dimension] = 1.0
      if dimension == 1:
        self.inner_wire = self.inner_wire.as_xz()
      if dimension == 0:
        self.inner_wire = self.inner_wire.as_yz()
      self.outer_wire = self.inner_wire.makeOffset2D(wall_design_thickness, join=2)
      
      self.inner_face = self.inner_wire.to_face()
      self.outer_face = self.outer_wire.to_face()
      
      self.inner_shape = self.inner_face.fancy_extrude (extrude_direction, centered (500))
      self.outer_shape = self.outer_face.fancy_extrude (extrude_direction, centered (500))
      
      #Part.show(self.inner_shape)
      #Part.show(self.outer_shape)
  
  class AirspaceIntersection(AirspaceWithWall):
    def __init__(self, members):
      self.inner_shape = members[0].inner_shape
      self.outer_shape = members[0].outer_shape
      for member in members[1:]:
        self.inner_shape = self.inner_shape.common(member.inner_shape)
        self.outer_shape = self.outer_shape.common(member.outer_shape)
      #Part.show(self.inner_shape)
      #Part.show(self.outer_shape)
      
  
  bar = max_zigzag_wall_thickness - wall_observed_thickness - wall_expansion
  side_walls_profile = AirspaceProfile (
    beyond_left_x,
    strong_filter_front_y + bar,
    beyond_right_x,
    strong_filter_back_y - bar,
  )
  
  foo = strong_filter_rim_inset/2 + max_zigzag_wall_thickness/2 - wall_expansion
  right_wall_profile = AirspaceProfile (
    beyond_left_x,
    beyond_front_y,
    strong_filter_right_x - foo,
    beyond_back_y,
  )
  
  strong_filter_airspace_left_wall_profile = AirspaceProfile (
    strong_filter_left_x + foo,
    beyond_front_y,
    beyond_right_x,
    beyond_back_y,
  )
  
  battery_space_left_wall_profile = AirspaceProfile (
    battery_space_left_x - wall_expansion,
    beyond_front_y,
    beyond_right_x,
    beyond_back_y,
  )
  
  fan_airspace_left_wall_profile = AirspaceProfile (
    fan_left_x - wall_expansion,
    beyond_front_y,
    beyond_right_x,
    beyond_back_y,
  )
  
  bar = airspace + wall_expansion
  strong_filter_airspace_front_profile = AirspaceProfile (
    beyond_left_x,
    strong_filter_bottom_z - bar,
    beyond_right_x,
    strong_filter_seal_bottom_z + bar,
    dimension = 1,
  )
  
  battery_space_bottom_profile = AirspaceProfile (
    beyond_front_y,
    battery_bottom_z - wall_expansion,
    beyond_back_y,
    beyond_top_z,
    dimension = 0,
  )
  
  battery_space_top_profile = AirspaceProfile (
    beyond_left_x,
    beyond_bottom_z,
    beyond_right_x,
    battery_top_z + wall_expansion,
    dimension = 1,
  )
  
  strong_filter_airspace_top_profile = AirspaceIntersection ([
    side_walls_profile,
    strong_filter_airspace_left_wall_profile,
    right_wall_profile,
  ])
  
  fan_intake_airspace_top_profile = AirspaceIntersection ([
    side_walls_profile,
    battery_space_left_wall_profile,
    right_wall_profile,
  ])
  
  fan_airspace_top_profile = AirspaceIntersection ([
    side_walls_profile,
    fan_airspace_left_wall_profile,
    right_wall_profile,
  ])
  
  filter_exclusion_box =box (
      centered (500),
      centered (500),
      bounds (strong_filter_bottom_z - strong_filter_holder_plate_design_height, strong_filter_seal_top_z + strong_filter_holder_plate_design_height),
    )
    
  strong_filter_airspace = AirspaceIntersection ([
    strong_filter_airspace_top_profile,
    strong_filter_airspace_front_profile,
  ])

  strong_filter_airspace_wall = strong_filter_airspace.outer_shape.cut ([
    strong_filter_airspace.inner_shape, filter_exclusion_box
  ])
  
  battery_space = AirspaceIntersection ([
    side_walls_profile,
    battery_space_left_wall_profile,
    battery_space_top_profile,
    #battery_space_bottom_profile,
    #right_wall_profile,
  ])
  
  battery_space_wall = battery_space.outer_shape.common(right_wall_profile.outer_shape).common(battery_space_bottom_profile.outer_shape).cut ([
    battery_space.inner_shape,
    box(
      bounds(-500, battery_right_x - tight_leeway - 120 + wall_expansion),
      centered(500),
      centered(500),
    ),
    box(
      centered(500),
      centered(25 + wall_expansion*2, on = (battery_front_y + battery_back_y)/2),
      bounds(battery_bottom_z - wall_expansion, battery_top_z + wall_expansion),
    ),
  ])
  
  fan_airspace_wall = fan_airspace_top_profile.outer_shape.cut ([
    fan_airspace_top_profile.inner_shape, strong_filter_airspace_front_profile.inner_shape
  ]).common (box (
    centered (500),
    centered (500),
    bounds (strong_filter_seal_top_z, fan_top_z + wall_expansion + wall_design_thickness),
  ))
  
  fan_intake_airspace_side_walls = fan_intake_airspace_top_profile.outer_shape.common(box(
    centered (500),
    centered (500),
    bounds (fan_top_z + wall_expansion, battery_bottom_z),
  )).cut([
    fan_intake_airspace_top_profile.inner_shape,
    battery_space_bottom_profile.inner_shape
  ])
  
  fan_cord_socket_slit = box (
    bounds (fan_space_right_x -fan_cord_socket_slit_width - wall_expansion, 500),
    bounds (-500, fan_front_y +fan_cord_socket_slit_length + wall_expansion),
    centered (500),
  )
  fan_cord_socket_slit_wall = box (
    bounds (fan_space_right_x -fan_cord_socket_slit_width - wall_expansion - wall_design_thickness, 500),
    bounds (-500, fan_front_y +fan_cord_socket_slit_length + wall_expansion + wall_design_thickness),
    bounds (fan_top_z + wall_expansion, battery_bottom_z),
  ).common (fan_intake_airspace_top_profile.inner_shape).cut([
    fan_cord_socket_slit,
    battery_space_bottom_profile.outer_shape,
  ])
  
  fan_intake_airspace_top_wall = fan_intake_airspace_top_profile.outer_shape.common(box(
    centered (500),
    centered (500),
    bounds (fan_top_z + wall_expansion + wall_design_thickness, battery_bottom_z),
  )).common([
    battery_space_bottom_profile.outer_shape
  ]).cut([
    battery_space_bottom_profile.inner_shape,
    fan_cord_socket_slit,
  ])
  
  fan_intake_airspace_rim = (box(
    centered (500),
    centered (500),
    bounds (fan_top_z + wall_expansion, fan_top_z + wall_expansion + wall_design_thickness)
  )
    .common (fan_intake_airspace_top_profile.inner_shape)
    .cut ([
      fan_airspace_left_wall_profile.outer_shape,
      box(
        bounds (
          prefilter_left_x + prefilter_rim_inset - wall_expansion,
          prefilter_right_x - prefilter_rim_inset + wall_expansion,
        ),
        bounds (
          prefilter_front_y + prefilter_rim_inset - wall_expansion,
          prefilter_back_y - prefilter_rim_inset + wall_expansion,
        ),
        centered (500)
      )
    ])
    
  )
  
  fan_intake_circle_wall = (box(
    centered (500),
    centered (500),
    bounds (fan_top_z + wall_expansion, fan_top_z + wall_expansion + wall_design_thickness)
  )
    .common (fan_airspace_top_profile.inner_shape)
    .cut ([
      Part.makeCylinder (fan_intake_circle_hole_radius + wall_expansion, 500, vector (fan_intake_circle_center_x, fan_intake_circle_center_y, -250)),
      box(
        bounds (fan_intake_circle_center_x - (fan_intake_circle_hole_radius + wall_expansion), fan_intake_circle_center_x),
        bounds (fan_intake_circle_center_y, fan_intake_circle_center_y + (fan_intake_circle_hole_radius + wall_expansion)),
        centered(500),
      ),
      fan_cord_socket_slit,
    ])
    
  )
  
  fan_restraining_wall = box (
    bounds (fan_right_x + wall_expansion, fan_right_x + wall_expansion + wall_design_thickness),
    bounds (fan_front_y - wall_expansion, 500),
    bounds (strong_filter_seal_top_z, fan_bottom_z + 3 - wall_expansion),
  ).common (fan_airspace_top_profile.inner_shape).cut (strong_filter_airspace_front_profile.outer_shape)

  
  
  fan_exit_airspace = box (
    bounds (-500, 500),
    bounds (-500, fan_front_y + wall_expansion),
    bounds (strong_filter_seal_top_z, fan_top_z + wall_expansion),
    
  ).fuse (box (
    bounds (fan_left_x - wall_expansion, fan_exit_right_x + wall_expansion),
    bounds (-500, fan_body_front_y - wall_expansion),
    bounds (fan_bottom_z - wall_expansion, fan_top_z + wall_expansion),
  )).cut(filter_exclusion_box).fuse (box (
    bounds(-500, strong_filter_right_x - strong_filter_rim_inset + wall_expansion),
    bounds (strong_filter_front_y + strong_filter_rim_inset - wall_expansion, fan_front_y - wall_expansion),
    bounds (strong_filter_seal_top_z, fan_top_z + wall_expansion),
  )).common (fan_airspace_top_profile.inner_shape)
  
  fan_exit_airspace_with_wall = box (
    bounds (-500, fan_exit_right_x + wall_expansion + wall_design_thickness),
    bounds (-500, fan_body_front_y - wall_expansion),
    bounds (strong_filter_seal_top_z, fan_top_z + wall_expansion + wall_design_thickness),
  ).fuse(
    box (
      bounds (-500, 500),
      bounds (-500, fan_front_y + wall_expansion + wall_design_thickness),
      bounds (strong_filter_seal_top_z, fan_top_z + wall_expansion + wall_design_thickness),
    )
  ).common (fan_airspace_top_profile.inner_shape).cut(strong_filter_airspace_front_profile.outer_shape)
  
  
  
  
  CPAP_build_list = [
    start_at(CPAP_design_inner_radius, 0),
    vertical_to(20),
    bezier([
      (CPAP_design_inner_radius, 35),
      (25, 50),
      (25, 100),
    ]),
  ]
  CPAP_inner_wire = FreeCAD_shape_builder().build (CPAP_build_list).as_xz().to_wire()
  
  rotate_y_direction = -1
  rotate_to_diagonal_angle = math.atan(math.sqrt(2))*360/math.tau
  
  foo = (max_zigzag_wall_thickness - wall_expansion)/2 # approximate
  
  bottom_corner = vector(
    strong_filter_right_x + foo,
    (strong_filter_back_y if rotate_y_direction == 1 else strong_filter_front_y) + foo*rotate_y_direction,
    strong_filter_bottom_z - strong_filter_holder_plate_design_height - foo
  )
  def rotated_to_diagonal (foo):
    return foo.rotated(vector(), vector(1, -1*rotate_y_direction, 0), rotate_to_diagonal_angle*rotate_y_direction)
  def rotated_from_diagonal (foo):
    return foo.rotated(vector(), vector(1, -1*rotate_y_direction, 0), -rotate_to_diagonal_angle*rotate_y_direction)
  def CPAP_transformed (foo):
    return rotated_to_diagonal (foo.translated(vector(-43, -27*rotate_y_direction, 0))).translated(bottom_corner).cut([strong_filter_airspace.inner_shape, box(centered(500), centered(500), bounds(strong_filter_bottom_z, 500))])
  
  CPAP_airspace = FreeCAD_shape_builder().build (CPAP_build_list+[
    horizontal_to (0),
    vertical_to(0),
    close(),
  ]).as_xz().to_wire().to_face().revolve (vector(), vector (0, 0, 1), 360)
  CPAP_airspace = CPAP_transformed (CPAP_airspace)
  
  CPAP_solid = CPAP_inner_wire.makeOffset2D(wall_design_thickness, fill=True).revolve (vector(), vector (0, 0, 1), 360).cut(box(centered(500), centered(500), bounds(-500, 0)))
  CPAP_solid = CPAP_transformed (CPAP_solid)
  
  artifical_support = rotated_to_diagonal (box (
    bounds (-8, 3),
    bounds (-8, 3) if rotate_y_direction == 1 else bounds(-3, 8),
    bounds (0, 20),
  )).translated (bottom_corner).cut([strong_filter_airspace.inner_shape, box(
    centered(500),
    bounds (strong_filter_front_y - wall_expansion, strong_filter_back_y + wall_expansion),
    bounds (strong_filter_bottom_z - wall_expansion - strong_filter_seal_squish_distance - tight_leeway, 500)
  )])
  
  fan_insert_box = box (
    bounds (fan_left_x - wall_expansion, fan_right_x + wall_expansion),
    bounds (fan_body_front_y - wall_expansion, 500),
    bounds (fan_bottom_z - wall_expansion, fan_top_z + wall_expansion),
  )

  
  air_purifier = strong_filter_sides.fuse(strong_filter_holder_plates + [
    strong_filter_airspace_wall,
    fan_exit_airspace_with_wall,
    fan_airspace_wall,
    CPAP_solid,
    artifical_support,
    fan_intake_airspace_side_walls,
    fan_intake_airspace_top_wall,
    fan_intake_airspace_rim,
    fan_intake_circle_wall,
    fan_restraining_wall,
    #battery_space_wall,
    fan_cord_socket_slit_wall,
  ]).cut ([
    fan_exit_airspace,
    CPAP_airspace,
    fan_insert_box,
  ])
  
  displayed_objects ["air_purifier"] = air_purifier
  '''displayed_objects ["grip_test"] = air_purifier.common(box(
    centered (25, on = strong_filter_right_x),
    centered (500),
    bounds (-20, 500),
  ))'''
  
  displayed_objects ["battery_box"] = box(
    bounds (battery_left_x, battery_right_x),
    bounds (battery_front_y, battery_back_y),
    bounds (battery_bottom_z, battery_top_z),
  )
  
  for name, object in displayed_objects.items():
    show (rotated_from_diagonal (object), name)

def run(g):
  for key, value in g.items():
    globals()[key] = value
  make_portable_air_purifier(wall_design_thickness = 0.5, wall_observed_thickness = 1.0)
  
  
  