########################################################################
########  Intake  #######
########################################################################

@run_if_changed
def make_intake_reference_curve():
  # The intake wants to have a surface that directs air towards air_target. It's convenient if that surface is the build surface, so make a plane for that. The "intake reference curve" will be the intersection between the shield surface and this build plane.
  # To decide the plane, first, we define an "intake middle" point, which will lie on the "intake reference curve" (it is defined to lie on the shield surface, and will define the build plane):
  
  intake_middle_on_build_surface_shield_curve = ShieldSample(intersecting = RayIsh(Point(0,intake_middle_y,intake_middle_z), Right))

  # Two degrees of freedom are removed by air_target and intake_middle_on_build_surface_shield_curve; to remove the third degree of freedom, the concave corner just above the intake, where the cloth nestles, should be elastic_holder_depth in front of shield_back. The build surface should be about shield_glue_face_width further in front of that... the actual formulas here are annoyingly complicated, but this is close enough:

  intake_third_source_sample = ShieldSample(intersecting = RayIsh(Point(
    0,
    shield_back + elastic_holder_depth + shield_glue_face_width,
    intake_middle_on_build_surface_shield_curve.position[2] + intake_flat_width/2
  ), Right))

  intake_source_direction_1 = Direction(intake_middle_on_build_surface_shield_curve.position, intake_third_source_sample.position)
  intake_source_direction_2 = Direction(air_target, intake_middle_on_build_surface_shield_curve.position)

  intake_curve_source_points = [
    air_target + intake_source_direction_1 * intake_flat_width*1.4,
    air_target - intake_source_direction_1 * intake_flat_width,
  ]
  intake_curve_source_surface = BSplineSurface([
      [point + intake_source_direction_2* 50 for point in intake_curve_source_points],
      [point + intake_source_direction_2*150 for point in intake_curve_source_points],
    ],
    BSplineDimension (degree = 1),
    BSplineDimension (degree = 1),
  )

  #p review(shield_surface, intake_curve_source_surface)
  save ("intake_reference_curve", ShieldCurveInPlane(intake_curve_source_surface))



@run_if_changed
def make_intake():
  # the center of the circle at the far CPAP connector end.
  CPAP_back_center_1 = Point(72, headphones_front - 40, -92)
  CPAP_back_center_2 = CPAP_back_center_1 + Vector(0, 4, -32) 
  CPAP_back_centers = [CPAP_back_center_1, CPAP_back_center_2]
  
  def augment_intake_sample(sample):
    sample.along_intake_flat = sample.normal.cross(Up).normalized()
    sample.along_intake_flat_unit_height_from_plane = sample.along_intake_flat/abs (sample.along_intake_flat.dot(sample.plane_normal))
    # basically just sample.position +
    #   shield_glue_face_width*sample.along_intake_flat_unit_height_from_plane,
    # but adjusted to be exactly on the shield, but make sure to not
    # alter its height-from-build-surface
    sample.below_shield_glue_base_point = ShieldSample(
      intersecting = RayIsh(
        sample.position
          + shield_glue_face_width*sample.along_intake_flat_unit_height_from_plane
          - sample.normal_in_plane * 10,
        sample.normal_in_plane)
    ).position

  # a base point on the lower side curve, just inside the shield.
  intake_middle = CurveSample(intake_reference_curve, z=intake_middle_z)
  augment_intake_sample(intake_middle)
  
  towards_air_target = Direction(intake_middle.position, air_target)
  towards_air_target_unit_height_from_shield = towards_air_target/abs(towards_air_target.dot(intake_middle.normal))
  
  # a reference point to try to aim the CPAP direction in a way that will make the whole shape smooth.
  CPAP_target_approx = intake_middle.position + towards_air_target_unit_height_from_shield * (min_wall_thickness + intake_flat_air_thickness_base/2)
  
  # aim the 2 CPAP hoses at the target, although also keep them a bit separate from each other (no reason to make the air converge).
  # /4 might be ideal (each hose gets half the space) but I make them converge a LITTLE more than that by saying /5, mostly based on intuition
  CPAP_forwardses = [
    Direction(CPAP_back_centers[0], CPAP_target_approx - intake_middle.curve_tangent*intake_flat_width/5),
    Direction(CPAP_back_centers[1], CPAP_target_approx + intake_middle.curve_tangent*intake_flat_width/5),
  ]
  
  # we also want a canonical "the average CPAP intake direction in general"
  # to use for constructing the geometry of the shared parts
  CPAP_forwards_average = Direction (CPAP_forwardses[0] + CPAP_forwardses[1])
  
  CPAP_forwards_average_unit_height_from_build_plane = CPAP_forwards_average/abs(CPAP_forwards_average.dot(intake_reference_curve.plane.normal((0,0))))
              

  intake_spout_smallest_radius = 3
  intake_spout_largest_radius = min_wall_thickness + intake_flat_air_thickness_base + min_wall_thickness + intake_spout_smallest_radius
  # the shield-ward surface of the intake wants to have a bit of a weird shape because of the shield surface shape, but for the face-ward surface, we can just use a plane. Let's define that plane:
  # the point on the build plate that's at the middle of the edge of the intake closest to the face:
  # so we are now working in a coordinate system where the dimensions are:
  # 1) towards_air_target
  # 2) CPAP_forwards_average
  # 3) intake_middle.curve_tangent
  
  au = towards_air_target_unit_height_from_shield 
  fu = CPAP_forwards_average_unit_height_from_build_plane
  ct = intake_middle.curve_tangent
  
  intake_faceward_middle = intake_middle.position + au * intake_spout_largest_radius
  
  # notably, the above isn't an orthogonal basis. To define the plane, we actually want a face that is approximately aligned with the shield, and thus, aligned with the curve tangent and CPAP_forwards, but NOT perpendicular to towards_air_target (because towards_air_target isn't perpendicular to the shield)
  intake_exit_plane = Plane(intake_faceward_middle, Direction (ct.cross(fu)))
  
  # an origin point for the center of curvature of the spout
  intake_radius_center_middle = intake_faceward_middle - CPAP_forwards_average_unit_height_from_build_plane * intake_spout_largest_radius
  
  # we are going to decide the control points in terms of a collection of cross-sections, uniformly spaced along the intake_middle.curve_tangent dimension; The control points across different cross-sections will be combined into hoops later.
    
  num_points_long_side = 14
  num_points_short_side = 5
  num_points_total = (num_points_long_side + num_points_short_side)*2
  
  cross_section_points = []
  
  for tangent_offset in subdivisions (intake_flat_width/2, -intake_flat_width/2, amount = num_points_long_side+2):
    radius_center = intake_radius_center_middle + ct*tangent_offset
    
    exit_points = [
      radius_center + fu * intake_spout_largest_radius,
      radius_center + fu * intake_spout_smallest_radius,
    ]
    
    # since we're going to use offset-surfaces later, and those offset-surfaces won't naturally agree with the exit plane, we extend it a little bit past the exit plane
    beyond_exit_points = [thing + au*3 for thing in exit_points]
    
    towards_exit_points = [
      exit_points[0] - au * intake_spout_largest_radius * 0.7,
      exit_points[1] - au * intake_spout_smallest_radius * 0.7,
    ]
    
    # for the next hoop, we want it to be aligned with the edge of the shield.
    # To simplify the geometry for us, instead of making the shield glue face an exact width, we make it an exact height from the build plane:
    sample = ShieldSample(intersecting = RayIsh(intake_faceward_middle + ct*tangent_offset - fu*shield_glue_face_width, -au))
    
    shield_guide_points = [
      sample.position,
      radius_center + Direction (radius_center, sample.position)*intake_spout_smallest_radius
    ]
    
    cross_section_points.append ([
      beyond_exit_points,
      exit_points,
      towards_exit_points,
      shield_guide_points
    ])
  frames = list(zip(*cross_section_points))
    
  def CPAP_hoop (CPAP_back_center, CPAP_forwards, frac):
    offset = (1 - frac) * 20
    center = CPAP_back_center + CPAP_forwards*offset
    direction = Direction (CPAP_forwards.cross (CPAP_forwards.cross (towards_air_target)))
    
    start_index = (num_points_long_side-1)/2
    def CPAP_point (index):
      angle = -(index-start_index)/num_points_total*math.tau
      return center + (direction*CPAP_outer_radius) @ Rotate(CPAP_forwards, radians=angle)
    return [CPAP_point (index) for index in range (num_points_total)]

  intake_surfaces = []
  for CPAP_back_center, CPAP_forwards in zip(CPAP_back_centers, CPAP_forwardses):
    hoops = [flatten([
      [large for large, small in frame[1:-1]],
      subdivisions(*frame[-1], amount = num_points_short_side+2)[1:-1],
      [small for large, small in reversed(frame[1:-1])],
      reversed(subdivisions(*frame[0], amount = num_points_short_side+2)[1:-1]),
    ])
    for frame in frames] + [CPAP_hoop (CPAP_back_center, CPAP_forwards, frac) for frac in [-0.3, 0.4, 0.6, 0.8, 1.0]]
        
    intake_surfaces.append(BSplineSurface(hoops, v=BSplineDimension(periodic=True)))
    
  save("new_intake", Compound (Face(intake_surfaces[0]).offset(min_wall_thickness, fill=True), Face(intake_surfaces[1])))

  preview(intake_surfaces)

  
  intake_support_hoops = []
  intake_support_exclusion_hoops = []
    
  for sample in curve_samples(intake_reference_curve, 1, intake_middle.curve_distance + intake_flat_width/2 + elastic_corner_opening_width, max_length=5):
    augment_intake_sample(sample)
    
    thickness1 = min(sample.curve_distance / 3, intake_support_thickness)
    thickness2 = min(sample.curve_distance / 6, intake_support_thickness)
    b = -sample.normal_in_plane_unit_height_from_shield * thickness1
    b2 = -sample.normal_in_plane_unit_height_from_shield * thickness2
        
    intake_support_hoops.append (Wire ([
      sample.position,
      sample.position + b,
      sample.below_shield_glue_base_point + b2,
      sample.below_shield_glue_base_point,
    ], loop = True))
    if sample.curve_distance < 32:
      a = contact_leeway * sample.normal_in_plane_unit_height_from_shield
      b = b - contact_leeway * sample.normal_in_plane_unit_height_from_shield
      c = contact_leeway * sample.along_intake_flat_unit_height_from_plane
      d = -contact_leeway * sample.curve_tangent
      intake_support_exclusion_hoops.append (Wire ([
        sample.position + a - c + d,
        sample.position + b - c + d,
        sample.below_shield_glue_base_point + b2 + c + d,
        sample.below_shield_glue_base_point + a + c + d,
      ], loop = True))
  
  save ("intake_support", Loft(intake_support_hoops, solid = True, ruled = True))
  save ("intake_support_exclusion", Loft(intake_support_exclusion_hoops, solid = True, ruled = True))
    
  
  intake_cloth_lip = []
  intake_shield_lip = []
  
  sample = CurveSample(intake_reference_curve, distance = intake_middle.curve_distance - intake_flat_width/2 - elastic_corner_opening_width)
  augment_intake_sample(sample)
  target_shield_convex_corner_above_intake = sample.below_elastic_base_point
  save("target_shield_convex_corner_above_intake", target_shield_convex_corner_above_intake)
  
  sample = CurveSample(intake_reference_curve, distance = intake_middle.curve_distance + intake_flat_width/2 + elastic_corner_opening_width)
  augment_intake_sample(sample)
  target_shield_convex_corner_below_intake = sample.below_elastic_base_point
  save("target_shield_convex_corner_below_intake", target_shield_convex_corner_below_intake)
  
  for sample in curve_samples(intake_reference_curve, intake_middle.curve_distance - intake_flat_width/2 - elastic_corner_opening_width, intake_middle.curve_distance + intake_flat_width/2 + elastic_corner_opening_width, max_length = 3):
    augment_intake_sample(sample)
    intake_shield_lip.append (sample.below_shield_glue_base_point)
  
  
  
  intake_air_cut_hoops = []
  intake_edges = ([], [], [], [])
  for sample in curve_samples(intake_reference_curve, intake_middle.curve_distance - intake_flat_width/2 + 0.1, intake_middle.curve_distance + intake_flat_width/2 - 0.1, amount = 70):
    augment_intake_sample(sample)
    
    # Get the offset relative to intake_middle:
    offset = sample.curve_distance - intake_middle.curve_distance
    relative_offset = offset / intake_flat_width
    
    # now, compute the shape of innermost edge (closest to the face), in the form of a height from the shield surface
    full_thickness_base = (intake_flat_air_thickness_base + 2*min_wall_thickness)
    #full_thickness = full_thickness_base * math.cos(relative_offset * math.pi)
    #full_thickness_derivative = -math.pi * full_thickness_base * math.sin(relative_offset * math.pi) / intake_flat_width
    full_thickness = full_thickness_base * math.cos(relative_offset * math.pi)**(2/3)
    full_thickness_derivative = -(2/3) * math.pi * full_thickness_base * math.sin(relative_offset * math.pi) / math.cos(relative_offset * math.pi)**(1/3) / intake_flat_width
    
    innermost_edge_normal_angle = math.atan2(full_thickness_derivative, 1)
        
    # we need wall to be uniform thickness, but we don't care about the shape of the air channel that much.
    # so we express these in two parts - an offset from the shield surface,
    # and an offset back from the first offset in the direction perpendicular to the curve of the innermost edge 
    edge_distances = [(0,0),
      (min_wall_thickness,0),
      (full_thickness, -min_wall_thickness),
      (full_thickness, 0),
    ]
    
    intake_edge_heights = []
    intake_edge_offsets = []
    for from_shield, from_edge in edge_distances:
      x = from_shield + from_edge * math.cos(innermost_edge_normal_angle)
      y = -from_edge * math.sin(innermost_edge_normal_angle)
      intake_edge_heights.append(x)
      intake_edge_offsets.append(
        - x*sample.normal_in_plane_unit_height_from_shield
        + y*sample.curve_tangent
      )

    
    if intake_edge_heights[3] > intake_edge_heights[0] + 0.1:
      for index in [0,3]:
        intake_edges [index].append ((
          sample.position + intake_edge_offsets [index],
          sample.below_shield_glue_base_point + intake_edge_offsets [index],
          sample.below_elastic_base_point + intake_edge_offsets [index],
        ))
    beyond_air = True
    if intake_edge_heights[2] > intake_edge_heights[1] + 0.1:
      beyond_air = False
      for index in [1,2]:
        intake_edges [index].append ((
          sample.position + intake_edge_offsets [index],
          sample.below_shield_glue_base_point + intake_edge_offsets [index],
          sample.below_elastic_base_point + intake_edge_offsets [index],
        ))
    
      
    if intake_edge_heights[2] > intake_edge_heights[1] + 1:
      q = sample.position + Up*0.01
      b = -sample.normal_in_plane_unit_height_from_shield * 20
      a = -sample.normal_in_plane_unit_height_from_shield * (min_wall_thickness*2)
      k = Between(sample.below_shield_glue_base_point, sample.below_elastic_base_point, 0.4)
      intake_air_cut_hoops.append (Wire ([
        q + a,
        q + b,
        k + b,
        k + a,
      ], loop = True))
  
  
  fins = []
  for sample in curve_samples(intake_reference_curve, intake_middle.curve_distance - intake_flat_width/2 + 9, intake_middle.curve_distance + intake_flat_width/2 - 11, amount = 6):
    augment_intake_sample(sample)
    perpendicular = towards_air_target.cross(sample.plane_normal)
    k = Between(sample.below_shield_glue_base_point, sample.below_elastic_base_point, 0.5)
    fins.append(Edge((Segment(sample.position, k)) @ Translate(towards_air_target * min_wall_thickness/2)).extrude(towards_air_target*20).extrude(perpendicular * min_wall_thickness, centered = True))
        
        
  intake_inner_ribs = intake_edges [1] + intake_edges[2][::-1]
  intake_outer_ribs = intake_edges [0] + intake_edges[3][::-1]
    

  save("intake_shield_lip", intake_shield_lip)

  intake_air_cut = Loft([intake_air_cut_hoops[0], intake_air_cut_hoops[-1]], solid = True, ruled = True)
  

  class IntakeSurface:
    def __init__(self, ribs, expansion):
      self.ribs = ribs
      self.expansion = expansion
      self.num_points = len(self.ribs)
      
      self.hoops = [self.flat_hoop (frac) for frac in [0,0.3,0.5,0.6,0.9,1.5]] + [self.CPAP_hoop (frac) for frac in [-0.3, 0.4, 0.6, 0.8, 1.0]]
      self.ends = [
        self.wire (self.hoops[0]),
        self.wire (self.hoops[-1])
      ]
      self.surface = BSplineSurface(self.hoops,
         v= BSplineDimension (periodic = True),
      )
      
    def wire(self, hoop):
      curve = BSplineCurve(hoop,
        BSplineDimension (periodic = True),
      )
      return Wire (Edge (curve))
       
    def CPAP_hoop (self, frac):
      offset = (1 - frac) * 20
      center = CPAP_back_center + CPAP_forwards*offset
      direction = -Direction (CPAP_forwards.cross (intake_middle.normal))
      other_direction = direction.cross (CPAP_forwards)
      def CPAP_point (index):
        angle = index/self.num_points*math.tau - 0.7*math.tau
        return center + direction*(CPAP_inner_radius + self.expansion)*math.sin (angle) + other_direction*(CPAP_inner_radius + self.expansion)*math.cos(angle)
      return [CPAP_point (index) for index in range (self.num_points)]

    def flat_hoop(self, frac):
      return [Between (b,c,(frac-0.5) * 2) if frac >= 0.5 else Between (a,b,frac * 2) for a,b,c in self.ribs]

  intake_interior = IntakeSurface (intake_inner_ribs, 0)
  intake_exterior = IntakeSurface (intake_outer_ribs, min_wall_thickness)
  def intake_cover(index):
    return Face (intake_exterior.ends[index], holes = intake_interior.ends[index].complemented())
  intake_CPAP_cover = intake_cover (-1)
  intake_flat_cover = intake_cover (0)
  save ("intake_solid", Solid (Shell (
    Face (intake_interior.surface),
    Face (intake_exterior.surface),
    intake_CPAP_cover,
    intake_flat_cover,
  )).cut(intake_air_cut))
  intake_solid_including_interior = Solid (Shell (
    Face (intake_exterior.surface),
    [Face (a) for a in intake_exterior.ends]
  ))
  save ("intake_fins", Compound(fins, Face(intake_reference_curve.plane).extrude(-intake_reference_curve.plane.normal((0,0))*min_wall_thickness)).intersection(intake_solid_including_interior))
  
  taut_direction = -intake_middle.normal
  for frac in subdivisions(0.2, 0.8, amount = 15):
    base = Between(target_shield_convex_corner_above_intake, target_shield_convex_corner_below_intake, frac)
    
    # a fairly arbitrary approximation, but a fully realistic calculation would be way more effort than it'd be worth
    intake_cloth_lip.append (intake_exterior.surface.intersections(RayIsh(base + taut_direction*1, taut_direction)).point())
  save("intake_cloth_lip", intake_cloth_lip)
    
  

#p review(intake_solid, intake_support, intake_fins, Compound([Vertex(a) for a in intake_shield_lip]), BSplineCurve(intake_cloth_lip))