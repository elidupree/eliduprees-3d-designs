


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

'''
math for laying out these cloths:

we want to force a particular curve of the cloth to stay on the rim. We do this by putting elastic on the outer edge (which tries to pull the cloth further onto the face shield) while making the cloth have curvature such that the next bit is shorter than the edge, so it can't be pulled over. Also, to keep the cloth relatively taut, we make every point on the rim have a straight line going to the closest point on the other curve.

To lay it out in two-dimensional space, we flatten small increments at a time. Treating it as infinitesimal, from a segment AB, we form a quadrilateral (A, B, B+dB, A+dA).
A and B are given
||dA|| is given (arc length of outer edge)
(component of (dB-dA) in the direction parallel to (B-A)) is given (change in distance from the outer edge to inner edge)

this leaves 2 degrees of freedom. Other constraints:

||dB|| >= arc length of inner edge
k(A) (signed curvature) >= a certain value (note: this is the only constraint that's nonlocal)
neither dB nor dA may become parallel to (B-A) (note: this is redundant with the below condition)
(component of dB in the direction perpendicular to (B-A))/(component of dA in the direction perpendicular to (B-A))/||B-A|| <= elastic tube border width (ability to lay out the elastic tube beyond A - wait, I think I did the math wrong here...), and vice versa for B
(dB in the direction of (B-A)) == 0 (without this condition, there's some OTHER A-to-other-curve line that's shorter than this one; if dB is positive OR negative, then there's an infinitesimally-close point that's infinitesimally shorter)

wait a minute, that last one is super restrictive... so it boils down to...

Assume X is the AB direction and Y is the other
dB[0] is 0
dA[0] can be inferred from that
dA[1] can be inferred from THAT
dB[1] is the only degree of freedom

what's the actual elastic-tube condition?
dA[1] * ||A-B|| / (dB[1] - dA[1]) >= elastic_tube_border_width, i.e. if dB[1]-dA[1] is positive,
dA[1] * ||A-B|| >= elastic_tube_border_width * (dB[1] - dA[1])
dA[1] * ||A-B|| + dA[1]*elastic_tube_border_width >= elastic_tube_border_width * dB[1]
dA[1] * ||A-B|| / elastic_tube_border_width + dA[1] >= dB[1]
dA[1] * (1 + ||A-B|| / elastic_tube_border_width) >= dB[1]

and in the other direction
dB[1] <= dA[1] / (1 + ||A-B|| / elastic_tube_border_width)


arc length of inner edge <= dB[1] <= dA[1]*||A-B||/elastic_tube_border_width
(also dA[1]*elastic_tube_border_width/||A-B|| <= dB[1], but that's redundant with the "arc length of inner edge" bond unless the B curve is already violating the elastic-tube condtion in the original shape, which doesn't happen anywhere in practice) 

the only constraint left is the curvature, which...
the angle change induced by dB[1] is (dB[1]-dA[1])/||B-A|| (which is infinitesimal)
so the curvature change is (dB[1]-dA[1])/||B-A||/||dA|| (finite again)
I'm pretty sure this is just additive with the curvature due to changes in dA as you advance through the cloth strip. Since it's linear, we can just take it relative to a base point:
curvature = (original curvature) - (dB[1]-(original dB[1]))/||B-A||/||dA||
          = (original curvature + (original dB[1]))/||B-A||/||dA||) - dB[1]/||B-A||/||dA||
if you have a target curvature and want to solve for dB
dB[1] = original dB[1] - (target curvature - original curvature) * ||B-A||*||dA||
          


'''

elastic_tube_border_width = 12

class RimHeadClothPiece(SerializeAsVars):
  pass
          
class RimHeadCloth(SerializeAsVars):
  def __init__(self, rim_samples, head_curve, target_head_multiplier = 1.5, min_curvature = 1/100, rim_extra_width = elastic_tube_border_width, head_extra_width = elastic_tube_border_width):
    self.source_head_length = 0
    self.cloth_head_length = 0
    
    self.pieces = []
    rim_samples = list(rim_samples)
    debug_display_target = 100
    debug_display_rate = math.ceil(len(rim_samples)/debug_display_target)
    
    for index, (rim_position, rim_curvature) in enumerate(rim_samples):
      piece = RimHeadClothPiece()
      piece.rim_source = rim_position
      head_parameter = head_curve.parameter (closest = piece.rim_source)
      piece.head_source = head_curve.value (head_parameter)
      source_diff = piece.head_source - piece.rim_source
      source_diff_direction = Direction (source_diff)
      piece.AB_length = source_diff.length()
      
      if len(self.pieces) == 0:
        piece.rim_output = Point()
        piece.head_output = Point(piece.AB_length, 0, 0)
      else:
        previous = self.pieces [-1]
        dA0 = previous.AB_length - piece.AB_length
        dA_length = (piece.rim_source - previous.rim_source).length()
        dA1 = math.sqrt (dA_length**2 - dA0**2)
        original_dB1 = (piece.head_source - previous.head_source).cross(source_diff_direction).length()
        original_dB_length = (piece.head_source - previous.head_source).length()
        original_curvature = rim_curvature
        min_curvature_change = min_curvature - original_curvature
        
        dB1_min_due_to_head_arc_length = original_dB_length
        dB1_min_due_to_head_extra_width = dA1/(1 + piece.AB_length / head_extra_width)
        dB1_max_due_to_rim_extra_width = dA1*(1 + piece.AB_length / rim_extra_width)
        dB1_max_due_to_curvature = original_dB1 - min_curvature_change * piece.AB_length * dA_length
        if dB1_max_due_to_rim_extra_width < dB1_max_due_to_curvature:
          print("Warning: RimHeadCloth conditions not behaving as expected (dB1_max_due_to_curvature should require positive curvature, which should make dB1_max_due_to_rim_extra_width irrelevant)")
        
        dB1_min = max(dB1_min_due_to_head_arc_length, dB1_min_due_to_head_extra_width)
        dB1_max = min(dB1_max_due_to_rim_extra_width, dB1_max_due_to_curvature)
        dB1_target = original_dB_length*target_head_multiplier
        if dB1_min > dB1_max_due_to_rim_extra_width:
          print("Warning: RimHeadCloth conditions were unsatisfiable (this should never happen in practice, because it should only happen the original position of the other rim is concave enough to prevent allocating rim_extra_width")
          dB1 = (dB1_min + dB1_max_due_to_rim_extra_width)/2
        elif dB1_min > dB1_max_due_to_curvature:
          dB1 = dB1_min
          curvature = original_curvature - (dB1 - original_dB1)/(piece.AB_length * dA_length)
          print(f"Warning: RimHeadCloth conditions couldn't be satisfied within the allowed curvature (original: {original_curvature}, allowed: {min_curvature}, used: {curvature}, difference: {min_curvature - curvature})")
        elif dB1_target < dB1_min_due_to_head_extra_width:
          print("Warning: RimHeadCloth dB1_min_due_to_head_extra_width was relevant (I thought this wouldn't happen in practice, is one of the curves really tight?)")
          dB1 = dB1_min
        elif dB1_target > dB1_max:
          dB1 = dB1_max
        else:
          dB1 = dB1_target
          
        self.source_head_length += original_dB_length
        self.cloth_head_length += dB1
        
        previous_output_direction = Direction (previous.head_output - previous.rim_output)
        previous_output_perpendicular = Direction (-previous_output_direction[1], previous_output_direction[0], 0)
        piece.rim_output = previous.rim_output + previous_output_direction*dA0 + previous_output_perpendicular*dA1
        piece.head_output = previous.head_output + previous_output_perpendicular*dB1
      
      output_diff = piece.head_output - piece.rim_output
      output_direction = Direction (output_diff)
      #print (f"cloth distances: {output_diff.length()}, {source_diff.length()}, {output_diff.length()/source_diff.length()}")
      if abs(output_diff.length()-source_diff.length()) > 0.5:
        print (f"Warning: cloth distances mismatch: original: {source_diff.length()}, generated: {output_diff.length()}, absolute difference: {output_diff.length()- source_diff.length()}, relative difference: {output_diff.length()/source_diff.length()- 1}")
      
      piece.endpoints = [
        piece.rim_output - output_direction*rim_extra_width,
        piece.head_output + output_direction*head_extra_width,
      ]
      self.pieces.append(piece)
      
      debug_display = False
      #debug_display = True
      '''if debug_display:
        if index % debug_display_rate == 0 or index == len(rim_samples) - 1:
          Part.show(Part.Compound([Part.LineSegment(piece.head_output, piece.rim_output).toShape(), Part.LineSegment(piece.head_source, piece.rim_source).toShape()]))'''
        
# TODO: more correct
def top_outer_rim_sample(sample):
  return (
    sample.position
      + min_wall_thickness*sample.normal_in_plane_unit_height_from_shield
      + min_wall_thickness*sample.curve_in_surface_normal_unit_height_from_plane,
    # hack?
    # curvature is the reciprocal of radius,
    # and I think it works out that expanding the curve is basically just expanding the radius by that amount,
    # so we can convert the curvature like so:
    1/((1/shield_top_curve.curvature(sample.curve_parameter))
      + min_wall_thickness*sample.normal_in_plane_unit_height_from_shield.length())
  )
      
@run_if_changed
def make_forehead_cloth():
  # Move the middle of the forehead inwards.
  # When the headband is put on a wider head, the headband pulls back farther than the top rim does, so we need some extra length.
  # I think 5 is enough; using 10 for some leeway.
  forehead_top_curve = BSplineCurve(
    [a + Up*headband_top + Front*((a-temple)[1])*10/(forehead_point-temple)[1] for a in standard_forehead_poles],
    BSplineDimension (periodic = True),
  )
  save("forehead_cloth_virtual_curve", forehead_top_curve)
  #forehead_top_curve = standard_forehead_curve.translated(vector(0,0,headband_top - standard_forehead_curve.StartPoint()[2]))
  forehead_cloth = RimHeadCloth(
    (top_outer_rim_sample(sample) for sample in curve_samples (shield_top_curve, shield_top_curve.precomputed_length/2, shield_top_curve.distance(closest = forehead_cloth_start_on_shield), amount = math.floor(shield_top_curve.precomputed_length * 2))),
    forehead_top_curve,
    target_head_multiplier=99,
    min_curvature = 1/130
  )
  
  save ("forehead_cloth", forehead_cloth)

  forehead_cloth_points = (
    [piece.endpoints [0] for piece in forehead_cloth.pieces]
    + [piece.endpoints [1] for piece in reversed (forehead_cloth.pieces)]
  )
  center_vertices_on_letter_paper(forehead_cloth_points)
  save("forehead_cloth_wire", Wire(forehead_cloth_points, loop=True))
  save_inkscape_svg("forehead_cloth", Wire(forehead_cloth_points, loop=True))

print(f"source_forehead_length: {forehead_cloth.source_head_length}, cloth_forehead_length: {forehead_cloth.cloth_head_length}, ratio: {forehead_cloth.cloth_head_length/forehead_cloth.source_head_length}")
reached = forehead_cloth_virtual_curve.value(distance = forehead_cloth_virtual_curve.distance(closest=forehead_point) + forehead_cloth.source_head_length/2)
original_forehead_length = standard_forehead_curve.distance(closest=reached) - standard_forehead_curve.distance(closest=reached@Reflect(Right))
print(f"original_forehead_length: {original_forehead_length}, cloth_forehead_length: {forehead_cloth.cloth_head_length}, ratio: {forehead_cloth.cloth_head_length/original_forehead_length}")


########################################################################
########  Chin cloth  #######
########################################################################

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
neck_points = [Point(a[0], a[1] + a[2]*0.2, a[2]) for a in neck_points] 
neck_points = neck_points + [a@Reflect (Right) for a in reversed(neck_points)]
save ("neck_curve", BSplineCurve(neck_points))

@run_if_changed
def make_chin_cloth():
  chin_cloth_lip_subdivisions = 500
  chin_cloth_lip_length = chin_cloth_lip.length()
  chin_cloth = RimHeadCloth(
    ((chin_cloth_lip.value (parameter), chin_cloth_lip.curvature (parameter)) for parameter in (chin_cloth_lip.parameter (distance = index*chin_cloth_lip_length/(chin_cloth_lip_subdivisions-1)) for index in range(chin_cloth_lip_subdivisions))),
    neck_curve,
    min_curvature = 1/120
  )
  save ("chin_cloth", chin_cloth)

  chin_cloth_points = (
    [piece.endpoints [0] for piece in chin_cloth.pieces]
    + [piece.endpoints [1] for piece in reversed (chin_cloth.pieces)]
  )
  center_vertices_on_letter_paper(chin_cloth_points)
  save ("chin_cloth_wire", Wire (chin_cloth_points, loop=True))
  save_inkscape_svg("chin_cloth", Wire (chin_cloth_points, loop=True))

print(f"source_neck_length: {chin_cloth.source_head_length}, cloth_neck_length: {chin_cloth.cloth_head_length}, ratio: {chin_cloth.cloth_head_length/chin_cloth.source_head_length}")