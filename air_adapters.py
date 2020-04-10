
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

def run(g):
  for key, value in g.items():
    globals()[key] = value
  elidupree_4in_to_CPAP_solid()
  
  
  