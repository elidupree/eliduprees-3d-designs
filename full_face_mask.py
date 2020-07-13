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



Additional notes after mostly completing second prototype:
– the intake applies significant torque to the face shield, twisting the clear plastic. Right now, the frame around the intake is very bendable; below the intake, this is a good thing to help the mask's "one-size-fits-all"-ness, but above the intake, it's flexing in the wrong direction. This doesn't seem to be a huge problem, but should still be avoided if possible.
– Despite being much more "one-size-fits-all", it didn't fit someone with glasses. I'll probably have to change the generalized cone shape.
– Right where the top rim meets the headband, it's very easy for the headband to bend the top rim inwards, making it slightly concave. I'm not sure if this is a problem in practice, but theoretically it bends the face shield in an undesired direction and worsens the seal with the forehead cloth.

'''


import os.path
import os
import Drawing


def make_full_face_mask():
  ########################################################################
  ########  Code bureaucracy  #######
  ########################################################################
  
  on_face = False
  #on_face = True
  pieces_invisible = False
  #pieces_invisible = True
  invisible_default = not pieces_invisible
  #invisible_default = True
  
  displayed_objects = {}
  def show_transformed(a,b, invisible = invisible_default):
    displayed_objects[b] = (a, invisible)
  
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
    
  def matrix_from_columns(a=vector(1,0,0),b=vector(0,1,0),c=vector(0,0,1),d=vector()):
    return FreeCAD.Matrix(
      a[0], b[0], c[0], d[0],
      a[1], b[1], c[1], d[1],
      a[2], b[2], c[2], d[2],
    )
  
  def fuse(shapes):
    return shapes[0].fuse(shapes[1:])
  
  def polygon(points):
    return Part.makePolygon(points + [points[0]])
  
  
  ########################################################################
  ########  Constants  #######
  ########################################################################
    
  min_wall_thickness = 0.6
  stiffer_wall_thickness = 1.1
  shield_glue_face_width = 5
  elastic_holder_depth = 10
  CPAP_outer_radius = 21.5/2
  CPAP_inner_radius = CPAP_outer_radius - min_wall_thickness
  CPAP_hose_helix_outer_radius = 22/2
  headband_thickness = min_wall_thickness
  headband_width = 12
  headband_cut_radius = 25
  forehead_point = vector (0, -58)
  headphones_front = forehead_point[1] - 75
  side_plate_width = max(min_wall_thickness + shield_glue_face_width, elastic_holder_depth)
  shield_back = headphones_front + side_plate_width - shield_glue_face_width
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
  
  top_minor_radius = 93
  top_major_radius = -back_edge*2
  shield_focal_z = 280
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
        self.ellipse_parameter = u
        self.x = self.minor_radius*math.cos (u)
        self.y = self.major_radius*(math.sin (u)-1.0) + z/shield_focal_ratio
      elif x is not None:
        self.x = x
        u = math.acos(x / self.minor_radius)
        self.ellipse_parameter = u
        self.y = self.major_radius*(math.sin (u)-1.0) + z/shield_focal_ratio
        recalculated_x = self.minor_radius*math.cos (u)
        assert (abs (recalculated_x - self.x) <0.01)
      else:
        self.y = y
        u = math.asin((y - z/shield_focal_ratio)/self.major_radius + 1.0)
        self.ellipse_parameter = u
        self.x = self.minor_radius*math.cos (u)
        recalculated_y = self.major_radius*(math.sin (u)-1.0) + z/shield_focal_ratio
        assert (abs (recalculated_y - self.y) <0.01)
      self.position = vector (self.x, self.y, self.z)
      self.ddz = vector (
        top_minor_radius*math.cos(u)*(-1.0 / shield_focal_z),
        top_major_radius*(math.sin (u)-1.0)*(-1.0 / shield_focal_z) + 1.0/shield_focal_ratio,
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
  
  
  
  
  shield_top_full_wire = Part.Ellipse(vector(0,0), vector (top_minor_radius, -top_major_radius), vector(0, -top_major_radius)).toShape().to_wire()
  shield_box = box(centered (500), bounds (shield_back, 500), bounds (-180, 0))
  shield_cross_section = shield_top_full_wire.to_face()
  shield_cross_sections = []
  for offset_distance in (20.0*x for x in range(10)):
    offset_fraction = offset_distance / -shield_focal_point[2]
    shield_cross_sections.append(shield_cross_section.scaled (1.0 - offset_fraction).translated (shield_focal_point*offset_fraction).common(shield_box))
    
  show_transformed (Part.Compound (shield_cross_sections), "shield_cross_sections", invisible=True)
  

  
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
  show_transformed (forehead_curve.toShape(), "forehead_curve", invisible=True)
  print(f"Forehead circumference: {forehead_curve.length()}")
  
  headband_cut_box = box(centered (50), bounds (-500, forehead_point[1]-100), centered(500))
  headband_interior_2D = forehead_curve.toShape().to_wire().to_face()
  show_transformed (headband_interior_2D , "headband_interior_2D", invisible=True)
  headband_2D = forehead_curve.toShape().makeOffset2D (headband_thickness, fill = True).cut(headband_cut_box)
  
  headband = headband_2D.extrude (vector (0, 0, headband_width))
  
  # using a weird shaped way to attach the elastic for now, just for FDM convenience
  elastic_link_radius = 3
  elastic_link = Part.Circle(vector(), vector(0,0,1), elastic_link_radius + headband_thickness).toShape().to_wire().to_face().cut(Part.Circle(vector(), vector(0,0,1), elastic_link_radius).toShape().to_wire().to_face())
  
  headband_elastic_link = elastic_link.translated(vector(-25 - (elastic_link_radius + headband_thickness/2), forehead_point[1]-192, 0)).cut(headband_interior_2D).extrude(vector (0, 0, headband_width))
  headband = headband.fuse([
    headband_elastic_link,
    headband_elastic_link.mirror(vector(), vector(1,0,0)),
  ]).translated(vector(0,0,shield_glue_face_width + min_wall_thickness - headband_width))
  show_transformed (headband, "headband")
  
  CPAP_grabber = (
    Part.Circle(vector(), vector(0,0,1), CPAP_hose_helix_outer_radius + min_wall_thickness).toShape().to_wire().to_face()
    .cut(Part.Circle(vector(), vector(0,0,1), CPAP_hose_helix_outer_radius).toShape().to_wire().to_face())
    .cut(FreeCAD_shape_builder().build ([
        start_at(0, 0),
        diagonal_to(-50, -100),
        horizontal_to(50),
        close()
      ]).to_wire().to_face())
    .fuse(elastic_link.translated(vector(CPAP_hose_helix_outer_radius + min_wall_thickness + elastic_link_radius, 0, 0)))
    .extrude(vector (0, 0, headband_width))
  )
  show_transformed (CPAP_grabber, "CPAP_grabber")
  
  
  
  top_rim_subdivisions = 10
  min_parameter = ShieldSurfacePoint(z=0, x=0).ellipse_parameter
  max_parameter = ShieldSurfacePoint(z=0, y=shield_back).ellipse_parameter
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
  ########  Side curve definition  #######
  ########################################################################
  
  source_side_points = [
    ShieldSurfacePoint (z=shield_glue_face_width, y= shield_back),
    ShieldSurfacePoint (z=0, y= shield_back),
    ShieldSurfacePoint (z= -20, y= shield_back),
    ShieldSurfacePoint (z= -40, y= shield_back),
    ShieldSurfacePoint (z= -60, y= shield_back),
    ShieldSurfacePoint (z= -80, y= shield_back+3),
    ShieldSurfacePoint (z= -100, y= forehead_point[1] - 63),
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
  
  subdivisions = 40
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
  side_curve_length = side_curve.length()
  
  show_transformed (side_curve.toShape(), "side_curve")
  
  class SideCurvePoint(ShieldSurfacePoint):
    def __init__(self, z = None, x = None, y = None, which = 0, parameter = None, distance = None):
      if distance is not None:
        self.side_curve_distance = distance
        self.side_curve_parameter = side_curve.parameterAtDistance (distance)
        source_position = side_curve.value (self.side_curve_parameter)
      elif parameter is not None:
        self.side_curve_parameter = parameter
        self.side_curve_distance = side_curve.length(0, self.side_curve_parameter)
        source_position = side_curve.value (self.side_curve_parameter)
      elif z is not None:
        source_position = vector(side_curve.intersect(
          Part.Plane (vector(0,0,z), vector(0,0,1))
        )[0][which])
        self.side_curve_parameter = side_curve.parameter (source_position)
        self.side_curve_distance = side_curve.length(0, self.side_curve_parameter)
      else:
        assert(false)
        
      self.side_curve_tangent = vector (*side_curve.tangent (self.side_curve_parameter))
      
      super().__init__(z=source_position [2], x=source_position [0])
      
      self.away = self.side_curve_tangent.cross (self.normal)
          
      self.moving_frame = matrix_from_columns(self.normal, -self.away, self.side_curve_tangent, self.position)
  
  def side_curve_at_z(z, which = 0):
    print("side_curve_at_z is deprecated")
    return vector(side_curve.intersect(
      Part.Plane (vector(0,0,z), vector(0,0,1))
    )[0][which])
  
  def side_curve_points(num, start_distance = 0, end_distance = side_curve_length):
    def point(index):
      fraction = index / (num-1)
      distance = start_distance*(1-fraction) + end_distance*fraction
      return SideCurvePoint(distance = distance)
    return (point(index) for index in range (num))
  
  ########################################################################
  ########  Side rim and stuff #######
  ########################################################################
  
  side_plate_bottom_z = -82
  elastic_catch_slope = 8
  
  side_plate_top = vector(forehead_curve.intersect(Part.LineSegment(
    vector(0, headphones_front), vector(500, headphones_front)
  ))[0])
  side_plate_bottom = ShieldSurfacePoint (z= side_plate_bottom_z, y= headphones_front).position
  side_plate_top_frontish = vector(forehead_curve.intersect(Part.LineSegment(
    vector(0, side_plate_top[1] + side_plate_width), vector(500, side_plate_top[1] + side_plate_width)
  ))[0])
  side_plate_bottom_frontish = ShieldSurfacePoint (z=side_plate_bottom.z, y= side_plate_bottom.y + side_plate_width).position
  side_plate_forwards = (side_plate_top_frontish - side_plate_top).normalized()
  side_plate_z_vector = side_plate_bottom_frontish - vector (min_wall_thickness, 0, 0) - side_plate_top_frontish
  side_plate_normal = side_plate_z_vector.cross (side_plate_forwards).normalized()
  def project_to_side_plate (input):
    return input - side_plate_normal*side_plate_normal.dot(input - side_plate_top)
  
  side_rim_hoop_wire = FreeCAD_shape_builder().build ([
        start_at(0, 0),
        vertical_to (shield_glue_face_width),
        horizontal_to (-min_wall_thickness),
        vertical_to (-min_wall_thickness),
        horizontal_to (min_wall_thickness),
        vertical_to (0),
        close()
      ]).to_wire()
  elastic_tension_wire = FreeCAD_shape_builder().build ([
        start_at(0, 0),
        horizontal_to (shield_glue_face_width),
      ]).to_wire()
  
  side_rim_hoops = []
  side_plate_hoops = []
  elastic_holder_hoops = []
  elastic_tension_hoops = []
  side_splitter = None
  for point in side_curve_points(79):
    position = point.position
    
    shield_shape = side_rim_hoop_wire.copy()
    shield_shape.transformShape (point.moving_frame)
    side_rim_hoops.append(shield_shape)
    #show_transformed (shape,f"side_strut_shape_{index}")
    
    # for historical reasons, defined as "first point that meets the condition" rather than a specific z; we're leaving it that way for now for backwards compatibility with already-printed parts, but it can be fixed in a future version. When fixing it, consider the issue about the splitter shape no longer lining up with the edge of the elastic holder plate
    if position [2] < side_plate_bottom_z - 4:
      if side_splitter is None:
        side_splitter = box(centered(500), centered(500), 500).transformGeometry(point.moving_frame)
    
    if position [2] >= side_plate_bottom_z and position [0] > 0:
      skew_away = -point.away/point.away[1]
      excess_forwards = position[1] - headphones_front
      back = position + skew_away * excess_forwards
      front = back - skew_away * side_plate_width
      points = [
        back,
        front,
        project_to_side_plate (front),
        project_to_side_plate (back),
      ]
      wire = Part.Shape ([Part.LineSegment (*pair) for pair in zip (points, points [1:] + [points [0]])]).to_wire()
      side_plate_hoops.append(wire)
      
    curve_normal = vector (*side_curve.normal(point.side_curve_parameter))
    elastic_tension_matrix = matrix_from_columns(-curve_normal, -curve_normal.cross(point.side_curve_tangent), point.side_curve_tangent, position)
    elastic_tension_shape = elastic_tension_wire.copy()
    elastic_tension_shape.transformShape (elastic_tension_matrix)
    elastic_tension_hoops.append(elastic_tension_shape)
    
  middle_distance = side_curve.length(0, 0.5)
  distances = (SideCurvePoint(z=-87, which=0).side_curve_distance, SideCurvePoint(z=-87, which=1).side_curve_distance)
  for point in side_curve_points(79, distances[0], distances[1]):
    position = point.position
    sine_curve = math.cos((point.side_curve_distance-middle_distance) / (distances[1]-distances[0]) * math.tau * 7.8)
    elastic_holder_hoop_wire = FreeCAD_shape_builder().build ([
        start_at(-min_wall_thickness, 0),
        vertical_to (-min_wall_thickness),
        horizontal_to (elastic_holder_depth * 0.5*(1.01+sine_curve)),
        vertical_to (0),
        close()
    ]).to_wire()
    elastic_holder_hoop_wire.transformShape (point.moving_frame)
    elastic_holder_hoops.append(elastic_holder_hoop_wire)
  
  side_rim = Part.makeLoft (side_rim_hoops, True)
  show_transformed (side_rim, "side_rim")
  side_elastic_holder = Part.makeLoft (elastic_holder_hoops, True)
  side_plate = Part.makeLoft (side_plate_hoops, True)
  show_transformed (side_plate, "side_plate")
  
  show_transformed (Part.Compound(elastic_tension_hoops), "elastic_tension")
  
  def elastic_plate_segment (num, start_distance, end_distance, thickness = min_wall_thickness):
    hoops = []
    for point in side_curve_points(num, start_distance, end_distance):
      fraction = (point.side_curve_distance - start_distance)/(end_distance - start_distance)
      offset = point.away*(min_wall_thickness + elastic_holder_depth) + point.side_curve_tangent*((fraction*2 - 1)*elastic_holder_depth/elastic_catch_slope)
      inside = point.position - point.normal*min_wall_thickness
      hoops.append(polygon ([
        inside,
        inside+ point.normal*thickness,
        inside+ point.normal*thickness + offset,
        inside+ offset,
      ]))
    return Part.makeLoft (hoops, True)
  
  side_elastic_holders = [
    side_elastic_holder,
    elastic_plate_segment (
      30,
      SideCurvePoint(z=-88, which=0).side_curve_distance,
      SideCurvePoint(z=-144, which=1).side_curve_distance,
    ),
    elastic_plate_segment (
      5,
      SideCurvePoint(z=-95, which=1).side_curve_distance,
      SideCurvePoint(z=-88, which=1).side_curve_distance,
      min_wall_thickness*2
    ),
  ]
  show_transformed (Part.Compound(side_elastic_holders), "side_elastic_holder")
  
  elastic_hook_base_length = 6
  elastic_hook_outwards = 10
  elastic_hook_forwards = 10
  
  elastic_hook = Part.makePolygon([
    vector(0,0),
    vector(elastic_hook_outwards,elastic_hook_forwards-1.25),
    vector(elastic_hook_outwards,elastic_hook_forwards),
    vector(0,elastic_hook_base_length),
    vector(0,0),
  ]).to_face().extrude(vector(0,0,stiffer_wall_thickness))


  def side_hook(distance):
    
    top = side_curve.value (side_curve.parameterAtDistance (distance))
    bottom = side_curve.value (side_curve.parameterAtDistance (distance+elastic_hook_forwards))
    downwards = (bottom-top).normalized()
    matrix = matrix_from_columns(side_plate_normal, downwards, -side_plate_normal.cross(downwards), top)
    hook = elastic_hook.copy()
    hook.transformShape (matrix)
    return hook

  rim_hook_back = ShieldSurfacePoint (z=shield_glue_face_width+min_wall_thickness, y= headphones_front+15)
  rim_hook_front = ShieldSurfacePoint (z=shield_glue_face_width+min_wall_thickness, y=rim_hook_back.position[1]+elastic_hook_forwards)
  rim_hook_forwards = (rim_hook_front.position - rim_hook_back.position).normalized()
  rim_hook = elastic_hook.copy()
  matrix = matrix_from_columns(rim_hook_forwards.cross (vector(0,0,1)), -rim_hook_forwards, vector(0,0,-1), rim_hook_front.position)
  rim_hook.transformShape (matrix)
  side_hooks = Part.Compound ([rim_hook]+[
    side_hook(elastic_hook_base_length*index) for index in range(8)
  ])
  
  show_transformed (side_hooks, "side_hooks")
    
  
  ########################################################################
  ########  Intake  #######
  ########################################################################
  
  intake_flat_thickness_base = 9
  intake_flat_width = 42
  intake_flat_subdivisions = 10
  
  
  intake_center = side_curve_at_z(-123, 1)
  intake_center_parameter = side_curve.parameter (intake_center)
  intake_center_distance = side_curve.length (0, intake_center_parameter)
  intake_center_on_shield = ShieldSurfacePoint (z = intake_center[2], y = intake_center[1])
  intake_center_on_shield = ShieldSurfacePoint (z = intake_center_on_shield.position[2], x = -intake_center_on_shield.position [0])
  intake_center_tangent = tangent = vector (*side_curve.tangent (intake_center_parameter)).normalized()
  intake_center_away = intake_center_tangent.cross (intake_center_on_shield.normal)
  intake_skew_factor = 0.8
  intake_forwards = ((- intake_center_away) - intake_center_tangent*intake_skew_factor).normalized()
  
  
  class IntakeSurface:
    def __init__(self, outside):
      self.outside = outside
      self.expansion = min_wall_thickness if outside else 0
      self.degree = 3
      self.num_points = intake_flat_subdivisions*2
      if outside:
        self.num_points += (self.degree - 1)*2
      
      flat_hoops_length = shield_glue_face_width + min_wall_thickness + elastic_holder_depth
      self.hoops = [self.flat_hoop (shield_glue_face_width-flat_hoops_length*index/4) for index in range (5)] + [self.CPAP_hoop (index*4) for index in range (5)]
      self.ends = [
        self.wire (self.hoops[0]),
        self.wire (self.hoops[-1])
      ]
      self.surface = Part.BSplineSurface()
      self.surface.buildFromPolesMultsKnots(self.hoops,
        [self.degree+1] + [1]*(len(self.hoops) - self.degree - 1) + [self.degree+1],
        [1]*(len (self.hoops[0]) + 1),
        udegree = self.degree,
        vdegree = self.degree,
        vperiodic=True,
      )
      
    def wire(self, hoop):
      curve = Part.BSplineCurve()
      curve.buildFromPolesMultsKnots(
        hoop,
        degree = self.degree,
        periodic = True,
      )
      return curve.toShape().to_wire()
       
    def CPAP_hoop (self, offset):
      center = intake_center - intake_forwards*45 - intake_center_on_shield.normal*(min_wall_thickness + intake_flat_thickness_base/2) - intake_forwards*offset
      direction = -intake_forwards.cross (intake_center_on_shield.normal).normalized()
      other_direction = -direction.cross (intake_forwards)
      def CPAP_point (index):
        angle = index/self.num_points*math.tau
        return center + direction*(CPAP_inner_radius + self.expansion)*math.sin (angle) + other_direction*(CPAP_inner_radius + self.expansion)*math.cos(angle)
      return [CPAP_point (index) for index in range (self.num_points)]

    def flat_hoop(self, forwards_offset):
      rim_edge = self.flat_edge (forwards_offset, True)
      other_edge = self.flat_edge (forwards_offset, False)
      return rim_edge [len(rim_edge)//2:] + other_edge + rim_edge [:len(rim_edge)//2]
    def flat_edge(self, forwards_offset, rim_side):
      edge = []
      backness = shield_glue_face_width - forwards_offset
      height = intake_flat_width + 2*(self.expansion + backness/elastic_catch_slope)
      if self.outside and rim_side:
        height += 8
      for index in range (intake_flat_subdivisions):
        fraction = index/(intake_flat_subdivisions -1)
        offset = (fraction - 0.5)*height# - forwards_offset*intake_skew_factor
        parameter = side_curve.parameterAtDistance (intake_center_distance + offset)
      
        source = side_curve.value(parameter)
        precise = ShieldSurfacePoint (z = source [2], y = source [1])
        precise = ShieldSurfacePoint (z = precise.position[2], x = -precise.position [0])
      
        tangent = vector (*side_curve.tangent (parameter)).normalized()
        normal = precise.normal
        away = tangent.cross (normal)
      
        if rim_side:
          normal_distance = min_wall_thickness - self.expansion
        else:
          thickness = intake_flat_thickness_base*0.5*(1+math.sin(fraction*math.tau/2))
          normal_distance = min_wall_thickness + thickness + self.expansion
      
        edge.append (precise.position - away*forwards_offset - normal*normal_distance)
      if rim_side:
        edge.reverse()
        if self.outside:
          edge = [edge [0]]*(self.degree - 1) + edge + [edge [-1]]*(self.degree - 1)
      return edge
  
  intake_interior = IntakeSurface (False)
  intake_exterior = IntakeSurface (True)
  def intake_cover(index):
    return Part.makeRuledSurface(intake_interior.ends[index], intake_exterior.ends[index])
  intake_CPAP_cover = intake_cover (-1)
  intake_flat_cover = intake_cover (0)
  show_transformed (intake_interior.surface.toShape(), "intake_interior", invisible = True)
  show_transformed (intake_exterior.surface.toShape(), "intake_exterior", invisible = True)
  show_transformed (intake_CPAP_cover, "intake_CPAP_cover", invisible = True)
  show_transformed (intake_flat_cover, "intake_flat_cover", invisible = True)
  intake_solid = Part.Solid(Part.Shell (Part.Compound ([
    Part.makeShell([intake_interior.surface.toShape(), intake_exterior.surface.toShape()]),
    intake_CPAP_cover,
    intake_flat_cover,
  ]).Faces))
  
  '''intake_surfaces_shell = Part.makeShell([intake_interior.surface.toShape(), intake_exterior.surface.toShape()])
  print (intake_surfaces_shell)
  show_transformed (intake_surfaces_shell, "intake_surfaces_shell", invisible = True)
  intake_solid = Part.Solid(Part.Compound ([
    Part.makeShell([intake_interior.surface.toShape(), intake_exterior.surface.toShape()]),
    intake_CPAP_cover,
    intake_flat_cover,
  ]))
  print (intake_solid)'''
  
  show_transformed (intake_solid, "intake_solid")
  
  
  ########################################################################
  ########  SVG bureaucracy  #######
  ########################################################################
  
  def to_svg_data(contents):
    if type(contents) is list:
      return "\n".join(to_svg_data(foo) for foo in contents)
    elif type(contents) is str:
      return contents
    else:
      return Drawing.projectToSVG(contents)
  
  def save_inkscape_svg(filename, contents):
    contents = to_svg_data(contents)
    file_data = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!-- Created with Inkscape (http://www.inkscape.org/) -->

<svg
   xmlns:dc="http://purl.org/dc/elements/1.1/"
   xmlns:cc="http://creativecommons.org/ns#"
   xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
   xmlns:svg="http://www.w3.org/2000/svg"
   xmlns="http://www.w3.org/2000/svg"
   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
   width="8.5in"
   height="11in"
   viewBox="0 0 215.9 279.4"
   version="1.1"
   id="svg8"
   inkscape:version="0.91 r13725"
   sodipodi:docname="'''+filename+'''">
  <defs
     id="defs2" />
  <sodipodi:namedview
     id="base"
     pagecolor="#ffffff"
     bordercolor="#666666"
     borderopacity="1.0"
     inkscape:pageopacity="0.0"
     inkscape:pageshadow="2"
     inkscape:zoom="0.35"
     inkscape:cx="437.51443"
     inkscape:cy="891.42856"
     inkscape:document-units="mm"
     inkscape:current-layer="layer1"
     showgrid="false"
     inkscape:window-width="1328"
     inkscape:window-height="1022"
     inkscape:window-x="363"
     inkscape:window-y="123"
     inkscape:window-maximized="0"
     units="in" />
  <metadata
     id="metadata5">
    <rdf:RDF>
      <cc:Work
         rdf:about="">
        <dc:format>image/svg+xml</dc:format>
        <dc:type
           rdf:resource="http://purl.org/dc/dcmitype/StillImage" />
        <dc:title></dc:title>
      </cc:Work>
    </rdf:RDF>
  </metadata>
  <g
     inkscape:label="Layer 1"
     inkscape:groupmode="layer"
     id="layer1">
      '''+contents+'''
  </g>
</svg>'''
    with open(os.path.join(data_path, "full_face_mask_svgs/", filename), "w") as file:
      file.write(file_data)

  def center_vertices_on_letter_paper(vertices):
    if type(vertices) is list:
      v = vertices
      vertices = lambda: v
    offset = vector(
      (215.9 - (max (vertex [0] for vertex in vertices()) + min (vertex [0] for vertex in vertices())))/2,
      (-279.4 - (max (vertex [1] for vertex in vertices()) + min (vertex [1] for vertex in vertices())))/2,
    )
    for vertex in vertices():
      vertex[0] += offset[0]
      vertex[1] += offset[1]
  
  
  ########################################################################
  ########  Unrolled shield shape  #######
  ########################################################################
    
  flat_approximation_increments = 201
  flat_approximation_factor = math.tau/2/(flat_approximation_increments -1)
  previous_surface = None
  flat_approximations = [0]
  for index in range (flat_approximation_increments):
    parameter = index*flat_approximation_factor
    surface = ShieldSurfacePoint(z=0, parameter = parameter)
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
    adjusted = surface.ellipse_parameter/flat_approximation_factor
    #linearly interpolate
    floor = math.floor (adjusted)
    fraction = adjusted - floor
    previous = flat_approximations [floor]
    next = flat_approximations [floor + 1]
    result = next*fraction + previous*(1-fraction)
    #print (f" angles: {surface.ellipse_parameter}, {adjusted}, floor: {floor}, {fraction}, {previous}, {next}, {result}, ")
    # put 0 in the middle
    return result - flat_approximations [(flat_approximation_increments -1)//2]
    
  
  
  def unrolled(surface):
    offset = surface.position - shield_focal_point
    distance = offset.Length
    paper_radians = flat_approximate_angle (surface)
    result = vector (
      distance*math.cos(paper_radians),
      distance*math.sin (paper_radians))
    return (surface, result)
  def segments (vertices):
    result = []
    for (a,b), (c,d) in zip (vertices [: -1], vertices [1:]):
      original = (a.position - c.position).Length
      derived = (b - d).Length
      ratio = derived/original
      
      #print (f"distances: {original}, {derived}, {derived/original}")
      assert (abs (1 - ratio) <=0.01)
      result.append(Part.LineSegment (b, d))
    print (f"total length: {sum( segment.length() for segment in result)}")
    return result
  
  unrolled_side = [unrolled (surface) for surface in side_points
    if surface.position [0] >= 0
    ]
  unrolled_top_subdivisions = 40
  unrolled_top_back = ShieldSurfacePoint(z=shield_glue_face_width, y= shield_back)
  unrolled_top_parameter_range = unrolled_top_back.ellipse_parameter - math.tau/4
  unrolled_top = [
    unrolled (
      ShieldSurfacePoint(z=shield_glue_face_width, parameter = math.tau/4 + index*unrolled_top_parameter_range/(unrolled_top_subdivisions - 1))
    ) for index in range (unrolled_top_subdivisions)]
    
  unrolled_combined = unrolled_top+unrolled_side
  center_vertices_on_letter_paper(lambda: (vertex [1] for vertex in unrolled_combined))
      
  
  unrolled = Part.Shape(
    segments (unrolled_top) + segments (unrolled_side) + [Part.LineSegment (unrolled_side[-1][1], unrolled_top[0][1])]
  )
  
  show_transformed (unrolled, "unrolled", invisible=pieces_invisible)
  save_inkscape_svg("unrolled_shield.svg", unrolled)
    
  
  ########################################################################
  ########  Cloth shapes  #######
  ########################################################################
  forehead_cloth_shield_back = rim_hook_front
  forehead_cloth_shield_parameter_range = forehead_cloth_shield_back.ellipse_parameter - math.tau/4
  #forehead_cloth_forehead_start_parameter = forehead_curve.parameter (vector(0, 500, 0))
  #forehead_cloth_forehead_end_parameter = forehead_curve.parameter (forehead_cloth_shield_back.position)
  elastic_tube_border_width = 16
  
  source_forehead_length = 0
  cloth_forehead_length = 0
  previous = None
  class ForeheadClothPiece:
    def __init__(self, index):
      nonlocal source_forehead_length
      nonlocal cloth_forehead_length
      self.fraction = index/(unrolled_top_subdivisions - 1)
      self.shield_parameter = math.tau/4 + forehead_cloth_shield_parameter_range*self.fraction
      self.shield = ShieldSurfacePoint(z=shield_glue_face_width+min_wall_thickness, parameter = self.shield_parameter)
      self.forehead_parameter = forehead_curve.parameter(self.shield.position) #forehead_cloth_forehead_start_parameter*(1-self.fraction) + forehead_cloth_forehead_end_parameter*self.fraction
      self.forehead = forehead_curve.value (self.forehead_parameter)
      self.forehead[2] = self.shield.position[2]
      self.source_diff = (self.forehead - self.shield.position)
      if previous is None:
        self.shield_output = vector()
        self.forehead_output = vector(0, -self.source_diff.Length)
        self.shield_angle = 0
        self.forehead_angle = 0
        self.output_shield_angle = 0
        self.output_forehead_angle = 0
      else:
        shield_diff = self.shield.position - previous.shield.position
        forehead_diff = self.forehead - previous.forehead
        source_forehead_length += forehead_diff.Length
        forehead_adjusted_distance = forehead_diff.Length+ min(0.2 * forehead_diff.Length, 0.01 * self.source_diff.Length)
        self.shield_angle = shield_diff.angle()
        shield_angle_diff = self.shield_angle - previous.shield_angle
        self.forehead_angle = forehead_diff.angle()
        forehead_angle_diff = self.forehead_angle - previous.forehead_angle
        
        self.output_shield_angle = previous.output_shield_angle + shield_angle_diff*0.7 # + shield_diff.Length/100
        self.shield_output = previous.shield_output + vector(angle=self.output_shield_angle, length = shield_diff.Length)
        
        perp = self.output_shield_angle - math.tau / 4
        diagonal = (previous.forehead_output - self.shield_output)
        new_output_angle = max(perp, diagonal.angle())
        if diagonal[0] < 0 and diagonal[1] > 0:
          new_output_angle = perp
        for i in range(180):
          new_output_angle += math.tau / 1906
          self.forehead_output = self.shield_output + vector(angle=new_output_angle, length = self.source_diff.Length)
          new_forehead_diff = self.forehead_output - previous.forehead_output
          self.output_forehead_angle = new_forehead_diff.angle()
          output_forehead_angle_diff = self.output_forehead_angle - previous.output_forehead_angle
          if new_forehead_diff.Length >= forehead_diff.Length and output_forehead_angle_diff <= forehead_angle_diff + forehead_diff.Length/60:
            break
          #print(f"{index}, {i}, {self.source_diff}, {new_forehead_diff}")
          assert(i < 175)
        cloth_forehead_length += new_forehead_diff.Length

      self.output_diff = self.forehead_output - self.shield_output
      self.output_direction = self.output_diff.normalized()
      assert(abs(self.output_diff.Length-self.source_diff.Length) < 0.01)
      #Part.show(Part.Compound([Part.LineSegment(self.forehead_output, self.shield_output).toShape(), Part.LineSegment(self.forehead, self.shield.position).toShape()]))
      self.endpoints = [
        self.forehead_output + self.output_direction*elastic_tube_border_width,
        self.shield_output - self.output_direction*elastic_tube_border_width,
      ]
        
  forehead_cloth_pieces = []
  print(f"start forehead_cloth")
  
  for index in range (unrolled_top_subdivisions):
    current = ForeheadClothPiece(index)
    forehead_cloth_pieces.append(current)
    previous = current
  print(f"source_forehead_length: {source_forehead_length}, cloth_forehead_length: {cloth_forehead_length}")
  
  def flipped(v):
    return vector(-v[0], v[1], v[2])
  forehead_cloth_points = (
    [piece.endpoints [0] for piece in forehead_cloth_pieces]
    + [piece.endpoints [1] for piece in reversed (forehead_cloth_pieces)]
    + [flipped(piece.endpoints [1]) for piece in forehead_cloth_pieces[1:]]
    + [flipped(piece.endpoints [0]) for piece in reversed (forehead_cloth_pieces)]
  )
  forehead_cloth_points = [vector(v[1], v[0]) for v in forehead_cloth_points]
  center_vertices_on_letter_paper(forehead_cloth_points)
  forehead_cloth = Part.makePolygon(forehead_cloth_points)
  show_transformed (forehead_cloth, "forehead_cloth", invisible=pieces_invisible)
  save_inkscape_svg("forehead_cloth.svg", forehead_cloth)

  
  ########################################################################
  ########  Split/assemble components into printable parts  #######
  ########################################################################
  whole_frame = Part.Compound ([
    headband,
    top_rim,
    side_rim,
    side_plate,
    side_plate.mirror(vector(), vector (1, 0, 0)),
    side_hooks,
    side_hooks.mirror(vector(), vector (1, 0, 0)),
    intake_solid,
  ]+side_elastic_holders)
  
  show_transformed (whole_frame, "whole_frame", invisible=True)
  
  top_splitter = box(centered (1500), centered (1500), bounds (-6.2, 500))
  right_half = box(bounds(25, 500), centered (1500), centered (1500))
  whole_frame_top = Part.Compound ([
    headband,
    top_rim,
  ] + [a.common(top_splitter) for a in [
    side_rim,
    side_plate,
    side_plate.mirror(vector(), vector (1, 0, 0)),
    side_hooks,
    side_hooks.mirror(vector(), vector (1, 0, 0)),
  ]])
  
  show_transformed (whole_frame_top, "whole_frame_top", invisible=pieces_invisible)
  
  upper_side = Part.Compound ([side_hooks.cut(top_splitter)] + [a.cut([top_splitter, side_splitter]).common(right_half) for a in [
    side_rim,
    side_plate,
  ]])
  show_transformed (upper_side, "upper_side", invisible=pieces_invisible)
  
  lower_right_side = Part.Compound ([a.common(side_splitter).common(right_half) for a in [
    side_rim,
  ]+side_elastic_holders])
  show_transformed (lower_right_side, "lower_right_side", invisible=pieces_invisible)
  
  lower_left_side = Part.Compound ([intake_solid]+[a.common(side_splitter.mirror(vector(), vector(1,0,0))).cut(right_half) for a in [
    side_rim,
  ]+side_elastic_holders])
  show_transformed (lower_left_side, "lower_left_side", invisible=pieces_invisible)
  
  '''import MeshPart
  whole_frame_top_mesh = MeshPart.meshFromShape (
    whole_frame_top,
    MaxLength = 2,
    AngularDeflection = math.tau / 
  )
  document().addObject ("Mesh::Feature", "whole_frame_top_mesh").Mesh = whole_frame_top_mesh'''
  ################################################
  ############### end of current code ############
  ################################################
  return finish()
  
  
  

  forehead_exclusion = forehead_curve.toShape().to_wire().to_face().fancy_extrude (vector (0, 0, 1), bounds (-5, 50))
  
  #forehead_elastic_hole = Part.makeCylinder (3, 50, vector (-86.4, -161, -4))
  forehead_elastic_hole = box (centered (1), 5, centered (100)).makeOffsetShape (1.5, 0.01).rotated (vector(), vector (0, 0, 1), -10).translated (vector (-85.4, -162, -4))
  forehead_exclusion = forehead_exclusion.fuse ([
    forehead_elastic_hole,
    forehead_elastic_hole.mirror (vector(), vector (1, 0, 0)),
  ])
  
  
  
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
  
  
    
  
  
    
  
  return finish()

def run(g):
  for key, value in g.items():
    globals()[key] = value
  globals()["data_path"] = os.path.join(os.path.dirname(os.path.dirname(eliduprees_3d_designs_path)), "data")
  return make_full_face_mask()
  
  
  