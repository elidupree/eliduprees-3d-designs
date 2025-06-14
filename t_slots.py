from pyocct_system import *

lip_thickness_range = (1.8, 1.9)
slot_depth_range = (6.1, 6.2)
entrance_width_range = (6.2, 6.3)
undercut_width_range = (10.88, 10.95)
undercut_depth_approximate = 1.6
bottom_width_approximate = 5.4
entrance_chamferish_width_approx = 7.15
# inset the entrance because it's always going to be 3D-printed as a concave corner, which tends to get tugged into the space that's supposed to be empty
default_entrance_inset = 0.2

def _half_t_profile_points_and_round_distances(entrance_inset = default_entrance_inset):
    return [
        (Point(entrance_width_range[0]/2 - entrance_inset, lip_thickness_range[1] + entrance_inset, 0), 0.1),
        (Point(undercut_width_range[0]/2, lip_thickness_range[1], 0), 0.2),
        (Point(undercut_width_range[0]/2, lip_thickness_range[1] + undercut_depth_approximate, 0), 0.2),
        (Point(bottom_width_approximate/2, slot_depth_range[0], 0), 0.5),
    ]
def _curve_from_half(half_points_and_round_distances):
    half_points = []
    for i, (point, round_distance) in enumerate(half_points_and_round_distances):
        half_points.append(point)
        if i+1 < len(half_points_and_round_distances):
            next_point, next_round_distance = half_points_and_round_distances[i+1]
            direction = Direction (point, next_point)
            half_points.append(point + direction * round_distance)
            half_points.append(next_point - direction * next_round_distance)
        else:
            half_points.append(point + Left * round_distance)

    return BSplineCurve(half_points + [p @ Mirror(Right) for p in half_points[::-1]])

def t_profile_curve_straight(entrance_inset = default_entrance_inset):
    return _curve_from_half(
    [
        (Point(entrance_width_range[0]/2 - entrance_inset, 0, 0), 0.1),
    ] + _half_t_profile_points_and_round_distances(entrance_inset)
)
def t_profile_curve_flared(entrance_inset = default_entrance_inset):
    return _curve_from_half(
    [
        (Point(entrance_chamferish_width_approx/2, 0, 0), 0.1),
        (Point(entrance_width_range[0]/2 - entrance_inset, 0, 0), 0.2),
    ] + _half_t_profile_points_and_round_distances(entrance_inset)
)

def t_profile_straight(entrance_inset = default_entrance_inset):
    return Face(Wire(t_profile_curve_straight(entrance_inset), loop = True))

def t_profile_flared(entrance_inset = default_entrance_inset):
    return Face(Wire(t_profile_curve_flared(entrance_inset), loop = True))