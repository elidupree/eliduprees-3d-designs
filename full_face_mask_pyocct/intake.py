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


# the center of the circle at the far CPAP connector end.
CPAP_back_center_1 = Point(72, headphones_front - 40, -92)
CPAP_back_center_2 = CPAP_back_center_1 + Vector(0, 4, -32) 
CPAP_back_centers = [CPAP_back_center_1, CPAP_back_center_2]

# a base point on the lower side curve, just inside the shield.
intake_middle = CurveSample(intake_reference_curve, z=intake_middle_z)
intake_middle_position = intake_middle.position
intake_middle_curve_tangent = intake_middle.curve_tangent
intake_middle_curve_distance = intake_middle.curve_distance
intake_middle_normal = intake_middle.normal

towards_air_target = Direction(intake_middle_position, air_target)
towards_air_target_unit_height_from_shield = towards_air_target/abs(towards_air_target.dot(intake_middle_normal))

# a reference point to try to aim the CPAP direction in a way that will make the whole shape smooth.
CPAP_target_approx = intake_middle_position + towards_air_target_unit_height_from_shield * (min_wall_thickness + intake_flat_air_thickness_base/2)

# aim the 2 CPAP hoses at the target, although also keep them a bit separate from each other (no reason to make the air converge).
# /4 might be ideal (each hose gets half the space) but I make them converge a LITTLE more than that by saying /5, mostly based on intuition
CPAP_forwardses = [
  Direction(CPAP_back_centers[0], CPAP_target_approx - intake_middle_curve_tangent*intake_flat_width/5),
  Direction(CPAP_back_centers[1], CPAP_target_approx + intake_middle_curve_tangent*intake_flat_width/5),
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
# 3) intake_middle_curve_tangent

at = towards_air_target
cf = CPAP_forwards_average
ct = intake_middle_curve_tangent
atu = at/abs(at.dot(Direction(cf.cross(ct))))
cfu = cf/abs(cf.dot(Direction(at.cross(ct))))
ctu = ct/abs(ct.dot(Direction(at.cross(cf))))

intake_faceward_middle = intake_middle_position + atu * intake_spout_largest_radius

# notably, the above isn't an orthogonal basis. To define the plane, we actually want a face that is approximately aligned with the shield, and thus, aligned with the curve tangent and CPAP_forwards, but NOT perpendicular to towards_air_target (because towards_air_target isn't perpendicular to the shield)
#intake_exit_plane = Plane(intake_faceward_middle, Direction (ct.cross(cfu)))

# an origin point for the center of curvature of the spout
intake_radius_center_middle = intake_faceward_middle - CPAP_forwards_average_unit_height_from_build_plane * intake_spout_largest_radius

# we are going to decide the control points in terms of a collection of cross-sections, uniformly spaced along the intake_middle_curve_tangent dimension; The control points across different cross-sections will be combined into hoops later.
  
num_points_long_side = 14
num_points_short_side = 5
num_points_total = (num_points_long_side + num_points_short_side)*2
  
  
  
@run_if_changed
def make_intake():
  cross_section_points = []
  
  for tangent_offset in subdivisions (intake_flat_width/2, -intake_flat_width/2, amount = num_points_long_side+2):
    radius_center = intake_radius_center_middle + ct*tangent_offset
    
    exit_points = [
      radius_center + cfu * intake_spout_largest_radius,
      radius_center + cfu * intake_spout_smallest_radius,
    ]
    
    # since we're going to use offset-surfaces later, and those offset-surfaces won't naturally agree with the exit plane, we extend it a little bit past the exit plane
    beyond_exit_points = [thing + atu*3 for thing in exit_points]
    
    towards_exit_points = [
      exit_points[0] - atu * intake_spout_largest_radius * 0.7,
      exit_points[1] - atu * intake_spout_smallest_radius * 0.7,
    ]
    
    # for the next hoop, we want it to be aligned with the edge of the shield.
    # To simplify the geometry for us, instead of making the shield glue face an exact width, we make it an exact height from the build plane:
    sample = ShieldSample(intersecting = RayIsh(intake_faceward_middle + ct*tangent_offset - cfu*shield_glue_face_width, -atu))
    
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

  beyond_exit_exclusion = Vertex (intake_faceward_middle).extrude (cfu*intake_spout_largest_radius*2, centered = True).extrude (ct*lots, centered = True).extrude (atu*lots)

  intake_outer_solids = []
  intake_outer_surfaces_extended = []
  intake_inner_solids = []
  for CPAP_back_center, CPAP_forwards in zip(CPAP_back_centers, CPAP_forwardses):
    hoops = [flatten([
      [large for large, small in frame[1:-1]],
      subdivisions(*frame[-1], amount = num_points_short_side+2)[1:-1],
      [small for large, small in reversed(frame[1:-1])],
      reversed(subdivisions(*frame[0], amount = num_points_short_side+2)[1:-1]),
    ])
    for frame in frames] + [CPAP_hoop (CPAP_back_center, CPAP_forwards, frac) for frac in [-0.3, 0.4, 0.6, 0.8, 1.0]]
    
    outer_surface_extended = BSplineSurface(hoops, v=BSplineDimension(periodic=True))
    intake_outer_surfaces_extended.append(outer_surface_extended)
    inner_surface_extended = Face (outer_surface_extended).offset(min_wall_thickness)
    
    outer_surface = Face (outer_surface_extended).cut(beyond_exit_exclusion)
    inner_surface = inner_surface_extended.cut(beyond_exit_exclusion@Translate (atu*1))
    
    def close_holes(surface):
      fa, fb = [Face(w).complemented() for w in ClosedFreeWires (surface)]
      return Solid (Shell (surface.complemented().faces() + [fa.complemented(), fb]))
    
    intake_outer_solids.append(close_holes(outer_surface))
    intake_inner_solids.append(close_holes(inner_surface))

  jiggle = Right*0.003 + Back*0.004 + Up*0.001
  
  intake_wall_solids = [s
    .cut(intake_inner_solids[1] @ Translate(jiggle-cfu*0.01))
    .cut(intake_inner_solids[0] @ Translate(-jiggle-cfu*0.01))
  for s in intake_outer_solids]

  intake_wall = Compound(intake_wall_solids)
  save("intake_wall", intake_wall)
  save("intake_outer_solids", intake_outer_solids)
  save("intake_outer_surfaces_extended", intake_outer_surfaces_extended)
  save("intake_inner_solids", intake_inner_solids)


def augment_intake_sample(sample):
  sample.cf_in_shield = Direction(cf.cross(sample.normal).cross(-sample.normal))
  sample.cfu_in_shield = sample.cf_in_shield/abs(sample.cf_in_shield.dot(sample.plane_normal))
  # basically just sample.position +
  #   shield_glue_face_width*sample.cfu_in_shield,
  # but adjusted to be exactly on the shield, but make sure to not
  # alter its height-from-build-surface
  sample.below_shield_glue_base_point = ShieldSample(
    intersecting = RayIsh(
      sample.position
        - shield_glue_face_width*sample.cfu_in_shield
        - sample.normal_in_plane * 10,
      sample.normal_in_plane)
  ).position


@run_if_changed
def make_intake_support():
  intake_support_hoops = []
  intake_support_exclusion_hoops = []
    
  for sample in curve_samples(intake_reference_curve, 1, intake_middle_curve_distance, max_length=5):
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
      c = -contact_leeway * sample.cfu_in_shield
      d = -contact_leeway * sample.curve_tangent
      intake_support_exclusion_hoops.append (Wire ([
        sample.position + a - c + d,
        sample.position + b - c + d,
        sample.below_shield_glue_base_point + b2 + c + d,
        sample.below_shield_glue_base_point + a + c + d,
      ], loop = True))
      
  intake_support_2_hoops = []
  for tangent_offset in subdivisions (intake_flat_width/2, -intake_flat_width/2, amount = num_points_long_side+2):
    a = intake_faceward_middle + ct*tangent_offset 
    b = a - cfu*shield_glue_face_width
    c = ShieldSample(intersecting = RayIsh(b, -atu)).position
    d = ShieldSample(intersecting = RayIsh(a, -atu)).position
    intake_support_2_hoops.append (Wire ([
      a,b,c,d,
    ], loop = True))
  
  intake_support = [
    Loft(intake_support_hoops, solid = True, ruled = True),
    Loft(intake_support_2_hoops, solid = True, ruled = True),
  ]
  jiggle = Right*0.003 + Back*0.004 + Up*0.001
  intake_support = Compound (
    support.cut (intake_outer_solids[1] @ Translate(jiggle+0.1*at-0.01*cf))
    for support in intake_support
  )
  
  save ("intake_support", intake_support)
  save ("intake_support_exclusion", Loft(intake_support_exclusion_hoops, solid = True, ruled = True))
    
@run_if_changed
def make_intake_peripherals():
  intake_cloth_lip = []
  intake_shield_lip = []
  
  sample = CurveSample(intake_reference_curve, distance = intake_middle_curve_distance - intake_flat_width/2 - elastic_corner_opening_width)
  augment_intake_sample(sample)
  target_shield_convex_corner_above_intake = sample.below_shield_glue_base_point - CPAP_forwardses[0] * elastic_holder_depth
  save("target_shield_convex_corner_above_intake", target_shield_convex_corner_above_intake)
  
  sample = CurveSample(intake_reference_curve, distance = intake_middle_curve_distance + intake_flat_width/2 + elastic_corner_opening_width)
  augment_intake_sample(sample)
  target_shield_convex_corner_below_intake = sample.below_shield_glue_base_point - CPAP_forwardses[1] * elastic_holder_depth
  save("target_shield_convex_corner_below_intake", target_shield_convex_corner_below_intake)
  
  for sample in curve_samples(intake_reference_curve, intake_middle_curve_distance - intake_flat_width/2 - elastic_corner_opening_width, intake_middle_curve_distance + intake_flat_width/2 + elastic_corner_opening_width, max_length = 3):
    augment_intake_sample(sample)
    intake_shield_lip.append (sample.below_shield_glue_base_point)

  save("intake_shield_lip", intake_shield_lip)
  
  
  fins = []
  for tangent_offset in subdivisions (intake_flat_width/2, -intake_flat_width/2, amount = 8)[1:-1]:
    fins.append(Vertex (intake_faceward_middle + ct*tangent_offset).extrude (ctu*min_wall_thickness, centered = True).extrude (-atu*lots).extrude (-cfu*(intake_spout_largest_radius - intake_spout_smallest_radius/3)))
        
        
  save ("intake_fins", Compound([Intersection (fin, intake_outer_solids[0]) for fin in fins]))
  
  taut_direction = intake_middle_normal
  for frac in subdivisions(0, 1, amount = 20):
    base = Between(target_shield_convex_corner_above_intake, target_shield_convex_corner_below_intake, frac) - taut_direction*30
    
    # a fairly arbitrary approximation, but a fully realistic calculation would be way more effort than it'd be worth
    ray = RayIsh(base, taut_direction)
    points = flatten ([s.intersections (ray).points for s in intake_outer_surfaces_extended])
    if points:
      intake_cloth_lip.append (min(points, key = lambda p: p.distance(base)))
  save("intake_cloth_lip", intake_cloth_lip)
    
  

#p review(intake_solid, intake_support, intake_fins, Compound([Vertex(a) for a in intake_shield_lip]), BSplineCurve(intake_cloth_lip))