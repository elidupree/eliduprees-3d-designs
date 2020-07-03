def make_full_face_mask():
  slot_width = 0.5
  
  displayed_objects = {}
  def show_transformed(a,b):
    displayed_objects[b] = a
  
  forehead_point = vector (0, -58)
  back_edge = -134
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
  
  shield_top_full_wire = Part.Ellipse(vector(0,0), vector (116, back_edge*1.8), vector(0, back_edge*2)).toShape().to_wire()
  shield_box = box(centered (500), bounds (back_edge, 500), centered (500))
  shield_top_curve = shield_top_full_wire.common(shield_box)
  
  
  show_transformed(shield_top_curve, "shield_top_curve")
  
  shield_extension_fraction = 0.1
  shield_focal_point = vector (0, back_edge, back_edge*2)
  shield_extension_curve = shield_top_full_wire.scaled (0.1).translated (shield_focal_point*(1-shield_extension_fraction))
  print(type(shield_extension_curve))
  
  shield_cross_section = shield_top_full_wire.to_face().common(shield_box)
  for index, offset_distance in enumerate (20.0*x for x in range(10)):
    offset_fraction = offset_distance / -shield_focal_point[2]
    show_transformed (shield_cross_section.scaled (1.0 - offset_fraction).translated (shield_focal_point*offset_fraction), f"shield_cross_section_{index}")
  
  show_transformed(shield_extension_curve, "shield_extension_curve")
  
  shield_outer_surface = Part.makeRuledSurface(shield_top_full_wire, shield_extension_curve).common(shield_box)
  
  #show_transformed(shield_outer_surface, "shield_outer_surface")
  
  shield_solid = shield_outer_surface.makeOffsetShape (slot_width, 0.01, fill = True)
  
  #show_transformed(shield_solid, "shield_solid")
  
  on_face = False
  on_face = True
  for name, object in displayed_objects.items():
    if on_face:
      object = (object
      .translated (- forehead_point)
      .as_xz()
      .mirror(vector(), vector(0,1,0))
      .rotated(vector(), vector(1, 0, 0), 360/math.tau*math.atan2(-42,123))
      .translated (vector (0, 14, 0.25)))
    show (object, name)
    
  if on_face:
    faces.run(globals())

def run(g):
  for key, value in g.items():
    globals()[key] = value
  make_full_face_mask()
  
  
  