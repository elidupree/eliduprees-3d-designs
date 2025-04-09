import math

from pyocct_system import *
initialize_pyocct_system()

bolt_od = 5
nut_od = 5.9
nut_flange_od = 10.5
nut_flange_thickness = 2.2

thrust_bearing_id = 6
thrust_bearing_od = 11
thrust_bearing_thickness=4.5

bolt_leeway = 2
nut_length = 8

nut_bottom_z = bolt_leeway
nut_inner_corner_z = nut_bottom_z + nut_length
nut_top_z = nut_inner_corner_z + nut_flange_thickness
thrust_bearing_bottom_z = nut_inner_corner_z - thrust_bearing_thickness


bolt = Face(Circle(Axes(Point(0, 0, 0), Up), bolt_od/2)).extrude(Up*bolt_leeway)
nut = Face(Circle(Axes(Point(0, 0, bolt_leeway), Up), nut_od/2)).extrude(Up*nut_length)
nut_flange = Face(Circle(Axes(Point(0, 0, bolt_leeway+nut_length), Up), nut_flange_od/2)).extrude(Up*nut_flange_thickness)
thrust_bearing = Face(Circle(Axes(Point(0, 0, bolt_leeway+nut_length), Up), thrust_bearing_od/2)).cut(Face(Circle(Axes(Point(0, 0, bolt_leeway+nut_length), Up), thrust_bearing_id/2))).extrude(Down*thrust_bearing_thickness)

part_profile = Face(Wire([
    Point(thrust_bearing_od/2+0.3, 0, nut_top_z),
    Point(thrust_bearing_od/2+0.3, 0, thrust_bearing_bottom_z),
    Point(thrust_bearing_id/2, 0, thrust_bearing_bottom_z),
    Point(thrust_bearing_id/2 + thrust_bearing_bottom_z, 0, 0),
    Point(10, 0, 0),
    Point(10, 0, nut_top_z),
], loop=True))

preview(bolt, nut, nut_flange, thrust_bearing, part_profile) 
