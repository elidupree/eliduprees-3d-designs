import re

import importlib


def setup(wrap, export, override_attribute):
  def simple_override (c, name, value):
    override_attribute(c, name, lambda original: value)
  #import pkgutil
  #import OCCT
  #modules = [module.name for module in pkgutil.iter_modules(OCCT.__path__)]
  modules = re.findall(r"[\w_]+", "Exchange, TopoDS, gp, TopAbs, BRep, BRepBuilderAPI, BRepCheck")
  for name in modules:
    globals() [name] = wrap (importlib.import_module ("OCCT."+name))
    
  ExchangeBasic = Exchange.ExchangeBasic
  
  Vector = gp.gp_Vec
  Point = gp.gp_Pnt
  
  def vector(*args, **kwargs):
    return Vector (*args, **kwargs)
  
  def make_Vector(original):
    def derived(cls, *args):
      #if type(args[0]) is Point:
      if len(args) == 3:
        return original(*(float (value) for value in args))
      return original(*args)
    return classmethod(derived)
  override_attribute(Vector, "__new__", make_Vector)
  
  def Vector_str(self):
    return f"Vector({self.X()}, {self.Y()}, {self.Z()})"
  def Point_str(self):
    return f"Point({self.X()}, {self.Y()}, {self.Z()})"
  def Vector_index(self, index):
    if index == 0:
      return self.X()
    if index == 1:
      return self.Y()
    if index == 2:
      return self.Z()
    raise IndexError("point/vector can only be indexed with 0-2")
  
  simple_override(Vector, "__str__", Vector_str)
  simple_override(Vector, "__index__", Vector_index)
  simple_override(Point, "__index__", Vector_index)
  simple_override(Point, "__str__", Point_str)
  simple_override(Vector, "Translated", lambda self, other: self + other)
    
    
  simple_override(Point, "__add__", lambda self, other: self.Translated (other))
  simple_override(Point, "__sub__", lambda self, other: self.Translated (-other))
  
   
  shape_typenames = ["Vertex", "Edge", "Wire", "Face", "Shell", "Solid", "CompSolid", "Compound"]
  shape_types_by_ShapeType = {}
  def handle_shape_type(typename):
    c = getattr(TopoDS, f"TopoDS_{typename}")
    from_shape = getattr(TopoDS.TopoDS, f"{typename}_")
    shape_types_by_ShapeType [getattr (TopAbs.TopAbs_ShapeEnum, "TopAbs_"+ typename.upper())] = c
    globals() [typename] = c
    simple_override(c, "from_shape", from_shape)
    #simple_override(c, "read_brep", lambda path: from_shape(Shape.read_brep (path)))
    simple_override(c, "write_brep", lambda self, path: Exchange.ExchangeBasic.write_brep (self, path))
    #import pprint
    print(c().wrapped_object.__class__ is c.wrapped_object)
    #pprint.pprint({a:getattr(c().wrapped_object, a, None) for a in dir(c().wrapped_object)})
    print(c.wrapped_object.__init__, c().wrapped_object.__init__)
    print(c().write_brep)
    print(type(c.wrapped_object))
    
    
  for typename in shape_typenames:
    handle_shape_type(typename)
  
  Shape = TopoDS.TopoDS_Shape
  #simple_override(Shape, "read_brep", Exchange.ExchangeBasic.read_brep)
  simple_override(Shape, "write_brep", lambda self, path: Exchange.ExchangeBasic.write_brep (self, path))
  
  def is_shape(obj):
    return isinstance(obj, Shape)
  def read_brep (path):
    shape = Exchange.ExchangeBasic.read_brep (path)
    return shape.downcast()
  def shape_type(shape):
    return shape_types_by_ShapeType[shape.ShapeType()]
  
  simple_override(Shape, "shape_type", lambda self: shape_types_by_ShapeType[self.ShapeType()])
  simple_override(Shape, "downcast", lambda self: shape_type(self).from_shape (self))
  
  def make_Vertex (original):
    def derived(cls, *args, **kwargs):
      if len(args) == 0:
        return original()
      if len (args) == 3:
        args = [Point (*args)]
      return BRepBuilderAPI.BRepBuilderAPI_MakeVertex(*args, **kwargs).Vertex()
    return classmethod(derived)
  override_attribute(Vertex, "__new__", make_Vertex)
  
  def make_Edge(original):
    def derived(cls, *args):
      if len(args) == 0:
        return original()
      return BRepBuilderAPI.BRepBuilderAPI_MakeEdge(*args).Edge()
    return classmethod(derived)
  override_attribute(Edge, "__new__", make_Edge)
  
  def make_Wire(original):
    def derived(cls, edges_or_wires = []):
      builder = BRepBuilderAPI.BRepBuilderAPI_MakeWire()
      for item in edges_or_wires:
        builder.Add (item)
      if not builder.IsDone():
        raise RuntimeError("Invalid wire (detected by builder)")
      result = builder.Wire()
      if not BRepCheck.BRepCheck_Analyzer(result).IsValid():
        raise RuntimeError("Invalid wire (detected by analyzer)")
      return result
    return classmethod(derived)
  override_attribute(Wire, "__new__", make_Wire)
  
  def make_Face(original):
    def derived(cls, *args, holes = []):
      if len(args) == 0:
        return original()
      builder = BRepBuilderAPI.BRepBuilderAPI_MakeFace(*args)
      for hole in holes:
        builder.Add (hole)
      if not builder.IsDone():
        raise RuntimeError("Invalid face (detected by builder)")
      result = builder.Face()
      if not BRepCheck.BRepCheck_Analyzer(result).IsValid():
        raise RuntimeError("Invalid face (detected by analyzer)")
      return result
    return classmethod(derived)
  override_attribute(Face, "__new__", make_Face)
  
  def make_Shell(original):
    def derived(cls, faces = []):
      shell = original()
      builder = BRep.BRep_Builder()
      #print ("builder created")
      builder.MakeShell(shell)
      #print ("Shell made?")
      for face in faces:
        #print ("adding face", face)
        builder.Add (shell, face)
      #print ("done adding faces")
      if not BRepCheck.BRepCheck_Analyzer(shell).IsValid():
        raise RuntimeError("Invalid shell (detected by analyzer)")
      return shell
    return classmethod(derived)
  override_attribute(Shell, "__new__", make_Shell)
  
  def make_Solid(original):
    def derived(cls, *args, holes = []):
      if len(args) == 0:
        return original()
      builder = BRepBuilderAPI.BRepBuilderAPI_MakeSolid(*args)
      for hole in holes:
        builder.Add (hole)
      if not builder.IsDone():
        raise RuntimeError("Invalid solid (detected by builder)")
      result = builder.Solid()
      if not BRepCheck.BRepCheck_Analyzer(result).IsValid():
        raise RuntimeError("Invalid solid (detected by analyzer)")
      return result
    return classmethod(derived)
  override_attribute(Solid, "__new__", make_Solid)
  
  
  for name in re.findall(r"[\w_]+", "vector, Vector, Point, Shape, is_shape, read_brep"):
    export(name, locals()[name])
  for name in shape_typenames:
    export(name, globals()[name])
