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

CPAP_outer_radius = 21.5 / 2

flat_wall_thickness = inch * 0.030

screw_radius = 2
contact_leeway = 0.4
nut_short_radius = 4.4
nut_long_radius = nut_short_radius / math.cos(math.tau / 12)
nut_thickness = 3
nut_holder_thickness = 2

frame_outer_zigzag_width = 0.6

# screw_offset = strong_filter_length / 4
screw_filter_contact_leeway = 1

plate_thickness = 10

nut_bracket_cuts = None

nut_bracket_protrusion_length = None
@run_if_changed
def nut_bracket():
    global nut_bracket_cuts, nut_bracket_protrusion_length
    holder_radius = nut_long_radius + nut_holder_thickness
    screw_center = Origin + Left * max(screw_radius + screw_filter_contact_leeway,
                                       holder_radius - strong_filter_rim_inset)

    nut_bracket_protrusion_length = -screw_center[0] + holder_radius

    cylinder = Face(Circle(Axes(screw_center, Up), holder_radius)).extrude(Up * plate_thickness)
    a = screw_center + Direction(-1, -1, 0) * holder_radius
    b = a + Vector(1, - 1, 0) * -a[0]
    frustum = Face(Wire([
        b, a, a @ Mirror(Back), b @ Mirror(Back)
    ], loop=True)).extrude(Up * plate_thickness)

    screw_hole = Face(Circle(Axes(screw_center, Up), screw_radius + contact_leeway)).extrude(Up * plate_thickness)
    nut_hole = Face(Wire([
        Point((nut_short_radius + contact_leeway) / math.cos(math.tau / 12), 0, nut_holder_thickness)
        @ Rotate(Up, degrees=i * 60)
        for i in range(6)
    ], loop=True)).extrude(Up * plate_thickness) @ Translate(screw_center - Origin)

    cutaway = HalfSpace(screw_center + Left * nut_long_radius + Up * (nut_holder_thickness + nut_thickness),
                        Direction(-1, 0, 1))
    nut_bracket_cuts = Compound(screw_hole, nut_hole)

    # sacrificial_bridge = Face (Circle (Axes(screw_center + Up*nut_holder_thickness, Up), screw_radius+ contact_leeway)).extrude (Down*0.28)

    real = Compound(cylinder, frustum).cut([
        screw_hole, nut_hole, cutaway
    ])
    return Compound(
        real,
        # sacrificial_bridge,
    )


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
frame_full_length = strong_filter_length + 2 * nut_bracket_protrusion_length


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


@run_if_changed
def plate():
    b1 = nut_bracket @ Rotate(Up, degrees=90) @ Translate(Front * (strong_filter_length / 2))
    c1 = nut_bracket_cuts @ Rotate(Up, degrees=90) @ Translate(Front * (strong_filter_length / 2))
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

    # print the plate upside-down, because we want the filter-facing face to be the one that's less warped
    # result = result @ Mirror(Up)
    save_STL("filter_plate", result)
    return result


@run_if_changed
def bracket_test():
    result = plate.intersection(
        Face(Circle(Axes(Origin + Back * (strong_filter_length / 2 + screw_radius), Up), 20)).extrude(Up * lots,
                                                                                                      centered=True))
    save_STL("bracket_test", result)
    preview(result)


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


@run_if_changed
def plate_to_elidupree_4in():
    result = Compound(plate, elidupree_4in_connector)
    save_STL("plate_to_elidupree_4in", result)
    return result


# For the PAPR:
#
# the biggest landmark is the wall surrounding the main air chamber; we shall make 0, 0, 0 the corner of the airspace before the prefilter.

putative_inplace_filter2_thickness_with_padding = 18

prefilter_airspace_front_y = 0
prefilter_airspace_right_x = 0
main_airspace_top_z = 0
prefilter_airspace_left_x = prefilter_airspace_right_x - frame_full_width
filter2_plate1_right_x = prefilter_airspace_left_x - flat_wall_thickness
filter2_plate2_left_x = filter2_plate1_right_x - putative_inplace_filter2_thickness_with_padding - plate_thickness*2

prefilter_airspace_back_y = prefilter_airspace_front_y + frame_full_width - flat_wall_thickness * 2

prefilter_front_y = prefilter_airspace_front_y + 15
prefilter_back_y = prefilter_front_y + 16
prefilter_plate2_back_y = prefilter_back_y + plate_thickness

main_airspace_height = strong_filter_length - strong_filter_rim_inset * 2 + flat_wall_thickness * 2
main_airspace_bottom_z = main_airspace_top_z - main_airspace_height
filters_vertical_center = Between(main_airspace_top_z, main_airspace_bottom_z)
filters_absolute_top = main_airspace_top_z + (frame_full_length - main_airspace_height)/2

fan_center_y = Between(prefilter_plate2_back_y, prefilter_airspace_back_y)
fan_front_y = fan_center_y - fan_thickness / 2
fan_back_y = fan_center_y + fan_thickness / 2
fan_body_left_x = filter2_plate1_right_x + (fan_front_y - prefilter_plate2_back_y)
fan_exit_left_x = fan_body_left_x + fan_exit_length

battery_top = filters_absolute_top
battery_left = prefilter_airspace_right_x + flat_wall_thickness
battery_front = prefilter_airspace_front_y + flat_wall_thickness
battery_back =battery_front + battery_width
battery_right = battery_left + battery_thickness
battery_bottom =battery_top -battery_length


@run_if_changed
def papr_filter2_plate1():
    return plate @ Transform(Back, Up, Right) @ Translate(
        Vector(filter2_plate1_right_x - plate_thickness, prefilter_airspace_front_y + frame_full_width / 2,
               filters_vertical_center))

@run_if_changed
def papr_filter2_plate2():
    return plate @ Transform(Back, Up, Left) @ Translate(
        Vector(filter2_plate2_left_x + plate_thickness, prefilter_airspace_front_y + frame_full_width / 2,
               filters_vertical_center))


@run_if_changed
def papr_prefilter_plate2():
    return plate @ Transform(Left, Up, Back) @ Translate(
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
    #Point(prefilter_airspace_right_x, prefilter_airspace_back_y),
    #Point(prefilter_airspace_right_x, prefilter_airspace_front_y),
]
main_wall2_top_inner_wire_points = [
    Point(prefilter_airspace_left_x- flat_wall_thickness, prefilter_airspace_back_y),
    Point(prefilter_airspace_right_x, prefilter_airspace_back_y),
    Point(prefilter_airspace_right_x, prefilter_airspace_front_y),
]


@run_if_changed
def main_airspace_top_face():
    return Face(Wire(main_airspace_top_wire_points, loop=True)).extrude(Up * flat_wall_thickness)

@run_if_changed
def main_airspace_bottom_face():
    return Face(Wire(main_airspace_top_wire_points, loop=True)).extrude(Down * flat_wall_thickness) @ Translate(Down*main_airspace_height)


# @run_if_changed
# def main_wall1():
    #preview(Wire(main_wall1_top_inner_wire_points))
    #return Wire(main_wall1_top_inner_wire_points).offset2D(flat_wall_thickness, fill=True).extrude(Up * flat_wall_thickness, Down*main_airspace_height + flat_wall_thickness)
    #return Wire(main_wall1_top_inner_wire_points).extrude(Up * flat_wall_thickness, Down*(main_airspace_height + flat_wall_thickness)).offset(flat_wall_thickness, fill=True)

@run_if_changed
def battery ():
    return Vertex(battery_right, battery_back, battery_top).extrude(Front*battery_width).extrude(Down*battery_length).extrude(Left*battery_thickness)

preview(papr_filter2_plate1, papr_prefilter_plate2, main_airspace_top_face, main_airspace_bottom_face, papr_filter2_plate2, battery,Wire(main_wall1_top_inner_wire_points), Wire(main_wall2_top_inner_wire_points))
# preview(plate, elidupree_4in_connector)
