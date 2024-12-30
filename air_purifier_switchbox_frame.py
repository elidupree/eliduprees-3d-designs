import math

from pyocct_system import *
initialize_pyocct_system()

outer_width= 78
outer_length = 136
wall_thickness=8
wall_thickness_bot=13

depth = 24.5

power_out_width = 1.75
power_out_depth = 3.8

power_in_diameter = 5.7

screw_radius = 3
screw_inset = 5

brick = Vertex(Origin).extrude(Right*outer_width).extrude(Back*outer_length).extrude(Down*depth)
brick = Fillet(brick, [(e, 5) for e in brick.edges() if all_equal((v[1],v[0]) for v in e.vertices())])

main_hole = Vertex(Origin).extrude(Right*wall_thickness, Right*(outer_width - wall_thickness)).extrude(Back*wall_thickness_bot, Back*(outer_length- wall_thickness)).extrude(Down*depth)
main_hole = main_hole.cut(HalfSpace(Point(outer_width-15, 0), Direction(1, -0.15, 0)))
main_hole = main_hole.cut(HalfSpace(Point(outer_width, 19, 0), Direction(0.15, -1, 0)))
main_hole = Fillet(main_hole, [(e, 10) for e in main_hole.edges() if all_equal((v[1],v[0]) for v in e.vertices()) and (e.bounds().max()[0] > 50 or e.bounds().max()[1] > 50)])

power_out_route = Wire(BSplineCurve([
    Origin,
    Point(0, 4),
    Point(14, 3),
    Point(14, 6),
    Point(14, 9),
    Point(0, 8),
    Point(0, 13),
]))
power_out_cut=power_out_route.offset2d(power_out_width/2, fill = True).extrude(Down*power_out_depth)

power_in_route = Wire(BSplineCurve([
    Point(-38, -10),
    Point(-36, 0),
    Point(-36, 3),
    Point(-33, 10),
    Point(-18, 10),
    Point(-8, 12),
    Point(-5, 30),
    Point(-5, 40),
    Point(-30, 50),
]))
power_in_cut=power_in_route.offset2d(power_in_diameter/2, fill = True).extrude(Down*power_in_diameter)

screw_cut = Face(Circle(Axes(Origin,Up),screw_radius)).extrude(Down*depth)

air_hole_thickness = 1.5
space_between = (wall_thickness - air_hole_thickness*2)/3
from_edge = space_between + air_hole_thickness/2
air_hole = Wire([
    Point(0, 0, 0),
    Point(from_edge, 0, 0),
    Point(from_edge, 0, -(air_hole_thickness+space_between)),
    Point(wall_thickness-from_edge, 0, -(air_hole_thickness+space_between)),
    Point(wall_thickness-from_edge, 0, 0),
    Point(wall_thickness, 0, 0),
]).offset2d(air_hole_thickness/2, fill=True).extrude(Back*10) @ Translate(Down*air_hole_thickness/2)
air_hole_total_occupied = air_hole_thickness*2+space_between
air_hole_column_span = (depth - air_hole_total_occupied/3)
air_hole_rows = math.floor(air_hole_column_span / air_hole_total_occupied)
air_hole_column = Compound(air_hole @ Translate(Down*x) for x in subdivisions(0, air_hole_column_span - air_hole_total_occupied, amount = air_hole_rows))
air_hole_column_spacing = 10+space_between
air_hole_column_staircase = Compound(
    [air_hole_column @ Translate(0, k*air_hole_column_spacing, -k*air_hole_total_occupied/3)
    for k in range(2)],
    [air_hole_column @Mirror(Up) @ Translate(0, (2+k)*air_hole_column_spacing, (1-k)*air_hole_total_occupied/3 - depth)
     for k in range(2)],)

solid = brick.cut([
    main_hole,
    screw_cut@Translate(Vector(screw_inset,screw_inset)),
    screw_cut@Translate(Vector(outer_width-screw_inset,screw_inset)),
    screw_cut@Translate(Vector(screw_inset,outer_length-screw_inset)),
    screw_cut@Translate(Vector(outer_width-screw_inset,outer_length-screw_inset)),
    power_out_cut@Translate(Right*9),
    power_out_cut@Translate(Right*24),
    power_in_cut@Translate(Right*outer_width),
    air_hole_column_staircase @ Translate(Back*22),
    air_hole_column_staircase @ Translate(Back*(22 + air_hole_column_spacing*4)),

    air_hole_column_staircase @ Translate(Back*60 + Right*(outer_width-wall_thickness)),])

preview (solid, power_out_route@Translate(Right*8), power_in_route@Translate(Right*outer_width))
