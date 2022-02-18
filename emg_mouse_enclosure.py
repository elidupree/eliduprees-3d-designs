import math

from pyocct_system import *
initialize_system (globals())


printed_wall_thickness = 0.6
contact_leeway = 0.4


sensor_width = 21.9
sensor_length = 35.1
sensor_board_thickness = 1.2
sensor_thickness_with_connectors = 6.7
space_below_sensor_induced_by_audio_cable_connector = 0.6 # my current audio cable connectors are that wide; I could fix this by buying thinner audio cables, but who cares
min_sensor_spacing = sensor_thickness_with_connectors + space_below_sensor_induced_by_audio_cable_connector
controller_width = 31.1
controller_length = 38.7
controller_board_thickness = 0.9
ports_slot_width = 10
porthole_depth = 5
porthole_width = porthole_depth*2

controller_contact_inset = 1.2
controller_contact_spacing = 22.5/9

sensor_power_offset = Vector (0.0, 2.5, sensor_length + 3)


controller_back = 0
controller_front = controller_back - controller_board_thickness
a = -12.1
t = sensor_board_thickness
sensor_backs = [a+t-min_sensor_spacing*i for i in range(4)]

w = controller_width/2
i = controller_contact_inset
s = controller_contact_spacing
p = 13.2
power_source = Point (w - i - s, controller_front, p)
ground_source = power_source + Up*s
signal_sources = [
  power_source + Up*s*4 + Right*s,
  power_source@Mirror (Right) + Left*s + Up*s*3,
  power_source@Mirror (Right) + Left*s + Up*s*2,
  power_source@Mirror (Right) + Left*s + Up*s*4,
]




controller_board =Vertex (Origin + Back*controller_back).extrude (Left*controller_width, centered = True).extrude (Front*controller_board_thickness).extrude (Up*controller_length)

sensor_boards = Compound ([
  Vertex (Origin + Back*back).extrude (Left*sensor_width, centered = True).extrude (Front*sensor_board_thickness).extrude (Up*sensor_length)
  for back in sensor_backs
])

power_wire = Wire (
  power_source,
  [Origin + Back*back + sensor_power_offset for back in sensor_backs],
)
ground_wire = Wire (
  ground_source,
  [Origin + Back*back + sensor_power_offset + Right*2.0 for back in sensor_backs],
)
signal_wires = [
  Wire (
    source,
    Origin + Back*sensor_backs [0] + sensor_power_offset + Left*2.0 + Left*index + Back*3,
    Origin + Back*back             + sensor_power_offset + Left*2.0,
  )
  for index, (back, source) in enumerate (zip (sensor_backs, signal_sources))
]

a = Point (- controller_width/2, controller_back, 0)
b = Point (- sensor_width/2, sensor_backs [-1] - sensor_board_thickness, 0)
c = Point (sensor_width/2, sensor_backs [-1] - sensor_board_thickness, 0)
d = Point (controller_width/2, controller_back, 0)
wall_curve_points = [Between(a, b, amount) + Left*1.2 for amount in subdivisions (-0.25, 1.2, amount=5)] + [Between(c, d, amount) + Right*(3.4 + porthole_depth) for amount in subdivisions (-0.2, 1.25, amount=3)]


wall_curve = BSplineCurve (wall_curve_points, BSplineDimension (periodic = True))
wall_curve_length = wall_curve.length()
ankle_start_distance = wall_curve.distance (closest =a)
ankle_finish_distance = wall_curve.distance (closest =b)

perforated_length = ankle_start_distance - ankle_finish_distance
num_portholes = round (perforated_length/porthole_width)

print (ankle_start_distance, ankle_finish_distance, wall_curve_length, perforated_length)

def perforated_control_points (layer):
  def control_point (distance):
    derivatives = wall_curve.derivatives (distance = distance)
    perforated_fraction = (distance - ankle_finish_distance)/perforated_length
    if 0 < perforated_fraction < 1:
      portholes_past = perforated_fraction*num_portholes
      phase = portholes_past % 1
      portholes_past = math.floor(portholes_past)
      if portholes_past % 2 == 0:
        depth = math.sqrt(math.sin(phase * math.pi))*porthole_depth
        inwards = derivatives.tangent @ Rotate(Up, degrees=90)
        return derivatives.position + inwards*depth
    
    return derivatives.position
  
  return [control_point (distance) for distance in subdivisions (0, wall_curve_length, max_length = 2)]


preview (controller_board, sensor_boards, power_wire, ground_wire, signal_wires, wall_curve, BSplineCurve (perforated_control_points (0), BSplineDimension (periodic = True)))

