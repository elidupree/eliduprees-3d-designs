import math

from pyocct_system import *
initialize_pyocct_system()

bolt_od = 5
# nut_od = 5.9
# nut_flange_od = 10.5
# nut_flange_thickness = 2.2

thrust_bearing_id = 5
thrust_bearing_od = 15
thrust_bearing_thickness=2

bolt_leeway = 0.4
# nut_length = 8

# nut_bottom_z = bolt_leeway
# nut_inner_corner_z = nut_bottom_z + nut_length
# nut_top_z = nut_inner_corner_z + nut_flange_thickness
# thrust_bearing_bottom_z = nut_inner_corner_z - thrust_bearing_thickness
#
#
# bolt = Face(Circle(Axes(Point(0, 0, 0), Up), bolt_od/2)).extrude(Up*bolt_leeway)
# nut = Face(Circle(Axes(Point(0, 0, bolt_leeway), Up), nut_od/2)).extrude(Up*nut_length)
# nut_flange = Face(Circle(Axes(Point(0, 0, bolt_leeway+nut_length), Up), nut_flange_od/2)).extrude(Up*nut_flange_thickness)
# thrust_bearing = Face(Circle(Axes(Point(0, 0, bolt_leeway+nut_length), Up), thrust_bearing_od/2)).cut(Face(Circle(Axes(Point(0, 0, bolt_leeway+nut_length), Up), thrust_bearing_id/2))).extrude(Down*thrust_bearing_thickness)
#
# part_profile = Face(Wire([
#     Point(thrust_bearing_od/2+0.3, 0, nut_top_z),
#     Point(thrust_bearing_od/2+0.3, 0, thrust_bearing_bottom_z),
#     Point(thrust_bearing_id/2, 0, thrust_bearing_bottom_z),
#     Point(thrust_bearing_id/2 + thrust_bearing_bottom_z, 0, 0),
#     Point(10, 0, 0),
#     Point(10, 0, nut_top_z),
# ], loop=True))
#
# preview(bolt, nut, nut_flange, thrust_bearing, part_profile)

housing_od = 20
housing_wall_thickness = 2
housing_id = housing_od - housing_wall_thickness*2
housing_floor_thickness = 2

nut_od = 15
nut_thickness = 5


thrust_bearing_bottom = housing_wall_thickness
thrust_bearing_top = nut_bottom = thrust_bearing_bottom + thrust_bearing_thickness
nut_top = bolt_top = housing_wall_thickness + bolt_leeway + nut_thickness

bolt = Face(Circle(Axes(Point(0, 0, 0), Up), bolt_od/2)).extrude(Down*bolt_leeway, Up*bolt_top)
nut = Face(Circle(Axes(Point(0, 0, nut_bottom), Up), nut_od/2)).extrude(Up*nut_thickness)
thrust_bearing = Face(Circle(Axes(Origin, Up), thrust_bearing_od/2)).cut(Face(Circle(Axes(Origin, Up), thrust_bearing_id/2))).extrude(Up*thrust_bearing_bottom, Up*thrust_bearing_top)

housing_floor = Face(Circle(Axes(Origin, Up), housing_od/2)).extrude(Up*housing_floor_thickness)
housing_walls = Face(Circle(Axes(Origin, Up), housing_od/2)).cut(Face(Circle(Axes(Origin, Up), housing_id/2))).extrude(Up*housing_floor_thickness, Up*20)
preview(bolt, housing_floor, thrust_bearing, nut, housing_walls.wires())

button =