import math

from pyocct_system import *
from pyocct_utils import inch
initialize_pyocct_system()

layer_height = 0.3
slider_strip_thickness = 3

def dimpled_wall_cross_section_points(a, b, offs, phase):
    def modified_point(index, p):
        termination = smootherstep(min(p.distance(a), p.distance(b)), 5, 4)
        if termination != 0:
            return p + offs*termination*-2
        if index % 19 == phase % 19:
            return p + offs
        return p
    return [modified_point(index, p) for index, p in enumerate (subdivisions(a, b, max_length = 1))]

def dimpled_wall_layer(a, b, extrude_vector, phase):
    offset_depth = 1
    a_points = dimpled_wall_cross_section_points(a, a+extrude_vector, Direction(a, b)*offset_depth, phase)
    b_points = dimpled_wall_cross_section_points(b, b+extrude_vector, Direction(b, a)*offset_depth, phase)
    # preview(a_points)
    return Face(BSplineSurface([
        a_points, b_points
    ], u=BSplineDimension(degree =1))).extrude (Up*layer_height)

def slider_strip(length):
    layers = []
    strip_height =9
    for layer_index in range(0, round (strip_height/layer_height)):
        bottom_z = layer_index * layer_height
        middle_z = bottom_z + layer_height / 2
        chevronness = abs(middle_z - (strip_height+slider_strip_thickness)/2) - (strip_height+slider_strip_thickness)/2
        a = Point(0, chevronness-5, middle_z)
        b = a + Back*slider_strip_thickness
        layers.append (dimpled_wall_layer(a, b, Right*length, layer_index*7))

    wall1 = Compound (layers)

    struts = [Vertex(p).extrude (Right*slider_strip_thickness).extrude(Up*slider_strip_thickness).extrude(Back*10, centered=True) for p in subdivisions(Origin, Point(length-slider_strip_thickness, 0, 0), max_length=inch)]
    end_stops = [Vertex(p).extrude (Right*2).extrude(Up*slider_strip_thickness, Up*strip_height).extrude(Back*14, centered=True) for p in [Origin, Point(length-2, 0, 0)]]
    return Compound (wall1, wall1 @ Mirror(Back), struts, end_stops)


@run_if_changed
def slider_strip_10in():
    result = slider_strip(10*inch)
    save_STL("slider_strip_10in", result, linear_deflection=0.2)
    return result

# export("slider_strip_10in.stl", "slider_strip_10in_1.stl")

preview(slider_strip_10in)