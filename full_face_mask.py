'''

Big list of considerations after completing first mask prototype:

STRUCTURE:
– Currently, the forehead is shaped exactly for my forehead. Consider how to make the mask more one-size-fits-all.
– Currently, the mask doesn't have much resistance to being tilted up/down or sideways. The only resistance to torque comes from the tension of the headband elastic, combined with the contact force at the forehead. These forces have infinite mechanical disadvantage when the mask is in standard position, so it always end up being slightly tilted. Furthermore, there is always torque on the mask - the weight of the CPAP hose, and also the tension of the elastic that holds the cloth on to the chin. Improve this situation.
– Related to the above, it isn't perfectly comfortable right now – even after I glued some foam onto the forehead part, the force on my forehead is a little high.
– Even when not tilted, the chin piece is within my visual range. Move it lower.
– The mask is too bulky near my ears for me to wear my noise canceling headphones with it. Can this be fixed?
– The intake is currently angled too far out to the side, increasing the unwanted torque and potentially making it more likely to bump into things.
– Consider concerns about whether, in a bicycle crash, mask pieces would break in a dangerous way
– Maybe add a practical way to attach/detach unrelated fabric to cover the neck and back of her head against UV/bugs

PRINTING PRACTICALITIES:
– Probably we will ultimately use a manufacturing process that is not FDM - perhaps Shapeways SLS, perhaps even injection molding.
– The connection between the intake and the frame needs to be stronger (probably just by printing it as one piece; I still need to 3d-model this).
– The forehead piece isn't perfectly printable. Using my home 3D printer, it warped a little. Using SLS or injection molding, it won't be able to print as a hollow solid the same way it currently does. Improve this situation. (This may be rendered moot by structure changes)

FACE SHIELD:
– Glue it on instead of being clever with a slot. (The slot didn't hold it well enough, and also the shield buzzed when I talked.) Probably just remove one side of the slot, so there's an exposed face to glue to. (Keep the outer rim, to help with positioning and to make it so the face doesn't touch other objects if you put it down on a flat surface.)
– Pursue antireflective coating, perhaps http://www.mecanusa.com/polarizer/AR-film/AR_roll.htm.
– Probably use a material that is slightly thicker – we still want it to be possible to curve by hand, but the current version bends a little too easily, making it scrunch up a little under moderate force, which will put more and more bend marks on the surface over time.

CLOTH:
– The current mechanism of attaching the cloth was very inconvenient. Come up with a better one.
– How to properly seal the cloth around the intake?
– Generate a pattern for the cloth.
– Pick a good kind of cloth to use, perhaps based on https://pubs.acs.org/doi/full/10.1021/acsnano.0c03252
– Research whether there's any automation nowadays that would be less work than "a human manually cuts cloth using the pattern, sews it using a sewing machine, and threads the elastic".

OTHER:
– Can all the materials be heatproof so you can sterilize the mask using heat?
– This isn't about the mask per se, but there wasn't quite enough airflow for me to breathe hard. Make sure the air purifier provides more airflow.



Based on the above:

To deal with the up/down tilt, we need at least one more rigid attachment between the mask and a contact point on the head. Nowhere on the face makes a good contact point, so the natural places to consider are "further up the forehead" and "the back of the head". Using the back of the head requires a directionally-rigid component (a headband that can flex around the head to have a tight grip, but can't bend when viewed from the side of the head). Fortunately, such materials exist, and in fact, they can be 3D printed as part of the same object simply by making them wider in one dimension than the other.

Further up the forehead is trickier because I want it to be possible to wear this mask with a bicycle helmet. Anything further up the forehead would have to go *under* the helmet, but the nature of the mask means that bicycle helmet straps can't go over it and must go under it, so putting both parts under each other would be thoroughly inconvenient at best.

Asymmetric torque, as from the CPAP hose, is harder to deal with, since I prefer not to have ANY asymmetric forces on my head for comfort reasons. There's not much else that is expected to apply asymmetric torque, though, so we should be able to deal with this by simply securing the CPAP hose at the back of the head, as I do with the nose-fitting mask.

… Let's see, with the idea of a directionally-rigid headband, let's see if we can jump off onto the "one-size-fits-all" issue. We need to get rid of the wide, flat, rigid forehead piece; whatever we replace it with has to accomplish the same 2 goals: attach to the top edge of the face shield and block air from escaping between the forehead and the shield. It also must be rigid enough not to dip down into the vision area. We could have the headband plus a second, slightly flexible outer rim, strong in the same direction as the headband, rigidly attached to the headband at the 2 sides of the head. (Note that it might want to be less tall than the headband, because space between the vision area and a hypothetical bicycle helmet is limited, while the headband can go lower; being less tall is okay because the rim doesn't need to be as strong, since it's not really holding up anything.) The only question is what to use to block air passing between the headband and the rim. Cloth is a possibility, but we'd need a way to keep it taut, to prevent it from getting into the vision area. A rigid object isn't possible, but maybe an accordionlike solid could work?

Hmm, there could be a bunch of parallel curved slightly-flexible rims, dividing the space up like a grating. That could look super cool and also help keep cloth from drooping.

If I do use cloth on the forehead area, that combines this with the other main design challenge, which is how to attach the cloth conveniently. Cloth for the forehead might also reduce the amount of noise (by reducing the amount of solid interior surfaces that reflect sound back to the wearer)

For the chin cloth:
– To attach it to the frame, I'm thinking we can just make the elastic be sewn into the cloth and have a loop at each end, which goes over a hook built into the frame; it doesn't need to be adjustable. Then it's just a matter of making it easy to set into the frame (perhaps by making the contact surface rotate with the normal to the curve, plus making some cutaways in the sides of the channel so that you can get your fingers in to press it into the channel). Note that in order to form a good seal, we only need the elastic to hold the cloth taut onto the frame, which automatically happens if it's in the normal direction, as long as the curvature isn't too low. The curvature near the top is pretty low; we might need a technique to fix this, or it might become moot due to other changes. The channel doesn't need to have solid walls on the non-normal sides, it could theoretically just be rows of prongs that keep the elastic from sliding off.
– To attach it to the neck, we can do the same thing except that it now needs to be adjustable – but the elastic can be bent over the headband and attached to one of *several* hooks at different positions down the outside frame (which I guess have to be in front of the place the cloth attaches to the frame...)
– Wait, just doing both of those things means the cloth is loose at the top corner, creating a leak. This could be resolved by putting an additional, very short piece of elastic between the ends of the chin elastic and the end of the frame elastic (elastic short enough that it will be taut around the frame even when the neck elastic is at the loosest hook, but inside a cloth tube long enough that it can reach the tightest hook)
– None of these techniques make the cloth itself taut, so they don't immediately solve the forehead thing
– since the forehead thing shouldn't be flexing all that much, an exact-sized cloth might be good enough
– To deal with the intake, try to route the cloth-channel BEHIND the intake rather than in front of it
– New idea: with apologies for trying to describe a 3D shape in text: the channel on the side/bottom rim only needs to go up to around Z=-70, from which the remainder of the side frame is almost vertical. If we can put a nonconcave surface on the faceward side of the frame above that, then the elastic can be pulled taut along that whole nonconcave surface, then go over the headband and hook onto a hook on the outside of the headband. Then it only needs to hook in *one* place on each side rather than two, simplifying the design significantly. (The only reason we still need a channel on the rest of the frame is that the bottom of the mask isn't *straight*). This allows the frame to be slimmer at the sides, allowing the sides to go less far back near the ears while still staying out of the vision area.

The current design assumes that the face does not get wider as you move down from the temple. But some people have faces that do that. We don't necessarily need to PERFECTLY avoid the edges of the vision on all faces; it would be tolerable to have the side of the mask end in a vertical edge that bows outwards along with whatever point of the cheek sticks out the furthest. If the frame is slightly flexible, the face shield can afford to bow outwards in approximately this way. (It can unroll along the cone.) What we want to avoid is the case where bowing the face shield also bows out the headband, losing the seal. To accomplish both of these things at the same time, there cannot be a direct attachment between the headband and the corner of the shield. That seems fairly complicated to pull off while also attaching the cloth appropriately. Another possibility is to let the face shield bow to a position where the cheek DOES stick out further than the temple. A third possibility is to just make the mask wider at the cheek regardless, SLIGHTLY reducing the visual range.

'''


def make_full_face_mask():
  ########################################################################
  ########  Code bureaucracy  #######
  ########################################################################
  displayed_objects = {}
  def show_transformed(a,b, invisible = False):
    displayed_objects[b] = (a, invisible)
  
  on_face = False
  #on_face = True
  def finish():
    for name, (object, invisible) in displayed_objects.items():
      if on_face:
        object = (object
        .translated (- forehead_point)
        .as_xz()
        .mirror(vector(), vector(0,1,0))
        .rotated(vector(), vector(1, 0, 0), 360/math.tau*math.atan2(-28,123))
        .translated (vector (0, 18, 0.25)))
      show (object, name, invisible = invisible)
    return on_face
    
  def matrix_from_columns(a,b,c,d=vector()):
    return FreeCAD.Matrix(
      a[0], b[0], c[0], d[0],
      a[1], b[1], c[1], d[1],
      a[2], b[2], c[2], d[2],
    )
  
  ########################################################################
  ########  Constants  #######
  ########################################################################
    
  shield_slot_width = 1.3 # deprecated
  shield_slot_depth = 5 # deprecated
  elastic_slot_catch_length = 2 # deprecated
  elastic_slot_width = 8 # deprecated
  elastic_slot_depth = 5 # deprecated
  shield_glue_face_width = 5
  min_wall_thickness = 1.0
  CPAP_outer_radius = 21.5/2
  CPAP_inner_radius = CPAP_outer_radius - min_wall_thickness
  headband_thickness = 0.6
  headband_width = 16
  headband_cut_radius = 25
  forehead_point = vector (0, -58)
  headphones_front = forehead_point[1] - 75
  shield_back = headphones_front + min_wall_thickness
  back_edge = forehead_point[1] - 96
  
  
  ########################################################################
  ########  Generalized cone definitions  #######
  ########################################################################
  '''
  
  formulas:
  if we represent the surface as a function of z, u (z position and ellipse parameter in radians)
  
  then
  oval_size_factor = (shield_focal_z - z) / shield_focal_z = 1.0 - z / shield_focal_z
  y = top_major_radius*oval_size_factor*(sin(u)-1.0) + z/shield_focal_ratio
  x = top_minor_radius*oval_size_factor*cos(u)
  
  dy/du = top_major_radius*oval_size_factor*cos(u)
  dy/dz = top_major_radius*(sin(u)-1.0)*(-1.0 / shield_focal_z) + 1.0/shield_focal_ratio
  dx/du = top_minor_radius*oval_size_factor*-sin(u)
  dx/dz = top_minor_radius*cos(u)*(-1.0 / shield_focal_z)
  dz/du = 0
  dz/dz = 1
  
  solve for u given x:
  x = top_minor_radius*oval_size_factor*cos(u)
  x / (top_minor_radius*oval_size_factor) = cos(u)
  u = acos(x / (top_minor_radius*oval_size_factor))
  
  solve for u given y:
  y = top_major_radius*oval_size_factor*(sin(u)-1.0) + z/shield_focal_ratio
  (y - z/shield_focal_ratio + top_major_radius*oval_size_factor) = top_major_radius*oval_size_factor*sin(u)
  (y - z/shield_focal_ratio + top_major_radius*oval_size_factor)/top_major_radius*oval_size_factor = sin(u)
  (y - z/shield_focal_ratio)/top_major_radius*oval_size_factor + 1.0 = sin(u)
  u = asin((y - z/shield_focal_ratio)/top_major_radius*oval_size_factor + 1.0)
  '''
  
  top_minor_radius = 95
  top_major_radius = -back_edge*2
  shield_focal_z = 300
  shield_focal_ratio = 2
  shield_focal_point = vector (0, shield_focal_z / shield_focal_ratio, shield_focal_z)

  class ShieldSurfacePoint:
    def __init__(self, z = None, x = None, y = None, parameter = None):
      self.oval_size_factor = 1.0 - z / shield_focal_z
      self.minor_radius = top_minor_radius*self.oval_size_factor
      self.major_radius = top_major_radius*self.oval_size_factor
      self.z = z
      if parameter is not None:
        u = parameter
        self.u = u
        self.parameter = u
        self.x = self.minor_radius*math.cos (self.parameter)
        self.y = self.major_radius*(math.sin (self.parameter)-1.0) + z/shield_focal_ratio
      elif x is not None:
        self.x = x
        u = math.acos(x / self.minor_radius)
        self.u = u
        self.parameter = u
        self.y = self.major_radius*(math.sin (self.parameter)-1.0) + z/shield_focal_ratio
        recalculated_x = self.minor_radius*math.cos (self.parameter)
        assert (abs (recalculated_x - self.x) <0.01)
      else:
        self.y = y
        u = math.asin((y - z/shield_focal_ratio)/self.major_radius + 1.0)
        self.u = u
        self.parameter = u
        self.x = self.minor_radius*math.cos (self.parameter)
        recalculated_y = self.major_radius*(math.sin (self.parameter)-1.0) + z/shield_focal_ratio
        assert (abs (recalculated_y - self.y) <0.01)
      self.position = vector (self.x, self.y, self.z)
      self.ddz = vector (
        top_minor_radius*math.cos(u)*(-1.0 / shield_focal_z),
        top_major_radius*(math.sin (self.parameter)-1.0)*(-1.0 / shield_focal_z) + 1.0/shield_focal_ratio,
        1
      )
      self.ddu = vector (
        self.minor_radius*-math.sin(u),
        self.major_radius*math.cos(u),
        0,
      )
      #self.horizontal_tangent = self.ddu.normalized()
      #self.vertical_tangent = self.ddz.normalized()
      self.normal = self.ddu.cross(self.ddz).normalized()
  
  
  
  ########################################################################
  ########  Forehead/headband/top rim  #######
  ########################################################################
  
  
  
  forehead_points = [
    vector (0, 0),
    vector (15, 0),
    vector (25, -2.5),
    vector (35, -7),
    vector (45, -14),
    vector (55, -27),
    vector (62, -37),
    vector (71, -53),
    vector (79, -90),
    vector (81, -107),
    vector (81, -130),
    vector (60, -180),
    vector (15, -195),
    vector (0, -195),
  ]
  degree = 3
  forehead_poles = [forehead_point + vector (-a[0], a[1]) for a in reversed(forehead_points[1:])] + [forehead_point + a for a in forehead_points[:-1]]
  forehead_curve = Part.BSplineCurve()
  forehead_curve.buildFromPolesMultsKnots(
    forehead_poles,
    degree = degree,
    periodic = True,
  )
  show_transformed (forehead_curve.toShape(), "forehead_curve")
  
  
  headband_cut_box = box(centered (50), bounds (-500, forehead_point[1]-100), centered(500))
  headband_interior_2D = forehead_curve.toShape().to_wire().to_face()
  show_transformed (headband_interior_2D , "headband_interior_2D", invisible=True)
  headband_2D = forehead_curve.toShape().makeOffset2D (headband_thickness, fill = True).cut(headband_cut_box)
  
  headband = headband_2D.extrude (vector (0, 0, headband_width))
  
  # using a weird shaped way to attach the elastic for now, just for FDM convenience
  headband_elastic_link_radius = 3
  headband_elastic_link = Part.Circle(vector(), vector(0,0,1), headband_elastic_link_radius + headband_thickness).toShape().to_wire().to_face().cut(Part.Circle(vector(), vector(0,0,1), headband_elastic_link_radius).toShape().to_wire().to_face()).translated(vector(-25 - (headband_elastic_link_radius + headband_thickness/2), forehead_point[1]-192, 0)).cut(headband_interior_2D).extrude(vector (0, 0, headband_width))
  headband = headband.fuse([
    headband_elastic_link,
    headband_elastic_link.mirror(vector(), vector(1,0,0)),
  ]).translated(vector(0,0,shield_glue_face_width + min_wall_thickness - headband_width))
  show_transformed (headband, "headband")
  
  
  top_rim_subdivisions = 10
  min_parameter = ShieldSurfacePoint(z=0, x=0).parameter
  max_parameter = ShieldSurfacePoint(z=0, y=shield_back).parameter
  top_rim_hoops = []
  for index in range (top_rim_subdivisions):
    parameter = min_parameter + (max_parameter-min_parameter)*index/(top_rim_subdivisions-1)
    bottom_point = ShieldSurfacePoint(z=0, parameter=parameter)
    #top_point = ShieldSurfacePoint(z=shield_glue_face_width + min_wall_thickness, parameter=parameter)
    towards_focus = (shield_focal_point - bottom_point.position).normalized()
    towards_focus_skewed = towards_focus/towards_focus[2]
    wall_thickness_skewed = min_wall_thickness/towards_focus.cross(bottom_point.normal).Length
    flat_outwards = (bottom_point.normal - vector(0,0,bottom_point.normal[2])).normalized()
    coords = [
      (0, 0),
      (0, shield_glue_face_width),
      (wall_thickness_skewed, shield_glue_face_width),
      (wall_thickness_skewed, shield_glue_face_width + min_wall_thickness),
      (-wall_thickness_skewed, shield_glue_face_width + min_wall_thickness),
      (-wall_thickness_skewed, 0),
    ]
    points = [bottom_point.position + towards_focus_skewed*b + flat_outwards*a for a,b in coords]
    wire = Part.Shape ([Part.LineSegment (*pair) for pair in zip (points, points [1:] + [points [0]])]).to_wire()
    top_rim_hoops.append (wire)
    
  
  top_rim = Part.makeLoft ([wire.mirror (vector(), vector (1, 0, 0)) for wire in reversed (top_rim_hoops[1:])] + top_rim_hoops, True)
  show_transformed (top_rim, "top_rim")
  
  
  ########################################################################
  ########  Side rim  #######
  ########################################################################
  
  source_side_points = [
    ShieldSurfacePoint (z=shield_slot_depth, y= shield_back),
    ShieldSurfacePoint (z=0, y= shield_back),
    ShieldSurfacePoint (z= -20, y= shield_back),
    ShieldSurfacePoint (z= -40, y= shield_back),
    ShieldSurfacePoint (z= -60, y= shield_back),
    ShieldSurfacePoint (z= -80, y= shield_back),
    ShieldSurfacePoint (z= -100, y= forehead_point[1] - 60),
    ShieldSurfacePoint (z= -135, x = 54),
    ShieldSurfacePoint (z= -155, x = 25),
    ShieldSurfacePoint (z= -155, x = 0),
  ]
  
  degree = 3
  source_side_poles = [a.position for a in source_side_points]
  source_side_curve = Part.BSplineCurve()
  source_side_curve.buildFromPolesMultsKnots(
    source_side_poles,
    mults = [degree+1] + [1]*(len(source_side_poles) - degree - 1) + [degree+1],
    degree = degree,
  )


  show_transformed (source_side_curve.toShape(), "source_side_curve", invisible=True)
  
  subdivisions = 100
  source_side_curve_length = source_side_curve.length()
  def refined_side_point (distance):
    parameter = source_side_curve.parameterAtDistance (distance)
    
    intermediate = source_side_curve.value (parameter)
    #print (f" parameter: {parameter}, distance: {distance}, intermediate: {intermediate}")
    y_based = ShieldSurfacePoint (z= intermediate [2], y= intermediate [1])
   
    x_frac = (intermediate[1] - -140)/60
    if x_frac < 0:
      return ShieldSurfacePoint (z= intermediate [2], y= intermediate [1])
    elif x_frac > 1:
      return ShieldSurfacePoint (z= intermediate [2], x= intermediate [0])
    else:
      x_based = ShieldSurfacePoint (z= intermediate [2], x= intermediate [0])
      y_based = ShieldSurfacePoint (z= intermediate [2], y= intermediate [1])
      intermediate = x_based.position*x_frac + y_based.position*(1-x_frac)
      return ShieldSurfacePoint (z= intermediate [2], x= intermediate [0])
  
  side_points = [
    refined_side_point (source_side_curve_length * index / (subdivisions -1))
    for index in range (subdivisions)
  ]
  side_points = side_points + [ShieldSurfacePoint (z= point.z, x= -point.x) for point in reversed(side_points[:-1])]
  
  degree = 3
  side_poles = [a.position for a in side_points]
  side_curve = Part.BSplineCurve()
  side_curve.buildFromPolesMultsKnots(
    side_poles,
    mults = [degree+1] + [1]*(len(side_poles) - degree - 1) + [degree+1],
    degree = degree,
  )
  
  show_transformed (side_curve.toShape(), "side_curve")
  
  
  
  side_rim_hoop_wire = FreeCAD_shape_builder().build ([
        start_at(0, 0),
        vertical_to (shield_glue_face_width),
        horizontal_to (-min_wall_thickness),
        vertical_to (-min_wall_thickness),
        horizontal_to (min_wall_thickness),
        vertical_to (0),
        close()
      ]).to_wire()
  
  side_rim_hoops = []
  for index, point in enumerate (side_points):
    position = point.position
    parameter = side_curve.parameter (position)
    tangent = vector (*side_curve.tangent (parameter)).normalized()
    normal = point.normal
    away = tangent.cross (normal)
    
    shield_slot_matrix = matrix_from_columns(normal, -away, tangent, position)
    shield_shape = side_rim_hoop_wire.copy()
    shield_shape.transformShape (shield_slot_matrix)
    side_rim_hoops.append(shield_shape)
    #show_transformed (shape,f"side_strut_shape_{index}")
  
  side_rim = Part.makeLoft (side_rim_hoops, True)
  show_transformed (side_rim, "side_rim")

  return finish()

  forehead_exclusion = forehead_curve.toShape().to_wire().to_face().fancy_extrude (vector (0, 0, 1), bounds (-5, 50))
  
  #forehead_elastic_hole = Part.makeCylinder (3, 50, vector (-86.4, -161, -4))
  forehead_elastic_hole = box (centered (1), 5, centered (100)).makeOffsetShape (1.5, 0.01).rotated (vector(), vector (0, 0, 1), -10).translated (vector (-85.4, -162, -4))
  forehead_exclusion = forehead_exclusion.fuse ([
    forehead_elastic_hole,
    forehead_elastic_hole.mirror (vector(), vector (1, 0, 0)),
  ])
  
  
  shield_top_full_wire = Part.Ellipse(vector(0,0), vector (top_minor_radius, -top_major_radius), vector(0, -top_major_radius)).toShape().to_wire()
  lenient_box = box(centered (500), bounds (back_edge-50, 500), bounds(-180, 20))
  shield_box = box(centered (500), bounds (back_edge, 500), bounds (-180, shield_slot_depth))
  shield_top_curve = shield_top_full_wire.common(shield_box)
  #show_transformed(shield_box, "shield_box")
  
  show_transformed(shield_top_curve, "shield_top_curve")
  
  
  
  
  shield_slot_top = min_wall_thickness + shield_slot_depth
  elastic_slot_bottom = shield_slot_top - elastic_slot_width - min_wall_thickness*2
  side_shield_slot_shape = FreeCAD_shape_builder().build ([
        start_at(-shield_slot_width- min_wall_thickness, 0),
        diagonal_to (0, elastic_slot_bottom),
        horizontal_to (elastic_slot_depth + elastic_slot_catch_length + min_wall_thickness*2),
        vertical_to (elastic_slot_bottom+ min_wall_thickness),
        diagonal_to (elastic_slot_depth + min_wall_thickness*2, elastic_slot_bottom+ elastic_slot_catch_length + min_wall_thickness),
        horizontal_to (elastic_slot_depth + min_wall_thickness),
        vertical_to (elastic_slot_bottom+ min_wall_thickness),
        horizontal_to (min_wall_thickness),
        vertical_to (shield_slot_top - min_wall_thickness),
        horizontal_to (elastic_slot_depth + min_wall_thickness),
        vertical_to (shield_slot_top - min_wall_thickness - elastic_slot_catch_length),
        horizontal_to (elastic_slot_depth + min_wall_thickness*2),
        diagonal_to (elastic_slot_depth + min_wall_thickness*2 + elastic_slot_catch_length, shield_slot_top - min_wall_thickness),
        vertical_to (shield_slot_top),
        horizontal_to (0),
        vertical_to (min_wall_thickness),
        horizontal_to (-shield_slot_width),
        vertical_to (min_wall_thickness + shield_slot_depth),
        horizontal_to (-shield_slot_width- min_wall_thickness),
        close()
      ]).to_wire() #.to_face()
  
  '''elastic_slot_shape = FreeCAD_shape_builder().build ([
        start_at(0, 0),
        horizontal_to (min_wall_thickness+elastic_slot_depth),
        vertical_to (min_wall_thickness),
        horizontal_to (min_wall_thickness),
        vertical_to (elastic_slot_width + min_wall_thickness),
        horizontal_to (min_wall_thickness+elastic_slot_depth),
        vertical_to (elastic_slot_width + min_wall_thickness*2),
        horizontal_to (0),
        close()
      ]).to_wire()'''
      
  
  
  side_shield_slot_pieces = []
  intake_flat_outside_edge = []
  intake_flat_inside_edge = []
  #side_elastic_slot_pieces = []
  for index, point in enumerate (side_points):
    position = point.position
    parameter = side_curve.parameter (position)
    tangent = vector (*side_curve.tangent (parameter)).normalized()
    normal = point.normal
    away = tangent.cross (normal)
    
    shield_slot_matrix = matrix_from_columns(normal, -away, tangent, position)
    shield_shape = side_shield_slot_shape.copy()
    shield_shape.transformShape (shield_slot_matrix)
    side_shield_slot_pieces.append(shield_shape)
    #show_transformed (shape,f"side_strut_shape_{index}")
    
    '''curve_normal = vector (*side_curve.normal(parameter))
    elastic_slot_matrix = matrix_from_columns(-curve_normal, -curve_normal.cross(tangent), tangent, position)
    elastic_shape = elastic_slot_shape.copy()
    elastic_shape.transformShape (elastic_slot_matrix)
    side_elastic_slot_pieces.append(elastic_shape)'''
    
    if position [0] <0 and position [2] >= -100 and position [2] <= -60:
      intake_flat_outside_edge.append (position - normal*(shield_slot_width + min_wall_thickness*1.6))
      intake_flat_inside_edge.append (position - normal*(shield_slot_width + min_wall_thickness*1.6 + 7))
  intake_flat_inside_edge.reverse()
  
  side_shield_slot = Part.makeLoft (side_shield_slot_pieces, True)
  show_transformed (side_shield_slot,f"side_shield_slot")
  
  #side_elastic_slot = Part.makeLoft (side_elastic_slot_pieces, True)
  #show_transformed (side_elastic_slot,f"side_elastic_slot")
  
  
  shield_extension_zs = [-180, 20]
  def shield_extension_curve (z):
    offset_fraction = z / shield_focal_point[2]
    return shield_top_full_wire.scaled (1.0 - offset_fraction).translated (shield_focal_point*offset_fraction)
  shield_extension_curves = [shield_extension_curve (z) for z in shield_extension_zs]
  
  shield_cross_section = shield_top_full_wire.to_face().common(shield_box)
  shield_cross_sections = []
  for offset_distance in (20.0*x for x in range(10)):
    offset_fraction = offset_distance / -shield_focal_point[2]
    shield_cross_sections.append(shield_cross_section.scaled (1.0 - offset_fraction).translated (shield_focal_point*offset_fraction))
    
  show_transformed (Part.Compound (shield_cross_sections), "shield_cross_sections")
  
  #show_transformed(shield_extension_curves[0], "shield_extension_curve_0")
  #show_transformed(shield_extension_curves[1], "shield_extension_curve_1")
  
  shield_outer_surface = Part.makeRuledSurface(*shield_extension_curves).common(lenient_box)
  
  frame_space = shield_outer_surface.makeOffsetShape (-min_wall_thickness, 0.01).common (lenient_box).extrude(vector(0, -200, 0))
  #show_transformed (frame_space, "frame_space")
  
  #show_transformed(shield_outer_surface, "shield_outer_surface")
  
  shield_solid = shield_outer_surface.makeOffsetShape (shield_slot_width, 0.01, fill = True).common (shield_box)
  
  show_transformed(shield_solid, "shield_solid")
  
  visor = box(
    centered (500),
    centered (500),
    bounds (0, shield_slot_depth + min_wall_thickness),
  ).common (lenient_box).common(frame_space).cut (forehead_exclusion).cut(shield_solid)
  
  #forehead_expanded = forehead_curve.toShape().to_wire().makeOffset2D (1).to_face().fancy_extrude (vector (0, 0, 1), bounds (0, 4))
  #show_transformed (forehead_expanded.common (lenient_box).common(frame_space).cut (forehead_exclusion), "forehead_shape")
  
  
  show_transformed (visor, "visor")
  #show_transformed (visor.common(box(centered (30, on = 85), centered (40, on = -160), centered (500))), "visor_fragment")
  #show_transformed (side_shield_slot.common(box(centered (30, on = 85), centered (40, on = -160), centered (40))), "side_shield_slot_fragment")
  
  intake_flat_width = 7
  intake_center = min (
    (side_point for side_point in side_points if side_point.position [0] <0),
    key = lambda side_point: abs (-80 - side_point.position [2])
  )
  intake_direction = intake_center.normal.cross (vector (0, 0, -1)).normalized()
  intake_sideways = vector (*side_curve.tangent (side_curve.parameter (intake_center. position)))
  intake_flat_subdivisions = 10
  intake_flat_height = 40
  def intake_flat_wire (expansion, forwards_offset):
    outside_edge = []
    inside_edge = []
    height = intake_flat_height + expansion*2
    center_source = intake_center.position - intake_direction*forwards_offset
    center = ShieldSurfacePoint (z = center_source [2], y = center_source [1])
    center = ShieldSurfacePoint (z = center_source [2], x = -center.position[0])
    
    for index in range (intake_flat_subdivisions):
      fraction = index/(intake_flat_subdivisions -1)
      offset = (fraction - 0.5)*height/intake_sideways [2]
      source = center.position + intake_sideways*offset
      precise = ShieldSurfacePoint (z = source [2], y = source [1])
      precise = ShieldSurfacePoint (z = precise.position[2], x = -precise.position [0])
      
      # we have to project everything onto the same plane so that the loft can be closed
      def projected (position):
        threeD_offset = position - center.position
        normal_component = center.normal.dot (threeD_offset)
        sideways_component = intake_sideways.dot(threeD_offset)
        result = center.position + center.normal*normal_component + intake_sideways*sideways_component
        #print (f"{result - position}, {normal_component}, {sideways_component}, {center.normal}, {intake_sideways}")
        return result
      
      outside_edge.append (projected (precise.position - precise.normal*(shield_slot_width + min_wall_thickness - expansion)))
      inside_edge.append (projected (precise.position - precise.normal*(shield_slot_width + min_wall_thickness + intake_flat_width + expansion)))
    outside_edge.reverse()
    degree = 3
    poles = outside_edge + inside_edge
    intake_flat_curve = Part.BSplineCurve()
    intake_flat_curve.buildFromPolesMultsKnots(
      poles,
      degree = degree,
      periodic = True,
    )
    return intake_flat_curve.toShape().to_wire()
      
  
  def intake_loft_components (expansion):
    CPAP_wire = Part.Shape ([Part.Circle (intake_center.position + intake_direction*45 - intake_center.normal*(shield_slot_width + min_wall_thickness + intake_flat_width/2) + vector (0, 0, 3), intake_direction, CPAP_inner_radius + expansion)]).to_wire()
    result = []
    if expansion == 0:
      flat_start = -1
    return (
      [intake_flat_wire(expansion, 7-index*2) for index in range (5)]
      + [CPAP_wire.translated (intake_direction*index*4) for index in range (5)])
    
  intake_interior = Part.makeLoft (intake_loft_components (0.0), True)
  intake_exterior = Part.makeLoft (intake_loft_components (min_wall_thickness), True)
  
  show_transformed (intake_interior, "intake_interior")
  show_transformed (intake_exterior, "intake_exterior")
  
  intake_solid = intake_exterior.cut (intake_interior) #intake_surface.makeOffsetShape (min_wall_thickness, 0.01, fill=True)
  
  show_transformed (intake_solid, "intake_solid")
  
  top_splitter = box (bounds (0, 500), centered (500), bounds (0, 500))
  top_splitter2 = box (bounds (-500, 0), centered (500), bounds (0, 500))
  #show_transformed (top_splitter, "top_splitter")
  show_transformed (Part.Compound ([
    visor,
    side_shield_slot.common(top_splitter2),
    #side_shield_slot.common(top_splitter),
    side_shield_slot.common(top_splitter2).mirror(vector(), vector(1,0,0)),
  ]), "augmented_visor")
  
  side_splitter = box (bounds (-500, -56), centered (500), bounds (-500, 0))
  side_splitter_2 = box (bounds (-56, 56), centered (500), centered (500))
  show_transformed (side_shield_slot. common (side_splitter_2), "bottom_slot")
  show_transformed (side_shield_slot.common (side_splitter), "side_slot")
  
  
  
  flat_approximation_increments = 201
  flat_approximation_factor = math.tau/2/(flat_approximation_increments -1)
  previous_surface = None
  flat_approximations = [0]
  for index in range (flat_approximation_increments):
    parameter = index*flat_approximation_factor
    surface = ShieldSurfacePoint(z=shield_slot_depth, parameter = parameter)
    if previous_surface is not None:
      difference = surface.position - previous_surface.position
      average = (surface.position + previous_surface.position)/2
      from_focus = (average - shield_focal_point)
      relevant_difference = difference - from_focus*(difference.dot(from_focus)/from_focus.dot(from_focus))
      angle = math.atan2(relevant_difference.Length, from_focus.Length)
      flat_approximations.append (flat_approximations [-1] + angle)
    previous_surface = surface
  #should print (f"{flat_approximations}")
  def flat_approximate_angle (surface):
    adjusted = surface.parameter/flat_approximation_factor
    #linearly interpolate
    floor = math.floor (adjusted)
    fraction = adjusted - floor
    previous = flat_approximations [floor]
    next = flat_approximations [floor + 1]
    result = next*fraction + previous*(1-fraction)
    #print (f" angles: {surface.parameter}, {adjusted}, floor: {floor}, {fraction}, {previous}, {next}, {result}, ")
    # put 0 in the middle
    return result - flat_approximations [(flat_approximation_increments -1)//2]
  
  front_normal = (vector() - shield_focal_point).normalized()
  back_normal = (vector(0, -top_major_radius*2, 0) - shield_focal_point).normalized()
  radius_per_distance_from_focal_point = (front_normal - back_normal).Length/2
  vertical = -((front_normal + back_normal)/2).normalized()
  horizontal = vector (0, 1, 0).cross (vertical).normalized()
  forwards = vertical.cross (horizontal)
  #print (f" directions: {vertical}, {horizontal}, {forwards}")
  horizontal_shift = 0
  def unrolled(surface):
    offset = surface.position - shield_focal_point
    distance = offset.Length
    #conic_angle = math.atan2(offset.dot(forwards), offset.dot(horizontal))
    #radius = distance * radius_per_distance_from_focal_point
    #reconstructed = shield_focal_point+vertical*offset.dot(vertical) + forwards*radius*math.sin(conic_angle) + horizontal*radius*math.cos(conic_angle)
    #print (f"original: {surface.position}, reconstructed: {reconstructed}")
    #wrong: conic_angle = surface.parameter
    #print (f" angles: {conic_angle}, {surface.parameter}")
    paper_radians = flat_approximate_angle (surface) #(conic_angle - math.tau/4)*radius_per_distance_from_focal_point
    result = vector (distance*math.cos(paper_radians) + horizontal_shift, distance*math.sin (paper_radians))
    return (surface, result)
  def segments (vertices):
    result = []
    for (a,b), (c,d) in zip (vertices [: -1], vertices [1:]):
      original = (a.position - c.position).Length
      derived = (b - d).Length
      ratio = derived/original
      
      print (f"distances: {original}, {derived}, {derived/original}")
      assert (abs (1 - ratio) <=0.01)
      result.append(Part.LineSegment (b, d))
    print (f"total length: {sum( segment.length() for segment in result)}")
    return result
  
  horizontal_shift = 26 - unrolled(ShieldSurfacePoint(z=shield_slot_depth, y=0))[1][0]
  
  unrolled_side = [unrolled (surface) for surface in side_points
    if surface.position [0] >= 0
    ]
  unrolled_top_subdivisions = 40
  unrolled_top_back = ShieldSurfacePoint(z=shield_slot_depth, y= back_edge)
  unrolled_top_parameter_range = unrolled_top_back.parameter - math.tau/4
  unrolled_top = [
    unrolled (
      ShieldSurfacePoint(z=shield_slot_depth, parameter = math.tau/4 + index*unrolled_top_parameter_range/(unrolled_top_subdivisions - 1))
    ) for index in range (unrolled_top_subdivisions)]
  
  unrolled = Part.Shape(
    segments (unrolled_top) + segments (unrolled_side) + [Part.LineSegment (unrolled_side[-1][1], unrolled_top[0][1])]
  )
  
  show_transformed (unrolled, "unrolled")
  
    
  
  return finish()

def run(g):
  for key, value in g.items():
    globals()[key] = value
  return make_full_face_mask()
  
  
  