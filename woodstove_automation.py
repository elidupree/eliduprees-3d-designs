import math

from pyocct_system import *

initialize_pyocct_system()

lots=500
motor_width = 42
motor_depth = 38
motor_shaft_radius = 2.5
motor_shaft_length = 23
motor_d_diameter = 4.5
motor_d_length = 20
motor_ring_radius = 11
motor_ring_depth = 1.9

rod_radius = 9.5/2
min_exposed_rod_length = 20
max_knob_radius = 12
knob_length=35
dial_radius=33/2
dial_center = Origin+Right*(dial_radius+14) + Up*3
dial_depth=24
plate_descent = 30

@run_if_changed
def motor():
    center =Origin+ Left * (motor_shaft_length + max_knob_radius + 5)+ Front * motor_width / 2 + Down*(plate_descent - motor_width/2)
    body = Vertex (center).extrude (Left *motor_depth).extrude (Front * motor_width, centered = True).extrude (Up * motor_width, centered = True)
    ring =Face (Circle (Axes (center, Right),motor_ring_radius)).extrude (Right *motor_ring_depth)
    shaft =Face (Circle (Axes (center, Right),motor_shaft_radius)).extrude (Right *motor_shaft_length).cut (Vertex (center + Right *(motor_shaft_length - motor_d_length)+ Down*(motor_shaft_radius - motor_d_diameter)).extrude (Right *lots).extrude (Up * lots).extrude (Back*lots, centered = True))
    return Compound (body, ring, shaft)

@run_if_changed
def dial():
    return Face (Circle (Axes (dial_center, Front),dial_radius)).extrude (Front *dial_depth)

@run_if_changed
def plate():
    return Vertex(Origin).extrude (Left *500, centered = True).extrude (Up * 90, Down*plate_descent)

@run_if_changed
def rod():
    r = Face (Circle (Axes (Origin, Front),rod_radius)).extrude (Front *min_exposed_rod_length)
    k = Face (Circle (Axes (Origin + Front *min_exposed_rod_length, Front),max_knob_radius)).extrude (Front *knob_length)
    return Compound(r,k)

preview (plate, rod, motor, dial)