import math

from pyocct_system import *

initialize_pyocct_system()

from air_adapters import elidupree_4in_output_outer_radius
from pyocct_utils import wallify

lots = 500
inch = 25.4

strong_filter_length = 152
strong_filter_width = 101
strong_filter_rim_inset = 6

fan_thickness = 28
fan_width = 79.7
fan_length = 78.9
fan_exit_width = 26
fan_exit_length = 8

battery_thickness = 27.8
battery_width = 85.5
battery_length = 144.2
battery_cord_diameter = 3.5
battery_plug_diameter = 11.4
battery_plug_length = 38.2
cords_space = 25

fan_socket_thickness = 11.5
fan_socket_width = 13.7
fan_socket_length = 36.3

CPAP_outer_radius = 21.5 / 2

flat_wall_thickness = inch * 0.030

screw_radius = 1.5
screw_headspace_radius = 3.5
screw_headspace_depth = 3
screw_print_contact_leeway = 0.3
threaded_insert_hole_radius = 2.4
threaded_insert_opening_radius = 2.9
threaded_insert_depth = 4
holder_radius = 4.5

frame_outer_zigzag_width = 0.6

# screw_offset = strong_filter_length / 4
screw_filter_contact_leeway = 1

plate_thickness = 10

threaded_insert_bracket, screw_bracket, threaded_insert_bracket_cuts, screw_bracket_cuts, bracket_protrusion_length = None, None, None, None, None


@run_if_changed
def brackets():
    global threaded_insert_bracket, screw_bracket, threaded_insert_bracket_cuts, screw_bracket_cuts, bracket_protrusion_length
    screw_center = Origin + Left * max(screw_radius + screw_filter_contact_leeway,
                                       holder_radius - strong_filter_rim_inset)

    bracket_protrusion_length = -screw_center[0] + holder_radius

    cylinder = Face(Circle(Axes(screw_center, Up), holder_radius)).extrude(Up * plate_thickness)
    a = screw_center + Direction(-1, -1, 0) * holder_radius
    b = a + Vector(1, - 1, 0) * -a[0]
    frustum = Face(Wire([
        b, a, a @ Mirror(Back), b @ Mirror(Back)
    ], loop=True)).extrude(Up * plate_thickness)

    screw_hole = Face(Circle(Axes(screw_center, Up), screw_radius + screw_print_contact_leeway)).extrude(
        Up * plate_thickness)
    threaded_insert_hole = Face(Wire([
        screw_center,
        screw_center + Right*threaded_insert_opening_radius,
        screw_center + Right*threaded_insert_hole_radius + Up*1.2,
        screw_center + Right*threaded_insert_hole_radius + Up*plate_thickness,
        screw_center + Up*plate_thickness,
    ], loop=True)).revolve(Axis(screw_center, Up))
    screw_head_hole = Face(Circle(Axes(screw_center, Up), screw_headspace_radius + screw_print_contact_leeway)).extrude(
        Up * 2, Up * plate_thickness)
    # nut_hole = Face(Wire([
    #     Point((nut_short_radius + screw_print_contact_leeway) / math.cos(math.tau / 12), 0, nut_holder_thickness)
    #     @ Rotate(Up, degrees=i * 60)
    #     for i in range(6)
    # ], loop=True)).extrude(Up * plate_thickness) @ Translate(screw_center - Origin)

    threaded_insert_cutaway = HalfSpace(screw_center + Left * threaded_insert_hole_radius + Up * threaded_insert_depth,
                                        Direction(-1, 0, 1))
    screw_cutaway = HalfSpace(screw_center + Left * screw_headspace_radius + Up * screw_headspace_depth,
                              Direction(-1, 0, 1))
    screw_bracket_cuts = Compound(screw_hole, screw_head_hole)
    threaded_insert_bracket_cuts = threaded_insert_hole

    # sacrificial_bridge = Face (Circle (Axes(screw_center + Up*nut_holder_thickness, Up), screw_radius+ screw_print_contact_leeway)).extrude (Down*0.28)

    threaded_insert_bracket = Compound(cylinder, frustum).cut([
        threaded_insert_hole, threaded_insert_cutaway
    ])
    screw_bracket = Compound(cylinder, frustum).cut([
        screw_hole, screw_head_hole, screw_cutaway
    ])
    preview (threaded_insert_bracket)


def zigzag_loop_control_points(points, right_hand_offset):
    result = []
    for a, b in pairs(points, loop=True):
        along = Direction(b - a)
        l = a.distance(b)
        perpendicular = along @ Rotate(Up, degrees=-90)
        control_points = []
        marks = subdivisions(0, l, max_length=5, require_parity=1)
        for i, d in enumerate(marks):
            c = a + along * d
            if i == 0 or i == len(marks) - 1:
                control_points.append(c)
            elif i % 2 == 0:
                control_points.append(c - perpendicular * right_hand_offset)
            else:
                control_points.append(c + perpendicular * right_hand_offset * 2)
        result.append(control_points)
    return result


def zigzag_loop(points, right_hand_offset):
    return Wire([BSplineCurve(p) for p in zigzag_loop_control_points(points, right_hand_offset)])


def rectangle_points(o1, o2):
    return [
        Origin + o1 + o2,
        Origin - o1 + o2,
        Origin - o1 - o2,
        Origin + o1 - o2,
    ]


@run_if_changed
def frame():
    result = Face(zigzag_loop(rectangle_points(Right * strong_filter_width / 2, Back * strong_filter_length / 2),
                              frame_outer_zigzag_width)) \
        .extrude(Up * plate_thickness)

    cut = Face(zigzag_loop(rectangle_points(
        Right * (strong_filter_width / 2 - strong_filter_rim_inset),
        Back * (strong_filter_length / 2 - strong_filter_rim_inset)
    ), -frame_outer_zigzag_width)) \
        .extrude(Up * plate_thickness)
    # old_cut = Vertex(Origin) \
    #     .extrude(Left * (strong_filter_width - strong_filter_rim_inset * 2), centered=True) \
    #     .extrude(Back * (strong_filter_length - strong_filter_rim_inset * 2), centered=True) \
    #     .extrude(Up * plate_thickness)
    # preview(cut, old_cut)

    result = result.cut(cut)
    result = Fillet(result, [(e, 2) for e in result.edges() if all_equal((v[0], v[1]) for v in e.vertices())])
    return result


frame_full_width = strong_filter_width + 2 * frame_outer_zigzag_width
frame_full_length = strong_filter_length + 2 * bracket_protrusion_length


# @run_if_changed
# def reinforcement():
#     edge = Edge(BSplineCurve([
#         Point(0, 0, 0),
#         Point(0, 3, plate_thickness / 2),
#         Point(0, 0, plate_thickness),
#     ], BSplineDimension(degree=2)))
#
#     cross_section = Face(Wire(edge, edge @ Mirror(Back)))
#
#     return cross_section.extrude(Left * (strong_filter_width - strong_filter_rim_inset * 2), centered=True)

def filter_plate(bracket, bracket_cuts):
    b1 = bracket @ Rotate(Up, degrees=90) @ Translate(Front * (strong_filter_length / 2))
    c1 = bracket_cuts @ Rotate(Up, degrees=90) @ Translate(Front * (strong_filter_length / 2))
    # r1 = reinforcement @ Translate(Back*screw_offset)
    result = Compound([
        b1,
        b1 @ Mirror(Back),
        # r1,
        # r1 @ Mirror(Back),
        frame.cut([
            c1,
            c1 @ Mirror(Back),
        ])
    ])
    return result


@run_if_changed
def screw_filter_plate():
    result = filter_plate(screw_bracket, screw_bracket_cuts)
    save_STL("screw_filter_plate", result)
    return result


@run_if_changed
def threaded_insert_filter_plate():
    result = filter_plate(threaded_insert_bracket, threaded_insert_bracket_cuts)
    save_STL("threaded_insert_filter_plate", result)
    return result


@run_if_changed
def bracket_tests():
    local_area = Face(Circle(Axes(Origin + Back * (strong_filter_length / 2 + screw_radius), Up), 10)).extrude(
        Up * lots,
        centered=True)
    screw_bracket_test = screw_filter_plate.intersection(local_area)
    threaded_insert_bracket_test = threaded_insert_filter_plate.intersection(local_area)
    save_STL("screw_bracket_test", screw_bracket_test)
    save_STL("threaded_insert_bracket_test", threaded_insert_bracket_test)
    preview(screw_bracket_test, threaded_insert_bracket_test @ Translate(Right * 20))


@run_if_changed
def elidupree_4in_connector():
    wall_thickness = 0.5
    zig = zigzag_loop(rectangle_points(
        Right * (strong_filter_width / 2 - strong_filter_rim_inset + wall_thickness + 1.8),
        Back * (strong_filter_length / 2 - strong_filter_rim_inset + wall_thickness + 1.8)
    ), -1.8)
    row0 = points_along_wire(zig, max_length=2)  # [p for edge in z for p in edge[:-1]]
    rows = [
        row0
    ]
    for z in [25, 50, 60, 75]:
        rows.append([Origin + Up * z + Direction(p - Origin) * elidupree_4in_output_outer_radius for p in row0])

    # deliberately expanding the wall inwards, because we need the outer radius correct
    return wallify(rows, thickness=wall_thickness, loop=True) @ Translate(Up * plate_thickness)


# @run_if_changed
# def screw_filter_plate_to_elidupree_4in():
#     result = Compound(screw_filter_plate, elidupree_4in_connector)
#     save_STL("screw_filter_plate_to_elidupree_4in", result)
#     return result


# For the PAPR:
#
# the biggest landmark is the wall surrounding the main air chamber; we shall make 0, 0, 0 the corner of the airspace before the prefilter.

putative_inplace_filter2_thickness_with_padding = 18

prefilter_airspace_front_y = 0
prefilter_airspace_right_x = 0
main_airspace_top_z = 0
prefilter_airspace_left_x = prefilter_airspace_right_x - frame_full_width
filter2_plate1_right_x = prefilter_airspace_left_x - flat_wall_thickness
filter2_plate2_left_x = filter2_plate1_right_x - putative_inplace_filter2_thickness_with_padding - plate_thickness * 2
filter2_center_y = prefilter_airspace_front_y + frame_full_width / 2

prefilter_airspace_back_y = prefilter_airspace_front_y + frame_full_width - flat_wall_thickness * 2

prefilter_front_y = prefilter_airspace_front_y + 15
prefilter_back_y = prefilter_front_y + 16
prefilter_plate2_back_y = prefilter_back_y + plate_thickness

main_airspace_height = strong_filter_length - strong_filter_rim_inset * 2 + flat_wall_thickness * 2
main_airspace_bottom_z = main_airspace_top_z - main_airspace_height
filters_vertical_center = Between(main_airspace_top_z, main_airspace_bottom_z)
filters_absolute_top = main_airspace_top_z + (frame_full_length - main_airspace_height) / 2
covered_top = filters_absolute_top

fan_center_y = Between(prefilter_plate2_back_y, prefilter_airspace_back_y)
fan_front_y = fan_center_y - fan_thickness / 2
fan_back_y = fan_center_y + fan_thickness / 2
fan_body_left_x = filter2_plate1_right_x + (fan_front_y - prefilter_plate2_back_y)
fan_exit_left_x = fan_body_left_x + fan_exit_length
fan_bottom_z = main_airspace_bottom_z
fan_top_z = fan_bottom_z + fan_width

battery_top = covered_top
battery_left = prefilter_airspace_right_x + flat_wall_thickness
battery_front = prefilter_airspace_front_y + flat_wall_thickness
battery_back = battery_front + battery_width
battery_right = battery_left + battery_thickness
battery_bottom = battery_top - battery_length

covered_bottom = battery_bottom - battery_plug_length
covered_right = battery_right + flat_wall_thickness
covered_left = filter2_plate2_left_x - 5
covered_front = filter2_center_y - frame_full_width/2
covered_back = filter2_center_y + frame_full_width/2

@run_if_changed
def papr_filter2_plate1():
    return threaded_insert_filter_plate @ Transform(Back, Up, Right) @ Translate(
        Vector(filter2_plate1_right_x - plate_thickness, filter2_center_y,
               filters_vertical_center))


@run_if_changed
def papr_filter2_plate2():
    return screw_filter_plate @ Transform(Back, Up, Left) @ Translate(
        Vector(filter2_plate2_left_x + plate_thickness, filter2_center_y,
               filters_vertical_center))


@run_if_changed
def papr_prefilter_plate2():
    return threaded_insert_filter_plate @ Transform(Left, Up, Back) @ Translate(
        Vector(Between(prefilter_airspace_left_x, prefilter_airspace_right_x), prefilter_back_y,
               filters_vertical_center))


main_airspace_top_wire_points = [
    Point(prefilter_airspace_right_x, prefilter_plate2_back_y),
    Point(prefilter_airspace_left_x - flat_wall_thickness, prefilter_plate2_back_y),
    Point(prefilter_airspace_left_x - flat_wall_thickness, prefilter_airspace_back_y),
    Point(prefilter_airspace_right_x, prefilter_airspace_back_y),
]

main_wall1_top_inner_wire_points = [
    Point(prefilter_airspace_left_x, prefilter_airspace_front_y),
    Point(prefilter_airspace_left_x, prefilter_plate2_back_y),
    Point(fan_body_left_x, fan_front_y),
    Point(fan_body_left_x, fan_back_y),
    Point(prefilter_airspace_left_x, prefilter_airspace_back_y),
    # Point(prefilter_airspace_right_x, prefilter_airspace_back_y),
    # Point(prefilter_airspace_right_x, prefilter_airspace_front_y),
]
main_wall2_top_inner_wire_points = [
    Point(prefilter_airspace_left_x - flat_wall_thickness, prefilter_airspace_back_y),
    Point(prefilter_airspace_right_x, prefilter_airspace_back_y),
    Point(prefilter_airspace_right_x, prefilter_airspace_front_y),
]


@run_if_changed
def main_airspace_top_face():
    return Face(Wire(main_airspace_top_wire_points, loop=True)).extrude(Up * flat_wall_thickness)


@run_if_changed
def main_airspace_bottom_face():
    return Face(Wire(main_airspace_top_wire_points, loop=True)).extrude(Down * flat_wall_thickness) @ Translate(
        Down * main_airspace_height)


@run_if_changed
def main_wall1():
    # preview(Wire(main_wall1_top_inner_wire_points))
    # return Wire(main_wall1_top_inner_wire_points).offset2D(flat_wall_thickness, fill=True).extrude(Up * flat_wall_thickness, Down*main_airspace_height + flat_wall_thickness)
    # return Wire(main_wall1_top_inner_wire_points).extrude(Up * flat_wall_thickness, Down*(main_airspace_height + flat_wall_thickness)).offset(flat_wall_thickness, fill=True)
    return Wire(main_wall1_top_inner_wire_points).extrude(Up * flat_wall_thickness,
                                                          Down * (main_airspace_height + flat_wall_thickness))


@run_if_changed
def main_wall2():
    return Wire(main_wall2_top_inner_wire_points).extrude(Up * filters_absolute_top, Down * (main_airspace_height))


@run_if_changed
def battery():
    return Vertex(battery_right, battery_back, battery_top).extrude(Front * battery_width).extrude(
        Down * battery_length).extrude(Left * battery_thickness)


@run_if_changed
def battery_plug():
    return Face(Wire(Edge(Circle(Axes(Point(battery_left + 13, battery_back - 16, battery_bottom), Up),
                                 battery_plug_diameter / 2)))).extrude(Down * battery_plug_length)


@run_if_changed
def fan_exit():
    return Vertex(fan_body_left_x, fan_back_y, fan_top_z).extrude(Front * fan_thickness).extrude(
        Down * fan_exit_width).extrude(Left * fan_exit_length)


@run_if_changed
def fan_body():
    return Vertex(fan_body_left_x, fan_back_y, fan_top_z).extrude(Front * fan_thickness).extrude(
        Down * fan_width).extrude(Right * (fan_length - fan_exit_length))


@run_if_changed
def fan_socket():
    return Vertex(battery_left, battery_back + flat_wall_thickness, battery_bottom).extrude(
        Back * fan_socket_width).extrude(Up * fan_socket_length).extrude(Right * fan_socket_thickness)


preview(papr_filter2_plate1, papr_prefilter_plate2, main_airspace_top_face.wires(), main_airspace_bottom_face.wires(),
        papr_filter2_plate2, battery, battery_plug, main_wall1.wires(), main_wall2.wires(), fan_exit, fan_body, fan_socket)
# preview(plate, elidupree_4in_connector)
