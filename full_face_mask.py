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



Additional notes after completing second prototype:
– the intake applies significant torque to the face shield, twisting the clear plastic. Right now, the frame around the intake is very bendable; below the intake, this is a good thing to help the mask's "one-size-fits-all"-ness, but above the intake, it's flexing in the wrong direction. This doesn't seem to be a huge problem, but should still be avoided if possible.
– Despite being much more "one-size-fits-all", it didn't fit someone with glasses. I'll probably have to change the generalized cone shape.
– Right where the top rim meets the headband, it's very easy for the headband to bend the top rim inwards, making it slightly concave. I'm not sure if this is a problem in practice, but theoretically it bends the face shield in an undesired direction and worsens the seal with the forehead cloth.
– The back part of the headband is pretty flexible, such that if you grab just one side of the back, the mask will flop around. It would be preferable if it was more rigid (e.g. if we made the headband wider in the back, which may be desirable anyway).
– The nose-air-replacement is pretty good, but consider whether a grille to direct the air towards my nose could improve it more.
– The chin cloth had several problems:
– – When using the brown elastic, it was much too tight (which makes the cloth harder to install; causes direct discomfort on the chin; pulls down the headband, causing more discomfort at the forehead; makes the mask harder to put on; and puts too much force on some of the weak glued-together joints of the frame).
– – I switched to using a much thinner white elastic, and then it was mostly fine on the chin, but didn't grip the frame quite well enough. The main problem point is around the intake; proposal: don't make gaps in the elastic plate, just fully route it in a curve around the intake. Similarly, we can route the elastic plates a short distance behind the bottom edges of the side plates, providing better grip and frame strength. (Note that, at that point, we can also make the elastic plate have an angled/FDM-printable edge, because there is no longer tension against that edge)
– – The bottom edge of the side plates isn't wide enough; probably we can just make the side plates a bit longer to fix this.
– – Even with the brown elastic, the cloth doesn't actually seal to the side plates. (This may be an acceptable sacrifice though, and in practice, people's faces will often press on it and improve the seal.)
– – The other point where frame strength is a problem is the joint between the sides and the headband. This MIGHT be resolved by printing them as one piece using SLS, but even with SLS, it might be advantageous to print as 2 separate pieces for "arranging more copies into the print volume" reasons. Fortunately, there is no downside to making the frame thicker at the temples (doesn't get in the way of vision, bicycle helmet, OR headphones). So maybe I can design something like a mortise-and-tenon joint there. Another joint in the same place could attach the top rim to the headband as a separate piece, if that would be desirable for any reason.



Let's think about the ideal shape for the face shield to accommodate glasses. What are the technical requirements on the face shield shape?
– Must be a generalized cone
– The point of the generalized cone – which I will call the "focus" – must be either above or below the whole face, otherwise it's weird
– For vision reasons, a few other points are required to be on the cone: a point under the chin, and points very close to the temple and the cheek under it. Also, the lines between these points and the focus cannot intersect the face.
– The entire surface must be convex.
– Let's assume that the focus is horizontally centered on the face. That's not technically required, but not doing it would be ridiculous.
– I measured some moderately bulky glasses as 132 mm across. There must be a point on the cone that is slightly outside of this; further, the line between the glasses-point and the focus must have a third point on it for the frame, which must be outside your vision.

Convexity imposes some interesting restrictions. We can think of it in terms of a view from the focus: with the camera at the focus, all points on the surface can be projected as a 2D curve, and that curve must be convex. So, when we are given any set of required points in 3D, we must find a position of the focus such that those points can be convex. In particular, the glasses point cannot appear outside the line-segment-ish from the temple. (And it's presumably below that line segment.) Therefore, the Y position of the focus must be ... [quick approximations]... either > 490, or < headphones_front (i.e. behind her and and below the face). (Note that in some sense, it wraps around, and values behind the face are greater than any value in front of the face, so this is basically one inequality, not two separate cases.)

Since we prefer not to have flat parts of the shield, it's ideal if the temple "line segment" projects to as short a segment as possible. This suggests that the focus should be BEHIND the face – moderately behind headphones_front, and therefore below the face. (Note that if the focus is too close behind headphones_front, it would project to a line segment going perpendicularly away from the face, which would need to bend too *sharply* in order to get to the front part of the face shield; putting the focus further behind headphones_front makes it diagonal enough to be fine).

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
    
  min_wall_thickness = 0.8
  stiffer_wall_thickness = 1.1
  shield_glue_face_width = 6
  elastic_holder_depth = 10
  CPAP_outer_radius = 21.5/2
  CPAP_inner_radius = CPAP_outer_radius - min_wall_thickness
  CPAP_hose_helix_outer_radius = 22/2
  headband_thickness = min_wall_thickness
  headband_width = 12
  headband_cut_radius = 25
  forehead_point = vector (0, -58)
  headphones_front = forehead_point[1] - 75
  #side_plate_width = max(min_wall_thickness + shield_glue_face_width, elastic_holder_depth)
  #shield_back = headphones_front + side_plate_width - shield_glue_face_width
  shield_back = headphones_front + min_wall_thickness
  back_edge = forehead_point[1] - 96
  wide_face = True
  if wide_face:
    temple_angle = (math.tau/4) * 0.6
  else:
    temple_angle = (math.tau/4) * 0.95
  
  
  ########################################################################
  ########  Generalized cone definitions  #######
  ########################################################################
  '''
  
  formulas:
  if we represent the surface as a function of z, u (z position and ellipse parameter in radians)
  
  then
  oval_size_factor = (shield_focal_z - z) / shield_focal_z = 1.0 - z / shield_focal_z
  y = top_major_radius*oval_size_factor*(sin(u)-1.0) + z/shield_focal_slope
  x = top_minor_radius*oval_size_factor*cos(u)
  
  dy/du = top_major_radius*oval_size_factor*cos(u)
  dy/dz = top_major_radius*(sin(u)-1.0)*(-1.0 / shield_focal_z) + 1.0/shield_focal_slope
  dx/du = top_minor_radius*oval_size_factor*-sin(u)
  dx/dz = top_minor_radius*cos(u)*(-1.0 / shield_focal_z)
  dz/du = 0
  dz/dz = 1
  
  solve for u given x:
  x = top_minor_radius*oval_size_factor*cos(u)
  x / (top_minor_radius*oval_size_factor) = cos(u)
  u = acos(x / (top_minor_radius*oval_size_factor))
  
  solve for u given y:
  y = top_major_radius*oval_size_factor*(sin(u)-1.0) + z/shield_focal_slope
  (y - z/shield_focal_slope + top_major_radius*oval_size_factor) = top_major_radius*oval_size_factor*sin(u)
  (y - z/shield_focal_slope + top_major_radius*oval_size_factor)/top_major_radius*oval_size_factor = sin(u)
  (y - z/shield_focal_slope)/top_major_radius*oval_size_factor + 1.0 = sin(u)
  u = asin((y - z/shield_focal_slope)/top_major_radius*oval_size_factor + 1.0)
  '''
  
  shield_focal_slope = 2
  
  temple_direction = vector(angle = temple_angle, length = 1)
  temple = vector(77, shield_back, 0)
  
  shield_focal_y = temple[1] - (temple[0] * temple_direction[1] / temple_direction[0])
  shield_focal_point = vector (0, shield_focal_y, shield_focal_y * shield_focal_slope)
  
  
  shield_source_curve_points = [
    temple + vector(0,0,shield_glue_face_width),
    temple + vector(1,0,-20),
  ] + ([
    #temple + vector(0,0,-40),
    temple + vector(-1,0,-60),
    #temple + vector(-3,3,-80),
    temple + vector(-4,7,-100),
    temple + vector(-11,21,-123), # just outside the glasses point
    temple + vector(-27,35,-140),
  ] if wide_face else [
    temple + vector(1.5,0,-40),
    temple + vector(1,0,-60),
    temple + vector(1,3,-80),
    temple + vector(-0.5,7,-100),
    temple + vector(-6,21,-123), # just outside the glasses point
    temple + vector(-22,35,-140),
  ]) + [
    temple + vector(-50,46,-153),
    temple + vector(-75,52,-156),
  ]
  shield_source_curve_points = shield_source_curve_points + [vector(-v[0], v[1], v[2]) for v in reversed (shield_source_curve_points[:-1])]
  shield_source_curve_points.reverse()
  degree = 3
  shield_source_curve = Part.BSplineCurve()
  shield_source_curve.buildFromPolesMultsKnots(
    shield_source_curve_points,
    mults = [degree+1] + [1]*(len(shield_source_curve_points) - degree - 1) + [degree+1],
    degree = degree,
  )
  shield_source_curve_length = shield_source_curve.length()
  
  def scaled_shield_source_curve_points (zmin=None, zmax=None):
    if zmin is not None:
      factor = (zmin - shield_focal_point[2]) / (min(vertex[2] for vertex in shield_source_curve_points) - shield_focal_point[2])
    if zmax is not None:
      factor = (zmax - shield_focal_point[2]) / (max(vertex[2] for vertex in shield_source_curve_points) - shield_focal_point[2])
    return [shield_focal_point + (vertex - shield_focal_point)*factor for vertex in shield_source_curve_points]
  
  shield_surface = Part.BSplineSurface()
  shield_surface.buildFromPolesMultsKnots([
    scaled_shield_source_curve_points (zmax = -160),
    scaled_shield_source_curve_points (zmin = 20),
  ],
        [2,2],
        [degree+1] + [1]*(len(shield_source_curve_points) - degree - 1) + [degree+1],
        udegree = 1,
        vdegree = degree,
      )
  show_transformed(Part.Compound ([Part.Point (vertex).toShape() for vertex in shield_source_curve_points]), "shield_source_curve_points", invisible = True)
  show_transformed(shield_source_curve.toShape(), "shield_source_curve", invisible = True)
  show_transformed(shield_surface.toShape(), "shield_surface", invisible = True)
  
  
  
  
  class ShieldCurveInPlane:
    def __init__(self, plane):
      self.plane = plane
      self.curve = shield_surface.intersect(
            plane
          )[0]
      
    def __getattr__(self, name):
      return getattr(self.curve, name)
      
      
      
  side_curve_source_points = [
    (shield_back, shield_glue_face_width),
    (shield_back, -100),
    (-80, -156)
  ]
  side_curve_source_surface = Part.BSplineSurface()
  side_curve_source_surface.buildFromPolesMultsKnots([
    [vector(100, y, z) for y,z in side_curve_source_points],
    [vector(-100, y, z) for y,z in side_curve_source_points],
  ],
        [2,2],
        [2] + [1]*(len(side_curve_source_points) - 1 - 1) + [2],
        udegree = 1,
        vdegree = 1,
      )
      
  upper_side_curve_source_surface = Part.BSplineSurface()
  upper_side_curve_source_surface.buildFromPolesMultsKnots([
    [vector(100, y, z) for y,z in side_curve_source_points[0:2]],
    [vector(0, y, z) for y,z in side_curve_source_points[0:2]],
  ],
        [2,2],
        [2,2],
        udegree = 1,
        vdegree = 1,
      )
  lower_side_curve_source_surface = Part.BSplineSurface()
  lower_side_curve_source_surface.buildFromPolesMultsKnots([
    [vector(100, y, z) for y,z in side_curve_source_points[1:3]],
    [vector(-100, y, z) for y,z in side_curve_source_points[1:3]],
  ],
        [2,2],
        [2,2],
        udegree = 1,
        vdegree = 1,
      )
      
  
  
  show_transformed(side_curve_source_surface.toShape(), "side_curve_source_surface", invisible = True)
  show_transformed(upper_side_curve_source_surface.toShape(), "upper_side_curve_source_surface", invisible = True)
  show_transformed(lower_side_curve_source_surface.toShape(), "lower_side_curve_source_surface", invisible = True)
  shield_side_curve = shield_surface.intersect(
            side_curve_source_surface
          )[0]
  shield_upper_side_curve = ShieldCurveInPlane(upper_side_curve_source_surface)
  shield_lower_side_curve = ShieldCurveInPlane(lower_side_curve_source_surface)
  shield_side_curve_length = shield_side_curve.length()
  show_transformed(shield_side_curve.toShape(), "shield_side_curve", invisible = True)
  show_transformed(shield_upper_side_curve.toShape(), "shield_upper_side_curve", invisible = True)
  show_transformed(shield_lower_side_curve.toShape(), "shield_lower_side_curve", invisible = True)
  upper_side_curve_source_surface.exchangeUV()
  lower_side_curve_source_surface.exchangeUV()
  
  shield_top_curve = ShieldCurveInPlane(Part.Plane(vector(0,0,shield_glue_face_width), vector(0,0,1)))
  shield_top_curve_length = shield_top_curve.length()
  show_transformed(shield_top_curve.toShape(), "shield_top_curve", invisible = True)
  print(shield_top_curve.NbPoles)
  for index in range(100):
    foo = index / 100
    a = shield_top_curve.value(foo)
    p = shield_surface.parameter(a)
    b = shield_surface.value(*p)
    #print((a-b).Length)


  glasses_point = forehead_point + vector (66, 0, -10)
  show_transformed(Part.Point(glasses_point).toShape(), "glasses_point", invisible = True)
  diff = (glasses_point - shield_focal_point).normalized()
  show_transformed(Part.LineSegment(glasses_point + diff*180, glasses_point - diff*180).toShape(), "glasses_line", invisible = True)

  
  
  
  class ShieldSample:
    def __init__(self, parameter = None, closest = None):
      if closest is not None:
        self.shield_parameter = shield_surface.parameter(closest)
      elif parameter is not None:
        self.shield_parameter = parameter
      else:
        assert(false)
      
      self.position = shield_surface.value(*self.shield_parameter)
      self.normal = shield_surface.normal(*self.shield_parameter)
  
  
  class CurveSample (ShieldSample):
    def __init__(self, curve, distance = None, closest = None, y = None, z = None, which = 0):
      self.curve = curve
      if distance is not None:
        self.curve_distance = distance
        self.curve_parameter = curve.parameterAtDistance (distance)
      elif closest is not None:
        self.curve_parameter = curve.parameter(closest)
        self.curve_distance = curve.length(0, self.curve_parameter)
      elif y is not None:
        position = vector(curve.intersect(
              Part.Plane (vector(0,y,0), vector(0,1,0))
            )[0][which])
        self.curve_parameter = curve.parameter(position)
        self.curve_distance = curve.length(0, self.curve_parameter)
      elif z is not None:
        position = vector(curve.intersect(
              Part.Plane (vector(0,0,z), vector(0,0,1))
            )[0][which])
        self.curve_parameter = curve.parameter(position)
        self.curve_distance = curve.length(0, self.curve_parameter)
      else:
        assert(false)
        
      super().__init__(closest = curve.value (self.curve_parameter))
      
      self.curve_tangent = vector (*curve.tangent (self.curve_parameter))
      self.curve_in_surface_normal = self.curve_tangent.cross (self.normal)
      
      if isinstance(self.curve, ShieldCurveInPlane):
        self.plane_normal = self.curve.plane.normal(0,0)
        self.normal_in_plane = -self.normal.cross(self.plane_normal).cross(self.plane_normal).normalized()
        
        self.normal_in_plane_unit_height_from_shield = self.normal_in_plane/self.normal_in_plane.dot(self.normal)
        self.curve_in_surface_normal_unit_height_from_plane = self.curve_in_surface_normal/self.curve_in_surface_normal.dot(self.plane_normal)
      
      # selected to approximately match XYZ when looking at the +x end of the side curve
      self.moving_frame = matrix_from_columns(self.normal, self.curve_in_surface_normal, self.curve_tangent, self.position)


  def curve_samples(curve, num, start_distance, end_distance):
    def point(index):
      fraction = index / (num-1)
      distance = start_distance*(1-fraction) + end_distance*fraction
      return CurveSample(curve, distance=distance)
    return (point(index) for index in range (num))
  
  
  shield_top_full_wire = Part.Shape([shield_top_curve.curve, Part.LineSegment(shield_top_curve.EndPoint, shield_top_curve.StartPoint)]).to_wire()
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
  
  headband_top = shield_glue_face_width + min_wall_thickness
  
  headband_elastic_link = elastic_link.translated(vector(-25 - (elastic_link_radius + headband_thickness/2), forehead_point[1]-192, 0)).cut(headband_interior_2D).extrude(vector (0, 0, headband_width))
  headband = headband.fuse([
    headband_elastic_link,
    headband_elastic_link.mirror(vector(), vector(1,0,0)),
  ]).translated(vector(0,0,headband_top - headband_width))
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
  
  
  
  top_rim_subdivisions = 20
  top_rim_hoops = []
  for sample in curve_samples(shield_top_curve, top_rim_subdivisions, shield_top_curve_length/2, shield_top_curve_length):
    coords = [
      (0, -shield_glue_face_width),
      (0, 0),
      (min_wall_thickness, 0),
      (min_wall_thickness, min_wall_thickness),
      (-min_wall_thickness, min_wall_thickness),
      (-min_wall_thickness, -shield_glue_face_width),
    ]
    wire = polygon([sample.position
      + a*sample.normal_in_plane_unit_height_from_shield
      + b*sample.curve_in_surface_normal_unit_height_from_plane
      for a,b in coords]).to_wire()
    top_rim_hoops.append (wire)
    
  
  top_rim = Part.makeLoft ([wire.mirror (vector(), vector (1, 0, 0)) for wire in reversed (top_rim_hoops[1:])] + top_rim_hoops, True)
  show_transformed (top_rim, "top_rim")
  
  contact_leeway = 0.4
  temple_block_inside = []
  temple_block_top = []
  temple_block_bottom = []
  temple_block_start_distance = forehead_curve.length (0, forehead_curve.parameter (temple))-1
  for distance in range (16):
    temple_block_inside.append (forehead_curve.value (forehead_curve.parameterAtDistance(temple_block_start_distance - distance)))
    sample = CurveSample(shield_top_curve, distance = shield_top_curve_length-distance)
    
    foo = sample.position - sample.normal_in_plane_unit_height_from_shield*min_wall_thickness - sample.normal_in_plane*contact_leeway
    temple_block_top.append(foo + sample.curve_in_surface_normal_unit_height_from_plane*min_wall_thickness)
    temple_block_bottom.append(foo + sample.curve_in_surface_normal_unit_height_from_plane*(min_wall_thickness - headband_width))
  temple_block_hoops = [
    polygon(temple_block_top + [vector(a[0], a[1], temple_block_top[0][2]) for a in reversed(temple_block_inside)]), 
    polygon(temple_block_bottom + [vector(a[0], a[1], temple_block_bottom[0][2]) for a in reversed(temple_block_inside)]), 
  ]
  temple_block = Part.makeLoft(temple_block_hoops, True)
  '''temple_side_peg_flat = polygon([
    (temple_block_bottom[2] + temple_block_inside[2])/2,
    (temple_block_bottom[6]*4 + temple_block_inside[6])/5,
    (temple_block_bottom[6] + temple_block_inside[6]*4)/5,
  ])
  temple_side_peg = temple_side_peg_flat.to_face().fancy_extrude(vector(0,0,1), bounds(-5, shield_glue_face_width+min_wall_thickness))
  temple_block = temple_block.cut (temple_side_peg_flat.makeOffset2D (contact_leeway, join=2).to_face().fancy_extrude(vector(0,0,1), centered (500)))
  
  show_transformed (temple_block, "temple_block")
  show_transformed (temple_side_peg, "temple_side_peg")'''

  ########################################################################
  ########  Side rim and stuff #######
  ########################################################################
  
  
  side_plate_bottom_z = -82
  
  lower_rim_cut = box(centered(500), bounds(-500, shield_back + shield_glue_face_width + contact_leeway), bounds(-100-contact_leeway, 500))
  upper_rim_cut = box(centered(500), centered(500), bounds(0-contact_leeway, 500))
  show_transformed (lower_rim_cut, "lower_rim_cut", invisible=True)
  
  elastic_tension_wire = FreeCAD_shape_builder().build ([
        start_at(0, 0),
        horizontal_to (shield_glue_face_width),
      ]).to_wire()
  
  upper_side_cloth_lip = []
  upper_side_rim_hoops = []
  lower_side_rim_hoops = []
  #side_plate_hoops = []
  elastic_holder_hoops = []
  elastic_tension_hoops = []
  for sample in curve_samples(shield_side_curve, 79, 0, shield_side_curve_length):
    position = sample.position          
    curve_normal = vector (*shield_side_curve.normal(sample.curve_parameter))
    elastic_tension_matrix = matrix_from_columns(-curve_normal, -curve_normal.cross(sample.curve_tangent), sample.curve_tangent, position)
    elastic_tension_shape = elastic_tension_wire.copy()
    elastic_tension_shape.transformShape (elastic_tension_matrix)
    elastic_tension_hoops.append(elastic_tension_shape)
  
  for sample in curve_samples(shield_upper_side_curve, 20, 0, shield_upper_side_curve.length()):
    lip_tip = sample.position + shield_glue_face_width*sample.curve_in_surface_normal
    upper_side_cloth_lip.append (lip_tip)
    upper_side_rim_hoops.append(polygon([
      sample.position,
      lip_tip,
      sample.position + shield_glue_face_width*sample.curve_in_surface_normal - sample.normal*min_wall_thickness,
      sample.position - sample.normal_in_plane_unit_height_from_shield*min_wall_thickness,
      sample.position - sample.normal_in_plane_unit_height_from_shield*min_wall_thickness - sample.plane_normal*min_wall_thickness,
      sample.position - sample.plane_normal*min_wall_thickness + sample.normal_in_plane*min_wall_thickness,
      sample.position + sample.normal_in_plane*min_wall_thickness,
    ]))
    
  def augment_lower_curve_sample(sample):
    sample.lip_direction = (-sample.plane_normal + sample.normal_in_plane*1.5).normalized()
    sample.lip_direction_unit_height_from_shield = sample.lip_direction/sample.lip_direction.dot(sample.normal)
    sample.curve_in_surface_normal_unit_height_from_lip = sample.curve_in_surface_normal/sample.curve_in_surface_normal.cross(sample.lip_direction).Length
    sample.lip_tip = sample.position - min_wall_thickness*sample.curve_in_surface_normal_unit_height_from_lip + sample.lip_direction_unit_height_from_shield*min_wall_thickness
    
  for sample in curve_samples(shield_lower_side_curve, 40, 0, shield_lower_side_curve.length()):
    augment_lower_curve_sample(sample)
    lower_side_rim_hoops.append(polygon([
      sample.position,
      sample.position + shield_glue_face_width*sample.curve_in_surface_normal,
      sample.position + shield_glue_face_width*sample.curve_in_surface_normal - sample.normal_in_plane_unit_height_from_shield*min_wall_thickness,
      sample.position - min_wall_thickness*sample.curve_in_surface_normal_unit_height_from_lip - sample.lip_direction_unit_height_from_shield*min_wall_thickness,
      sample.lip_tip,
      sample.position + sample.lip_direction_unit_height_from_shield*min_wall_thickness,
    ]))

  
  upper_side_rim = Part.makeLoft (upper_side_rim_hoops, True)
  upper_side_rim = upper_side_rim.cut(upper_rim_cut)
  show_transformed (upper_side_rim, "upper_side_rim")
  lower_side_rim = Part.makeLoft (lower_side_rim_hoops, True)
  lower_side_rim = lower_side_rim.cut(lower_rim_cut)
  show_transformed (lower_side_rim, "lower_side_rim")
  #side_elastic_holder = Part.makeLoft (elastic_holder_hoops, True)
  #side_plate = Part.makeLoft (side_plate_hoops, True)
  #show_transformed (side_plate, "side_plate")
  
  show_transformed (Part.Compound(elastic_tension_hoops), "elastic_tension")
  
  side_joint_peg_flat = polygon([
    vector(-2, shield_glue_face_width, 0),
    vector(-4, shield_glue_face_width, 0),
    vector(-5, shield_glue_face_width-3, 0),
    vector(-1, shield_glue_face_width-3, 0),
  ])
  
  side_joint_peg = side_joint_peg_flat.to_face().fancy_extrude(vector(0,0,1), bounds(-5, 8))
  sample = CurveSample (shield_lower_side_curve, distance = shield_lower_side_curve.length())
  matrix = matrix_from_columns(sample.normal_in_plane, sample.curve_in_surface_normal, -sample.curve_tangent, sample.position)
  side_joint_peg = side_joint_peg.transformGeometry(matrix)
  side_joint_peg_hole = side_joint_peg.makeOffsetShape(contact_leeway, 0.01)
  side_joint_peg_neighborhood = side_joint_peg.makeOffsetShape(contact_leeway + stiffer_wall_thickness, 0.01)
  show_transformed (side_joint_peg, "side_joint_peg")
  show_transformed (side_joint_peg_hole, "side_joint_peg_hole", invisible=True)
  
  lower_rim_block = Part.makeLoft ([
    polygon([
      vector(0, shield_glue_face_width, 0),
      vector(-4, shield_glue_face_width, 0),
      vector(-5, shield_glue_face_width-3, 0),
      vector(0, shield_glue_face_width-3, 0),
    ]).to_wire().transformGeometry(matrix_from_columns(sample.normal_in_plane, sample.curve_in_surface_normal, -sample.curve_tangent, sample.position))

    for sample in curve_samples(shield_lower_side_curve, 5, shield_lower_side_curve.length() - 10, shield_lower_side_curve.length())
  ], True)
  lower_rim_block = lower_rim_block.cut(lower_rim_cut)
  show_transformed (lower_rim_block, "lower_rim_block")
  
  upper_side_rim_lower_block = Part.makeLoft ([
    polygon([
      vector(0, shield_glue_face_width, 0),
      vector(-7, shield_glue_face_width, 0),
      vector(-7, -min_wall_thickness/sample.curve_in_surface_normal_unit_height_from_plane.Length, 0),
      vector(0, -min_wall_thickness/sample.curve_in_surface_normal_unit_height_from_plane.Length, 0),
    ]).to_wire().transformGeometry(matrix_from_columns(sample.normal_in_plane, sample.curve_in_surface_normal, -sample.curve_tangent, sample.position))

    for sample in curve_samples(shield_upper_side_curve, 5, 0, 9)
  ], True).cut(side_joint_peg_hole).common(side_joint_peg_neighborhood)
  show_transformed (upper_side_rim_lower_block, "upper_side_rim_lower_block")
  
  upper_side_rim_upper_block = Part.makeLoft ([
    polygon([
      vector(0, 3, 0),
      vector(-10, 3, 0),
      vector(-10, -0.6, 0),
      vector(0, -0.6, 0),
    ]).to_wire().transformGeometry(matrix_from_columns(forehead_curve.tangent(forehead_curve.parameter(temple))[0], sample.curve_in_surface_normal, -sample.curve_tangent, sample.position))

    for sample in curve_samples(shield_upper_side_curve, 2, shield_upper_side_curve.length() - shield_glue_face_width - contact_leeway, shield_upper_side_curve.length() + min_wall_thickness - headband_width + 2)
  ], True)
  show_transformed (upper_side_rim_upper_block, "upper_side_rim_upper_block")
  
  def top_peg (distance, length):
    sample = CurveSample (shield_top_curve, distance = distance)
    return polygon([
      vector(-1.3, min_wall_thickness, 0),
      vector(1.3, min_wall_thickness, 0),
      vector(2, -2.5, 0),
      vector(-2, -2.5, 0),
    ]).to_face().transformGeometry(matrix_from_columns(sample.curve_tangent, sample.curve_in_surface_normal_unit_height_from_plane, sample.normal, sample.position)).fancy_extrude (-forehead_curve.tangent(forehead_curve.parameter(temple))[0], bounds(min_wall_thickness/2, length))
  top_pegs = [top_peg (shield_top_curve_length - 1.5, 10), top_peg (shield_top_curve_length - 8, 5)]
  show_transformed (Part.Compound (top_pegs), "top_pegs")
  
  temple_block = temple_block.cut ([upper_side_rim_upper_block.makeOffsetShape(contact_leeway, 0.01)] + [peg.makeOffsetShape (contact_leeway, 0.01) for peg in top_pegs])
  show_transformed (temple_block, "temple_block")
  
  
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
  
  
  elastic_hook_base_length = 5
  elastic_hook_outwards = 6
  elastic_hook_forwards = 10
  
  elastic_hook = Part.makePolygon([
    vector(0,0),
    vector(elastic_hook_outwards,elastic_hook_forwards-1.25),
    vector(elastic_hook_outwards,elastic_hook_forwards),
    vector(0,elastic_hook_base_length),
    vector(0,0),
  ]).to_face().extrude(vector(0,0,stiffer_wall_thickness))


  top_hook_back = CurveSample (shield_top_curve, y= headphones_front+4, which = 1)
  top_hook_front = CurveSample (shield_top_curve, distance = top_hook_back.curve_distance - elastic_hook_forwards)
  top_hook_forwards = (top_hook_front.position - top_hook_back.position).normalized()
  top_hook = elastic_hook.copy()
  matrix = matrix_from_columns(top_hook_forwards.cross (vector(0,0,1)), -top_hook_forwards, vector(0,0,-1), top_hook_front.position + vector(0,0,min_wall_thickness))
  top_hook.transformShape (matrix)
  
  side_hook = elastic_hook.copy()
  matrix = matrix_from_columns(vector(1,0,0), vector(0,0,1), vector(0,1,0), temple + vector(0, -min_wall_thickness, -elastic_hook_base_length-1))
  side_hook.transformShape (matrix)
  
  show_transformed (top_hook, "top_hook")
  show_transformed (side_hook, "side_hook")
    

  ########################################################################
  ########  Intake  #######
  ########################################################################
  
  intake_flat_thickness_base = 9
  intake_flat_width = 42
  intake_flat_subdivisions = 10
  
  
  intake_center = CurveSample(shield_lower_side_curve, z=-123, which=0)
  intake_skew_factor = 0.8
  intake_forwards = (intake_center.curve_in_surface_normal + intake_center.curve_tangent*intake_skew_factor).normalized()
  
  
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
      center = intake_center.position - intake_forwards*45 - intake_center.normal*(min_wall_thickness + intake_flat_thickness_base/2) - intake_forwards*offset
      direction = intake_forwards.cross (intake_center.normal).normalized()
      other_direction = direction.cross (intake_forwards)
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
      height = intake_flat_width + 2*self.expansion
      if self.outside and rim_side:
        height += 8
      for index in range (intake_flat_subdivisions):
        fraction = index/(intake_flat_subdivisions -1)
        offset = (fraction - 0.5)*height# - forwards_offset*intake_skew_factor
      
        sample = CurveSample(shield_lower_side_curve, distance = intake_center.curve_distance + offset)

        if rim_side:
          normal_distance = min_wall_thickness - self.expansion
        else:
          thickness = intake_flat_thickness_base*0.5*(1+math.sin(fraction*math.tau/2))
          normal_distance = min_wall_thickness + thickness + self.expansion
      
        edge.append (sample.position + sample.curve_in_surface_normal_unit_height_from_plane*forwards_offset - sample.normal_in_plane_unit_height_from_shield*normal_distance)
      if rim_side:
        edge.reverse()
        if self.outside:
          edge = [edge [0]]*(self.degree - 1) + edge + [edge [-1]]*(self.degree - 1)
      return edge
  
  intake_interior = IntakeSurface (False)
  intake_exterior = IntakeSurface (True)
  def intake_cover(index):
    return intake_exterior.ends[index].to_face().cut(intake_interior.ends[index].to_face())
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
  previous_sample = None
  flat_approximations = [0]
  for sample in curve_samples(shield_top_curve, flat_approximation_increments, 0, shield_top_curve_length):
    if previous_sample is not None:
      difference = sample.position - previous_sample.position
      average = (sample.position + previous_sample.position)/2
      from_focus = (average - shield_focal_point)
      relevant_difference = difference - from_focus*(difference.dot(from_focus)/from_focus.dot(from_focus))
      angle = math.atan2(relevant_difference.Length, from_focus.Length)
      flat_approximations.append (flat_approximations [-1] + angle)
    previous_sample = sample
  #print (f"{flat_approximations}")
  def flat_approximate_angle (sample):
    difference = (sample.position - shield_focal_point)
    projected = CurveSample (shield_top_curve, closest = shield_focal_point + difference*(shield_top_curve.StartPoint[2] - shield_focal_point[2])/difference [2])
    adjusted = projected.curve_distance*(flat_approximation_increments -1)/shield_top_curve_length
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
  
  unrolled_side = [unrolled (surface) for surface in curve_samples (shield_side_curve, 40, 0, shield_side_curve_length/2)
    ]
  unrolled_top = [unrolled (surface) for surface in curve_samples (shield_top_curve, 40, 0, shield_top_curve_length/2)
      ]
    
  unrolled_combined = unrolled_top+unrolled_side
  center_vertices_on_letter_paper(lambda: (vertex [1] for vertex in unrolled_combined))
      
  
  unrolled = Part.Shape(
    segments (unrolled_top) + segments (unrolled_side) + [Part.LineSegment (unrolled_side[-1][1], unrolled_top[-1][1])]
  )
  
  show_transformed (unrolled, "unrolled", invisible=pieces_invisible)
  save_inkscape_svg("unrolled_shield.svg", unrolled)
  
  
  ########################################################################
  ########  Forehead cloth  #######
  ########################################################################
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
  
  elastic_tube_border_width = 16

  class RimHeadClothPiece(object):
    pass
            
  class RimHeadCloth:
    def __init__(self, rim_samples, head_curve, target_head_multiplier = 1.5, min_curvature = 1/100, rim_extra_width = elastic_tube_border_width, head_extra_width = elastic_tube_border_width):
      self.source_head_length = 0
      self.cloth_head_length = 0
      
      self.pieces = []
      rim_samples = list(rim_samples)
      debug_display_target = 100
      debug_display_rate = math.ceil(len(rim_samples)/debug_display_target)
      
      for index, rim_sample in enumerate(rim_samples):
        piece = RimHeadClothPiece()
        piece.rim_source = rim_sample.position
        head_parameter = head_curve.parameter (piece.rim_source)
        piece.head_source = head_curve.value (head_parameter)
        source_diff = piece.head_source - piece.rim_source
        source_diff_direction = source_diff.normalized()
        piece.AB_length = source_diff.Length
        
        if len(self.pieces) == 0:
          piece.rim_output = vector()
          piece.head_output = vector(piece.AB_length, 0)
        else:
          previous = self.pieces [-1]
          dA0 = previous.AB_length - piece.AB_length
          dA_length = (piece.rim_source - previous.rim_source).Length
          dA1 = math.sqrt (dA_length**2 - dA0**2)
          original_dB1 = (piece.head_source - previous.head_source).cross(source_diff_direction).Length
          original_dB_length = (piece.head_source - previous.head_source).Length
          original_curvature = rim_sample.curve.curvature(rim_sample.curve_parameter)
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
          
          previous_output_direction = (previous.head_output - previous.rim_output).normalized()
          previous_output_perpendicular = vector(-previous_output_direction[1], previous_output_direction[0])
          piece.rim_output = previous.rim_output + previous_output_direction*dA0 + previous_output_perpendicular*dA1
          piece.head_output = previous.head_output + previous_output_perpendicular*dB1
        
        output_diff = piece.head_output - piece.rim_output
        output_direction = output_diff.normalized()
        #print (f"cloth distances: {output_diff.Length}, {source_diff.Length}, {output_diff.Length/source_diff.Length}")
        if abs(output_diff.Length-source_diff.Length) > 0.5:
          print (f"Warning: cloth distances mismatch: original: {source_diff.Length}, generated: {output_diff.Length}, absolute difference: {output_diff.Length - source_diff.Length}, relative difference: {output_diff.Length/source_diff.Length - 1}")
        
        piece.endpoints = [
          piece.rim_output - output_direction*rim_extra_width,
          piece.head_output + output_direction*head_extra_width,
        ]
        self.pieces.append(piece)
        
        debug_display = False
        #debug_display = True
        if debug_display:
          if index % debug_display_rate == 0 or index == len(rim_samples) - 1:
            Part.show(Part.Compound([Part.LineSegment(piece.head_output, piece.rim_output).toShape(), Part.LineSegment(piece.head_source, piece.rim_source).toShape()]))
          
  # TODO: more correct
  top_outer_rim_curve = shield_top_curve
  forehead_top_curve = forehead_curve.translated(vector(0,0,top_outer_rim_curve.StartPoint[2] - forehead_curve.StartPoint[2]))
  forehead_cloth = RimHeadCloth(
    curve_samples (top_outer_rim_curve, math.floor(shield_top_curve_length * 2), shield_top_curve_length/2, top_hook_front.curve_distance),
    forehead_top_curve,
    min_curvature = 1/120
  )
  
  forehead_cloth_points = (
    [piece.endpoints [0] for piece in forehead_cloth.pieces]
    + [piece.endpoints [1] for piece in reversed (forehead_cloth.pieces)]
  )
  center_vertices_on_letter_paper(forehead_cloth_points)
  forehead_cloth_shape = polygon(forehead_cloth_points)
  show_transformed (forehead_cloth_shape, "forehead_cloth", invisible=pieces_invisible)
  save_inkscape_svg("forehead_cloth.svg", forehead_cloth_shape)
  
  print(f"source_forehead_length: {forehead_cloth.source_head_length}, cloth_forehead_length: {forehead_cloth.cloth_head_length}, ratio: {forehead_cloth.cloth_head_length/forehead_cloth.source_head_length}")
  
  
  ########################################################################
  ########  Chin cloth  #######
  ########################################################################
  
  # add significant leeway to accommodate larger necks, reduce the chance of yanking it off the rim
  neck_y = shield_back - 20
  neck_points = [
    vector(75, neck_y, 20),
    vector(75, neck_y, 0),
    vector(75, neck_y, -20),
    vector(74, neck_y, -40),
    vector(70, neck_y, -60),
    vector(66, neck_y, -80),
    vector(57, neck_y, -100),
    vector(38, neck_y, -120),
    vector(8, neck_y, -140),
  ]
  neck_points = neck_points + [vector(-a[0], a[1], a[2]) for a in reversed(neck_points)]
  
  degree = 3
  neck_curve = Part.BSplineCurve()
  neck_curve.buildFromPolesMultsKnots(
    neck_points,
    mults = [degree+1] + [1]*(len(neck_points) - degree - 1) + [degree+1],
    degree = degree,
  )
  show_transformed(neck_curve.toShape(), "neck_curve", invisible = True)
  
  # TODO: more correct
  side_outer_rim_curve = shield_side_curve
  chin_cloth = RimHeadCloth(
    curve_samples (side_outer_rim_curve, math.floor(shield_side_curve_length * 2), shield_side_curve_length/2, shield_side_curve_length + min_wall_thickness - headband_width),
    neck_curve,
    min_curvature = 1/120
  )
  
  chin_cloth_points = (
    [piece.endpoints [0] for piece in chin_cloth.pieces]
    + [piece.endpoints [1] for piece in reversed (chin_cloth.pieces)]
  )
  center_vertices_on_letter_paper(chin_cloth_points)
  chin_cloth_shape = polygon(chin_cloth_points)
  show_transformed (chin_cloth_shape, "chin_cloth", invisible=pieces_invisible)
  save_inkscape_svg("chin_cloth.svg", chin_cloth_shape)
  
  print(f"source_neck_length: {chin_cloth.source_head_length}, cloth_neck_length: {chin_cloth.cloth_head_length}, ratio: {chin_cloth.cloth_head_length/chin_cloth.source_head_length}")

  ########################################################################
  ########  Split/assemble components into printable parts  #######
  ########################################################################
  '''whole_frame = Part.Compound ([
    headband,
    top_rim,
    side_rim,
    side_plate,
    side_plate.mirror(vector(), vector (1, 0, 0)),
    side_hooks,
    side_hooks.mirror(vector(), vector (1, 0, 0)),
    intake_solid,
  ]+side_elastic_holders)
  
  show_transformed (whole_frame, "whole_frame", invisible=True)'''
  
  def reflected (component):
    return [component, component.mirror (vector(), vector (1, 0, 0))]
  
  whole_headband = Part.Compound ([headband] + reflected (temple_block))
  show_transformed (whole_headband, "whole_headband", invisible=pieces_invisible)
  
  whole_top_rim = Part.Compound ([top_rim] + reflected (top_pegs[0]) + reflected (top_pegs[1]) + reflected (top_hook))
  show_transformed (whole_top_rim, "whole_top_rim", invisible=pieces_invisible)
  
  upper_side = Part.Compound ([upper_side_rim, upper_side_rim_lower_block, upper_side_rim_upper_block, side_hook])
  show_transformed (upper_side, "upper_side", invisible=pieces_invisible)
  
  lower_side = Part.Compound ([lower_side_rim, intake_solid] + reflected (lower_rim_block) + reflected (side_joint_peg))
  show_transformed (lower_side, "lower_side", invisible=pieces_invisible)
  
  
  joint_test_box = box(centered(22, on=78), centered(40, on=-123), centered(40))
  show_transformed (Part.Compound([foo.common(joint_test_box) for foo in upper_side.Solids]), "upper_side_joint_test", invisible=pieces_invisible)
  show_transformed (whole_top_rim.common(joint_test_box), "top_rim_joint_test", invisible=pieces_invisible)
  show_transformed (whole_headband.common(joint_test_box), "headband_joint_test", invisible=pieces_invisible)
  
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
  
  
  