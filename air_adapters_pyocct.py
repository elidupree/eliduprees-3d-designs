import math

from pyocct_system import *
initialize_system (globals())

from air_adapters import elidupree_4in_threshold, elidupree_4in_leeway_one_sided, elidupree_4in_intake_inner_radius, elidupree_4in_output_outer_radius


  
strong_filter_length = 151.9
strong_filter_width = 101



def elidupree_4in_wire(offset):
  return Wire (Edge (Circle (Axes (Point (0,0,80) + Up*offset, Up), elidupree_4in_output_outer_radius)))

def strong_filter_wire(offset, outset):
  
  length = strong_filter_length/2 + outset - offset*0.14
  width = strong_filter_width/2 + outset - offset*0.14
  return Wire(
    Point (-length, -width, 0),
    Point (length, -width, 0),
    Point (length, width, 0),
    Point (-length, width, 0),
    loop = True,
  )@Translate(Up*offset)


@run_if_changed
def make_hepa_to_4in():
  wall_thickness = 0.5
  sections = (
    [strong_filter_wire(offset, wall_thickness) for offset in subdivisions(-2, 8, amount = 5)]
    + [elidupree_4in_wire(offset) for offset in subdivisions(-20, 0, amount = 5)]
  )
  solid = Loft(sections, solid=True)
  save ("hepa_to_4in", solid)
  save_STL("hepa_to_4in", solid)
  
  
@run_if_changed
def make_hepa_to_nothing():
  wall_thickness = 1.0
  sections = [
    strong_filter_wire(-5, wall_thickness),
    strong_filter_wire(0, wall_thickness),
    strong_filter_wire(0, -5),
  ]
  loft = Loft(sections[0:2], ruled = True)
  faces = loft.faces() + [
    Face (sections [1], holes = sections [2].complemented()),
  ]
  pointy_shell = Shell (faces)
  shell = pointy_shell
  '''Fillet(pointy_shell, [(edge, 1.0 + wall_thickness) for edge in 
    sections [1].edges() + [edge for edge in loft.edges() if not all_equal (vertex [2] for vertex in edge.vertices())]
  ])'''
  preview (shell)
  preview (Offset (shell, -wall_thickness, fill = False))
  solid = Offset (shell, -wall_thickness, fill = True)
  save ("hepa_to_nothing", solid)
  save_STL("hepa_to_nothing", solid)
    

preview(hepa_to_nothing)
