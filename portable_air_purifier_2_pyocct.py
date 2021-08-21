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
cords_space = 25


CPAP_outer_radius = (22/2)
CPAP_inner_radius = CPAP_outer_radius-printed_wall_thickness

lots = 500





chamber_interior_back = 0
chamber_interior_top = 0
chamber_interior_length = battery_width
battery_right = 0
battery_back = chamber_interior_back - cords_space
battery_top = chamber_interior_top
battery_left = battery_right - battery_thickness
battery_front = battery_back - battery_width
battery_bottom = battery_top - battery_length
battery_plug_bottom = battery_bottom - battery_plug_length

battery = Vertex(battery_right, battery_back, battery_top).extrude(Front*battery_width).extrude(Down*battery_length).extrude(Left*battery_thickness)

batt_plug = Face( Wire (Edge (Circle (Axes (Point (battery_left+13, battery_back-16, battery_bottom), Up), battery_plug_diameter/2)))).extrude(Down*battery_plug_length)

batt_lights = Vertex(battery_right, Between(battery_front, battery_back), battery_bottom + 15).extrude(Front*28, centered=True)

c = Vertex(battery_right, battery_back, battery_bottom)
d = battery_back - batt_plug.bounds().max()[1]
c2 = Vertex(battery_right, battery_front, battery_bottom)
batt_holder_1 = Compound(
  c.extrude(Left*battery_thickness).extrude(Up*battery_length).extrude(Back*flat_wall_thickness),
  c.extrude(Left*battery_thickness).extrude(Front*d).extrude(Down*flat_wall_thickness),
  c.extrude(Front*battery_width, Back*(chamber_interior_back - battery_back)).extrude(Up*battery_length).extrude(Right*flat_wall_thickness).cut(batt_lights.extrude(Right*lots).extrude(Down*lots) @ Translate(Up*5)),
  c2.extrude(Left*battery_thickness).extrude(Up*battery_length).extrude(Front*flat_wall_thickness),
  c2.extrude(Left*battery_thickness).extrude(Back*d).extrude(Down*flat_wall_thickness),
)


chamber_interior_front_to_airspace_front = strong_filter_depth_without_seal + strong_filter_seal_depth_expanded + plenty_airspace
batt_chamber_wall = Vertex(battery_left, chamber_interior_back, chamber_interior_top).extrude(Front*(chamber_interior_length + chamber_interior_front_to_airspace_front)).extrude(Down*(battery_length+battery_plug_length)).extrude(Left*flat_wall_thickness)


chamber_interior_right = battery_left - flat_wall_thickness
chamber_interior_front = chamber_interior_back - chamber_interior_length
chamber_interior_wall_right = chamber_interior_right - strong_filter_width
chamber_interior_bottom = chamber_interior_top - strong_filter_length
chamber_interior_left = chamber_interior_wall_right - (strong_filter_width**2 - chamber_interior_length**2)**0.5
chamber_interior_width = chamber_interior_right - chamber_interior_left

butt_chamber_wall = Vertex(chamber_interior_right, chamber_interior_back, chamber_interior_top).extrude(Back*flat_wall_thickness).extrude(Down*(battery_length+battery_plug_length)).extrude(Left*chamber_interior_width, Right*battery_thickness)

chamber_interior_wall = Vertex(chamber_interior_wall_right, chamber_interior_back, chamber_interior_top).extrude(Front*(chamber_interior_length + chamber_interior_front_to_airspace_front)).extrude(Down*(strong_filter_length)).extrude(Left*flat_wall_thickness)

fan_center_height = Between(chamber_interior_top, chamber_interior_bottom)
fan_exit = Vertex(chamber_interior_wall_right, chamber_interior_back, fan_center_height).extrude(Front*fan_exit_width).extrude(Down*fan_thickness, centered=True).extrude(Left*fan_exit_length)
fan_body = Vertex(chamber_interior_wall_right, chamber_interior_back, fan_center_height).extrude(Front*fan_width).extrude(Down*fan_thickness, centered=True).extrude(Right*(fan_length - fan_exit_length))


in_filter = Vertex(chamber_interior_right, chamber_interior_front, chamber_interior_top).extrude(Front*strong_filter_depth_without_seal).extrude(Down*strong_filter_length).extrude(Left*strong_filter_width)

along_out_filter = Direction(Point(chamber_interior_left, chamber_interior_back, 0), Point(chamber_interior_wall_right, chamber_interior_front, 0))
out_of_out_filter = along_out_filter.cross(Up)

#out_filter_left = chamber_interior_left - strong_filter_depth_without_seal
out_filter = Vertex(chamber_interior_left, chamber_interior_back, chamber_interior_top).extrude(along_out_filter*strong_filter_width).extrude(Down*strong_filter_length).extrude(out_of_out_filter*strong_filter_depth_without_seal)

a = Point (chamber_interior_left, chamber_interior_back, chamber_interior_bottom)
b = Point (chamber_interior_wall_right, chamber_interior_front, chamber_interior_bottom)
cpap_approx = Face( Wire (Edge (Circle (Axes (Between(a, b, 0.52), Up), CPAP_outer_radius)))).extrude(Down*50) @ Translate(out_of_out_filter * (strong_filter_depth_without_seal + CPAP_inner_radius))

cpaps_approx = Compound(cpap_approx @ Translate(along_out_filter*16), cpap_approx @ Translate(along_out_filter*-16))


cover_interior_left = chamber_interior_left + (out_of_out_filter*strong_filter_depth_with_seal)[0]
cover_interior_right = battery_right
cover_interior_front = chamber_interior_front - chamber_interior_front_to_airspace_front
cover_interior_back = chamber_interior_back + flat_wall_thickness
cover_interior_top = chamber_interior_top + flat_wall_thickness
cover_interior_bottom = battery_plug_bottom

cover_interior = (Vertex(Origin)
  .extrude(Right*cover_interior_left, Right*cover_interior_right)
  .extrude(Up*cover_interior_bottom, Up*cover_interior_top)
  .extrude(Back*cover_interior_front, Back*cover_interior_back)
  )

cis = cover_interior.bounds().size()
print("Cover interior bounds: "+str(cis))

preview(
  battery,
  batt_plug,
  batt_holder_1,
  batt_lights,
  batt_chamber_wall,
  Compound(chamber_interior_wall.edges()),
  Compound(butt_chamber_wall.edges()),
  fan_exit,
  fan_body,
  in_filter,
  out_filter,
  cpaps_approx,
  Compound(cover_interior.edges()),
  )
