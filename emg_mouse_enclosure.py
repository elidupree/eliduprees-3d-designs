import math

from pyocct_system import *
initialize_system (globals())


printed_wall_thickness = 0.8
contact_leeway = 0.4
lots = 100


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
slot_depth = 0.6

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
b = Point (- sensor_width/2 - 0.5, sensor_backs [-1] - sensor_board_thickness, 0)
c = Point (sensor_width/2 + 3.2 + porthole_depth, sensor_backs [-1] - sensor_board_thickness, 0)
d = Point (controller_width/2 + 3.0, controller_back, 0)
wall_curve_points = (
    [Between(a, b, amount) + Left*(printed_wall_thickness + 0.7)
       for amount in subdivisions (-0.25, 1.2, amount=5)]
  + [Between(c, d, amount)
       for amount in subdivisions (-0.3, 1.35, amount=3)]
)

@run_if_changed
def make_wall_curve():
  wall_curve = BSplineCurve (wall_curve_points, BSplineDimension (periodic = True))
  save ("wall_curve", wall_curve)
wall_curve_length = wall_curve.length()
ankle_start_distance = wall_curve.distance (closest =a) - 4
ankle_finish_distance = wall_curve.distance (closest =b) + 5
control_board_outside_distance = wall_curve.distance (closest =d)

#perforated_length = ankle_start_distance - ankle_finish_distance
#num_perforated_columns = round (perforated_length/porthole_width)
#porthole_exact_width = perforated_length/num_perforated_columns

#print (ankle_start_distance, ankle_finish_distance, wall_curve_length, perforated_length)

def natural_column (start_distance, finish_distance):
  start_distance -= 0.05
  finish_distance += 0.05
  start = wall_curve.derivatives (distance = start_distance)
  finish = wall_curve.derivatives (distance = finish_distance)
  inside_wire = Edge (wall_curve).offset2D (- printed_wall_thickness)
  return Face (Wire (
    TrimmedCurve (wall_curve, start.parameter, finish.parameter),
    finish.position + finish.normal*5,
    start.position + start.normal*5,
    loop = True,
  )).cut (Face (inside_wire)).extrude (Up*controller_length)

def perforated_column (start_distance, finish_distance, parity):
  start_distance -= 0.05
  finish_distance += 0.05
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
    offset_surface = BSplineSurface([[p + (surface.normal(closest=p)*1).projected_perpendicular (Up).normalized()*printed_wall_thickness for p in row] for row in rows])
    joiner = Loft(Face(surface).outer_wire(), Face(offset_surface).outer_wire())
    result.append (Solid(Shell(Face(surface).complemented(), Face(offset_surface), joiner.complemented().faces())))
  return result

@run_if_changed
def make_perforated_columns ():
  a = control_board_outside_distance - 3
  b = control_board_outside_distance + 3
  perforated_columns = [
    perforated_column (*pair, index % 2)
    for index, pair in enumerate (pairs (subdivisions (ankle_finish_distance, a, max_length = porthole_width)))
  ] + [
    perforated_column (*pair, (index + 1) % 2)
    for index, pair in enumerate (pairs (subdivisions (b, ankle_start_distance, max_length = porthole_width)))
  ] + [
    natural_column (a, b),
    natural_column (ankle_start_distance, ankle_finish_distance),
  ]
  save ("perforated_columns", perforated_columns)
  

@run_if_changed
def make_board_slots():
  bounding_solid = Face (Wire(wall_curve).offset2D(-printed_wall_thickness*0.9)).extrude (Up*controller_length)
  
  def board_slot(width, thickness, back):
    c = contact_leeway
    k = contact_leeway + printed_wall_thickness
    slot_cut_width = c + width + c
    block    = Vertex (0, back + k, 0).extrude (Front*(k + thickness + k)).extrude (Left*(k + width + k), centered = True).extrude (Up*controller_length)
    slot_cut = Vertex (0, back + c, 0).extrude (Front*(c + thickness + c)).extrude (Left*slot_cut_width, centered = True).extrude (Up*lots, centered = True)
    face_cut = Vertex (0, back, 0).extrude (Front*lots, centered = True).extrude (Left*(slot_cut_width - 2*slot_depth), centered = True).extrude (Up*lots, centered = True)
    strut    = Vertex (0, back - thickness/2, 0).extrude (Front*printed_wall_thickness, centered = True).extrude (Left*lots, centered = True).extrude (Up*controller_length)
    
    return Compound (block.cut ([slot_cut, face_cut]), strut.cut (slot_cut)).intersection (bounding_solid)
  
  controller_slot = board_slot (controller_width, controller_board_thickness, controller_back)
  sensor_slots = [board_slot (sensor_width, sensor_board_thickness, back) for back in sensor_backs]
  save ("board_slots", Compound (controller_slot, sensor_slots))
    
@run_if_changed
def make_base():
  solid = Face (wall_curve).extrude (Down*printed_wall_thickness)
  
  slot = Edge (
    Vertex (0, controller_back + 5, 0),
    Vertex (0, sensor_backs [-1] - 5, 0),
  ).extrude (Left*ports_slot_width, centered = True).extrude (Up*lots, centered = True)
  save ("base", solid.cut (slot))
  
@run_if_changed
def make_combined():
  combined = Compound (
    perforated_columns,
    board_slots,
    base,
  )
  save ("combined", combined)
  save_STL ("combined", combined)
  
preview (
  controller_board,
  sensor_boards,
  power_wire,
  ground_wire,
  signal_wires,
  wall_curve,
  combined
)

