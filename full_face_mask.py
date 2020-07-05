def make_full_face_mask():
  shield_slot_width = 1.3
  shield_slot_depth = 5
  elastic_slot_catch_length = 2
  elastic_slot_width = 8
  elastic_slot_depth = 5
  min_wall_thickness = 1.0
  CPAP_outer_radius = 21.5/2
  CPAP_inner_radius = CPAP_outer_radius - min_wall_thickness
  
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
    vector (25, -2.5),
    vector (35, -7),
    vector (45, -14),
    vector (55, -27),
    vector (62, -37),
    vector (71, -53),
    vector (79, -90),
    vector (81, -107),
    vector (88, -108),
    vector (94, -107),
    vector (100, -107),
    vector (100, -207),
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
  
  #forehead_elastic_hole = Part.makeCylinder (3, 50, vector (-86.4, -161, -4))
  forehead_elastic_hole = box (centered (1), 5, centered (100)).makeOffsetShape (1.5, 0.01).rotated (vector(), vector (0, 0, 1), -10).translated (vector (-85.4, -162, -4))
  forehead_exclusion = forehead_exclusion.fuse ([
    forehead_elastic_hole,
    forehead_elastic_hole.mirror (vector(), vector (1, 0, 0)),
  ])
  
  top_minor_radius = 100
  top_major_radius = -back_edge*2
  shield_top_full_wire = Part.Ellipse(vector(0,0), vector (top_minor_radius, -top_major_radius), vector(0, -top_major_radius)).toShape().to_wire()
  lenient_box = box(centered (500), bounds (back_edge-50, 500), bounds(-180, 20))
  shield_box = box(centered (500), bounds (back_edge, 500), bounds (-180, shield_slot_depth))
  shield_top_curve = shield_top_full_wire.common(shield_box)
  #show_transformed(shield_box, "shield_box")
  
  show_transformed(shield_top_curve, "shield_top_curve")
  
  shield_focal_z = 400
  shield_focal_ratio = 2
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
    ShieldSurfacePoint (z=shield_slot_depth, y= back_edge),
    ShieldSurfacePoint (z=0, y= back_edge),
    ShieldSurfacePoint (z= -20, y= back_edge),
    ShieldSurfacePoint (z= -40, y= back_edge),
    ShieldSurfacePoint (z= -60, y= forehead_point[1] - 90),
    ShieldSurfacePoint (z= -80, y= forehead_point[1] - 75),
    ShieldSurfacePoint (z= -100, y= forehead_point[1] - 60),
    ShieldSurfacePoint (z= -120, x = 54),
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
  
  show_transformed (source_side_curve.toShape(), "source_side_curve")
  
  subdivisions = 100
  source_side_curve_length = source_side_curve.length()
  def refined_side_point (distance):
    parameter = source_side_curve.parameterAtDistance (distance)
    
    intermediate = source_side_curve.value (parameter)
    #print (f" parameter: {parameter}, distance: {distance}, intermediate: {intermediate}")
    y_based = ShieldSurfacePoint (z= intermediate [2], y= intermediate [1])
   
    x_frac = (intermediate[1] - -140)/60
    if x_frac < 0:
      return ShieldSurfacePoint (z= intermediate [2], y= intermediate [1])
    elif x_frac > 1:
      return ShieldSurfacePoint (z= intermediate [2], x= intermediate [0])
    else:
      x_based = ShieldSurfacePoint (z= intermediate [2], x= intermediate [0])
      y_based = ShieldSurfacePoint (z= intermediate [2], y= intermediate [1])
      intermediate = x_based.position*x_frac + y_based.position*(1-x_frac)
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
  
  shield_slot_top = min_wall_thickness + shield_slot_depth
  elastic_slot_bottom = shield_slot_top - elastic_slot_width - min_wall_thickness*2
  side_shield_slot_shape = FreeCAD_shape_builder().build ([
        start_at(-shield_slot_width- min_wall_thickness, 0),
        diagonal_to (0, elastic_slot_bottom),
        horizontal_to (elastic_slot_depth + elastic_slot_catch_length + min_wall_thickness*2),
        vertical_to (elastic_slot_bottom+ min_wall_thickness),
        diagonal_to (elastic_slot_depth + min_wall_thickness*2, elastic_slot_bottom+ elastic_slot_catch_length + min_wall_thickness),
        horizontal_to (elastic_slot_depth + min_wall_thickness),
        vertical_to (elastic_slot_bottom+ min_wall_thickness),
        horizontal_to (min_wall_thickness),
        vertical_to (shield_slot_top - min_wall_thickness),
        horizontal_to (elastic_slot_depth + min_wall_thickness),
        vertical_to (shield_slot_top - min_wall_thickness - elastic_slot_catch_length),
        horizontal_to (elastic_slot_depth + min_wall_thickness*2),
        diagonal_to (elastic_slot_depth + min_wall_thickness*2 + elastic_slot_catch_length, shield_slot_top - min_wall_thickness),
        vertical_to (shield_slot_top),
        horizontal_to (0),
        vertical_to (min_wall_thickness),
        horizontal_to (-shield_slot_width),
        vertical_to (min_wall_thickness + shield_slot_depth),
        horizontal_to (-shield_slot_width- min_wall_thickness),
        close()
      ]).to_wire() #.to_face()
  
  '''elastic_slot_shape = FreeCAD_shape_builder().build ([
        start_at(0, 0),
        horizontal_to (min_wall_thickness+elastic_slot_depth),
        vertical_to (min_wall_thickness),
        horizontal_to (min_wall_thickness),
        vertical_to (elastic_slot_width + min_wall_thickness),
        horizontal_to (min_wall_thickness+elastic_slot_depth),
        vertical_to (elastic_slot_width + min_wall_thickness*2),
        horizontal_to (0),
        close()
      ]).to_wire()'''
      
  def matrix_from_columns(a,b,c,d):
    return FreeCAD.Matrix(
      a[0], b[0], c[0], d[0],
      a[1], b[1], c[1], d[1],
      a[2], b[2], c[2], d[2],
    )
  
  side_shield_slot_pieces = []
  intake_flat_outside_edge = []
  intake_flat_inside_edge = []
  #side_elastic_slot_pieces = []
  for index, point in enumerate (side_points):
    position = point.position
    parameter = side_curve.parameter (position)
    tangent = vector (*side_curve.tangent (parameter)).normalized()
    normal = point.normal
    away = tangent.cross (normal)
    
    shield_slot_matrix = matrix_from_columns(normal, -away, tangent, position)
    shield_shape = side_shield_slot_shape.copy()
    shield_shape.transformShape (shield_slot_matrix)
    side_shield_slot_pieces.append(shield_shape)
    #show_transformed (shape,f"side_strut_shape_{index}")
    
    '''curve_normal = vector (*side_curve.normal(parameter))
    elastic_slot_matrix = matrix_from_columns(-curve_normal, -curve_normal.cross(tangent), tangent, position)
    elastic_shape = elastic_slot_shape.copy()
    elastic_shape.transformShape (elastic_slot_matrix)
    side_elastic_slot_pieces.append(elastic_shape)'''
    
    if position [0] <0 and position [2] >= -100 and position [2] <= -60:
      intake_flat_outside_edge.append (position - normal*(shield_slot_width + min_wall_thickness*1.6))
      intake_flat_inside_edge.append (position - normal*(shield_slot_width + min_wall_thickness*1.6 + 7))
  intake_flat_inside_edge.reverse()
  
  side_shield_slot = Part.makeLoft (side_shield_slot_pieces, True)
  show_transformed (side_shield_slot,f"side_shield_slot")
  
  #side_elastic_slot = Part.makeLoft (side_elastic_slot_pieces, True)
  #show_transformed (side_elastic_slot,f"side_elastic_slot")
  
  
  shield_extension_zs = [-180, 20]
  def shield_extension_curve (z):
    offset_fraction = z / shield_focal_point[2]
    return shield_top_full_wire.scaled (1.0 - offset_fraction).translated (shield_focal_point*offset_fraction)
  shield_extension_curves = [shield_extension_curve (z) for z in shield_extension_zs]
  
  shield_cross_section = shield_top_full_wire.to_face().common(shield_box)
  for index, offset_distance in enumerate (20.0*x for x in range(10)):
    offset_fraction = offset_distance / -shield_focal_point[2]
    #show_transformed (shield_cross_section.scaled (1.0 - offset_fraction).translated (shield_focal_point*offset_fraction), f"shield_cross_section_{index}")
  
  #show_transformed(shield_extension_curves[0], "shield_extension_curve_0")
  #show_transformed(shield_extension_curves[1], "shield_extension_curve_1")
  
  shield_outer_surface = Part.makeRuledSurface(*shield_extension_curves).common(lenient_box)
  
  frame_space = shield_outer_surface.makeOffsetShape (-min_wall_thickness, 0.01).common (lenient_box).extrude(vector(0, -200, 0))
  #show_transformed (frame_space, "frame_space")
  
  #show_transformed(shield_outer_surface, "shield_outer_surface")
  
  shield_solid = shield_outer_surface.makeOffsetShape (shield_slot_width, 0.01, fill = True).common (shield_box)
  
  show_transformed(shield_solid, "shield_solid")
  
  visor = box(
    centered (500),
    centered (500),
    bounds (0, shield_slot_depth + min_wall_thickness),
  ).common (lenient_box).common(frame_space).cut (forehead_exclusion).cut(shield_solid)
  
  #forehead_expanded = forehead_curve.toShape().to_wire().makeOffset2D (1).to_face().fancy_extrude (vector (0, 0, 1), bounds (0, 4))
  #show_transformed (forehead_expanded.common (lenient_box).common(frame_space).cut (forehead_exclusion), "forehead_shape")
  
  
  show_transformed (visor, "visor")
  #show_transformed (visor.common(box(centered (30, on = 85), centered (40, on = -160), centered (500))), "visor_fragment")
  #show_transformed (side_shield_slot.common(box(centered (30, on = 85), centered (40, on = -160), centered (40))), "side_shield_slot_fragment")
  
  intake_flat_width = 7
  intake_center = min (
    (side_point for side_point in side_points if side_point.position [0] <0),
    key = lambda side_point: abs (-80 - side_point.position [2])
  )
  intake_direction = intake_center.normal.cross (vector (0, 0, -1)).normalized()
  intake_sideways = vector (*side_curve.tangent (side_curve.parameter (intake_center. position)))
  intake_flat_subdivisions = 10
  intake_flat_height = 40
  def intake_flat_wire (expansion, forwards_offset):
    outside_edge = []
    inside_edge = []
    height = intake_flat_height + expansion*2
    center_source = intake_center.position - intake_direction*forwards_offset
    center = ShieldSurfacePoint (z = center_source [2], y = center_source [1])
    center = ShieldSurfacePoint (z = center_source [2], x = -center.position[0])
    
    for index in range (intake_flat_subdivisions):
      fraction = index/(intake_flat_subdivisions -1)
      offset = (fraction - 0.5)*height/intake_sideways [2]
      source = center.position + intake_sideways*offset
      precise = ShieldSurfacePoint (z = source [2], y = source [1])
      precise = ShieldSurfacePoint (z = precise.position[2], x = -precise.position [0])
      
      # we have to project everything onto the same plane so that the loft can be closed
      def projected (position):
        threeD_offset = position - center.position
        normal_component = center.normal.dot (threeD_offset)
        sideways_component = intake_sideways.dot(threeD_offset)
        result = center.position + center.normal*normal_component + intake_sideways*sideways_component
        #print (f"{result - position}, {normal_component}, {sideways_component}, {center.normal}, {intake_sideways}")
        return result
      
      outside_edge.append (projected (precise.position - precise.normal*(shield_slot_width + min_wall_thickness - expansion)))
      inside_edge.append (projected (precise.position - precise.normal*(shield_slot_width + min_wall_thickness + intake_flat_width + expansion)))
    outside_edge.reverse()
    degree = 3
    poles = outside_edge + inside_edge
    intake_flat_curve = Part.BSplineCurve()
    intake_flat_curve.buildFromPolesMultsKnots(
      poles,
      degree = degree,
      periodic = True,
    )
    return intake_flat_curve.toShape().to_wire()
      
  
  def intake_loft_components (expansion):
    CPAP_wire = Part.Shape ([Part.Circle (intake_center.position + intake_direction*45 - intake_center.normal*(shield_slot_width + min_wall_thickness + intake_flat_width/2) + vector (0, 0, 3), intake_direction, CPAP_inner_radius + expansion)]).to_wire()
    result = []
    if expansion == 0:
      flat_start = -1
    return (
      [intake_flat_wire(expansion, 7-index*2) for index in range (5)]
      + [CPAP_wire.translated (intake_direction*index*4) for index in range (5)])
    
  intake_interior = Part.makeLoft (intake_loft_components (0.0), True)
  intake_exterior = Part.makeLoft (intake_loft_components (min_wall_thickness), True)
  
  show_transformed (intake_interior, "intake_interior")
  show_transformed (intake_exterior, "intake_exterior")
  
  intake_solid = intake_exterior.cut (intake_interior) #intake_surface.makeOffsetShape (min_wall_thickness, 0.01, fill=True)
  
  show_transformed (intake_solid, "intake_solid")
  
  top_splitter = box (bounds (0, 500), centered (500), bounds (0, 500))
  top_splitter2 = box (bounds (-500, 0), centered (500), bounds (0, 500))
  #show_transformed (top_splitter, "top_splitter")
  show_transformed (Part.Compound ([
    visor,
    side_shield_slot.common(top_splitter2),
    #side_shield_slot.common(top_splitter),
    side_shield_slot.common(top_splitter2).mirror(vector(), vector(1,0,0)),
  ]), "augmented_visor")
  
  side_splitter = box (bounds (-500, -56), centered (500), bounds (-500, 0))
  side_splitter_2 = box (bounds (-56, 56), centered (500), centered (500))
  show_transformed (side_shield_slot. common (side_splitter_2), "bottom_slot")
  show_transformed (side_shield_slot.common (side_splitter), "side_slot")
  
  on_face = False
  #on_face = True
  for name, object in displayed_objects.items():
    if on_face:
      object = (object
      .translated (- forehead_point)
      .as_xz()
      .mirror(vector(), vector(0,1,0))
      .rotated(vector(), vector(1, 0, 0), 360/math.tau*math.atan2(-28,123))
      .translated (vector (0, 18, 0.25)))
    show (object, name)
    
  return on_face

def run(g):
  for key, value in g.items():
    globals()[key] = value
  return make_full_face_mask()
  
  
  