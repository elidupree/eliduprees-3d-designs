'''FREECADPATH = r"C:\Program Files\FreeCAD 0.18\bin"

import sys
sys.path.append(FREECADPATH)
 
import FreeCAD
       
       
import FreeCADGui 

FreeCADGui.showMainWindow()
import time
time.sleep(5)'''

import PartDesignGui
import importlib
import shape_builder
importlib.reload(shape_builder)
from shape_builder import *

FreeCAD = App
def document():
  return App.activeDocument()
def vector(*arguments):
  return FreeCAD.Vector (*arguments)

for document_name in list(FreeCAD.listDocuments().keys()):
  FreeCAD.closeDocument (document_name)
#Gui.activateWorkbench("PartWorkbench")

App.newDocument("Something")
#App.setActiveDocument("Something")

layer_height = 0.12
band_width = 6
band_thickness = 1
band_leeway = 1
flex_perpendicular_leeway = 3
claw_length = band_width + 2
claw_deflect_distance = claw_length + 1
claw_arm_length = 40
claw_solid_length = 18
flex_length = 12
flex_thickness = 1
flex_support_length = 6
claw_thickness = 2.5
claw_width = 6
motion_distance = 100
channel_depth = 6
slider_channel_tolerance = 0.4
channel_wall_thickness = 3
channel_stop_thickness = 0.5
deflector_peg_diameter = 3
deflector_peg_length = 2
deflector_thickness = 1
deflector_slope = 0.2
releaser_slope = 0.6
releaser_extra_length = 5

deflector_peg_radius = deflector_peg_diameter/2
deflector_radius = deflector_thickness/2

claw_right = 0
claw_left = claw_right - claw_thickness
slider_left = claw_left - flex_perpendicular_leeway/2
deflector_peg_left = claw_left
deflector_peg_right = deflector_peg_left + deflector_peg_diameter
claw_solid_right = claw_left + claw_solid_length
flex_right = claw_right + claw_arm_length
flex_left = flex_right - flex_length
flex_support_right = flex_right + flex_support_length

flex_top = 0
claw_top = flex_top + claw_length
flex_bottom = flex_top - flex_thickness
claw_solid_bottom = flex_top - claw_thickness
deflector_top_center = flex_top - deflector_radius
deflector_fully_down_center = deflector_top_center - claw_deflect_distance
deflector_peg_bottom = flex_top - deflector_thickness - deflector_peg_diameter - slider_channel_tolerance
slider_top = deflector_peg_bottom - claw_deflect_distance - slider_channel_tolerance
slider_bottom = slider_top - channel_depth
channel_floor_bottom = slider_bottom - channel_wall_thickness
slider_vertical_middle = (slider_top + slider_bottom)/2
deflector_peg_horizontal_middle = claw_left + deflector_peg_radius
deflector_peg_vertical_middle = deflector_peg_bottom + deflector_peg_radius

claw_front = - claw_width/2
claw_back = claw_front + claw_width
slider_protrusions_front = claw_front - deflector_peg_length
slider_protrusions_back = claw_back + deflector_peg_length


channel_left_stop = slider_left
channel_right_stop = flex_support_right + motion_distance
deflector_left_end = deflector_peg_right + flex_perpendicular_leeway/2
deflector_left_end_center = deflector_left_end + deflector_radius
deflector_fully_down_horizontal = claw_right + band_thickness*2 + band_leeway*2 + (deflector_peg_horizontal_middle - claw_left)
deflector_right_end_center = deflector_fully_down_horizontal + claw_deflect_distance/deflector_slope
releaser_fully_down_horizontal = deflector_peg_horizontal_middle + motion_distance
releaser_left_end_center = releaser_fully_down_horizontal - claw_deflect_distance/releaser_slope
releaser_right_end_center = releaser_fully_down_horizontal + releaser_extra_length

slider_shape = FreeCAD_shape_builder (lambda whatever: whatever + vector (0, 0, claw_front)).build ([
  start_at (flex_support_right, slider_bottom),
  horizontal_to (slider_left), vertical_to (slider_top), horizontal_to (flex_right), vertical_to (flex_bottom), horizontal_to (flex_left), diagonal_to (claw_solid_right, claw_solid_bottom), horizontal_to (deflector_peg_right),
  
  #vertical_to (deflector_peg_bottom + deflector_peg_radius),
  #arc_through_to ((deflector_peg_horizontal_middle, deflector_peg_bottom), (deflector_peg_left, deflector_peg_bottom + deflector_peg_radius)),
  horizontal_to (deflector_peg_horizontal_middle),
  diagonal_to (claw_left, deflector_peg_bottom + deflector_peg_radius),
  
  vertical_to (claw_top), horizontal_to (claw_right), vertical_to (flex_top), horizontal_to (flex_support_right), close()
])

slider_main_part = Part.Face (Part.Wire (slider_shape.Edges)).extrude (FreeCAD.Vector (0, 0, claw_width))

slider_triangle_shape = FreeCAD_shape_builder (lambda whatever: vector (slider_left, whatever [1], whatever [0])).build ([
  start_at(claw_front, slider_top),
  horizontal_to (claw_back),
  diagonal_to (slider_protrusions_back, slider_vertical_middle),
  diagonal_to (claw_back, slider_bottom),
  horizontal_to (claw_front),
  diagonal_to (slider_protrusions_front, slider_vertical_middle),
  close(),
])

slider_triangle_part = Part.Face (Part.Wire (slider_triangle_shape.Edges)).extrude (FreeCAD.Vector (flex_support_right - slider_left, 0, 0))

deflector_peg_part = Part.makeCylinder (
  deflector_peg_radius, claw_width + deflector_peg_length*2,
  vector (deflector_peg_horizontal_middle, deflector_peg_vertical_middle, claw_front - deflector_peg_length),
  vector (0, 0, 1),
)

slider_part = slider_main_part.fuse ((slider_triangle_part, deflector_peg_part))
FreeCAD.Console.PrintMessage ([edge
  for edge in slider_part.Edges
  if FreeCAD.BoundBox (claw_right, flex_top, -100, claw_right, claw_top, 100).isInside (edge.BoundBox) or FreeCAD.BoundBox (flex_right, flex_bottom, -100, flex_right, flex_bottom, 100).isInside (edge.BoundBox)])
edges = [edge
  for edge in slider_part.Edges
  if #FreeCAD.BoundBox (claw_right, flex_top, -100, claw_right, claw_top, 100).isInside (edge.BoundBox)
  # or
   FreeCAD.BoundBox (flex_right, flex_bottom, -100, flex_right, flex_bottom, 100).isInside (edge.BoundBox)
  #and not
   or FreeCAD.BoundBox (claw_right, claw_top, -100, claw_right, claw_top, 100).isInside (edge.BoundBox)
   or FreeCAD.BoundBox (claw_right, flex_top, -100, claw_right, claw_top, 0).isInside (edge.BoundBox)
   or FreeCAD.BoundBox (claw_right, flex_top, 0, claw_right, claw_top, 100).isInside (edge.BoundBox)
   or FreeCAD.BoundBox (claw_left, claw_top, -100, claw_right, claw_top, 0).isInside (edge.BoundBox)
   or FreeCAD.BoundBox (claw_left, claw_top, 0, claw_right, claw_top, 100).isInside (edge.BoundBox)
   
  ]

slider_part = slider_part.makeFillet(1.5, edges) #[slider_part.Edges [index] for index in range (0, len (slider_part.Edges), 3)])

channel_box = Part.makeBox (
  channel_right_stop - channel_left_stop + channel_stop_thickness,
  flex_top - slider_bottom + channel_wall_thickness,
  slider_protrusions_back - slider_protrusions_front + channel_wall_thickness*2)
channel_box.translate (vector (
  channel_left_stop - channel_stop_thickness,
  slider_bottom - channel_wall_thickness,
  slider_protrusions_front - channel_wall_thickness))

wide_channel_shape = FreeCAD_shape_builder (lambda whatever: vector (channel_left_stop, whatever [1], whatever [0])).build ([
  start_at(claw_front, slider_top),
  horizontal_to (slider_protrusions_front),
  vertical_to (flex_top),
  horizontal_to (slider_protrusions_back),
  vertical_to (slider_top),
  horizontal_to (claw_back),
  diagonal_to (slider_protrusions_back, slider_vertical_middle),
  diagonal_to (claw_back, slider_bottom),
  horizontal_to (claw_front),
  diagonal_to (slider_protrusions_front, slider_vertical_middle),
  close(),
])
wide_channel_wire = Part.Wire (wide_channel_shape.Edges)
wide_channel_wire = wide_channel_wire.makeOffset2D (slider_channel_tolerance)
wide_channel_part = Part.Face (wide_channel_wire).extrude (FreeCAD.Vector (channel_right_stop - channel_left_stop, 0, 0))

narrow_channel_shape = FreeCAD_shape_builder (lambda whatever: vector (channel_left_stop, whatever [1], whatever [0])).build ([
  start_at(claw_front, slider_top),
  vertical_to (flex_top),
  horizontal_to (claw_back),
  vertical_to (slider_top),
  diagonal_to (slider_protrusions_back, slider_vertical_middle),
  diagonal_to (claw_back, slider_bottom),
  horizontal_to (claw_front),
  diagonal_to (slider_protrusions_front, slider_vertical_middle),
  close(),
])
narrow_channel_wire = Part.Wire (narrow_channel_shape.Edges)
narrow_channel_wire = narrow_channel_wire.makeOffset2D (slider_channel_tolerance)
narrow_channel_part = Part.Face (narrow_channel_wire).extrude (FreeCAD.Vector (channel_right_stop - channel_left_stop, 0, 0))

deflector_shape = FreeCAD_shape_builder (lambda whatever: whatever + vector (0, 0, slider_protrusions_front - channel_wall_thickness)).build ([
  start_at (deflector_left_end_center, deflector_fully_down_center),
  horizontal_to (deflector_fully_down_horizontal),
  diagonal_to (deflector_right_end_center, deflector_top_center),
])
deflector_wire = Part.Wire (deflector_shape.Edges).makeOffset2D (deflector_radius)
deflector_part = Part.Face (deflector_wire).extrude (FreeCAD.Vector (0, 0, slider_protrusions_back - slider_protrusions_front + channel_wall_thickness*2))

releaser_shape = FreeCAD_shape_builder (lambda whatever: whatever + vector (0, 0, slider_protrusions_front - channel_wall_thickness)).build ([
  start_at (releaser_right_end_center, deflector_fully_down_center),
  horizontal_to (releaser_fully_down_horizontal),
  diagonal_to (releaser_left_end_center, deflector_top_center),
])
releaser_wire = Part.Wire (releaser_shape.Edges).makeOffset2D (deflector_radius)
releaser_part = Part.Face (releaser_wire).extrude (FreeCAD.Vector (0, 0, slider_protrusions_back - slider_protrusions_front + channel_wall_thickness*2))


deflector_sacrificial_bridges_wire = Part.Wire (deflector_shape.Edges).makeOffset2D (layer_height/2)
releaser_sacrificial_bridges_wire = Part.Wire (releaser_shape.Edges).makeOffset2D (layer_height/2)

sacrificial_bridges_part = Part.Face (deflector_sacrificial_bridges_wire).fuse (Part.Face ( releaser_sacrificial_bridges_wire)).extrude (FreeCAD.Vector (0, 0, slider_protrusions_back - slider_protrusions_front + channel_wall_thickness*2))
sacrificial_bridges_part.translate (vector (0, - deflector_radius + layer_height/2, 0))

body_part = channel_box.cut(wide_channel_part).fuse ((deflector_part, releaser_part)).cut(narrow_channel_part).fuse (sacrificial_bridges_part)


Part.show (slider_part, "SliderSquare")

Part.show (body_part)

crop_box = Part.makeBox (5, 100, 100)
crop_box.translate (vector (5, -50, -50))
Part.show (body_part.common(crop_box))



document().recompute()
#Gui.SendMsgToActiveView("ViewFit")
#Gui.activeDocument().setEdit("Sketch")
#Gui.activeDocument().activeView().viewIsometric()

