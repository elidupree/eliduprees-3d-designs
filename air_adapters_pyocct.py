import math

from pyocct_system import *
initialize_pyocct_system()

from air_adapters import elidupree_4in_threshold, elidupree_4in_leeway_one_sided, elidupree_4in_intake_inner_radius, elidupree_4in_output_outer_radius


  
strong_filter_length = 151.9
strong_filter_width = 101
CPAP_outer_radius = 21.5/2



def elidupree_4in_wire(offset):
  return Wire (Edge (Circle (Axes (Point (0,0,80) + Up*offset, Up), elidupree_4in_output_outer_radius)))

def strong_filter_wire(outset):
  
  length = strong_filter_length/2 + outset
  width = strong_filter_width/2 + outset
  return Wire(
    Point (-length, -width, 0),
    Point (length, -width, 0),
    Point (length, width, 0),
    Point (-length, width, 0),
    loop = True,
  )


@run_if_changed
def make_hepa_to_4in():
  wall_thickness = 0.5
  sections = (
    [strong_filter_wire(wall_thickness - offset*0.14)@Translate(Up*offset) for offset in subdivisions(-2, 8, amount = 5)]
    + [elidupree_4in_wire(offset) for offset in subdivisions(-20, 0, amount = 5)]
  )
  solid = Loft(sections, solid=True)
  save_STL("hepa_to_4in", solid)
  
  
@run_if_changed
def make_hepa_to_nothing():
  return
  wall_thickness = 0.6
  plate_thickness = 3
  sections = [
    strong_filter_wire(wall_thickness + 5*0.14)@Translate(Up*5),
    strong_filter_wire(wall_thickness),
    strong_filter_wire(-5),
  ]
  loft = Loft(sections[0:2], ruled = True)
  '''
  faces = loft.faces() + [
    Face (sections [1], holes = sections [2].complemented()),
  ]
  pointy_shell = Shell (faces)
  shell = pointy_shell
  '''
  '''Fillet(pointy_shell, [(edge, 1.0 + wall_thickness) for edge in 
    sections [1].edges() + [edge for edge in loft.edges() if not all_equal (vertex [2] for vertex in edge.vertices())]
  ])'''
  #preview (shell)
  #preview (Offset (shell, -wall_thickness, fill = False))
  #solid = Offset (shell, -wall_thickness, fill = True)
  
  wall = Offset (Shell(loft.faces()), wall_thickness, fill = True)
  plate_top = Face (sections [1], holes = sections [2].complemented())
  plate = plate_top.extrude(Up*0.1, Down*plate_thickness)
  
  peg_width = 5
  peg_length = 15
  peg_thickness = 4
  peg = Vertex(Origin).extrude(Right*peg_length).extrude(Up*peg_thickness).extrude(Back*peg_width, centered=True) @ Translate(Down*plate_thickness)
  center_peg = peg @ Translate(Right*(strong_filter_length/2 + wall_thickness))
  corner_peg = center_peg @ Translate(Front*(strong_filter_width/2 + wall_thickness - peg_width / 2))
  right_pegs = Compound(center_peg, corner_peg, corner_peg @ Mirror(Back))
  
  solid = Compound(wall, plate, right_pegs, right_pegs@Mirror(Left))

  save_STL("hepa_to_nothing", solid)
  # preview(solid)
  
@run_if_changed
def make_hepa_to_nothing_clips():
  wall_thickness = 1.5
  inset = 5.5
  wall_radius = wall_thickness/2
  gripped_thickness = 19.0
  gripped_thickness_to_line = gripped_thickness + wall_thickness
  
  c = Origin
  b = c + Right*(7 + wall_thickness)
  a = b + Back*1.5
  
  d = c + Back*(5+wall_thickness)
  e = d + Back*((gripped_thickness_to_line + 1) - (5+wall_thickness)) + Right*1.7
  f = e + Right*inset + Front*1
  g = e + Back*inset
  h = g + Left*4
  
  wire = Wire([a,b,c,d,e,f,g,h])
  solid = Face (wire.offset2D (wall_radius)).extrude (Up*6)
  
  '''
  a = Origin
  b = a + Right*7
  c = b + Back*3
  d = c + Right*wall_thickness
  e = d + Front*(3+wall_thickness)
  
  f = e + Left*(7+wall_thickness)
  g = f + Back*(gripped_thickness + wall_thickness*2 + inset)
  h = g + Right*wall_thickness
  
  k = a + Back*gripped_thickness
  j = k + Right*inset
  i = j + Back*wall_thickness
  
  wire = Wire([a,b,c,d,e,f,g,h,i,j,k],loop=True)
  preview(wire)
  
  solid = Face(wire).extrude(Up*10)'''

  save_STL ("hepa_to_nothing_clips", solid)
  
  # preview(solid)



class CircleSizing:
  def __init__(self, id=None, od=None, wall_thickness=1.2):
    if id is None:
      id = od - wall_thickness*2
    if od is None:
      od = id + wall_thickness*2
    self.id = id
    self.od = od

  def __add__(self, other):
    return self.__class__(self.id+other.id, self.od+other.od)
  def __sub__(self, other):
    return self.__class__(self.id-other.id, self.od-other.od)
  def __mul__(self, other):
    return self.__class__(self.id*other, self.od*other)

  def wires(self, axes):
    return [Wire(Circle(axes, self.id/2)), Wire(Circle(axes, self.od/2))]
  def face(self, axes):
    w = self.wires(axes)
    return Face(w[1], holes=[w[0].reversed()])

class Taper:
  def __init__(self, opening: CircleSizing, connected_end: CircleSizing, length):
    self.opening = opening
    self.connected_end = connected_end
    self.length = length

  def inner_solid(self, exiting_direction, opening_center=None, connected_end_center=None):
    # TODO reduce duplicate code ID 1728406
    if opening_center is None:
      opening_center = connected_end_center + exiting_direction*self.length
    if connected_end_center is None:
      connected_end_center = opening_center - exiting_direction*self.length

    wires = [
      self.opening.wires(Axes(opening_center, exiting_direction))[0],
      self.connected_end.wires(Axes(connected_end_center, exiting_direction))[0],
    ]
    return Loft(wires[0], wires[1], solid=True, ruled=True)

  def solid(self, exiting_direction, opening_center=None, connected_end_center=None):
    # TODO reduce duplicate code ID 1728406
    if opening_center is None:
      opening_center = connected_end_center + exiting_direction*self.length
    if connected_end_center is None:
      connected_end_center = opening_center - exiting_direction*self.length

    wires = list(zip(
      self.opening.wires(Axes(opening_center, exiting_direction)),
      self.connected_end.wires(Axes(connected_end_center, exiting_direction)),
    ))

    faces = [
      Loft(wires[0][0], wires[0][1], ruled=True).faces(),
      Face(wires[1][1], holes=[wires[0][1].reversed()]),
      Loft(wires[1][1], wires[1][0], ruled=True).faces(),
      Face(wires[1][0], holes=[wires[0][0].reversed()]),
    ]
    # preview(faces)

    return Shell(faces)
    return Solid(Shell(faces))


def round_adapter(tapers, joiner_length=None, joiner_radius=None):
  result = [tapers[0].solid(Down, connected_end_center=Origin)]
  base = Origin
  basedir = Up
  if joiner_length is not None:
    face = tapers[0].connected_end.face(Axes(Origin, Up))
    if joiner_radius is None:
      # result.append(face.extrude(Up*joiner_length))
      raise RuntimeError("oops didn't implement this right, it needs to be another taper")
      base = base + Up*joiner_length
    else:
      hoops = []
      axis = Axis(Origin+Right*joiner_radius, Back)
      # angle = Radians(joiner_length/joiner_radius)
      for x in subdivisions(0,1,amount=8):
        angle = Radians(x*joiner_length/joiner_radius)
        b2 = base @ Rotate(axis, angle)
        b2dir = Up @ Rotate(axis, angle)
        hoops.append(Between(tapers[0].connected_end, tapers[1].connected_end, x).wires(Axes(b2, b2dir)))
      base = base @ Rotate(axis, angle)
      basedir = Up @ Rotate(axis, angle)
      result.append(Loft([h[1] for h in hoops], solid=True).cut(Loft([h[0] for h in hoops], solid=True)))

  result.append(tapers[1].solid(basedir, connected_end_center=base))
  return Compound(result)

@run_if_changed
def make_sander_dustport_to_shopvac1_adapter():
  result = round_adapter([
    Taper(opening=CircleSizing(id=31.5, wall_thickness=2), connected_end=CircleSizing(id=30.1, wall_thickness=2), length=30),
    Taper(opening=CircleSizing(id=38.7, wall_thickness=2), connected_end=CircleSizing(id=38.3, wall_thickness=2), length=35)],
    joiner_length=50,
    joiner_radius = 100
  )
  # preview(result)
  save_STL("sander_dustport_to_shopvac1_adapter", result)
  # export("sander_dustport_to_shopvac1_adapter.stl", "sander_dustport_to_shopvac1_adapter_1.stl")



@run_if_changed
def make_flat_wall_to_cpaps():
  wall_thickness = 1.0
  plate_thickness = 1.2
  flat_wall_thickness = 3 # approximate - cardboard thicker than this can be jammed in, sheets thinner than this can be padded with hot glue
  # CPAP_inner_radius = CPAP_outer_radius - wall_thickness
  CPAP_smooth_length = 22
  CPAP_diagonal_length = plate_thickness*2 + flat_wall_thickness + 3
  CPAP_diagonal_spread = 3

  CPAP_tapers = [
      Taper(opening=CircleSizing(od = 2*CPAP_outer_radius + 2*CPAP_diagonal_spread, wall_thickness=2), connected_end=CircleSizing(od = 2*CPAP_outer_radius, wall_thickness=wall_thickness), length=CPAP_diagonal_length),
      Taper(opening=CircleSizing(od=2*CPAP_outer_radius, wall_thickness=wall_thickness), connected_end=CircleSizing(od=2*CPAP_outer_radius, wall_thickness=wall_thickness), length=CPAP_smooth_length),
  ]
  rot = Rotate(Up, Degrees(90)) @ Translate(Up*CPAP_diagonal_length)
  CPAP_walls = round_adapter(CPAP_tapers,
    joiner_length = 16,
    joiner_radius = 18
  ) @ rot
  CPAP_inner_solid = CPAP_tapers[0].inner_solid(Down, connected_end_center=Origin) @ rot
  # o0 = Point(CPAP_outer_radius + CPAP_diagonal_spread, 0, -CPAP_diagonal_length)
  # oa = Point(CPAP_outer_radius + CPAP_diagonal_spread, 0, 0)
  # ob = Point(CPAP_outer_radius, 0, CPAP_diagonal_length)
  # oc = Point(CPAP_outer_radius, 0, CPAP_diagonal_length+CPAP_smooth_length)
  # od = Point(0, 0, CPAP_diagonal_length+CPAP_smooth_length)
  # oe = Origin
  # outer_wire = Wire(Edge(BSplineCurve(
  #   [o0, oa, Between(oa, ob), ob, Between(ob, oc, 0.2), oc]
  # )), od, oe, loop=True)
  # ia = oa + Left*wall_thickness + Down*0.001
  # ib = ob + Left*wall_thickness
  # ic = oc + Left*wall_thickness + Up*0.001
  # id = od + Up*0.001
  # ie = oe + Down*0.001
  # inner_wire = Wire(Edge(BSplineCurve(
  #   [ia, Between(ia, ib), ib, Between(ib, ic, 0.2), ic]
  # )), id, ie, loop=True)
  # rot = Translate(Up*4) @ Rotate(Left, Degrees(20))
  # outer_solid = Face(outer_wire).revolve(Axis(Origin, Up)) @ rot
  # inner_solid = Face(inner_wire).revolve(Axis(Origin, Up)) @ rot
  # cpap = outer_solid.cut(inner_solid)

  cpap_separation = 32
  cpap_total_width = CPAP_outer_radius*2 + CPAP_diagonal_spread*2
  cpap_total_length = cpap_total_width + cpap_separation

  plate_glue_tab_length = 8
  plate_length = cpap_total_length + plate_glue_tab_length * 4
  cross_plate_width = cpap_total_width + plate_glue_tab_length * 2

  plate = Vertex(Origin).extrude(Left*plate_length, centered = True).extrude (Back*cpap_total_width, centered = True).extrude (Up*plate_thickness)
  cross_plate = Vertex(Origin).extrude(Left*cpap_total_length, centered = True).extrude (Back*cross_plate_width, centered = True).extrude (Up*plate_thickness) @ Translate(Up*(plate_thickness+ flat_wall_thickness))

  block = Vertex(Origin).extrude(Left*cpap_total_length, centered = True).extrude (Back*cpap_total_width, centered = True).extrude (Up*(plate_thickness*2 + flat_wall_thickness))

  cuts = Compound(
    CPAP_inner_solid @ Translate(Left*(cpap_separation/2)),
    CPAP_inner_solid @ Translate(Right*(cpap_separation/2)),
    )
  # preview(plate, CPAP_inner_solid)

  adapter = Compound(
    CPAP_walls @ Translate(Left*(cpap_separation/2)),
    CPAP_walls @ Translate(Right*(cpap_separation/2)),
    plate.cut(cuts),
    cross_plate.cut(cuts),
    block.cut(cuts),
    )

  save_STL ("flat_wall_to_cpaps", adapter)
  export("flat_wall_to_cpaps.stl", "flat_wall_to_cpaps_2.stl")

  preview(adapter)