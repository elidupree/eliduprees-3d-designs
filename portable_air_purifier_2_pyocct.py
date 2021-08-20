import math

from pyocct_system import *
initialize_system (globals())


printed_wall_thickness = 0.6

flat_wall_thickness = 1.0

# extra leeway for rigid parts that need to fit into a slot, so that printing irregularities don't make them not fit.
# we generally want to rely on slightly springy parts rather than exact sizing; with a perfect fabrication process, I would use 0.0 for this. The positive number exists to compensate for my diagonal printing process adding some unnecessary thickness
contact_leeway = 0.4

strong_filter_length = 151.9
strong_filter_width = 101
strong_filter_depth_without_seal = 14
strong_filter_seal_depth_expanded = 2
strong_filter_seal_squish_distance = 0.5
strong_filter_seal_depth_squished = strong_filter_seal_depth_expanded - strong_filter_seal_squish_distance
strong_filter_depth_with_seal = strong_filter_depth_without_seal + strong_filter_seal_depth_squished
strong_filter_rim_inset = 6
strong_filter_airspace_wall_inset = strong_filter_rim_inset

fan_thickness = 28
fan_width = 79.7
fan_length = 78.9
fan_exit_width = 26
fan_exit_length = 8
fan_intake_circle_measured_radius = 24.4
fan_intake_circle_center_from_front = 40.3
fan_intake_circle_center_from_left = 44
fan_intake_circle_center_to_back = fan_length - fan_intake_circle_center_from_front
fan_intake_circle_center_to_right = fan_width - fan_intake_circle_center_from_left

plenty_airspace = 11

battery_thickness = 27.8
battery_width = 85.5
battery_length = 144.2
battery_cord_diameter = 3.5
battery_plug_diameter = 11.4
battery_plug_length = 38.2


CPAP_outer_radius = (22/2)
CPAP_inner_radius = CPAP_outer_radius-printed_wall_thickness

lots = 500





chamber_interior_back = 0
chamber_interior_top = 0
battery_right = 0
battery_back = chamber_interior_back
battery_top = chamber_interior_top
battery_left = battery_right - battery_thickness
battery_front = battery_back - battery_width
battery_bottom = battery_top - battery_length
battery_plug_bottom = battery_bottom - battery_plug_length

battery = Vertex(battery_right, battery_back, battery_top).extrude(Front*battery_width).extrude(Down*battery_length).extrude(Left*battery_thickness)

batt_plug = Face( Wire (Edge (Circle (Axes (Point (battery_left+13, battery_back-16, battery_bottom), Up), battery_plug_diameter/2)))).extrude(Down*battery_plug_length)

batt_lights = Vertex(battery_right, Between(battery_front, battery_back), battery_bottom + 15).extrude(Front*28, centered=True)

batt_chamber_wall = Vertex(battery_left, chamber_interior_back, chamber_interior_top).extrude(Front*strong_filter_width).extrude(Down*(battery_length+battery_plug_length)).extrude(Left*flat_wall_thickness)

chamber_interior_right = battery_left - flat_wall_thickness
chamber_interior_front = chamber_interior_back - strong_filter_width
chamber_interior_left = chamber_interior_right - strong_filter_width
chamber_interior_bottom = chamber_interior_top - strong_filter_length

butt_chamber_wall = Vertex(chamber_interior_right, chamber_interior_back, chamber_interior_top).extrude(Back*flat_wall_thickness).extrude(Down*(battery_length+battery_plug_length)).extrude(Left*strong_filter_width)


in_filter = Vertex(chamber_interior_right, chamber_interior_front, chamber_interior_top).extrude(Front*strong_filter_depth_without_seal).extrude(Down*strong_filter_length).extrude(Left*strong_filter_width)

out_filter_left = chamber_interior_left - strong_filter_depth_without_seal
out_filter = Vertex(chamber_interior_left, chamber_interior_back, chamber_interior_top).extrude(Front*strong_filter_width).extrude(Down*strong_filter_length).extrude(Left*strong_filter_depth_without_seal)

cpap_approx = Face( Wire (Edge (Circle (Axes (Point (out_filter_left - CPAP_inner_radius, Between(chamber_interior_back, chamber_interior_front), chamber_interior_bottom), Up), CPAP_outer_radius)))).extrude(Down*50)

cpaps_approx = Compound(cpap_approx @ Translate(Front*16), cpap_approx @ Translate(Back*16))


preview(battery, batt_plug, batt_lights, batt_chamber_wall, Compound(butt_chamber_wall.edges()), in_filter, out_filter, cpaps_approx)
