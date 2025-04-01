
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
plate_thickness_leeway = 1.0
leewayed_plate_height = measured_plate_height + plate_thickness_leeway/2
leewayed_plate_thickness = measured_plate_thickness + plate_thickness_leeway
leewayed_security_screw_hole_height = measured_security_screw_hole_height + 1
block_width = measured_plate_width + strong_wall_thickness*2 + plate_side_leeway
foot_y = block_width/2 - 8

foot_xs = [8,42]
foot_ys = [foot_y,-foot_y]

foot_screw_radius = 2
foot_screw_leeway = 0.3
security_screw_leeway = 0.3

plateish_corner = Point(50, 0, 10)
VESAish_corner = Point(10, 0, leewayed_security_screw_hole_height+strong_wall_thickness)
security_screw_plate_bottom_corner = Point(-measured_security_screw_hole_backset - security_screw_radius - security_screw_leeway - strong_wall_thickness, 0, leewayed_security_screw_hole_height)


@run_if_changed
def security_screw_hole():
    return Face(Circle(Axes(Point(-measured_security_screw_hole_backset, 0, 0),Up), security_screw_radius + security_screw_leeway)).extrude(Up*100)

@run_if_changed
def protrusion_cutaway():
    return Vertex(Origin).extrude(Front*16, centered=True).extrude(Up*31, Down*100).extrude(Right*1)

@run_if_changed
def bracket_mount():

    big_block = Face(Wire([
        # Point(0, 0, 0),
        Point(50, 0, 0),
        plateish_corner,
        VESAish_corner,
        Point(-measured_security_screw_hole_backset - security_screw_radius - security_screw_leeway - strong_wall_thickness, 0, leewayed_security_screw_hole_height + strong_wall_thickness),
        security_screw_plate_bottom_corner,
        # Point(-leewayed_plate_thickness-strong_wall_thickness, 0, leewayed_security_screw_hole_height),
        security_screw_plate_bottom_corner.projected(onto=Plane(Point(-leewayed_plate_thickness-strong_wall_thickness-1, 0, 0), Right), by=Direction(plateish_corner, VESAish_corner)),
        Point(-leewayed_plate_thickness-strong_wall_thickness-1, 0, 0),
    ], loop=True)).extrude(Back*block_width, centered=True)

    foot_cut = Compound(
        Face(Circle(Axes(Origin,Up), foot_screw_radius + foot_screw_leeway)).extrude(Up*100),
        # Face(Circle(Axes(Origin,Up), 6)).extrude(Up*6, Up*100),
        pointy_hexagon(short_radius = 3.9).extrude(Up*1.8, Up*100),
    )

    extra_diagonals = Face(Wire([
        security_screw_plate_bottom_corner,
        security_screw_plate_bottom_corner.projected(Plane(Origin, Right), by=Direction(plateish_corner, VESAish_corner))
    ], loop=True))

    result = big_block.cut([
        Vertex(Origin).extrude(Left*leewayed_plate_thickness).extrude(Back*(measured_plate_width+plate_thickness_leeway), centered=True).extrude(Up*leewayed_plate_height),
        Vertex(Origin).extrude(Left*100).extrude(Back*measured_grip_width, centered=True).extrude(Up*leewayed_security_screw_hole_height),
        Vertex(Origin).extrude(Left*100).extrude(Back*measured_nub_width, centered=True).extrude(Up*measured_nub_height),
        security_screw_hole,
        protrusion_cutaway,
    ])
    # preview(result)
    # result = Fillet(result, [(e, 0.9) for e in result.edges() if e.bounds().min()[2] +0.1 < e.bounds().max()[2]])

    result = result.cut([foot_cut @ Translate(x,y,0) for x in foot_xs for y in foot_ys])
    save_STL("bracket", result)
    export("bracket.stl", "bracket_3.stl")
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

@run_if_changed
def vesa_plate():
    
    vesa_thickness=10
    vesa_width=120
    vesa_height=120
    vesa_center = Point(0,0,20)

    big_block = Face(Wire([
        Point(vesa_thickness, 0, 0),
        Point(vesa_thickness, 0, vesa_center[2] + vesa_height/2),
        Point(-measured_security_screw_hole_backset - security_screw_radius - security_screw_leeway - strong_wall_thickness, 0, vesa_center[2] + vesa_height/2),
        security_screw_plate_bottom_corner,
        # Point(-leewayed_plate_thickness-strong_wall_thickness, 0, leewayed_security_screw_hole_height),
        security_screw_plate_bottom_corner.projected(onto=Plane(Point(-leewayed_plate_thickness-strong_wall_thickness-1, 0, 0), Right), by=Direction(plateish_corner, VESAish_corner)),
        Point(-leewayed_plate_thickness-strong_wall_thickness-1, 0, 0),
    ], loop=True)).extrude(Back*(measured_plate_width + vesa_thickness*2 + plate_side_leeway), centered=True)
    big_block = Chamfer(big_block, [(e, 1) for e in big_block.edges()])

    grip = big_block.cut([
        Vertex(Origin).extrude(Left*leewayed_plate_thickness).extrude(Back*(measured_plate_width+plate_thickness_leeway), centered=True).extrude(Up*leewayed_plate_height),
        Vertex(Origin).extrude(Left*100).extrude(Back*measured_grip_width, centered=True).extrude(Up*leewayed_security_screw_hole_height),
        Vertex(Origin).extrude(Left*100).extrude(Back*measured_nub_width, centered=True).extrude(Up*measured_nub_height),
        security_screw_hole,
        Face(Circle(Axes(Point(-measured_security_screw_hole_backset, 0, leewayed_security_screw_hole_height + strong_wall_thickness),Up), security_screw_radius + security_screw_leeway + 8)).extrude(Up*100),
        protrusion_cutaway,
    ])

    vesa_plate = Vertex(vesa_center).extrude(Right*vesa_thickness).extrude(Up*vesa_width, centered=True).extrude(Back*vesa_height, centered=True)

    vesa_hole = Face(Circle(Axes(vesa_center, Right), 2.2)).extrude(Right*100, centered=True)
    vesa_holes = [vesa_hole @ Translate(dir * dist / 2) for dir in [Vector(0,1,1),Vector(0,1,-1),Vector(0,-1,-1),Vector(0,-1,1),] for dist in [75, 100]]

    vesa_cutaways = [Face(Circle(Axes(vesa_center, Right), vesa_width*0.4)).extrude(Right*100, centered=True) @ Translate(dir*90) for dir in [Back,Up,Down,Front]]
    # preview(vesa_cutaways, vesa_plate)
    vesa_plate = vesa_plate.cut(vesa_cutaways)
    vesa_plate = Chamfer(vesa_plate, [(e, 1) for e in vesa_plate.edges()])

    vesa_plate = vesa_plate.cut(vesa_holes + [protrusion_cutaway])

    #

    result = Compound(grip, vesa_plate)
    save_STL("vesa_plate", result)
    export("vesa_plate.stl", "vesa_plate_1.stl")
    preview(result)
    return result

preview(bracket_mount, [foot @ Translate(x,y,-6) for x in foot_xs for y in foot_ys])
