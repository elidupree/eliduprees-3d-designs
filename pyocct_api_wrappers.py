import re
import math
import importlib


def setup(wrap, unwrap, export, override_attribute):
  def simple_override (c, name, value):
    override_attribute(c, name, lambda original: value)
  #import pkgutil
  #import OCCT
  #modules = [module.name for module in pkgutil.iter_modules(OCCT.__path__)]
  modules = re.findall(r"[\w_\.]+", "Exchange, TopoDS, TopExp, gp, TopAbs, BRep, BRepPrimAPI, BRepAlgoAPI, BRepBuilderAPI, BRepTools, BRepOffset, BRepOffsetAPI, BRepCheck, Geom, GeomAbs, TColStd, TColgp, , ShapeAnalysis, ShapeUpgrade, Message")
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
  Array1OfPnt = TColgp.TColgp_Array1OfPnt
  override_attribute(Array1OfPnt, "__new__", make_Array1)
  Array2OfPnt = TColgp.TColgp_Array2OfPnt
  override_attribute(Array2OfPnt, "__new__", make_Array2)
  
  
  def make_List(original):
    def derived(cls, values):
      result = original()
      for value in values:
        result.Append(value)
      return result
    return classmethod(derived)
  ListOfShape = TopoDS.TopoDS_ListOfShape
  override_attribute(ListOfShape, "__new__", make_List)
      
  # conveniently allow you to throw together nested lists of shapes
  def recursive_flatten (arguments):
    try:
      return [value for argument in arguments for value in recursive_flatten (argument)]
    except AttributeError:
      return [arguments]
  
  simple_override (Message.Message_Report, "Dump", lambda self, gravity: repr(list(set(alert.GetMessageKey() for alert in self.GetAlerts (gravity)))))
  
  ################################################################
  ######################  Vector/etc.  ###########################
  ################################################################
  Vector = gp.gp_Vec
  Point = gp.gp_Pnt
  Direction = gp.gp_Dir
  Transform = gp.gp_Trsf
  Axis = gp.gp_Ax1
  Axes = gp.gp_Ax2

  
  
  def vector(*args, **kwargs):
    return Vector (*args, **kwargs)

  def make_Vector(original):
    def derived(cls, *args):
      #if type(args[0]) is Point:
      if len(args) == 1 and isinstance(args[0], Vector):
        return args[0]
      if len(args) == 3:
        return original(*(float (value) for value in args))
      return original(*args)
    return classmethod(derived)
  override_attribute(Vector, "__new__", make_Vector)
  
  def Vector_str(self):
    return f"Vector({self.X()}, {self.Y()}, {self.Z()})"
  def Point_str(self):
    return f"Point({self.X()}, {self.Y()}, {self.Z()})"
  def Direction_str(self):
    return f"Direction({self.X()}, {self.Y()}, {self.Z()})"
  def Vector_index(self, index):
    if index == 0:
      return self.X()
    if index == 1:
      return self.Y()
    if index == 2:
      return self.Z()
    raise IndexError("point/vector can only be indexed with 0-2")
  
  simple_override(Vector, "__str__", Vector_str)
  simple_override(Vector, "__repr__", Vector_str)
  simple_override(Point, "__str__", Point_str)
  simple_override(Point, "__repr__", Point_str)
  simple_override(Direction, "__str__", Direction_str)
  simple_override(Direction, "__repr__", Direction_str)
  
  simple_override(Vector, "__getitem__", Vector_index)
  simple_override(Point, "__getitem__", Vector_index)
  simple_override(Direction, "__getitem__", Vector_index)
  
  simple_override(Vector, "Translated", lambda self, other: self + other)
  simple_override(Vector, "__neg__", lambda self: self * -1)
  
    
    
  simple_override(Point, "__add__", lambda self, other: self.Translated (other))
  simple_override(Point, "__sub__", lambda self, other: Vector(other, self) if isinstance(other, Point) else self.Translated (other*-1))
  
  
  def make_Transform(original):
    def derived(cls, a=vector(1,0,0),b=vector(0,1,0),c=vector(0,0,1),d=vector(0,0,0)):
      if isinstance(a, gp.gp_Trsf2d):
        return original(a)
        
      result = original()
      result.SetValues(
        a[0], b[0], c[0], d[0],
        a[1], b[1], c[1], d[1],
        a[2], b[2], c[2], d[2],
      )
      return result
      
    return classmethod(derived)
  override_attribute(Transform, "__new__", make_Transform)
  simple_override(Transform, "__matmul__", lambda self, other: other.Multiplied(self))
  simple_override(Transform, "Inverse", Transform.Inverted)
  
  for transformable in [Vector, Point]:
    simple_override(transformable, "__matmul__", lambda self, other: self.Transformed(other))
    
  def Mirror(argument):
    if isinstance (argument, Direction):
      argument = Axes (Point(), argument)
    transform = Transform()
    transform.SetMirror(argument)
    return transform
    
  def Translate (*args):
    return Transform (
      vector(1,0,0),
      vector(0,1,0),
      vector(0,0,1),
      vector(*args)
    )
    
  def Rotate(axis, *, radians=None, degrees=None):
    if degrees:
      radians = degrees * math.tau/360
    transform = Transform()
    transform.SetRotation(axis, radians)
    return transform
  
  def Transform_str (self):
    return "Transform[\n"+"\n".join(
      ", ".join(str(self.Value(row + 1, column + 1)) for column in range (4))
    for row in range(3))+"]"
  
  simple_override(Transform, "__str__", Transform_str)
  simple_override(Transform, "__repr__", Transform_str)
  
  export_locals ("vector, Vector, Point, Direction, Transform, Axis, Axes, Mirror, Translate, Rotate")
  
  ################################################################
  #####################  Other geometry  #########################
  ################################################################
  
  
  Circle = Geom.Geom_Circle
  Plane = Geom.Geom_Plane
  
  Surface = Geom.Geom_Surface
  BSplineSurface = Geom.Geom_BSplineSurface
  BSplineCurve = Geom.Geom_BSplineCurve
  
  def default_multiplicities(num_poles, degree, periodic):
    if periodic:
      return [1]*(num_poles+1)
    else:
      return [degree+1] + [1]*(num_poles - degree - 1) + [degree+1]
  
  def default_knots(num_multiplicities):
    return list(range(num_multiplicities))
  
  class BSplineDimension:
    def __init__(self, *, num_poles = None, multiplicities = None, knots = None, degree = 3, periodic = False):
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
        return default_knots(len(self.multiplicities(num_poles)))
      return self.explicit_knots
  
  def make_BSplineSurface (original):
    def derived(cls, poles, u = BSplineDimension(), v = BSplineDimension(), *, weights = None):
      num_u = len (poles)
      num_v = len (poles[0])
      
      if weights is None:
        weights = [[1 for value in row] for row in poles]
      #print(num_u, u.knots(num_u), u.multiplicities(num_u))
      return original(
        Array2OfPnt(poles),
        Array2OfReal(weights),
        Array1OfReal(u.knots(num_u)),
        Array1OfReal(v.knots(num_v)),
        Array1OfInteger(u.multiplicities(num_u)),
        Array1OfInteger(v.multiplicities(num_v)),
        u.degree,
        v.degree,
        u.periodic,
        v.periodic,
      )
    
    return classmethod(derived)
  
  def make_BSplineCurve (original):
    def derived(cls, poles, u = BSplineDimension(), *, weights = None):
      num_u = len (poles)
      
      if weights is None:
        weights = [1 for value in poles]
      print(num_u, len(u.knots(num_u)), len(u.multiplicities(num_u)))
      return original(
        Array1OfPnt(poles),
        Array1OfReal(weights),
        Array1OfReal(u.knots(num_u)),
        Array1OfInteger(u.multiplicities(num_u)),
        u.degree,
        u.periodic,
      )
    
    return classmethod(derived)

    
  override_attribute(BSplineSurface, "__new__", make_BSplineSurface)
  override_attribute(BSplineCurve, "__new__", make_BSplineCurve)
  export_locals (" Circle, Plane, BSplineCurve, BSplineSurface, BSplineDimension")
  
  ################################################################
  ####################  BRep Shape types  ########################
  ################################################################
  def subshapes (shape, subshape_type):
    explorer = TopExp.TopExp_Explorer(shape, subshape_type.ShapeEnum)
    result = []
    while explorer.More():
      result.append (explorer.Current())
      explorer.Next()
    return result
  
  shape_typenames = ["Vertex", "Edge", "Wire", "Face", "Shell", "Solid", "CompSolid", "Compound"]
  shape_typename_plurals = ["Vertices", "Edges", "Wires", "Faces", "Shells", "Solids", "CompSolids", "Compounds"]
  shape_types_by_ShapeType = {}
  def handle_shape_type(typename):
    c = getattr(TopoDS, f"TopoDS_{typename}")
    from_shape = getattr(TopoDS.TopoDS, f"{typename}_")
    enum_value = getattr (TopAbs.TopAbs_ShapeEnum, "TopAbs_"+ typename.upper())
    shape_types_by_ShapeType [enum_value] = c
    globals() [typename] = c
    simple_override(c, "from_shape", from_shape)
    simple_override(c, "ShapeEnum", enum_value)
    #simple_override(c, "read_brep", lambda path: from_shape(Shape.read_brep (path)))
    simple_override(c, "write_brep", lambda self, path: Exchange.ExchangeBasic.write_brep (self, path))
    simple_override(c, "ShapeType", lambda self: c)
    simple_override(c, "__matmul__", lambda self, matrix: BRepBuilderAPI.BRepBuilderAPI_Transform(self, matrix).Shape())
    #simple_override(c, "__add__", lambda self, v: self @ Translate(v))

    def handle_subtype(subtype, plural):
      simple_override(c, plural, lambda self: subshapes (self, subtype))
    for (other_type, plural) in zip (shape_typenames, shape_typename_plurals):
      if other_type == typename:
        break
      handle_subtype(globals() [other_type], plural)
    
    
  for typename in shape_typenames:
    handle_shape_type(typename)
    
  simple_override(Vertex, "Point", lambda self: BRep.BRep_Tool.Pnt_(self))
  simple_override(Vertex, "__getitem__", lambda self, index: Vector_index(self.Point(), index))
  simple_override(Face, "OuterWire", BRepTools.BRepTools.OuterWire_)
  
  
  
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
  
  def shape_valid(shape):
    return BRepCheck.BRepCheck_Analyzer(shape).IsValid()
  def check_shape(shape):
    a = BRepCheck.BRepCheck_Analyzer(shape)
    if not a.IsValid():
      raise RuntimeError(f'Invalid shape (detected by analyzer) {[str(b).replace("BRepCheck_Status.BRepCheck_", "") for b in a.Result(shape).Status()]}')
  
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
    def derived(cls, *edges_or_wires):
      edges_or_wires = recursive_flatten(edges_or_wires)
      builder = BRepBuilderAPI.BRepBuilderAPI_MakeWire()
      for item in edges_or_wires:
        builder.Add (item)
      if not builder.IsDone():
        raise RuntimeError("Invalid wire (detected by builder)")
      result = builder.Wire()
      check_shape(result)
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
      check_shape(result)
      return result
    return classmethod(derived)
  override_attribute(Face, "__new__", make_Face)
  
  def make_Shell(original):
    def derived(cls, *faces):
      faces = recursive_flatten(faces)
      shell = original()
      builder = BRep.BRep_Builder()
      #print ("builder created")
      builder.MakeShell(shell)
      #print ("Shell made?")
      for face in faces:
        #print ("adding face", face)
        if not isinstance(face, Face):
          raise RuntimeError(f"adding non-face to shell: {face}")
        builder.Add (shell, face)
      #print ("done adding faces")
      if not shape_valid(shell):
        shell = ShapeUpgrade.ShapeUpgrade_ShellSewing().ApplySewing(shell)
      check_shape(shell)
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
      check_shape(result)
      return result
    return classmethod(derived)
  override_attribute(Solid, "__new__", make_Solid)
  
  def make_Compound(original):
    def derived(cls, *shapes):
      shapes = recursive_flatten(shapes)
      compound = original()
      builder = BRep.BRep_Builder()
      #print ("builder created")
      builder.MakeCompound(compound)
      #print ("Compound made?")
      for shape in shapes:
        #print ("adding shape", face)
        builder.Add (compound, shape)
      #print ("done adding faces")
      check_shape(compound)
      return compound
    return classmethod(derived)
  override_attribute(Compound, "__new__", make_Compound)
  
  export_locals ("Shape, is_shape, read_brep")
  for name in shape_typenames:
    export(name, globals()[name])
  
  
  ################################################################
  #####################  BRep algorithms  ########################
  ################################################################
  
  MakeThickSolid = BRepOffsetAPI.BRepOffsetAPI_MakeThickSolid
  
  JoinArc = GeomAbs.GeomAbs_JoinType.GeomAbs_Arc
  JoinIntersection = GeomAbs.GeomAbs_JoinType.GeomAbs_Intersection
  ModeSkin = BRepOffset.BRepOffset_Mode.BRepOffset_Skin
  
  def thicken_shell_or_face (shape, offset, join = JoinArc):
    print ("note: thicken_shell_or_face is actually broken")
    builder = BRepOffsetAPI.BRepOffsetAPI_MakeThickSolid(shape, ListOfShape(), offset, default_tolerance, ModeSkin, False, False, join)
    return builder.Shape()
    
  def thicken_solid (shape, removed_faces, offset, join = JoinArc):
    builder = BRepOffsetAPI.BRepOffsetAPI_MakeThickSolid(shape, ListOfShape(removed_faces), offset, default_tolerance, BRepOffset.BRepOffset_Mode.BRepOffset_Skin, False, False, join)
    return builder.Shape()
    
  def Offset (shape, offset,*, tolerance = default_tolerance, mode = ModeSkin, join = JoinArc, fill = False):
    builder = BRepOffsetAPI.BRepOffsetAPI_MakeOffsetShape()
    builder.PerformByJoin (shape, offset, tolerance, mode, False, False, join)
    result = builder.Shape()
    if not fill:
      return result
      
    image = builder.MakeOffset().OffsetEdgesFromShapes()
    #faces = shape.Faces() + result.Faces()
    shells = [shape, result]
    free_check = ShapeAnalysis.ShapeAnalysis_FreeBoundsProperties (shape)
    free_check.Perform()
    for free_bound in free_check.ClosedFreeBounds():
      #print("free bound")
      free_wire = free_bound.FreeBound()
      offset_wire = Wire (image.Image (edge) for edge in free_wire.Edges())
      loft = Loft(free_wire, offset_wire)
      #faces.extend(loft.Faces())
      shells.append (loft)
    #print (faces)
    #shell = Shell (faces)
    sewing = BRepBuilderAPI.BRepBuilderAPI_Sewing(tolerance)
    for shell in shells:
      sewing.Add(shell)
    sewing.Perform()
    complete_shell = sewing.SewedShape()
    print (complete_shell)
    return Solid (complete_shell)
        
      
    
    
  def Loft (*sections, solid = False, ruled = False):
    sections = recursive_flatten (sections)
    builder = BRepOffsetAPI.BRepOffsetAPI_ThruSections(solid, ruled)
    for section in sections:
      if isinstance (section, Vertex):
        builder.AddVertex (section)
      else:
        builder.AddWire (section)
    builder.Build()
    return builder.Shape()

  
  def finish_Boolean (builder):
    builder.Build()
    if not builder.IsDone():
      raise RuntimeError (f"Union failed {builder.GetReport().Dump (Message.Message_Gravity.Message_Fail)} {builder.GetReport().Dump (Message.Message_Gravity.Message_Alarm)} {builder.GetReport().Dump (Message.Message_Gravity.Message_Warning)}")
    return builder.Shape()
  
  def Union (*shapes):
    shapes = recursive_flatten (shapes)
    builder = BRepAlgoAPI.BRepAlgoAPI_Fuse()
    builder.SetArguments (ListOfShape (shapes [:1]))
    builder.SetTools (ListOfShape (shapes [1:]))
    return finish_Boolean (builder)
    
  def Intersection (first, second):
    builder = BRepAlgoAPI.BRepAlgoAPI_Common(first, second)
    return finish_Boolean (builder)
  
  def Difference (first, second):
    builder = BRepAlgoAPI.BRepAlgoAPI_Cut()
    builder.SetArguments (ListOfShape (recursive_flatten (first)))
    builder.SetTools (ListOfShape (recursive_flatten (second)))
    return finish_Boolean (builder)
  
  
  def Box (*args):
    return BRepPrimAPI.BRepPrimAPI_MakeBox (*args).Shape()
  
  def HalfSpace(point, direction):
    plane = Plane (point, direction)
    reference = point + Vector (direction)
    return BRepPrimAPI.BRepPrimAPI_MakeHalfSpace(Face(plane), reference).Solid()
    
  export_locals ("thicken_shell_or_face, thicken_solid, Box, HalfSpace, Loft, Offset, Union, Intersection, Difference, JoinArc, JoinIntersection")
  

  
  ################################################################
  #########################  Exports  ############################
  ################################################################
  for name in exported_locals:
    export(name, locals()[name])
  
  
