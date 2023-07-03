import math

from pyocct_system import *

initialize_pyocct_system()

from air_adapters import elidupree_4in_output_outer_radius
from pyocct_utils import wallify

lots = 500

strong_filter_length = 152
strong_filter_width = 101
strong_filter_rim_inset = 6

screw_radius = 2
contact_leeway = 0.4
nut_short_radius = 4.4
nut_long_radius = nut_short_radius / math.cos(math.tau / 12)
nut_thickness = 3
nut_holder_thickness = 2

# screw_offset = strong_filter_length / 4
screw_filter_contact_leeway = 1

plate_thickness = 10

nut_bracket_cuts = None


@run_if_changed
def nut_bracket():
    global nut_bracket_cuts
    holder_radius = nut_long_radius + nut_holder_thickness
    screw_center = Origin + Left * max(screw_radius + screw_filter_contact_leeway,
                                       holder_radius - strong_filter_rim_inset)

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
    result = Face(zigzag_loop(rectangle_points(Right * strong_filter_width / 2, Back * strong_filter_length / 2), 0.6)) \
        .extrude(Up * plate_thickness)

    cut = Face(zigzag_loop(rectangle_points(
        Right * (strong_filter_width / 2 - strong_filter_rim_inset),
        Back * (strong_filter_length / 2 - strong_filter_rim_inset)
    ), -0.6)) \
        .extrude(Up * plate_thickness)
    # old_cut = Vertex(Origin) \
    #     .extrude(Left * (strong_filter_width - strong_filter_rim_inset * 2), centered=True) \
    #     .extrude(Back * (strong_filter_length - strong_filter_rim_inset * 2), centered=True) \
    #     .extrude(Up * plate_thickness)
    # preview(cut, old_cut)

    result = result.cut(cut)
    result = Fillet(result, [(e, 2) for e in result.edges() if all_equal((v[0], v[1]) for v in e.vertices())])
    return result


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
    row0 = points_along_wire(zig, max_length=2) #[p for edge in z for p in edge[:-1]]
    rows = [
        row0
    ]
    for z in [25, 50, 60, 75]:
        rows.append([Origin + Up*z + Direction(p - Origin)*elidupree_4in_output_outer_radius for p in row0])

    # deliberately expanding the wall inwards, because we need the outer radius correct
    return wallify(rows, thickness=wall_thickness, loop=True) @ Translate(Up*plate_thickness)


@run_if_changed
def plate_to_elidupree_4in():
    result = Compound(plate, elidupree_4in_connector)
    save_STL("plate_to_elidupree_4in", result)
    return result

preview(plate, elidupree_4in_connector)
