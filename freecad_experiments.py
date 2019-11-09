'''FREECADPATH = r"C:\Program Files\FreeCAD 0.18\bin"

import sys
sys.path.append(FREECADPATH)
 
import FreeCAD
       
       
import FreeCADGui 

FreeCADGui.showMainWindow()
import time
time.sleep(5)'''

import PartDesignGui

FreeCAD = App
def document():
  return App.activeDocument()

for document_name in list(FreeCAD.listDocuments().keys()):
  FreeCAD.closeDocument (document_name)
#Gui.activateWorkbench("PartWorkbench")

App.newDocument("Something")
#App.setActiveDocument("Something")


band_width = 6
claw_length = band_width + 2
flex_length = 40
flex_thickness = 1
flex_support_length = 6
claw_thickness = 2
claw_width = 6
motion_distance = 100
channel_depth = 6
slider_channel_tolerance = 0.2
channel_wall_thickness = 3
deflector_peg_diameter = 2
deflector_peg_length = 2
deflector_thickness = 1

deflector_peg_radius = deflector_peg_diameter/2

claw_right = 0
claw_left = claw_right - claw_thickness
flex_right = claw_right + flex_length
flex_support_right = flex_right + flex_support_length

flex_top = 0
claw_top = flex_top + claw_length
flex_bottom = flex_top - flex_thickness
peg_bottom = flex_top - deflector_thickness - deflector_peg_diameter
slider_top = peg_bottom - claw_length
slider_bottom = slider_top - channel_depth
channel_floor_bottom = slider_bottom - channel_wall_thickness
slider_vertical_middle = (slider_top + slider_bottom)/2

claw_front = - claw_width/2
claw_back = claw_front + claw_width
slider_protrusions_front = claw_front - deflector_peg_length
slider_protrusions_back = claw_back + deflector_peg_length

document().addObject ("PartDesign::Body", "Body")
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
document().slider_triangle_pad.Length = flex_support_right - claw_left

#object = document.addObject("Part::Box","Box")
#object.Label = "Cube"

#App.getDocument("Something").Cut.Placement=App.Placement(App.Vector(5,0,0), App.Rotation(App.Vector(0,0,1),0), App.Vector(0,0,0))

document().recompute()
#Gui.SendMsgToActiveView("ViewFit")
Gui.activeDocument().setEdit("Sketch")
#Gui.activeDocument().activeView().viewIsometric()

