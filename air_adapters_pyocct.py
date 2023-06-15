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
  preview(solid)
  
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
  
  preview(solid)

  
@run_if_changed
def make_flat_wall_to_cpaps():
  wall_thickness = 0.8
  plate_thickness = 1.2
  flat_wall_thickness = 3 # approximate - cardboard thicker than this can be jammed in, sheets thinner than this can be padded with hot glue
  CPAP_inner_radius = CPAP_outer_radius - wall_thickness
  CPAP_smooth_length = 22
  CPAP_diagonal_length = plate_thickness*2 + flat_wall_thickness + 3
  CPAP_diagonal_spread = 3
  
  oa = Point(CPAP_outer_radius + CPAP_diagonal_spread, 0, 0)
  ob = Point(CPAP_outer_radius, 0, CPAP_diagonal_length)
  oc = Point(CPAP_outer_radius, 0, CPAP_diagonal_length+CPAP_smooth_length)
  od = Point(0, 0, CPAP_diagonal_length+CPAP_smooth_length)
  oe = Origin
  outer_wire = Wire(Edge(BSplineCurve(
    [oa, Between(oa, ob), ob, Between(ob, oc, 0.2), oc]
  )), od, oe, loop=True)
  ia = oa + Left*wall_thickness + Down*0.001
  ib = ob + Left*wall_thickness
  ic = oc + Left*wall_thickness + Up*0.001
  id = od + Up*0.001
  ie = oe + Down*0.001
  inner_wire = Wire(Edge(BSplineCurve(
    [ia, Between(ia, ib), ib, Between(ib, ic, 0.2), ic]
  )), id, ie, loop=True)
  outer_solid = Face(outer_wire).revolve(Axis(Origin, Up))
  inner_solid = Face(inner_wire).revolve(Axis(Origin, Up))
  cpap = outer_solid.cut(inner_solid)
  
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
    inner_solid @ Translate(Left*(cpap_separation/2)),
    inner_solid @ Translate(Right*(cpap_separation/2)),
    )
  
  adapter = Compound(
    cpap @ Translate(Left*(cpap_separation/2)),
    cpap @ Translate(Right*(cpap_separation/2)),
    plate.cut(cuts),
    cross_plate.cut(cuts),
    block.cut(cuts),
    )

  save_STL ("flat_wall_to_cpaps", adapter)
  
  preview(adapter)