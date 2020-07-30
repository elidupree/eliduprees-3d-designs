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
  fan_0802GS_to_CPAP_solid()
  
  
  