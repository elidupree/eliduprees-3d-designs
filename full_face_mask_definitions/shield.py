import math

from full_face_mask_definitions.constants import putative_chin, TowardsFrontOfHead, putative_eyeball, TowardsBackOfHead
from full_face_mask_definitions.headband import top_cloth_lip_back_for_shield, temple_extender
from full_face_mask_definitions.headband_geometry import headband_top
from full_face_mask_definitions.intake import intake_outer_solids, headband_to_intake_strut
from full_face_mask_definitions.shield_geometry import shield_back_y, shield_surface, ShieldSample, temple_top, \
    curve_samples, shield_top_curve, shield_focal_point, CurveSample
from pyocct_system import *
del Front, Back

# The bottom point of the shield. Ideally, this should be further down than the invisible point – far enough down that even after cloth is put over it, the cloth is also invisible. In practice, the very center is invisible because of my nose, but the parts beside it are just barely visible as a compromise with "not bumping the bottom edge into my chest".
shield_bottom_z = putative_chin[2] - 50


@run_if_changed
def shield_bottom_peak():
    return ShieldSample(intersecting=Line(Point(0, 0, shield_bottom_z), TowardsFrontOfHead))


@run_if_changed
def shield_back_face():
    c = BSplineCurve([
        temple_top + Up*2,
        temple_top + Down * 60,
        temple_top + Down * 125,
        shield_bottom_peak.position,
    ], BSplineDimension(degree=2))
    return Edge(c).extrude(Right * 500, centered=True)


@run_if_changed
def shield_infinitesimal_without_cuts():
    result = Face(shield_surface)
    # result = result.intersection(HalfSpace(Point(0, shield_back_y, 0), TowardsFrontOfHead))
    # result = result.intersection(HalfSpace(Point(0, 0, headband_top), Down))
    # result = result.intersection(HalfSpace(shield_bottom_peak.position, Direction(0, 1.6, 1)))
    result = result.intersection(shield_back_face.extrude(TowardsFrontOfHead * 200))
    return result

@run_if_changed
def shield_infinitesimal():
    result = shield_infinitesimal_without_cuts
    result = result.cut(Vertex(top_cloth_lip_back_for_shield).extrude(Up*50).extrude(TowardsBackOfHead*50).extrude(Right*500, centered=True))
    for transform in [Transform(), Reflect(Right)]:
        result = result.cut(temple_extender @ transform)
        result = result.cut(temple_extender @ Translate(Left*1) @ transform)
    for solid in intake_outer_solids:
        result = result.cut(solid)
    return result


# Make a contact surface with the intake spout, as noted in intake.py.
# This function is kind of a bunch of hacks.
@run_if_changed
def spout_to_shield_contact_part():
    def is_near_intake(shape):
        b = shape.bounds()
        return b.max()[2] < -50 and b.min()[2] > shield_bottom_z + 10
    intake_cut_wire = Wire([e for e in shield_infinitesimal.edges() if is_near_intake(e)])
    approx_curve_points = points_along_wire(intake_cut_wire, max_length = 6)
    approx_curve = BSplineCurve(approx_curve_points)
    approx_edge = Edge(approx_curve)
    result = Edge(approx_curve).extrude(Left*9, centered = True).offset(6, fill=True)
    shield_shadow = shield_infinitesimal_without_cuts.intersection(HalfSpace(Point(20,0,0), Right)).extrude(Left*50)
    result = result.intersection(shield_shadow)
    result = result.intersection(shield_back_face.extrude(TowardsFrontOfHead * 200) @ Translate(TowardsFrontOfHead * 2))
    #preview(headband_to_intake_strut.bounds().min(), result, headband_to_intake_strut.bounds().min() + vector(2, 1, -1))
    # quick hack to chop off a protruding bit:
    corner = min(headband_to_intake_strut.vertices(), key=lambda v: v[0]+v[1]+v[2])
    c = HalfSpace(corner.point() + Right*1, Direction(2, 1, -1))
    #preview(result, c.intersection())
    result = result.intersection(c)
    for s in intake_outer_solids:
        result = result.cut(s)
    #preview(approx_edge, result)
    return result



# To help analyze the reflection properties of the surface, we draw sight lines – provocatively called "eye lasers" – to see the locations from which light could unpleasantly reflect off the shield into the eye.
@run_if_changed
def eye_lasers():
    lasers = []
    for x in subdivisions(-2, 2, amount=10):
        for z in subdivisions(-2, 2, amount=10):
            direction = Direction(x, 1, z)
            try:
                sample = ShieldSample(intersecting=RayIsh(putative_eyeball, direction), which=0)
            except IndexError:
                # if it doesn't hit the shield, you couldn't see in that direction anyway
                continue
            # hack - also exclude points that aren't in the cropped shield
            # maybe this should explicitly use shield_infinitesimal
            if sample.position[2] > headband_top:
                continue

            reflected_direction = direction @ Reflect(sample.normal)
            # add a laser for direct vision
            lasers.append(Wire(putative_eyeball, sample.position, sample.position + direction * 50))

            try:
                sample2 = ShieldSample(
                    intersecting=RayIsh(sample.position + 0.1 * reflected_direction, reflected_direction), which=0)
            except IndexError:
                # if it doesn't hit the shield, it wasn't a problematic reflection
                continue
            # hack - also exclude points that aren't in the cropped shield
            # maybe this should explicitly use shield_infinitesimal
            if not RayIsh(sample2.position, TowardsBackOfHead).intersections(shield_back_face.surface()).points:
                continue
            # add a laser for the problematic reflection
            lasers.append(
                Wire(putative_eyeball, sample.position, sample2.position, sample2.position + reflected_direction * 50))
    return Compound(lasers)


# Current plastic was billed as 1/32 inch, which should be 0.79; experimentally measured with calipers as:
# shield_thickness = 0.74


# When we make the unrolled cutout, the most principled thing WOULD be to size it based on the middle of the thickness, rather than a specific face. The infinitesimal shield is the inner surface of the face, so we offset outwards by half the thickness.
#
# Unfortunately, this would make it no longer be a generalized cone – and thus technically unable to be unrolled to a flat surface, so we can't do this, and just go with the naïve approach.
# @run_if_changed
# def shield_middle_of_thickness():
#     return shield_infinitesimal.offset(shield_thickness / 2)


# We unroll the shield based on the following logic:
# 
# The focal point will be a single point within the flat version. All the lines going directly from the focal point are straight in 3D space; they will also be straight after being unrolled, and must be the same length. So, when choosing where to place a 3D point, you already know the distance from the focal point, and the only remaining choice is what angle to put it at.
#
# We precalculate approximate angles for every point on shield_top_curve, using some calculus; to find the angle for any other point, we project onto shield_top_curve and take the angle there.

flat_approximation_increments = 201


@run_if_changed
def flat_approximations():
    previous_sample = None
    result = [0]
    for sample in curve_samples(shield_top_curve, amount=flat_approximation_increments):
        if previous_sample is not None:
            difference = sample.position - previous_sample.position
            average = Between(sample.position, previous_sample.position)
            from_focus = Vector(shield_focal_point, average)
            relevant_difference = difference - from_focus * (difference.dot(from_focus) / from_focus.dot(from_focus))
            angle = math.atan2(relevant_difference.length(), from_focus.length())
            result.append(result[-1] + angle)
        previous_sample = sample
    # print (f"{flat_approximations}")
    return result


def flat_approximate_angle(position):
    difference = (position - shield_focal_point)
    projected = CurveSample(shield_top_curve, closest=shield_focal_point + difference * (
            shield_top_curve.StartPoint()[2] - shield_focal_point[2]) / difference[2])
    adjusted = projected.curve_distance * (flat_approximation_increments - 1) / shield_top_curve.precomputed_length
    # linearly interpolate
    floor = math.floor(adjusted)
    fraction = adjusted - floor
    previous = flat_approximations[floor]
    if floor + 1 >= len(flat_approximations):
        assert (floor + 0.99 < len(flat_approximations))
        result = previous
    else:
        next = flat_approximations[floor + 1]
        result = next * fraction + previous * (1 - fraction)
    # print (f" angles: {surface.ellipse_parameter}, {adjusted}, floor: {floor}, {fraction}, {previous}, {next}, {result}, ")
    # put 0 in the middle
    return result - flat_approximations[(flat_approximation_increments - 1) // 2]


def unrolled_point(position):
    offset = position - shield_focal_point
    distance = offset.length()
    paper_radians = flat_approximate_angle(position)
    result = Point(
        distance * math.cos(paper_radians),
        distance * math.sin(paper_radians),
        0
    )
    return result


# Break down each edge into a bunch of linear segments. Could we technically convert each BSplineCurve into another BSplineCurve in the plane? I'm not 100% sure whether the math works out, and this way is easier anyway.

def check_lengths(original_points, flat_points):
    for (a, b), (c, d) in zip(pairs(original_points, loop=True), pairs(flat_points, loop=True)):
        original = (a - b).length()
        derived = (c - d).length()
        ratio = derived / original
        if (abs(1 - ratio) > 0.01):
            print(derived, original)
            preview(Wire(original_points), Wire(flat_points), a, b, c, d)
        assert (abs(1 - ratio) <= 0.01)


@run_if_changed
def unrolled_shield_wire():
    original_points = points_along_wire(shield_infinitesimal.wire(), max_length=0.5)[:-1]
    flat_points = []
    for p in original_points:
        flat_points.append(unrolled_point(p))

    center_vertices_on_letter_paper(flat_points)
    check_lengths(original_points, flat_points)

    result = Wire(flat_points, loop=True)
    save_inkscape_svg("unrolled_shield", result)
    return result
