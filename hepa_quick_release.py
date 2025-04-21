import math

from pyocct_system import *
from pyocct_utils import circleish_rect_points, two_BSplineSurfaces_to_solid, flat_ended_tube_BSplineSurface_to_solid
initialize_pyocct_system()

filter_max_length = 151.9
filter_max_width = 101
filter_rim_inset = 5
filter_insertion_depth = 18.5
filter_squished_depth = 17
filter_squish_distance = filter_insertion_depth-filter_squished_depth


wall_thickness = 1.0
frame_height = 10
frame_thickness = 5
rod_radius = 1.7
cam_max_diameter = filter_rim_inset + 10
cam_max_radius = cam_max_diameter/2
cam_overshoot_distance = 0.5
cam_min_radius = cam_max_radius - cam_overshoot_distance - filter_squish_distance
handle_thickness = 2
handle_length = (frame_thickness + filter_squished_depth)*0.8
handle_fillet_width = 1
cam_contact_pad_width = 2*(cam_max_radius - handle_thickness - handle_fillet_width)

max_overhang_slope = 1
cam_overshoot_distance_with_leeway = cam_overshoot_distance + 0.2
filter_overshot_squished_depth_with_leeway = filter_squished_depth - cam_overshoot_distance_with_leeway

# origin = (center of rod, center of filter, top edge of filter) I guess?
# fillet_turns = asin((cam_contact_pad_width/2 + handle_fillet_distance)/cam_max_radius).turns
cam_center = Point(0, 0, cam_max_radius + frame_height-3)

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
        Point(-cam_max_radius+handle_thickness, 0, frame_height-3),
        Point(-cam_max_radius+handle_thickness, 0, frame_height-2),
    ], BSplineDimension(periodic=True))))


cutaway_slant_length = (cam_max_radius*2 - handle_thickness)/max_overhang_slope
strut_thickness=5
d = frame_length/2 - strut_thickness*2.5 - cutaway_slant_length/2
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

strut_width = (rod_radius+wall_thickness)*2
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

filter_left_rim_inner_x = max(cam_max_radius+wall_thickness, strut_width/2 +  filter_rim_inset)
print(cam_max_radius+wall_thickness, strut_width/2 + filter_rim_inset, filter_left_rim_inner_x)
frame_left_inner_x = filter_left_rim_inner_x - filter_rim_inset
filter_center_top = Point(frame_left_inner_x + filter_max_width / 2, 0, 0)

@run_if_changed
def spring_hole():
    standard_compressed_length = 4.8
    return Face(Circle(Axes(Origin + Down*cam_overshoot_distance_with_leeway/2, Up), 1.3)).extrude(Down*standard_compressed_length, centered=True)

@run_if_changed
def spring_holes():
    return [spring_hole @ Translate(Back*d*(frame_length - (frame_thickness+wall_thickness))/2) for d in [1,-1]]


# @run_if_changed
# def spring_peg_holes():
#     hole =

@run_if_changed
def top_part_long_edge():
    profile = Vertex(Origin).extrude(Left*(cam_max_radius - handle_thickness - 0.2), Right*filter_left_rim_inner_x).extrude(Up*frame_height)
    profile = profile.cut(cam_axial_profile)
    result = profile.extrude(Front*frame_length, centered=True)
    strut_hole = Vertex(cam_center).extrude(Right*(strut_width+0.4), centered=True).extrude(Down*100, centered=True).extrude(Back*(strut_thickness+0.4), centered=True)
    result = result.cut([strut_hole @ Translate(Back*y) for y in strut_center_ys] + spring_holes)
    # end_stop_profile = Union(
    #     Face(Circle(Axes(cam_center, Front), cam_min_radius)),
    #     Vertex(cam_center).extrude(Right*cam_min_radius*2, centered=True).extrude(Down*(cam_center[2])),
    # )
    # end_stop = end_stop_profile.extrude(Front*frame_length, Front*(frame_length - strut_thickness))
    # result = Compound(result, )
    return result

@run_if_changed
def top_part_short_edge():
    outer_corner = filter_center_top + Front*frame_length/2 + Up*frame_height
    return Vertex(outer_corner).extrude(Back*(wall_thickness+filter_rim_inset)).extrude(Down*frame_height).extrude(Left*(filter_max_width - filter_rim_inset*2), centered=True)

@run_if_changed
def bottom_part_long_edge():
    outer_corner = Origin + Down*(filter_squished_depth+frame_height)
    profile = Union(
        Vertex(outer_corner).extrude(Left*(strut_width/2),  Right*frame_left_inner_x).extrude(Up*(filter_overshot_squished_depth_with_leeway+frame_height)),
        Vertex(outer_corner).extrude(Left*(strut_width/2), Right*filter_left_rim_inner_x).extrude(Up*frame_height),
    )
    result = profile.extrude(Front*frame_length, centered=True)
    result = result.cut([HalfSpace(outer_corner, Direction(-1, 0, -1))] + spring_holes)
    result = Compound(result, struts)
    return result

@run_if_changed
def bottom_part_short_edge():
    outer_corner = filter_center_top + Front*frame_length/2 + Down*(filter_squished_depth+frame_height)
    result = Vertex(outer_corner).extrude(Back*(wall_thickness+filter_rim_inset)).extrude(Up*frame_height).extrude(Left*(filter_max_width - filter_rim_inset*2), centered=True)

    # result = result.cut(HalfSpace(outer_corner + Vector(0, 2, 2), Direction(0, -1, -1)))
    return result


@run_if_changed
def top_part():
    half = Compound(top_part_long_edge, top_part_short_edge)
    # outer_corner = filter_center_top + Front*frame_length/2 + Down*(filter_squished_depth+frame_height)
    return Compound(
        half,
        half @ Rotate(Axis(filter_center_top, Up), Degrees(180)),
        # Vertex(outer_corner).extrude(Back*(wall_thickness)).extrude(Up*(frame_height + filter_squished_depth - filter_squish_distance - 0.2)).extrude(Left*filter_max_width, centered=True)
    )

@run_if_changed
def bottom_part():
    half = Compound(bottom_part_long_edge, bottom_part_short_edge)
    return Compound(half, half @ Rotate(Axis(filter_center_top, Up), Degrees(180)))


def top_part_to_small_circle(cir_max_ir, join_len, taper):
    # related to under_door_adapter_pyocct.small_hose_spout
    rect_width = (filter_max_width - filter_rim_inset*2)
    rect_length = (filter_max_length - filter_rim_inset*2)
    target_slope = 1.5
    cir_height = (rect_length/2 - cir_max_ir) * target_slope
    wslope = cir_height / (rect_width/2 - cir_max_ir)
    # def cir(p):
    #     return Wire (Edge (Circle (Axes (filter_center_top + Up*p[2], Up), p[0])))
    # def solid(outset_from_airspace):
    #     hoops = [Vertex(filter_center_top + Up*z).extrude(Left*(rect_width + (outset_from_airspace - z/wslope)*2), centered=True).extrude(Back*(rect_length + (outset_from_airspace - z/target_slope)*2), centered=True).outer_wire() for z in subdivisions(0, cir_height/3, amount=7)] + [cir(p) @ Translate(Up*cir_height) for p in subdivisions(Point(25+outset_from_airspace, 0, 0), Point((cir_max_rad - taper)+outset_from_airspace, 0, join_len), amount=7)]
    #     # preview(hoops)
    #     return Loft (
    #         hoops
    #         , solid=True
    #     )
    # return solid(wall_thickness).cut(solid(0))
    def surface(outset_from_airspace):
        rows = [circleish_rect_points(width = rect_width + (outset_from_airspace - z/wslope)*2, length = rect_length + (outset_from_airspace - z/target_slope)*2, amount=30, center=filter_center_top + Up*z, corner_copies = 2) for z in subdivisions(0, cir_height/3, amount=2)] + [Circle (Axes (filter_center_top + Up*(cir_height + p[2]), Up), p[0]).subdivisions(amount=30) for p in subdivisions(Point(25+outset_from_airspace, 0, 0), Point((cir_max_ir - taper)+outset_from_airspace, 0, join_len), amount=5)]
        return BSplineSurface(rows, v = BSplineDimension(periodic=True))
    outer_surface = surface(wall_thickness)
    inner_surface = surface(0)
    outer_surface.VReverse()
    outer_solid = flat_ended_tube_BSplineSurface_to_solid(outer_surface)
    support = Vertex(filter_center_top).extrude(Left*rect_width, centered=True).extrude(Back*rect_length, centered=True).extrude(Up*frame_height)
    # preview(outer_solid, support)
    support = support.cut(outer_solid @ Translate(Down*0.01))
    # preview(support)
    tube = two_BSplineSurfaces_to_solid(outer_surface, inner_surface)
    return Compound(support, tube)

@run_if_changed
def top_part_to_air_heater():
    return Compound(top_part, top_part_to_small_circle(25-wall_thickness, 40, 1))



test_region = Vertex(0, 45, 0).extrude(Left*20, Right*20).extrude(Back*50).extrude(Up*30, Down*40)


# save_STL("bottom_part_test", bottom_part.intersection(test_region))
# export("bottom_part_test.stl", "bottom_part_test_2.stl")
# save_STL("top_part_test", top_part.intersection(test_region))
# export("top_part_test.stl", "top_part_test_2.stl")
# save_STL("cam_test", cam.intersection(test_region))
# export("cam_test.stl", "cam_test_2.stl")


# save_STL("bottom_part", bottom_part)
# export("bottom_part.stl", "bottom_part_1.stl")
# save_STL("top_part", top_part)
# export("top_part.stl", "top_part_1.stl")
# save_STL("cam", cam)
# export("cam.stl", "cam_1.stl")

save_STL("top_part_to_air_heater", top_part_to_air_heater)
export("top_part_to_air_heater.stl", "top_part_to_air_heater_1.stl")

preview(cam, top_part, bottom_part, test_region.wires(), top_part_to_air_heater)