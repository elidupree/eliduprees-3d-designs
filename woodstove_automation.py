import math
from pyocct_system import *

initialize_pyocct_system()

from gears import InvoluteGear

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
max_knob_radius = 21.4/2 #12
knob_length=35
dial_radius=33/2
dial_center = Origin+Right*(dial_radius+14) + Up*3
dial_depth=24
plate_descent = 30

roller_solid_radius = 11/2
roller_smallest_radius = roller_solid_radius + 0.5
roller_largest_radius = roller_solid_radius + 1.5
gear_thickness =4
teeth1 = 30
teeth2 = 13

bearing_od = 12
bearing_depth = 4

pitch_radius = roller_smallest_radius+rod_radius
print("pitch_radius:", pitch_radius)

@run_if_changed
def first_gear_info():
    return InvoluteGear(teeth1, pitch_radius =pitch_radius)
@run_if_changed
def drive_gear_info():
    return InvoluteGear(teeth2, pitch_radius =pitch_radius*teeth2/teeth1)

roller_center_y = -(first_gear_info.outside_radius + 1) #roller_largest_radius - min_exposed_rod_length

#motor_shaft_tip_center = Origin+ Left * (max_knob_radius + 1)+ Front * motor_width / 2 + Down*(plate_descent - motor_width/2)
motor_shaft_tip_center = Point(-(max_knob_radius + 1), roller_center_y - first_gear_info.pitch_radius - drive_gear_info.pitch_radius, -pitch_radius)

@run_if_changed
def motor():
    center =motor_shaft_tip_center+ Left * (motor_shaft_length)
    body = Vertex (center).extrude (Left *motor_depth).extrude (Front * motor_width, centered = True).extrude (Up * motor_width, centered = True)
    ring =Face (Circle (Axes (center, Right),motor_ring_radius)).extrude (Right *motor_ring_depth)
    shaft =Face (Circle (Axes (center, Right),motor_shaft_radius)).extrude (Right *motor_shaft_length).cut (Vertex (center + Right *(motor_shaft_length - motor_d_length)+ Down*(motor_shaft_radius - motor_d_diameter)).extrude (Right *lots).extrude (Up * lots).extrude (Back*lots, centered = True))
    return [body, ring, shaft]

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

@run_if_changed
def gears():
    first = (first_gear_info.shape @ Rotate(Back, Degrees(90))) @ Translate(Back*roller_center_y + Up*pitch_radius + Left*(max_knob_radius+1))
    first = first.extrude(Left *gear_thickness)
    second = first @ Translate(Down*pitch_radius*2)
    third = (drive_gear_info.shape @ Rotate(Back, Degrees(90))) @ Translate(motor_shaft_tip_center - Origin)
    third = third.extrude(Left *gear_thickness)
    third = third.cut(motor[2])
    save_STL("drive_gear", third)
    #third = Chamfer(third, [(e,  for e in third.edges()])
    return [first, second, third]

@run_if_changed
def rollers():
    first = Face(Circle(Axes(Origin, Left), roller_largest_radius)).extrude(Left*(max_knob_radius+1), Right*(rod_radius+1)) @ Translate(Back*roller_center_y + Up*pitch_radius)
    second = first @ Translate(Down*pitch_radius*2)
    return [first, second]

@run_if_changed
def bearings():
    first = Face(Circle(Axes(Origin, Left), bearing_od/2)).extrude(Left*(bearing_depth)) @ Translate(Back*roller_center_y + Up*pitch_radius + Left*(max_knob_radius+1+gear_thickness))
    second = first @ Translate(Down*pitch_radius*2)
    result = [first, second]
    result.extend([b @ Translate(Right*(max_knob_radius+1+gear_thickness+rod_radius+1 + bearing_depth)) for b in result])
    return result


preview (plate, rod, motor, dial, gears, rollers, bearings)