import math

from pyocct_system import *
initialize_pyocct_system()

filter_max_length = 151.9
filter_width = 101
filter_rim_inset = 5
filter_insertion_depth = 18.5
filter_squished_depth = 17
filter_squish_distance = filter_insertion_depth-filter_squished_depth


wall_thickness = 1.0
frame_thickness = 7
rod_radius = 2
cam_max_diameter = filter_rim_inset + 10
cam_max_radius = cam_max_diameter/2
cam_overshoot_distance = 0.5
cam_min_radius = cam_max_radius - cam_overshoot_distance - filter_squish_distance
handle_thickness = 2
handle_length = (frame_thickness*2 + filter_squished_depth)*0.8
handle_fillet_width = 1
cam_contact_pad_width = 2*(cam_max_radius - handle_thickness - handle_fillet_width)

max_overhang_slope = 2

# origin = (center of rod, center of filter, top edge of filter) I guess?
# fillet_turns = asin((cam_contact_pad_width/2 + handle_fillet_distance)/cam_max_radius).turns
cam_center = Point(0, 0, cam_max_radius + frame_thickness)

frame_length = filter_max_length+wall_thickness*2

@run_if_changed
def rod_axial_profile():
    return Face(Circle(Axes(cam_center, Front), rod_radius))

@run_if_changed
def rod():
    return rod_axial_profile.extrude(Front*frame_length, centered=True)

@run_if_changed
def cam_axial_profile():
    half_pad_turns = asin((cam_contact_pad_width/2)/cam_max_radius).turns
    print(half_pad_turns)
    cam_radius_points = [
        (-half_pad_turns, cam_max_radius),
        (-half_pad_turns/2, cam_max_radius - cam_overshoot_distance),
        (0, cam_max_radius - cam_overshoot_distance),
        (half_pad_turns/2, cam_max_radius - cam_overshoot_distance),
        (half_pad_turns, cam_max_radius),
        (half_pad_turns+0.1, cam_max_radius),
        (0.4, cam_min_radius),
        (0.5, cam_min_radius),
        (0.6, cam_min_radius),
        (0.75, cam_max_radius),
        ]
    cam_radius_curve = BSplineCurve([Point(a,0,-r) for a,r in cam_radius_points])
    # preview(cam_radius_curve)
    return Face(Wire(BSplineCurve([cam_radius_curve.position(x=t) @ Rotate(Front, Turns(t)) @ Translate(cam_center-Origin) for t in subdivisions(-half_pad_turns, 0.75, amount=30)] + [
        Point(-cam_max_radius, 0, -handle_length+2),
        Point(-cam_max_radius, 0, -handle_length),
        Point(-cam_max_radius+handle_thickness, 0, -handle_length),
        Point(-cam_max_radius+handle_thickness, 0, -handle_length+2),
        Point(-cam_max_radius+handle_thickness, 0, frame_thickness),
        Point(-cam_max_radius+handle_thickness, 0, frame_thickness+1),
    ], BSplineDimension(periodic=True))))


cutaway_slant_length = (cam_max_radius*2 - handle_thickness)/max_overhang_slope
strut_thickness=5
d = frame_length/2 - strut_thickness*2.5 - cutaway_slant_length
strut_center_ys = subdivisions(-d, d, amount=4)

@run_if_changed
def cam():
    profile = cam_axial_profile.cut(rod_axial_profile)
    cutaway_for_strut = Face(Wire([
        Point(cam_max_radius, -strut_thickness/2-cutaway_slant_length, 0),
        Point(cam_max_radius, strut_thickness/2+cutaway_slant_length, 0),
        Point(-(cam_max_radius-handle_thickness-0.001), strut_thickness/2, 0),
        Point(-(cam_max_radius-handle_thickness-0.001), -strut_thickness/2, 0),
    ], loop=True)).extrude(Up*100, centered=True)
    result = profile.extrude(Front*frame_length, centered=True)
    # preview(result, cutaway_for_strut)
    result = result.cut([cutaway_for_strut @ Translate(Back*y) for y in strut_center_ys])
    return result

strut_width = (cam_max_radius - handle_thickness - wall_thickness - 0.4)*2
@run_if_changed
def strut():
    profile = Union(
        Face(Circle(Axes(cam_center, Front), strut_width/2)),
        Vertex(cam_center).extrude(Right*strut_width, centered=True).extrude(Down*(cam_center[2] + filter_squished_depth)),
    )
    rod_hole_octagonized = Union(
        rod_axial_profile,
        Vertex(cam_center).extrude(Right*rod_radius*2, centered=True).extrude(Up*rod_radius).cut([HalfSpace(cam_center + d*rod_radius, d) for d in [Direction(-1,0,1), Direction(1,0,1)]]),
    )
    profile = profile.cut(rod_hole_octagonized)
    return profile.extrude(Back*strut_thickness, centered=True)

@run_if_changed
def struts():
    return Compound([strut @ Translate(Back*y) for y in strut_center_ys])
# @run_if_changed
# def bottom_part():
#
#

@run_if_changed
def top_part_long_edge():
    profile = Vertex(Origin).extrude(Left*(cam_max_radius - handle_thickness - 0.2), Right*(cam_max_radius+wall_thickness)).extrude(Up*(frame_thickness+3))
    profile = profile.cut(cam_axial_profile)
    result = profile.extrude(Front*frame_length, centered=True)
    strut_hole = Vertex(cam_center).extrude(Right*(strut_width+0.4), centered=True).extrude(Down*100, centered=True).extrude(Back*(strut_thickness+0.4), centered=True)
    result = result.cut([strut_hole @ Translate(Back*y) for y in strut_center_ys])
    return result


preview(cam, struts, top_part_long_edge)
