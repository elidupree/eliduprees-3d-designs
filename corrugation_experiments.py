import math

from pyocct_system import *

initialize_pyocct_system()


def wall(a, b, width, face_thickness, max_separation):
    along = Direction (b - a)
    perpendicular = along @ Rotate (Up, Degrees(90))
    centerline = Edge(Segment(a - along*face_thickness/2, b+along*face_thickness/2))
    faces = centerline.extrude (perpendicular * width, centered=True).cut (centerline.extrude (perpendicular * (width - face_thickness * 2), centered=True))
    strut = Vertex(a).extrude (perpendicular*width, centered=True).extrude (along * face_thickness,centered = True)
    struts = [strut @ Translate ( along*position) for position in subdivisions (0,a.distance(b), max_length = max_separation)]

    return Compound (faces, struts)

@run_if_changed
def t_beam():
    cross_section = Compound(
        wall (Point(0, 10, 0), Point(0, -10, 0), width = 2,face_thickness =0.3,max_separation =5),
        wall (Point(1-0.15, 0, 0), Point(25, 0, 0), width = 2,face_thickness =0.3,max_separation =5),
    )
    return cross_section


@run_if_changed
def star_pillar():
    inner_radius = 9
    outer_radius = 12
    num_zigs = math.floor(inner_radius * math.tau / 3)
    points = [
        p
        for i in range(num_zigs)
        for p in [
            Point(inner_radius, 0, 0) @ Rotate(Up, Radians(i * math.tau / num_zigs)),
            Point(outer_radius, 0, 0) @ Rotate(Up, Radians((i+0.5) * math.tau / num_zigs)),
        ]
    ]
    result = Face(Wire(points, loop=True)).extrude(Up*100)
    save_STL("star_pillar", result)
    return result


@run_if_changed
def zigzag_sheet():
    period = 4
    depth = 3
    num = 18
    thickness = 0.3
    length = 220
    base = Vertex(Origin).extrude (Back*thickness)
    v = Compound (
        base.extrude(Vector(0, -period/2, depth)),
        base.extrude(Vector(0, period/2, depth)),
    ).extrude(Right*length)
    cap = Face(Wire([Origin, Origin + Front*period, Origin + Front*period/2 + Up*depth], loop = True)).extrude(Right*thickness)
    caps = Compound (cap, cap @ Translate (Right*(length-thickness)))
    result = Compound([v @ Translate (Back*period*i) for i in range (num)], [caps @ Translate (Back*period*i) for i in range (num+1)])
    save_STL("zigzag_sheet", result)
    return result


preview(zigzag_sheet)