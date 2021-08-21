import math

from pyocct_system import *
initialize_system (globals())


printed_wall_thickness = 0.6

flat_wall_thickness = 1.0


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




@run_if_changed
def make_fan_bracket():
  outer_diameter = 6.5
  inner_diameter = 3
  contact_leeway = 0.3
  plate_thickness = 0.8
  
  a = outer_diameter/2
  b = 8-a
  fan_plate = Face(Wire([
    Point(-b, plate_thickness, 0),
    Point(b, plate_thickness, 0),
    Point(0, a, 0),
  ], loop = True).offset2D(a)).extrude(Up*5).cut(Face(Circle(Axes(Point(0, a, 0), Up), inner_diameter/2 + contact_leeway)).extrude(Up*lots, centered=True))
  
  fan_plate = Intersection(fan_plate, HalfSpace(Origin, Back))
  
  wall_plate = Vertex(Origin).extrude(Up*16).extrude(Back*plate_thickness).extrude(Right*16, centered=True)
  
  bracket = Compound(fan_plate, wall_plate)
  
  peg_radius = inner_diameter/2 - contact_leeway
  peg_length_without_catches = 16
  catch_length = 3
  catch_extension = 0.5
  catch_radius = peg_radius + catch_extension
  printability_height = peg_radius * 0.5**0.5
  peg = Face(Circle(Axes(Origin, Right), peg_radius)).extrude(Right*(peg_length_without_catches + 0.01))
  catch_half = Face(Wire([
    Point(-catch_length/2, -catch_radius, 0),
    Point(-catch_length, -peg_radius+0.1, 0),
    Point(-catch_length, -catch_extension - contact_leeway/4, 0),
    Point(0, -catch_extension - contact_leeway/4, 0),
    Point(0, -peg_radius+0.1, 0),
  ], loop = True)).extrude(Up*(printability_height*2), centered=True)
  catch = Compound(catch_half, catch_half @ Mirror(Back))
  
  peg= Compound(
    Intersection(peg, HalfSpace(Origin + Down*printability_height, Up)),
    catch,
    catch @ Mirror(Right) @ Translate(Right*peg_length_without_catches)
  )
  
  save("fan_bracket", bracket)
  save_STL("fan_bracket", bracket)
  preview(bracket)
  
  save("fan_bracket_peg", peg)
  save_STL("fan_bracket_peg", peg)
  preview(peg)


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
