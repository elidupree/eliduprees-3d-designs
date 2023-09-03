import math

from pyocct_system import *

initialize_pyocct_system()

inch = 25.4

@run_if_changed
def deforming_slot():
    zigs = 10
    zig_length = 3
    gap_thickness = 0.3
    deform_length = 14
    final_angle = Degrees (90-45/2)
    def hoop(frac):
        angle = final_angle * frac
        z = deform_length * (1 - frac)
        zig = Vector(zig_length, 0, 0) @ Rotate(Up, angle)
        points = [Point(zig[0] * (i - 0.5*(zigs-1)), zig[1]/2 * (1 if i % 2 == 0 else -1), z) for i in range(zigs)]
        dy = gap_thickness * zig_length / zig[0] / 2
        # outer_points = [Point(*i) for i in [-1, 1]]
        return Wire(
            [p + Back*dy for p in points]
            + [p + Front*dy for p in points[::-1]]
            , loop = True
        )
    hoops = [hoop(frac) for frac in subdivisions(0, 1, amount=7)]
    slot = Loft(hoops, solid=True)
    #preview(slot)
    solid = Vertex(Origin).extrude (Left * (zigs*zig_length + 6), centered=True).extrude (Back * (zig_length + 12), centered=True).extrude(Up*deform_length)
    result = solid.cut(slot)
    save_STL("deforming_slot", result)
    preview(result)

@run_if_changed
def single_fold_deforming_slot():
    zig_length = 5
    sheet_width = 15
    throat_depth = sheet_width - zig_length*2
    deform_length = 50
    gap_thickness = 0.3
    final_angle = Degrees (135)
    wall_thickness = 6

    def hoop(frac):
        angle = final_angle * frac
        ha = angle/2
        z = deform_length * (1 - frac)
        middle = Origin + Up*z
        zig = Vector(zig_length/2, 0, 0) @ Rotate(Up, angle)
        c = middle + zig
        b = middle - zig
        a = b + Left*throat_depth
        d = c + Right*zig_length
        e = d + Back*zig_length
        def points(side):
            return [
                a + Back*1*side,
                a + Back*1*side + Right*gap_thickness,
                a + Back*side*gap_thickness/2 + Right*gap_thickness,
                b + side*(Back*gap_thickness/2 + Left*ha.sin()/ha.cos()*gap_thickness/2),
                c + side*(Back*gap_thickness/2 + Left*ha.sin()/ha.cos()*gap_thickness/2),
                d + Back*side*gap_thickness/2 + Left*side*gap_thickness/2,
                e + Back*side*gap_thickness/2 + Left*side*gap_thickness/2,
            ]
        outer_points = [
            a + Back*wall_thickness + Left*wall_thickness,
            #a + Back*wall_thickness*side + Right*wall_thickness,
            e + Front*gap_thickness/2 + Left*wall_thickness,
            e + Front*gap_thickness/2 + Right*wall_thickness,
            d + Front*wall_thickness + Right*wall_thickness,
            a + Front*wall_thickness + Right*wall_thickness,
            a + Front*wall_thickness + Left*wall_thickness,
        ]

        # outer_points = [Point(*i) for i in [-1, 1]]
        return Wire(
            points(1) + points(-1)[::-1]
            , loop = True
        ), Wire(outer_points, loop = True)
    hoops = [hoop(frac) for frac in subdivisions(0.01, 1, amount=7)]
    slot = Loft([h[0] for h in hoops], solid=True)
    preview(slot)
    solid = Loft([h[1] for h in hoops], solid=True)
    result = solid.cut(slot)
    save_STL("single_fold_deforming_slot", result)
    preview(result)

@run_if_changed
def bending_brake_diagonal_clamp():
    presser_plate_thickness = 11
    clamp_width = 10
    clamp_thickness = 10
    bolt_radius = 3
    spring_space = 50


    a = Vector(0, 52, 32)
    presser_plate_length = a.magnitude() + 2
    slot_length = presser_plate_length + 5
    clamp_length = presser_plate_length + spring_space
    da = Direction (a)
    db = (Direction (a) @ Rotate(Right, Degrees(90)))
    b = db * presser_plate_thickness
    presser_plate_ish = Vertex (Origin).extrude (da*presser_plate_length).extrude (b).extrude (Left*2*inch)

    clamp_cross_section = Face(Wire([
        Origin,
        Origin + Back*da[1]*(slot_length+clamp_thickness),
        Origin + da*(clamp_length),
        Origin + da*(clamp_length) + db*(presser_plate_thickness),
        Origin + da*(slot_length+clamp_thickness) + db*(presser_plate_thickness+clamp_thickness),
        Origin + db*(presser_plate_thickness+clamp_thickness),
    ], loop = True)).cut(Vertex (Origin).extrude (da*slot_length).extrude (b)).cut(HalfSpace(Origin, Front))
    clamp = clamp_cross_section.extrude(Left*clamp_width)
    clamp = clamp.cut(Face (Circle (Axes (Origin + db*presser_plate_thickness/2 + Left*clamp_width/2, da), bolt_radius)).extrude(da * 1000))

    spring_peg = Face(Wire([
        Origin,
        Point(-10, 0, 0),
        Point(-10, 5/2, 0),
        Point(-6, 4/2, 0),
        Point(0, 6, 0),
    ], loop = True)).revolve(Left) @ Translate(da*(clamp_length - 6) + db*presser_plate_thickness/2 + Left*clamp_width)
    clamp = Compound(clamp, spring_peg)

    spring_grabber = Face(Wire([
        Point(-5, 0, 0),
        Point(-5, 3, 0),
        Point(-4, 3, 0),
        Point(0, 4/2, 0),
        Point(4, 3, 0),
        Point(5, 3, 0),
        Point(5, 0, 0),
    ], loop = True)).revolve(Left)
    s = Vertex(Origin).extrude(Back*3, Front * 25).extrude(Up*(presser_plate_thickness + 6), centered=True)
    s = s.cut(Vertex(Origin).extrude(Front*(4/2 + 3 + 2), Front * 1000).extrude(Up*(presser_plate_thickness), centered=True))
    s = s.extrude(Left*10, centered=True)
    a = Direction(0,1,1)
    b = Direction(0,1,-1)
    s = s.cut(HalfSpace(Origin + a*3, a)).cut(HalfSpace(Origin + b*3, b)).cut(HalfSpace(Origin + Back*3/math.sqrt(2), Back))
    s = s.cut(Vertex(Origin).extrude(Back*100, Front * (4/2 + 2.3)).extrude(Up*100, centered=True).extrude(Left*8, centered=True))
    spring_grabber = Compound(spring_grabber, s)

    save_STL("bending_brake_diagonal_clamp", clamp @ Rotate(Back, Degrees(90)))

    preview (clamp, presser_plate_ish, spring_grabber @ Transform(Right,da,db) @ Translate(da*(presser_plate_length + 4/2 + 3 + 2) + db*presser_plate_thickness/2 + Left*(clamp_width + 6)))


