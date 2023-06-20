import math

from full_face_mask_definitions.headband import temple_distance_along_headband, temple_block_far_corner, temple_block_near_corner
from full_face_mask_definitions.shield_geometry import shield_top_curve
from full_face_mask_definitions.headband_geometry import headband_curve, headband_top, headband_curve_middle
from pyocct_system import *

del Front, Back


# For the top cloth, whose natural position is flat, we basically want to shape it as-is. But, for someone whose head is a little bigger than mine, the cloth also wants to be bigger. Experimentally, I think we want it to be 15% longer from the center of the forehead to the center of the face shield. (Smaller heads are already fine, because the cloth can scrunch.)
#
# There are many degrees of freedom in the exact shape, so we have to make some arbitrary choices. The main requirement is that all of the edges be the correct lengths; secondarily, we would like to make the curvature at the edges match the solid parts as well as possible, to minimize issues during assembly.
#
# The exact math would be complex to figure out, so we just do iterative approximations. Given a "curvature adjustment" as an input, we can generate a "bent" version of either edge, which gives us the distance between the endpoints of that new edge. Given a pair (adjusted forehead edge, adjusted shield edge), there are 2 kinds of wrongness: The middle-to-middle distance can disagree with our target (meaning we should curl both edges in the same direction), and the end-to-end distances can disagree with each other (meaning we should curl them in opposite directions). It's possible that either of these will "overshoot" and make the wrongness worse; we can just use dynamic learning rate adjustment to avoid overshooting.

def bent_curve(curve, endpoint_distances, curvature_adjustment):
    result = [Origin]
    latest_rotation = Rotate(Up, radians=0)
    for (d1, d2) in pairs(subdivisions(*endpoint_distances, max_length=2)):
        p1 = curve.value(distance=d1)
        p2 = curve.value(distance=d2)
        half_rotation = Rotate(Up, radians=curvature_adjustment * (d2 - d1) / 2)
        full_rotation = Rotate(Up, radians=curvature_adjustment * (d2 - d1))
        result.append(result[-1] + ((p2 - p1) @ latest_rotation @ half_rotation))
        latest_rotation = latest_rotation @ full_rotation
    return result


@run_if_changed
def stretched_curves():
    shield_curvature = 0
    forehead_curvature = 0
    shield_top_curve_middle = shield_top_curve.precomputed_length / 2
    shield_curve = shield_top_curve.curve @ Translate(Down * headband_top)
    shield_curve_end = shield_curve.distance(closest=temple_block_far_corner)
    headband_curve_end = headband_curve.distance(closest=temple_block_near_corner)

    initial_middle_distance = shield_curve.value(distance=shield_top_curve_middle).distance(
        headband_curve.value(distance=headband_curve_middle))
    target_middle_distance = initial_middle_distance * 1.15

    temple_block_near_corner_sample = headband_curve.derivatives(distance=headband_curve_end)
    temple_block_corner_offset = temple_block_far_corner - temple_block_near_corner_sample.position
    temple_block_corner_tangent_offset = temple_block_corner_offset.dot(temple_block_near_corner_sample.tangent)
    temple_block_corner_normal_offset = temple_block_corner_offset.dot(temple_block_near_corner_sample.normal)

    class Attempt:
        def __init__(self, shield_curvature, forehead_curvature):
            self.shield_curvature = shield_curvature
            self.forehead_curvature = forehead_curvature
            self.bent_shield = bent_curve(shield_curve, [shield_top_curve_middle,
                                                         shield_curve_end], shield_curvature)
            self.bent_forehead = bent_curve(headband_curve, [headband_curve_middle, headband_curve_end],
                                            forehead_curvature)
            t = BSplineCurve(self.bent_forehead).derivatives(distance=headband_curve_end)
            self.temple_block_far_corner = t.position + t.tangent * temple_block_corner_tangent_offset + t.normal * temple_block_corner_normal_offset
            self.bent_shield = [p + vector(0, self.temple_block_far_corner[1] - self.bent_shield[-1][1], 0) for p in
                                self.bent_shield]
            self.middle_distance = self.bent_shield[0].distance(self.bent_forehead[0])
            self.middle_distance_change_need = target_middle_distance - self.middle_distance
            self.relative_change_need_for_shield = self.temple_block_far_corner[0] - self.bent_shield[-1][0]

    latest_attempt = Attempt(shield_curvature, forehead_curvature)
    # visuals = []
    print("Bent curve error:")
    while abs(latest_attempt.middle_distance_change_need) > 0.1 or abs(
            latest_attempt.relative_change_need_for_shield) > 0.01:
        print(abs(latest_attempt.middle_distance_change_need), abs(
            latest_attempt.relative_change_need_for_shield))
        # visuals.extend ([BSplineCurve(latest_attempt.bent_shield),BSplineCurve(latest_attempt.bent_forehead)])
        # if len (visuals) > 20:
        #     preview (visuals)
        forehead_curvature += latest_attempt.middle_distance_change_need * 0.0003
        shield_curvature += latest_attempt.relative_change_need_for_shield * 0.00003
        # print (initial_middle_distance,latest_attempt.middle_distance_change_need, forehead_curvature, shield_curvature)
        latest_attempt = Attempt(shield_curvature, forehead_curvature)

    return latest_attempt.bent_shield,latest_attempt.bent_forehead


# Having calculated the half-curves, we can now lay out the top cloth, which is the full curves, joined by straight lines, and with a small leeway around all edges for practicalities of sewing.
top_cloth_leeway = 6
@run_if_changed
def top_cloth():
    a,b = stretched_curves
    exact_wire = Wire ([
        BSplineCurve([p @ Reflect(Right) for p in a[:0:-1]] + a),
        Edge(a[-1],b[-1]),
        BSplineCurve(b[:0:-1] + [p @ Reflect(Right) for p in b]),
        Edge(b[-1],a[-1]) @ Reflect(Right),
    ])
    result = exact_wire.offset2D(top_cloth_leeway)
    save_inkscape_svg("top_cloth", result)
    return result
