'''FREECADPATH = r"C:\Program Files\FreeCAD 0.18\bin"
import sys
sys.path.append(FREECADPATH)
 
import FreeCAD
       
       
import FreeCADGui 

FreeCADGui.showMainWindow()
import time
time.sleep(5)'''
App.newDocument("Unnamed")
App.getDocument("Unnamed").Cut.Placement=App.Placement(App.Vector(5,0,0), App.Rotation(App.Vector(0,0,1),0), App.Vector(0,0,0))

