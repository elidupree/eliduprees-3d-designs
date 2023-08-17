import math

from pyocct_system import *
from gears import InvoluteGear

initialize_pyocct_system()

inch = 25.4

shank_short_radius = inch / 8
shank_long_radius = shank_short_radius / math.cos(math.tau / 12)
lego_shaft_diameter = 4.75

def hex_shank(length, indent = True):

    shank = Face(Wire([
        Point(shank_long_radius, 0, 0) @ Rotate(Up, degrees=i * 60)
        for i in range(6)
    ], loop=True)).extrude(Up * length)

    if indent:
        indentation_result_radius = inch * 3 / 32
        indentation_cut_halfwidth = inch * 3 / 32
        knob_length = inch * 5 / 16
        # algebra:
        # indentation_cut_center_x - indentation_result_radius = sqrt((indentation_cut_width/2)**2 + (indentation_cut_center_x - shank_short_radius)**2)
        # solve for indentation_cut_center_x:
        indentation_cut_center_x = (
                                               indentation_result_radius ** 2 - shank_short_radius ** 2 - indentation_cut_halfwidth ** 2) / (
                                       2*(indentation_result_radius - shank_short_radius))
        indentation_cut_radius = indentation_cut_center_x - indentation_result_radius
        indentation = Face(
            Circle(Axes(Point(indentation_cut_center_x, 0, length - knob_length - indentation_cut_halfwidth), Back),
                   indentation_cut_radius)).revolve(Up)

        shank = shank.cut(indentation)
    shank = Chamfer(shank, [(e, 1.5) for e in shank.edges() if e.bounds().min()[2] > length - 0.01])

    #preview (shank)
    return shank


def stirrer(head_radius, fin_height = shank_long_radius):
    length = 4 * inch


    shield_size = 10

    shield = Vertex(shield_size,0,length-24).extrude(Right*0.8).extrude(Vector(-50, 0, -50)).intersection(HalfSpace(Origin, Right)).revolve(Up)

    fin_thickness = 0.8
    fin = Vertex(0, -shank_long_radius/2, 0).extrude(Vector(0, shank_long_radius-fin_thickness, fin_height)).extrude(Back*fin_thickness).extrude(Right*head_radius)

    return Compound(hex_shank(length), shield, [fin @ Rotate(Up, degrees=i * 60 + 30)
                                                for i in range(6)])


@run_if_changed
def stirrer_1():
    result = stirrer(13)
    save_STL("stirrer_1", result)
    return result

@run_if_changed
def stirrer_2():
    result = stirrer(25, 10)
    save_STL("stirrer_2", result)
    return result


def lego_shaft_hole(length, end_closed):
    contact_leeway = 0.1
    chamfer = 1.5
    def hoop(expand, z):
        return Vertex(Origin + Up*z).extrude(Left*(1.9 + 2*expand), centered=True).extrude(Back*(lego_shaft_diameter + 2*expand), centered=True).outer_wire()
    hoops = [hoop(chamfer + contact_leeway, 0), hoop(contact_leeway, chamfer)]
    if end_closed:
        hoops += [hoop(contact_leeway, length - 4), hoop(contact_leeway - 0.15, length)]
    else:
        hoops += [hoop(contact_leeway, length - chamfer), hoop(chamfer + contact_leeway, length)]

    cut = Loft(hoops, ruled=True, solid=True)
    return Compound(cut, cut @ Rotate(Up, degrees=90))


@run_if_changed
def drill_to_lego_shaft():
    result = hex_shank(inch)
    sheath = Face(Circle(Axes(Origin, Up), 6)).extrude(Up*9)
    sheath = Loft([
        Wire(Circle(Axes(Origin, Up), 8)),
        Wire(Circle(Axes(Origin + Up*1, Up), 8)),
        Wire(Circle(Axes(Origin + Up*3, Up), 6)),
        Wire(Circle(Axes(Origin + Up*9, Up), 6)),
    ], ruled=True, solid=True)
    cut = lego_shaft_hole(length = 9, end_closed = True)
    result = Compound(result, sheath).cut(cut)
    save_STL("drill_to_lego_shaft", result)
    return result


def sorted_points_from_edges(edges):
    result = [v.point() for v in edges[0].vertices()]
    rest = edges[1:]
    while rest:
        new_rest = []
        for edge in rest:
            points = [v.point() for v in edge.vertices()]
            epsilon=0.00001
            if points[0].distance(result[-1]) < epsilon:
                result.append (points [1])
            elif points[1].distance(result[-1]) < epsilon:
                result.append (points [0])
            else:
                new_rest.append(edge)
        if len(new_rest) == len(rest):
            break
        rest = new_rest
    return result

@run_if_changed
def cardboard_roller_stuff():
    crusher_diameter = 25.9
    crush_to_width = 1.0
    shaft_distance = crusher_diameter + crush_to_width

    #gear = read_brep("involute_gear_12teeth_1pitchrad_fixed.brep")
    # gear = read_brep("involute_gear_12teeth_1pitchrad.brep")
    # gear = Wire(sorted_points_from_edges(gear.edges()))
    # gear.write_brep("involute_gear_12teeth_1pitchrad_fixed.brep")
    gear = InvoluteGear(12, pitch_radius=shaft_distance/2).shape

    #gear = gear @ Scale((crusher_diameter + crush_to_width)/2)
    #preview(gear, gear.offset2D(-0.2))
    #gear = gear.offset2D(-0.2)
    #chamfer = 1.2
    thickness = 6
    # hoops = [
    #     gear.offset2D(-0.2 - chamfer),
    #     gear.offset2D(-0.2) @ Translate(Up*chamfer),
    #     gear.offset2D(-0.2) @ Translate(Up*(thickness-chamfer)),
    #     gear.offset2D(-0.2 - chamfer) @ Translate(Up*thickness),
    # ]
    # preview(hoops)
    # gear = Loft(hoops[:2], ruled=True, solid=True)
    gear = gear.extrude(Up*thickness)
    #gear = Chamfer(gear, [(e, chamfer) for e in gear.edges()])
    gear = gear.cut(lego_shaft_hole(length = thickness, end_closed = False))
    save_STL("cardboard_roller_drive_gear", gear)

    r1 = lego_shaft_diameter/2 + 0.1
    r2 = r1 + 3.0
    bar = Vertex(Origin).extrude(Right*shaft_distance).extrude (Back * r2*2, centered = True).extrude (Up * 3)
    centers = [Origin, Origin + Right*shaft_distance]
    bar = Compound(bar, [Face(Circle(Axes(p, Up), r2)).extrude (Up * 3) for p in centers])
    bar = bar.cut([Face(Circle(Axes(p, Up), r1)).extrude (Up * 3) for p in centers])
    #bar = bar.extrude (Up * 3)
    save_STL("cardboard_roller_bar", bar)

    preview(bar)


@run_if_changed
def bending_brake_knob():
    knob_diameter = 36
    rod_outer_diameter = 12
    rod_inner_diameter = 10.5
    thread_length = 13
    collet_hole_diameter = 18
    collet_hole_length = 15
    a = Point(rod_outer_diameter/2 + 2, 0, 0)
    g = Point(0, 0, knob_diameter)
    f = g + Right*collet_hole_diameter/2
    h = f + Down*collet_hole_length
    i = Point(0, 0, knob_diameter-collet_hole_length)
    section = Face(Wire([
        Edge(Origin, a),
        BSplineCurve([
            a,
            a + Direction(1,0,1) * 10,
            Point(knob_diameter/2, 0, knob_diameter/2 - 2),
            Point(knob_diameter/2, 0, knob_diameter/2 + 8),
            f + Right*5,
            f,
            f + Down*2,
            h + Up*2,
            h,
            h + Left*2,
        ]),
        i,
    ], loop = True))
    result = section.revolve(Up)
    result = Compound(result, hex_shank(knob_diameter, indent=False))
    result = result.cut (Face(Circle(Axes(Origin, Up), rod_inner_diameter/2)).extrude (Up * thread_length))
    save_STL("bending_brake_knob", result)
    preview(result)

preview(stirrer_2)