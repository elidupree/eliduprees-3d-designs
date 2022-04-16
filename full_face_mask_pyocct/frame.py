


########################################################################
########  Forehead/headband  #######
########################################################################


standard_forehead_points = [forehead_point + vector (a,b,0) for a,b in [
  (0, 0),
  (15, -0.01),
  (25, -2.5),
  (35, -7),
  (45, -14),
  (55, -27),
  (62, -37),
  (71, -53),
  (79, -90),
  (81, -107),
  (81, -130),
  (60, -180),
  (15, -195),
  (0, -195),
]]
standard_forehead_poles = [a@Mirror (Right) for a in reversed(standard_forehead_points[1:-1])] + standard_forehead_points
save ("standard_forehead_curve", BSplineCurve(
  standard_forehead_poles,
  BSplineDimension (periodic = True),
))
print(f"Standard forehead circumference: {standard_forehead_curve.length()}")


def flat_to_headband(shape):
  return (shape@Translate (Up*headband_top)).extrude (Down*headband_width)

@run_if_changed
def make_standard_headband():
  standard_headband_2D = Offset2D(Wire (Edge (standard_forehead_curve)), headband_thickness, fill = True)
  save ("standard_headband_2D", standard_headband_2D)

  standard_headband = flat_to_headband(standard_headband_2D)
  save("standard_headband", standard_headband)


head_variability = max_head_circumference - min_head_circumference


def forehead_wave(*distance_range):
  forehead_wave_curves = []
  for (distance0, start), (distance1, finish) in pairs ([(d, standard_forehead_curve.derivatives(distance=d)) for d in subdivisions (*distance_range, max_length = 17)]):
    middle = standard_forehead_curve.derivatives(distance = (distance1 + distance0)/2)
    control_distance = (distance1 - distance0)/4
    close_offset = -min_wall_thickness * 1.3
    far_offset = -6.6 - min_wall_thickness/2
    forehead_wave_curves.append (BSplineCurve([
      start.position + start.normal*close_offset,
      start.position + start.normal*close_offset + start.tangent*control_distance,
      middle.position + middle.normal*far_offset - middle.tangent*control_distance,
      middle.position + middle.normal*far_offset,
    ]))
    forehead_wave_curves.append (BSplineCurve([
      middle.position + middle.normal*far_offset,
      middle.position + middle.normal*far_offset + middle.tangent*control_distance,
      finish.position + finish.normal*close_offset - finish.tangent*control_distance,
      finish.position + finish.normal*close_offset,
    ]))
    
  return Face(Offset2D(Wire (Edge(curve) for curve in forehead_wave_curves), min_wall_thickness/2))



temple_on_headband_distance = standard_forehead_curve.distance (closest = temple)
temple_on_headband_derivatives = standard_forehead_curve.derivatives(closest = temple)


temple_block_length = 36
temple_block_start_distance = temple_on_headband_distance
temple_block_end_distance = temple_block_start_distance - temple_block_length


@run_if_changed
def make_temple_block():
  temple_block_start_derivatives = standard_forehead_curve.derivatives(distance = temple_block_start_distance)
  temple_block_hoops = []  
  for distance in subdivisions(temple_block_start_distance, temple_block_end_distance, amount=10):
    d = standard_forehead_curve.derivatives(distance = distance)
    a = d.position + Up*headband_top
    b = d.position + Up*headband_bottom
    c = ShieldSample(intersecting = RayIsh(b, -temple_block_start_derivatives.normal)).position
    d = ShieldSample(intersecting = RayIsh(a, -temple_block_start_derivatives.normal)).position
    temple_block_hoops.append(Wire([
      a, b, c, d
    ], loop = True))

  temple_block = Loft(temple_block_hoops, solid = True)
  save ("temple_block_uncut", temple_block)

standard_middle_distance = standard_forehead_curve.distance (closest = forehead_point)
temple_block_from_middle_distance = temple_block_start_distance - standard_middle_distance
#p review(temple_knob_curve , temple_block_uncut)


temple_extender_width = 6

@run_if_changed
def make_temple_extender():
  length = 60
  width = temple_extender_width
  wall_thickness = 1.5
  hoops = []
  holes = []
  for distance in subdivisions(temple_block_start_distance-17, temple_block_start_distance+length, amount=30):
    d = standard_forehead_curve.derivatives(distance = distance)
    a = d.position + Up*headband_top
    b = d.position + Up*headband_bottom
    k = -d.normal * width
    j = -d.normal * wall_thickness
    l = -d.normal * (width - wall_thickness)
    z = Up*1
    hoops.append(Wire([
      a, b, b+k, a+k
    ], loop = True))
    holes.append(Wire([
      a+z+j, b-z+j, b-z+l, a+z+l
    ], loop = True))
  result = Loft(hoops, solid = True)
  result = Fillet(result, [(edge, width/2.2) for edge in result.edges() if all_equal(v[1] for v in edge.vertices())])
  for foo in range(3):
    bar = 11 + foo * 6
    result = result.cut(Loft(holes[bar:bar + 6], solid= True))
  
  save("temple_extender", result)
  #save_STL("temple_extender_hack", result)
    


  
@run_if_changed
def make_headband_wave():
  q = temple_block_from_middle_distance - temple_block_length + 0.5
  face = forehead_wave(
    standard_middle_distance + q,
    standard_middle_distance - q,
  )
  save("standard_headband_wave", flat_to_headband(face))
  


forehead_cloth_start_on_headband_distance = temple_on_headband_distance - 20
forehead_cloth_start_on_headband_derivatives = standard_forehead_curve.derivatives(distance = forehead_cloth_start_on_headband_distance)
f = forehead_cloth_start_on_headband_derivatives
forehead_cloth_start_on_shield = ShieldSample(intersecting = RayIsh(f.position + Up*headband_top, -f.normal)).position

@run_if_changed
def make_temple_block_cuts():
  '''temple_block_cuts_depth = 4
  forehead_cloth_start_on_headband_derivatives = standard_forehead_curve.derivatives(distance = forehead_cloth_start_on_headband_distance)
  f = forehead_cloth_start_on_headband_derivatives
  g = f.position + Up*headband_top - f.normal*min_wall_thickness
  forehead_cloth_cut_1 = Edge(
    g,
    g + (forehead_cloth_start_on_shield-g)*2,
  ).extrude(Down*temple_block_cuts_depth - f.tangent*2).extrude(f.tangent*3)
  
  forehead_cloth_cut_2_hoops = []
  for distance in subdivisions(forehead_cloth_start_on_headband_distance, temple_block_end_distance-1, amount=15):
    d = standard_forehead_curve.derivatives(distance = distance)
    q = temple_block_end_distance
    frac = min(1.0, (distance - q) / (forehead_cloth_start_on_headband_distance - 5 - q))
    a = d.position + Up*headband_top - d.normal * min_wall_thickness + Up*(1-frac)*temple_block_cuts_depth
    b = a - d.normal * 3
    c = Down*temple_block_cuts_depth
    forehead_cloth_cut_2_hoops.append(Wire([
      a, b, b+c, a+c
    ], loop = True))
  forehead_cloth_cut_2 = Loft(forehead_cloth_cut_2_hoops, solid = True, ruled = True)
  save("temple_block", temple_block_uncut.cut(forehead_cloth_cut_1).cut(forehead_cloth_cut_2))'''
  save("temple_block", temple_block_uncut)

'''
@run_if_changed
def make_elastic_loop():
  shield_exclusion = Face (shield_surface).intersection (HalfSpace (Point (10, 0, 0), Right)).intersection (HalfSpace (temple, Back)).extrude (Left*lots) @ Translate(Left*0.1)
  c = Point(temple[0] + 8, temple[1] + 15, headband_top)
  a = Axes(c, Up, Right)
  r = 7
  f = Face(Wire(Edge(Circle(a, r))), holes= Wire(Edge(Circle(a, r-1.5))).complemented())
  save("elastic_loop", f.extrude(Down*3).cut(shield_exclusion))'''
  
########################################################################
########  Side rim and stuff #######
########################################################################

upper_side_curve_source_points = [
  Point (0, shield_back, headband_top),
  Point (0, shield_back, target_shield_convex_corner_above_intake[2]),
]
save ("upper_side_curve_source_surface", BSplineSurface([
    upper_side_curve_source_points,
    [point + Right*100 for point in upper_side_curve_source_points],
  ],
  BSplineDimension (degree = 1),
  BSplineDimension (degree = 1),
))

@run_if_changed
def make_upper_side_curve():
  save ("shield_upper_side_curve", ShieldCurveInPlane(upper_side_curve_source_surface))

upper_side_cloth_lip = []
for sample in curve_samples(shield_upper_side_curve, amount = 20):
  upper_side_cloth_lip.append (sample.position)



shield_lower_curve_source_points = [
  ShieldSample(closest = target_shield_convex_corner_below_intake).position,
 #ShieldSample(closest = shield_bottom_peak.position + Right*5).position,
  ShieldSample(closest = shield_bottom_peak.position + Right*20).position,
  shield_bottom_peak.position,
]
shield_lower_curve_source_points = shield_lower_curve_source_points + [a@Mirror(Right) for a in reversed(shield_lower_curve_source_points[:-1])]
save ("shield_lower_curve_source_surface", BSplineSurface([
    [point + Front*0.1 for point in shield_lower_curve_source_points],
    [point + Back*100+Down*100 for point in shield_lower_curve_source_points],
  ],
  BSplineDimension (degree = 1),
  BSplineDimension (degree = 3),
))

@run_if_changed
def make_shield_lower_curve():
  save ("shield_lower_curve", shield_surface.intersections (
    shield_lower_curve_source_surface
  ).curve())
  
lower_curve_cloth_lip = []
for sample in curve_samples(shield_lower_curve, amount = 50):
  lower_curve_cloth_lip.append (sample.position)


  

z = -1.2
a=0
b=3
c=5
s=-4
p=-1
q=1
r=4
temple_knob_coordinates = [
  (z, s), (a, s), (a,p), (b,p), (b,s), (c,s), (c,p), (c,q), (c,r), (b,r), (b,q), (a,q), (a,r), (z, r)
]
temple_knob_offset = -4
def temple_knob_ring(z, offset):
  sample = CurveSample(shield_upper_side_curve, z=z)
  result = []
  for x,y in temple_knob_coordinates:
    d = standard_forehead_curve.derivatives(distance = temple_block_start_distance+offset-y)
    #s2 = ShieldSample(intersecting = RayIsh(sample.position - sample.curve_in_surface_normal*y, Left, length=1))
    result.append(d.position - d.normal*(temple_extender_width + x))
    result[-1][2] = z
  return result

@run_if_changed
def make_temple_knob():
  knobs = []
  for offset in [-1, neck_offset]:
    temple_knob_rings = [temple_knob_ring(a, offset) for a in [headband_top, headband_top - 5]]
    temple_knob_surface = BSplineSurface(temple_knob_rings, BSplineDimension(degree=1), BSplineDimension(periodic = True))
    knobs.append(Solid(Shell(
        [Face(temple_knob_surface)] + [Face(BSplineCurve(r, BSplineDimension(periodic = True))) for r in temple_knob_rings]
      )))
  
  save("temple_knob", Compound(knobs))


upper_side_rim_bottom = 47

  
@run_if_changed
def make_side_pegs():
  shield_exclusion = Face (shield_surface).intersection (HalfSpace (Point (10, 0, 0), Right)).intersection (HalfSpace (temple, Back)).extrude (Right*lots)
  forehead_exclusion = Face(standard_forehead_curve).extrude(Down*lots, centered=True)
  #build_plate_exclusion = Face(intake_reference_curve.plane).extrude(Back*lots)
  
  def side_peg (sample, expansion):
    return Vertex(
      sample.position - 5.5*sample.curve_in_surface_normal
    ).extrude(-sample.normal*10 + sample.curve_in_surface_normal*7).extrude (sample.curve_tangent*(3+expansion), centered = True).extrude (sample.curve_in_surface_normal*(3+expansion), centered = True)
  
  side_peg_samples = list(curve_samples (shield_upper_side_curve, upper_side_rim_bottom - 4, upper_side_rim_bottom - 12, amount = 2))
  save ("side_peg_holes", Compound ([side_peg(sample, contact_leeway*2) for sample in side_peg_samples]))
  save ("side_pegs", Compound ([side_peg(sample, 0) for sample in side_peg_samples]).cut(shield_exclusion).cut(forehead_exclusion))
  

@run_if_changed
def make_upper_side_rim():
  upper_side_rim_hoops = []
  top_curve_start = putative_eyeball [2] + 15
  forehead_exclusion = Face(standard_forehead_curve).extrude(Down*lots, centered=True)
  forehead_size = standard_forehead_curve.value (closest = temple) [0]
  for sample in curve_samples(shield_upper_side_curve, headband_width-0.1, upper_side_rim_bottom, amount = 20):
    glue_width = shield_glue_face_width+1
    highness = (sample.position [2] - top_curve_start)/(headband_top-3 - top_curve_start)
    if highness > 0:
      glue_width += 30 * (1 - math.sqrt(1 - highness**2))
    front_edge = sample.position - glue_width*sample.curve_in_surface_normal
    
    # note: the math for the part at the bottom is a bit inelegant, which will reduce maintainability. Part of the reason for this is that I couldn't use a Loft if I allowed the little shield-holder ridge to be cut off. TODO: improve upon this troublesome thing
    conservative_eyeball = putative_eyeball + Front*20
    towards_eye_normal = Direction (Vector(front_edge, conservative_eyeball).projected_perpendicular (sample.curve_tangent))
    adjusted_forehead_exclusion = forehead_exclusion
    required_solid_x = sample.position [0] - min_wall_thickness
    if required_solid_x < forehead_size:
      scale = Scale(required_solid_x/forehead_size, center = Point(0, temple[1], 0))
      adjusted_forehead_exclusion = adjusted_forehead_exclusion @ scale
    
    face = Face(Wire([
      #sample.position,
      front_edge,
      front_edge + towards_eye_normal*50,
      sample.position - sample.normal_in_plane*30,
      sample.position + vector(0,0.01,0), # avoid buggy degerenate case in shield cut below
    ], loop = True))
    upper_side_rim_hoops.append(face.cut(adjusted_forehead_exclusion).wire())
  
  upper_side_rim = Loft (upper_side_rim_hoops, solid = True)
  
  shield_cut = Face (shield_surface).intersection (HalfSpace (Point (10, 0, 0), Right)).intersection (HalfSpace (temple, Back)).extrude (Right*lots)

  upper_side_rim = upper_side_rim.cut(shield_cut)
  upper_side_rim = upper_side_rim.cut(side_peg_holes)
  upper_side_rim = upper_side_rim.cut(intake_support_exclusion)
  
  save ("upper_side_rim", upper_side_rim)
  


preview(temple_extender, shield_bottom_peak.position, target_shield_convex_corner_below_intake, side_pegs, upper_side_rim.wires(), temple_block, temple_knob, intake_wall, intake_support, intake_support_exclusion, intake_fins, Compound([Vertex(a) for a in upper_side_cloth_lip + intake_shield_lip + lower_curve_cloth_lip]), BSplineCurve(upper_side_cloth_lip + intake_cloth_lip + lower_curve_cloth_lip))
  
  

  


#preview(upper_side_rim, lower_side_rim, top_rim, standard_headband, top_hook, side_hook, eye_lasers, glasses_edge)  