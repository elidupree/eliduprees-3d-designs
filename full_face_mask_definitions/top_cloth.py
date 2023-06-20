import math

from full_face_mask_definitions.headband import temple_distance_along_headband, temple_block_far_corner
from full_face_mask_definitions.shield_geometry import shield_top_curve
from full_face_mask_definitions.headband_geometry import headband_curve, headband_top
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
    learning_rate = 1
    shield_top_curve_middle = shield_top_curve.precomputed_length / 2
    shield_curve = shield_top_curve.curve @ Translate(Down * headband_top)
    headband_curve_middle = headband_curve.distance (closest = Point(0,500,0))#headband_curve.length() / 2

    initial_middle_distance = shield_curve.value(distance=shield_top_curve_middle).distance(
        headband_curve.value(distance=headband_curve_middle))
    target_middle_distance = initial_middle_distance * 1.15

    temple_block_far_corner_reference = temple_block_far_corner + Down*headband_top
    temple_block_relative_sample = headband_curve.derivatives(closest =temple_block_far_corner_reference)
    temple_block_corner_offset = temple_block_far_corner_reference - temple_block_relative_sample.position
    temple_block_corner_tangent_offset = temple_block_corner_offset.dot(temple_block_relative_sample.tangent)
    temple_block_corner_normal_offset = temple_block_corner_offset.dot(temple_block_relative_sample.normal)

    class Attempt:
        def __init__(self, shield_curvature, forehead_curvature):
            self.shield_curvature = shield_curvature
            self.forehead_curvature = forehead_curvature
            self.bent_shield = bent_curve(shield_curve, [shield_top_curve_middle,
                                          shield_top_curve.precomputed_length], shield_curvature)
            self.bent_forehead = bent_curve(headband_curve, [headband_curve_middle, temple_distance_along_headband], forehead_curvature)
            # self.temple_block
            self.bent_shield = [p + vector(0, self.bent_forehead[-1][1] - self.bent_shield[-1][1], 0) for p in
                                self.bent_shield]
            self.middle_distance = self.bent_shield[0].distance(self.bent_forehead[0])
            self.middle_distance_change_need = target_middle_distance - self.middle_distance
            self.relative_change_need_for_shield = self.bent_forehead[-1][0] - self.bent_shield[-1][0]

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
        #print (initial_middle_distance,latest_attempt.middle_distance_change_need, forehead_curvature, shield_curvature)
        latest_attempt = Attempt(shield_curvature, forehead_curvature)

