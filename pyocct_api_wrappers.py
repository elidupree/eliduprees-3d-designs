'''

Capitalization convention:
– because I use Dragon, capitalizing things is extra work. Thus, single-word methods should normally be used lowercase.
– The types and functions from this module are uppercase, because I use a glob import and I don't want to have collisions with variables, and "cap X" is easier to say than "API dot X". One exception is "vector" because it is extremely commonly used
– in this file, by convention, methods which are not intended to be used in other files – only used as an implementation detail for wrappers – may be written in their original uppercase

'''


import re
import math
import importlib
import os.path
import functools


def setup(Wrapper, wrap, unwrap, do_export, override_attribute, SerializeAsVars, register_file_read):
  def simple_override (c, name, value):
    override_attribute(c, name, lambda original: value)
  #import pkgutil
  #import OCCT
  #modules = [module.name for module in pkgutil.iter_modules(OCCT.__path__)]
  modules = re.findall(r"[\w_\.]+", "Exchange, TopoDS, TopExp, gp, TopAbs, BOPTools, BRep, BRepMesh, BRepPrimAPI, BRepAlgoAPI, BRepFilletAPI, BRepBuilderAPI, BRepTools, BRepOffset, BRepOffsetAPI, BRepCheck, BRepLib, Geom, GeomAbs, GeomAPI, GeomLProp, TColStd, TColgp, , ShapeAnalysis, ShapeUpgrade, Message, ChFi2d, StlAPI, Bnd, BRepBndLib, GeomAdaptor,GCPnts,RWStl, IntTools,STEPControl")
  for name in modules:
    globals() [name] = wrap (importlib.import_module ("OCCT."+name))
    
  ExchangeBasic = Exchange.ExchangeBasic
  
  def export (function):
    do_export (function.__name__, function)
    return function
  
  exported_locals = []
  def export_locals(names):
    for match in re.finditer(r"[\w_]+", names):
      exported_locals.append(match.group(0))
      
  default_tolerance = 1e-6
  
  ################################################################
  #######################  Type utils  ###########################
  ################################################################
  
  class ArbitraryFields():
    def __init__(self, **kwargs):
      for key, value in kwargs.items():
        setattr(self, key, value)
  
  def make_Array1(original):
    def derived(cls, values):
      result = original (1, len(values))
      for index, value in enumerate (values):
        result.SetValue (index + 1, value)
      return result
    return classmethod(derived)
    
  def make_Array2(original):
    def derived(cls, rows):
      num_rows = len (rows)
      num_columns = len (rows[0])
      if any(len (row) != num_columns for row in rows):
        raise RuntimeError (f"inconsistent numbers of columns in Array2OfPnt constructor: {rows}")
      result = original (1, num_rows, 1, num_columns)
      for row_index, row in enumerate (rows):
        for column_index, value in enumerate (row):
          result.SetValue (row_index + 1, column_index + 1, value)
      #print (result.NbRows(), result.NbColumns())
      return result
    return classmethod(derived)
  
  makers = {1: make_Array1, 2: make_Array2}
  modules = {
    "TColStd": "Integer, Real, Boolean",
    "TColgp": "Pnt, Vec",
  }
  
  def do_array (module, item, dimensions, prefix):
    #try: 
      array = getattr (globals() [module], f"{module}_{prefix}Array{dimensions}Of{item}")
      globals() [f"{prefix}Array{dimensions}Of{item}"] = array
      override_attribute(array, "__new__", makers [dimensions])
      if dimensions==1: simple_override(array, "__len__", lambda self: self.Length())
    #except AttributeError:
    #  pass
  
  for module, items in modules.items():
    for match in re.finditer(r"[\w]+", items):
      for dimensions in range (1, 3):
        for prefix in ["", "H"]:
          do_array (module, match.group (0), dimensions, prefix)
  
  
  def make_List(original):
    def derived(cls, values):
      result = original()
      for value in values:
        result.append(value)
      return result
    return classmethod(derived)
  ListOfShape = TopoDS.TopoDS_ListOfShape
  override_attribute(ListOfShape, "__new__", make_List)
  
  @export
  def flatten (arguments):
    assert(type(arguments) is list)
    return [b for a in arguments for b in a]
      
  # conveniently allow you to throw together nested lists of shapes
  @export
  def recursive_flatten (arguments):
    assert(type(arguments) is not str)
    if isinstance(arguments, Wrapper):
      return [arguments]
    try:
      return [value for argument in arguments for value in recursive_flatten (argument)]
    except AttributeError:
      return [arguments]
  
  simple_override (Message.Message_Report, "dump", lambda self, gravity: repr(list(set(alert.GetMessageKey() for alert in self.GetAlerts (gravity)))))
    
  ################################################################
  ##################  Convenience functions  #####################
  ################################################################
  
  def pairs(points, loop=False):
    points = iter(points)
    first = prev = next(points)
    for point in points:
      yield (prev, point)
      prev = point
    if loop:
      yield (prev, first)
    
  def all_equal(iterable):
    i = iter(iterable)
    try:
      first = next(i)
    except StopIteration:
      return True
    return all(v == first for v in i)
  
  def subdivisions (start, end, *, amount = None, max_length = None, require_parity = None):
    delta = end - start

    if amount is None and max_length is None:
      raise RuntimeError (f"subdivisions() must specify either amount or max_length")

    if max_length is not None:
      distance = delta.magnitude() if isinstance (delta, Vector) else abs (delta)
      required = math.ceil (distance/max_length) + 1
      if require_parity is not None:
        if required % 2 != require_parity:
          required += 1
      amount = max ((amount or 0), required)
    
    if amount < 2:
      raise RuntimeError (f"subdivisions() must have enough amount to include at least the start point and end point")
      
    factor = 1/(amount - 1)
    return [start + delta*i*factor for i in range(amount)]
  
  @export
  def smootherstep(x, left=0, right=1):
    f = (x - left) / (right - left)
    if f <= 0: return 0
    if f >= 1: return 1
    return f*f*f*(f*(f*6 - 15) + 10 );
  
  export_locals ("pairs, all_equal, subdivisions")
  
  ################################################################
  ######################  Vector/etc.  ###########################
  ################################################################
  Vector = gp.gp_Vec
  Point = gp.gp_Pnt
  Direction = gp.gp_Dir
  Transform = gp.gp_Trsf
  GeometryTransform = gp.gp_GTrsf
  Axis = gp.gp_Ax1
  Axes = gp.gp_Ax2

  Vector2 = gp.gp_Vec2d
  Point2 = gp.gp_Pnt2d
  Direction2 = gp.gp_Dir2d
  
  Up = Direction (0, 0, 1)
  Down = Direction (0, 0, -1)
  Left = Direction (-1, 0, 0)
  Right = Direction (1, 0, 0)
  Front = Direction (0, -1, 0)
  Back = Direction (0, 1, 0)
  
  Origin = Point (0, 0, 0)
  
  def vector(*args, **kwargs):
    return Vector (*args, **kwargs)

  def make_Vector(original):
    def derived(cls, *args, all=None, xy=None, yz=None, xz=None):
      #if type(args[0]) is Point:
      if len(args) == 1 and isinstance(args[0], Vector):
        args = [args[0].XYZ()]
      if len(args) == 2 and (isinstance(args[0], float) or isinstance(args[0], int)):
        args = [args[0], args[1], 0]
      if all is not None:
        args = [all, all, all]
      if xy is not None:
        args = [xy, xy, 0]
      if yz is not None:
        args = [0, yz, yz]
      if xz is not None:
        args = [xz, 0, xz]
      if len(args) == 3:
        return original(*(float (value) for value in args))
      return original(*args)
    return classmethod(derived)
  override_attribute(Vector, "__new__", make_Vector)
  
  def make_Direction(original):
    def derived(cls, *args):
      if len(args) == 1 and isinstance(args[0], Direction):
        args = [args[0].XYZ()]
      if len(args) == 2 and isinstance(args[0], Point) and isinstance(args[1], Point):
        args = [Vector(*args)]
      return original(*args)
    return classmethod(derived)
  override_attribute(Direction, "__new__", make_Direction)
  
  def make_Point(original):
    def derived(cls, *args):
      if len(args) == 1 and isinstance(args[0], Point):
        args = [args[0].XYZ()]
      if len(args) == 2:
        args = (args[0], args[1], 0)
      return original(*args)
    return classmethod(derived)
  override_attribute(Point, "__new__", make_Point)
  
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
  def Vector3_coords(self):
    return (self.X(), self.Y(), self.Z())
  def Vector2_coords(self):
    return (self.X(), self.Y())
  def Vector_setindex(self, index, value):
    if index == 0:
      return self.SetX(value)
    if index == 1:
      return self.SetY(value)
    if index == 2:
      return self.SetZ(value)
    raise IndexError("point/vector can only be indexed with 0-2")
  def Vector_withindex(self, index, value):
    result = self.clone()
    result[index] = value
    return result
    
  def vector_if_direction (value):
    if isinstance (value, Direction):
      return Vector (value)
    return value
  
  def represent (whatever, function):
    simple_override(whatever, "__str__", function)
    simple_override(whatever, "__repr__", function)
    simple_override(whatever, "__format__", lambda self, _: function(self))
  represent (Vector, Vector_str)
  represent (Point, Point_str)
  represent (Direction, Direction_str)

  for whatever in [Vector2, Point2, Direction2]:
    simple_override(whatever, "coords", Vector2_coords)
    simple_override(whatever, "__len__", lambda self: 2)
  for whatever in [Vector, Point, Direction]:
    simple_override(whatever, "coords", Vector3_coords)
    simple_override(whatever, "__len__", lambda self: 3)
  for whatever in [Vector, Point, Direction, Vector2, Point2, Direction2]:
    simple_override(whatever, "__getitem__", Vector_index)
    simple_override(whatever, "__setitem__", Vector_setindex)
    simple_override(whatever, "__iter__", lambda self: iter(self.coords()))
    simple_override(whatever, "clone", lambda self: wrap(unwrap(self).__class__)(self))
    simple_override(whatever, "with_coordinate", Vector_withindex)
    simple_override(whatever, "with_x", lambda self, value: self.with_coordinate(0, value))
    simple_override(whatever, "with_y", lambda self, value: self.with_coordinate(1, value))
    simple_override(whatever, "with_z", lambda self, value: self.with_coordinate(2, value))

  
  simple_override(Vector, "translated", lambda self, other: self + other)
  simple_override(Vector, "__neg__", lambda self: self * -1)
  simple_override(Vector, "length", lambda self: self.magnitude())
  override_attribute (Vector, "dot", lambda original: lambda self, other: original (vector_if_direction (other)))
  simple_override(Vector, "cross", lambda self, other: self.Crossed(vector_if_direction (other)))
  
  simple_override(Direction, "__mul__", lambda self, other: Vector(self) * other)
  simple_override(Direction, "__truediv__", lambda self, other: Vector(self) / other)
  def Direction_cross(self, other):
    if isinstance (other, Direction) and self.dot (other) == 0:
      return self.Crossed(other)
    else:
      return Vector(self).Crossed(vector_if_direction (other))
  simple_override(Direction, "cross", Direction_cross)
  
  simple_override(Vector, "__rmul__", lambda self, other: self * other)
  simple_override(Vector, "__radd__", lambda self, other: self + other)
  simple_override(Direction, "__rmul__", lambda self, other: self * other)
    
  simple_override(Point, "__add__", lambda self, other: self.translated (other))
  simple_override(Point, "__sub__", lambda self, other: Vector(other, self) if isinstance(other, Point) else self.translated (other*-1))
  
  def Between (first, second, fraction = 0.5):
    #return first + Vector (first, second)*fraction
    return first + (second - first) * fraction
  
  simple_override(Direction, "__add__", lambda self, other: Vector(self) + vector_if_direction (other))
  simple_override(Direction, "__sub__", lambda self, other: Vector(self) - vector_if_direction (other))
  simple_override(Direction, "__neg__", lambda self: Direction(-self[0], -self[1], -self[2]))
  
  def require_instance (value, t):
    if not isinstance(value, t):
      raise TypeError (f"Value must be an instance of {t}, but was {value}")
      
  def vector_projected(self, direction):
    require_instance (direction, Direction)
    return direction * self.dot (direction)
  simple_override(Vector, "projected", vector_projected)
  simple_override(Vector, "projected_perpendicular", lambda self, direction: self - self.projected (direction))
  
  def point_projected (self, onto, by = None):
    if isinstance (onto, Plane):
      normal = onto.normal() 
      if by is None:
        by = normal
      distance = Vector (self, onto.location()).dot (normal)
      
      return self + (by/by.dot (normal))*distance
    raise RuntimeError (f"don't know how to project point onto {onto}")
      
  simple_override(Point, "projected", point_projected)
  
  def make_Transform(original):
    def derived(cls, a=vector(1,0,0),b=vector(0,1,0),c=vector(0,0,1),d=vector(0,0,0)):
      if isinstance(a, gp.gp_Trsf2d):
        return original(a)
        
      result = original()
      values = [
        a[0], b[0], c[0], d[0],
        a[1], b[1], c[1], d[1],
        a[2], b[2], c[2], d[2],
      ]
      result.SetValues(*values)
      result_values = [result.value(row + 1, column + 1) for row in range(3) for column in range (4)]
      if any(abs(a - b) > default_tolerance for a,b in zip(values, result_values)):
        raise RuntimeError (f"it's no good use Transform when it automatically adjusts the values (original: {values}, adjusted: {result_values})")
      return result
      
    return classmethod(derived)
  
  def make_GeometryTransform(original):
    def derived(cls, a=vector(1,0,0),b=vector(0,1,0),c=vector(0,0,1),d=vector(0,0,0)):
      if isinstance(a, gp.gp_GTrsf2d) or isinstance(a, Transform):
        return original(a)
        
      result = original()
      values = [
        a[0], b[0], c[0], d[0],
        a[1], b[1], c[1], d[1],
        a[2], b[2], c[2], d[2],
      ]
      indices = [(row+1, column +1) for row in range(3) for column in range (4)]
      for value, index in zip (values, indices):
        result.SetValue(*index, value)
      return result
      
    return classmethod(derived)
    
  override_attribute(Transform, "__new__", make_Transform)
  simple_override(Transform, "__matmul__", lambda self, other: other.Multiplied(self))
  simple_override(Transform, "inverse", lambda self: self.Inverted())
  override_attribute(GeometryTransform, "__new__", make_GeometryTransform)
  simple_override(GeometryTransform, "__matmul__", lambda self, other: other.Multiplied(self))
  simple_override(GeometryTransform, "inverse", lambda self: self.Inverted())
    
  def transform_direction (self, transform):
    if abs(transform.ScaleFactor()) != 1.0:
      raise RuntimeError (f"Tried to transform a direction with {transform}, which has a non-unit scale factor of {transform.ScaleFactor()}. If this was intentional, either use Transformed explicitly (to get a Direction) or convert to Vector first (so the magnitude can be adjusted)")
    return self.Transformed (transform)
  simple_override(Direction, "__matmul__", transform_direction)
    
  def Mirror(argument):
    if isinstance (argument, Direction):
      argument = Axes (Point(), argument)
    transform = Transform()
    transform.SetMirror(argument)
    return transform
  Reflect = Mirror
  def Translate (*args):
    return Transform (
      vector(1,0,0),
      vector(0,1,0),
      vector(0,0,1),
      vector(*args)
    )

  def Rotate(axis, angle=None, *, radians=None, degrees=None):
    if isinstance (axis, Direction):
      axis = Axis (Origin, axis)
    if degrees is not None:
      angle = Degrees(degrees)
    if radians is not None:
      angle = Radians(radians)
    if not isinstance(angle, Angle):
      raise RuntimeError("must specify an Angle for Rotate")
    transform = Transform()
    transform.SetRotation(axis, angle.radians)
    return transform
    
  def Scale(ratio,*, center =Origin):
    transform = Transform()
    transform.SetScale (center, ratio)
    return transform
  
  def Transform_str (self):
    return "Transform[\n"+"\n".join(
      ", ".join(str(self.value (row + 1, column + 1)) for column in range (4))
    for row in range(3))+"]"
  def GeometryTransform_str (self):
    return "GeometryTransform[\n"+"\n".join(
      ", ".join(str(self.value (row + 1, column + 1)) for column in range (4))
    for row in range(3))+"]"
  
  represent (Transform, Transform_str)
  represent (GeometryTransform, GeometryTransform_str)
  

  
  export_locals ("vector, Vector, Point, Direction, Vector2 Point2 Direction2,  Transform, GeometryTransform, Axis, Axes, Mirror, Reflect Translate, Rotate, Scale, Up, Down, Left, Right, Front, Back, Origin, Between")
  
  ################################################################
  #####################  Other geometry  #########################
  ################################################################
  
  
  Circle = Geom.Geom_Circle
  Plane = Geom.Geom_Plane
  Line = Geom.Geom_Line
  Bounds =Bnd.Bnd_Box
  
  Curve = Geom.Geom_Curve
  Surface = Geom.Geom_Surface
  BSplineSurface = Geom.Geom_BSplineSurface
  BSplineCurve = Geom.Geom_BSplineCurve
  BezierCurve = Geom.Geom_BezierCurve
  TrimmedCurve = Geom.Geom_TrimmedCurve
  
  simple_override(Plane, "normal", lambda self, *args: self.Axis().Direction())
  simple_override (Bounds, "max", lambda self: self.CornerMax())
  simple_override (Bounds, "min", lambda self: self.CornerMin())
  simple_override (Bounds, "size", lambda self: self.max() - self.min())
  
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

  def dimension_of_BSplineCurve(curve):
    return BSplineDimension(multiplicities=curve.multiplicities(), knots=curve.knots(), degree=curve.degree(), periodic=curve.IsPeriodic())

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
    def derived(cls, poles, u = None, *, weights = None, **kwargs):
      if u is None:
        u = BSplineDimension(**kwargs)
      num_u = len (poles)
      
      if weights is None:
        weights = [1 for value in poles]
      #print(num_u, len(u.knots(num_u)), len(u.multiplicities(num_u)))
      return original(
        Array1OfPnt(poles),
        Array1OfReal(weights),
        Array1OfReal(u.knots(num_u)),
        Array1OfInteger(u.multiplicities(num_u)),
        u.degree,
        u.periodic,
      )
    
    return classmethod(derived)
      
  def make_BezierCurve (original):
    def derived(cls, poles, weights = None):
      num_u = len (poles)
      
      if weights is None:
        return original(Array1OfPnt(poles))
      else:
        return original(Array1OfPnt(poles), Array1OfReal(weights))

    return classmethod(derived)
    
  override_attribute(BSplineSurface, "__new__", make_BSplineSurface)
  override_attribute(BSplineCurve, "__new__", make_BSplineCurve)
  override_attribute(BezierCurve, "__new__", make_BezierCurve)
  override_attribute(BSplineCurve, "poles", lambda original: lambda self: [a for a in original()])
  override_attribute(BSplineCurve, "knots", lambda original: lambda self: [a for a in original()])
  override_attribute(BSplineCurve, "multiplicities", lambda original: lambda self: [a for a in original()])
  simple_override(BSplineCurve, "dimension", dimension_of_BSplineCurve)

  def BSplineCurve_cartesian_product(ucurve, vcurve):
    upoles = ucurve.poles()
    vpoles = vcurve.poles()
    return BSplineSurface([[up + (vp-Origin) for vp in vpoles] for up in upoles], u = ucurve.dimension(), v = vcurve.dimension())

  def extrude_BSplineCurve(curve, offset, second_offset = None, *, centered = False):
    if centered:
      second_offset = -offset/2
      offset = offset/2
    if second_offset is None:
      second_offset = offset
      offset = Vector()
    return BSplineCurve_cartesian_product(curve, Segment(Origin+offset, Origin+second_offset))

  def map_BSplineCurve_poles(curve, mapper):
    return BSplineCurve([mapper(p) for p in curve.poles()], curve.dimension())

  simple_override(BSplineCurve, "extrude", extrude_BSplineCurve)
  simple_override(BSplineCurve, "cartesian_product", BSplineCurve_cartesian_product)
  simple_override(BSplineCurve, "map_poles", map_BSplineCurve_poles)

  
  def Interpolate (points,*, periodic = False, tolerance = default_tolerance, parameters = None, tangents = None):
    points = HArray1OfPnt (points)
    if parameters is not None:
      builder = GeomAPI.GeomAPI_Interpolate (points, HArray1OfReal (parameters), periodic, tolerance)
    else:
      builder = GeomAPI.GeomAPI_Interpolate (points, periodic, tolerance)
    
    if tangents is not None:
      if len(tangents) == 2:
        # I don't actually know what the Scale argument does, but if you don't say False, the result has unnecessary asymmetry
        builder.Load (*tangents, False)
      else:
        tangent_array = []
        bool_array = []
        for t in tangents:
          if t is None:
            bool_array.append(False)
            tangent_array.append(Vector())
          else:
            bool_array.append(True)
            tangent_array.append(t)
        builder.Load(Array1OfVec(tangent_array), HArray1OfBoolean(bool_array), False)


    
    builder.Perform()
    return builder.Curve()
    
  def curve_parameter_function (function):
    @functools.wraps(function)
    def wrapped(curve, parameter = None, *, distance = None, from_parameter = 0, closest = None, on = None, x = None, y = None, z = None, min_by = None, max_by = None, **kwargs):
      if x is not None:
        on = Plane(Origin+Right*x, Right)
      if y is not None:
        on = Plane(Origin+Back*y, Back)
      if z is not None:
        on = Plane(Origin+Up*z, Up)

      if on is not None:
        points = curve.intersections(on).points
        if len(points) < 1:
          raise RuntimeError(f"specified 'on', x, y, or z, but there were no such points")
        if max_by is not None:
          if max_by == "x": min_by = "-x"
          elif max_by == "y": min_by = "-y"
          elif max_by == "z": min_by = "-z"
          else: min_by = lambda p: -max_by(p)
        if min_by is not None:
          if min_by == "x": min_by = lambda p: p[0]
          elif min_by == "y": min_by = lambda p: p[1]
          elif min_by == "z": min_by = lambda p: p[2]
          elif min_by == "-x": min_by = lambda p: -p[0]
          elif min_by == "-y": min_by = lambda p: -p[1]
          elif min_by == "-z": min_by = lambda p: -p[2]
          closest = min(points, key = min_by)
        else:
          if len(points) > 1:
            raise RuntimeError(f"specified 'on', x, y, or z, but there were {len(points)} choices; if that's expected, try adding min_by")
          closest = points[0]

      if closest is not None:
        parameter = GeomAPI.GeomAPI_ProjectPointOnCurve (closest, curve).LowerDistanceParameter()
        if False: #exceptions not handled yet
          parameter = min ([
            curve.FirstParameter(), curve.LastParameter()
          ], key = lambda parameter: curve.value (parameter).distance (closest))
      
      if distance is not None:
        adapter = GeomAdaptor.GeomAdaptor_Curve (curve)
        parameter = GCPnts.GCPnts_AbscissaPoint (adapter, distance, from_parameter).Parameter()

      return function(curve, parameter, **kwargs)
    return wrapped
    
  def curve_length (curve, first = None, last = None):
    if first is None: first = curve.FirstParameter()
    if last is None: last = curve.LastParameter()
    adapter = GeomAdaptor.GeomAdaptor_Curve (curve)
    return GCPnts.GCPnts_AbscissaPoint.Length_(adapter, first, last)
    
    
  simple_override (Curve, "length", curve_length)
  simple_override (Curve, "parameter", curve_parameter_function (lambda curve, parameter: parameter))
  simple_override (Curve, "distance", curve_parameter_function (lambda curve, parameter: curve.length(0, parameter)))
  
  class GeomIntersections:
    def __init__(self, *, points=[], curves=[]):
      self.points = points
      self.curves = curves
      
    def point(self):
      if len (self.points) != 1:
        raise RuntimeError (f"assumed that intersection had exactly one point, but it actually had {self.points}")
      return self.points[0]
    
    def curve(self):
      if len (self.curves) != 1:
        raise RuntimeError (f"assumed that intersection had exactly one curve, but it actually had {self.curves}")
      return self.curves[0]
  
  
  def curve_intersections (self, other, tolerance = default_tolerance):
    if isinstance (other, Surface):
      return surface_intersections(other, self)
    '''if isinstance (other, Curve):
      builder = IntTools.IntTools_EdgeEdge (Edge (self), Edge (other))
      builder.Perform()
      print ([(part.VertexParameter1(), part.VertexParameter2()) for part in builder.CommonParts()])'''
    raise RuntimeError (f"don't know how to intersect a curve with {other}")
  def surface_intersections (self, other, tolerance = default_tolerance):
    if isinstance (other, Curve):
      builder = GeomAPI.GeomAPI_IntCS (other, self)
      
      return GeomIntersections(
        points = [builder.Point (index + 1) for index in range ( builder.NbPoints())],
        curves = [builder.Segment (index + 1) for index in range ( builder.NbSegments())],
      )
    if isinstance (other, Surface):
      builder = GeomAPI.GeomAPI_IntSS (self, other, tolerance)
      return GeomIntersections(curves = [builder.Line (index + 1) for index in range ( builder.NbLines())])
    raise RuntimeError (f"don't know how to intersect a surface with {other}")
  def merge_intersections(iss):
    return GeomIntersections(
      points = [p for i in iss for p in i.points],
      curves = [c for i in iss for c in i.curves],
    )

  simple_override (Surface, "intersections", surface_intersections)
  simple_override (Curve, "intersections", curve_intersections)
  
  def surface_parameter (surface, closest):
    analyzer = ShapeAnalysis.ShapeAnalysis_Surface (surface)
    return analyzer.ValueOfUV (closest, default_tolerance)
    
  
  def surface_parameter_function (function):
    @functools.wraps(function)
    def wrapped(surface, parameter = None, *, closest = None, **kwargs):
      if closest is not None:
        parameter = surface_parameter (surface, closest)
      
      if type(parameter) is not list:
        parameter = [parameter[0], parameter[1]]
        
      if len(parameter) != 2:
        parameter = [parameter[0][0], parameter[0][1]]
      
      return function(surface, parameter, **kwargs)
    return wrapped
    

  simple_override (Surface, "parameter", surface_parameter)
  
  override_attribute (Surface, "value", lambda original: surface_parameter_function(lambda surface, parameter: original(*parameter)))
  simple_override (Surface, "position", lambda self, *args, **kwargs: self.value(*args, **kwargs))
  simple_override (Surface, "normal", surface_parameter_function(lambda surface, parameter: GeomLProp.GeomLProp_SLProps(surface, *parameter, 2, default_tolerance).Normal()))
  
  class CurveDerivatives:
    def __init__(self, curve, parameter, *, derivatives = 2):
      self.parameter = parameter
      self.position = curve.value (parameter)
      props = GeomLProp.GeomLProp_CLProps(curve, parameter, derivatives, default_tolerance)
      if derivatives > 0:
        self.velocity = props.D1()
        self.tangent = Direction (self.velocity)
      if derivatives > 1:
        self.acceleration = props.D2()
        putative_normal = self.tangent.cross (self.acceleration).cross (self.tangent)
        if putative_normal.magnitude() > default_tolerance:
          self.normal = Direction(putative_normal)
        else:
          self.normal = None
  
  simple_override (Curve, "derivatives", curve_parameter_function (lambda curve, parameter, **kwargs: CurveDerivatives(curve, parameter, **kwargs)))
  simple_override (Curve, "curvature", curve_parameter_function (lambda curve, parameter: GeomLProp.GeomLProp_CLProps(curve, parameter, 2, default_tolerance).Curvature()))
  override_attribute (Curve, "value", lambda original: curve_parameter_function (lambda curve, parameter: original (parameter)))
  simple_override (Curve, "position", lambda self, *args, **kwargs: self.value(*args, **kwargs))

  
  # def subdivisions (start, end, *, amount = None, max_length = None, require_parity = None):
  def curve_subdivisions(curve, start_distance = None, end_distance = None, *, wrap = None, output = "positions", **kwargs):
    start_args = {}
    end_args = {}
    subdivisions_args = {}
    for k,v in kwargs.items():
      if k.startswith("start_"):
        start_args[k[6:]] = v
      elif k.startswith("end_"):
        end_args[k[4:]] = v
      else:
        subdivisions_args[k] = v
    
    used_defaults = 0
    if start_distance is None:
      if len(start_args) == 0:
        start_distance = 0
        used_defaults += 1
      else:
        start_distance = curve.distance(**start_args)
    
    if end_distance is None:
      if len(end_args) == 0:
        end_distance = curve.length()
        used_defaults += 1
      else:
        end_distance = curve.distance(**end_args)
        
    if curve.IsPeriodic() and wrap is None and used_defaults != 2:
        raise RuntimeError(f"called curve_subdivisions on a periodic curve without specifying wrapping behavior")

    if wrap is None:
      distances = subdivisions(start_distance, end_distance, **subdivisions_args)
    else:
      length = curve.length()
      if wrap == "closest":
        if abs(end_distance - start_distance) > length/2:
          end_distance += length
      elif wrap is True:
        end_distance += length
      elif isinstance(wrap, int):
        end_distance += length*wrap
      elif wrap is False:
        pass
      else:
        raise RuntimeError(f"unknown wrapping behavior `{wrap}`")
      distances = [d % length for d in subdivisions(start_distance, end_distance, **subdivisions_args)]

    if output == "positions":
      return [curve.position(distance = d) for d in distances]
    elif output == "derivatives":
      return [curve.derivatives(distance = d) for d in distances]
    else:
      raise RuntimeError(f"unknown output type `{output}`")
  simple_override (Curve, "subdivisions", curve_subdivisions)
  
  for transformable in [Vector, Point, Curve, Surface]:
    simple_override(transformable, "__matmul__", lambda self, other: self.Transformed(other))
  
  @export
  def Segment(start, end):
    return BSplineCurve([start, end], BSplineDimension(degree=1))
  @export
  def RayIsh(start, direction, length = 9000):
    return Segment(start, start + direction * length)

  export_locals (" Curve, Surface, Circle, Line, Plane, BSplineCurve, BezierCurve, BSplineSurface, BSplineDimension, Interpolate, TrimmedCurve")
  
  ################################################################
  ####################  BRep Shape types  ########################
  ################################################################
  Shape = TopoDS.TopoDS_Shape
  
  def subshapes (shape, subshape_type):
    explorer = TopExp.TopExp_Explorer(shape, subshape_type.ShapeEnum)
    result = []
    while explorer.More():
      result.append (explorer.Current())
      explorer.Next()
    return result
  
  def shape_bounds (self):
    result = Bounds()
    BRepBndLib.BRepBndLib.Add_(self, result)
    return result

  def write_brep(self, path):
    dirname = os.path.dirname(path)
    if dirname != "":
      os.makedirs(os.path.dirname(path), exist_ok=True)
    Exchange.ExchangeBasic.write_brep (self, path)
  
  simple_override(Shape, "bounds", shape_bounds)
  simple_override(Shape, "__matmul__", lambda self, matrix: (BRepBuilderAPI.BRepBuilderAPI_Transform if isinstance (matrix, Transform) else BRepBuilderAPI.BRepBuilderAPI_GTransform)(self, matrix).Shape())
  simple_override(Shape, "write_brep", write_brep)
  simple_override(Shape, "clone", lambda self: BRepBuilderAPI.BRepBuilderAPI_Copy (self).Shape())
  simple_override(Shape, "extrude", lambda self, *args, **kwargs: Extrude (self, *args, **kwargs))
  simple_override(Shape, "cut", lambda self, *args, **kwargs: Difference(self, *args, **kwargs))
  simple_override(Shape, "intersection", lambda self, *args, **kwargs: Intersection(self, *args, **kwargs))
  simple_override(Shape, "offset", lambda self, *args, **kwargs: Offset (self, *args, **kwargs))
  simple_override(Shape, "offset2D", lambda self, *args, **kwargs: Offset2D (self, *args, **kwargs))
  simple_override(Shape, "offset2d", lambda self, *args, **kwargs: Offset2D (self, *args, **kwargs))
  simple_override(Shape, "revolve", lambda self, *args, **kwargs: Revolve (self, *args, **kwargs))
  
  
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
    
    #simple_override(c, "ShapeType", lambda self: c)
    
    #simple_override(c, "__add__", lambda self, v: self @ Translate(v))

    def handle_subtype(subtype_name, plural):
      subtype = globals() [subtype_name]
      simple_override(c, plural.lower(), lambda self: subshapes (self, subtype))
      def assume_singleton (self):
        shapes = subshapes (self, subtype)
        if len (shapes) != 1:
          raise RuntimeError (f"Called {subtype_name.lower()}() on {self}, thereby assuming that it has exactly one {subtype_name}, but in fact it had {len (shapes)} ({shapes})")
        return shapes [0]
      simple_override(c, subtype_name.lower(), assume_singleton)
    for (other_type, plural) in zip (shape_typenames, shape_typename_plurals):
      handle_subtype(other_type, plural)
      if other_type == typename:
        break
    
    
  for typename in shape_typenames:
    handle_shape_type(typename)
    
  simple_override(Vertex, "point", lambda self: BRep.BRep_Tool.Pnt_(self))
  simple_override(Vertex, "__getitem__", lambda self, index: Vector_index(self.point(), index))
  simple_override(Edge, "curve", lambda self: BRep.BRep_Tool.Curve_(self, 0, 0))
  simple_override(Wire, "orient_edges", lambda self: RuntimeError("OrientEdgesOnWire_ doesn't work (apparent bug in OCCT?)"))#BOPTools.BOPTools_AlgoTools.OrientEdgesOnWire_(self))
  simple_override(Wire, "intersections", lambda self, other: merge_intersections([e.trimmed_curve().intersections(other) for e in self.edges()]))
  simple_override(Face, "outer_wire", lambda self: BRepTools.BRepTools.OuterWire_(self))
  simple_override(Face, "surface", lambda self: BRep.BRep_Tool.Surface_(self))
  
  def edge_length(self):
    curve, a, b = self.curve()
    return curve.length(a, b)
  simple_override(Edge, "length", edge_length)
  def edge_trimmed_curve(self):
    curve, a, b = self.curve()
    return TrimmedCurve(curve, a, b)
  simple_override(Edge, "trimmed_curve", edge_trimmed_curve)
  
  def compounded_shapes (compound):
    if not isinstance (compound, Compound):
      return [compound]
    iterator = TopoDS.TopoDS_Iterator (compound, True, True)
    results = []
    while iterator.More():
      child = iterator.Value()
      iterator.Next()
      results.extend (compounded_shapes (child))
    
    return results
  
  def CompoundIfNeeded (shapes):
    if len (shapes) == 1:
      return shapes[0]
    return Compound (shapes)
    
  def decompose_compound (compound):
    return CompoundIfNeeded (compounded_shapes (compound))
    
  simple_override(Compound, "decompose", decompose_compound)
  simple_override(Shape, "decompose_if_compound", decompose_compound)
  simple_override(Shape, "compounded_shapes", compounded_shapes)
  
  def recursive_flatten_compounded (*arguments):
    return [value for argument in recursive_flatten(*arguments) for value in compounded_shapes (argument)]

  def recursive_decompose (*arguments):
    return CompoundIfNeeded (recursive_flatten_compounded (*arguments))
  
  def is_shape(obj):
    return isinstance(obj, Shape)
  def read_brep (path):
    register_file_read(path)
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
  
  #override_attribute (Shape, "ShapeType", lambda original: lambda self: shape_type(original, shape))
  simple_override(Shape, "__wrap__", downcast_shape)
  
  def shape_valid(shape):
    return BRepCheck.BRepCheck_Analyzer(shape).IsValid()
  def check_shape(shape):
    a = BRepCheck.BRepCheck_Analyzer(shape)
    if not a.IsValid():
      raise RuntimeError(f'Invalid shape (detected by analyzer) {[str(b).replace("BRepCheck_Status.BRepCheck_", "") for b in a.Result(shape).Status()]}')
  
  def make_Vertex (original):
    def derived(cls, *args):
      if len(args) == 0:
        return original()
      if len (args) == 3:
        args = [Point (*args)]
      return BRepBuilderAPI.BRepBuilderAPI_MakeVertex(*args).Vertex()
    return classmethod(derived)
  override_attribute(Vertex, "__new__", make_Vertex)
  
  def make_Edge(original):
    def derived(cls, *args):
      if len(args) == 0:
        return original()
      builder = BRepBuilderAPI.BRepBuilderAPI_MakeEdge(*args)
      if not builder.IsDone():
        raise RuntimeError(f"Invalid edge (detected by builder): {args} => {builder.Error()}")
      return builder .Edge()
    return classmethod(derived)
  override_attribute(Edge, "__new__", make_Edge)
  
  def make_Wire(original):
    def derived(cls, *inputs, loop = False):
      inputs = recursive_flatten(inputs)
      builder = BRepBuilderAPI.BRepBuilderAPI_MakeWire()
      first_vertex = None
      last_vertex = None
      for index, item in enumerate (inputs):
        if isinstance (item, Point):
          item = Vertex (item)
        if isinstance (item, Curve):
          item = Edge (item)
        if first_vertex is None:
          first_vertex = item.vertices()[0]
        if isinstance (item, Vertex):
          if last_vertex is not None:
            builder.Add (Edge (last_vertex, item))
          last_vertex = item
        else:
          builder.Add (item)
          # for some reason, this doesn't work (gets "vertex hasn't gp_Pnt" errors)
          #last_vertex = builder.Vertex()
          last_vertex = item.edges()[-1].vertices()[-1]
      if loop:
        builder.Add (Edge (last_vertex, first_vertex))
      if not builder.IsDone():
        raise RuntimeError(f"Invalid wire (detected by builder): {inputs} => {builder.Error()}")
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
      if len(args) == 1 and isinstance(args[0], Curve):
        args = [Wire(args[0])]
      if len(args) == 1 and isinstance(args[0], Edge):
        args = [Wire(args[0])]
      builder = BRepBuilderAPI.BRepBuilderAPI_MakeFace(*args)
      for hole in recursive_flatten(holes):
        if not isinstance (hole, Wire):
          hole = Wire(hole)
        builder.Add (hole)
      if not builder.IsDone():
        raise RuntimeError(f"Invalid face (detected by builder) {args}, {holes} => {builder.Error()}")
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
        raise RuntimeError(f"Invalid solid (detected by builder) {args}, {holes} => {builder.Error()}")
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
        #print ("adding shape", shape)
        builder.Add (compound, shape)
      check_shape(compound)
      return compound
    return classmethod(derived)
  override_attribute(Compound, "__new__", make_Compound)
  
  export_locals ("Shape, is_shape, read_brep")
  for name in shape_typenames:
    do_export(name, globals()[name])
  
  
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
  
  def ClosedFreeWires(shape):
    free_check = ShapeAnalysis.ShapeAnalysis_FreeBoundsProperties (shape)
    free_check.Perform()
    return [free_bound.FreeBound() for free_bound in free_check.ClosedFreeBounds()]
    
  def FindSurface(shape, *, tolerance = -1, only_plane = False, only_closed = False):
    result = BRepLib.BRepLib_FindSurface (shape, tolerance, only_plane, only_closed).Surface()
    if only_plane:
      return GeomAdaptor.GeomAdaptor_Surface (shared_surface).Plane()
    
  def Offset2D (spine, offset, *, join = JoinArc, fill = False, open = False):
    if isinstance(spine, Edge):
      spine = Wire(spine)
    builder = BRepOffsetAPI.BRepOffsetAPI_MakeOffset (spine, join, open)
    builder.Perform (offset)
    result = builder.Shape()
    if fill:
      if spine.closed():
        if offset > 0:
          return Face (result, holes = [spine.Complemented()])
        else:
          return Face (spine.Complemented(), holes = [result])
      else:
        if open:
          raise RuntimeError("TODO: support open wires with open = True")
        else:
          return Face(result)

    return result
    
    
    
  def Offset (shape, offset, *, tolerance = default_tolerance, mode = ModeSkin, join = JoinArc, fill = False):
    builder = BRepOffsetAPI.BRepOffsetAPI_MakeOffsetShape()
    builder.PerformByJoin (shape, offset, tolerance, mode, False, False, join)
    
    result = builder.Shape()
    if not fill:
      return result
      
    image = builder.MakeOffset().OffsetEdgesFromShapes()
    #faces = shape.Faces() + result.Faces()
    shells = [shape, result]
    for free_wire in ClosedFreeWires(shape):
      #print("free bound")
      offset_wire = Wire (image.Image (edge) for edge in free_wire.edges())
      loft = Loft(free_wire, offset_wire)
      #faces.extend(loft.faces())
      shells.append (loft)
    #print (faces)
    #shell = Shell (faces)
    sewing = BRepBuilderAPI.BRepBuilderAPI_Sewing(tolerance)
    for shell in shells:
      if offset > 0:
        shell = shell.complemented()
      sewing.Add(shell)
    sewing.Perform()
    complete_shell = sewing.SewedShape()
    check_shape(complete_shell)
    #print (complete_shell)
    return Solid (complete_shell)

  class Angle(SerializeAsVars):
    def cos(self):
      return math.cos(self.radians)
    def sin(self):
      return math.sin(self.radians)
    def __mul__(self, other):
      return Radians(self.radians * other)
    __rmul__ = __mul__
    def __truediv__(self, other):
      return Radians(self.radians / other)

  class Degrees(Angle):
    def __init__(self, degrees):
      self.degrees = degrees
      self.turns = self.degrees / 360
      self.radians = self.turns * math.tau

  class Radians(Angle):
    def __init__(self, radians):
      self.radians = radians
      self.turns = self.radians / math.tau
      self.degrees = self.turns * 360

  class Turns(Angle):
    def __init__(self, turns):
      self.turns = turns
      self.radians = self.turns * math.tau
      self.degrees = self.turns * 360

  @export
  def acos(ratio):
    return Radians(math.acos(ratio))
      
  @export
  def Revolve(shape, axis, angle = None, *, radians=None, degrees=None):
    if isinstance (axis, Direction):
      axis = Axis (Origin, axis)
    if degrees is not None:
      angle = Degrees(degrees)
    if radians is not None:
      angle = Radians(radians)
    return BRepPrimAPI.BRepPrimAPI_MakeRevol(shape, axis, angle and angle.radians).Shape()
  
    
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
  
  @export
  def Fillet(shape, edges_info):
    builder = BRepFilletAPI.BRepFilletAPI_MakeFillet (shape)
    for info in edges_info:
      builder.Add (*info[1:], info [0])
    builder.Build()
    return builder.Shape()
    
  @export
  def Chamfer(shape, edges_info):
    builder = BRepFilletAPI.BRepFilletAPI_MakeChamfer (shape)
    for info in edges_info:
      builder.Add (*info[1:], info [0])
    builder.Build()
    return builder.Shape()
  
  
  def FilletedEdges(input, loop = False):
    previous_edge = None
    result = []
    def digest (item):
      if type (item) is tuple:
        return item
      return (item, None)
    if loop:
      previous_edge = Edge (digest (input [-1]) [0], digest (input [0]) [0])
    
    def handle_pair (first, second, append_edges = True):
      nonlocal previous_edge
      first, radius = digest (first)
      second, _ = digest (second)
      new_edge = Edge (first, second)
      
      if radius is not None:
        # hack – doesn't accommodate edges whose endpoints are collinear but they curve off to the side
        v0 = previous_edge.vertices()
        v1 = new_edge.vertices()
        arbitrary_point = v0[1].point()
        plane_normal = Direction((v0[1].point() - v0[0].point()).cross (v1[1].point() - v1[0].point()))
        builder = ChFi2d.ChFi2d_FilletAlgo (previous_edge, new_edge, Plane(arbitrary_point, plane_normal).Pln())
        builder.Perform(radius)
        new_joiner = builder.Result (arbitrary_point, previous_edge, new_edge)
        if append_edges:
          result.append (new_joiner)
      if append_edges:
        result.append (new_edge)
      previous_edge = new_edge
    
    
    for pair in pairs (input):
      handle_pair (*pair)
    
    if loop:
      handle_pair (input [-1], input [0])
      handle_pair (input [0], input [1], False)
      
    return result
  
  
  
  def finish_Boolean (builder):
    builder.Build()
    if not builder.IsDone():
      raise RuntimeError (f"Boolean operation failed {builder.GetReport().dump (Message.Message_Gravity.Message_Fail)} {builder.GetReport().dump (Message.Message_Gravity.Message_Alarm)} {builder.GetReport().dump (Message.Message_Gravity.Message_Warning)}")
    return builder.Shape()
  
  def Union (*shapes):
    shapes = recursive_flatten_compounded (shapes)
    builder = BRepAlgoAPI.BRepAlgoAPI_Fuse()
    builder.SetArguments (ListOfShape (shapes [:1]))
    builder.SetTools (ListOfShape (shapes [1:]))
    return finish_Boolean (builder)
    
  def Intersection (first, second):
    first_shapes = recursive_flatten_compounded(first)
    if len (first_shapes) > 1:
      return CompoundIfNeeded ([result_shape for shape in first_shapes for result_shape in Intersection (shape, second).compounded_shapes()])
      
    second_shapes = recursive_flatten_compounded(second)
    if len (second_shapes) > 1:
      return CompoundIfNeeded ([result_shape for shape in second_shapes for result_shape in Intersection (first, shape).compounded_shapes()])
      
    builder = BRepAlgoAPI.BRepAlgoAPI_Common(first.decompose_if_compound(), second.decompose_if_compound())
    return finish_Boolean (builder)
  
  def Difference (first, second):
    builder = BRepAlgoAPI.BRepAlgoAPI_Cut()
    builder.SetArguments (ListOfShape (recursive_flatten_compounded (first)))
    builder.SetTools (ListOfShape (recursive_flatten_compounded (second)))
    return finish_Boolean (builder)
  
  @export
  def Section (first, second):
    builder = BRepAlgoAPI.BRepAlgoAPI_Section(first, second)
    return finish_Boolean (builder)
  
  def Extrude (shape, offset, second_offset = None, *, centered = False):
    infinite = isinstance (offset, Direction)
    if infinite:
      builder = BRepPrimAPI.BRepPrimAPI_MakePrism (shape, offset, centered)
    elif second_offset is not None:
      builder = BRepPrimAPI.BRepPrimAPI_MakePrism (shape @ Translate(offset), second_offset - offset)
    else:
      builder = BRepPrimAPI.BRepPrimAPI_MakePrism (shape, offset)
    result = builder.Shape()
    if centered and not infinite:
      assert second_offset is None, "Error: extruding with both centered and a second offset"
      result = result@Translate (- offset*0.5)
    return result
    
  
  def Box (*args):
    return BRepPrimAPI.BRepPrimAPI_MakeBox (*args).Shape()
  
  def HalfSpace(point, direction):
    plane = Plane (point, direction)
    reference = point + Vector (direction)
    return BRepPrimAPI.BRepPrimAPI_MakeHalfSpace(Face(plane), reference).Solid()
    
    
  def BuildMesh (shape, linear_deflection = 0.01, angular_deflection = 0.1):
    builder = BRepMesh.BRepMesh_IncrementalMesh (shape, linear_deflection, False, angular_deflection, True)
    builder.Perform()
  
  def SaveSTL_raw (path, shape):
    StlAPI.StlAPI.Write_ (shape, path)
  
  @export
  def SaveSTEP_raw (path, shape):
    writer = STEPControl.STEPControl_Writer()
    writer.Transfer(shape, STEPControl.STEPControl_StepModelType.STEPControl_AsIs)
    writer.Write(path)
      
  def LoadSTL (path):
    register_file_read(path)
    #note: it appears that StlAPI.Read is simply nonfunctional
    '''shape = Shape()
    StlAPI.StlAPI.Read_ (shape, os.path.abspath (path))
    shape = downcast_shape (shape)'''
    #print (os.path.abspath (path))
    triangulation = RWStl.RWStl.ReadFile_(os.path.abspath (path))
    vertices = [Vertex (point) for point in triangulation.nodes()]
    faces = [Wire (*(vertices [index - 1] for index in triangle.Get (0, 0, 0))) for triangle in triangulation.triangles()]
    return Compound (faces)
  
  export_locals ("thicken_shell_or_face, thicken_solid, Box, HalfSpace, Loft, Offset, Offset2D, Union, Intersection, Difference, JoinArc, JoinIntersection, FilletedEdges, ClosedFreeWires, BuildMesh, SaveSTL_raw Extrude LoadSTL Angle Degrees Radians Turns")
  

  
  ################################################################
  #########################  Exports  ############################
  ################################################################
  for name in exported_locals:
    do_export(name, locals()[name])
  
  
