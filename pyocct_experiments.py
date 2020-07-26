import pprint
import OCCT.BOPAlgo
import OCCT.BRepAlgoAPI
import OCCT.BRepBuilderAPI
import OCCT.gp # geometric primitives
import OCCT.TopoDS
import OCCT.GC
import OCCT.Geom
import OCCT.Geom2d
from OCCT.STEPControl import STEPControl_Reader

'''
for mod in [OCCT.BOPAlgo, OCCT.BRepAlgoAPI, OCCT.BRepBuilderAPI, OCCT.TopoDS, OCCT.gp]:
  print(mod)
  pprint.pprint({a:type(getattr(mod,a)) for a in dir(mod)})
  
foo = OCCT.BRepAlgoAPI.BRepAlgoAPI_BooleanOperation()
reader = STEPControl_Reader()
foo = reader.OneShape
foo = OCCT.gp.gp_Vec.__init__
pprint.pprint({a:repr(getattr(foo,a)) for a in dir(foo)})
print(str(OCCT.gp.gp_Vec.__init__.__name__))
print(OCCT.gp.gp_Vec({}))
print(OCCT.BRepBuilderAPI.BRepBuilderAPI_MakeFace(6))
'''

import dis
g=5
repr(str(dis.dis(pprint.pprint)))
print (type (globals()))
