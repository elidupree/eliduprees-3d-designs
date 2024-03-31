import math

from pyocct_system import *
initialize_pyocct_system()

inch = 25.4
curve_radius = 100
pipe_radius = inch * 1.25 / 2
curve_center = Point(0,0,curve_radius)
curve_axis = Back
curve_swept_degrees = -60
lots = 500

@run_if_changed
def pipe_solid_cross_section():
    return Face(Wire(Circle(Axes(Origin, Right), pipe_radius)))
@run_if_changed
def pipe_interior_cross_section():
    return Face(Wire(Circle(Axes(Origin, Right), pipe_radius - 1.0)))
@run_if_changed
def pipe_wall_cross_section():
    return pipe_solid_cross_section.cut(pipe_interior_cross_section)

@run_if_changed
def main_pipe():
    return pipe_wall_cross_section.revolve(Axis(curve_center, Back), Degrees(curve_swept_degrees))

@run_if_changed
def main_pipe_interior():
    return pipe_interior_cross_section.revolve(Axis(curve_center, Back), Degrees(curve_swept_degrees))

@run_if_changed
def untouched_part():
    return Vertex (Origin).extrude(Up*pipe_radius*2).extrude(Back*pipe_radius*2, centered=True).revolve(Axis(curve_center, Back), Degrees(curve_swept_degrees))

@run_if_changed
def dust_pipe_cross_section():
    fins = [Vertex(0,0,z).extrude(Back*lots, centered=True).extrude(Up*1.0, centered = True) for z in subdivisions (-pipe_radius, pipe_radius, max_length = 5)[1:-1]]
    fins = Intersection(Compound(fins), pipe_solid_cross_section)
    return Compound (pipe_wall_cross_section, fins)



@run_if_changed
def dust_collector_y():
    return Compound (
        dust_pipe_cross_section.extrude (Right *100).cut(main_pipe_interior),
        main_pipe.cut(pipe_interior_cross_section.extrude (Right *100)))

preview(dust_collector_y)
# preview(main_pipe, untouched_part)