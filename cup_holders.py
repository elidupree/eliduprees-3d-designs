import math

from pyocct_system import *

initialize_pyocct_system()

cup_bottom_diameter = 64
cup_top_diameter = 71
cup_bottom_radius = cup_bottom_diameter / 2
cup_top_radius = cup_top_diameter / 2
cup_approx_height = 190
cup_slope = (cup_top_radius-cup_bottom_radius)/cup_approx_height

grip_leeway = 0.4

inch = 25.4
post_diameter = inch/2
post_radius = post_diameter/2

funnel_radius = 48

def cup_holder(bottom_radius, slope):
    inside = []
    outside = []
    for z,expand_frac in [(0,0),(15,0),(30,0),(33,0.1),(40,0.66),(45,1.0)]:
        base_radius = bottom_radius + grip_leeway + z*slope
        expand = (funnel_radius - 0.8 - base_radius) * expand_frac
        inner_radius = base_radius + expand
        outer_radius = inner_radius + 0.8 + 3.2*(1.0 - expand_frac)

        inside.append (Point(inner_radius,0,z))
        outside.append (Point(outer_radius,0,z))

    cross_section = Face(Wire([BSplineCurve(inside), outside [-1], BSplineCurve(outside[::-1]), inside[0]]))
    result = Revolve(cross_section, Up)
    interior_cross_section = Face(Wire([BSplineCurve(inside), Point(0,0,45), Origin, inside[0]]))
    interior = Revolve(interior_cross_section, Up)

    # bottom = Circle(Axes(Origin, Up), bottom_radius)
    # bottom2 = Circle(Axes(Origin, Up), bottom_radius + grip_leeway)
    # preview(bottom, bottom2, cross_section)
    # save_STL("cup_holder_solid", result)
    return result, interior

num_holders = 4
centers = [Point(67.5, 0, 0) @ Rotate(Up, radians = math.tau*i/num_holders) for i in range(num_holders)]


holders, interiors = None, None
@run_if_changed
def holders_and_interiors():
    global holders, interiors
    ch, ci = cup_holder(cup_bottom_radius, cup_slope)
    jh, ji = cup_holder(73/2, 0)
    holders = [(ch if i != 0 else jh) @ Translate(center-Origin) for i, center in enumerate (centers)]
    interiors = [(ci if i != 0 else ji) @ Translate(center-Origin) for i, center in enumerate (centers)]


post_holder, post_holder_interior = None, None
@run_if_changed
def post_holder_and_interior():
    global post_holder, post_holder_interior

    inside = []
    outside = []
    for z,w in [(0,3),(15,3),(30,3),(45,3)]:
        inner_radius = post_radius + 0.3
        outer_radius = inner_radius + w
        inside.append (Point(inner_radius,0,z))
        outside.append (Point(outer_radius,0,z))

    cross_section = Face(Wire([BSplineCurve(inside), outside [-1], BSplineCurve(outside[::-1]), inside[0]]))
    post_holder = Revolve(cross_section, Up)
    interior_cross_section = Face(Wire([BSplineCurve(inside), Point(0,0,45), Origin, inside[0]]))
    post_holder_interior = Revolve(interior_cross_section, Up)




def strut(a, b, cuts):
    along = Direction(b - a)
    perp = along @ Rotate(Up, degrees = 90)
    return Vertex(a).extrude(b - a).extrude(perp*3, centered=True).extrude(Up*45).cut(cuts)

def bottom(center, interior):
    along = Direction(center - Origin)
    perp = along @ Rotate(Up, degrees = 90)
    return Vertex(center).extrude(along*500, centered=True).extrude(perp*3, centered=True).extrude(Up*3).intersection(interior)

@run_if_changed
def struts():
    return [strut(Origin, center, [interior, post_holder_interior]) for center, interior in zip(centers, interiors)] + [strut(c1, c2, [i1, i2]) for (c1, i1), (c2, i2) in pairs(list(zip(centers, interiors)), loop=True)]

    #return Compound(holders)


@run_if_changed
def bottoms():
    return [bottom(*p) for p in zip(centers, interiors)]


@run_if_changed
def post():
    return Face(Circle(Axes(Origin, Up), post_radius)).extrude(Up* (cup_approx_height + 30))

@run_if_changed
def post_bottom():
    return Face(Circle(Axes(Origin, Up), post_radius + 3)).extrude(Down*(10))

@run_if_changed
def post_base():
    return Face(Circle(Axes(Origin, Up), 130)).extrude(Down*(10)) @ Translate(Down*10)

@run_if_changed
def cup_holders():
    result = Compound(holders, post_holder, struts)
    save_STL("cup_holders", result)
    return result


preview (holders, post_holder, struts, bottoms, post, post_bottom, post_base)