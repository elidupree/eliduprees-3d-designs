import math
from pyocct_system import *

initialize_pyocct_system()

inch = 25.4
lots = inch*50

monitor_thickness = 9.35
monitor_width = 11.7*inch
monitor_height = 7.8*inch

monitor_distance = 22* inch

rod_diameter = inch/4
rod_radius = rod_diameter/2

#monitor_angle =

bracket_width = 60
bracket_inset = (monitor_width - 180)/2
bracket_wall_thickness = 3
bezel_coverage = 2

plate_clearance = 13 - rod_diameter

sheath_radius = rod_radius + bracket_wall_thickness

@run_if_changed
def bracket_shared():
    sheath = Face (Circle(Axes(Origin, Up), sheath_radius)).extrude (Down * lots, centered=True)
    wing = Vertex(Origin).extrude(Back*sheath_radius, Front*(rod_radius+plate_clearance+monitor_thickness+bracket_wall_thickness)).extrude (Down * lots, centered=True).extrude (Right * lots).cut(HalfSpace(Origin, Direction(-1, -1, 0)))
    filter = Face(Wire([
        Origin + Down * bracket_inset + Left * sheath_radius,
        Origin + Down * bracket_inset + Right * sheath_radius,
        Origin + Right * bracket_width + Up * bracket_wall_thickness,
        Origin + Left * sheath_radius + Up * bracket_wall_thickness,
    ], loop=True)).extrude (Back*lots, centered=True)
    monitor_cut = Compound(
        Vertex(Origin + Front*(rod_radius+plate_clearance)).extrude(Front*monitor_thickness).extrude (Down * lots).extrude (Right * lots, centered=True),
        Vertex(Origin + Front*sheath_radius + Down*bezel_coverage).extrude(Front*lots).extrude (Down * lots).extrude (Right * lots, centered=True),
    )
    rod_cut = Face (Circle(Axes(Origin, Up), rod_radius)).extrude (Down * lots, centered=True)
    return Compound(sheath, wing).intersection(filter).cut(monitor_cut).cut(rod_cut)

def bracket_cuts(parity):
    f = Face(Circle(Axes(Origin, Up), sheath_radius + 2))
    cuts = [
        f.extrude(Up*(top+0.0), Up*(bottom-0.0))
        for i, (top, bottom) in enumerate(pairs(subdivisions(bracket_wall_thickness, -bracket_inset, amount=7)))
        if i % 2 == parity
    ]
    return Compound(cuts)

@run_if_changed
def bracket_right():
    return bracket_shared.cut(bracket_cuts(0))

@run_if_changed
def bracket_left():
    return (bracket_shared @ Mirror(Left)).cut(bracket_cuts(1))

@run_if_changed
def save():
    save_STL("bracket_left", bracket_left)
    save_STL("bracket_right", bracket_right)

preview(bracket_right, bracket_left)