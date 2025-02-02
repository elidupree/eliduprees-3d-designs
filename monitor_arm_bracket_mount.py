
import math

from pyocct_system import *
from pyocct_utils import pointy_hexagon

initialize_pyocct_system()

measured_nub_height = 3.5
measured_plate_height = 59.3
measured_security_screw_hole_height = 61.2
security_screw_radius = 3.0
measured_plate_width = 44.5
measured_nub_width = 50.5
measured_plate_thickness = 2.0
measured_security_screw_hole_backset = 8.0
measured_grip_width = 36

strong_wall_thickness = 2.0

plate_side_leeway = 1.0
plate_thickness_leeway = 0.3
leeway_plate_thickness = measured_plate_thickness + plate_thickness_leeway
block_width = measured_plate_width + strong_wall_thickness*2 + plate_side_leeway
foot_y = block_width/2 - 8

foot_xs = [8,42]
foot_ys = [foot_y,-foot_y]

foot_screw_radius = 2
foot_screw_leeway = 0.3
security_screw_leeway = 0.3

@run_if_changed
def bracket_mount():

    big_block = Face(Wire([
        # Point(0, 0, 0),
        Point(50, 0, 0),
        Point(50, 0, 10),
        Point(10, 0, measured_security_screw_hole_height+strong_wall_thickness),
        Point(-measured_security_screw_hole_backset - security_screw_radius - security_screw_leeway - strong_wall_thickness, 0, measured_security_screw_hole_height+strong_wall_thickness),
        Point(-measured_security_screw_hole_backset - security_screw_radius - security_screw_leeway - strong_wall_thickness, 0, measured_security_screw_hole_height),
        Point(-leeway_plate_thickness-strong_wall_thickness, 0, measured_security_screw_hole_height),
        Point(-leeway_plate_thickness-strong_wall_thickness, 0, 0),
    ], loop=True)).extrude(Back*block_width, centered=True)

    foot_cut = Compound(
        Face(Circle(Axes(Origin,Up), foot_screw_radius + foot_screw_leeway)).extrude(Up*100),
        # Face(Circle(Axes(Origin,Up), 6)).extrude(Up*6, Up*100),
        pointy_hexagon(short_radius = 3.9).extrude(Up*1.8, Up*100),
    )

    security_screw_hole = Face(Circle(Axes(Point(-measured_security_screw_hole_backset, 0, 0),Up), security_screw_radius + security_screw_leeway)).extrude(Up*100)

    result = big_block.cut([
        Vertex(Origin).extrude(Left*leeway_plate_thickness).extrude(Back*(measured_plate_width+plate_thickness_leeway), centered=True).extrude(Up*measured_plate_height),
        Vertex(Origin).extrude(Left*10).extrude(Back*measured_grip_width, centered=True).extrude(Up*measured_plate_height),
        Vertex(Origin).extrude(Left*10).extrude(Back*measured_nub_width, centered=True).extrude(Up*measured_nub_height),
        security_screw_hole,
    ])
    # preview(result)
    # result = Fillet(result, [(e, 0.9) for e in result.edges() if e.bounds().min()[2] +0.1 < e.bounds().max()[2]])

    result = result.cut([foot_cut @ Translate(x,y,0) for x in foot_xs for y in foot_ys])
    save_STL("bracket", result)
    export("bracket.stl", "bracket_2.stl")
    return result


@run_if_changed
def foot():
    result = Compound(
        Face(Circle(Axes(Origin,Up), 6), holes = [Wire(Circle(Axes(Origin,Down), foot_screw_radius + foot_screw_leeway))]).extrude(Down*1.8),
        Face(Circle(Axes(Origin,Up), 7), holes = [Wire(Circle(Axes(Origin,Down), 5))]).extrude(Down*5),
    )
    save_STL("foot", result)
    export("foot.stl", "foot_1.stl")
    return result

preview(bracket_mount, [foot @ Translate(x,y,-6) for x in foot_xs for y in foot_ys])
