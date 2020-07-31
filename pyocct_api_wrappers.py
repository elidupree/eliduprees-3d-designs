import re

import importlib


def setup(wrap, unwrap, export, override_attribute):
  def simple_override (c, name, value):
    override_attribute(c, name, lambda original: value)
  #import pkgutil
  #import OCCT
  #modules = [module.name for module in pkgutil.iter_modules(OCCT.__path__)]
  modules = re.findall(r"[\w_]+", "Exchange, TopoDS, gp, TopAbs, BRep, BRepBuilderAPI, BRepCheck, Geom, TColStd, TColgp")
  for name in modules:
    globals() [name] = wrap (importlib.import_module ("OCCT."+name))
    
  ExchangeBasic = Exchange.ExchangeBasic
  
  exported_locals = []
  def export_locals(names):
    for match in re.finditer(r"[\w_]+", names):
      exported_locals.append(match.group(0))
      
  default_tolerance = 1e-6
  
  ################################################################
  #######################  Type utils  ###########################
  ################################################################
  
  def make_Array1(original):
    def derived(cls, values):
      result = original (0, len(values) - 1)
      for index, value in enumerate (values):
        result.SetValue (index, value)
      return result
    return classmethod(derived)
    
  def make_Array2(original):
    def derived(cls, rows):
      num_rows = len (rows)
      num_columns = len (rows[0])
      if any(len (row) != num_columns for row in rows):
        raise RuntimeError (f"inconsistent numbers of columns in Array2OfPnt constructor: {rows}")
      result = original (0, num_rows-1, 0, num_columns-1)
      for row_index, row in enumerate (rows):
        for column_index, value in enumerate (row):
          result.SetValue (row_index, column_index, value)
      #print (result.NbRows(), result.NbColumns())
      return result
    return classmethod(derived)
  
  Array1OfReal = TColStd.TColStd_Array1OfReal
  override_attribute(Array1OfReal, "__new__", make_Array1)
  Array2OfReal = TColStd.TColStd_Array2OfReal
  override_attribute(Array2OfReal, "__new__", make_Array2)
  Array1OfInteger = TColStd.TColStd_Array1OfInteger
  override_attribute(Array1OfInteger, "__new__", make_Array1)
  Array2OfPnt = TColgp.TColgp_Array2OfPnt
  override_attribute(Array2OfPnt, "__new__", make_Array2)
  
  ################################################################
  ######################  Vector/etc.  ###########################
  ################################################################
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
  simple_override(Point, "__sub__", lambda self, other: Vector(other, self) if isinstance(other, Point) else self.Translated (-other))
      
  export_locals ("vector, Vector, Point")
  
  ################################################################
  #####################  Other geometry  #########################
  ################################################################
  
  Surface = Geom.Geom_Surface
  BSplineSurface = Geom.Geom_BSplineSurface
  
  def default_multiplicities(num_poles, degree, periodic):
    if periodic:
      return [1]*num_poles
    else:
      return [degree+1] + [1]*(num_poles - degree - 1) + [degree+1]
  
  def default_knots(num_poles):
    return list(range(num_poles))
  
  class BSplineDimension:
    def __init__(self, num_poles = None, multiplicities = None, knots = None, degree = 1, periodic = False):
      self.explicit_multiplicities = multiplicities
      self.explicit_knots = knots
      self.degree = degree
      self.periodic = periodic
    def multiplicities (self, num_poles):
      if self.explicit_multiplicities is None:
        return default_multiplicities(num_poles, self.degree, self.periodic)
      return self.explicit_multiplicities
    def knots(self, num_poles):
      if self.explicit_knots is None:
        return default_knots(num_poles)
      return self.explicit_knots
  
  def make_BSplineSurface (original):
    def derived(cls, poles, weights = None, u = BSplineDimension(), v = BSplineDimension()):
      num_u = len (poles)
      num_v = len (poles[0])
      
      if weights is None:
        weights = [[1 for value in row] for row in poles]
              
      return original(
        unwrap(Array2OfPnt(poles)),
        unwrap(Array2OfReal(weights)),
        unwrap(Array1OfReal(u.knots(num_u))),
        unwrap(Array1OfReal(v.knots(num_v))),
        unwrap(Array1OfInteger(u.multiplicities(num_u))),
        unwrap(Array1OfInteger(v.multiplicities(num_v))),
        u.degree,
        v.degree,
        u.periodic,
        v.periodic,
      )
    
    return classmethod(derived)
    
  override_attribute(BSplineSurface, "__new__", make_BSplineSurface)
  export_locals ("BSplineSurface, BSplineDimension")
  
  ################################################################
  ####################  BRep Shape types  ########################
  ################################################################
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
    simple_override(c, "ShapeType", lambda self: c)
    #import pprint
    #print(c().wrapped_object.__class__ is c.wrapped_object)
    #pprint.pprint({a:getattr(c().wrapped_object, a, None) for a in dir(c().wrapped_object)})
    #print(c.wrapped_object.__init__, c().wrapped_object.__init__)
    #print(c().write_brep)
    #print(type(c.wrapped_object))
    
    
  for typename in shape_typenames:
    handle_shape_type(typename)
  
  Shape = TopoDS.TopoDS_Shape
  #simple_override(Shape, "read_brep", Exchange.ExchangeBasic.read_brep)
  simple_override(Shape, "write_brep", lambda self, path: Exchange.ExchangeBasic.write_brep (self, path))
  
  def is_shape(obj):
    return isinstance(obj, Shape)
  def read_brep (path):
    return Exchange.ExchangeBasic.read_brep (path)
  def shape_type(original, shape):
    #print("shapetype", shape),
    # note: pyOCCT segfaults when you construct a null shape and call ShapeType on it
    if shape.IsNull():
      return None
    else:
      return shape_types_by_ShapeType[original()]
  def downcast_shape(shape):
    if shape.IsNull():
      return shape
    shapetype = shape_type(shape.ShapeType, shape)
    #print("downcasting", repr(shape), shapetype)
    return shapetype.from_shape (shape)
  
  override_attribute (Shape, "ShapeType", lambda original: lambda self: shape_type(original, shape))
  simple_override(Shape, "__wrap__", downcast_shape)
  
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
      if len(args) == 1 and isinstance(args[0], Surface):
        args = [args[0], default_tolerance]
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
  
  export_locals ("Shape, is_shape, read_brep")
  for name in shape_typenames:
    export(name, globals()[name])
  
  
  ################################################################
  #########################  Exports  ############################
  ################################################################
  for name in exported_locals:
    export(name, locals()[name])
  
  
