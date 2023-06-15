import math

from pyocct_system import *
initialize_pyocct_system()


printed_wall_thickness = 0.8
contact_leeway = 0.4
lots = 500


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
porthole_depth = 4
porthole_width = 10
controller_slot_depth = 0.8
sensor_slot_depth = 1.4

controller_contact_inset = 1.2
controller_contact_spacing = 22.5/9

sensor_power_offset = Vector (0.0, 2.5, sensor_length + 3)

usb_plug_width = 15
usb_plug_thickness = 7.5
usb_plug_height = 15.5
usb_plug_pinch = 0.6
battery_holder_length = 75
battery_holder_inner_diameter = 25

ankle_offset = Vector(-62, -35, 0)
ankle_points = [Point(x,y,0)+ankle_offset for x,y in [(52, 0), (50, 5), (50, 15), (46, 28), (42, 34), (38, 37), (28, 40), (20, 40), (16, 43)]]
ankle_curve = BSplineCurve (ankle_points)
ankle_center = Point(16, 0)+ankle_offset
ankle_verticality_center = Point(33, 39)+ankle_offset
ankle_top_scale = 1.15
ankle_middle_inset = 2
#preview(ankle_curve, ankle_points, Interpolate (ankle_points), ankle_verticality_center)


def wallify(rows, thickness, *, loop):
  """
  Take rows, which define a BSplineSurface, where each row should be flat (compared with the build plate),
  and extrude that surface by `thickness` in the direction that is normal to the surface within the parallel-to-build-plate plane (note: the caller must be careful about positive versus negative)
  """
  surface = BSplineSurface(
    rows,
    v = BSplineDimension (periodic = loop)
  )
  other_rows = [
    [
      p + (surface.normal(closest=p)*1).projected_perpendicular (Up).normalized()*thickness
      for v,p in enumerate(row)
    ]
    for u,row in enumerate(rows)
  ]
  
  other_surface = BSplineSurface(
    other_rows,
    v = BSplineDimension (periodic = loop)
  )
  if loop:
    joiner = [
      Face(BSplineSurface([rows[0], other_rows[0]], BSplineDimension(degree=1), BSplineDimension (periodic = loop))),
      Face(BSplineSurface([rows[-1], other_rows[-1]], BSplineDimension(degree=1), BSplineDimension (periodic = loop))),
    ]
  else:
    joiner = Loft(Face(surface).outer_wire(), Face(other_surface).outer_wire()).faces()
  #preview(surface, other_surface, joiner)
  wall = Solid(Shell(Face(surface).complemented(), Face(other_surface), joiner))
  return wall


ankle_slant = -((ankle_verticality_center-ankle_center)*(ankle_top_scale - 1)) / battery_holder_length
def ankle_row(height, scale):
  return [ankle_center + (p - ankle_center)*scale + Up*height + ankle_slant*height for p in ankle_points]

ankle_middle_scale = (Between(1, ankle_top_scale, fraction=0.5)) - ankle_middle_inset / (ankle_verticality_center - ankle_center).magnitude()
print(f"middle scale: {ankle_middle_scale}")
ankle_rows = [
  ankle_row(-printed_wall_thickness, 1.04),
  ankle_row(6, 1),
  ankle_row(Between(0, battery_holder_length, fraction=0.25), Between(1, ankle_middle_scale, fraction=0.6)),
  ankle_row(Between(0, battery_holder_length, fraction=0.5), ankle_middle_scale),
  ankle_row(Between(0, battery_holder_length, fraction=0.75), Between(ankle_middle_scale, ankle_top_scale, fraction=0.4)),
  ankle_row(battery_holder_length-6, ankle_top_scale),
  ankle_row(battery_holder_length, ankle_top_scale+0.04),
]

@run_if_changed
def ankle_wall():
  ankle_wall = wallify(ankle_rows, printed_wall_thickness, loop = False)
  save_STL ("ankle_wall", ankle_wall)
  return ankle_wall
@run_if_changed
def ankle_exclusion():
  return Face (BSplineSurface(ankle_rows)).extrude (vector(-lots,-lots,0))@Scale(1.001)
#preview(ankle_wall, ankle_exclusion)
    
battery_transformation = Rotate(axis=Up, degrees = 135)@Translate (vector (-23, 16.5))
boards_transformation = Rotate(axis=Up, degrees = 9)@Translate (vector (-3.3,3.5))

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
def wall_curve():
  return BSplineCurve (wall_curve_points, BSplineDimension (periodic = True))
wall_curve_length = wall_curve.length()
ankle_start_distance = wall_curve.distance (closest =a) - 14
ankle_finish_distance = wall_curve.distance (closest =b) + 5
control_board_outside_distance = wall_curve.distance (closest =d)

#preview(wall_curve, wall_curve_points)

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
    result.append (wallify(rows, printed_wall_thickness, loop = False))
  return result

@run_if_changed
def perforated_columns ():
  a = control_board_outside_distance - 3
  b = control_board_outside_distance + 3
  return [
    perforated_column (*pair, index % 2)
    for index, pair in enumerate (pairs (subdivisions (ankle_finish_distance, a, max_length = porthole_width)))
  ] + [
    perforated_column (*pair, (index + 1) % 2)
    for index, pair in enumerate (pairs (subdivisions (b, ankle_start_distance, max_length = porthole_width)))
  ] + [
    natural_column (a, b),
  ]

@run_if_changed
def ankle_column ():
  return natural_column (ankle_start_distance, ankle_finish_distance)
  

@run_if_changed
def board_slots():
  bounding_solid = Face (Wire(wall_curve).offset2D(-printed_wall_thickness*0.9)).extrude (Up*controller_length)
  
  def board_slot(width, thickness, back, slot_depth):
    c = contact_leeway
    k = contact_leeway + printed_wall_thickness
    slot_cut_width = c + width + c
    block    = Vertex (0, back + k, 0).extrude (Front*(k + thickness + k)).extrude (Left*(k + width + k), centered = True).extrude (Up*controller_length)
    slot_cut = Vertex (0, back + c, 0).extrude (Front*(c + thickness + c)).extrude (Left*slot_cut_width, centered = True).extrude (Up*lots, centered = True)
    face_cut = Vertex (0, back, 0).extrude (Front*lots, centered = True).extrude (Left*(slot_cut_width - 2*slot_depth), centered = True).extrude (Up*lots, centered = True)
    strut    = Vertex (0, back - thickness/2, 0).extrude (Front*printed_wall_thickness, centered = True).extrude (Left*lots, centered = True).extrude (Up*controller_length).cut(ankle_exclusion @ boards_transformation.inverse())
    
    return Compound (block.cut ([slot_cut, face_cut]), strut.cut (slot_cut)).intersection (bounding_solid)
  
  controller_slot = board_slot (controller_width, controller_board_thickness, controller_back, controller_slot_depth)
  sensor_slots = [board_slot (sensor_width, sensor_board_thickness, back, sensor_slot_depth) for back in sensor_backs]
  return Compound (controller_slot, sensor_slots)
    
@run_if_changed
def base():
  solid = Face (wall_curve).extrude (Down*printed_wall_thickness)
  
  slot = Edge (
    Vertex (0, controller_back + 5, 0),
    Vertex (0, sensor_backs [-1] - 5, 0),
  ).extrude (Left*ports_slot_width, centered = True).extrude (Up*lots, centered = True)
  return solid.cut (slot).cut(ankle_exclusion @ boards_transformation.inverse())

usb_holder_wall, usb_holder_cut = None, None
@run_if_changed
def make_usb_holder():
  def row(height, pinch):
    w = usb_plug_width + contact_leeway*2
    t = usb_plug_thickness + 0.1*2 + contact_leeway*2
    h = height
    return [
      Point(w/2, -t/3, h),
      Point(w/2,   0, h),
      Point(w/2, t/3, h),
      Point(w/3, t/2, h),
      Point(  0, t/2 - pinch*3, h),
      Point(-w/3, t/2, h),
      Point(-w/2, t/3, h),
      Point(-w/2,   0, h),
      Point(-w/2, -t/3, h),
      Point(-w/3, -t/2, h),
      Point(  0, -t/2 + pinch*3, h),
      Point(w/3, -t/2, h),
    ][::-1]
  rows = [
    row(0, 0),
    row(usb_plug_height*1/4, 0),
    row(usb_plug_height*2/4, usb_plug_pinch),
    row(usb_plug_height*3/4, 0),
    row(usb_plug_height*4/4, 0),
  ]
  #.extrude (Down*printed_wall_thickness)
  
  offset = vector(0, -2.5, 0)

  global usb_holder_wall, usb_holder_cut
  usb_holder_wall = wallify(rows, printed_wall_thickness, loop = True) @ Translate(offset)
  preview(usb_holder_wall)
  usb_holder_cut = Compound(
    Face(BSplineCurve(rows[0], BSplineDimension (periodic = True))).extrude(Up*lots),
    Face(BSplineCurve([Point(p[0]*0.8, p[1]) for p in rows[0]], BSplineDimension (periodic = True))).extrude(Up*lots, centered=True)
  ) @ Translate(offset)
  save_STL ("usb_holder_wall", usb_holder_wall)

battery_holder_inner_solid, battery_holder_wall = None, None
@run_if_changed
def make_battery_holder():
  global battery_holder_inner_solid, battery_holder_wall
  battery_holder_outer_diameter = battery_holder_inner_diameter + printed_wall_thickness*2
  battery_holder_outer_solid = Face (Circle (Axes(Origin, Up), battery_holder_outer_diameter/2)).extrude (Up*battery_holder_length)
  battery_holder_inner_solid = Face (Circle (Axes(Origin, Up), battery_holder_inner_diameter/2)).extrude (Up*lots, centered=True)
  battery_holder_wall = battery_holder_outer_solid.cut(battery_holder_inner_solid)
  battery_holder_strut = Vertex(0,0,0).extrude(Left*printed_wall_thickness, centered=True).extrude(Down*printed_wall_thickness, Up*battery_holder_length).extrude(Back*(battery_holder_outer_diameter/2+10)).cut(battery_holder_inner_solid).cut(ankle_exclusion @ battery_transformation.inverse())
  
  #cr = 16
  #battery_holder_window_cut = Face (Circle (Axes(Point(0, -cr-3, battery_holder_length*0.6), Right), cr)).extrude (Right*lots, centered=True) @ Rotate(Up, degrees=35)
  #battery_holder_wall = battery_holder_wall.cut(battery_holder_window_cut)
   
  cr = 22
  close_points = []
  far_points = []
  for h in subdivisions(-cr, cr, amount=50):
    w = math.cos(h/cr * math.pi/2)*cr/(math.pi/2)
    radians = w / (battery_holder_outer_diameter/2)
    t = math.tan(radians)
    close_points.append (Point(1, t, h))
    f = battery_holder_outer_diameter
    far_points.append (Point(f, t*f, h))
  half_cut = Face(BSplineSurface([close_points, far_points], BSplineDimension(degree = 1)))
  half_close = Edge(BSplineCurve(close_points))
  half_far = Edge(BSplineCurve(far_points))
  close_face = Face(Wire(half_close, half_close @ Rotate(Left, degrees=180)))
  far_face = Face(Wire(half_far, half_far @ Rotate(Left, degrees=180)))
  #preview(half_cut, half_cut @ Rotate(Left, degrees=180), close_face, far_face)
  battery_holder_window_cut = Solid(Shell(half_cut, half_cut @ Rotate(Left, degrees=180), close_face, far_face).complemented())
  battery_holder_window_cut = battery_holder_window_cut @ Translate(Up*battery_holder_length*0.6)@ Rotate(Up, degrees=-45)
  
  #preview(battery_holder_window_cut)
  battery_holder_wall = battery_holder_wall.cut(battery_holder_window_cut)
    
  
  battery_holder_base = Compound(
    Face (Circle (Axes(Origin, Up), battery_holder_outer_diameter/2)).extrude (Down*printed_wall_thickness),
    Intersection(
      Vertex(0,-2.5,0).extrude(Front*printed_wall_thickness, centered=True).extrude(Left*lots, centered=True).extrude(Up*usb_plug_height),
      battery_holder_inner_solid,
    )
  )
    
  battery_holder_base = battery_holder_base.cut (usb_holder_cut)
  
  #preview(usb_holder_wall, battery_holder_wall, battery_holder_base)
  battery_holder_wall = Compound(battery_holder_wall, battery_holder_strut, battery_holder_base)

@run_if_changed
def combined_boards_holder():
  combined_boards_holder = Compound (
    perforated_columns,
    ankle_column.cut(ankle_exclusion @ boards_transformation.inverse()).cut(battery_holder_inner_solid @ battery_transformation @ boards_transformation.inverse()),
    board_slots,
    base,
  )
  save_STL ("combined_boards_holder", combined_boards_holder)
  return combined_boards_holder
  
@run_if_changed
def everything_placed():
  boards_holder_placed = combined_boards_holder@boards_transformation
  battery_placed = Compound(usb_holder_wall, battery_holder_wall)@battery_transformation
  everything_placed = Compound(ankle_wall, boards_holder_placed, battery_placed)
  save_STL("everything_placed", everything_placed)
  return everything_placed


preview (
  Compound(
    controller_board,
    sensor_boards,
    power_wire,
    ground_wire,
    signal_wires,
    Edge(wall_curve),
  )@boards_transformation,
  everything_placed,
)

