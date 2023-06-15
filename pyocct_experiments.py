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
initialize_pyocct_system()

def dependency_function():
  transitive_dependency
  pass

@run_if_changed
def test():
  dependency_function()
  return g
print (test)

v1 = vector(1,2,3)
v2 = vector(4,5,6)
print("vectors added", v1 + v2)

import OCCT.BRepBuilderAPI
import OCCT.gp
@run_if_changed
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

@run_if_changed
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
    Wire ([edges [0], edges [3], edges [5].complemented(), edges [1].complemented()]),
    Wire ([edges [8], edges [10], edges [11].complemented(), edges [9].complemented()]).complemented(),
    Wire ([edges [0], edges [4], edges [8].complemented(), edges [2].complemented()]).complemented(),
    Wire ([edges [5], edges [7], edges [11].complemented(), edges [6].complemented()]),
    Wire ([edges [1], edges [6], edges [9].complemented(), edges [2].complemented()]),
    Wire ([edges [3], edges [7], edges [10].complemented(), edges [4].complemented()]).complemented(),
  ]
  faces = [Face (wire) for wire in wires]
  shell = Shell (faces)
  solid = Solid (shell)
  offset = thicken_solid(solid, [faces[0]], 0.2)
  return {
    "vertices": vertices,
    "edges": edges,
    "wires": wires,
    "faces": faces,
    "shell": shell,
    "solid": solid,
    "offset": offset,
  }
  
print ("cube", cube)

@run_if_changed
def surface():
  surface = BSplineSurface(
    [[Point(0,0,0), Point(1,0,0)], [Point(0,1,0), Point(1,1,1)]],
    u = BSplineDimension (degree = 1),
    v = BSplineDimension (degree = 1),
    weights = [[1,1], [1,1]]
  )
  
  return Face(surface)


print(surface)

@run_if_changed
def flex_but_dont_twist():
  curve = BSplineCurve ([Origin, Point (20, 50, 0), Point (0, 100, 0)], BSplineDimension (degree = 2))
  length = curve.length()
  controls = []
  struts = []
  amount = 13
  radius = 0.25
  for index, distance in enumerate (subdivisions (0, length, amount = amount)):
    steps_from_terminus = min(index, (amount-1)-index)
    parameter = curve.parameter (distance = distance)
    derivatives = curve.derivatives (parameter)
    offset = 0 if steps_from_terminus == 0 else (-4 if index % 2 == 0 else 12)
    print(vars (derivatives))
    controls.append (derivatives.position - derivatives.normal*offset)
    if index % 2 == 0 and steps_from_terminus != 0:
      struts.append(Edge(derivatives.position, derivatives.position - derivatives.normal*10).extrude(derivatives.tangent*radius*2, centered=True))  
  
  zigzag_wire = Wire (Edge (BSplineCurve (controls)))
  curve_wire = Wire (Edge (curve))
  interior = Face (Wire (curve_wire, zigzag_wire)).extrude (Up*10)
  struts = [Intersection (interior, strut) for strut in struts]
  #struts = [Offset2D (Wire (strut), radius) for strut in struts]
  #print(struts)
  #preview (struts[5])
 
  zigzag = Face (Offset2D (zigzag_wire, radius))
  curve_face = Face (Offset2D (curve_wire, radius))
  result = Compound(zigzag, curve_face, struts).extrude (Up*10)
  save_STL("flex_but_dont_twist_mesh", result)
  preview (result)
  return result

viewed = cube["offset"]
#viewed = surface_test
preview (viewed)
