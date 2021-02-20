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
– It was practical to wear with a bike helmet, but that means wearing it about a centimeter farther down than I usually do, which means the shield is significantly farther away from my face (due to both shield_focal_slope and the slope of my forehead). My particular bike helmet dips down at the temples, pushing the temple block down but not requiring the forehead to move, so the mask is slanted in a way that moves the shield even further from the face. The quick fix is to just change putative_chin, making the mask smaller.
– The headband also digs into my forehead a bit more in the biking position because the forehead is shaped differently down there on the eyebrows; I'm not worried about this for the moment.
– A fancier solution could theoretically move the temple block downwards in normal usage, allowing the front headband to be higher up than the temple block (and making the top edge of the face shield be a more complex curve), but this might have problems with torque moving the mask the wrong way in normal usage.
– Partly related to the bike position issue, it might now be helpful to redirect the air towards the face instead of along the shield surface; this should now be practical given the current design of the intake.



Additional notes after prototype #7:
– It finally works well with a bike helmet!!
– The chin cloth I made for prototype #5 didn't stay on the face shield very well, but the new, sized-for-#7 chin cloth did. This is strong evidence that the shape actually mattered.
– The positioning of the nub/slot (elastic hook replacement) worked fine, but both were too easy for the elastic to slide off of (even after getting the cloth sizing correct). In the case of the nubs, part of the problem is that they don't stick out far enough past the thickness of the shield itself, which I didn't account for.
– The mask has the "wants to tilt upwards" problem a bit, but this isn't a big problem (and it's unavoidably tilted with my bike helmet).
– The air redirection reduced fogging in cold weather by a lot.
– The shield tends to pop off the glue at the intake. This can be resolved by printing a short slot to hold onto it from the outside.
– Even after getting the chin cloth size correct, it still tended to slide off the shield at the top of the intake. I resolved this by putting a dot of glue on the outside of the shield at the convex corner; I could also resolve it by building a little prong into the 3d printed part (the printing direction isn't ideal but it should work, and I'd have to adjust the shield shape but that's easy enough).
– (after adding the temple extender hacks) The temple extender hacks seemed to keep it stable on my head much better even without a top strap (vague theory: the y-distance from forehead to end of the extender was about twice the y-distance from forehead to previous elastic attach point, so it could only wobble about half as much). But the temple extenders kept coming unglued, so I'll have to build them into a new full print.

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
putative_chin = forehead_point + vector (0, -13, -125)

# The amount of distance in the y dimension to put between the putative chin and the shield
chin_leeway = 10

# The bottom edge of the shield. Ideally, this should be further down than the invisible point – far enough down that even after cloth is put over it, the cloth is also invisible.
rim_bottom_z = putative_chin[2] - 36 

# The putative corner of where glasses might be, experimentally determined from someone with large glasses.
glasses_point = forehead_point + vector (66, 0, -10)

# The putative source of sight, used for determining where reflections will be visible.
putative_eyeball = forehead_point + vector (35, -15, -35)

# The location the air should be directed towards, intended to be just under the nose.
air_target = putative_chin + vector(0, 10, 40)

contact_leeway = 0.4

# The corner where the shield surface meets the headband. This is not guaranteed to be placed exactly on the headband curve.
temple = Point (77, shield_back, 0)

# The angle (in the XY plane) that the shield surface extends from the temple.
temple_radians = (math.tau/4) * 0.6
temple_direction = Right@Rotate (Up, radians = temple_radians)

# The angle of the shield surface in the YZ plane.
shield_focal_slope = 1.8

# The thickness of the flat part of the air passage at its thickest point
intake_flat_air_thickness_base = 10.4

# The length, along the side curve, of exterior of the intake wall (this may be a slight overestimate because we will curve the points of the walls a bit)
intake_flat_width = 56

# The width of the opening of the triangular corner the elastic should nestle into
elastic_corner_opening_width = 6

# The width of the concave point (avoid leaving an air gap by either making it too pointy, so the cloth doesn't go all the way to the point, or too loose, so the cloth doesn't fill it)
elastic_corner_point_width = 1

# the thickness of the intake support in the direction normal to the shield
intake_support_thickness = 4

intake_middle_y = -50
intake_middle_z = -100


lots = 500

# Estimated minimum and maximum sizes of real people's heads (currently unused, I think)
min_head_circumference = 500
max_head_circumference = 650


headband_top = shield_glue_face_width + min_wall_thickness
headband_bottom= headband_top - headband_width

########################################################################
########  Generalized cone definitions  #######
########################################################################


# The above constants uniquely determine a focal point for
# the generalized cone of the shield surface; we calculate that now
shield_focal_y = temple[1] - (temple[0] * temple_direction[1] / temple_direction[0])

shield_chin_peak = putative_chin + Back*chin_leeway
shield_focal_point = Point (0, shield_focal_y, shield_chin_peak[2] + (shield_focal_y - shield_chin_peak[1]) * shield_focal_slope)


# For historical reasons, the top edge of the shield
# does not have z-coordinate 0, but headband_top.
# We describe a "source curve" at the top edge of the shield,
# which is projected towards the focal point to describe the surface.
above_temple = temple + vector (0, 0, headband_top)
def projected_to_top (point):
  return point.projected (
    Plane (above_temple, Up),
    by = Direction (shield_focal_point, point)
  )

shield_source_curve_points = [
  above_temple,
  projected_to_top (glasses_point + vector (15, 10, 0)),
  projected_to_top (shield_chin_peak),
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

print (f"Shield position directly in front of chin: {shield_surface.intersections (Line(putative_chin, Back)).point()} (should be equal to {shield_chin_peak})")

# Now that we've defined the shield surface itself, we can define a system for taking samples from it, with useful extra date of like the normal to the surface and such

class ShieldSample(SerializeAsVars):
  def __init__(self, *, parameter = None, closest = None, intersecting = None, which = None):
    if intersecting is not None:
      intersections = shield_surface.intersections (intersecting)
      closest = intersections.points [which] if which is not None else intersections.point()
    if closest is not None:
      self.shield_parameter = shield_surface.parameter(closest)
    elif parameter is not None:
      self.shield_parameter = parameter
    else:
      raise RuntimeError ("didn't specify how to initialize ShieldSample")
    
    self.position = shield_surface.value(self.shield_parameter)
    self.normal = shield_surface.normal(self.shield_parameter)


class CurveSample (ShieldSample):
  def __init__(self, curve, *, distance = None, closest = None, y = None, z = None, which = None, intersecting = None):
    if y is not None:
      intersecting = Plane (Point(0,y,0), Front)
    if z is not None:
      intersecting = Plane (Point(0,0,z), Up)
    if intersecting is not None:
      intersections = curve.intersections (intersecting)
      closest = intersections.points [which] if which is not None else intersections.point()
    
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
    try:
      end_distance = curve.precomputed_length
    except AttributeError:
      end_distance = curve.length()
  return (CurveSample(curve, distance=distance) for distance in subdivisions(start_distance, end_distance, **kwargs))



shield_bottom_peak = ShieldSample(intersecting = Line(Point(0,0,rim_bottom_z), Back))


# There's at least one instance where we want a *planar* curve within the shield surface, to assist with making FDM-printable objects. This gets special features!

class ShieldCurveInPlane(SerializeAsVars):
  def __init__(self, plane):
    self.plane = plane
    self.curve = shield_surface.intersections (plane).curve()
    self.precomputed_length = self.curve.length()
    
  def __getattr__(self, name):
    return getattr(self.curve, name)



@run_if_changed
def make_shield_top_curve():
  save ("shield_top_curve", ShieldCurveInPlane(Plane(Point (0, 0, headband_top), Up)))
  
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

  
  

save ("glasses_vertex", Vertex (glasses_point))
diff = Direction (glasses_point - shield_focal_point)
save ("glasses_edge", Edge (glasses_point + diff*180, glasses_point - diff*180))


########################################################################
########  Intake  #######
########################################################################

# The intake wants to have a surface that direct air towards air_target. It's convenient if that surface is the build surface, so make a plane for that:

intake_middle_in_build_surface_shield_curve = ShieldSample(intersecting = RayIsh(Point(0,intake_middle_y,intake_middle_z), Right))

# Two degrees of freedom are removed by air_target and intake_middle_in_build_surface_shield_curve; to remove the third degree of freedom, the concave corner just above the intake, where the cloth nestles, should be elastic_holder_depth in front of shield_back. The build surface should be about shield_glue_face_width further in front of that... the actual formulas here are annoyingly complicated, but this is close enough:

intake_third_source_sample = ShieldSample(intersecting = RayIsh(Point(
  0,
  shield_back + elastic_holder_depth + shield_glue_face_width,
  intake_middle_in_build_surface_shield_curve.position[2] + intake_flat_width/2
), Right))

intake_source_direction_1 = Direction(intake_middle_in_build_surface_shield_curve.position, intake_third_source_sample.position)
intake_source_direction_2 = Direction(air_target, intake_middle_in_build_surface_shield_curve.position)

intake_curve_source_points = [
  air_target + intake_source_direction_1 * intake_flat_width*1.4,
  air_target - intake_source_direction_1 * intake_flat_width,
]
save ("intake_curve_source_surface", BSplineSurface([
    [point + intake_source_direction_2* 50 for point in intake_curve_source_points],
    [point + intake_source_direction_2*150 for point in intake_curve_source_points],
  ],
  BSplineDimension (degree = 1),
  BSplineDimension (degree = 1),
))

#preview(shield_surface, intake_curve_source_surface)


@run_if_changed
def make_intake_curve():
  save ("intake_curve", ShieldCurveInPlane(intake_curve_source_surface))



@run_if_changed
def make_intake():
  # hack - temporary value to avoid augment_intake_sample circular dependency issue
  CPAP_forwards = Back
  def augment_intake_sample(sample):
    sample.along_intake_flat = sample.normal.cross(Up).normalized()
    sample.along_intake_flat_unit_height_from_plane = sample.along_intake_flat/abs (sample.along_intake_flat.dot(sample.plane_normal))
    sample.below_shield_glue_base_point = ShieldSample(closest = sample.position + shield_glue_face_width*sample.along_intake_flat_unit_height_from_plane).position
    sample.below_elastic_base_point = sample.below_shield_glue_base_point - CPAP_forwards * elastic_holder_depth
    
  # a base point on the lower side curve, just inside the shield.
  intake_middle = CurveSample(intake_curve, z=intake_middle_z)
  augment_intake_sample(intake_middle)
  
  # the center of the circle at the far CPAP connector end.
  CPAP_back_center = Point(72, headphones_front - 40, -92)
  
  # a reference point to try to aim the CPAP direction in a way that will make the whole shape smooth.
  intake_flat_back_center_approx = (intake_middle.position
    + (shield_glue_face_width + elastic_holder_depth + 4)
      *intake_middle.along_intake_flat_unit_height_from_plane
    - intake_middle.normal
      *(min_wall_thickness + intake_flat_air_thickness_base/2)
    + Up*5)
  
  CPAP_forwards = Direction (CPAP_back_center, intake_flat_back_center_approx) #vector(0.2, 1, -0.1).normalized()
  
  towards_air_target = Direction(intake_middle.position, air_target)
  
  
  
  intake_cloth_lip = []
  intake_shield_lip = []
  intake_support_hoops = []
  intake_air_cut_hoops = []
  intake_support_exclusion_hoops = []
  intake_edges = ([], [], [], [])
  
  for sample in curve_samples(intake_curve, 1, intake_middle.curve_distance - intake_flat_width/2 - elastic_corner_opening_width, amount = 10):
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
  
  sample = CurveSample(intake_curve, distance = intake_middle.curve_distance - intake_flat_width/2 - elastic_corner_opening_width)
  augment_intake_sample(sample)
  target_shield_convex_corner_above_intake = sample.below_elastic_base_point
  save("target_shield_convex_corner_above_intake", target_shield_convex_corner_above_intake)
  sample = CurveSample(intake_curve, distance = intake_middle.curve_distance - intake_flat_width/2 - elastic_corner_point_width)
  augment_intake_sample(sample)
  intake_shield_lip.append (sample.below_shield_glue_base_point)
  
  for sample in curve_samples(intake_curve, intake_middle.curve_distance - intake_flat_width/2 + 0.1, intake_middle.curve_distance + intake_flat_width/2 - 0.1, amount = 70):
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
    
    
    intake_shield_lip.append (sample.below_shield_glue_base_point)

    
    do_support = offset < 0 and intake_edge_heights[3] - min_wall_thickness / 2 < intake_support_thickness
    if do_support:
      a = intake_edge_offsets[3] + sample.normal_in_plane_unit_height_from_shield * min_wall_thickness * 2/3
      if beyond_air:
        a = vector()
      b = -sample.normal_in_plane_unit_height_from_shield * intake_support_thickness
      intake_support_hoops.append (Wire ([
        sample.position + a,
        sample.position + b,
        sample.below_shield_glue_base_point + b,
        sample.below_shield_glue_base_point + a,
      ], loop = True))
      a = a + contact_leeway * sample.normal_in_plane_unit_height_from_shield
      b = b - contact_leeway * sample.normal_in_plane_unit_height_from_shield
      c = contact_leeway * sample.along_intake_flat_unit_height_from_plane
      d = -contact_leeway * sample.curve_tangent
      intake_support_exclusion_hoops.append (Wire ([
        sample.position + a - c + d,
        sample.position + b - c + d,
        sample.below_shield_glue_base_point + b + c + d,
        sample.below_shield_glue_base_point + a + c + d,
      ], loop = True))
      
    if intake_edge_heights[2] > intake_edge_heights[1] + 1 and not do_support:
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
  
  
  sample = CurveSample(intake_curve, distance = intake_middle.curve_distance + intake_flat_width/2 + elastic_corner_point_width)
  augment_intake_sample(sample)
  intake_shield_lip.append (sample.below_shield_glue_base_point)
  sample = CurveSample(intake_curve, distance = intake_middle.curve_distance + intake_flat_width/2 + elastic_corner_opening_width)
  augment_intake_sample(sample)
  target_shield_convex_corner_below_intake = sample.below_elastic_base_point
  save("target_shield_convex_corner_below_intake", target_shield_convex_corner_below_intake)
  
  
  fins = []
  for sample in curve_samples(intake_curve, intake_middle.curve_distance - intake_flat_width/2 + 9, intake_middle.curve_distance + intake_flat_width/2 - 11, amount = 6):
    augment_intake_sample(sample)
    perpendicular = towards_air_target.cross(sample.plane_normal)
    k = Between(sample.below_shield_glue_base_point, sample.below_elastic_base_point, 0.5)
    fins.append(Edge((Segment(sample.position, k)) @ Translate(towards_air_target * min_wall_thickness/2)).extrude(towards_air_target*20).extrude(perpendicular * min_wall_thickness, centered = True))
        
        
  intake_inner_ribs = intake_edges [1] + intake_edges[2][::-1]
  intake_outer_ribs = intake_edges [0] + intake_edges[3][::-1]
    

  save("intake_shield_lip", intake_shield_lip)

  intake_air_cut = Loft([intake_air_cut_hoops[0], intake_air_cut_hoops[-1]], solid = True, ruled = True)
  save ("intake_support", Loft(intake_support_hoops, solid = True, ruled = True))
  save ("intake_support_exclusion", Loft(intake_support_exclusion_hoops, solid = True, ruled = True))

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
  save ("intake_fins", Compound(fins, Face(intake_curve.plane).extrude(-intake_curve.plane.normal(0,0)*min_wall_thickness)).intersection(intake_solid_including_interior))
  
  taut_direction = -intake_middle.normal
  for frac in subdivisions(0.2, 0.8, amount = 15):
    base = Between(target_shield_convex_corner_above_intake, target_shield_convex_corner_below_intake, frac)
    
    # a fairly arbitrary approximation, but a fully realistic calculation would be way more effort than it'd be worth
    intake_cloth_lip.append (intake_exterior.surface.intersections(RayIsh(base + taut_direction*1, taut_direction)).point())
  save("intake_cloth_lip", intake_cloth_lip)
    
  

#preview(intake_solid, intake_support, intake_fins, Compound([Vertex(a) for a in intake_shield_lip]), BSplineCurve(intake_cloth_lip))

  
  
  
########################################################################
########  Eye lasers  #######
########################################################################


def eye_laser(direction):
  try: 
    sample = ShieldSample(intersecting = TrimmedCurve(Line (putative_eyeball, direction), 0, lots), which = 0)
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
#preview(temple_knob_curve , temple_block_uncut)


@run_if_changed
def make_temple_extender_hack():
  length = 60
  width = 10
  depth = 5
  hoops = []
  holes = []
  for distance in subdivisions(temple_block_start_distance-17, temple_block_start_distance+length, amount=30):
    d = standard_forehead_curve.derivatives(distance = distance)
    a = d.position + Up*(headband_top + depth)
    b = d.position + Up*headband_top
    k = -d.normal * width
    j = -d.normal * 2.5
    l = -d.normal * (width - 2.5)
    z = Up*1
    hoops.append(Wire([
      a, b, b+k, a+k
    ], loop = True))
    holes.append(Wire([
      a+z+j, b-z+j, b-z+l, a+z+l
    ], loop = True))
  result = Loft(hoops, solid = True)
  result = Fillet(result, [(edge, 3.0) for edge in result.edges() if all_equal(v[1] for v in edge.vertices())])
  for foo in range(3):
    bar = 11 + foo * 6
    result = result.cut(Loft(holes[bar:bar + 6], solid= True))
  
  save("temple_extender_hack", result)
  save_STL("temple_extender_hack", result)
    


  
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
  temple_block_cuts_depth = 4
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
  save("temple_block", temple_block_uncut.cut(forehead_cloth_cut_1).cut(forehead_cloth_cut_2))


@run_if_changed
def make_elastic_loop():
  shield_exclusion = Face (shield_surface).intersection (HalfSpace (Point (10, 0, 0), Right)).intersection (HalfSpace (temple, Back)).extrude (Left*lots) @ Translate(Left*0.1)
  c = Point(temple[0] + 8, temple[1] + 15, headband_top)
  a = Axes(c, Up, Right)
  r = 7
  f = Face(Wire(Edge(Circle(a, r))), holes= Wire(Edge(Circle(a, r-1.5))).complemented())
  save("elastic_loop", f.extrude(Down*3).cut(shield_exclusion))
  
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


  

z = -2
a=0
b=1.5
c=3.5
s=2
p=4
q=6
r=8
temple_knob_coordinates = [
  (z, s), (a, s), (a,p), (b,p), (b,s), (c,s), (c,p), (c,q), (c,r), (b,r), (b,q), (a,q), (a,r), (z, r)
]
temple_knob_offset = -4
def temple_knob_ring(z):
  sample = CurveSample(shield_upper_side_curve, z=z)
  result = []
  for x,y in temple_knob_coordinates:
    s2 = ShieldSample(intersecting = RayIsh(sample.position - sample.curve_in_surface_normal*y, Left, length=1))
    result.append(s2.position + s2.normal*x)
    result[-1][2] = z
  return result

@run_if_changed
def make_temple_knob():
  temple_knob_rings = [temple_knob_ring(a) for a in [headband_top, headband_top - 5]]
  temple_knob_surface = BSplineSurface(temple_knob_rings, BSplineDimension(degree=1), BSplineDimension(periodic = True))
  
  save("temple_knob", Solid(Shell(
    [Face(temple_knob_surface)] + [Face(BSplineCurve(r, BSplineDimension(periodic = True))) for r in temple_knob_rings]
  )))


upper_side_rim_bottom = 47

  
@run_if_changed
def make_side_pegs():
  shield_exclusion = Face (shield_surface).intersection (HalfSpace (Point (10, 0, 0), Right)).intersection (HalfSpace (temple, Back)).extrude (Right*lots)
  forehead_exclusion = Face(standard_forehead_curve).extrude(Down*lots, centered=True)
  #build_plate_exclusion = Face(intake_curve.plane).extrude(Back*lots)
  
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
  


preview(temple_extender_hack, shield_bottom_peak.position, target_shield_convex_corner_below_intake, elastic_loop, side_pegs, upper_side_rim.wires(), temple_block, temple_knob, intake_solid, intake_support, intake_fins, Compound([Vertex(a) for a in upper_side_cloth_lip + intake_shield_lip + lower_curve_cloth_lip]), BSplineCurve(upper_side_cloth_lip + intake_cloth_lip + lower_curve_cloth_lip))
  
  

  


#preview(upper_side_rim, lower_side_rim, top_rim, standard_headband, top_hook, side_hook, eye_lasers, glasses_edge)  


########################################################################
########  Combine the parts of shield/cloth lip from above  #######
########################################################################

side_shield_lip_points = (
    upper_side_cloth_lip
    + intake_shield_lip
    + lower_curve_cloth_lip
    + [a@Mirror (Right) for a in intake_shield_lip[::-1]]
    + [a@Mirror (Right) for a in upper_side_cloth_lip[::-1]]
  )
chin_cloth_lip_points = (
    upper_side_cloth_lip
    + intake_cloth_lip
    + lower_curve_cloth_lip
    + [a@Mirror (Right) for a in intake_cloth_lip[::-1]]
    + [a@Mirror (Right) for a in upper_side_cloth_lip[::-1]]
  )
@run_if_changed
def make_cloth_lip():
  save ("chin_cloth_lip", Interpolate (chin_cloth_lip_points))
#save ("side_shield_lip_points", Compound([Vertex(a) for a in side_shield_lip_points])

#preview(intake_solid, intake_support, chin_cloth_lip, Compound ([Vertex (point) for point in side_shield_lip_points]), Edge(air_target, CurveSample(shield_lower_side_curve, z=-100, which=0).position))

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
    intake_fins,
    side_pegs,
  ])
  #preview(lower_side)
  save("lower_side", lower_side)
  save_STL("lower_side", lower_side)


@run_if_changed
def make_FDM_printable_headband():
  headband_final = Compound ([
    standard_headband.intersection(HalfSpace(temple, Back)),
    standard_headband_wave,
  ]
  + reflected ([
    temple_block,
    upper_side_rim,
    elastic_loop,
    temple_knob,
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
  
  
  