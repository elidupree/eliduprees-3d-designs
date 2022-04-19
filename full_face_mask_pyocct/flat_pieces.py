
########################################################################
########  Combine the parts of shield/cloth lip from above  #######
########################################################################

side_shield_lip_points = (
    upper_side_cloth_lip
    + intake_shield_lip
    + lower_curve_cloth_lip
    #+ [a@Mirror (Right) for a in intake_shield_lip[::-1]]
    + [a@Mirror (Right) for a in upper_side_cloth_lip[::-1]]
  )
chin_cloth_lip_points = (
    upper_side_cloth_lip
    + intake_cloth_lip
    + lower_curve_cloth_lip
    #+ [a@Mirror (Right) for a in intake_cloth_lip[::-1]]
    + [a@Mirror (Right) for a in upper_side_cloth_lip[::-1]]
  )
@run_if_changed
def make_cloth_lip():
  save ("chin_cloth_lip", Interpolate (chin_cloth_lip_points))
#save ("side_shield_lip_points", Compound([Vertex(a) for a in side_shield_lip_points])

#p review(intake_solid, intake_support, chin_cloth_lip, Compound ([Vertex (point) for point in side_shield_lip_points]), Edge(air_target, CurveSample(shield_lower_side_curve, z=-100, which=0).position))

########################################################################
########  Unrolled shield shape  #######
########################################################################

flat_approximation_increments = 201
@run_if_changed
def make_flat_approximations():
  previous_sample = None
  flat_approximations = [0]
  for sample in curve_samples(shield_top_curve, amount=flat_approximation_increments):
    if previous_sample is not None:
      difference = sample.position - previous_sample.position
      average = Between(sample.position, previous_sample.position)
      from_focus = Vector(shield_focal_point, average)
      relevant_difference = difference - from_focus*(difference.dot(from_focus)/from_focus.dot(from_focus))
      angle = math.atan2(relevant_difference.length(), from_focus.length())
      flat_approximations.append (flat_approximations [-1] + angle)
    previous_sample = sample
  #print (f"{flat_approximations}")
  save("flat_approximations", flat_approximations)
  
def flat_approximate_angle (position):
  difference = (position - shield_focal_point)
  projected = CurveSample (shield_top_curve, closest = shield_focal_point + difference*(shield_top_curve.StartPoint()[2] - shield_focal_point[2])/difference [2])
  adjusted = projected.curve_distance*(flat_approximation_increments -1)/shield_top_curve.precomputed_length
  #linearly interpolate
  floor = math.floor (adjusted)
  fraction = adjusted - floor
  previous = flat_approximations [floor]
  if floor+1 >= len(flat_approximations):
    assert(floor+0.99 < len(flat_approximations))
    result = previous
  else:
    next = flat_approximations [floor + 1]
    result = next*fraction + previous*(1-fraction)
  #print (f" angles: {surface.ellipse_parameter}, {adjusted}, floor: {floor}, {fraction}, {previous}, {next}, {result}, ")
  # put 0 in the middle
  return result - flat_approximations [(flat_approximation_increments -1)//2]
  


def unrolled(position):
  offset = position - shield_focal_point
  distance = offset.length()
  paper_radians = flat_approximate_angle (position)
  result = Point(
    distance*math.cos(paper_radians),
    distance*math.sin (paper_radians),
    0
  )
  return (position, result)
def segments (vertices):
  result = []
  for (a,b), (c,d) in zip (vertices [: -1], vertices [1:]):
    original = (a - c).length()
    derived = (b - d).length()
    ratio = derived/original
    
    #print (f"distances: {original}, {derived}, {derived/original}")
    assert (abs (1 - ratio) <=0.01)
    result.append(Edge(b, d))
  print (f"total length: {sum( segment.length() for segment in result)}")
  return result

@run_if_changed
def make_unrolled_shield():
  unrolled_side = [unrolled (position) for position in reversed(side_shield_lip_points)]
  unrolled_top = [unrolled (surface.position) for surface in curve_samples (shield_top_curve, 0, shield_top_curve.precomputed_length, amount=40)]
  print (unrolled_top[0], unrolled_top[-1], unrolled_side[0], unrolled_side[-1])
    
  unrolled_combined = unrolled_top+unrolled_side
  center_vertices_on_letter_paper(lambda: (vertex [1] for vertex in unrolled_combined))
      
  unrolled_shield_wire = Wire(
    segments (unrolled_side) + segments (unrolled_top) #+ [Edge(unrolled_side[0][1], unrolled_top[-1][1])]
  )
  save("unrolled_shield_wire", unrolled_shield_wire)
  save_inkscape_svg("unrolled_shield", unrolled_shield_wire)
#preview(unrolled_shield_wire)

########################################################################
########  Forehead cloth  #######
########################################################################
'''
For the top cloth:

In the current design, we glue one edge of the cloth to the interior face of the headband, and the other edge to the exterior face of the shield.

The biggest challenge here is the headband face. To make it conform to flat face of the headband, it want its flattened form to be a rectangle. But by also folding it over towards the shield, we create an edge of negative Gaussian curvature, which requires some form of pleating.

The outer edge is easier – it has positive Gaussian curvature, so we can just fold the cloth over and scrunch it. The main constraint for the outer edge is that its flattened form must be (at least) the length of its 3D form.

To do calculus on this, I'm going to partition the source shape (the region from the top edge of the headband to the top edge of the shield) into infinitely many, infinitesimal quadrilateral slices (A, A+dA, B+dB, B), with points A and A+dA on the outer rim, and B and B+dB on the inner rim, which will be mapped into a flat shape (A', A'+dA', B'+dB', B'). Furthermore, my particular choice of partitioning will be the one where the slices are perpendicular to the headband (i.e. B perpendicular to dB). Also, I'm going to express the coordinates of the flattened points such that coordinate 0 is "along the headband" and 1 is "towards the shield", i.e. dB'[1]=0 and (A'-B')[0] = 0.

Given the source quadrilateral, we have at least the following constraints:

"Cloth can't stretch":
1. d(A', B') >= d(A, B)
2. d(A'+dA', B'+dB') >= d(A+dA, B+dB)
3. ||dA'|| >= ||dA||
4. ||dB'|| >= ||dB||

"Flattened headband must remain rectangular":
5. dB'[1] == 0
6. (A'-B')[0] == 0 (which implies (dA'-dB')[0] == 0, when you consider how it applies to the next slice)

At this point, we still have multiple degrees of freedom.
* We can make dA'[0] and dB'[0] arbitrarily large ("any number of extra unnecessary pleats along the length of both edges")
* We can make d(A', B') (and d(A'+dA', B'+dB')) arbitrarily large (and arbitrarily different from each other))

To fully constrain it, I'll add these additional constraints:

"Include a fixed, slight leeway for different head sizes":
7. d(A', B') = d(A, B) * 1.2

"Only pleat as much as you need to"
8. Within the above of constraints, minimize dA' (equivalently "minimize dB'"; equivalently, ||dA'|| = ||dA||, because the shield curve is always longer than the headband curve.).

Now that we've mapped the quadrilaterals, we can extend the cloth bit on each end to be able to fold over the plastic and be glued down.
'''

class RimHeadClothCrossSection (SerializeAsVars):
  '''
  Nominally, one of the A-B pairs described above.
  This class keeps track of both the original and flattened positions.
  '''
  def __init__(self, A, B):
    self.A = A
    self.B = B
    self.source_length = (A-B).length()

class RimHeadCloth(SerializeAsVars):
  def __init__(self, rim_samples, head_curve, *, length_multiplier):
    self.sections = []
    for sample in rim_samples:
      head = head_curve.derivatives(closest = sample)
      section = RimHeadClothCrossSection(sample, head.position)
      if len(self.sections) == 0:
        section.B_prime = Point()
      else:
        previous = self.sections[-1]
        
        # we now need to find the right horizontal distance in the flattened space,
        # such that the diagonal will be exactly the desired length
        hypotenuse = (section.A - previous.A).length()
        y_distance = abs(section.source_length - previous.source_length)*length_multiplier
        x_distance = math.sqrt(hypotenuse**2 - y_distance**2)
        
        section.B_prime = previous.B_prime + Right*x_distance
      
      section.A_prime = section.B_prime + Back*section.source_length*length_multiplier
      self.sections.append(section)
    
  def source_wire(self):
    return Wire([p.A for p in self.sections] + [p.B for p in reversed(self.sections)],
      loop = True)
    
  def minimal_wire(self):
    return Wire([
        self.sections[-1].B_prime,
        self.sections[0].B_prime,
      ] + [p.A_prime for p in self.sections],
      loop = True)
  
  def extended_wire(self, rim_extra_width, head_extra_width):
    return Wire([
        self.sections[-1].A_prime,
        self.sections[-1].B_prime + Front*head_extra_width,
        self.sections[0].B_prime + Front*head_extra_width,
        self.sections[0].A_prime,
      ] + [p + (Direction(c.A_prime,d.A_prime)*rim_extra_width) @ Rotate(Up, degrees = 90) for c,d in pairs(self.sections) for p in [c.A_prime,d.A_prime]],
      loop = True)
      
@run_if_changed
def make_forehead_cloth():
  corner_backoff = 15
  forehead_cloth = RimHeadCloth(
    [a.position + a.normal*shield_thickness for a in curve_samples (shield_top_curve, corner_backoff, shield_top_curve.precomputed_length - corner_backoff, amount = math.floor(shield_top_curve.precomputed_length * 2))],
    standard_forehead_curve@Translate (Up*headband_top),
    length_multiplier = 1.2)
  save("forehead_cloth", forehead_cloth)
  save_inkscape_svg("forehead_cloth", forehead_cloth.extended_wire(shield_glue_face_width, headband_width))




########################################################################
########  Chin cloth  #######
########################################################################

# Make a virtual neck line; the details of this don't matter TOO much,
# it's mostly picked arbitrarily to end up with something that worked out
# okay for me in practice
neck_points = [
  Point(75, neck_y, 20),
  Point(75, neck_y, 0),
  Point(75, neck_y, -20),
  Point(74, neck_y, -40),
  Point(70, neck_y, -60),
  Point(66, neck_y, -80),
  Point(57, neck_y, -100),
  Point(38, neck_y, -120),
  Point(8, neck_y, -140),
]
neck_points = [Point(a[0], a[1] + a[2]*0.3, a[2]) for a in neck_points] 
neck_points = neck_points + [a@Reflect (Right) for a in reversed(neck_points)]
save ("neck_curve", BSplineCurve(neck_points))

elastic_tube_border_width = 12

@run_if_changed
def make_chin_cloth():
  # basically use the same formula as above.
  # The chin cloth has fewer constraints, so I can do basically whatever I want,
  # but it happens to be convenient for assembly if the elastic edge of the straight line (because you can fold it over instead of doing extra cuts and sewing)
  
  chin_cloth = RimHeadCloth(
    [chin_cloth_lip.value(distance = distance) for distance in subdivisions (0, chin_cloth_lip.length(), max_length = 0.5)],
    neck_curve,
    length_multiplier = 1)
  save("chin_cloth", chin_cloth)
  save_inkscape_svg("chin_cloth", chin_cloth.extended_wire(shield_glue_face_width, elastic_tube_border_width))
  
  
preview(
  forehead_cloth.source_wire(),
  forehead_cloth.minimal_wire(),
  forehead_cloth.extended_wire(shield_glue_face_width, headband_width),
  temple_extender,
  temple_block,
  temple_knob,
  chin_cloth.source_wire(),
  chin_cloth.minimal_wire(),
  chin_cloth.extended_wire(shield_glue_face_width, elastic_tube_border_width),
  )