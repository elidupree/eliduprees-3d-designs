import math

from pyocct_system import *

initialize_pyocct_system()

chamber_inner_radius=40
chamber_wall_thickness = 0.5
chamber_outer_radius = chamber_inner_radius + chamber_wall_thickness
chamber_inner_height = 40
chamber_outer_height = chamber_inner_height + chamber_wall_thickness*2
central_axle_radius = 3
axle_separation = 0.1
sleeve_thickness = 1.0


@run_if_changed
def cylindrical_chamber_outer_solid():
    return Face (Circle(Axes (Origin, Up), chamber_outer_radius)).extrude (Up*chamber_outer_height, centered=True)
@run_if_changed
def cylindrical_chamber_inner_solid():
    return Face (Circle(Axes (Origin, Up), chamber_inner_radius)).extrude (Up*chamber_inner_height, centered=True)
@run_if_changed
def cylindrical_chamber():
    return cylindrical_chamber_outer_solid.cut(cylindrical_chamber_inner_solid)

@run_if_changed
def two_independent_wheels():
    chamber = cylindrical_chamber
    hole_span_angle = Degrees(20)
