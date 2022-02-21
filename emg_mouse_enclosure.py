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
wall_curve_points = (
    [Between(a, b, amount) + Left*1.2
       for amount in subdivisions (-0.25, 1.2, amount=5)]
  + [Between(c, d, amount) + Right*(3.4 + porthole_depth)
       for amount in subdivisions (-0.3, 1.35, amount=3)]
)


wall_curve = BSplineCurve (wall_curve_points, BSplineDimension (periodic = True))
wall_curve_length = wall_curve.length()
ankle_start_distance = wall_curve.distance (closest =a) - I will 4
ankle_finish_distance = wall_curve.distance (closest =b) + 5

perforated_length = ankle_start_distance - ankle_finish_distance
num_perforated_columns = round (perforated_length/porthole_width)
porthole_exact_width = perforated_length/num_perforated_columns

print (ankle_start_distance, ankle_finish_distance, wall_curve_length, perforated_length)


def perforated_column (start_distance, finish_distance, parity):
  start = wall_curve.derivatives (distance = start_distance)
  finish = wall_curve.derivatives (distance = finish_distance)
  delta = finish.position - start.position
  length = finish_distance - start_distance
  inwards = (delta@Rotate(Up, degrees=90)).normalized()
  natural_points = [
    start.position + start.tangent*length/3,
    finish.position - finish.tangent*length/3,
  ]
  straight_points = [
    start.position + delta/3,
    finish.position - delta/3,
  ]
  cup_points = [a+inwards*porthole_depth for a in straight_points]
  for l in [natural_points, straight_points, cup_points]:
    l.insert(0, start.position)
    l.append(finish.position)
  
  def natural_row(height):
    return [a + Up*height for a in natural_points]
    
  def cup_row(height, cup_fraction):
    return [Between (a,b,smootherstep(cup_fraction)) + Up*height for a,b in zip (natural_points, cup_points)]
  
  def straight_row(height, straight_fraction):
    return [Between (a,b, straight_fraction**2) + Up*height for a,b in zip (natural_points, straight_points)]
  
  cup_length = porthole_depth*1.5
  straight_recovery_length = 3
  segment_length = cup_length + straight_recovery_length
    
  current_height = 0
  current_rows = []
  rowses = []
  if parity > 0:
    current_height = segment_length/2
    current_rows.extend (natural_row(height) for height in subdivisions (0, current_height, amount = 5))
    
  while current_height < controller_length - segment_length:
    current_rows.extend (cup_row (current_height + cup_fraction*cup_length, cup_fraction) for cup_fraction in subdivisions (0, 1, amount = 5))
    current_height += cup_length
    rowses.append(current_rows)
    current_rows = [straight_row (current_height + (1-straight_fraction)*straight_recovery_length, straight_fraction) for straight_fraction in subdivisions (1, 0, amount = 5)]
    current_height += straight_recovery_length
  
  current_rows.extend (natural_row(height) for height in subdivisions (current_height, controller_length, amount = 5))
  rowses.append(current_rows)
  
  result = []
  for rows in rowses:
    surface = BSplineSurface (rows)
    offset_surface = BSplineSurface([[p + surface.normal(closest=p)*printed_wall_thickness for p in row] for row in rows])
    joiner = Loft(Face(surface).outer_wire(), Face(offset_surface).outer_wire())
    result.append (Solid(Shell(Face(surface).complemented(), Face(offset_surface), joiner.complemented().faces())))
  return result
    

perforated_columns = [
  perforated_column (ankle_finish_distance + porthole_exact_width*index, ankle_finish_distance + porthole_exact_width*(index+1), index % 2)
  for index in range (num_perforated_columns)
]


preview (
  controller_board,
  sensor_boards,
  power_wire,
  ground_wire,
  signal_wires,
  wall_curve,
  perforated_columns,
)

