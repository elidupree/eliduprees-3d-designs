import math

from pyocct_system import *
from pyocct_utils import inch
initialize_pyocct_system()

cardboard_thickness = 4
wall_thickness = 0.5

protector_length = 40
protector_depth = 10


@run_if_changed
def cardboard_corner_protector():
    block = Vertex(Origin)\
        .extrude(Right*protector_length)\
        .extrude(Back*(cardboard_thickness+2*wall_thickness), centered = True)\
        .extrude(Up*protector_depth) \
        .cut(HalfSpace(Point(0, 0, 2), Direction(-1,0,-1)))
    cut = Vertex(Origin) \
        .extrude(Right*wall_thickness, Right*protector_length) \
        .extrude(Back*cardboard_thickness, centered = True) \
        .extrude(Up*0.6, Up*protector_depth)\
        .cut(HalfSpace(Point(0, 0, 2.7), Direction(-1,0,-1)))

    return block.cut(cut).cut(HalfSpace(Point(protector_length, 0, protector_depth/2), Direction(1,0,1)))

t_depth = 15
t_length = inch*3/4

@run_if_changed
def t_protector():
    point_backset = 1.5
    angle = Degrees(3)
    r = Rotate(Up, angle)
    p_ns = [
        (Point(-t_length, -cardboard_thickness, 0), Vector(0, -1, 0)),
        (Point(t_length, -cardboard_thickness, 0), Vector(1, -1, 0)),
        (Point(t_length, cardboard_thickness, 0), Vector(1, 1, 0)),
        (Point(0, cardboard_thickness, 0), Vector(1, 1, 0)),
        (Point(0, t_length, 0) @ r, Vector(1, 0, 0) @ r),
    ]
    wires = [Face(BSplineCurve([p - n*point_backset, p + Up*point_backset, p + Up*(t_depth - 1.5), p - n*0.5 + Up*t_depth], BSplineDimension(degree=3)).extrude(n*wall_thickness)).outer_wire() for p, n in p_ns]

    floor_points = [p + n*(wall_thickness - point_backset) for p, n in p_ns]

    return Compound(
        Loft(wires, solid=True, ruled=True),
        Face(Wire(floor_points + [BSplineCurve([
            floor_points[-1],
            Point(-cardboard_thickness, t_length, 0),
            Point(-cardboard_thickness*2.5, t_length, 0),
            Point(-t_length, cardboard_thickness*1.5, 0),
            Point(-t_length, 0, 0),
            floor_points[0]]
        )])).extrude(Up*0.6)
    )

# save_STL("cardboard_corner_protector", cardboard_corner_protector)
# export("cardboard_corner_protector.stl", "cardboard_corner_protector_1.stl")
# save_STL("t_protector", t_protector)
# export("t_protector.stl", "t_protector_1.stl")
preview(cardboard_corner_protector, t_protector @ Translate(Up*20))