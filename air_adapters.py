CPAP_outer_radius = 21.5/2
elidupree_4in_threshold = 51.616
elidupree_4in_leeway_one_sided = 0.12
elidupree_4in_intake_inner_radius = elidupree_4in_threshold + elidupree_4in_leeway_one_sided
elidupree_4in_output_outer_radius = elidupree_4in_threshold - elidupree_4in_leeway_one_sided

single_wall_thickness = 0.4

def elidupree_4in_to_CPAP_solid():
  CPAP_wire = Part.Shape([Part.Circle (vector(), vector (0, 0, 1), CPAP_outer_radius)]).to_wire()
  elidupree_4in_wire = Part.Shape([Part.Circle (vector(), vector (0, 0, 1), elidupree_4in_intake_inner_radius + single_wall_thickness)]).to_wire()
  
  adapter = Part.makeLoft ([elidupree_4in_wire.translated (vector (0, 0, index*5)) for index in range (5)]
  + [CPAP_wire.translated (vector (0, 0, 95+index*4)) for index in range (5)], True, False, False, 5)
  
  show (adapter, "adapter")

def elidupree_4in_under_door():
  wall_thickness = 0.5
  def elidupree_4in_wire(radius, index):
    dirv = vector(-1.3, 0, 1).normalized()
    start = vector(-100,0,18 -dirv[0]*radius)
    return Part.Shape([Part.Circle (start + dirv*index*2.5, dirv, radius)]).to_wire()
  
  zigzag_depth = -3
  curved_zigzag_offset = zigzag_depth/3
  under_door_polygon = FreeCAD_shape_builder(zigzag_length_limit=6, zigzag_depth = zigzag_depth).build([
    start_at (-60, curved_zigzag_offset),
    horizontal_to (60),
    vertical_to (32 - wall_thickness*2 - curved_zigzag_offset),
    horizontal_to(-60),
    close()
  ]).as_yz().to_wire()
  
  under_door_curve = Part.BSplineCurve()
  under_door_curve.buildFromPolesMultsKnots(
    [v.Point for v in under_door_polygon.Vertexes],
    periodic = True,
    degree = 3,
  )
  under_door_wire = under_door_curve.toShape().to_wire()
  
  def half_shape(k, dir, radius):
    e4ins = [elidupree_4in_wire(radius, index) for index in reversed(range (10))]
    start = Part.makeLoft (e4ins
    + [under_door_wire.translated (vector (40*(index-5)/10, 0, 0)) for index in range (6)]
    #+ [elidupree_4in_wire(1, elidupree_4in_output_outer_radius - wall_thickness, index) for index in range (5)]
    , )
    #start.sewShape()
    #print(start.fix(0.01, 0.005, 0.02))
    
    show (start, "start"+k, invisible = True)
    outside = start.makeOffsetShape(-wall_thickness, 0.01)#, fill=True)
    #show(start.Face6, "ver"+k)
    #adapter = start.makeThickness([start.Face6], wall_thickness, 0.01)
    
    show (outside, "outside"+k, invisible = True)
    
    cover1 = Part.Face([under_door_wire.makeOffset2D(wall_thickness), under_door_wire])
    show(cover1, "cover1"+k, invisible = True)
    cover2 = Part.Face([e4ins[0].makeOffset2D(wall_thickness), e4ins[0]])
    
    solid = Part.Solid(Part.Shell(Part.Compound([
      start, outside, cover1, cover2
    ]).Faces))
    if dir == 1:
      solid = solid.mirror(vector(), vector(1,0,0))
    show(solid, "solid"+k, invisible = True)
    
    import MeshPart
    mesh = MeshPart.meshFromShape(solid, 0.005, 0.1)
    Mesh.show(mesh, "mesh"+k)
  
  half_shape("intake", -1, elidupree_4in_intake_inner_radius)
  half_shape("output", 1, elidupree_4in_output_outer_radius - wall_thickness)
  
  
  

def CPAP_to_anemometer_solid():
  anemometer_inner_radius = 26/2
  CPAP_wire = Part.Shape([Part.Circle (vector(), vector (0, 0, 1), CPAP_outer_radius)]).to_wire()
  anemometer_wire = Part.Shape([Part.Circle (vector(), vector (0, 0, 1), anemometer_inner_radius + single_wall_thickness)]).to_wire()
  
  adapter = Part.makeLoft ([anemometer_wire.translated (vector (0, 0, index*5)) for index in range (5)]
  + [CPAP_wire.translated (vector (0, 0, 60+index*4)) for index in range (5)], True, False, False, 5)
  
  show (adapter, "adapter")
  
def fan_0802GS_to_CPAP_solid():
  CPAP_wire = Part.Shape([Part.Circle (vector(), vector (0, 0, 1), CPAP_outer_radius)]).to_wire()
  a = 28.5/2 + 0.5
  b = 26.5/2 + 0.5
  fan_wire = FreeCAD_shape_builder().build([
    start_at (a, b),
    horizontal_to (-a),
    vertical_to (-b),
    horizontal_to(a),
    close()
  ]).to_wire()
  
  adapter = Part.makeLoft ([fan_wire.translated (vector (0, 0, index*2)) for index in range (5)]
  + [CPAP_wire.translated (vector (0, 0, 30+index*4)) for index in range (5)], True, False, False, 5)
  
  show (adapter, "adapter")

def CPAP_to_CPAP():
  wall_thickness = single_wall_thickness*2 # make 'em tough because you put a bunch of force on these things
  end_length = 16
  diagonal_size = 3
  part = FreeCAD_shape_builder().build([
    start_at (CPAP_outer_radius - wall_thickness, 0),
    horizontal_to (CPAP_outer_radius),
    vertical_to (end_length),
    diagonal_to (CPAP_outer_radius + diagonal_size, end_length+diagonal_size),
    diagonal_to (CPAP_outer_radius, end_length+diagonal_size+diagonal_size),
    vertical_to (end_length+diagonal_size+diagonal_size+end_length),
    horizontal_to(CPAP_outer_radius - wall_thickness),
    close()
  ]).as_xz().revolve (vector(), vector (0, 0, 1), 360)
  
  show (part, "part")

def run(g):
  for key, value in g.items():
    globals()[key] = value
  elidupree_4in_under_door()
  
  
  