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
– Eventually, the temple joint deformed (wasn't strong enough)


Additional notes after (never-completed) prototype #4:
– the temple joint needs reinforcing to prevent the upper side rim bending forwards and backwards
– the "flex but don't twist" wave got in the way of plugging the upper side ran into its whole (let's just plug it lower down)
– the upper side rim needs reinforcing to prevent it from twisting
– the side joint likewise needs to be reinforced to prevent twisting (once the upper side is no longer the weakest point)
– one of the forehead elastic hooks broke; also it would be nice to have "flex but don't twist" across the whole forehead, so maybe give up on the elastic hooks and just put the elastic on the human forehead again
– the chin positioning wasn't quite right; with the most comfortable headband position, I measured the shield around 19mm in front of my chin instead of the target 10mm.
– the overhead strap needs to be stopped from wobbling side to side
– the CPAP grabber was no good (you can't put the mask on while holding both hoses to the back of the head, and also it was unhelpful and thence the overhead strap all over the place); probably just get rid of it and rely on the mask stiffness to handle the hoses
– the hook and loop fasteners stick to your hair if you're not careful, and also a normal person might put them on wrong; try making a plastic valley around the hooks to help with these
– for my headphones, it might be nice to have the CPAP intakes about 5mm lower, but I think that might bump into my shoulders too much.

main things that need attention now: temple/upper side reinforcing; hook and loop valley; overhead strap wobble




Additional notes after prototype #5:
– we had some plastic deformation issues:
– – at the top of the 3 ridges at the front of the overhead strap (this was just some sort of 3D printing artifact)
– – between the overhead strap slots in the back (I had worried about this, but it seems practical to address by just stiffening it more
– The chin cloth piece came out a little too small (I slightly messed up cutting/sewing it, but I should investigate whether there's a design problem as well). Likewise, the forehead cloth ended up SLIGHTLY too small, leaking a little at my forehead. (That one was because it didn't account for the foam thickness.) And the shield was visible around the bottom edge, also because of the foam thickness.
– the rear overhead strap slot was too stiff (you could damage the strap while trying to insert it, and it was hard to adjust by just one tick at a time)
– thanks to the foam taking up space, the head sizing needs to be adjusted
– we got some fogging at the bottom in outdoor temperatures below 70F; it seems that the air is blown in at a position significantly above the place you exhale to, so the exhale target gets to remain moist
– after 3 month of use, the headband snapped under moderate leverage where it meets the left triangle block (only the flat part snapped, the wave didn't, and then I glued it back together)



Additional notes after prototype #6:
– The side hook isn't printable as-is; let's replace it with a nub
– The top hook should be moved closer to the temple (not a new issue); maybe we can use the same nub for both?
– The elastic doesn't exert enough torque on the temple block to resist the face shield torquing it the other way (by trying to flatten); this can probably be fixed by moving the elastic attachpoint away from the head along the x axis
– It was practical to wear with a bike helmet, but that means wearing it about a centimeter farther down than I usually do, which means the shield is significantly farther away from my face (due to both shield_focal_slope and the slope of my forehead). My particular bike helmet dips down at the temples, pushing the temple block down but not requiring the forehead to move, so the mask is slanted in a way that moves the shield even further from the face. The quick fix is to just change putative_chin, making the mask smaller. A fancier solution could theoretically move the temple block downwards in normal usage, allowing the front headband to be higher up than the temple block (and making the top edge of the face shield be a more complex curve). The headband also digs into my forehead a bit more this way because the forehead is shaped differently down there on the eyebrows; I'm not worried about this for the moment.

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
headband_width = 10
overhead_strap_width = headband_width
headband_cut_radius = 25
cloth_with_elastic_space = 3
forehead_point = Origin
headphones_front = forehead_point[1]-75
#side_plate_width = max(min_wall_thickness + shield_glue_face_width, elastic_holder_depth)
#shield_back = headphones_front + side_plate_width - shield_glue_face_width
shield_back = headphones_front #+ min_wall_thickness
back_edge = forehead_point[1] - 96
putative_chin = forehead_point + vector (0, -9, -135)
rim_bottom_z = -165 - shield_glue_face_width # experimentally measured -165 as the approximate invisible position; subtracting shield_glue_face_width isn't exactly the right formula, but it's an arbitrary number anyway
glasses_point = forehead_point + vector (66, 0, -10)
putative_eyeball = forehead_point + vector (35, -15, -35)
air_target = putative_chin + Up*40

contact_leeway = 0.4
ridge_thickness = 2

temple_radians = (math.tau/4) * 0.6
shield_focal_slope = 1.8
lots = 500

min_head_circumference = 500
max_head_circumference = 650
min_overhead_strap_length = 250
fastener_hook_length = 40
fastener_hook_skirt_width = 10
fastener_loop_extra_width = 4


########################################################################
########  Generalized cone definitions  #######
########################################################################



temple_direction = Right@Rotate (Up, radians = temple_radians)
temple = Point (77, shield_back, 0)

shield_focal_y = temple[1] - (temple[0] * temple_direction[1] / temple_direction[0])


shield_source_peak = putative_chin + vector (0, 10, 0)
shield_focal_point = Point (0, shield_focal_y, shield_source_peak[2] + (shield_focal_y - shield_source_peak[1]) * shield_focal_slope)

above_temple = temple + vector (0, 0, shield_glue_face_width)
def projected_to_top (point):
  return point.projected (
    Plane (above_temple, Up),
    by = Direction (shield_focal_point, point)
  )

shield_source_curve_points = [
  above_temple,
  projected_to_top (glasses_point + vector (15, 25, 0)),
  projected_to_top (shield_source_peak),
]

shield_source_curve_points = shield_source_curve_points + [v@Reflect (Right) for v in reversed (shield_source_curve_points[:-1])]
shield_source_curve_points.reverse()
save ("shield_source_curve", Interpolate (shield_source_curve_points, tangents = [Vector (temple_direction)@Reflect (Right), Vector (temple_direction)@Reflect (Origin)]))


shield_source_curve_length = shield_source_curve.length()




def scaled_shield_source_curve(z):
  return [pole@Scale (
    (shield_focal_point [2]-z)/shield_focal_point [2],
    center = shield_focal_point
  ) for pole in shield_source_curve.poles()]

save ("shield_surface", BSplineSurface (
  [
    scaled_shield_source_curve (rim_bottom_z - 5),
    scaled_shield_source_curve (20),
  ],
  u = BSplineDimension (degree = 1),
  v = BSplineDimension (knots = shield_source_curve.knots(), multiplicities = shield_source_curve.multiplicities())
))
    
save ("shield_source_points", Compound ([Vertex (point) for point in shield_source_curve_points]))

print (f"Shield position directly in front of chin: {shield_surface.intersections (Line(putative_chin, Back)).point()}")

shield_bottom_peak = shield_surface.intersections (Line(Point(0,0,rim_bottom_z), Back)).point()

class ShieldCurveInPlane(SerializeAsVars):
  def __init__(self, plane):
    self.plane = plane
    self.curve = shield_surface.intersections (plane).curve()
    
  def __getattr__(self, name):
    return getattr(self.curve, name)

side_curve_source_points = [
  Point (0, shield_back, shield_glue_face_width),
  Point (0, shield_back, -55),
  Point (0, shield_bottom_peak[1]+0.001, shield_bottom_peak[2])
]

save ("side_curve_source_surface", BSplineSurface([
    [point + Left*100 for point in side_curve_source_points],
    [point + Right*100 for point in side_curve_source_points],
  ],
  BSplineDimension (degree = 1),
  BSplineDimension (degree = 1),
))

upper_side_curve_source_points = side_curve_source_points[0:2]
upper_side_curve_source_points[1] = upper_side_curve_source_points[1] + Down*25
save ("upper_side_curve_source_surface", BSplineSurface([
    upper_side_curve_source_points,
    [point + Right*100 for point in upper_side_curve_source_points],
  ],
  BSplineDimension (degree = 1),
  BSplineDimension (degree = 1),
))

save ("lower_side_curve_source_surface", BSplineSurface([
    [point + Left*100 for point in side_curve_source_points[1:3]],
    [point + Right*100 for point in side_curve_source_points[1:3]],
  ],
  BSplineDimension (degree = 1),
  BSplineDimension (degree = 1),
))

save ("lower_side_curve_inner_plane", Plane (lower_side_curve_source_surface.value (0, 0) + lower_side_curve_source_surface.normal (0, 0)*shield_glue_face_width, lower_side_curve_source_surface.normal (0, 0)))

@run_if_changed
def make_shield_curves():
  save ("shield_side_curve", shield_surface.intersections (
    side_curve_source_surface
  ).curve())
  save ("shield_upper_side_curve", ShieldCurveInPlane(upper_side_curve_source_surface))
  save ("shield_lower_side_curve", ShieldCurveInPlane(lower_side_curve_source_surface))
  save ("shield_lower_side_inner_curve", ShieldCurveInPlane(lower_side_curve_inner_plane))
  
  save ("shield_top_curve", ShieldCurveInPlane(Plane(Point (0,0,shield_glue_face_width), Up)))
  
shield_side_curve_length = shield_side_curve.length()

shield_top_curve_length = shield_top_curve.length()



save ("glasses_vertex", Vertex (glasses_point))
diff = Direction (glasses_point - shield_focal_point)
save ("glasses_edge", Edge (glasses_point + diff*180, glasses_point - diff*180))




class ShieldSample(SerializeAsVars):
  def __init__(self, parameter = None, closest = None, intersecting = None, which = 0):
    if intersecting is not None:
      closest = shield_surface.intersections (intersecting).points [which]
    if closest is not None:
      self.shield_parameter = shield_surface.parameter(closest)
    elif parameter is not None:
      self.shield_parameter = parameter
    else:
      raise RuntimeError ("didn't specify how to initialize ShieldSample")
    
    self.position = shield_surface.value(self.shield_parameter)
    self.normal = shield_surface.normal(self.shield_parameter)


class CurveSample (ShieldSample):
  def __init__(self, curve, distance = None, closest = None, y = None, z = None, which = 0, intersecting = None):
    if y is not None:
      intersecting = Plane (Point(0,y,0), Front)
    if z is not None:
      intersecting = Plane (Point(0,0,z), Up)
    if intersecting is not None:
      closest = curve.intersections (intersecting).points [which]
    
    if distance is not None:
      self.curve_distance = distance
      self.curve_parameter = curve.parameter(distance = distance)
    elif closest is not None:
      self.curve_parameter = curve.parameter(closest = closest)
      self.curve_distance = curve.length(0, self.curve_parameter)
    else:
      raise RuntimeError ("didn't specify how to initialize CurveSample")
    
    derivatives = curve.derivatives(self.curve_parameter)
    super().__init__(closest = derivatives.position)
    
    self.curve_tangent = derivatives.tangent
    self.curve_normal = derivatives.normal
    self.curve_in_surface_normal = Direction (self.curve_tangent.cross (self.normal))
    
    if isinstance(curve, ShieldCurveInPlane):
      self.plane_normal = curve.plane.normal(0,0) # note: the plane is actually a BSplineSurface, so we need to give the parameters
      self.normal_in_plane = Direction (-self.normal.cross(self.plane_normal).cross(self.plane_normal))
      
      self.normal_in_plane_unit_height_from_shield = self.normal_in_plane/self.normal_in_plane.dot(self.normal)
      self.curve_in_surface_normal_unit_height_from_plane = self.curve_in_surface_normal/abs (self.curve_in_surface_normal.dot(self.plane_normal))
    
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
########  Eye lasers  #######
########################################################################


def eye_laser(direction):
  try: 
    sample = ShieldSample(intersecting = TrimmedCurve(Line (putative_eyeball, direction), 0, lots))
    further_direction = direction@Reflect (sample.normal)
    return Wire (putative_eyeball, sample.position, sample.position + further_direction*200)
  except IndexError:
    return Wire (putative_eyeball, putative_eyeball + direction*200)
    
@run_if_changed
def make_eye_lasers():
  save ("eye_lasers", Compound ([
    eye_laser(Direction (x, 1, z))
    for x in subdivisions (-2, 2, amount = 10)
    for z in subdivisions (-2, 2, amount = 10)
  ]))

########################################################################
########  Forehead/headband/top rim  #######
########################################################################

headband_top = shield_glue_face_width + min_wall_thickness
headband_bottom= headband_top - headband_width
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
degree = 3
standard_forehead_poles = [a@Mirror (Right) for a in reversed(standard_forehead_points[1:-1])] + standard_forehead_points
save ("standard_forehead_curve", BSplineCurve(
  standard_forehead_poles,
  BSplineDimension (periodic = True),
))
print(f"Standard forehead circumference: {standard_forehead_curve.length()}")

overhead_strap_points = [forehead_point + vector(0,a,b) for a,b in [
  (0, headband_bottom),
  (-2, 10),
  (-4, 21),
  (-22, 50),
  (-70, 75),
  (-125, 75),
  (-173, 60),
  (-191, 21),
  (-195, 0),
  (-195, -50),
  (-186, -102),
]]

save ("overhead_strap_curve", BSplineCurve(overhead_strap_points))

def flat_to_headband(shape):
  return (shape@Translate (Up*headband_top)).extrude (Down*headband_width)

@run_if_changed
def make_standard_headband():
  standard_headband_2D = Offset2D(Wire (Edge (standard_forehead_curve)), headband_thickness, fill = True)
  save ("standard_headband_2D", standard_headband_2D)

  standard_headband = flat_to_headband(standard_headband_2D)
  save("standard_headband", standard_headband)


head_variability = max_head_circumference - min_head_circumference
fastener_loop_length = fastener_hook_length + head_variability
'''
for someone with the maximum head circumference, the fastener hooks will be lined up with the very end of the fastener loops on the other end of the headband; this still leaves 1 degree of freedom (how far to the left or right, on the back of the head, that position would be)

I'm initially assuming that the fastener hooks will be at the center of the back of the head on an average head (further right on a smaller head, further left on a larger head).

Also, all users must have the slots for the overhead strap be able to be in the middle of the back of the head; for maximum sized heads, the rightmost slot would be exactly in the center. If we don't want to make the headband any longer than needed, we actually want to put the fastener hooks all the way at the right end of the slots, meaning that, if they are shorter than the slots, they would be significantly to the right of the back on the average head. That's okay.
'''
fastener_loop_width = headband_width + fastener_loop_extra_width
overhead_strap_slots_width = head_variability + overhead_strap_width
headband_left_length = max_head_circumference/2 + overhead_strap_width/2
headband_right_length = (max_head_circumference + fastener_hook_length + fastener_hook_skirt_width) - headband_left_length

def curled_forehead_points(total_distance, offset_distance):
  result = []
  class CurlStep(object):
    pass
  
  previous = None
  start = standard_forehead_curve.length(0, standard_forehead_curve.parameter (closest = forehead_point))
  temple_distance = standard_forehead_curve.length(0, standard_forehead_curve.parameter (closest = temple))
  circle_center = forehead_point + Front*80
  for distance in subdivisions (start, temple_distance, max_length = 5):
    step = CurlStep()
    step.curve_distance = distance
    parameter = standard_forehead_curve.parameter (distance = distance)
    derivatives = step.derivatives = standard_forehead_curve.derivatives (parameter)
    if previous is None:
      step.output_position = derivatives.position
      step.total_radians_change = 0
    else:
      offset = Vector (previous.derivatives.position, derivatives.position)
      tangent_distance = derivatives.tangent.dot(previous.derivatives.tangent)
      normal_distance = derivatives.tangent.dot(previous.derivatives.normal)
      observed_radians = math.atan2(normal_distance, tangent_distance)
      current_adjusted_tangent = derivatives.tangent@Rotate(Up, radians = previous.total_radians_change)
      target_curvature_change = -0.0005
      target_radians_change = (distance - previous.curve_distance)*target_curvature_change
      # if uncurling, arbitrarily restrict it from becoming straight or inverted; not sure if there's an actual need for this
      radians_change = min(target_radians_change, observed_radians*0.8)
      step.total_radians_change = previous.total_radians_change + radians_change
      step.output_position = previous.output_position + offset@Rotate (Up, radians = step.total_radians_change)
    result.append (step.output_position)
    previous = step
  
  point = previous.output_position
  counterpoint = previous.output_position@Reflect (Right) + Left*offset_distance*2
  curve = Interpolate ([
      point,
      Between (point, counterpoint, 0.25) + Front*(105 + offset_distance),
      Between (point, counterpoint) + Front*(115 + offset_distance),
      Between (point, counterpoint, 0.75) + Front*(105 + offset_distance),
      counterpoint
    ],
    tangents = [Vector (current_adjusted_tangent), Vector (current_adjusted_tangent@Reflect (Front))])
  for distance in subdivisions (0, total_distance - (temple_distance - start), max_length = 5)[1:]:
    parameter = curve.parameter (distance = distance)
    assert(parameter < curve.LastParameter())
    result.append (curve.value(parameter))
  
  return result

@run_if_changed
def make_curled_forehead():
  curled_forehead_poles = [a@Mirror (Right) for a in reversed(
  curled_forehead_points(headband_left_length, 5)[1:])] + curled_forehead_points(headband_right_length, -5)
  save("large_forehead_curve", BSplineCurve(
    curled_forehead_poles,
  ))

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
    
  


@run_if_changed
def make_curled_headband():
  wire = Wire(Edge(large_forehead_curve))
  shifted = Offset2D(wire, -min_wall_thickness/2, open=True)
  expanded = Face(Offset2D(shifted, min_wall_thickness/2))
  solid = flat_to_headband(expanded)
  
  def fastener_part(a, b):
    curve = TrimmedCurve (large_forehead_curve, a, b)
    wire = Wire (Edge (curve))
    shifted = Offset2D(wire, -min_wall_thickness/2, open=True)
    expanded = Face(Offset2D(shifted, min_wall_thickness/2))
    return (expanded@Translate (Up*headband_top)).extrude (Down*fastener_loop_width)
  save("curled_headband", Compound (
    solid,
    fastener_part(large_forehead_curve.parameter (distance = large_forehead_curve.length() - fastener_loop_length), large_forehead_curve.LastParameter()),
    fastener_part(0, large_forehead_curve.parameter (distance = fastener_hook_length + fastener_hook_skirt_width*2))),
  )

@run_if_changed
def make_hook_skirt():
  sections = []
  for distance in subdivisions (0, fastener_hook_length + fastener_hook_skirt_width*2, amount = 20):
    derivatives = large_forehead_curve.derivatives (distance = distance)
    sections.append (Wire ([derivatives.position + Up*headband_top + a for a in [
      (Up - derivatives.normal)*fastener_hook_skirt_width,
      Vector(0,0,0),
      Down*fastener_loop_width,
      Down*fastener_loop_width + (Down - derivatives.normal)*fastener_hook_skirt_width
    ]]).offset2D (min_wall_thickness/2))
    
  save("hook_skirt", Loft(sections, solid =True))

ridge_slot_width = overhead_strap_width*2.5
def ridge_slot(curve, start, finish, *, direction, top, bottom, wall_adjust=0, prong_side = 0):
  middle = (start + finish)/2
  positions = subdivisions (-ridge_slot_width/2, ridge_slot_width/2, amount = 7)
  fractions = [0, 1, 1, 1, 1, 1, 0]
  controls = []
  def augmented_derivatives(offset):
    derivatives = curve.derivatives (distance = middle + offset)
    derivatives.adjusted_normal = derivatives.tangent@Rotate (Up, degrees = 90*direction)
    derivatives.adjusted_position = derivatives.position + derivatives.adjusted_normal*wall_adjust
    return derivatives
  position_derivatives = [augmented_derivatives(position) for position in positions]
  control_offset_distance = min_wall_thickness + ridge_thickness + contact_leeway*2 + 0.2
  for derivatives, fraction in zip (position_derivatives, fractions):
    controls.append (derivatives.adjusted_position + derivatives.adjusted_normal*fraction*control_offset_distance)
  slot_curve = BSplineCurve (controls)
  slot = Wire (Edge (slot_curve))
  slot = Face (Offset2D (slot, min_wall_thickness/2))
  slot = (slot@Translate(Up*bottom)).extrude (Up*(top - bottom))
  prong = Edge (position_derivatives[2].adjusted_position, position_derivatives [-3].adjusted_position)
  middle_derivatives = position_derivatives [len (position_derivatives)//2]
  prong_length = min_wall_thickness/2 + ridge_thickness - min_wall_thickness
  prong = prong.extrude (middle_derivatives.adjusted_normal*prong_length).extrude (Up*1.5*math.copysign(1, top - bottom))
  prong = prong@Translate (Up*bottom)
  if prong_side == 1:
    prong = prong@Translate (middle_derivatives.adjusted_normal*(control_offset_distance - prong_length))
  guides = []
  for side in [-1, 1]:
    derivatives = augmented_derivatives(side*(overhead_strap_width/2 + contact_leeway))
    points = [
      derivatives.adjusted_position,
      #slot_curve.intersections(Line (derivatives.adjusted_position, derivatives.adjusted_normal)) [0]
      slot_curve.intersections (Plane (derivatives.adjusted_position, derivatives.tangent)).point()
    ]
    if prong_side == 1:
      points.reverse()
    delta = points [1] - points [0]
    space = min_wall_thickness*1.5 if prong_side == 0 else min_wall_thickness*2
    guide_flat = Edge (points [1], points [0] + Direction (delta)*space).extrude (derivatives.tangent*side*min_wall_thickness)
    guides.append ((guide_flat@Translate(Up*bottom)).extrude (Up*(top - bottom)))
    
  return Compound(slot, prong, guides)

@run_if_changed
def make_headband_3():
  overhead_strap_slots = []
  for start, finish in pairs (subdivisions (0, overhead_strap_slots_width, max_length = overhead_strap_width*3)):
    overhead_strap_slots.append (ridge_slot(large_forehead_curve, start, finish, direction = -1, wall_adjust = -min_wall_thickness/2, top = headband_bottom, bottom = headband_top))
  save ("overhead_strap_slots", Compound (overhead_strap_slots))
  
'''overhead_strap_slot_test_region = flat_to_headband(Face(Wire(Edge(Circle (Axes (Point (47, -198, 0), Up), 20)))))
save ("overhead_strap_slot_test", Intersection (
  Compound (overhead_strap_slots, curled_headband, ),
  overhead_strap_slot_test_region, 
))
save_STL ("overhead_strap_slot_test", overhead_strap_slot_test)
preview (overhead_strap_slot_test)
#preview (large_forehead_curve, curled_headband, curled_headband_wave, standard_headband_2D, overhead_strap_slots)'''

def overhead_strap_ridges_face(start, finish):
  ridge_points = []
  ridge_back_points = []
  for index, ridge_distance in enumerate (subdivisions (start, finish, max_length = 2, require_parity = 1)):
    derivatives = overhead_strap_curve.derivatives (distance = ridge_distance)
    offset = (min_wall_thickness/2) if index % 2 == 0 else (ridge_thickness - min_wall_thickness/2)
    ridge_points.append (derivatives.position - derivatives.normal*offset)
    ridge_back_points.append (derivatives.position)
  return Face(Wire(ridge_points + ridge_back_points[::-1], loop=True))


print("Overhead strap curve length:", overhead_strap_curve.length())
@run_if_changed
def make_overhead_strap():
  strap_face = Face(Offset2D(Wire(Edge(overhead_strap_curve)), min_wall_thickness/2))
  combined_face = Union(
    strap_face,
    overhead_strap_ridges_face(min_overhead_strap_length, overhead_strap_curve.length()),
    overhead_strap_ridges_face(0, headband_width*1.2),
  )
  save ("overhead_strap", combined_face.extrude(Right*overhead_strap_width, centered = True))

'''save ("overhead_strap_test", Intersection (
  overhead_strap,
  Face(Wire(Edge(Circle (Axes (overhead_strap_points[-2], Right), 15)))).extrude(Right*20, centered=True)
))
save_STL ("overhead_strap_test", overhead_strap_test)
preview(overhead_strap_test)'''

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
  
  top_rim = Loft ([wire@Mirror (Right) for wire in reversed (top_rim_hoops[1:])] + top_rim_hoops, solid = True)
  sample = CurveSample (shield_upper_side_curve, z=0)
  cut = Box (Point(0, -lots, -lots), Point(lots, lots, lots)).intersection(HalfSpace (
    sample.position - sample.curve_in_surface_normal*(shield_glue_face_width + contact_leeway),
    sample.curve_in_surface_normal
  ))
  
  save ("top_rim", Difference(top_rim, [cut, cut@Reflect (Right)]))



'''
CPAP_grabber_length = 16
@run_if_changed
def make_CPAP_grabber():
  main_circle_radius = CPAP_hose_helix_outer_radius - 2 + min_wall_thickness/2
  min_parameter = math.tau/16
  main_arc = TrimmedCurve (Circle (Axes (Origin, Up, Front), main_circle_radius), min_parameter, math.tau - min_parameter)
  derivatives = main_arc.derivatives (min_parameter)
  # we want: radius - (outward normal[0]*radius) = x - min_wall_thickness/2 - space/2
  space = 1.5
  side_arc_radius = (derivatives.position [0] - min_wall_thickness/2 - space/2) / (1 + derivatives.normal[0])
  side_arc = TrimmedCurve (Circle (Axes (derivatives.position - derivatives.normal*side_arc_radius, Up, Right), side_arc_radius), math.tau/4 + min_parameter, math.tau*6/8)
  curves = [
    side_arc,
    main_arc,
    side_arc@Reflect (Right)
  ]
  CPAP_grabber_wire = Wire (curves)
  CPAP_grabber_solid = Face (CPAP_grabber_wire.offset2D (min_wall_thickness/2)).extrude (Up*CPAP_grabber_length)
  # hack - instead of a strictly straight line, disambiguate a plane
  joining_curve = BSplineCurve ([
    Point (- main_circle_radius, main_circle_radius, 0),
    Point (0, main_circle_radius+0.1, 0),
    Point (main_circle_radius, main_circle_radius, 0),
  ], BSplineDimension (degree = 2))
  slot = ridge_slot (joining_curve, 0, joining_curve.length(), direction=1, bottom = 0, top = CPAP_grabber_length)
  joining_solid = Face (Edge(joining_curve).offset2D (min_wall_thickness/2)).extrude (Up*CPAP_grabber_length)
  CPAP_grabber_assembled = Compound ([
    CPAP_grabber_solid@Translate (Right*main_circle_radius),
    CPAP_grabber_solid@Translate (Left*main_circle_radius),
    joining_solid,
    slot,
  ])
  save("CPAP_grabber", CPAP_grabber_assembled)
  save_STL("CPAP_grabber", CPAP_grabber_assembled)'''



temple_block_length = 36
temple_block_start_distance = standard_forehead_curve.distance (closest = temple)-1

@run_if_changed
def make_temple_block():
  temple_block_inside = []
  temple_block_top = []
  temple_block_bottom = []
  
  for distance in range (temple_block_length + 1):
    temple_block_inside.append (standard_forehead_curve.value (distance = temple_block_start_distance - distance))
    sample = CurveSample(shield_top_curve, distance = shield_top_curve_length-distance*1.1)
    
    foo = sample.position
    temple_block_top.append(foo + sample.curve_in_surface_normal_unit_height_from_plane*min_wall_thickness)
    temple_block_bottom.append(foo + sample.curve_in_surface_normal_unit_height_from_plane*(min_wall_thickness - headband_width))
  temple_block_hoops = [
    Wire(temple_block_top + [Point(a[0], a[1], temple_block_top[0][2]) for a in reversed(temple_block_inside)], loop = True), 
    Wire(temple_block_bottom + [Point(a[0], a[1], temple_block_bottom[0][2]) for a in reversed(temple_block_inside)], loop = True), 
  ]
  temple_block = Loft(temple_block_hoops, solid = True)
  save ("temple_block", temple_block)

standard_middle_distance = standard_forehead_curve.distance (closest = forehead_point)
curled_middle_distance = large_forehead_curve.distance (closest = forehead_point)
temple_block_from_middle_distance = temple_block_start_distance - standard_middle_distance
curled_temple_block_distance = curled_middle_distance + (temple_block_from_middle_distance)



@run_if_changed
def make_forehead_overhead_strap_joint():
  save("forehead_overhead_strap_joint", ridge_slot(large_forehead_curve, curled_middle_distance-20, curled_middle_distance+20, direction = 1, wall_adjust = min_wall_thickness/2, top = headband_bottom, bottom = headband_top, prong_side = 1))

  
@run_if_changed
def make_headband_wave():
  faces = Compound(
    forehead_wave(temple_block_start_distance + 16, temple_block_start_distance),
    forehead_wave(temple_block_start_distance - temple_block_length, standard_middle_distance - (temple_block_from_middle_distance - temple_block_length)),
    forehead_wave(standard_middle_distance - temple_block_from_middle_distance, standard_middle_distance - temple_block_from_middle_distance - 16),
  )
  save("standard_headband_wave", flat_to_headband(faces))

@run_if_changed
def make_curled_headband_wave():
  faces = Compound(
    forehead_wave(fastener_hook_length + 80, curled_middle_distance - temple_block_from_middle_distance),
    forehead_wave(curled_middle_distance - (temple_block_from_middle_distance - temple_block_length), curled_middle_distance - ridge_slot_width/2),
    forehead_wave(curled_middle_distance + ridge_slot_width/2, curled_middle_distance + (temple_block_from_middle_distance - temple_block_length)),
    forehead_wave(curled_middle_distance + temple_block_from_middle_distance, large_forehead_curve.length() - (fastener_loop_length - fastener_hook_length)),
  )
  save("curled_headband_wave", flat_to_headband(faces))
  
########################################################################
########  Side rim and stuff #######
########################################################################


def upper_side_lip_tip(sample):
  return sample.position - sample.plane_normal*min_wall_thickness + sample.normal_in_plane*min_wall_thickness

upper_side_cloth_lip = []
for sample in curve_samples(shield_upper_side_curve,
    0,
    CurveSample (shield_upper_side_curve, z = side_curve_source_points [1][2]).curve_distance,
    amount = 20):
  upper_side_cloth_lip.append (sample.position)
  
def augment_lower_curve_sample(sample):
  sample.lip_direction = Direction (-sample.plane_normal + sample.normal_in_plane*1.5)
  sample.lip_direction_unit_height_from_shield = sample.lip_direction/sample.lip_direction.dot(sample.normal)
  sample.curve_in_surface_normal_unit_height_from_lip = sample.curve_in_surface_normal/sample.curve_in_surface_normal.cross(sample.lip_direction).length()
  sample.lip_tip = sample.position + min_wall_thickness*sample.curve_in_surface_normal_unit_height_from_lip + sample.lip_direction_unit_height_from_shield*min_wall_thickness

@run_if_changed
def make_lower_side_rim():
  lower_side_rim_hoops = []
  for sample in curve_samples(shield_lower_side_curve, amount = 40):
    augment_lower_curve_sample(sample)
    lower_side_rim_hoops.append(Wire([
      sample.position,
      sample.position - shield_glue_face_width*sample.curve_in_surface_normal_unit_height_from_plane,
      sample.position - shield_glue_face_width*sample.curve_in_surface_normal_unit_height_from_plane - sample.normal_in_plane_unit_height_from_shield*min_wall_thickness,
      sample.lip_tip - sample.normal_in_plane_unit_height_from_shield*min_wall_thickness*2,
      sample.lip_tip,
      sample.position + sample.lip_direction_unit_height_from_shield*min_wall_thickness,
    ], loop = True))
  lower_side_rim = Loft (lower_side_rim_hoops, solid = True)
  save ("lower_side_rim", lower_side_rim)

@run_if_changed
def make_elastic_tension():
  #side_plate_hoops = []
  elastic_tension_hoops = []
  for sample in curve_samples(shield_side_curve, amount = 79):
    elastic_tension_hoops.append (Edge (sample.position, sample.position + sample.curve_normal*10))         

  save("elastic_tension", Compound (elastic_tension_hoops))

  
#print(shield_upper_side_curve.plane)
  
@run_if_changed
def make_side_joint():
  def side_peg (sample, length):
    return Edge (
      sample.position - (shield_glue_face_width - 4)*sample.curve_in_surface_normal_unit_height_from_plane,
      sample.position - (shield_glue_face_width)*sample.curve_in_surface_normal_unit_height_from_plane
    ).extrude (-sample.normal_in_plane*length).extrude (sample.curve_tangent*3, centered = True)
  
  side_pegs = [side_peg(sample, length) for length, sample in zip([4, 7], curve_samples (shield_lower_side_curve, 10, 24, amount = 2))]
  save ("side_peg_holes", Compound ([Solid(Offset(a, contact_leeway)) for a in side_pegs]))
  save ("side_pegs", Compound (side_pegs))
  


@run_if_changed
def make_temple_block_pegs():  
  def top_peg (sample):
    return Edge (
      sample.position - (stiffer_wall_thickness - min_wall_thickness + contact_leeway)*sample.curve_in_surface_normal_unit_height_from_plane,
      sample.position - (shield_glue_face_width)*sample.curve_in_surface_normal_unit_height_from_plane
    ).extrude (-sample.normal_in_plane*10).extrude (sample.curve_tangent*3, centered = True)
  
  top_pegs = [top_peg(sample) for sample in curve_samples (shield_top_curve, shield_top_curve_length - 14, shield_top_curve_length - temple_block_length + 2, amount = 2)]
  
  save ("temple_top_pegs", Compound (top_pegs))
  save ("top_peg_holes", Compound ([Solid(Offset(a, contact_leeway)) for a in top_pegs]))
  


@run_if_changed
def make_upper_side_rim():
  upper_side_rim_hoops = []
  top_curve_start = putative_eyeball [2] + 15
  forehead_exclusion = Face(standard_forehead_curve).extrude(Down*lots, centered=True)
  forehead_size = standard_forehead_curve.value (closest = temple) [0]
  for sample in curve_samples(shield_upper_side_curve, amount = 20):
    glue_width = shield_glue_face_width
    highness = (sample.position [2] - top_curve_start)/(headband_top - top_curve_start)
    if highness > 0:
      glue_width += 30 * (1 - math.sqrt(1 - highness**2))
    front_edge = sample.position - glue_width*sample.curve_in_surface_normal
    
    # note: the math for the part at the bottom is a bit inelegant, which will reduce maintainability. Part of the reason for this is that I couldn't use a Loft if I allowed the little shield-holder ridge to be cut off. TODO: improve upon this troublesome thing
    if sample.position [2] < side_curve_source_points [1][2]:
      front_edge = CurveSample (shield_lower_side_inner_curve, intersecting = Plane (sample.position, sample.curve_tangent), which = 1).position
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
  upper_side_rim = upper_side_rim.cut(Face (lower_side_curve_source_surface @ Translate(lower_side_curve_source_surface.normal(0,0)*-(min_wall_thickness+contact_leeway))).extrude (Front*lots))
  
  shield_cut = Face (shield_surface).intersection (HalfSpace (Point (10, 0, 0), Right)).intersection (HalfSpace (temple, Back)).extrude (Right*lots)

  upper_side_rim = upper_side_rim.cut(shield_cut)

  #top_rim_exclusion = Solid(Offset (top_rim, contact_leeway))
  #upper_side_rim = upper_side_rim.cut(top_rim_exclusion)
  #lower_side_rim_exclusion = Solid(Offset (lower_side_rim, contact_leeway))
  #upper_side_rim = upper_side_rim.cut(lower_side_rim_exclusion)
  upper_side_rim = upper_side_rim.cut(top_peg_holes)
  upper_side_rim = upper_side_rim.cut(side_peg_holes)
  save ("upper_side_rim", upper_side_rim)
  

  
  
  

elastic_hook_base_length = 5
elastic_hook_outwards = 6
elastic_hook_forwards = 10

elastic_hook = Face(Wire([
  Point(0,0,0),
  Point(elastic_hook_outwards,elastic_hook_forwards-1.25,0),
  Point(elastic_hook_outwards,elastic_hook_forwards,0),
  Point(0,elastic_hook_base_length,0),
], loop = True)).extrude(vector(0,0,stiffer_wall_thickness))


top_hook_back = CurveSample (shield_top_curve, y= headphones_front+8, which = 1)
save("top_hook_front", CurveSample (shield_top_curve, distance = top_hook_back.curve_distance - elastic_hook_forwards))
top_hook_forwards = Direction (top_hook_front.position - top_hook_back.position)

save("top_hook", elastic_hook @ Transform(top_hook_forwards.cross (vector(0,0,1)), -top_hook_forwards, vector(0,0,-1), top_hook_front.position + vector(0,0,min_wall_thickness)))

save("side_hook", (elastic_hook @ Transform(vector(1,0,0), vector(0,0,1), vector(0,1,0), vector(Origin, temple) + vector(0, 0, headband_top-elastic_hook_forwards + 3))).intersection(HalfSpace(Origin + Up*headband_top, Down)))



  
@run_if_changed
def make_temple_block_on_curled_headband():
  s0 = standard_forehead_curve.value(distance = temple_block_start_distance)
  s1 = standard_forehead_curve.value(distance = temple_block_start_distance - temple_block_length)
  c0 = large_forehead_curve.value(distance = curled_temple_block_distance)
  c1 = large_forehead_curve.value(distance = curled_temple_block_distance - temple_block_length)
  transform = Rotate (
      Axis(s0, Up),
      radians = -Direction(s0,s1).Angle(Direction(c0, c1))
    ) @ Translate (
      s0, c0
    )
  save("temple_block_on_curled_headband", temple_block@transform)
  save("upper_side_rim_on_curled_headband", upper_side_rim@transform)
  save("side_hook_on_curled_headband", side_hook@transform)


#preview(upper_side_rim, lower_side_rim, top_rim, standard_headband, top_hook, side_hook, eye_lasers)

########################################################################
########  Intake  #######
########################################################################

# The thickness of the flat part of the air passage at its thickest point
intake_flat_air_thickness_base = 10.4

# The length, along the side curve, of exterior of the intake wall (this may be a slight overestimate because we will curve the points of the walls a bit)
intake_flat_width = 56

# The width of the opening of the triangular corner the elastic should nestle into
elastic_corner_opening_width = 6

# the thickness of the intake support in the direction normal to the shield
intake_support_thickness = 4
  
def augment_intake_sample(sample):
  sample.along_intake_flat = sample.normal.cross(Up).normalized()
  sample.along_intake_flat_unit_height_from_plane = sample.along_intake_flat/abs (sample.along_intake_flat.dot(sample.plane_normal))
  sample.print_surface_base_point = sample.position - shield_glue_face_width*sample.along_intake_flat_unit_height_from_plane
  
  augment_lower_curve_sample(sample)


@run_if_changed
def make_intake():
  # a base point on the lower side curve, just inside the shield.
  intake_middle = CurveSample(shield_lower_side_curve, z=-110, which=0)
  augment_intake_sample(intake_middle)
  
  # the center of the circle at the far CPAP connector end.
  CPAP_back_center = Point(72, headphones_front - 40, -102)
  
  # a reference point to try to aim the CPAP direction in a way that will make the whole shape smooth.
  intake_flat_back_center_approx = intake_middle.position + (elastic_holder_depth+4)*intake_middle.along_intake_flat_unit_height_from_plane - intake_middle.normal*(min_wall_thickness + intake_flat_air_thickness_base/2) + Up*5
  
  CPAP_forwards = Direction (CPAP_back_center, intake_flat_back_center_approx) #vector(0.2, 1, -0.1).normalized()
  
  lower_side_cloth_lip = []
  lower_side_shield_lip = []
  intake_support_hoops = []
  intake_support_exclusion_hoops = []
  intake_edges = ([], [], [], [])
  
  for sample in curve_samples(shield_lower_side_curve, 1, intake_middle.curve_distance - intake_flat_width/2 - elastic_corner_opening_width, amount = 20):
    augment_intake_sample(sample)
    depth = min(
      elastic_holder_depth/abs (sample.along_intake_flat.dot(sample.plane_normal)),
      (sample.position[1] - headphones_front)/-sample.along_intake_flat[1],
    )
    l = ShieldSample(closest = sample.position + depth*sample.along_intake_flat).position
    lower_side_cloth_lip.append (l)
    lower_side_shield_lip.append (l)
    
    thickness = min(sample.curve_distance / 4, intake_support_thickness)
    b = -sample.normal_in_plane_unit_height_from_shield * thickness
    intake_support_hoops.append (Wire ([
      sample.print_surface_base_point,
      sample.print_surface_base_point + b,
      sample.position + b,
      sample.position,
    ], loop = True))
    a = contact_leeway * sample.normal_in_plane_unit_height_from_shield
    b = b - contact_leeway * sample.normal_in_plane_unit_height_from_shield
    c = contact_leeway * sample.along_intake_flat_unit_height_from_plane
    d = -contact_leeway * sample.curve_tangent
    intake_support_exclusion_hoops.append (Wire ([
      sample.print_surface_base_point + a - c + d,
      sample.print_surface_base_point + b - c + d,
      sample.position + b + c + d,
      sample.position + a + c + d,
    ], loop = True))
  
  
  for sample in curve_samples(shield_lower_side_curve, intake_middle.curve_distance - intake_flat_width/2 + 0.1, intake_middle.curve_distance + intake_flat_width/2 - 0.1, amount = 70):
    augment_intake_sample(sample)
    
    # Get the offset relative to intake_middle:
    offset = sample.curve_distance - intake_middle.curve_distance
    relative_offset = offset / intake_flat_width
    
    # now, compute the shape of innermost edge (closest to the face), in the form of a height from the shield surface
    full_thickness_base = (intake_flat_air_thickness_base + 2*min_wall_thickness)
    full_thickness = full_thickness_base * math.cos(relative_offset * math.pi)
    full_thickness_derivative = -math.pi * full_thickness_base * math.sin(relative_offset * math.pi) / intake_flat_width
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
      
    
    elastic_end_base_point = sample.position + elastic_holder_depth*sample.along_intake_flat_unit_height_from_plane
    
    if intake_edge_heights[3] > intake_edge_heights[0] + 0.1:
      for index in [0,3]:
        intake_edges [index].append ((
          sample.print_surface_base_point + intake_edge_offsets [index],
          elastic_end_base_point + intake_edge_offsets [index],
        ))
    beyond_air = True
    if intake_edge_heights[2] > intake_edge_heights[1] + 0.1:
      beyond_air = False
      for index in [1,2]:
        intake_edges [index].append ((
          sample.print_surface_base_point + intake_edge_offsets [index],
          elastic_end_base_point + intake_edge_offsets [index],
        ))
    
    
    lower_side_shield_lip.append (sample.position)
    # a fairly arbitrary approximation, but it's not necessarily worth the effort of computing the points it would realistically be taut across
    if intake_edge_heights[3] > intake_flat_air_thickness_base/2:
      lower_side_cloth_lip.append (sample.position + intake_edge_offsets[3] + elastic_holder_depth*sample.along_intake_flat_unit_height_from_plane)
    
    if offset < 0 and intake_edge_heights[3] - min_wall_thickness / 2 < intake_support_thickness:
      a = intake_edge_offsets[3] + sample.normal_in_plane_unit_height_from_shield * min_wall_thickness * 2/3
      if beyond_air:
        a = vector()
      b = -sample.normal_in_plane_unit_height_from_shield * intake_support_thickness
      intake_support_hoops.append (Wire ([
        sample.print_surface_base_point + a,
        sample.print_surface_base_point + b,
        sample.position + b,
        sample.position + a,
      ], loop = True))
      a = a + contact_leeway * sample.normal_in_plane_unit_height_from_shield
      b = b - contact_leeway * sample.normal_in_plane_unit_height_from_shield
      c = contact_leeway * sample.along_intake_flat_unit_height_from_plane
      d = -contact_leeway * sample.curve_tangent
      intake_support_exclusion_hoops.append (Wire ([
        sample.print_surface_base_point + a - c + d,
        sample.print_surface_base_point + b - c + d,
        sample.position + b + c + d,
        sample.position + a + c + d,
      ], loop = True))
    
    
    
  for sample in curve_samples(shield_lower_side_curve, intake_middle.curve_distance + intake_flat_width/2 + elastic_corner_opening_width, shield_lower_side_curve.length()/2-1, amount = 20):
    augment_intake_sample(sample)
    lower_side_center_max = min(1.0, abs(sample.position[0])/50)
    depth = min(
      elastic_holder_depth/abs (sample.along_intake_flat.dot(sample.plane_normal)),
      elastic_holder_depth * 1.4 * lower_side_center_max
    )
    l = ShieldSample(closest = sample.position + depth*sample.along_intake_flat).position
    lower_side_cloth_lip.append (l)
    lower_side_shield_lip.append (l)
  
    
        
        
  intake_inner_pairs = intake_edges [1] + intake_edges[2][::-1]
  intake_outer_pairs = intake_edges [0] + intake_edges[3][::-1]
    

  chin_cloth_lip_points = (
    upper_side_cloth_lip
    + lower_side_cloth_lip
    + [a@Mirror (Right) for a in lower_side_cloth_lip[::-1]]
    + [a@Mirror (Right) for a in upper_side_cloth_lip[::-1]]
  )
  side_shield_lip_points = (
    upper_side_cloth_lip
    + lower_side_shield_lip
    + [a@Mirror (Right) for a in lower_side_shield_lip[::-1]]
    + [a@Mirror (Right) for a in upper_side_cloth_lip[::-1]]
  )
  save ("chin_cloth_lip", Interpolate (chin_cloth_lip_points))
  save ("chin_cloth_lip_points", Compound ([Vertex (point) for point in chin_cloth_lip_points]))
  #save ("side_shield_lip", Interpolate (side_shield_lip_points))
  save ("side_shield_lip_points", side_shield_lip_points)

  save ("intake_support", Loft(intake_support_hoops, solid = True, ruled = True))
  save ("intake_support_exclusion", Loft(intake_support_exclusion_hoops, solid = True, ruled = True))

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
      direction = -Direction (CPAP_forwards.cross (intake_middle.normal))
      other_direction = direction.cross (CPAP_forwards)
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
  save ("intake_solid", Solid (Shell (
    Face (intake_interior.surface),
    Face (intake_exterior.surface),
    intake_CPAP_cover,
    intake_flat_cover,
  )))

#preview(intake_solid, intake_support, chin_cloth_lip, Compound ([Vertex (point) for point in side_shield_lip_points]))

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
  adjusted = projected.curve_distance*(flat_approximation_increments -1)/shield_top_curve_length
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
  unrolled_top = [unrolled (surface.position) for surface in curve_samples (shield_top_curve, 0, shield_top_curve_length, amount=40)]
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
    (top_outer_rim_sample(sample) for sample in curve_samples (shield_top_curve, shield_top_curve_length/2, top_hook_front.curve_distance, amount = math.floor(shield_top_curve_length * 2))),
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

# add significant leeway to accommodate larger necks, reduce the chance of yanking it off the rim
neck_y = shield_back - 20 #5
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
#neck_points = [vector(a[0], a[1] + a[2]*0.2, a[2]) for a in neck_points] 
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

########################################################################
########  Split/assemble components into printable parts  #######
########################################################################

def reflected (components):
  return components + [component@Reflect(Right) for component in components]
  
@run_if_changed
def make_FDM_printable_lower_side():
  lower_side = Compound ([
    intake_solid,
    intake_support,
    side_pegs,
  ])
  #preview(lower_side)
  save("lower_side", lower_side)
  save_STL("lower_side", lower_side)

'''@run_if_changed
def make_FDM_printable_upper_side():
  upper_side = Compound ([
    upper_side_rim.cut(side_joint_peg_hole),
    temple_side_peg,
    side_hook,
    upper_side_rim_lower_block,
  ])
  save("upper_side", upper_side)
  save_STL("upper_side", upper_side)'''


@run_if_changed
def make_FDM_printable_top_rim():
  top_rim_final = Compound ([
    top_rim,
  ]
  + reflected ([temple_top_pegs, top_hook]))
  save("top_rim_final", top_rim_final)
  save_STL("top_rim_final", top_rim_final)


@run_if_changed
def make_FDM_printable_overhead_strap():
  save_STL("overhead_strap", overhead_strap)

@run_if_changed
def make_FDM_printable_headband():
  headband_final = Compound ([
    standard_headband.intersection(HalfSpace(temple + Front*16, Back)),
    standard_headband_wave,
  ]
  + reflected ([
    temple_block,
    upper_side_rim.cut(intake_support_exclusion),
    side_hook,
    top_hook,
    #forehead_elastic_hooks,
  ]))
  save("headband_final", headband_final)
  save_STL("headband_final", headband_final)
preview(lower_side, headband_final)

@run_if_changed
def make_FDM_printable_hook_skirt():
  save_STL("hook_skirt", hook_skirt)


@run_if_changed
def make_combined():
  combined = Compound ([
    headband_final @ Translate(0,0,-headband_top) @ Rotate(Front, degrees=180),
    top_rim_final @ Translate(0,0,-headband_top) @ Rotate(Front, degrees=180) @ Translate(0, -30, 13),
    overhead_strap @ Translate(overhead_strap_width/2, 0, 0)@Rotate (Front, degrees=90)@Rotate (Up, degrees=80)@Translate(-100, -110, 0),
    lower_side @(
      Transform(Right, Direction(side_curve_source_points[1], side_curve_source_points[2]), Right.cross(Direction(side_curve_source_points[1], side_curve_source_points[2])), Vector(Origin, side_curve_source_points[1])).inverse()
    ) @ Rotate(Front, degrees=180) @ Translate(0, -152, 18),
    
  ])
  save("combined_final", combined)
  save_STL("combined_final", combined, linear_deflection = 0.02, angular_deflection = 0.2)
  preview(combined)

preview(
  headband_final,
  overhead_strap,
  hook_skirt,
)
preview (
  standard_headband,
  temple_top_pegs,
  temple_block,
  top_rim,
  upper_side_rim,
  upper_side_rim@Reflect(Right),
  
  side_pegs,
  
  lower_side_rim,
  lower_side_extra_lip,
  lower_side_extra_lip@Reflect(Right),
  intake_solid,
  intake_solid@Reflect(Right),
  top_hook,
  side_hook,
  #shield_cross_sections,
  #Face (shield_surface),
  Edge(shield_source_curve),
  Edge(shield_top_curve.curve),
  shield_source_points,
  #eye_lasers,
  #LoadSTL ("private/face5_for_papr.stl"),
  
  unrolled_shield_wire,
  forehead_cloth_wire,
  chin_cloth_wire,
)
  
  
  