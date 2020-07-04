def make_full_face_mask():
  slot_width = 0.5
  slot_depth = 5
  min_wall_thickness = 1.0
  
  displayed_objects = {}
  def show_transformed(a,b):
    displayed_objects[b] = a
  
  forehead_point = vector (0, -58)
  back_edge = forehead_point[1] - 96
  '''shield_top_points = [
    vector (10, 0),
    vector (30, -10),
    vector (50, -25),
    vector (60, -40),
    vector (70, -57),
    vector (80, -75),
    vector (100, back_edge),
  ]
  degree = 3
  shield_top_poles = [vector (-a[0], a[1]) for a in reversed(shield_top_points)] + [vector(0, 0)] + shield_top_points
  shield_top_curve = Part.BSplineCurve()
  shield_top_curve.buildFromPolesMultsKnots(
    shield_top_poles,
    [degree+1] + [1]*(len(shield_top_poles) - degree - 1) + [degree+1],
    degree = degree,
  )'''
  
  forehead_points = [
    vector (15, 0),
    vector (25, -3.5),
    vector (35, -7),
    vector (45, -12),
    vector (55, -22),
    vector (62, -35),
    vector (70, -53),
    vector (79, -90),
    vector (79, -110),
    vector (79, -130),
  ]
  degree = 3
  forehead_poles = [forehead_point + vector (-a[0], a[1]) for a in reversed(forehead_points)] + [forehead_point] + [forehead_point + a for a in forehead_points]
  forehead_curve = Part.BSplineCurve()
  forehead_curve.buildFromPolesMultsKnots(
    forehead_poles,
    degree = degree,
    periodic = True,
  )
  forehead_exclusion = forehead_curve.toShape().to_wire().to_face().fancy_extrude (vector (0, 0, 1), bounds (-5, 50))
  
  top_minor_radius = 100
  top_major_radius = -back_edge*2
  shield_top_full_wire = Part.Ellipse(vector(0,0), vector (top_minor_radius, -top_major_radius), vector(0, -top_major_radius)).toShape().to_wire()
  lenient_box = box(centered (500), bounds (back_edge, 500), bounds(-180, 20))
  shield_box = box(centered (500), bounds (back_edge, 500), bounds (-180, slot_depth))
  shield_top_curve = shield_top_full_wire.common(shield_box)
  #show_transformed(shield_box, "shield_box")
  
  show_transformed(shield_top_curve, "shield_top_curve")
  
  shield_focal_z = 100
  shield_focal_ratio = 1.8
  shield_focal_point = vector (0, shield_focal_z / shield_focal_ratio, shield_focal_z)
  #shield_focal_point = vector (0, back_edge, back_edge*2)
  
  '''
  
  formulas:
  if we represent the surface as a function of z, u (z position and ellipse parameter in radians)
  
  then
  oval_size_factor = (shield_focal_z - z) / shield_focal_z = 1.0 - z / shield_focal_z
  y = top_major_radius*oval_size_factor*(sin(u)-1.0) + z/shield_focal_ratio
  x = top_minor_radius*oval_size_factor*cos(u)
  
  dy/du = top_major_radius*oval_size_factor*cos(u)
  dy/dz = top_major_radius*(sin(u)-1.0)*(-1.0 / shield_focal_z) + 1.0/shield_focal_ratio
  dx/du = top_minor_radius*oval_size_factor*-sin(u)
  dx/dz = top_minor_radius*cos(u)*(-1.0 / shield_focal_z)
  dz/du = 0
  dz/dz = 1
  
  solve for u given x:
  x = top_minor_radius*oval_size_factor*cos(u)
  x / (top_minor_radius*oval_size_factor) = cos(u)
  u = acos(x / (top_minor_radius*oval_size_factor))
  
  solve for u given y:
  y = top_major_radius*oval_size_factor*(sin(u)-1.0) + z/shield_focal_ratio
  (y - z/shield_focal_ratio + top_major_radius*oval_size_factor) = top_major_radius*oval_size_factor*sin(u)
  (y - z/shield_focal_ratio + top_major_radius*oval_size_factor)/top_major_radius*oval_size_factor = sin(u)
  (y - z/shield_focal_ratio)/top_major_radius*oval_size_factor + 1.0 = sin(u)
  u = asin((y - z/shield_focal_ratio)/top_major_radius*oval_size_factor + 1.0)
  '''
  
  class ShieldSurfacePoint:
    def __init__(self, z = None, x = None, y = None):
      self.oval_size_factor = 1.0 - z / shield_focal_z
      self.minor_radius = top_minor_radius*self.oval_size_factor
      self.major_radius = top_major_radius*self.oval_size_factor
      self.z = z
      if x is not None:
        self.x = x
        u = math.acos(x / self.minor_radius)
        self.u = u
        self.parameter = u
        self.y = self.major_radius*(math.sin (self.parameter)-1.0) + z/shield_focal_ratio
        recalculated_x = self.minor_radius*math.cos (self.parameter)
        assert (abs (recalculated_x - self.x) <0.01)
      else:
        self.y = y
        print(y)
        print(z)
        print(self.major_radius)
        u = math.asin((y - z/shield_focal_ratio)/self.major_radius + 1.0)
        self.u = u
        self.parameter = u
        self.x = self.minor_radius*math.cos (self.parameter)
        recalculated_y = self.major_radius*(math.sin (self.parameter)-1.0) + z/shield_focal_ratio
        assert (abs (recalculated_y - self.y) <0.01)
      self.position = vector (self.x, self.y, self.z)
      self.ddz = vector (
        top_minor_radius*math.cos(u)*(-1.0 / shield_focal_z),
        top_major_radius*(math.sin (self.parameter)-1.0)*(-1.0 / shield_focal_z) + 1.0/shield_focal_ratio,
        1
      )
      self.ddu = vector (
        self.minor_radius*-math.sin(u),
        self.major_radius*math.cos(u),
        0,
      )
      #self.horizontal_tangent = self.ddu.normalized()
      #self.vertical_tangent = self.ddz.normalized()
      self.normal = self.ddu.cross(self.ddz).normalized()
  
  
  source_side_points = [
    ShieldSurfacePoint (z=0, y= back_edge),
    ShieldSurfacePoint (z= -20, y= back_edge),
    ShieldSurfacePoint (z= -40, y= back_edge),
    ShieldSurfacePoint (z= -60, y= forehead_point[1] - 85),
    ShieldSurfacePoint (z= -80, y= forehead_point[1] - 65),
    ShieldSurfacePoint (z= -100, y= forehead_point[1] - 45),
    ShieldSurfacePoint (z= -120, x = 50),
    ShieldSurfacePoint (z= -140, x = 25),
    ShieldSurfacePoint (z= -140, x = 0),
  ]
  
  degree = 3
  source_side_poles = [a.position for a in source_side_points]
  source_side_curve = Part.BSplineCurve()
  source_side_curve.buildFromPolesMultsKnots(
    source_side_poles,
    mults = [degree+1] + [1]*(len(source_side_poles) - degree - 1) + [degree+1],
    degree = degree,
  )
  
  subdivisions = 40
  source_side_curve_length = source_side_curve.length()
  def refined_side_point (distance):
    intermediate = source_side_curve.value (source_side_curve.parameterAtDistance (distance))
    return ShieldSurfacePoint (z= intermediate [2], x= intermediate [0])
  side_points = [
    refined_side_point (source_side_curve_length * index / (subdivisions -1))
    for index in range (subdivisions)
  ]
  side_points = side_points + [ShieldSurfacePoint (z= point.z, x= -point.x) for point in reversed(side_points[:-1])]
  
  degree = 3
  side_poles = [a.position for a in side_points]
  side_curve = Part.BSplineCurve()
  side_curve.buildFromPolesMultsKnots(
    side_poles,
    mults = [degree+1] + [1]*(len(side_poles) - degree - 1) + [degree+1],
    degree = degree,
  )
  
  show_transformed (side_curve.toShape(), "side_curve")
  
  side_strut_shape = FreeCAD_shape_builder().build ([
        start_at(-slot_width- min_wall_thickness, 0),
        horizontal_to (min_wall_thickness),
        vertical_to (min_wall_thickness + slot_depth),
        horizontal_to (0),
        vertical_to (min_wall_thickness),
        horizontal_to (-slot_width),
        vertical_to (min_wall_thickness + slot_depth),
        horizontal_to (-slot_width- min_wall_thickness),
        close()
      ]).to_wire() #.to_face()
  
  side_strut_pieces = []
  for index, point in enumerate (side_points):
    position = point.position
    parameter = side_curve.parameter (position)
    tangent = vector (*side_curve.tangent (parameter)).normalized()
    normal = point.normal
    away = tangent.cross (normal)
    
    matrix = FreeCAD.Matrix(
      normal [0], -away [0], tangent [0], position[0],
      normal [1], -away [1], tangent [1], position[1],
      normal [2], -away [2], tangent [2], position[2],
    )
    shape = side_strut_shape.copy()
    shape.transformShape (matrix)
    side_strut_pieces.append(shape)
    #show_transformed (shape,f"side_strut_shape_{index}")
  
  side_strut = Part.makeLoft (side_strut_pieces, True)
  show_transformed (side_strut,f"side_strut")
  
  
  shield_extension_zs = [-180, 20]
  def shield_extension_curve (z):
    offset_fraction = z / shield_focal_point[2]
    return shield_top_full_wire.scaled (1.0 - offset_fraction).translated (shield_focal_point*offset_fraction)
  shield_extension_curves = [shield_extension_curve (z) for z in shield_extension_zs]
  
  shield_cross_section = shield_top_full_wire.to_face().common(shield_box)
  for index, offset_distance in enumerate (20.0*x for x in range(10)):
    offset_fraction = offset_distance / -shield_focal_point[2]
    show_transformed (shield_cross_section.scaled (1.0 - offset_fraction).translated (shield_focal_point*offset_fraction), f"shield_cross_section_{index}")
  
  #show_transformed(shield_extension_curves[0], "shield_extension_curve_0")
  #show_transformed(shield_extension_curves[1], "shield_extension_curve_1")
  
  shield_outer_surface = Part.makeRuledSurface(*shield_extension_curves).common(lenient_box)
  
  frame_space = shield_outer_surface.makeOffsetShape (-min_wall_thickness, 0.01).common (lenient_box).extrude(vector(0, -200, 0))
  #show_transformed (frame_space, "frame_space")
  
  #show_transformed(shield_outer_surface, "shield_outer_surface")
  
  shield_solid = shield_outer_surface.makeOffsetShape (slot_width, 0.01, fill = True).common (shield_box)
  
  show_transformed(shield_solid, "shield_solid")
  
  visor = box(
    centered (500),
    centered (500),
    bounds (0, slot_depth + min_wall_thickness),
  ).common (lenient_box).common(frame_space).cut (forehead_exclusion).cut(shield_solid)
  
  show_transformed (visor, "visor")
  
  on_face = False
  #on_face = True
  for name, object in displayed_objects.items():
    if on_face:
      object = (object
      .translated (- forehead_point)
      .as_xz()
      .mirror(vector(), vector(0,1,0))
      .rotated(vector(), vector(1, 0, 0), 360/math.tau*math.atan2(-42,123))
      .translated (vector (0, 14, 0.25)))
    show (object, name)
    
  return on_face

def run(g):
  for key, value in g.items():
    globals()[key] = value
  return make_full_face_mask()
  
  
  