########################################################################
########  Split/assemble components into printable parts  #######
########################################################################

def reflected (components):
  return components + [component@Reflect(Right) for component in components]
  
@run_if_changed
def make_FDM_printable_lower_side():
  lower_side = Compound ([
    intake_wall,
    #intake_support,
    intake_fins,
  ])
  #preview(lower_side)
  save("lower_side", lower_side)
  save_STL("lower_side", lower_side)
  
  #save_STL("non_intake_side", non_intake_side)


@run_if_changed
def make_FDM_printable_headband():
  headband_final = Compound ([
    standard_headband.intersection(HalfSpace(temple, Back)),
    standard_headband_wave,
  ]
  + reflected ([
    temple_block,
    temple_extender,
    #upper_side_rim,
    temple_knob,
  ]))
  save("headband_final", headband_final)
  save_STL("headband_final", headband_final)

preview (
  lower_side,
  #non_intake_side,
  headband_final,
  neck_curve,
  chin_cloth_lip,

  Edge(shield_source_curve),
  Edge(shield_top_curve.curve),
  shield_source_points,
  side_shield_lip_points,
  #eye_lasers,
  #LoadSTL ("private/face5_for_papr.stl"),
  
  #unrolled_shield_wire@Translate(100, 0, 0),
  #forehead_cloth_wire@Translate(0, 350, 0),
  #chin_cloth_wire@Translate(-300, 0, 0),
)

'''
@run_if_changed
def make_FDM_printable_hook_skirt():
  save_STL("hook_skirt", hook_skirt)


@run_if_changed
def make_combined():
  combined = Compound ([
    headband_final @ Translate(0,0,-headband_top) @ Rotate(Front, degrees=180),
    top_rim_final @ Translate(0,0,-headband_top) @ Rotate(Front, degrees=180) @ Translate(0, -30, 13),
    overhead_strap @ Translate(overhead_strap_width/2, 0, 0)@Rotate (Front, degrees=90)@Rotate (Up, degrees=80)@Translate(-100, -110, 0),
    lower_side @(
      Transform(Right, Direction(side_curve_source_points[1], side_curve_source_points[2]), Right.cross(Direction(side_curve_source_points[1], side_curve_source_points[2])), Vector(Origin, side_curve_source_points[1])).inverse()
    ) @ Rotate(Front, degrees=180) @ Translate(0, -152, 18),
    
  ])
  save("combined_final", combined)
  save_STL("combined_final", combined, linear_deflection = 0.02, angular_deflection = 0.2)
  preview(combined)

preview(
  headband_final,
  overhead_strap,
  hook_skirt,
)
preview (
  standard_headband,
  temple_top_pegs,
  temple_block,
  top_rim,
  #upper_side_rim,
  #upper_side_rim@Reflect(Right),
  
  lower_side_rim,
  lower_side_extra_lip,
  lower_side_extra_lip@Reflect(Right),
  intake_solid,
  intake_solid@Reflect(Right),
  top_hook,
  side_hook,
  #shield_cross_sections,
  #Face (shield_surface),
  Edge(shield_source_curve),
  Edge(shield_top_curve.curve),
  shield_source_points,
  #eye_lasers,
  #LoadSTL ("private/face5_for_papr.stl"),
  
  unrolled_shield_wire,
  forehead_cloth_wire,
  chin_cloth_wire,
)
  '''
  