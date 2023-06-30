import math

from pyocct_system import *

initialize_pyocct_system()

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

screw_offset = strong_filter_length / 4
screw_filter_contact_leeway = 1

plate_thickness = 10


nut_bracket_cuts = None
@run_if_changed
def nut_bracket():
    global nut_bracket_cuts
    holder_radius = nut_long_radius + nut_holder_thickness
    screw_center = Origin + Left*max(screw_radius+ screw_filter_contact_leeway, holder_radius - strong_filter_rim_inset)

    cylinder = Face (Circle (Axes(screw_center, Up), holder_radius)).extrude (Up*plate_thickness)
    a = screw_center + Direction (-1, -1, 0) * holder_radius
    b = a + Vector(1, - 1, 0)* -a[0]
    frustum = Face (Wire([
        b, a, a@Mirror(Back), b@Mirror(Back)
    ], loop = True)).extrude (Up*plate_thickness)

    screw_hole = Face (Circle (Axes(screw_center, Up), screw_radius+ contact_leeway)).extrude (Up*plate_thickness)
    nut_hole = Face (Wire([
        Point((nut_short_radius + contact_leeway) / math.cos(math.tau / 12), 0, nut_holder_thickness)
        @ Rotate(Up, degrees = i*60)
        for i in range(6)
    ], loop = True)).extrude (Up*plate_thickness) @ Translate(screw_center - Origin)

    cutaway = HalfSpace(screw_center + Left*nut_long_radius + Up*(nut_holder_thickness + nut_thickness), Direction (-1,0, 1))
    nut_bracket_cuts = Compound(screw_hole, nut_hole)

    return Compound (cylinder, frustum).cut([
        screw_hole, nut_hole, cutaway
    ])


@run_if_changed
def frame():
    result = Vertex (Origin)\
        .extrude (Left*strong_filter_width, centered = True)\
        .extrude (Back*strong_filter_length, centered = True)\
        .extrude (Up*plate_thickness)

    cut = Vertex (Origin) \
        .extrude (Left*(strong_filter_width-strong_filter_rim_inset*2), centered = True) \
        .extrude (Back*(strong_filter_length-strong_filter_rim_inset*2), centered = True) \
        .extrude (Up*plate_thickness)

    result = result.cut (cut)
    result = Fillet(result, [(e, 2) for e in result.edges() if all_equal((v[0], v[1]) for v in e.vertices())])
    return result

@run_if_changed
def reinforcement():
    edge = Edge(BSplineCurve([
        Point(0, 0, 0),
        Point(0, 3, plate_thickness/2),
        Point(0, 0, plate_thickness),
    ], BSplineDimension(degree=2)))

    cross_section = Face (Wire(edge, edge @ Mirror(Back)))

    return cross_section.extrude(Left*(strong_filter_width-strong_filter_rim_inset*2), centered = True)

@run_if_changed
def plate():
    b1 = nut_bracket @ Translate(Left*(strong_filter_width/2) + Back*screw_offset)
    c1 = nut_bracket_cuts @ Translate(Left*(strong_filter_width/2) + Back*screw_offset)
    r1 = reinforcement @ Translate(Back*screw_offset)
    result = Compound ([
        b1,
        b1 @ Mirror(Left),
        b1 @ Mirror(Back),
        b1 @ Mirror(Left) @ Mirror(Back),
        r1,
        r1 @ Mirror(Back),
        frame.cut([
            c1,
            c1 @ Mirror(Left),
            c1 @ Mirror(Back),
            c1 @ Mirror(Left) @ Mirror(Back),
        ])
    ])
    
    save_STL("filter_plate", result)
    return result

@run_if_changed
def bracket_test():
    result = plate.intersection(Face(Circle(Axes(Origin + Left*(strong_filter_width/2 + screw_radius) + Back*screw_offset, Up), 20)).extrude(Up*lots))
    save_STL("bracket_test", result)
    preview(result)

preview (plate)