'''FREECADPATH = r"C:\Program Files\FreeCAD 0.18\bin"
import sys
sys.path.append(FREECADPATH)
 
import FreeCAD
       
       
import FreeCADGui 

FreeCADGui.showMainWindow()
import time
time.sleep(5)'''

FreeCAD = App

for document_name in FreeCAD.listDocuments().keys():
  FreeCAD.closeDocument (document_name)
Gui.activateWorkbench("PartWorkbench")

document = App.newDocument("Something")
object = document.addObject("Part::Box","Box")
object.Label = "Cube"

#App.getDocument("Something").Cut.Placement=App.Placement(App.Vector(5,0,0), App.Rotation(App.Vector(0,0,1),0), App.Vector(0,0,0))

document.recompute()
Gui.SendMsgToActiveView("ViewFit")
Gui.activeDocument().activeView().viewIsometric()

