import re

import importlib


def setup(wrap, export, override_attribute):
  def simple_override (c, name, value):
    override_attribute(c, name, lambda original: value)
  #import pkgutil
  #import OCCT
  #modules = [module.name for module in pkgutil.iter_modules(OCCT.__path__)]
  modules = re.findall(r"[\w_]+", "Exchange, TopoDS, gp, TopAbs")
  for name in modules:
    globals() [name] = wrap (importlib.import_module ("OCCT."+name))
    
  ExchangeBasic = Exchange.ExchangeBasic
  
  
  
  def vector(*arguments):
    if len (arguments) == 3:
      return gp.gp_Vec(*(float (value) for value in arguments))
    if len (arguments) == 0:
      return gp.gp_Vec()
  
  def vec_str(self):
    return f"Vec({self.X()}, {self.Y()}, {self.Z()})"
  def vec_index(self, index):
    if index == 0:
      return self.X()
    if index == 1:
      return self.Y()
    if index == 2:
      return self.Z()
    raise IndexError("vector can only be indexed with 0-2")
  
  simple_override(gp.gp_Vec, "__str__", vec_str)
  simple_override(gp.gp_Vec, "__index__", vec_index)
  
  
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
  
  for name in re.findall(r"[\w_]+", "vector, Shape, is_shape, read_brep"):
    export(name, locals()[name])
  for name in shape_typenames:
    export(name, globals()[name])
