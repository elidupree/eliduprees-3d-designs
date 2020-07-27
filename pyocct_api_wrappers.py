import re

import importlib


def setup(wrap, export, override_attribute):
  def simple_override (c, name, value):
    override_attribute(c, name, lambda original: value)
  #import pkgutil
  #import OCCT
  #modules = [module.name for module in pkgutil.iter_modules(OCCT.__path__)]
  modules = re.findall(r"[\w_]+", "Exchange, TopoDS, gp")
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
  
  
  brep_typenames = ["Vertex", "Edge", "Wire", "Face", "Shell", "Solid", "CompSolid", "Compound"]
  def handle_brep_type(typename):
    c = getattr(TopoDS, f"TopoDS_{typename}")
    from_shape = getattr(TopoDS.TopoDS, f"{typename}_")
    globals() [typename] = c
    simple_override(c, "from_shape", from_shape)
    simple_override(c, "read_brep", lambda path: from_shape(Shape.read_brep (path)))
    simple_override(c, "write_brep", lambda self, path: Exchange.ExchangeBasic.write_brep (self, path))
    #import pprint
    print(c().wrapped_object.__class__ is c.wrapped_object)
    #pprint.pprint({a:getattr(c().wrapped_object, a, None) for a in dir(c().wrapped_object)})
    print(c.wrapped_object.__init__, c().wrapped_object.__init__)
    print(c().write_brep)
    print(type(c.wrapped_object))
    
    
  for typename in brep_typenames:
    handle_brep_type(typename)
  
  Shape = TopoDS.TopoDS_Shape
  simple_override(Shape, "read_brep", Exchange.ExchangeBasic.read_brep)
  simple_override(Shape, "write_brep", lambda self, path: Exchange.ExchangeBasic.write_brep (self, path))
  
  for name in re.findall(r"[\w_]+", "vector, Shape"):
    export(name, locals()[name])
  for name in brep_typenames:
    export(name, globals()[name])
