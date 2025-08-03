import math

from pyocct_system import *

initialize_pyocct_system()

# conveniently the premade magnetic connectors are documented and the physical objects match the documentation to within 0.04mm tolerance, usually erring on the small side. that's close enough that I have used the official measurements here.
premade_lip_thickness = premade_lip_length = 1
premade_lip_backset = 2
premade_total_thickness = premade_total_width = 4
premade_pin_radius = 0.35
premade_pin_separation = 2.5
premade_pin_length = 1.5
premade_magnet_offset = 4
premade_body_length = 12.5
premade_round_radius = premade_total_width/2

@run_if_changed
def premade_connector_representation():
    def rounded(length):
        return Compound(Vertex (Origin).extrude (Left * (length - 2*premade_round_radius), centered = True).extrude(Up*premade_total_width, centered=True), [Face(Circle(Axes(Origin + Right*d*(length/2 - premade_round_radius), Back), premade_round_radius)) for d in [-1, 1]])
    body = rounded(premade_body_length).extrude (Back * premade_total_thickness)
    lip = rounded(premade_body_length + premade_lip_length*2).extrude (Back * premade_lip_thickness) @ Translate(Back*premade_lip_backset)
    pins = [
        Face(Circle(Axes(Origin + Right*d*premade_pin_separation/2, Back), premade_pin_radius)).extrude (Back * premade_pin_length) @ Translate(Back*premade_total_thickness)
        for d in [-1, 1]
    ]

    return Compound(body, lip, pins)

def rounded_90deg_corner_wire(points):


preview(premade_connector_representation)
