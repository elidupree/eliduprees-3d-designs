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


band_width = 6
band_thickness = 1
band_leeway = 1
flex_perpendicular_leeway = 2
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
deflector_peg_diameter = 2
deflector_peg_length = 2
deflector_thickness = 1
deflector_slope = 0.2
releaser_slope = 0.6

deflector_peg_radius = deflector_peg_diameter/2
deflector_radius = deflector_thickness/2

claw_right = 0
claw_left = claw_right - claw_thickness
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


channel_left_stop = claw_left
channel_right_stop = flex_support_right + motion_distance
deflector_left_end = deflector_peg_right + flex_perpendicular_leeway
deflector_left_end_center = deflector_left_end + deflector_radius
deflector_fully_down_horizontal = claw_right + band_thickness*2 + band_leeway*2 + (deflector_peg_horizontal_middle - claw_left)
deflector_right_end_center = deflector_fully_down_horizontal + claw_deflect_distance/deflector_slope
releaser_fully_down_horizontal = deflector_peg_horizontal_middle + motion_distance
releaser_left_end_center = releaser_fully_down_horizontal - claw_deflect_distance/releaser_slope

slider_shape = FreeCAD_shape_builder (lambda whatever: whatever + vector (0, 0, claw_front)).build ([
  start_at (flex_support_right, slider_bottom),
  horizontal_to (claw_left), vertical_to (slider_top), horizontal_to (flex_right), vertical_to (flex_bottom), horizontal_to (flex_left), diagonal_to (claw_solid_right, claw_solid_bottom), horizontal_to (deflector_peg_right),
  
  #vertical_to (deflector_peg_bottom + deflector_peg_radius),
  #arc_through_to ((deflector_peg_horizontal_middle, deflector_peg_bottom), (deflector_peg_left, deflector_peg_bottom + deflector_peg_radius)),
  horizontal_to (deflector_peg_horizontal_middle),
  diagonal_to (claw_left, deflector_peg_bottom + deflector_peg_radius),
  
  vertical_to (claw_top), horizontal_to (claw_right), vertical_to (flex_top), horizontal_to (flex_support_right), close()
])

slider_main_part = Part.Face (Part.Wire (slider_shape.Edges)).extrude (FreeCAD.Vector (0, 0, claw_width))

slider_triangle_shape = FreeCAD_shape_builder (lambda whatever: vector (claw_left, whatever [1], whatever [0])).build ([
  start_at(claw_front, slider_top),
  horizontal_to (claw_back),
  diagonal_to (slider_protrusions_back, slider_vertical_middle),
  diagonal_to (claw_back, slider_bottom),
  horizontal_to (claw_front),
  diagonal_to (slider_protrusions_front, slider_vertical_middle),
  close(),
])

slider_triangle_part = Part.Face (Part.Wire (slider_triangle_shape.Edges)).extrude (FreeCAD.Vector (flex_support_right - claw_left, 0, 0))

deflector_peg_part = Part.makeCylinder (
  deflector_peg_radius, claw_width + deflector_peg_length*2,
  vector (deflector_peg_horizontal_middle, deflector_peg_vertical_middle, claw_front - deflector_peg_length),
  vector (0, 0, 1),
)

#document().addObject ("Part::MultiFuse", "slider_part").Shapes=[slider_main_part, slider_triangle_part, deflector_peg_part]

#Part.show (document().slider_part)
#Part.show (slider_triangle_part)

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

slider_part = slider_part.makeFillet(1, edges) #[slider_part.Edges [index] for index in range (0, len (slider_part.Edges), 3)])

channel_box = Part.makeBox (
  channel_right_stop - channel_left_stop + channel_wall_thickness,
  flex_top - slider_bottom + channel_wall_thickness,
  slider_protrusions_back - slider_protrusions_front + channel_wall_thickness*2)
channel_box.translate (vector (
  channel_left_stop - channel_wall_thickness,
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
  #start_at (channel_right_stop, deflector_fully_down_center),
  #horizontal_to (releaser_fully_down_horizontal),
  #diagonal_to (releaser_left_end_center, deflector_top_center),
])
deflector_wire = Part.Wire (deflector_shape.Edges).makeOffset2D (deflector_radius)
deflector_part = Part.Face (deflector_wire).extrude (FreeCAD.Vector (0, 0, slider_protrusions_back - slider_protrusions_front + channel_wall_thickness*2))

releaser_shape = FreeCAD_shape_builder (lambda whatever: whatever + vector (0, 0, slider_protrusions_front - channel_wall_thickness)).build ([
  start_at (channel_right_stop, deflector_fully_down_center),
  horizontal_to (releaser_fully_down_horizontal),
  diagonal_to (releaser_left_end_center, deflector_top_center),
])
releaser_wire = Part.Wire (releaser_shape.Edges).makeOffset2D (deflector_radius)
releaser_part = Part.Face (releaser_wire).extrude (FreeCAD.Vector (0, 0, slider_protrusions_back - slider_protrusions_front + channel_wall_thickness*2)).common (channel_box)


body_part = channel_box.cut(wide_channel_part).fuse ((deflector_part, releaser_part)).cut(narrow_channel_part)


Part.show (slider_part, "SliderSquare")

Part.show (body_part)

'''document().addObject ("Part::Fillet", "Slider")
document().Slider.Base = document().SliderSquare
FreeCAD.Console.PrintMessage ([(index, 1.0, 1.0)
  for index, edge in enumerate (document().SliderSquare.Shape.Edges)
  if FreeCAD.BoundBox (claw_right, flex_top, -100, claw_right, claw_top, 100).isInside (edge.BoundBox) or FreeCAD.BoundBox (flex_right, flex_bottom, -100, flex_right, flex_bottom, 100).isInside (edge.BoundBox)])
document().Slider.Edges = [(22, 1.0, 1.0)]
[(index, 1.0, 1.0)
  for index, edge in enumerate (document().SliderSquare.Shape.Edges)
  if FreeCAD.BoundBox (claw_right, flex_top, -100, claw_right, claw_top, 100).isInside (edge.BoundBox) or FreeCAD.BoundBox (flex_right, flex_bottom, -100, flex_right, flex_bottom, 100).isInside (edge.BoundBox)]
Gui.ActiveDocument.SliderSquare.Visibility = False'''

crop_box = Part.makeBox (5, 100, 100)
crop_box.translate (vector (5, -50, -50))
Part.show (body_part.common(crop_box))


'''document().addObject ("PartDesign::Body", "Body")
document().Body.newObject ("Sketcher::SketchObject", "Sketch")
#document().Sketch.Support = (App.activeDocument().XY_Plane, [''])
#document().Sketch.MapMode = "FlatFace"
current_sketch = "Sketch"

hack_offset = 0
def add_geometry(geometry, *constraints, coincident = True):
  index = document().getObject (current_sketch).GeometryCount
  document().getObject (current_sketch).addGeometry (geometry, False)
  if index > 0 and coincident:
    add_constraint ("Coincident", index - 1, 2, index, 1);
  for constraint in constraints:
    if isinstance(constraint, str):
      constraint = [constraint]
    else:
      constraint = list(constraint)
    constraint.insert(1, index)
    add_constraint (*constraint);
  return index

def add_line(*constraints, **kwargs):
  global hack_offset
  hack_offset += 1
  line = Part.LineSegment (FreeCAD.Vector (-5+hack_offset, 23+hack_offset), FreeCAD.Vector (-5+hack_offset*2, -4+hack_offset))
  return add_geometry(line, *constraints, **kwargs)



def vertical_to(coordinate, **kwargs):
  global hack_offset
  hack_offset += 1
  line = Part.LineSegment (FreeCAD.Vector (-5+hack_offset, 23+hack_offset), FreeCAD.Vector (-5+hack_offset*2, coordinate))
  index = add_geometry(line, "Vertical", **kwargs)
  add_constraint ("DistanceY", index, 2, coordinate)
  return index


def horizontal_to(coordinate, **kwargs):
  global hack_offset
  hack_offset += 1
  line = Part.LineSegment (FreeCAD.Vector (-5+hack_offset, 23+hack_offset), FreeCAD.Vector (coordinate, -5+hack_offset*2))
  index = add_geometry(line, "Horizontal", **kwargs)
  add_constraint ("DistanceX", index, 2, coordinate)
  return index
  
def diagonal_to(*coordinates, **kwargs):
  global hack_offset
  hack_offset += 1
  line = Part.LineSegment (FreeCAD.Vector (-5+hack_offset, 23+hack_offset), FreeCAD.Vector (coordinates [0], coordinates [1]))
  index = add_geometry(line, **kwargs)
  add_constraint ("DistanceX", index, 2, coordinates [0])
  add_constraint ("DistanceY", index, 2, coordinates [1])
  return index
  

def add_arc(*constraints, **kwargs):
  global hack_offset
  hack_offset += 1
  arc = Part.ArcOfCircle(Part.Circle(FreeCAD.Vector (-5+hack_offset, 23+hack_offset*1.1, 0), FreeCAD.Vector (0,0,1), 2+hack_offset), 2+hack_offset*1.2, 3+hack_offset*1.3)
  return add_geometry(arc, *constraints, **kwargs)
  
def add_constraint(*args):
  document().getObject (current_sketch).addConstraint(Sketcher.Constraint (*args))

slider_bottom_line = horizontal_to (claw_left)
#add_constraint ("DistanceY", slider_bottom_line, 1, slider_bottom);
slider_left_line = vertical_to (slider_top)
slider_top_line = horizontal_to (flex_right)
flex_support_left_line = vertical_to (flex_bottom)
#flex_inner_arc = add_arc(coincident = False)
#add_constraint ("DistanceY", flex_inner_arc, 2, flex_bottom);
#add_constraint ("DistanceX", flex_inner_arc, 2, flex_right);
flex_bottom_line = horizontal_to (claw_right)
peg_right_line = vertical_to (peg_bottom)
peg_bottom_line = horizontal_to (claw_left)
claw_left_line = vertical_to (claw_top)
claw_top_line = horizontal_to (claw_right)
claw_right_line = vertical_to (flex_top)
flex_top_line = horizontal_to (flex_support_right)
flex_support_right_line = vertical_to (slider_bottom)
#flex_outer_arc = add_arc(coincident = False)
#add_constraint ("DistanceY", flex_outer_arc, 2, slider_bottom);
#add_constraint ("DistanceX", flex_outer_arc, 2, flex_right);

add_constraint ("Coincident", flex_support_right_line, 2, slider_bottom_line, 1)

#add_constraint ("DistanceX", flex_bottom, 1, flex_top, 2, 0);
#add_constraint ("DistanceX", flex_bottom, 2, flex_top, 1, 0);
#add_constraint ("DistanceY", flex_top, 1, flex_bottom, 1, flex_thickness);
#add_constraint ("DistanceY", peg_bottom, 1, slider_top, 1, claw_length);
#add_constraint ("DistanceY", peg_bottom, 1, flex_top, 1, deflector_thickness + deflector_peg_diameter);
#add_constraint ("Tangent", flex_outer_arc, 1, flex_top_line, 2);
#add_constraint ("Tangent", flex_inner_arc, 2, flex_bottom_line, 1);
#add_constraint ("Tangent", slider_top_line, 2, flex_inner_arc, 1);

document().Body.newObject ("PartDesign::Pad", "slider_pad")
document().slider_pad.Profile = document().Sketch
document().slider_pad.Length = claw_width


document().Body.newObject ("Sketcher::SketchObject", "slider_triangle_sketch")
current_sketch = "slider_triangle_sketch"
document().slider_triangle_sketch.Support = (document().YZ_Plane, [""])
horizontal_to (claw_back)
diagonal_to (slider_protrusions_back, slider_vertical_middle)
diagonal_to (claw_back, slider_bottom)
horizontal_to (claw_front)
diagonal_to (slider_protrusions_front, slider_vertical_middle)
last = diagonal_to (claw_front, slider_top)
add_constraint ("Coincident", last, 2, 0, 1)

document().Body.newObject ("PartDesign::Pad", "slider_triangle_pad")
document().slider_triangle_pad.Profile = document().slider_triangle_sketch
document().slider_triangle_pad.Length = flex_support_right - claw_left'''

#object = document.addObject("Part::Box","Box")
#object.Label = "Cube"

#App.getDocument("Something").Cut.Placement=App.Placement(App.Vector(5,0,0), App.Rotation(App.Vector(0,0,1),0), App.Vector(0,0,0))

document().recompute()
#Gui.SendMsgToActiveView("ViewFit")
#Gui.activeDocument().setEdit("Sketch")
#Gui.activeDocument().activeView().viewIsometric()

