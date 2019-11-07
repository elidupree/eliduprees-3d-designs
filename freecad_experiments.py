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
claw_thickness = 1
motion_distance = 100
channel_depth = 6
deflector_peg_diameter = 3

deflector_peg_radius = deflector_peg_diameter/2

#document().addObject ("PartDesign::Body", "Body")
document().addObject ("Sketcher::SketchObject", "Sketch")
#document().Sketch.Support = (App.activeDocument().XY_Plane, [''])
#document().Sketch.MapMode = "FlatFace"
current_sketch = "Sketch"
def add_line(*constraints):
  index = document().getObject (current_sketch).GeometryCount
  document().getObject (current_sketch).addGeometry (Part.LineSegment (FreeCAD.Vector (-5+index, 23+index), FreeCAD.Vector (-5+index, -4+index)))
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
def add_constraint(*args):
  document().getObject (current_sketch).addConstraint(Sketcher.Constraint (*args))

claw_right = add_line("Vertical", ("Distance", claw_length))
flex_top = add_line("Horizontal", ("Distance", flex_length))

#object = document.addObject("Part::Box","Box")
#object.Label = "Cube"

#App.getDocument("Something").Cut.Placement=App.Placement(App.Vector(5,0,0), App.Rotation(App.Vector(0,0,1),0), App.Vector(0,0,0))

document().recompute()
#Gui.SendMsgToActiveView("ViewFit")
Gui.activeDocument().setEdit("Sketch")
#Gui.activeDocument().activeView().viewIsometric()

