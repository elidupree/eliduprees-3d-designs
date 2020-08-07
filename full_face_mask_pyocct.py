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



Additional notes after prototype #3:

– It runs into my nose more now, and it runs into another tester's nose also. It seems like my model now mistakenly touches (0,-7,0) instead of (0,0,0) like the last version. And also, the physical version is another ~3mm inwards from the model at its default position. I think it's because the top rim is less pointy, and therefore more able to bend inwards at the nose. I should probably just reduce shield_focal_slope to make the forehead stick out more for the same chin position
– The back parts of the headband still flex rather easily, and I still need a more convenient way to clip it together at the back.
– The clips that were supposed to hold the forehead cloth to the headband broke off
– The chin cloth pulls over the shield a bit more than it should on the non-intake side (but is fine on the intake side)
– a small amount of air leaks out at the temple (a small amount of torque from the intake hose bends the frame away from the face, causing the headband to form a triangle of airspace that can't be closed by the elastic-cloth-edge; the CPAP grabber can fix this, but it's preferable to make it impossible to leak by accident).
– We still need a way to make the headband more comfortable (I glued some foam on, but it's not the perfect foam for the job and also it's not very washable)
– This version has WAY less reflections because the shield surface normals mostly point towards the face instead of places where there can be bright light


'''

import math

from pyocct_system import *
initialize_system (globals())

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
cloth_with_elastic_space = 3
forehead_point = Origin
headphones_front = forehead_point[1]-75
#side_plate_width = max(min_wall_thickness + shield_glue_face_width, elastic_holder_depth)
#shield_back = headphones_front + side_plate_width - shield_glue_face_width
shield_back = headphones_front + min_wall_thickness
back_edge = forehead_point[1] - 96

temple_radians = (math.tau/4) * 0.6
shield_focal_slope = 2

lots = 500

########################################################################
########  Generalized cone definitions  #######
########################################################################



temple_direction = Right@Rotate (Up, radians = temple_radians)
temple = Point (77, shield_back, 0)

shield_focal_y = temple[1] - (temple[0] * temple_direction[1] / temple_direction[0])
shield_focal_point = Point (0, shield_focal_y, shield_focal_y * shield_focal_slope)

shield_source_curve_points = [
  temple + vector(0,0,shield_glue_face_width),
  temple + vector(1,0,-20),
  #temple + vector(0,0,-40),
  temple + vector(-1,0,-60),
  #temple + vector(-3,3,-80),
  temple + vector(-4,7,-100),
  temple + vector(-11,21,-123), # just outside the glasses point
  temple + vector(-27,35,-140),
  temple + vector(-50,46,-153),
  temple + vector(-75,52,-156),
]
shield_source_curve_points = shield_source_curve_points + [Point (-v[0], v[1], v[2]) for v in reversed (shield_source_curve_points[:-1])]
shield_source_curve_points.reverse()
save ("shield_source_curve", BSplineCurve(shield_source_curve_points))

shield_source_curve_length = shield_source_curve.length()

def scaled_shield_source_curve_points (zmin=None, zmax=None):
  if zmin is not None:
    factor = (zmin - shield_focal_point[2]) / (min(vertex[2] for vertex in shield_source_curve_points) - shield_focal_point[2])
  if zmax is not None:
    factor = (zmax - shield_focal_point[2]) / (max(vertex[2] for vertex in shield_source_curve_points) - shield_focal_point[2])
  return [shield_focal_point + (vertex - shield_focal_point)*factor for vertex in shield_source_curve_points]

save ("shield_surface", BSplineSurface ([
  scaled_shield_source_curve_points (zmax = -160),
  scaled_shield_source_curve_points (zmin = 20),
],
u = BSplineDimension (degree = 1)
    ))
    
save ("shield_source_points", Compound ([Vertex (point) for point in shield_source_curve_points]))





class ShieldCurveInPlane(SerializeAsVars):
  def __init__(self, plane):
    self.plane = plane
    self.curve = shield_surface.intersections (plane)[0]
    
  def __getattr__(self, name):
    return getattr(self.curve, name)

side_curve_source_points = [
  (shield_back, shield_glue_face_width),
  (shield_back, -64),
  (forehead_point[1]-22, -156)
]

save ("side_curve_source_surface", BSplineSurface([
    [Point (-100, y, z) for y,z in side_curve_source_points],
    [Point (100, y, z) for y,z in side_curve_source_points],
  ],
  BSplineDimension (degree = 1),
  BSplineDimension (degree = 1),
))

save ("upper_side_curve_source_surface", BSplineSurface([
    [Point (0, y, z) for y,z in side_curve_source_points[0:2]],
    [Point (100, y, z) for y,z in side_curve_source_points[0:2]],
  ],
  BSplineDimension (degree = 1),
  BSplineDimension (degree = 1),
))

save ("lower_side_curve_source_surface", BSplineSurface([
    [Point (-100, y, z) for y,z in side_curve_source_points[1:3]],
    [Point (100, y, z) for y,z in side_curve_source_points[1:3]],
  ],
  BSplineDimension (degree = 1),
  BSplineDimension (degree = 1),
))

@run_if_changed
def make_shield_curves():
  save ("shield_side_curve", shield_surface.intersections (
    side_curve_source_surface
  )[0])
  save ("shield_upper_side_curve", ShieldCurveInPlane(upper_side_curve_source_surface))
  save ("shield_lower_side_curve", ShieldCurveInPlane(lower_side_curve_source_surface))
  save ("shield_top_curve", ShieldCurveInPlane(Plane(Point (0,0,shield_glue_face_width), Up)))
  
shield_side_curve_length = shield_side_curve.length()
#preview (Compound (Face (shield_surface), Face (side_curve_source_surface)))

shield_top_curve_length = shield_top_curve.length()

'''print(shield_top_curve.NbPoles())
for index in range(100):
  foo = index / 100
  a = shield_top_curve.value(foo)
  p = shield_surface.parameter(a)
  b = shield_surface.value(p)
  #print((a-b).Length)'''


glasses_point = forehead_point + vector (66, 0, -10)
save ("glasses_vertex", Vertex (glasses_point))
diff = Direction (glasses_point - shield_focal_point)
save ("glasses_edge", Edge (glasses_point + diff*180, glasses_point - diff*180))




class ShieldSample:
  def __init__(self, parameter = None, closest = None):
    if closest is not None:
      self.shield_parameter = shield_surface.parameter(closest)
    elif parameter is not None:
      self.shield_parameter = parameter
    else:
      assert(false)
    
    self.position = shield_surface.value(self.shield_parameter)
    self.normal = shield_surface.normal(self.shield_parameter)


class CurveSample (ShieldSample):
  def __init__(self, curve, distance = None, closest = None, y = None, z = None, which = 0):
    self.curve = curve
    if distance is not None:
      self.curve_distance = distance
      self.curve_parameter = curve.parameter(distance = distance)
    elif closest is not None:
      self.curve_parameter = curve.parameter(closest = closest)
      self.curve_distance = curve.length(0, self.curve_parameter)
    elif y is not None:
      position = curve.intersections (
            Plane (Point(0,y,0), Front)
          ).points [which]
      self.curve_parameter = curve.parameter(closest = position)
      self.curve_distance = curve.length(0, self.curve_parameter)
    elif z is not None:
      position = curve.intersections (
            Plane (Point(0,0,z), Up)
          ).points [which]
      self.curve_parameter = curve.parameter(closest = position)
      self.curve_distance = curve.length(0, self.curve_parameter)
    else:
      assert(false)
    
    derivatives = curve.derivatives(self.curve_parameter)
    super().__init__(closest = derivatives.position)
    
    self.curve_tangent = derivatives.tangent
    self.curve_normal = derivatives.normal
    self.curve_in_surface_normal = self.curve_tangent.cross (self.normal)
    
    if isinstance(self.curve, ShieldCurveInPlane):
      self.plane_normal = self.curve.plane.normal(0,0) # note: even though it's a plane, it becomes a BSplineSurface when it gets reloaded, so we need to give the parameters
      self.normal_in_plane = -self.normal.cross(self.plane_normal).cross(self.plane_normal).normalized()
      
      self.normal_in_plane_unit_height_from_shield = self.normal_in_plane/self.normal_in_plane.dot(self.normal)
      self.curve_in_surface_normal_unit_height_from_plane = self.curve_in_surface_normal/self.curve_in_surface_normal.dot(self.plane_normal)
    
    # selected to approximately match XYZ when looking at the +x end of the side curve
    # self.moving_frame = Transform(self.normal, self.curve_in_surface_normal, self.curve_tangent, self.position)


def curve_samples(curve, start_distance = None, end_distance = None, **kwargs):
  if start_distance is None:
    start_distance = 0
    end_distance = curve.length()
  return (CurveSample(curve, distance=distance) for distance in subdivisions(start_distance, end_distance, **kwargs))


@run_if_changed
def make_shield_cross_sections():
  shield_top_full_wire = Wire (Edge (shield_top_curve.curve), Edge (shield_top_curve.EndPoint(), shield_top_curve.StartPoint()))
  shield_region = HalfSpace (Point (0, shield_back, 0), Back)
  shield_cross_section = Face (shield_top_full_wire)
  shield_cross_sections = []
  for offset_distance in (20.0*x for x in range(10)):
    offset_fraction = offset_distance / -shield_focal_point[2]
    full_section = shield_cross_section@Scale (1.0 - offset_fraction)@Translate (Vector(Origin,shield_focal_point)*offset_fraction)
    shield_cross_sections.append(Intersection(full_section, shield_region))
    
  save ("shield_cross_sections", Compound (shield_cross_sections))


########################################################################
########  Forehead/headband/top rim  #######
########################################################################

forehead_points = [vector (a,b,0) for a,b in [
  (0, 0),
  (15, 0),
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
degree = 3
forehead_poles = [forehead_point + a@Mirror (Right) for a in reversed(forehead_points[1:])] + [forehead_point + a for a in forehead_points[:-1]]
save ("forehead_curve", BSplineCurve(
  forehead_poles,
  BSplineDimension (periodic = True),
))
print(f"Forehead circumference: {forehead_curve.length()}")

#headband_cut_box = Box (centered (50), bounds (-500, forehead_point[1]-100), centered(500))
save ("headband_interior_2D", Face (Wire (Edge (forehead_curve))))

save ("headband_2D", Offset2D(Wire (Edge (forehead_curve)), headband_thickness, fill = True)#.cut(headband_cut_box)
)

headband = headband_2D.extrude (Up*headband_width)

'''headband_side_profile = Face(Wire(
Segment (y = 0),
Vertex (x = headphones_front + 20, tangent = True),
Bezier (),
Vertex (x = headphones_front, tangent = True),
Segment (y = -6),
Segment (x = -lots),
Segment (y = headband_width),
Segment (x = lots),
))

headband_side_profile = FreeCAD_shape_builder().build ([
  start_at(500, 0),
  horizontal_to(headphones_front + 20),
  bezier([
    (headphones_front + 15, 0),
    (headphones_front + 10, -3),
    (headphones_front + 5, -6),
    (headphones_front, -6),
  ]),
  horizontal_to(-500),
  vertical_to(headband_width),
  horizontal_to(500),
  close(),
]).as_yz().to_wire().to_face().fancy_extrude (vector (1, 0, 0), centered(500))
show_transformed (headband_side_profile, "headband_side_profile", invisible=True)
headband = headband.common(headband_side_profile)

# using a weird shaped way to attach the elastic for now, just for FDM convenience
elastic_link_radius = 3
elastic_link = Part.Circle(vector(), vector(0,0,1), elastic_link_radius + headband_thickness).toShape().to_wire().to_face().cut(Part.Circle(vector(), vector(0,0,1), elastic_link_radius).toShape().to_wire().to_face())'''

headband_top = shield_glue_face_width + min_wall_thickness

'''headband_elastic_link_parameter = forehead_curve.parameter(vector(60, forehead_point[1]-170))

headband_elastic_link = elastic_link.translated(
  forehead_curve.value(headband_elastic_link_parameter)
  - forehead_curve.normal(headband_elastic_link_parameter) * (headband_thickness + elastic_link_radius * 0.5)
).cut(headband_interior_2D).extrude(vector (0, 0, headband_width))
headband = headband.fuse([
  headband_elastic_link,
  headband_elastic_link.mirror(vector(), vector(1,0,0)),
]).translated(vector(0,0,headband_top - headband_width))'''

save("headband")

'''
CPAP_grabber_length = 16
CPAP_grabber_shape = FreeCAD_shape_builder(zigzag_length_limit = 3, zigzag_depth = -1).build ([
      start_at(CPAP_hose_helix_outer_radius + min_wall_thickness/2, 0),
      vertical_to(CPAP_grabber_length),
  ]).as_xz().to_wire().makeOffset2D(min_wall_thickness/2, fill=True).common(box(centered(500), centered(500), bounds(0, CPAP_grabber_length)))

CPAP_grabber_shape = CPAP_grabber_shape.revolve(vector(), vector(0,0,1), 360)
CPAP_grabber_shape = CPAP_grabber_shape.cut(
  FreeCAD_shape_builder().build ([
      start_at(0, 0),
      diagonal_to(-50, -100),
      horizontal_to(50),
      close()
    ]).to_wire().to_face().extrude(vector (0, 0, CPAP_grabber_length))
)

CPAP_grabber = Part.Compound([
  CPAP_grabber_shape,
  elastic_link.translated(vector(CPAP_hose_helix_outer_radius + min_wall_thickness + elastic_link_radius, 0, 0)).extrude(vector (0, 0, CPAP_grabber_length))
])
show_transformed (CPAP_grabber, "CPAP_grabber")'''


@run_if_changed
def make_top_rim():
  top_rim_subdivisions = 20
  top_rim_hoops = []
  for sample in curve_samples(shield_top_curve, shield_top_curve_length/2, shield_top_curve_length, amount=top_rim_subdivisions):
    coords = [
      (0, -shield_glue_face_width),
      (0, 0),
      (min_wall_thickness, 0),
      (min_wall_thickness, min_wall_thickness),
      (-min_wall_thickness, min_wall_thickness),
      (-min_wall_thickness, -shield_glue_face_width),
    ]
    wire = Wire([
      sample.position
        + a*sample.normal_in_plane_unit_height_from_shield
        + b*sample.curve_in_surface_normal_unit_height_from_plane
      for a,b in coords
    ], loop = True)
    top_rim_hoops.append (wire)
    
  save ("top_rim", Loft ([wire@Mirror (Right) for wire in reversed (top_rim_hoops[1:])] + top_rim_hoops, solid = True))

contact_leeway = 0.4

'''
temple_block_inside = []
temple_block_top = []
temple_block_bottom = []
temple_block_start_distance = forehead_curve.length (0, forehead_curve.parameter (temple))-1
temple_block_length = 15
for distance in range (temple_block_length + 1):
  temple_block_inside.append (forehead_curve.value (forehead_curve.parameterAtDistance(temple_block_start_distance - distance)))
  sample = CurveSample(shield_top_curve, distance = shield_top_curve_length-distance*1.1)
  
  foo = sample.position - sample.normal_in_plane_unit_height_from_shield*min_wall_thickness - sample.normal_in_plane*contact_leeway
  temple_block_top.append(foo + sample.curve_in_surface_normal_unit_height_from_plane*min_wall_thickness)
  temple_block_bottom.append(foo + sample.curve_in_surface_normal_unit_height_from_plane*(min_wall_thickness - headband_width))
temple_block_hoops = [
  polygon(temple_block_top + [vector(a[0], a[1], temple_block_top[0][2]) for a in reversed(temple_block_inside)]), 
  polygon(temple_block_bottom + [vector(a[0], a[1], temple_block_bottom[0][2]) for a in reversed(temple_block_inside)]), 
]
temple_block = Part.makeLoft(temple_block_hoops, True)

forehead_hook_thickness = 3
forehead_hook_distance = temple_block_start_distance - temple_block_length - cloth_with_elastic_space - forehead_hook_thickness/2
forehead_hook_parameter = forehead_curve.parameterAtDistance(forehead_hook_distance)
forehead_hook_base = forehead_curve.value(forehead_hook_parameter)
forehead_hook_normal = forehead_curve.normal(forehead_hook_parameter)
forehead_hook_tangent = vector(forehead_curve.tangent(forehead_hook_parameter)[0])
forehead_hook = Part.Compound([
  box(
    bounds(0, cloth_with_elastic_space + forehead_hook_thickness/2),
    centered(forehead_hook_thickness),
    bounds(headband_width - forehead_hook_thickness, headband_width),
  ),
  Part.makeCylinder(
    forehead_hook_thickness/2,
    headband_width,
    vector(cloth_with_elastic_space + forehead_hook_thickness/2, 0, 0),
    vector(0,0,1),
  )
])
matrix = matrix_from_columns(-forehead_hook_normal, forehead_hook_tangent, vector(0,0,1), forehead_hook_base + vector(0,0,headband_top - headband_width))
forehead_hook = forehead_hook.transformGeometry (matrix)

show_transformed (forehead_hook, "forehead_hook")

forehead_hook_distance_range = forehead_curve.length(0, forehead_curve.parameter(vector(-forehead_hook_base[0], forehead_hook_base[1], forehead_hook_base[2]))) - forehead_hook_distance
num_forehead_elastic_guides = 16
forehead_elastic_guides = []
forehead_elastic_guide_length = 3.5
for index in range(num_forehead_elastic_guides):
  frac = (index + 1) / (num_forehead_elastic_guides + 1)
  distance = forehead_hook_distance + forehead_hook_distance_range*frac
  parameter = forehead_curve.parameterAtDistance(distance)
  base = forehead_curve.value(parameter)
  normal = forehead_curve.normal(parameter)
  tangent = vector(forehead_curve.tangent(parameter)[0])
  shape = FreeCAD_shape_builder().build([
    start_at(0,0),
    horizontal_to(forehead_elastic_guide_length),
    vertical_to(min_wall_thickness),
    diagonal_to(min_wall_thickness, forehead_elastic_guide_length),
    horizontal_to(0),
    close()
  ]).to_wire().to_face().fancy_extrude(vector(0,0,1), centered(stiffer_wall_thickness))
  forehead_elastic_guides.append(
    shape.transformGeometry (matrix_from_columns(
      -normal,
      vector(0,0,1),
      tangent,
      base + vector(0,0,headband_top - headband_width)
    ))
  )
  forehead_elastic_guides.append(
    shape.transformGeometry (matrix_from_columns(
      -normal,
      vector(0,0,-1),
      tangent,
      base + vector(0,0,headband_top)
    ))
  )
forehead_elastic_guides = Part.Compound(forehead_elastic_guides)
show_transformed (forehead_elastic_guides, "forehead_elastic_guides")'''

########################################################################
########  Side rim and stuff #######
########################################################################


side_plate_bottom_z = -82
Vertex(0, shield_back + shield_glue_face_width + contact_leeway, side_curve_source_points[1][1]-contact_leeway).point()
save ("lower_rim_cut", Vertex(
  0,
  shield_back + shield_glue_face_width + contact_leeway,
  side_curve_source_points[1][1]-contact_leeway
).extrude(Right*lots, centered=True).extrude(Front).extrude(Up))
save ("upper_rim_cut", HalfSpace(Point(0,0,0-contact_leeway), Up))


def upper_side_lip_tip(sample):
  return sample.position - sample.plane_normal*min_wall_thickness + sample.normal_in_plane*min_wall_thickness
  
print(shield_upper_side_curve.plane)
  
@run_if_changed
def make_upper_side_rim():
  upper_side_rim_hoops = []
  for sample in curve_samples(shield_upper_side_curve, amount = 20):
    upper_side_rim_hoops.append(Wire([
      sample.position,
      sample.position - shield_glue_face_width*sample.curve_in_surface_normal,
      sample.position - shield_glue_face_width*sample.curve_in_surface_normal - sample.normal*min_wall_thickness,
      sample.position - sample.normal_in_plane_unit_height_from_shield*min_wall_thickness,
      sample.position - sample.normal_in_plane_unit_height_from_shield*min_wall_thickness - sample.plane_normal*min_wall_thickness,
      upper_side_lip_tip(sample),
      sample.position + sample.normal_in_plane*min_wall_thickness,
    ], loop = True))
  upper_side_rim = Loft (upper_side_rim_hoops, solid = True)
  upper_side_rim = Difference(upper_side_rim, upper_rim_cut)
  save ("upper_side_rim", upper_side_rim)


upper_side_cloth_lip = []
for sample in curve_samples(shield_upper_side_curve, 0, shield_upper_side_curve.length() + min_wall_thickness - headband_width, amount = 20):
  upper_side_cloth_lip.append (upper_side_lip_tip(sample))
  
def augment_lower_curve_sample(sample):
  sample.lip_direction = (-sample.plane_normal + sample.normal_in_plane*1.5).normalized()
  sample.lip_direction_unit_height_from_shield = sample.lip_direction/sample.lip_direction.dot(sample.normal)
  sample.curve_in_surface_normal_unit_height_from_lip = sample.curve_in_surface_normal/sample.curve_in_surface_normal.cross(sample.lip_direction).length()
  sample.lip_tip = sample.position - min_wall_thickness*sample.curve_in_surface_normal_unit_height_from_lip + sample.lip_direction_unit_height_from_shield*min_wall_thickness

@run_if_changed
def make_lower_side_rim():
  lower_side_rim_hoops = []
  for sample in curve_samples(shield_lower_side_curve, amount = 40):
    augment_lower_curve_sample(sample)
    lower_side_rim_hoops.append(Wire([
      sample.position,
      sample.position + shield_glue_face_width*sample.curve_in_surface_normal_unit_height_from_plane,
      sample.position + shield_glue_face_width*sample.curve_in_surface_normal_unit_height_from_plane - sample.normal_in_plane_unit_height_from_shield*min_wall_thickness,
      sample.lip_tip - sample.normal_in_plane_unit_height_from_shield*min_wall_thickness*2,
      sample.lip_tip,
      sample.position + sample.lip_direction_unit_height_from_shield*min_wall_thickness,
    ], loop = True))
  lower_side_rim = Loft (lower_side_rim_hoops, solid = True)
  lower_side_rim = Difference(lower_side_rim, lower_rim_cut)
  save ("lower_side_rim", lower_side_rim)


#side_plate_hoops = []
elastic_tension_hoops = []
for sample in curve_samples(shield_side_curve, amount = 79):
  elastic_tension_hoops.append (Edge (sample.position, sample.position + sample.curve_normal*10))         

save("elastic_tension", Compound (elastic_tension_hoops))




'''
side_joint_peg_flat = polygon([
  vector(-1, shield_glue_face_width, 0),
  vector(-4, shield_glue_face_width, 0),
  vector(-3, shield_glue_face_width-3, 0),
  vector(-1, shield_glue_face_width-3, 0),
])

side_joint_peg = side_joint_peg_flat.to_face().fancy_extrude(vector(0,0,1), bounds(-5, 8))
sample = CurveSample (shield_lower_side_curve, distance = shield_lower_side_curve.length())
matrix = matrix_from_columns(sample.normal_in_plane_unit_height_from_shield, sample.curve_in_surface_normal_unit_height_from_plane, -sample.curve_tangent, sample.position)
side_joint_peg = side_joint_peg.transformGeometry(matrix)
side_joint_peg_hole = side_joint_peg.makeOffsetShape(contact_leeway, 0.01)
side_joint_peg_neighborhood = side_joint_peg.makeOffsetShape(contact_leeway + min_wall_thickness, 0.01)
show_transformed (side_joint_peg, "side_joint_peg")
show_transformed (side_joint_peg_hole, "side_joint_peg_hole", invisible=True)

lower_rim_block = Part.makeLoft ([
  polygon([
    vector(0, shield_glue_face_width, 0),
    vector(-3.7, shield_glue_face_width, 0),
    vector(-2.9, shield_glue_face_width-3, 0),
    vector(0, shield_glue_face_width-3, 0),
  ]).to_wire().transformGeometry(matrix_from_columns(sample.normal_in_plane_unit_height_from_shield, sample.curve_in_surface_normal_unit_height_from_plane, -sample.curve_tangent, sample.position))

  for sample in curve_samples(shield_lower_side_curve, 5, shield_lower_side_curve.length() - 10, shield_lower_side_curve.length())
], True)
lower_rim_block = lower_rim_block.cut(lower_rim_cut)
show_transformed (lower_rim_block, "lower_rim_block")

upper_side_rim_lower_block = Part.makeLoft ([
  polygon([
    vector(0, shield_glue_face_width, 0),
    vector(-7, shield_glue_face_width, 0),
    vector(-7, -min_wall_thickness/sample.curve_in_surface_normal_unit_height_from_plane.length(), 0),
    vector(0, -min_wall_thickness/sample.curve_in_surface_normal_unit_height_from_plane.length(), 0),
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
show_transformed (side_hook, "side_hook")'''

  

########################################################################
########  Intake  #######
########################################################################

intake_flat_air_thickness_base = 12
intake_flat_width = 78
intake_flat_subdivisions = 10
intake_edge_skip_size = (cloth_with_elastic_space + min_wall_thickness)*2




@run_if_changed
def make_intake():
  intake_middle = CurveSample(shield_lower_side_curve, z=-110, which=1)
  augment_lower_curve_sample(intake_middle)
  #intake_skew_factor = 0.8
  #intake_forwards = (intake_middle.curve_in_surface_normal + intake_middle.curve_tangent*intake_skew_factor).normalized()
  CPAP_back_center = Point(-85, headphones_front - 40, -110)
  intake_flat_back_center_approx = intake_middle.lip_tip - (elastic_holder_depth+4)*intake_middle.curve_in_surface_normal_unit_height_from_plane - intake_middle.normal*(min_wall_thickness + intake_flat_air_thickness_base/2)
  CPAP_forwards = Direction (CPAP_back_center, intake_flat_back_center_approx) #vector(0.2, 1, -0.1).normalized()

  lower_side_center_sample = CurveSample(shield_lower_side_curve, distance=shield_lower_side_curve.length()/2)
  augment_lower_curve_sample(lower_side_center_sample)
  
  lower_side_cloth_lip = []
  lower_side_extra_lip_hoops = []
  intake_edges = ([], [], [], [])
  for sample in curve_samples(shield_lower_side_curve, shield_lower_side_curve.length()-3, 0, amount = 200):
    augment_lower_curve_sample(sample)
    offset = sample.curve_distance - intake_middle.curve_distance
    relative_offset = 2*offset / intake_flat_width
    outer_edge_from_air = min_wall_thickness+cloth_with_elastic_space
    if abs(relative_offset) < 1:
      # to make the thing continuous, we need that when this is zero, the END of the air is at the outer lip, so we need to add space to compensate
      air_thickness = (intake_flat_air_thickness_base + outer_edge_from_air) * math.e * math.exp(1/(relative_offset**2 - 1))
      air_thickness_derivative = (2 / intake_flat_width) * 2*relative_offset*air_thickness / ((relative_offset**2 - 1)**2)
    else:
      air_thickness = 0
      air_thickness_derivative = 0
    beyond_air_angle = math.atan2(air_thickness_derivative, 1)
    
    edge_distances = [(min_wall_thickness,0),
      (min_wall_thickness*2,0),
      (air_thickness, -outer_edge_from_air+0),
      (air_thickness, -outer_edge_from_air+min_wall_thickness),
      (air_thickness, -outer_edge_from_air+min_wall_thickness+cloth_with_elastic_space),
      (air_thickness, -outer_edge_from_air+min_wall_thickness*2+cloth_with_elastic_space),
    ]
    
    intake_edge_offsets = []
    for before_air, beyond_air in edge_distances:
      x = before_air + beyond_air * math.cos(beyond_air_angle)
      y = beyond_air * math.sin(beyond_air_angle)
      
      intake_edge_offsets.append(
        - x*sample.normal_in_plane_unit_height_from_shield
        + y*sample.curve_tangent
      )
      
    print_surface_base_point = sample.position + shield_glue_face_width*sample.curve_in_surface_normal_unit_height_from_plane + min_wall_thickness*sample.normal_in_plane_unit_height_from_shield
    elastic_end_base_point = sample.lip_tip - elastic_holder_depth*sample.curve_in_surface_normal_unit_height_from_plane
    
    if air_thickness > edge_distances[1][0] + 1.5 - edge_distances[2][1]:
      for index in [1,2]:
        intake_edges [index].append ((
          print_surface_base_point + intake_edge_offsets [index],
          elastic_end_base_point + intake_edge_offsets [index],
        ))
    if air_thickness > edge_distances[0][0] + 1 - edge_distances[3][1]:
      for index in [0,3]:
        intake_edges [index].append ((
          print_surface_base_point + intake_edge_offsets [index],
          elastic_end_base_point + intake_edge_offsets [index],
        ))
      
    if sample.position[0] > 0:
      lower_side_cloth_lip.append (sample.lip_tip)
    else:
      lower_side_center_max = (sample.lip_tip[2] - lower_side_center_sample.lip_tip[2])/sample.curve_in_surface_normal[2]
      new_lip_distance = min(
        elastic_holder_depth,
        lower_side_center_max*0.4,
        (sample.lip_tip[1] - headphones_front)/sample.curve_in_surface_normal[1],
      )
      lip_base_point = sample.lip_tip + intake_edge_offsets[4]
      inner_base_point = sample.lip_tip + intake_edge_offsets[5]
      
      down = -new_lip_distance*sample.curve_in_surface_normal
      leeway = 0.5*min_wall_thickness*sample.curve_in_surface_normal
      
      def limited_project_towards (source, target):
        #return target
        starting_amount = (source - sample.position).dot (sample.normal) + min_wall_thickness*0.7
        if starting_amount >= 0:
          return source
        amount_towards_shield = (target - source).dot (sample.normal)
        if starting_amount + amount_towards_shield <= 0:
          return target
        return source + (target - source)*(-starting_amount)/amount_towards_shield

      wall_inwards = min_wall_thickness*sample.normal_in_plane_unit_height_from_shield
      lower_side_extra_lip_hoops.append (Wire ([
        limited_project_towards (inner_base_point + leeway, print_surface_base_point+ intake_edge_offsets [3]),
        inner_base_point,
        inner_base_point + down,
        lip_base_point + down,
        lip_base_point,
        limited_project_towards (lip_base_point + leeway, print_surface_base_point+ intake_edge_offsets [2]),
      ], loop = True))
      
      if air_thickness < 0.001:
        lower_side_cloth_lip.append (lip_base_point + down)
      # a fairly arbitrary approximation, but it's not necessarily worth the effort of computing the points it would realistically be taut across
      elif air_thickness >= outer_edge_from_air+intake_flat_air_thickness_base*0.5:
        lower_side_cloth_lip.append (sample.lip_tip + intake_edge_offsets[3] + down)
        
  intake_inner_pairs = intake_edges [1] + intake_edges[2][::-1]
  intake_outer_pairs = intake_edges [0] + intake_edges[3][::-1]


        
  '''
  for sample in curve_samples(shield_lower_side_curve, 20, intake_middle.curve_distance + intake_flat_width/2, intake_middle.curve_distance - intake_flat_width/2):
    augment_intake_sample(sample)
    
    shift = -0.5*min_wall_thickness*sample.curve_in_surface_normal
    big_shift = (min_wall_thickness+elastic_holder_depth)*sample.curve_in_surface_normal
    lower_side_cloth_lip.append (sample.intake_edge_points[3]+shift - big_shift)
    lower_side_extra_lip_hoops.append (polygon ([
        sample.intake_edge_points[4]+shift,
        sample.intake_edge_points[5]+shift,
        sample.intake_edge_points[5]+shift - big_shift,
        sample.intake_edge_points[4]+shift - big_shift,
      ]).to_wire())

  '''
    

  chin_cloth_lip_points = upper_side_cloth_lip[::-1] + lower_side_cloth_lip + [a@Mirror (Right) for a in upper_side_cloth_lip]
  save ("chin_cloth_lip", Interpolate (chin_cloth_lip_points))
  save ("chin_cloth_lip", Compound ([Vertex (point) for point in chin_cloth_lip_points]))

  save ("lower_side_extra_lip", Loft(lower_side_extra_lip_hoops, solid = True, ruled = True))

  class IntakeSurface:
    def __init__(self, pairs, expansion):
      self.pairs = pairs
      self.expansion = expansion
      self.num_points = len(self.pairs)
      
      self.hoops = [self.flat_hoop (frac) for frac in [0,0.7,0.8,0.9,1.5]] + [self.CPAP_hoop (frac) for frac in [-0.3, 0.4, 0.6, 0.8, 1.0]]
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
      direction = Direction (CPAP_forwards.cross (intake_middle.normal))
      other_direction = -direction.cross (CPAP_forwards)
      def CPAP_point (index):
        angle = index/self.num_points*math.tau - 0.7*math.tau
        return center + direction*(CPAP_inner_radius + self.expansion)*math.sin (angle) + other_direction*(CPAP_inner_radius + self.expansion)*math.cos(angle)
      return [CPAP_point (index) for index in range (self.num_points)]

    def flat_hoop(self, frac):
      return [Between (a,b,frac) for a,b in self.pairs]

  intake_interior = IntakeSurface (intake_inner_pairs, 0)
  intake_exterior = IntakeSurface (intake_outer_pairs, min_wall_thickness)
  def intake_cover(index):
    return Face (intake_exterior.ends[index], holes = intake_interior.ends[index].complemented()),
  intake_CPAP_cover = intake_cover (-1)
  intake_flat_cover = intake_cover (0)
  '''show_transformed (intake_interior.surface.toShape(), "intake_interior", invisible = True)
  show_transformed (intake_exterior.surface.toShape(), "intake_exterior", invisible = True)
  show_transformed (intake_CPAP_cover, "intake_CPAP_cover", invisible = True)
  show_transformed (intake_flat_cover, "intake_flat_cover", invisible = True)'''
  save ("intake_solid", Solid (Shell (
    Face (intake_interior.surface),
    Face (intake_exterior.surface),
    intake_CPAP_cover,
    intake_flat_cover,
  )).complemented())


preview (upper_side_rim, lower_side_rim, intake_solid)

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
    angle = math.atan2(relevant_difference.length(), from_focus.length())
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
  distance = offset.length()
  paper_radians = flat_approximate_angle (surface)
  result = vector (
    distance*math.cos(paper_radians),
    distance*math.sin (paper_radians))
  return (surface, result)
def segments (vertices):
  result = []
  for (a,b), (c,d) in zip (vertices [: -1], vertices [1:]):
    original = (a.position - c.position).length()
    derived = (b - d).length()
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

elastic_tube_border_width = 12

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
    
    for index, (rim_position, rim_curvature) in enumerate(rim_samples):
      piece = RimHeadClothPiece()
      piece.rim_source = rim_position
      head_parameter = head_curve.parameter (piece.rim_source)
      piece.head_source = head_curve.value (head_parameter)
      source_diff = piece.head_source - piece.rim_source
      source_diff_direction = source_diff.normalized()
      piece.AB_length = source_diff.length()
      
      if len(self.pieces) == 0:
        piece.rim_output = vector()
        piece.head_output = vector(piece.AB_length, 0)
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
        
        previous_output_direction = (previous.head_output - previous.rim_output).normalized()
        previous_output_perpendicular = vector(-previous_output_direction[1], previous_output_direction[0])
        piece.rim_output = previous.rim_output + previous_output_direction*dA0 + previous_output_perpendicular*dA1
        piece.head_output = previous.head_output + previous_output_perpendicular*dB1
      
      output_diff = piece.head_output - piece.rim_output
      output_direction = output_diff.normalized()
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
      if debug_display:
        if index % debug_display_rate == 0 or index == len(rim_samples) - 1:
          Part.show(Part.Compound([Part.LineSegment(piece.head_output, piece.rim_output).toShape(), Part.LineSegment(piece.head_source, piece.rim_source).toShape()]))
        
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
    1/((1/sample.curve.curvature(sample.curve_parameter))
      + min_wall_thickness*sample.normal_in_plane_unit_height_from_shield.length())
  )
      

forehead_top_curve = forehead_curve.translated(vector(0,0,headband_top - forehead_curve.StartPoint[2]))
forehead_cloth = RimHeadCloth(
  (top_outer_rim_sample(sample) for sample in curve_samples (shield_top_curve, math.floor(shield_top_curve_length * 2), shield_top_curve_length/2, top_hook_front.curve_distance)),
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
neck_y = shield_back - 20 #5
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
#neck_points = [vector(a[0], a[1] + a[2]*0.2, a[2]) for a in neck_points] 
neck_points = neck_points + [vector(-a[0], a[1], a[2]) for a in reversed(neck_points)]

degree = 3
neck_curve = Part.BSplineCurve()
neck_curve.buildFromPolesMultsKnots(
  neck_points,
  mults = [degree+1] + [1]*(len(neck_points) - degree - 1) + [degree+1],
  degree = degree,
)
show_transformed(neck_curve.toShape(), "neck_curve", invisible = True)


chin_cloth_lip_subdivisions = 500
chin_cloth_lip_length = chin_cloth_lip.length()
chin_cloth = RimHeadCloth(
  ((chin_cloth_lip.value (parameter), chin_cloth_lip.curvature (parameter)) for parameter in (chin_cloth_lip.parameterAtDistance (index*chin_cloth_lip_length/(chin_cloth_lip_subdivisions-1)) for index in range(chin_cloth_lip_subdivisions))),
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

whole_headband = Part.Compound ([headband, forehead_elastic_guides] + reflected (temple_block) + reflected (forehead_hook))
show_transformed (whole_headband, "whole_headband", invisible=pieces_invisible)

whole_top_rim = Part.Compound ([top_rim] + reflected (top_pegs[0]) + reflected (top_pegs[1]) + reflected (top_hook))
show_transformed (whole_top_rim, "whole_top_rim", invisible=pieces_invisible)

upper_side = Part.Compound ([upper_side_rim, upper_side_rim_lower_block, upper_side_rim_upper_block, side_hook])
show_transformed (upper_side, "upper_side", invisible=pieces_invisible)

lower_side = Part.Compound ([lower_side_rim, lower_side_extra_lip, intake_solid] + reflected (lower_rim_block) + reflected (side_joint_peg))
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

  
  
  
  