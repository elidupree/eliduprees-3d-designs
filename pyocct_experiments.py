import pprint
import sys
import OCCT.BOPAlgo
import OCCT.BRepAlgoAPI
import OCCT.BRepBuilderAPI
import OCCT.gp # geometric primitives
import OCCT.TopoDS
import OCCT.GC
import OCCT.Geom
import OCCT.Geom2d
from OCCT.STEPControl import STEPControl_Reader

'''from OCCT.TopoDS import TopoDS_Shape as Shape
Shape().ShapeType()'''

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
g=7
transitive_dependency = 6
print(repr(str(dis.Bytecode(pprint.pprint).dis())))
print (type (globals()))

import pyocct_system
from pyocct_system import *
print (sys.argv)
initialize_system (globals(), sys.argv[1])

def dependency_function():
  transitive_dependency
  pass

@cached
def test():
  dependency_function()
  return g
print (test)

v1 = vector(1,2,3)
v2 = vector(4,5,6)
print("vectors added", v1 + v2)

import OCCT.BRepBuilderAPI
import OCCT.gp
@cached
def test2():
  result = Vertex(wrap(OCCT.gp).gp_Pnt(0, 0, 0))
  print ("before caching", repr (result))
  return result


print("after caching", repr(test2))
print(dir(test2))
print(test2.ShapeType())
print (isinstance((test2), (Shape)), unwrap(Shape))
print("uhhh")
s=Shape()
print("uhhh")
print("shape", repr(Shape()))

'''from OCCT.BRepTools import BRepTools
from OCCT.BRep import BRep_Builder
import io
wrap(BRepTools).Read_(Shape(), io.BytesIO(b""), BRep_Builder())'''

@cached
def cube():
  vertices = [
    Vertex (0, 0, 0),
    Vertex (0, 0, 1),
    Vertex (0, 1, 0),
    Vertex (0, 1, 1),
    Vertex (1, 0, 0),
    Vertex (1, 0, 1),
    Vertex (1, 1, 0),
    Vertex (1, 1, 1),
  ]
  edges = [
    Edge (vertices [0], vertices [1]),
    Edge (vertices [0], vertices [2]),
    Edge (vertices [0], vertices [4]),
    Edge (vertices [1], vertices [3]),
    Edge (vertices [1], vertices [5]),
    Edge (vertices [2], vertices [3]),
    
    Edge (vertices [2], vertices [6]),
    Edge (vertices [3], vertices [7]),
    Edge (vertices [4], vertices [5]),
    Edge (vertices [4], vertices [6]),
    Edge (vertices [5], vertices [7]),
    Edge (vertices [6], vertices [7]),
  ]
  # note that the latter edges don't need to be complemented; it seems like MakeWire forces the later edge orientations to match the first edge.
  wires = [
    Wire ([edges [0], edges [3], edges [5].Complemented(), edges [1].Complemented()]),
    Wire ([edges [8], edges [10], edges [11].Complemented(), edges [9].Complemented()]).Complemented(),
    Wire ([edges [0], edges [4], edges [8].Complemented(), edges [2].Complemented()]).Complemented(),
    Wire ([edges [5], edges [7], edges [11].Complemented(), edges [6].Complemented()]),
    Wire ([edges [1], edges [6], edges [9].Complemented(), edges [2].Complemented()]),
    Wire ([edges [3], edges [7], edges [10].Complemented(), edges [4].Complemented()]).Complemented(),
  ]
  faces = [Face (wire) for wire in wires]
  shell = Shell (faces)
  solid = Solid (shell)
  
  return {
    "vertices": vertices,
    "edges": edges,
    "wires": wires,
    "faces": faces,
    "shell": shell,
    "solid": solid,
  }
  
print ("cube", cube)

@cached
def surface_test():
  surface = BSplineSurface(
    [[Point(0,0,0), Point(1,0,0)], [Point(0,1,0), Point(1,1,1)]],
    u = BSplineDimension (degree = 1),
    v = BSplineDimension (degree = 1),
    weights = [[1,1], [1,1]]
  )
  
  return Face(surface)

print(surface_test)



view = False
#view = True
if view:
  from OCCT.Visualization.QtViewer import ViewerQt
  viewed = cube["solid"]
  viewed = surface_test
  v = ViewerQt(width=2000, height=1500)
  v.display_shape(unwrap(viewed))
  v.start()