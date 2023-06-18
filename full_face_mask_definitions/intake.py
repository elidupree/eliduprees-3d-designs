import math

from full_face_mask_definitions.constants import air_target, min_wall_thickness, CPAP_outer_radius
from full_face_mask_definitions.headband_geometry import headband_top
from full_face_mask_definitions.shield_geometry import ShieldSample, shield_back_y, ShieldCurveInPlane, CurveSample, \
    shield_surface
from pyocct_system import *

# The intake wants to have a surface that directs air towards air_target. It's convenient if that surface is the build surface, so we make a plane for that.
# To decide the plane, first, we define an "intake middle" point, which is defined to lie on the shield surface, and will define the build plane:
intake_middle_position = ShieldSample(intersecting=RayIsh(Point(0, -50, -100), Right)).position

# Two degrees of freedom are removed by air_target and intake_middle. To remove the third degree of freedom, we need to make sure that the FDM print is capable of making a strut that goes all the way up to the headband, while still being a good thickness for strength.
intake_build_surface_top_point = ShieldSample(
    intersecting=RayIsh(Point(0, shield_back_y + 10, headband_top), Right)).position

# We also define the length, approximately along the side curve, of the exterior of the intake wall. The actual width from the perspective of the moving air will be somewhat shorter than this, because the opening is angled.
intake_flat_width = 56
# We also define the thickness of the flat-ish part of the air passage at its thickest point (this may not be exact because we make it conform to the shield a bit).
intake_flat_air_thickness_base = 12


@run_if_changed
def intake_build_surface():
    d1 = Direction(intake_middle_position, intake_build_surface_top_point)
    d2 = Direction(air_target, intake_middle_position)
    source_points = [
        intake_build_surface_top_point,
        intake_middle_position - d1 * intake_flat_width * 0.8,
    ]
    return BSplineSurface([
        [point - d2 * 50 for point in source_points],
        [point + d2 * 50 for point in source_points],
    ],
        BSplineDimension(degree=1),
        BSplineDimension(degree=1),
    )


# We now define the "intake reference curve" as the intersection between the build surface and the shield surface.
@run_if_changed
def intake_reference_curve():
    return ShieldCurveInPlane(intake_build_surface)


@run_if_changed
def intake_middle():
    return CurveSample(intake_reference_curve, closest=intake_middle_position)


# We explicitly define the centers of the circles at the far CPAP connector end.
CPAP_back_center_1 = Point(72, shield_back_y - 40, -100)
CPAP_back_center_2 = CPAP_back_center_1 + Vector(22, 8, -16)
CPAP_back_centers = [CPAP_back_center_1, CPAP_back_center_2]

print(f"CPAP center distance: {CPAP_back_center_1.distance(CPAP_back_center_2)} (experimentally, only needs to be around 28)")

# The air will be directed towards the air target – but we don't mean it should all converge to an infinitesimal point. We will direct all the air in the same *direction*, which should naturally be the direction from the *middle* of the intake towards the air target.
towards_air_target = Direction(intake_middle.position, air_target)
# Thanks to the skew, we also want a version that induces a fixed perpendicular-distance from the shield, rather than being less thick depending on the skew.
towards_air_target_unit_height_from_shield = towards_air_target / abs(towards_air_target.dot(intake_middle.normal))

# As for the orientation of the CPAP connectors, they need to aim at some particular place internal to the intake structure. We define a reference point, intended to make the whole shape end up smooth.
CPAP_target_approx = intake_middle.position + towards_air_target_unit_height_from_shield * (
        min_wall_thickness + intake_flat_air_thickness_base / 2)

# Aim the 2 CPAP hoses at the target, although also keep them a bit separate from each other (as the air should be distributed throughout the intake, not converge to the middle).
# /4 might be ideal (each hose gets half the space) but I make them converge a LITTLE more than that by saying /5, mostly based on intuition.
CPAP_forwardses = [
    Direction(CPAP_back_centers[0], CPAP_target_approx - intake_middle.curve_tangent * intake_flat_width / 5),
    Direction(CPAP_back_centers[1], CPAP_target_approx + intake_middle.curve_tangent * intake_flat_width / 5),
]

# We also want a canonical "the average CPAP intake direction in general", to use for constructing the geometry of the shared parts.
CPAP_forwards_average = Direction(CPAP_forwardses[0] + CPAP_forwardses[1])
CPAP_forwards_average_unit_height_from_build_plane = CPAP_forwards_average / abs(
    CPAP_forwards_average.dot(intake_reference_curve.plane.normal((0, 0))))

# Part of the shape of the intake approximates a circular arc, with inner and outer radii:
intake_spout_smallest_radius = 3
intake_spout_largest_radius = min_wall_thickness + intake_flat_air_thickness_base + min_wall_thickness + intake_spout_smallest_radius

# Part of the intake is supposed to rest against the shield, where it should be sealed with glue; this should be wide enough to form a good seal, and historically was also intended to be structural.
shield_glue_face_width = 6

# The shield-ward surface of the intake wants to have a bit of a weird shape because of the shield surface shape, but for the face-ward surface, we can just use a plane. Let's define that plane to be parallel to intake_middle_curve_tangent and CPAP_forwards_average.
# So we are now working in a coordinate system where the dimensions are:
# 1) towards_air_target
# 2) CPAP_forwards_average
# 3) intake_middle_curve_tangent

at = towards_air_target
cf = CPAP_forwards_average
ct = intake_middle.curve_tangent
atu = at / abs(at.dot(Direction(cf.cross(ct))))
cfu = cf / abs(cf.dot(Direction(at.cross(ct))))
ctu = ct / abs(ct.dot(Direction(at.cross(cf))))

intake_faceward_middle = intake_middle.position + atu * intake_spout_largest_radius
# An origin point for the center of curvature of the spout:
intake_radius_center_middle = intake_faceward_middle - CPAP_forwards_average_unit_height_from_build_plane * intake_spout_largest_radius

# The main 3D shape of the intake will be defined using explicit BSplineSurfaces, extending all the way from the circle of the CPAP connector to the rounded-rectangle of the output. For this, we need to define numbers of control points on each side of the rounded-rectangle, so we can use the same number of points for the circle.
num_points_long_side = 14
num_points_short_side = 5
num_points_total = (num_points_long_side + num_points_short_side) * 2


def CPAP_hoop(CPAP_back_center, CPAP_forwards, frac):
    """
    Generate one of the circular cross-sections that defines a CPAP intake.

    :param CPAP_back_center: The center of the very entrance of this particular CPAP intake.
    :param CPAP_forwards: The direction forwards along this particular CPAP intake.
    :param frac: How far along the intake, as a fraction of the distance from the entrance to the part that's no longer governed by the circular shape.
    :return: A list of control points for this particular cross-section of the CPAP intake.
    """

    offset = frac * 20
    center = CPAP_back_center + CPAP_forwards * offset
    direction = Direction(CPAP_forwards.cross(CPAP_forwards.cross(towards_air_target)))

    start_index = (num_points_long_side - 1) / 2

    def CPAP_point(index):
        angle = -(index - start_index) / num_points_total * math.tau
        return center + (direction * CPAP_outer_radius) @ Rotate(CPAP_forwards, radians=angle)

    return [CPAP_point(index) for index in range(num_points_total)]


# The main model-generation:
intake_wall, intake_outer_solids, intake_inner_solids, intake_outer_surfaces_extended = None, None, None, None


@run_if_changed
def make_intake():
    global intake_wall, intake_outer_solids, intake_inner_solids, intake_outer_surfaces_extended

    # For the "spout" part (rather than the "CPAP" part), we first describe cross-sections arranged along the `curve_tangent` dimension, because that is the cleanest way of expressing them; they will later be transposed into cross-sections along the route of air movement.
    cross_section_points = []

    for tangent_offset in subdivisions(intake_flat_width / 2, -intake_flat_width / 2, amount=num_points_long_side + 2):
        center_of_curvature = intake_radius_center_middle + ct * tangent_offset

        # Each entry in cross_section_points is a pair – a point for the top of the spout, and a point for the bottom.
        exit_points = [
            center_of_curvature + cfu * intake_spout_largest_radius,
            center_of_curvature + cfu * intake_spout_smallest_radius,
        ]

        # Since we're going to use offset-surfaces later, and those offset-surfaces won't naturally agree with the exit plane, we extend it a little bit past the exit plane:
        beyond_exit_points = [p + atu * 3 for p in exit_points]

        before_exit_points = [
            exit_points[0] - atu * intake_spout_largest_radius * 0.7,
            exit_points[1] - atu * intake_spout_smallest_radius * 0.7,
        ]

        # For the next hoop, we want it to be aligned with the edge of the shield.
        # To simplify the geometry for us, instead of making the shield glue face an exact width, we make it an exact height from the build plane:
        sample = ShieldSample(
            intersecting=RayIsh(intake_faceward_middle + ct * tangent_offset - cfu * shield_glue_face_width, -atu))

        shield_guide_points = [
            sample.position,
            center_of_curvature + Direction(center_of_curvature, sample.position) * intake_spout_smallest_radius
        ]

        cross_section_points.append([
            shield_guide_points,
            before_exit_points,
            exit_points,
            beyond_exit_points,
        ])

    # Transpose the cross-sections, resulting in a list of "frames". Each frame is a list of pairs; each pair is a top point and corresponding bottom point.
    frames = list(zip(*cross_section_points))
    # Convert these into "hoops", list of control points for use in a BSplineSurface:
    spout_hoops = [flatten([
        [large for large, small in frame[1:-1]],
        subdivisions(*frame[-1], amount=num_points_short_side + 2)[1:-1],
        [small for large, small in reversed(frame[1:-1])],
        reversed(subdivisions(*frame[0], amount=num_points_short_side + 2)[1:-1]),
    ]) for frame in frames]

    beyond_exit_exclusion = Vertex(intake_faceward_middle)\
        .extrude(cfu * intake_spout_largest_radius * 2, centered=True)\
        .extrude(ct * (intake_flat_width), centered=True)\
        .extrude(atu * 50)

    intake_outer_solids = []
    intake_outer_surfaces_extended = []
    intake_inner_solids = []
    for CPAP_back_center, CPAP_forwards in zip(CPAP_back_centers, CPAP_forwardses):
        CPAP_hoops = [CPAP_hoop(CPAP_back_center, CPAP_forwards, frac) for frac in
                                               [0.0, 0.2, 0.4, 0.6, 1.3]]
        hoops = CPAP_hoops + spout_hoops
        outer_surface_extended = BSplineSurface(hoops, v=BSplineDimension(periodic=True))
        intake_outer_surfaces_extended.append(outer_surface_extended)
        inner_surface_extended = Face(outer_surface_extended).offset(-min_wall_thickness)

        outer_surface = Face(outer_surface_extended).cut(beyond_exit_exclusion)
        # Let the inner surface stick out a bit, so there's less degenerate cases in the cuts we will do later.
        inner_surface = inner_surface_extended.cut(beyond_exit_exclusion @ Translate(atu * 1))

        def close_holes(surface):
            fa, fb = [Face(w).complemented() for w in ClosedFreeWires(surface)]
            #preview(fa)
            #preview(fb)
            #preview(surface.faces() )
            return Solid(Shell(surface.faces() + [fa, fb]))

        intake_outer_solids.append(close_holes(outer_surface))
        intake_inner_solids.append(close_holes(inner_surface))

    # Sometimes you have to jiggle the surfaces to avoid degenerate cases which cause the algorithms to break. This value was determined by trial and error.
    jiggle = Right * 0.003 + Back * 0.004 + Up * 0.001

    intake_wall_solids = [s
                          .cut(intake_inner_solids[1] @ Translate(jiggle - cfu * 0.01))
                          .cut(intake_inner_solids[0] @ Translate(-jiggle - cfu * 0.01))
                          for s in intake_outer_solids]

    intake_wall = Compound(intake_wall_solids)

# The intake wants a bit of a cutout from the shield, so we describe that shape here, so the shield can use it.
# Why does it need this? Well, the intake can't avoid intersecting my visual range, so it takes up some of the area that would "naturally" be part of the shield; and the "back along the CPAP" direction is most comfortable if it intersects where the shield would be; and since the intake isn't optically clear anyway, there's no reason not to cut the shield there.
# @run_if_changed
# def shield_edge_for_intake():
