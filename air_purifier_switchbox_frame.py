import math

from pyocct_system import *
initialize_pyocct_system()

outer_width= 78
outer_length = 133
wall_thickness=8
wall_thickness_bot=13

depth = 24.5

power_out_width = 1.75
power_out_depth = 3.8

power_in_diameter = 5.7

heater_power_width = 2.3
heater_power_depth = 4.6

screw_radius = 2.8
screw_inset = 4.2
screw_inset_long = 9

brick = Vertex(Origin).extrude(Right*outer_width).extrude(Back*outer_length).extrude(Down*depth)
brick = Fillet(brick, [(e, 6) for e in brick.edges() if all_equal((v[1],v[0]) for v in e.vertices())])

main_hole = Vertex(Origin).extrude(Right*wall_thickness, Right*(outer_width - wall_thickness)).extrude(Back*wall_thickness_bot, Back*(outer_length- wall_thickness)).extrude(Down*depth)
main_hole = main_hole.cut(HalfSpace(Point(outer_width-15, 0), Direction(1, -0.15, 0)))
main_hole = main_hole.cut(HalfSpace(Point(outer_width, 19, 0), Direction(0.15, -1, 0)))
main_hole = Fillet(main_hole, [(e, 4) for e in main_hole.edges() if all_equal((v[1],v[0]) for v in e.vertices()) and (e.bounds().max()[0] > 50 or e.bounds().max()[1] > 50)])

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
    Point(-35, -3),
    Point(-35, 0),
    Point(-35, 3),
    Point(-32, 10),
    Point(-18, 10),
    Point(-8, 12),
    Point(-5, 30),
    Point(-5, 40),
    Point(-30, 50),
]))
power_in_cut=power_in_route.offset2d(power_in_diameter/2, fill = True).extrude(Down*power_in_diameter)

heater_power_cut = Vertex(0,65,0).extrude(Back*heater_power_width).extrude(Down*heater_power_depth).extrude(Right*50, Right*outer_width)

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

def strain_reliever(reliever_depth, reliever_width):
    reliever_thickness = 2
    reliever_length = 10
    brick = Vertex(Origin).extrude(Left*(reliever_width + 2*reliever_thickness), centered=True).extrude(Down*(reliever_depth + reliever_thickness)).extrude(Front*reliever_length)
    hole = Vertex(Origin).extrude(Left*reliever_width, centered=True).extrude(Down*reliever_depth).extrude(Front*reliever_length)

    result = brick.cut(hole)
    result = Fillet(result, [(e, 1.6) for e in result.edges() if e.bounds().min()[2] < -reliever_depth-0.1 and e.bounds().min()[1] < - 0.1])

    return result


solid = brick.cut([
    main_hole,
    screw_cut@Translate(Vector(screw_inset,screw_inset_long)),
    screw_cut@Translate(Vector(outer_width-screw_inset,screw_inset_long)),
    screw_cut@Translate(Vector(screw_inset,outer_length-screw_inset_long)),
    screw_cut@Translate(Vector(outer_width-screw_inset,outer_length-screw_inset_long)),
    power_out_cut@Translate(Right*9),
    power_out_cut@Translate(Right*24),
    power_in_cut@Translate(Right*outer_width),
    heater_power_cut,
    air_hole_column_staircase @ Translate(Back*22),
    air_hole_column_staircase @ Translate(Back*(22 + air_hole_column_spacing*4)),

    air_hole_column_staircase @ Translate(Back*70 + Right*(outer_width-wall_thickness)),])

solid = Compound(
    solid,
    strain_reliever(power_out_depth, power_out_width) @ Translate(Right*9),
    strain_reliever(power_out_depth, power_out_width) @ Translate(Right*24),
    strain_reliever(power_in_diameter, power_in_diameter) @ Translate(Right*(outer_width-35)),
)

save_STL("air_purifier_switchbox_frame", solid)
# export("air_purifier_switchbox_frame.stl", "air_purifier_switchbox_frame_2.stl")
preview (solid, power_out_route@Translate(Right*8), power_in_route@Translate(Right*outer_width))
