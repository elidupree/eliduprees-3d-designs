import math

from pyocct_system import *
initialize_system (globals())

from air_adapters import elidupree_4in_threshold, elidupree_4in_leeway_one_sided, elidupree_4in_intake_inner_radius, elidupree_4in_output_outer_radius


  
strong_filter_length = 151.9
strong_filter_width = 101



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
  save ("hepa_to_4in", solid)
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
  
  save ("hepa_to_nothing", solid)
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
  
  save ("hepa_to_nothing_clips", solid)
  save_STL ("hepa_to_nothing_clips", solid)
  

preview(hepa_to_nothing_clips)
