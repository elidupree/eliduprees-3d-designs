import math

from pyocct_system import *
from full_face_mask_definitions.constants import min_wall_thickness, TowardsFrontOfHead, neck_leeway
from full_face_mask_definitions.headband_geometry import headband_curve, headband_top, headband_bottom, \
    forehead_center_distance_on_headband_curve, extrude_flat_shape_to_headband, headband_curve_middle
from full_face_mask_definitions.shield_geometry import temple_xy, ShieldSample


@run_if_changed
def forehead_band():
    headband_2D = Offset2D(Wire(Edge(headband_curve)), min_wall_thickness, fill=True)
    headband = extrude_flat_shape_to_headband(headband_2D)
    return headband.intersection(HalfSpace(temple_xy, TowardsFrontOfHead))


# The joint between the headband and shield needs substantial reinforcement, to make sure the shield material remains oriented in the intended direction. We call this reinforcement the "temple block".
temple_distance_along_headband = headband_curve.distance(closest=temple_xy)

temple_block_length = 36
temple_block_start_distance = temple_distance_along_headband
temple_block_end_distance = temple_block_start_distance - temple_block_length

temple_block_far_corner, temple_block_near_corner = None, None


@run_if_changed
def temple_block_extrusion_direction():
    d = headband_curve.derivatives(distance=temple_block_start_distance)
    return -d.normal


@run_if_changed
def temple_block():
    global temple_block_far_corner, temple_block_near_corner
    hoops = []
    n = temple_block_extrusion_direction
    # Need to start slightly past the temple, because otherwise rounding error
    # might mean it has negative size
    for distance in subdivisions(temple_block_start_distance - 0.1, temple_block_end_distance, amount=10):
        d = headband_curve.derivatives(distance=distance)
        a = d.position + Up * headband_top + n * 0.02
        b = d.position + Up * headband_bottom + n * 0.02
        # preview(shield_surface, RayIsh(b, -start_derivatives.normal))
        c = ShieldSample(intersecting=RayIsh(b, n)).position
        d = ShieldSample(intersecting=RayIsh(a, n)).position
        temple_block_near_corner = a
        temple_block_far_corner = c
        hoops.append(Wire([
            a, b, c, d
        ], loop=True))

    return Loft(hoops, solid=True)


# We also want a tiny extra lip for the cloth to fuse to.
top_cloth_lip_back_for_shield = None


@run_if_changed
def top_cloth_lip():
    global top_cloth_lip_back_for_shield
    ad = temple_block_end_distance + min_wall_thickness
    a = headband_curve.value(distance=ad) @ Translate(Up * headband_top)
    b = ShieldSample(intersecting=RayIsh(a, temple_block_extrusion_direction)).position
    top_cloth_lip_back_for_shield = b
    adm = headband_curve_middle * 2 - ad
    wire = Wire([
        Edge(b @ Reflect(Right), a @ Reflect(Right)),
        Edge(TrimmedCurve(headband_curve, headband_curve.parameter(distance=adm),
                          headband_curve.parameter(distance=ad))) @ Translate(Up * headband_top),
        Edge(a, b),
    ])
    return Offset(wire.extrude(Up * 2), min_wall_thickness, fill=True)


# By adding a wave to a thin strip, we can make it still be able to flex, but not able to twist.
# This function generates a 2D wave shape, which can then be extruded vertically to form the 3D shape.
# It assumes that the (infinitesimal) curve argument actually describes a wall of width min_wall_thickness, expanded in the negative normal dimension of the curve.
def twist_resistant_waves(curve, start_distance, finish_distance):
    wave_curves = []
    touch_distances = subdivisions(start_distance, finish_distance, max_length=17)
    for (d1, d2) in pairs(touch_distances):
        start = curve.derivatives(distance=d1)
        middle = curve.derivatives(distance=(d1 + d2) / 2)
        finish = curve.derivatives(distance=d2)
        control_distance = (d2 - d1) / 4
        close_offset = -min_wall_thickness * 1.3
        far_offset = -6.6 - min_wall_thickness / 2
        wave_curves.append(BSplineCurve([
            start.position + start.normal * close_offset,
            start.position + start.normal * close_offset + start.tangent * control_distance,
            middle.position + middle.normal * far_offset - middle.tangent * control_distance,
            middle.position + middle.normal * far_offset,
        ]))
        wave_curves.append(BSplineCurve([
            middle.position + middle.normal * far_offset,
            middle.position + middle.normal * far_offset + middle.tangent * control_distance,
            finish.position + finish.normal * close_offset - finish.tangent * control_distance,
            finish.position + finish.normal * close_offset,
        ]))

    return Face(Offset2D(Wire(Edge(c) for c in wave_curves), min_wall_thickness / 2))


temple_block_from_forehead_center_distance = temple_block_start_distance - forehead_center_distance_on_headband_curve


@run_if_changed
def headband_waves():
    # +0.5 because the wave starts straight out in the normal direction, but the temple is angled back
    q = temple_block_from_forehead_center_distance - temple_block_length + 0.5
    face = twist_resistant_waves(
        headband_curve,
        forehead_center_distance_on_headband_curve + q,
        forehead_center_distance_on_headband_curve - q,
    )
    return extrude_flat_shape_to_headband(face)


temple_extender_width = 6


# Further back from the headband, near the ears, we add a strut that wants to be very strong (because it will be under the most torque) and have holes in it (for attaching the elastic).
# It needs to be long enough to exert good torque on the mask to prevent the mask from tilting up / down, but not so long that the back-of-head elastic is too short to stretch over the head easily.
@run_if_changed
def temple_extender():
    length = 60
    width = temple_extender_width
    wall_thickness = 1.5
    hoops = []
    potential_hole_hoops = []
    for distance in subdivisions(temple_block_start_distance - 17, temple_block_start_distance + length, amount=30):
        d = headband_curve.derivatives(distance=distance)
        a = d.position + Up * headband_top
        b = d.position + Up * headband_bottom
        k = -d.normal * width
        j = -d.normal * wall_thickness
        l = -d.normal * (width - wall_thickness)
        z = Up * 1
        hoops.append(Wire([
            a, b, b + k, a + k
        ], loop=True))
        potential_hole_hoops.append(Wire([
            a + z + j, b - z + j, b - z + l, a + z + l
        ], loop=True))
    result = Loft(hoops, solid=True)
    result = Fillet(result,
                    [(edge, width / 2.2) for edge in result.edges() if all_equal(v[1] for v in edge.vertices())])
    for foo in range(3):
        bar = 11 + foo * 6
        result = result.cut(Loft(potential_hole_hoops[bar:bar + 6], solid=True))

    return result


# We also need a little knob to tie the neck-elastic to.
z = -1.2
a = 0
b = 3
c = 5
s = -4
p = -1
q = 1
r = 4
temple_knob_coordinates = [
    (z, s), (a, s), (a, p), (b, p), (b, s), (c, s), (c, p), (c, q), (c, r), (b, r), (b, q), (a, q), (a, r), (z, r)
]


@run_if_changed
def temple_knob():
    hoop = []
    for x, y in temple_knob_coordinates:
        d = headband_curve.derivatives(distance=temple_block_start_distance + neck_leeway - y)
        hoop.append(d.position - d.normal * (temple_extender_width + x))
        hoop[-1][2]
    return Face(Wire(BSplineCurve(hoop, BSplineDimension(periodic=True)))).extrude(Up * (headband_bottom),
                                                                                   Up * (headband_bottom + 5))
