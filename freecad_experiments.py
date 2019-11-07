'''FREECADPATH = r"C:\Program Files\FreeCAD 0.18\bin"

import sys
sys.path.append(FREECADPATH)
 
import FreeCAD
       
       
import FreeCADGui 

FreeCADGui.showMainWindow()
import time
time.sleep(5)'''

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
claw_thickness = 2
motion_distance = 100
channel_depth = 6
deflector_peg_diameter = 2
deflector_thickness = 1

deflector_peg_radius = deflector_peg_diameter/2

#document().addObject ("PartDesign::Body", "Body")
document().addObject ("Sketcher::SketchObject", "Sketch")
#document().Sketch.Support = (App.activeDocument().XY_Plane, [''])
#document().Sketch.MapMode = "FlatFace"
current_sketch = "Sketch"

hack_offset = 0
def add_geometry(geometry, *constraints):
  index = document().getObject (current_sketch).GeometryCount
  document().getObject (current_sketch).addGeometry (geometry, False)
  if index > 0:
    add_constraint ("Coincident", index - 1, 2, index, 1);
  for constraint in constraints:
    if isinstance(constraint, str):
      constraint = [constraint]
    else:
      constraint = list(constraint)
    constraint.insert(1, index)
    add_constraint (*constraint);
  return index
def add_line(*constraints):
  global hack_offset
  hack_offset += 1
  line = Part.LineSegment (FreeCAD.Vector (-5+hack_offset, 23+hack_offset), FreeCAD.Vector (-5+hack_offset*2, -4+hack_offset))
  return add_geometry(line, *constraints)
def add_arc(*constraints):
  global hack_offset
  hack_offset += 1
  arc = Part.ArcOfCircle(Part.Circle(FreeCAD.Vector (-5+hack_offset, 23+hack_offset*1.1, 0), FreeCAD.Vector (0,0,1), 2+hack_offset), 2+hack_offset*1.2, 3+hack_offset*1.3)
  return add_geometry(arc, *constraints)
def add_constraint(*args):
  document().getObject (current_sketch).addConstraint(Sketcher.Constraint (*args))

slider_bottom = add_line ("Horizontal")
slider_left = add_line ("Vertical", ("Distance", channel_depth))
slider_top = add_line ("Horizontal")
flex_inner_arc = add_arc()
flex_bottom = add_line("Horizontal")
peg_right = add_line ("Vertical")
peg_bottom = add_line ("Horizontal")
claw_left = add_line("Vertical", ("Distance", claw_length + deflector_thickness + deflector_peg_diameter))
claw_top = add_line ("Horizontal", ("Distance", claw_thickness))
claw_right = add_line("Vertical", ("Distance", claw_length))
flex_top = add_line("Horizontal", ("Distance", flex_length))
flex_outer_arc = add_arc()

add_constraint ("Coincident", flex_outer_arc, 2, slider_bottom, 1)

add_constraint ("DistanceX", flex_bottom, 1, flex_top, 2, 0);
add_constraint ("DistanceX", flex_bottom, 2, flex_top, 1, 0);
add_constraint ("DistanceY", flex_top, 1, flex_bottom, 1, flex_thickness);
add_constraint ("DistanceY", peg_bottom, 1, slider_top, 1, claw_length);
#add_constraint ("DistanceY", peg_bottom, 1, flex_top, 1, deflector_thickness + deflector_peg_diameter);
add_constraint ("Tangent", flex_outer_arc, flex_top);


#object = document.addObject("Part::Box","Box")
#object.Label = "Cube"

#App.getDocument("Something").Cut.Placement=App.Placement(App.Vector(5,0,0), App.Rotation(App.Vector(0,0,1),0), App.Vector(0,0,0))

document().recompute()
#Gui.SendMsgToActiveView("ViewFit")
Gui.activeDocument().setEdit("Sketch")
#Gui.activeDocument().activeView().viewIsometric()

