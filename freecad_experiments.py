'''FREECADPATH = r"C:\Program Files\FreeCAD 0.18\bin"

import sys
sys.path.append(FREECADPATH)
 
import FreeCAD
       
       
import FreeCADGui 

FreeCADGui.showMainWindow()
import time
time.sleep(5)'''

import math
import PartDesignGui
import importlib

import freecad_utils
importlib.reload(freecad_utils)
from freecad_utils import *

import shape_builder
importlib.reload(shape_builder)
from shape_builder import *

FreeCAD = App
curse_freecad_types()

for document_name in list(FreeCAD.listDocuments().keys()):
  FreeCAD.closeDocument (document_name)
#Gui.activateWorkbench("PartWorkbench")

App.newDocument("Something")
#App.setActiveDocument("Something")

def make_snapper():
  layer_height = 0.12
  band_width = 6
  band_thickness = 1
  band_slack_length = 90
  band_lengthwise_stretch_distance = 100
  band_leeway = 1
  flex_perpendicular_leeway = 3
  claw_length = band_width + 2
  claw_deflect_distance = claw_length + 1
  claw_arm_length = 40
  claw_solid_length = 18
  flex_length = 12
  flex_thickness = 1
  flex_support_length = 6
  claw_thickness = 2.5
  claw_width = 6
  motion_distance = 100
  channel_depth = 6
  slider_channel_tolerance = 0.4
  additional_deflector_leeway = 0.3
  channel_wall_thickness = 3
  channel_stop_thickness = 0.5
  deflector_peg_diameter = 3
  deflector_peg_length = 2
  deflector_thickness = 1
  deflector_slope = 0.2
  releaser_slope = 0.6
  releaser_extra_length = 5
  sacrifical_bridges_radius = layer_height / 2

  deflector_peg_radius = deflector_peg_diameter/2
  deflector_radius = deflector_thickness/2

  claw_right = 0
  claw_left = claw_right - claw_thickness
  slider_left = claw_left - flex_perpendicular_leeway/2
  deflector_peg_left = claw_left
  deflector_peg_right = deflector_peg_left + deflector_peg_diameter
  claw_solid_right = claw_left + claw_solid_length
  flex_right = claw_right + claw_arm_length
  flex_left = flex_right - flex_length
  flex_support_right = flex_right + flex_support_length

  flex_top = 0
  claw_top = flex_top + claw_length
  flex_bottom = flex_top - flex_thickness
  claw_solid_bottom = flex_top - claw_thickness
  deflector_top_center = flex_top - deflector_radius
  deflector_fully_down_center = deflector_top_center - claw_deflect_distance
  deflector_peg_bottom = flex_top - deflector_thickness - deflector_peg_diameter - slider_channel_tolerance
  slider_top = deflector_peg_bottom - claw_deflect_distance - slider_channel_tolerance
  slider_bottom = slider_top - channel_depth
  channel_floor_bottom = slider_bottom - channel_wall_thickness
  slider_vertical_middle = (slider_top + slider_bottom)/2
  deflector_peg_horizontal_middle = claw_left + deflector_peg_radius
  deflector_peg_vertical_middle = deflector_peg_bottom + deflector_peg_radius

  claw_front = - claw_width/2
  claw_back = claw_front + claw_width
  slider_protrusions_front = claw_front - deflector_peg_length
  slider_protrusions_back = claw_back + deflector_peg_length


  channel_left_stop = slider_left
  channel_right_stop = flex_support_right + motion_distance
  deflector_left_end = deflector_peg_right + flex_perpendicular_leeway/2
  deflector_left_end_center = deflector_left_end + deflector_radius
  deflector_fully_down_horizontal = claw_right + band_thickness*2 + band_leeway*2 + (deflector_peg_horizontal_middle - claw_left)
  deflector_right_end_center = deflector_fully_down_horizontal + claw_deflect_distance/deflector_slope
  releaser_fully_down_horizontal = deflector_peg_horizontal_middle + motion_distance
  releaser_left_end_center = releaser_fully_down_horizontal - claw_deflect_distance/releaser_slope
  releaser_right_end_center = releaser_fully_down_horizontal + releaser_extra_length

  """slider_main_part = FreeCAD_shape_builder ().build ([
    start_at (flex_support_right, slider_bottom),
    horizontal_to (slider_left), vertical_to (slider_top), horizontal_to (flex_right), vertical_to (flex_bottom), horizontal_to (flex_left), diagonal_to (claw_solid_right, claw_solid_bottom), horizontal_to (deflector_peg_right),
    
    #vertical_to (deflector_peg_bottom + deflector_peg_radius),
    #arc_through_to ((deflector_peg_horizontal_middle, deflector_peg_bottom), (deflector_peg_left, deflector_peg_bottom + deflector_peg_radius)),
    horizontal_to (deflector_peg_horizontal_middle),
    diagonal_to (claw_left, deflector_peg_bottom + deflector_peg_radius),
    
    vertical_to (claw_top), horizontal_to (claw_right), vertical_to (flex_top), horizontal_to (flex_support_right), close()
  ]).to_wire().to_face().fancy_extrude (vector (0, 0, 1), centered (claw_width))

  slider_triangle_part = FreeCAD_shape_builder ().build ([
    start_at(claw_front, slider_top),
    horizontal_to (claw_back),
    diagonal_to (slider_protrusions_back, slider_vertical_middle),
    diagonal_to (claw_back, slider_bottom),
    horizontal_to (claw_front),
    diagonal_to (slider_protrusions_front, slider_vertical_middle),
    close(),
  ]).rotated(vector(), vector (0, 1, 0), 90).to_wire().to_face().fancy_extrude (vector (1, 0, 0), bounds (slider_left, flex_support_right))

  deflector_peg_part = Part.makeCylinder (
    deflector_peg_radius, claw_width + deflector_peg_length*2,
    vector (deflector_peg_horizontal_middle, deflector_peg_vertical_middle, claw_front - deflector_peg_length),
    vector (0, 0, 1),
  )

  slider_part = slider_main_part.fuse ((slider_triangle_part, deflector_peg_part))

  edges = [edge
    for edge in slider_part.Edges
    if #FreeCAD.BoundBox (claw_right, flex_top, -100, claw_right, claw_top, 100).isInside (edge.BoundBox)
    # or
     FreeCAD.BoundBox (flex_right, flex_bottom, -100, flex_right, flex_bottom, 100).isInside (edge.BoundBox)
    #and not
     or FreeCAD.BoundBox (claw_right, claw_top, -100, claw_right, claw_top, 100).isInside (edge.BoundBox)
     or FreeCAD.BoundBox (claw_right, flex_top, -100, claw_right, claw_top, 0).isInside (edge.BoundBox)
     or FreeCAD.BoundBox (claw_right, flex_top, 0, claw_right, claw_top, 100).isInside (edge.BoundBox)
     or FreeCAD.BoundBox (claw_left, claw_top, -100, claw_right, claw_top, 0).isInside (edge.BoundBox)
     or FreeCAD.BoundBox (claw_left, claw_top, 0, claw_right, claw_top, 100).isInside (edge.BoundBox)
     
    ]

  slider_part = slider_part.makeFillet(1.5, edges) #[slider_part.Edges [index] for index in range (0, len (slider_part.Edges), 3)])

  channel_box = box (
    bounds (channel_left_stop - channel_stop_thickness, channel_right_stop),
    bounds (slider_bottom - channel_wall_thickness, flex_top),
    bounds (slider_protrusions_front - channel_wall_thickness, slider_protrusions_back + channel_wall_thickness)
  )

  wide_channel_part = FreeCAD_shape_builder ().build ([
    start_at(claw_front, slider_top),
    horizontal_to (slider_protrusions_front),
    vertical_to (flex_top),
    horizontal_to (slider_protrusions_back),
    vertical_to (slider_top),
    horizontal_to (claw_back),
    diagonal_to (slider_protrusions_back, slider_vertical_middle),
    diagonal_to (claw_back, slider_bottom),
    horizontal_to (claw_front),
    diagonal_to (slider_protrusions_front, slider_vertical_middle),
    close(),
  ]).rotated(vector(), vector (0, 1, 0), 90).to_wire().makeOffset2D (slider_channel_tolerance).to_face().fancy_extrude (vector (1, 0, 0), bounds (channel_left_stop, channel_right_stop))

  narrow_channel_part = FreeCAD_shape_builder ().build ([
    start_at(claw_front, slider_top),
    vertical_to (flex_top),
    horizontal_to (claw_back),
    vertical_to (slider_top),
    close(),
  ]).rotated(vector(), vector (0, 1, 0), 90).to_wire().makeOffset2D (slider_channel_tolerance + additional_deflector_leeway).to_face().fancy_extrude (vector (1, 0, 0), bounds (channel_left_stop, channel_right_stop))

  deflector_bounds = bounds (slider_protrusions_front - channel_wall_thickness, slider_protrusions_back + channel_wall_thickness)

  deflector_wire = FreeCAD_shape_builder ().build ([
    start_at (deflector_left_end_center, deflector_fully_down_center),
    horizontal_to (deflector_fully_down_horizontal),
    diagonal_to (deflector_right_end_center, deflector_top_center),
  ]).to_wire()
  deflector_part = deflector_wire.makeOffset2D (deflector_radius).to_face().fancy_extrude (vector (0, 0, 1), deflector_bounds)

  releaser_wire = FreeCAD_shape_builder ().build ([
    start_at (releaser_right_end_center, deflector_fully_down_center),
    horizontal_to (releaser_fully_down_horizontal),
    diagonal_to (releaser_left_end_center, deflector_top_center),
  ]).to_wire()
  releaser_part = releaser_wire.makeOffset2D (deflector_radius).to_face().fancy_extrude (vector (0, 0, 1), deflector_bounds)


  deflector_sacrificial_bridges_wire = deflector_wire.makeOffset2D (sacrifical_bridges_radius)
  releaser_sacrificial_bridges_wire = releaser_wire.makeOffset2D (sacrifical_bridges_radius)

  sacrificial_bridges_part = (Part.Face (deflector_sacrificial_bridges_wire).fuse (Part.Face ( releaser_sacrificial_bridges_wire))
    .fancy_extrude (vector (0, 0, 1), deflector_bounds)
    .translated(vector (0, - deflector_radius + sacrifical_bridges_radius, 0)))

  body_part = channel_box.cut(wide_channel_part).fuse ((deflector_part, releaser_part)).cut(narrow_channel_part).fuse (sacrificial_bridges_part)


  Part.show (slider_part, "SliderSquare")

  Part.show (body_part)

  Part.show (body_part.common(box (bounds (5, 10), bounds (-50, -5), centered (100))))"""




  popsicle_stick_width = 9.5
  popsicle_stick_thickness = 2.0

  wheel_thickness = claw_width
  wheel_paddle_length = band_width*1.5
  wheel_paddle_thickness = 5
  wheel_axle_hole_radius = 3.5
  wheel_middle_radius = 12
  wheel_shadow_radius = wheel_middle_radius + wheel_paddle_length
  wheel_housing_radius = (wheel_thickness/2) + 4
  wheel_slider_radius = wheel_shadow_radius + 4
  wheel_drag_bar_height = wheel_middle_radius + band_width/2
  wheel_drag_bar_right = wheel_slider_radius
  slider_link_joint_xy = vector (wheel_drag_bar_right, wheel_drag_bar_height)
  wheel_housing_offset = 5
  wheel_loose_leeway = 1
  wheel_axle_leeway = 0.4
  wheel_axle_length = wheel_thickness + 7 - wheel_axle_leeway*2
  tight_leeway = 0.2
  catch_flex_left = -30
  catch_flex_length = 15
  catch_diagonal_length = 5
  catch_depth = 2.5
  catch_slope = 6
  catch_solid_thickness = claw_thickness
  catch_flex_thickness = flex_thickness
  catch_tip_deflection_distance = catch_depth*2
  catch_tip_lowest_y = - wheel_shadow_radius - catch_solid_thickness - catch_tip_deflection_distance
  slider_thickness = 1
  slider_width = popsicle_stick_thickness + 1
  slider_top_y = slider_thickness/2
  slider_bottom_y = - slider_thickness/2


  wheel_axle_radius = wheel_axle_hole_radius - wheel_axle_leeway

  wheel_front = - wheel_thickness/2

  paddle_part = box (wheel_shadow_radius, centered (wheel_paddle_thickness), centered (wheel_thickness))

  paddle_catch_part = FreeCAD_shape_builder ().build ([
    start_at (wheel_shadow_radius, wheel_paddle_thickness/2),
    vertical_to (wheel_paddle_thickness/2 + catch_depth/catch_slope),
    diagonal_to (wheel_shadow_radius - catch_depth, wheel_paddle_thickness/2),
    close(),
  ]).to_wire().to_face().fancy_extrude (vector (0, 0, 1), centered (wheel_thickness))
  paddle_part = paddle_part.fuse (paddle_catch_part)

  paddle_part = paddle_part.makeChamfer(1, [edge
    for edge in paddle_part.Edges
    if not FreeCAD.BoundBox (-100, 0, -100, 100, 100, 100).isInside (edge.BoundBox)])

  paddle_chamfer = box (centered (wheel_paddle_thickness), centered (wheel_paddle_thickness), centered (wheel_thickness)).rotated (vector (), vector (0, 0, 1), 45).translated (vector (wheel_middle_radius - 0.5, 0, 0))
  paddle_part = paddle_part.fuse (paddle_chamfer)

  num_paddles = 12
  paddles = []
  for index in range (num_paddles):
    angle = index*360/num_paddles
    paddles.append (paddle_part.rotated (vector (), vector (0, 0, 1), angle))

  wheel_shadow = Part.makeCylinder (wheel_shadow_radius, wheel_thickness, vector (0, 0, wheel_front), vector (0, 0, 1))
  wheel_axle_hole = Part.makeCylinder (wheel_axle_hole_radius, wheel_thickness, vector (0, 0, wheel_front), vector (0, 0, 1))
  wheel = Part.makeCylinder (wheel_middle_radius, wheel_thickness, vector (0, 0, wheel_front), vector (0, 0, 1)).fuse (paddles).cut (wheel_axle_hole )

  #hack = Part.makeLine ((0, 0, 0), (0, 0, 0.1))
  #wheel = wheel.makeChamfer(0.8, [edge for edge in wheel.Edges if edge.distToShape(hack)[0] <= wheel_middle_radius + 0.1])

  wheel_middle_extended = Part.makeCylinder (wheel_middle_radius, wheel_thickness + wheel_loose_leeway*2, vector (0, 0, wheel_front - wheel_loose_leeway), vector (0, 0, 1))

  wheel_housing_face = FreeCAD_shape_builder ().build ([
    start_at(- wheel_slider_radius + wheel_housing_offset, 0),
    diagonal_to (0, wheel_middle_radius - wheel_housing_offset),
    diagonal_to (wheel_middle_radius + wheel_housing_offset, wheel_middle_radius - wheel_housing_offset),
    diagonal_to (wheel_drag_bar_right, wheel_drag_bar_height),
    diagonal_to (wheel_slider_radius - wheel_housing_offset, 0),
    diagonal_to (catch_flex_left, - wheel_shadow_radius),
    close(),
  ]).to_wire().makeOffset2D (wheel_housing_offset).to_face()
  wheel_housing_part = wheel_housing_face.fancy_extrude (vector (0, 0, 1), centered (wheel_housing_radius*2))

  slider_part = wheel_housing_face.fancy_extrude (vector (0, 0, 1), centered ((wheel_housing_radius + slider_width)*2))
  slider_part_box = box (centered (100), centered (slider_thickness), centered (100))
  slider_part = slider_part.common (slider_part_box)

  catch_tip_xy = vector (0 + wheel_shadow_radius, - wheel_shadow_radius)

  catch_top = [start_at(catch_flex_left, - wheel_shadow_radius),
    horizontal_to (0 + wheel_paddle_thickness/2 + catch_depth/catch_slope),
    diagonal_to (0 + wheel_paddle_thickness/2,- wheel_shadow_radius + catch_depth),
    diagonal_to (catch_tip_xy),]


  catch_part = FreeCAD_shape_builder ().build (catch_top + [
    vertical_to (- wheel_shadow_radius - catch_solid_thickness),
    horizontal_to (catch_flex_left + catch_flex_length + catch_diagonal_length),
    diagonal_to (catch_flex_left + catch_flex_length, - wheel_shadow_radius - catch_flex_thickness),
    horizontal_to (catch_flex_left),
    close(),
  ]).to_wire().to_face().fancy_extrude (vector (0, 0, 1), centered (wheel_thickness))

  catch_shadow_part = FreeCAD_shape_builder ().build (catch_top + [
    vertical_to (- wheel_shadow_radius - 100),
    horizontal_to (catch_flex_left),
    close(),
  ]).to_wire().to_face().fancy_extrude (vector (0, 0, 1), centered ( wheel_thickness + wheel_loose_leeway*2)).translated (vector (0, 3, 0))


  axle_cut_part = box (bounds (-100, - wheel_axle_radius*math.sin(math.tau / 8)), centered (100), centered (100))

  axle_part = Part.makeCylinder (wheel_axle_radius, wheel_axle_length, vector (0, 0, - wheel_axle_length/2), vector (0, 0, 1)).cut(axle_cut_part)
  axle_hole_part = axle_part.makeOffsetShape (tight_leeway, 0.03)

  def do_axle (horizontal, vertical, angle):
    nonlocal wheel_housing_part
    wheel_housing_part = wheel_housing_part.cut(axle_hole_part
      .rotated (vector (), vector (0, 0, 1), angle)
      .translated (vector (horizontal, vertical, 0)))
    

  wheel_housing_part = wheel_housing_part.fuse (slider_part)
  wheel_housing_part = wheel_housing_part.cut (wheel_shadow.makeOffsetShape (wheel_loose_leeway, 0.1))
  wheel_housing_part = wheel_housing_part.fuse (wheel_middle_extended.cut (wheel_shadow.makeOffsetShape (wheel_axle_leeway, 0.1)))
  do_axle (0, 0, 0)
  do_axle (wheel_drag_bar_right, wheel_drag_bar_height, 180)
  do_axle (catch_flex_left + wheel_axle_hole_radius+2, -wheel_shadow_radius + wheel_axle_hole_radius + 5, 180)
  wheel_housing_part = wheel_housing_part.cut(catch_shadow_part).fuse(catch_part)

  wheel_housing_space_needed_radius = wheel_housing_radius + 0.3 # theoretically 14 wide, observed 14.6 after printing and assembly; originally gave it an extra 0.1 on each side, but no need for that based on observed tolerances
  """channel_holder_outside = 1
  channel_holder_hole_depth = popsicle_stick_width*0.7
  channel_holder_horizontal_radius = wheel_housing_space_needed_radius + wheel_axle_leeway + popsicle_stick_thickness + tight_leeway + channel_holder_outside
  channel_holder_vertical_radius = slider_thickness/2 + wheel_axle_leeway + popsicle_stick_width + tight_leeway + channel_holder_outside

  channel_holder_part = FreeCAD_shape_builder (zigzag_length_limit = 3, zigzag_depth = 1).build ([
    start_at(- channel_holder_horizontal_radius, - channel_holder_vertical_radius),
    horizontal_to (channel_holder_horizontal_radius),
    vertical_to (channel_holder_vertical_radius),
    horizontal_to (- channel_holder_horizontal_radius),
    close(),
  ]).as_yz().to_wire().to_face().fancy_extrude (vector (channel_holder_outside + channel_holder_hole_depth, 0, 0))

  def channel_holder_hole(horizontal, vertical):
    hole = box (
      channel_holder_hole_depth,
      centered (popsicle_stick_width + tight_leeway*2),
      centered (popsicle_stick_thickness + tight_leeway*2),
    )
    hole.translate (vector (0,
      vertical*(slider_thickness/2 + wheel_axle_leeway + popsicle_stick_width/2),
      horizontal*(wheel_housing_space_needed_radius + wheel_axle_leeway + popsicle_stick_thickness/2)
    ))
    return hole
    
    
  channel_holder_part = channel_holder_part.cut ([
    channel_holder_hole (horizontal, vertical)
    for horizontal in [-1, 1] for vertical in [-1, 1]
  ])"""



  farthest_left = -75
  handle_motion_distance = 25
  string_motion_distance = 15 # should be handle_motion_distance, but experimentally determined that we only see around 15mm in practice due to various tolerances
  band_lever_wall = 1
  band_lever_thickness = band_width + band_lever_wall*2
  band_lever_tip_circle_radius = 5
  band_lever_peg_radius = 1.5
  band_lever_peg_to_tip = band_lever_tip_circle_radius*math.tau*0.75
  band_lever_tip_xz = vector (0 + wheel_paddle_thickness*1.5, -50 + band_lever_peg_to_tip)
  band_lever_tip_stretched_xz = vector (farthest_left, -100) # yes, not exact, that's fine
  band_lever_length = 90
  band_lever_pivot_xz = arc_center ([band_lever_tip_xz, band_lever_tip_stretched_xz], band_lever_length)
  band_lever_pivot_to_tip_xz = band_lever_tip_xz - band_lever_pivot_xz
  band_lever_pivot_to_tip_stretched_xz = band_lever_tip_stretched_xz - band_lever_pivot_xz

  print(band_lever_pivot_xz)

  band_center_y = wheel_middle_radius + wheel_paddle_length/2
  band_lever_bottom_y = band_center_y - band_lever_thickness/2
  band_lever_top_y = band_center_y + band_lever_thickness/2
  #main_frame_bottom_y = slider_bottom_y - wheel_axle_radius - 1
  wheel_housing_right_z = -wheel_housing_space_needed_radius
  wheel_housing_front_x = catch_flex_left - wheel_housing_offset
  wheel_housing_back_x = wheel_drag_bar_right + wheel_housing_offset
  wheel_housing_back_stretched_x = wheel_housing_back_x + string_motion_distance
  wheel_housing_bottom_y = catch_tip_lowest_y
  wheel_part_top_y = wheel_shadow_radius
  main_frame_front_x = -wheel_slider_radius #wheel_housing_front_x - wheel_axle_leeway - 1
  main_frame_back_x = wheel_housing_back_stretched_x + wheel_axle_leeway + 1
  main_frame_around_pivot_radius = 5
  main_frame_strut_thickness = 6
  band_room_radius = band_lever_tip_circle_radius + band_thickness*3
  main_frame_bottom_y = wheel_housing_bottom_y - wheel_loose_leeway - main_frame_strut_thickness
  


  band_lever_angle = band_lever_pivot_to_tip_xz.angle()
  band_lever_stretched_angle = band_lever_pivot_to_tip_stretched_xz.angle()
  band_lever_rotation_angle = band_lever_stretched_angle - band_lever_angle
  # we need string_motion_distance to cause band_lever_rotation_angle
  # this angle is in radians, so conveniently,
  band_lever_string_radius = band_lever_rotation_angle*string_motion_distance
  print (band_lever_rotation_angle*360/math.tau)

  band_lever_pivot_center = vector (band_lever_pivot_xz [0], band_center_y, band_lever_pivot_xz [1])
  def along_band_lever (distance):
    return (band_lever_pivot_to_tip_xz)*(distance)/(band_lever_length)

  band_lever_tip_circle_center_xz = band_lever_pivot_xz + along_band_lever (band_lever_length -band_lever_tip_circle_radius)
  band_lever_tip_circle = (
    band_lever_tip_circle_center_xz - band_lever_pivot_xz,
    band_lever_tip_circle_radius
  )
  band_lever_string_circle = (vector(), band_lever_string_radius)
  #band_lever_peg_room_circle = (band_lever_peg - band_lever_pivot, band_lever_peg_room_radius)

  a,b = circle_circle_tangent_segment (band_lever_tip_circle, band_lever_string_circle)
  d,c = circle_circle_tangent_segment (band_lever_tip_circle, band_lever_string_circle, -1, -1)

  direction = (c-d).angle()
  normal_xz =(c-d).normalized()
  perpendicular_xz =vector (angle = direction + math.tau/4)
  something_xz = (band_lever_tip_circle_center_xz - band_lever_pivot_xz) + normal_xz*(band_lever_tip_circle_radius + band_room_radius/2)
  whatever_xz = something_xz + perpendicular_xz*band_lever_tip_circle_radius
  half_exit_offset_xz = normal_xz*(band_thickness + band_lever_peg_radius)

  other_xz = whatever_xz + half_exit_offset_xz
  other_2_xz = whatever_xz - half_exit_offset_xz

  mid_xz = point_circle_tangent (
        other_xz,
        (
    band_lever_tip_circle_center_xz - band_lever_pivot_xz,
    band_room_radius
  ),
        -1,
      )
  mid_2_xz = point_circle_tangent (
      other_2_xz,
      band_lever_tip_circle,
      -1,
    )

  band_lever_part = FreeCAD_shape_builder (zigzag_length_limit = 8, zigzag_depth = 1).build ([
    start_at(a),
    diagonal_to (a - (a-b).normalized() * 7),
    diagonal_to (b),
    arc_radius_to(- band_lever_string_radius, c, -1),
    diagonal_to (other_xz),
    #diagonal_to (other_xz + (mid_xz - other_xz).normalized()*band_lever_peg_radius),
    #diagonal_to (other_2_xz + (mid_2_xz - other_2_xz).normalized()*band_lever_peg_radius),
    diagonal_to (other_2_xz),
    diagonal_to (d),
    arc_radius_to(band_lever_tip_circle_radius, a, 1),
  ]).as_xz().to_wire().to_face().fancy_extrude (vector (0, 1, 0), centered (band_lever_thickness))
  #print(band_lever_part)

  string_holder_radius = band_lever_thickness*0.5/math.sin (math.tau/8)
  string_holder_edges_radius =band_lever_string_radius + string_holder_radius*(1 - math.sin (math.tau/8))
  band_lever_string_holder = FreeCAD_shape_builder ().build ([
    start_at(vector(10)),
    horizontal_to (string_holder_edges_radius),
    arc_radius_to (-string_holder_radius,
      (string_holder_edges_radius, band_lever_thickness),
      1,
    ),
    horizontal_to(10),
    close(),
  ]).to_wire().to_face().revolve (vector(), vector (0, 1, 0), 360).translated (vector (0, - band_lever_thickness/2, 0))
  #hack = band_lever_part
  band_lever_part = band_lever_part.fuse (band_lever_string_holder)
  #print(band_lever_part)
  #band_lever_part = band_lever_part.fuse (Part.makeCylinder (band_lever_string_radius, band_lever_thickness, vector(), vector (0, 1, 0)))

  string_attach_part = box (bounds (- 7, 0), centered (band_lever_thickness), centered (8)).cut (box (bounds (-7 + 1.5, 0), centered (band_lever_thickness - 1.5*2), centered (8)))
  string_attach_part = string_attach_part.makeChamfer (0.5, string_attach_part.Edges)

  band_lever_part = band_lever_part.fuse (string_attach_part.rotated (vector(), vector (0, 1, 0), (math.tau*0.75-(b-a).angle())*360/math.tau).translated (vector (b[0],0,b[1])))


  band_lever_cut_part = FreeCAD_shape_builder (zigzag_length_limit = 10, zigzag_depth = 1).build ([
    start_at(other_2_xz),
    diagonal_to (mid_2_xz),
    arc_radius_to(band_lever_tip_circle_radius, d, -1),
    diagonal_to (
    (band_lever_tip_circle_center_xz - band_lever_pivot_xz) - vector (band_room_radius, 0)
  ),
    arc_radius_to(band_room_radius, 
      mid_xz
    , 1),
    
    diagonal_to (other_xz),
    close(),
    
  ]).as_xz().to_wire().to_face().fancy_extrude (vector (0, 1, 0), centered (band_width, on = 1))

  foo_xz = whatever_xz - normal_xz*band_thickness*0.70
  band_lever_peg_part = Part.makeCylinder (band_lever_peg_radius, band_lever_thickness, vector (- band_lever_peg_radius, -band_lever_thickness/2, 0), vector (0, 1, 0)
  ).rotated (vector (), vector (0, 1, 0), -(direction + math.tau/4)*360/math.tau).translated (vector (foo_xz[0], 0, foo_xz[1]))

  band_lever_part = band_lever_part.cut (band_lever_cut_part)
  band_lever_part = band_lever_part.fuse (band_lever_peg_part)
  band_lever_part = band_lever_part.cut (Part.makeCylinder (wheel_axle_hole_radius, 100, vector (0, -50, 0), vector (0, 1, 0)))


  '''a,b = circle_circle_tangent_segment (band_lever_tip_circle, band_lever_peg_room_circle, 1, -1)
  d = vector (-1000, 1000)
  c = point_circle_tangent (d, band_lever_peg_room_circle)
  band_lever_band_room_part = FreeCAD_shape_builder ().build ([
    start_at(b),
    arc_radius_to( band_lever_peg_room_radius, c, -1),
    diagonal_to (d),
    diagonal_to (along_band_lever (band_lever_length)),
    arc_radius_to(band_lever_tip_circle_radius, a, 1),
    close(),
  ]).as_xz().to_wire().to_face().fancy_extrude (vector (0, 1, 0), centered (band_width, on = band_lever_thickness/2))
  #print(band_lever_part)
  band_lever_part = band_lever_part.cut (band_lever_band_room_part)

  band_lever_peg_cut_part = box (bounds (-100, - band_lever_peg_radius*math.sin(math.tau / 8)), centered (100), centered (100))
  band_lever_peg_part = Part.makeCylinder (band_lever_peg_radius, band_lever_thickness, vector(), vector (0, 1, 0)).cut(band_lever_peg_cut_part)
  band_lever_peg_hole_part = band_lever_peg_part.makeOffsetShape (tight_leeway, 0.03)
  band_lever_peg_part = band_lever_peg_part.fuse (Part.makeCylinder (band_lever_peg_radius + 1, 1, vector(0, band_lever_thickness, 0), vector (0, 1, 0))).cut(band_lever_peg_cut_part).rotated (vector(), vector (0, 1, 0), 65).translated (vector((band_lever_peg - band_lever_pivot)[0], 0, (band_lever_peg - band_lever_pivot)[1]))
  band_lever_peg_hole_part = band_lever_peg_hole_part.rotated (vector(), vector (0, 1, 0), 65).translated (vector((band_lever_peg - band_lever_pivot)[0], 0, (band_lever_peg - band_lever_pivot)[1]))

  band_lever_part = band_lever_part.cut (band_lever_peg_hole_part)'''


  band_lever_part.translate (band_lever_pivot_center)
  band_lever_peg_part.translate (band_lever_pivot_center)
  
  
    
  
  handle_height = 130
  handle_thickness = 26
  link_radius = wheel_housing_offset
  link_thickness = wheel_thickness
  max_space_inside_hand = 60
  handle_lever_radius = 8.4
  handle_side_thickness = handle_thickness/2 - (handle_lever_radius + wheel_axle_leeway)
  handle_fixed_size_x = 15
  string_passage_diameter = 3.5
  
  handle_lever_extra_motion_leeway = 2
  
  link_handle_joint_xy = vector (main_frame_back_x + 40 + main_frame_strut_thickness + handle_lever_radius - handle_lever_extra_motion_leeway, slider_link_joint_xy [1])
  handle_link_joint_xy = link_handle_joint_xy + vector(-handle_lever_extra_motion_leeway, 0)
  handle_link_joint_stretched_xy = link_handle_joint_xy + vector (handle_motion_distance + handle_lever_extra_motion_leeway, 0)
  handle_lever_pivot_xy = (handle_link_joint_xy + handle_link_joint_stretched_xy)/2+ vector (0, - handle_height)
  handle_lever_logical_length = (handle_link_joint_xy - handle_lever_pivot_xy).Length
  handle_lever_angle = (handle_link_joint_xy - handle_lever_pivot_xy).angle()
  handle_lever_stretched_angle = (handle_link_joint_stretched_xy - handle_lever_pivot_xy).angle()
  
  handle_lever_rotation_angle = handle_lever_angle - handle_lever_stretched_angle
  handle_lever_beyond_pivots_radius = handle_lever_radius
  link_highest_y = handle_lever_pivot_xy [1] + handle_lever_logical_length + link_radius + 1
  
  handle_fixed_back_x = handle_link_joint_xy [0] -8.4+ max_space_inside_hand
  main_frame_top_y = link_highest_y + wheel_loose_leeway + main_frame_strut_thickness
  
  
  link_part = FreeCAD_shape_builder (zigzag_length_limit = 6, zigzag_depth = 1).build ([
    start_at(link_handle_joint_xy + vector (0, - link_radius)),
    arc_through_to (
      link_handle_joint_xy + vector (link_radius, 0),
      link_handle_joint_xy + vector (0, link_radius)
    ),
    horizontal_to (slider_link_joint_xy [0]),
    arc_through_to (
      slider_link_joint_xy + vector (-link_radius, 0),
      slider_link_joint_xy + vector (0, -link_radius)
    ),
    close(),
  ]).to_wire().to_face().fancy_extrude (vector (0, 0, 1), centered (link_thickness))
  link_shadow_part = link_part.makeOffsetShape (wheel_axle_leeway, 0.03)
  link_stretched_shadow_part = link_shadow_part.translated (vector (handle_motion_distance, 0))
  for position in [handle_link_joint_xy, slider_link_joint_xy]:
    link_part = link_part.cut (Part.makeCylinder (wheel_axle_hole_radius, 100, position + vector (0, 0, -50), vector (0, 0, 1)))
    
  wheel_housing_part = wheel_housing_part.cut(link_shadow_part)
  wheel_housing_split = box (centered (100), centered (100), bounds (wheel_thickness/2, 100))
  wheel_housing_main = wheel_housing_part.cut (wheel_housing_split)
  wheel_housing_other = wheel_housing_part.common (wheel_housing_split)
  
  handle_lever_profile = FreeCAD_shape_builder().build ([
    start_at (0, handle_lever_radius),
    arc_through_to ((-handle_lever_radius, 0), (0, -handle_lever_radius)),
    horizontal_to (20),
    vertical_to (handle_lever_radius),
    close(),
  ]).as_xz().to_wire()
  
  
  foo_xy = vector (20, handle_lever_logical_length+handle_lever_beyond_pivots_radius)
  bar_xy = point_circle_tangent (
    foo_xy,
    (vector(), handle_lever_radius),
    -1
  )
  handle_lever_back_angle = (foo_xy - bar_xy).angle()
  handle_lever_filter_cylinder = Part.makeCylinder (handle_lever_logical_length + handle_lever_beyond_pivots_radius, 50, vector (0, 0, -25), vector (0, 0, 1))
  handle_lever_side_filter = FreeCAD_shape_builder().build ([
    start_at (- handle_lever_radius, handle_lever_logical_length+handle_lever_beyond_pivots_radius),
    vertical_to (0),
    arc_through_to(
      vector (0, -handle_lever_radius),
      bar_xy,
    ),
    diagonal_to (foo_xy),
    close(),
  ]).to_wire().to_face().fancy_extrude (vector (0, 0, 1), centered (50)).common (handle_lever_filter_cylinder )
  
  handle_lever_fillet_size = 6
  
  handle_lever_shadow = FreeCAD_shape_builder().build ([
    start_at (-200, 200),
    vertical_to (- handle_lever_radius),
    arc_through_to(
      vector (angle = math.tau*7/8, length = handle_lever_radius),
      bar_xy,
    ),
    diagonal_to (foo_xy),
    close(),
  ]).to_wire().to_face().fancy_extrude (vector (0, 0, 1), centered (handle_lever_radius*2)).common (
    # slightly higher radius than the regular filter - housing should rub on the sides, but not the end
    Part.makeCylinder (handle_lever_logical_length + handle_lever_beyond_pivots_radius + 0.7, 50, vector (0, 0, -25), vector (0, 0, 1))
  ).translated (handle_lever_pivot_xy).rotated (handle_lever_pivot_xy, vector (0, 0, 1),-handle_lever_rotation_angle/2*360/math.tau)
  handle_lever_shadow = handle_lever_shadow.makeFillet(handle_lever_fillet_size, handle_lever_shadow.Edges)
  # note: in a test print with only wheel_axle_leeway, the handle gripped the lever tightly; with my cheap digital calipers, I measured that inserting the lever forced the handle sides apart by 0.5mm. Rounded up to 0.6mm for safety. (That counts both sides, so 0.3 for each side.)
  handle_lever_leeway = wheel_axle_leeway+0.3
  handle_lever_shadow = handle_lever_shadow.makeOffsetShape(handle_lever_leeway, 0.03)
  
  handle_lever_part = handle_lever_profile.to_face().fancy_extrude (vector (0, 1, 0), bounds (-handle_lever_radius, handle_lever_logical_length +handle_lever_beyond_pivots_radius))
  
  # note: handle_lever_shadow_2 is slightly the wrong shape in a couple of ways. It doesn't seem worth the effort to fix
  handle_lever_shadow_2 = handle_lever_part.makeFillet(handle_lever_fillet_size, handle_lever_part.Edges)
  handle_lever_shadow_2 = handle_lever_shadow_2.makeOffsetShape(handle_lever_leeway, 0.03)
  handle_lever_shadow_2.translate (handle_lever_pivot_xy + vector (0, 0.7))
  handle_lever_shadow_2.rotate (handle_lever_pivot_xy, vector (0, 0, 1),handle_lever_rotation_angle/2*360/math.tau)  
  #Part.show (handle_lever_shadow_2)
  handle_lever_part = handle_lever_part.common (handle_lever_side_filter)
  handle_lever_part.translate (handle_lever_pivot_xy)
  handle_lever_part.rotate (handle_lever_pivot_xy, vector (0, 0, 1),-handle_lever_rotation_angle/2*360/math.tau)  
  handle_lever_part = handle_lever_part.makeFillet(handle_lever_fillet_size, handle_lever_part.Edges)
  handle_lever_part = handle_lever_part.cut (link_stretched_shadow_part)
  handle_lever_part = handle_lever_part.cut (Part.makeCylinder (wheel_axle_hole_radius, 50, handle_lever_pivot_xy + vector (0, 0, -25), vector (0, 0, 1)))
  
  handle_link_axle_part = FreeCAD_shape_builder().build ([
    start_at (vector (angle = math.tau*3/8, length = wheel_axle_radius)),
    arc_radius_to (-wheel_axle_radius,vector (angle = math.tau*1/8, length = wheel_axle_radius), -1),
    close(),
  ]).to_wire().to_face().fancy_extrude (vector (0, 0, 1), centered(handle_lever_radius*2 + wheel_axle_radius*4))
  
  for direction in [-1, 1]:
    handle_link_axle_part = handle_link_axle_part.cut(Part.makeCylinder (
      string_passage_diameter/2,
      50,
      vector(0, -25, direction*(handle_lever_radius + wheel_axle_radius)),
      vector (0, 1, 0),
    ))
  
  handle_link_axle_part = handle_link_axle_part.rotated(vector(), vector(0,0,1), (handle_lever_back_angle - handle_lever_rotation_angle/2)*360/math.tau).translated (handle_link_joint_stretched_xy)
  
  handle_lever_part = handle_lever_part.cut (handle_link_axle_part.makeOffsetShape (tight_leeway, 0.03))
  
  handle_lever_part.rotate (handle_lever_pivot_xy, vector (0, 0, 1),handle_lever_rotation_angle*360/math.tau)
  handle_lever_part = handle_lever_part.cut (link_shadow_part)
  
  handle_lever_stretched_part = handle_lever_part.copy()
  handle_lever_part.rotate (handle_lever_pivot_xy, vector (0, 0, 1),-handle_lever_rotation_angle*360/math.tau)
  
  handle_fixed_profile = FreeCAD_shape_builder().build ([
    start_at (- handle_fixed_size_x, - handle_thickness/2),
    bezier ([(0, - handle_thickness/2), (0, handle_thickness/2), (- handle_fixed_size_x, handle_thickness/2)]),
    horizontal_to (-20 + handle_side_thickness/2),
    bezier([
      (-20, handle_thickness/2),
      (-20, -handle_thickness/2),
      (-20 + handle_side_thickness/2, -handle_thickness/2),
      ]),
    close(),
  ]).as_xz().to_wire()
  handle_fixed_profile.translate (vector (- handle_fixed_profile.BoundBox.XMax, 0, 0))
  #Part.show(handle_fixed_profile)
  
  handle_fixed_web_radius = 15
  web_xy = vector(0, -link_radius-15)
  foo_xy = web_xy + vector (handle_fixed_web_radius, 0) + vector (length = handle_fixed_web_radius, angle = math.tau*3/8)
  bar_xy = vector (foo_xy [0], web_xy[1]-(foo_xy [1]-web_xy[1]))
  handle_fixed_start_xy = vector (50, 50)
  handle_curve_end_xy = web_xy + vector (40, -80)
  handle_fixed_curve = FreeCAD_shape_builder().build ([
    start_at (handle_fixed_start_xy),
    bezier ([handle_fixed_start_xy + vector (0, -20), foo_xy + vector (15, 15), foo_xy]),
    arc_through_to (web_xy, bar_xy),
    bezier ([bar_xy + vector (25, -25), handle_curve_end_xy]),
  ]).to_wire()
  #Part.show (handle_fixed_curve)
  #Part.show(handle_fixed_curve.makeOffset2D(handle_fixed_size_x, openResult = False))
  #Part.show(handle_fixed_curve.makeOffset2D(-handle_fixed_size_x, openResult = False))
  #Part.show(handle_fixed_curve.makeOffset2D(handle_fixed_size_x, openResult = True))
  #Part.show(handle_fixed_curve.makeOffset2D(-handle_fixed_size_x, openResult = True))
  handle_curve_shadow = handle_fixed_curve.makeOffset2D(handle_fixed_size_x, openResult = True).fancy_extrude (vector (0, 0, 1), centered (500)).translated (vector (handle_fixed_back_x, handle_link_joint_xy [1])).extrude(vector(500, 0, 0))
  #Part.show(handle_curve_shadow)
  handle_fixed_profile.translate (handle_fixed_start_xy)
  #handle_fixed_part = handle_fixed_profile.to_face().fancy_extrude (vector (0.5, -1, 0).normalized(), bounds (-handle_lever_beyond_pivots_radius, handle_height +handle_lever_beyond_pivots_radius))
  handle_fixed_part = handle_fixed_curve.makePipeShell ([handle_fixed_profile], True, False, 1)
  handle_fixed_part = handle_fixed_part.translated (vector (handle_fixed_back_x, handle_link_joint_xy [1]))
  handle_curve_end_xy = handle_curve_end_xy + vector (handle_fixed_back_x, handle_link_joint_xy [1])
  
  handle_cover_around_axle_radius = wheel_axle_radius + wheel_loose_leeway
  handle_cover_inner_radius = handle_lever_logical_length + handle_cover_around_axle_radius
  
  # the 5mm are for the string knot
  handle_side_curve_center = handle_lever_pivot_xy + (handle_link_joint_stretched_xy - handle_lever_pivot_xy + vector(5, 0, 0)).normalized()*(handle_lever_logical_length)
  handle_side_segment = [
    handle_side_curve_center + vector(angle = handle_lever_stretched_angle - math.tau/2, length = handle_cover_around_axle_radius / math.sin(math.tau/8)),
    handle_lever_pivot_xy + (handle_link_joint_stretched_xy - handle_lever_pivot_xy).normalized()*(30) + vector(angle = handle_lever_stretched_angle - math.tau/4, length = 2)
  ]
  
  handle_pivot_strut_circle = (handle_lever_pivot_xy, 8)
  bar_xy = handle_curve_end_xy + vector(-10, 0)
  handle_strut_1 = FreeCAD_shape_builder().build ([
    start_at (handle_link_joint_xy + vector (-50, 100)),
    diagonal_to (handle_lever_pivot_xy + vector(-10, handle_cover_inner_radius, 0)),
    diagonal_to (handle_lever_pivot_xy + vector(0, handle_cover_inner_radius, 0)),
    arc_radius_to (-(handle_cover_inner_radius),
      handle_lever_pivot_xy + (handle_side_curve_center - handle_lever_pivot_xy).normalized()*(handle_cover_inner_radius)),
    arc_radius_to (-(handle_cover_around_axle_radius),
      point_circle_tangent (handle_side_segment [0], (handle_side_curve_center, handle_cover_around_axle_radius))),
    diagonal_to (handle_side_segment [0]),
    diagonal_to (handle_side_segment [1]),
    diagonal_to (point_circle_tangent (handle_side_segment [1], handle_pivot_strut_circle)),
    arc_radius_to (handle_pivot_strut_circle [1], point_circle_tangent (bar_xy, handle_pivot_strut_circle, -1)),
    diagonal_to (bar_xy),
    vertical_to(handle_link_joint_xy[1] + 100),
    close()
  ]).to_wire().to_face().fancy_extrude (vector (0, 0, 1), centered (handle_thickness))
  handle_strut_1 = handle_strut_1.makeFillet(2, handle_strut_1.Edges).cut (handle_curve_shadow)
  
  handle_fixed_part = handle_fixed_part.fuse (handle_strut_1)
  
  handle_fixed_part = handle_fixed_part.common (Part.makeCylinder (handle_lever_logical_length + handle_lever_beyond_pivots_radius + 6, handle_thickness, handle_lever_pivot_xy + vector (0, 0, - handle_thickness/2), vector (0, 0, 1))).cut(handle_lever_shadow)
  
  foo_xy = vector (main_frame_back_x, main_frame_bottom_y)
  bar_xy = point_circle_tangent (foo_xy, handle_pivot_strut_circle)
  perpendicular = vector (angle = math.tau/4+ (bar_xy - foo_xy).angle())
  handle_pivot_strut_2 = FreeCAD_shape_builder().build ([
    start_at (foo_xy),
    diagonal_to (bar_xy),
    diagonal_to (bar_xy + perpendicular*6),
    diagonal_to (foo_xy + perpendicular*6),
    close(),
  ]).to_wire().to_face().fancy_extrude (vector (0, 0, 1), centered (handle_thickness))
  handle_pivot_strut_2 = handle_pivot_strut_2.makeFillet(2, handle_pivot_strut_2.Edges).cut (handle_lever_shadow_2)
  
  handle_frame_strut = FreeCAD_shape_builder().build ([
    start_at (main_frame_back_x, main_frame_top_y),
    vertical_to (-200),
    horizontal_to (main_frame_back_x + main_frame_strut_thickness),
    vertical_to (slider_link_joint_xy [1] - link_radius -3),
    arc_radius_to (-(link_radius+3 + handle_cover_around_axle_radius), 
    (main_frame_back_x + main_frame_strut_thickness + link_radius+3 + handle_cover_around_axle_radius, handle_lever_pivot_xy[1] + handle_cover_inner_radius)),
    horizontal_to (handle_lever_pivot_xy [0]),
    vertical_to (main_frame_top_y),
close(),
  ]).to_wire().to_face().fancy_extrude (vector (0, 0, 1), centered (200)).cut (box (centered (500), bounds (slider_link_joint_xy [1] - link_radius -3, link_highest_y + wheel_loose_leeway), centered (link_thickness + wheel_loose_leeway*2))).cut (handle_lever_shadow_2)
  
  string_guide_thickness = link_radius*2
  string_guide_radius = string_guide_thickness*0.5/math.sin (math.tau/8)
  string_guide_edges_radius = 7
  string_guide_inner_radius = string_guide_edges_radius - string_guide_radius*(1 - math.sin (math.tau/8))
  string_guide_center_xz = vector (handle_link_joint_xy[0] - string_guide_inner_radius  - wheel_axle_radius - wheel_loose_leeway, handle_lever_radius + string_guide_inner_radius  + string_passage_diameter + wheel_loose_leeway)
  handle_string_guide = FreeCAD_shape_builder ().build ([
    start_at(vector(0, - string_guide_thickness)),
    horizontal_to (string_guide_edges_radius),
    arc_radius_to (-string_guide_radius,
      (string_guide_edges_radius, 0),
      1,
    ),
    horizontal_to(0),
    close(),
  ]).to_wire().to_face().revolve (vector(), vector (0, 1, 0), 360).translated (vector (string_guide_center_xz[0], handle_lever_pivot_xy[1] + handle_cover_inner_radius, string_guide_center_xz[1]))
  
  handle_frame_strut_top_filter = FreeCAD_shape_builder().build ([
    start_at(handle_lever_pivot_xy [0], 0),
    vertical_to (handle_thickness/2),
    bezier ([(string_guide_center_xz [0] + string_guide_edges_radius, handle_thickness/2), string_guide_center_xz + vector (string_guide_edges_radius, 0)]),
    arc_radius_to (string_guide_edges_radius, string_guide_center_xz + vector (0, string_guide_edges_radius)),
    bezier ([
      string_guide_center_xz + vector (-30, string_guide_edges_radius),
      vector (main_frame_back_x +20, 40),
      vector (main_frame_back_x, 40)]
      ),
    vertical_to (0),
    close(),
  ]).as_xz().to_wire().to_face().fancy_extrude (vector (0, 1, 0), centered (500))
  handle_frame_strut_top_filter = handle_frame_strut_top_filter.fuse (handle_frame_strut_top_filter.mirror (vector(), vector (0, 0, 1)))
  
  handle_frame_strut = handle_frame_strut.common (handle_frame_strut_top_filter)
  
  handle_side_filter = FreeCAD_shape_builder().build ([
    start_at(main_frame_top_y, 40),
    bezier ([
      vector (main_frame_bottom_y -25, 40),
      vector (main_frame_bottom_y -25, -40),
      vector (main_frame_top_y, -40)]
      ),
    close(),
  ]).as_yz().to_wire().to_face().fancy_extrude (vector (1, 0, 0), centered (500)).fuse (box (
    bounds (main_frame_back_x +20, 500),
    bounds (-500, main_frame_top_y),
    centered (500),
  ))
  
  handle_fixed_part = handle_fixed_part.fuse ([
   handle_frame_strut,
  handle_string_guide,
  handle_string_guide.mirror (vector(), vector (0, 0, 1)),
  ]).common (handle_side_filter)
  handle_fixed_part = handle_fixed_part.fuse(handle_pivot_strut_2)
  
  #handle_fixed_part = handle_fixed_part.makeFillet(0.9, handle_fixed_part.Edges)
  
  '''average_xy = (foo_xy + bar_xy + handle_lever_pivot_xy)/3
  inset_distance = 20
  blob = FreeCAD_shape_builder().build ([
    start_at (handle_lever_pivot_xy + (average_xy - handle_lever_pivot_xy).normalized()*inset_distance),
    diagonal_to (bar_xy + (average_xy - bar_xy).normalized()*inset_distance),
    diagonal_to (foo_xy + (average_xy - foo_xy).normalized()*inset_distance*1.5),
    close(),
  ]).to_wire().to_face().fancy_extrude(vector(0,0,1), centered(0.01)).makeOffsetShape (inset_distance, 0.03)
  #Part.show(blob)
  for direction in [-1, 1]:
    #Part.show(blob.translated (vector (0, 0, handle_thickness/2+ inset_distance -1)*direction))
    handle_fixed_part = handle_fixed_part.cut(blob.translated (vector (0, 0, handle_thickness/2+ inset_distance -2)*direction))'''
  
  
  handle_pivot_axle_part = FreeCAD_shape_builder().build ([
    start_at (vector (angle = math.tau*7/8, length = wheel_axle_radius)),
    arc_radius_to (-wheel_axle_radius,vector (angle = math.tau*5/8, length = wheel_axle_radius), -1),
    close(),
  ]).to_wire().to_face().fancy_extrude (vector (0, 0, 1), centered(handle_thickness)).translated (handle_lever_pivot_xy)

  handle_fixed_part = handle_fixed_part.cut (handle_pivot_axle_part.makeOffsetShape (tight_leeway, 0.03))
  
  another_cut_part = FreeCAD_shape_builder(zigzag_length_limit = 6, zigzag_depth = 1).build ([
    start_at (0, 0),
    diagonal_to (main_frame_back_x, -100),
    vertical_to (100),
    close(),
  ]).as_xz().to_wire().to_face().fancy_extrude (vector (0, 1, 0), centered(500))
  handle_fixed_part = handle_fixed_part.cut (another_cut_part)
  another_cut_part = FreeCAD_shape_builder(zigzag_length_limit = 6, zigzag_depth = 1).build ([
    start_at (main_frame_back_x + main_frame_strut_thickness + 50, 0),
    diagonal_to (main_frame_back_x + main_frame_strut_thickness, 100),
    vertical_to (-100),
    close(),
  ]).as_xz().to_wire().to_face().fancy_extrude (vector (0, 1, 0), bounds(-500, slider_link_joint_xy [1] - link_radius -3)).common(
    FreeCAD_shape_builder().build ([
      start_at (main_frame_back_x + main_frame_strut_thickness + 50, 0),
      diagonal_to (main_frame_back_x + main_frame_strut_thickness, slider_link_joint_xy [1] - link_radius -3),
      diagonal_to (main_frame_back_x + main_frame_strut_thickness - 1, slider_link_joint_xy [1] - link_radius -6),
      vertical_to (main_frame_bottom_y +6),
      diagonal_to (main_frame_back_x + main_frame_strut_thickness, main_frame_bottom_y +2),
      close(),
    ]).to_wire().to_face().fancy_extrude (vector (0, 0, 1), centered(500))
  )
  handle_fixed_part = handle_fixed_part.cut (another_cut_part)
  
  another_cut_part = FreeCAD_shape_builder(zigzag_length_limit = 6, zigzag_depth = 1).build ([
    start_at (handle_lever_pivot_xy [0], handle_thickness/2+5),
    vertical_to (handle_thickness/2),
    horizontal_to (handle_curve_end_xy [0]+ 50),
    vertical_to (-handle_thickness/2),
    horizontal_to (handle_lever_pivot_xy [0]),
    vertical_to (- handle_thickness/2-5),
    horizontal_to (handle_curve_end_xy [0]+ 55),
    vertical_to (handle_thickness/2+5),
    close(),
  ]).as_xz().to_wire().to_face().fancy_extrude (vector (0, 1, 0), centered(500))
  handle_fixed_part = handle_fixed_part.cut (another_cut_part)
  
  handle_fixed_part = handle_fixed_part.cut (handle_lever_shadow_2.rotated(handle_lever_pivot_xy, vector (0, 0, 1), 12).translated(vector(-10, 30, 0)))
  
  """main_frame_part = FreeCAD_shape_builder (zigzag_length_limit = 10, zigzag_depth = 1).build ([
    start_at(wheel_housing_front_x - wheel_axle_leeway, 0),
    vertical_to (wheel_housing_right_z - wheel_axle_leeway),
    horizontal_to (wheel_housing_back_stretched_x + wheel_axle_leeway),
    vertical_to (0),
    horizontal_to (main_frame_back_x),
    vertical_to (wheel_housing_right_z - slider_thickness - wheel_axle_leeway),
    diagonal_to (point_circle_tangent (
      vector (main_frame_back_x, wheel_housing_right_z - slider_thickness - wheel_axle_leeway),
      (band_lever_pivot_xz, band_lever_string_radius),
      -1,
    )),
    arc_radius_to(-band_lever_string_radius, 
      point_circle_tangent (
        vector (main_frame_front_x, wheel_housing_right_z - slider_thickness - wheel_axle_leeway),
        (band_lever_pivot_xz, band_lever_string_radius),
        1
      )
    , 1),
    diagonal_to (vector (main_frame_front_x, wheel_housing_right_z - slider_thickness - wheel_axle_leeway)),
    vertical_to (0),
    close(),
  ]).as_xz().to_wire().to_face().fancy_extrude (vector (0, 1, 0), bounds (main_frame_bottom_y, band_lever_bottom_y - wheel_loose_leeway))

  main_frame_part = main_frame_part.fuse (Part.makeCylinder (band_lever_string_radius, band_lever_bottom_y - wheel_axle_leeway - main_frame_bottom_y, vector (band_lever_pivot_xz [0], main_frame_bottom_y, band_lever_pivot_xz [1]), vector (0, 1, 0)))

  main_frame_part = main_frame_part.cut (box (
    bounds (wheel_housing_front_x - wheel_axle_leeway, wheel_housing_back_stretched_x + wheel_axle_leeway),
    centered (slider_thickness + wheel_axle_leeway*2),
    bounds (wheel_housing_right_z - slider_width - wheel_axle_leeway, 0),
  ))

  # sacrificial bridges
  main_frame_part = main_frame_part.fuse (box (
    bounds (wheel_housing_front_x - wheel_axle_leeway, wheel_housing_back_stretched_x + wheel_axle_leeway),
    bounds (slider_thickness/2 + wheel_axle_leeway, slider_thickness/2 + wheel_axle_leeway + 0.28),
    bounds (wheel_housing_right_z - slider_width - wheel_axle_leeway, 0),
  ))"""

  outer_corner_yz = vector (band_lever_bottom_y - wheel_axle_leeway - main_frame_strut_thickness, band_lever_pivot_xz [1] - main_frame_around_pivot_radius - 1.1)
  close_corner_yz = vector (main_frame_bottom_y, wheel_housing_right_z - wheel_axle_leeway)
  along_yz = (outer_corner_yz - close_corner_yz).normalized()
  perpendicular_yz = along_yz.rotated (90)
  close_inner_corner_yz = close_corner_yz + perpendicular_yz*main_frame_strut_thickness + along_yz*main_frame_strut_thickness*((-perpendicular_yz [1])/along_yz [1])
  outer_inner_corner_yz = outer_corner_yz + perpendicular_yz*main_frame_strut_thickness + along_yz*main_frame_strut_thickness*((-perpendicular_yz [0])/along_yz [0])

  main_frame_outer_wire = FreeCAD_shape_builder (zigzag_length_limit = main_frame_around_pivot_radius*2.4, zigzag_depth = - 1).build ([
    start_at (wheel_housing_bottom_y - wheel_loose_leeway, 0),
    horizontal_to (close_corner_yz [0]),
    vertical_to (close_corner_yz [1]),
    diagonal_to (outer_corner_yz),
    horizontal_to (band_lever_top_y + wheel_axle_leeway + main_frame_strut_thickness),
    diagonal_to (main_frame_top_y, wheel_housing_right_z - wheel_axle_leeway),
    vertical_to (0),
    horizontal_to (link_highest_y + wheel_loose_leeway),
    vertical_to (wheel_housing_right_z - wheel_axle_leeway),
    horizontal_to (slider_top_y + wheel_axle_leeway),
    vertical_to (wheel_housing_right_z - slider_width - wheel_loose_leeway),
    horizontal_to (slider_bottom_y - wheel_axle_leeway),
    vertical_to (wheel_housing_right_z - wheel_axle_leeway),
    horizontal_to (wheel_housing_bottom_y - wheel_loose_leeway),
    close(),
  ]).as_yz().to_wire()

  '''main_frame_inner_wire = FreeCAD_shape_builder (zigzag_length_limit = 5, zigzag_depth = - 1).build ([
    start_at (band_lever_bottom_y - wheel_axle_leeway - main_frame_strut_thickness, wheel_housing_right_z - wheel_axle_leeway - main_frame_strut_thickness),
    diagonal_to (outer_inner_corner_yz),
    diagonal_to (close_inner_corner_yz),
    close(),
  ]).as_yz().to_wire()'''

  main_frame_part = Part.Face([main_frame_outer_wire, 
    # Note: Saves material, but increases printing time because there's more outer surfaces
    #main_frame_inner_wire
  ]).fancy_extrude (vector (1, 0, 0), bounds (main_frame_front_x, main_frame_back_x))

  main_frame_missing_part = FreeCAD_shape_builder (zigzag_length_limit = main_frame_around_pivot_radius*2.2, zigzag_depth = 1).build ([
    start_at (band_lever_bottom_y - wheel_axle_leeway, 0),
    vertical_to (outer_corner_yz[1]),
    horizontal_to (band_lever_top_y + wheel_axle_leeway),
    
    vertical_to (0),
    
    close(),
  ]).as_yz().to_wire().to_face().fancy_extrude (vector (1, 0, 0), bounds (main_frame_front_x, main_frame_back_x))

  a,b = circle_circle_tangent_segment (
    (band_lever_pivot_xz, string_holder_edges_radius + 2),
    (band_lever_tip_circle_center_xz, band_lever_tip_circle_radius + 2),
  )
  main_frame_missing_part_missing_part = FreeCAD_shape_builder ().build ([
    start_at (b),
    #diagonal_to (
    diagonal_to (band_lever_tip_xz [0] + handle_motion_distance + 10, 0),
    horizontal_to (main_frame_back_x),
    vertical_to (a[1]),
    diagonal_to (a),
    close(),
  ]).as_xz().to_wire().to_face().fancy_extrude (vector (0, 1, 0), centered (500))

  main_frame_missing_part = main_frame_missing_part.cut (main_frame_missing_part_missing_part)

  main_frame_part = main_frame_part.cut (main_frame_missing_part)

  def main_frame_profile_filter(front):
   something_xz = band_lever_pivot_xz + main_frame_around_pivot_radius*vector (math.sin(math.tau / 8), - math.sin(math.tau / 8))
   
   if front:
     differing = [
       horizontal_to (band_lever_pivot_xz [0] - main_frame_around_pivot_radius),
       vertical_to (band_lever_pivot_xz [1]),
     ]
   else:
     differing = [
       horizontal_to (main_frame_front_x),
       vertical_to (-10),
       bezier([
         (main_frame_front_x, -30),
         band_lever_pivot_xz + vector(-main_frame_around_pivot_radius, 70),
         band_lever_pivot_xz + vector(-main_frame_around_pivot_radius, 0),
       ]),
     ]

   return FreeCAD_shape_builder ().build ([
    start_at (something_xz),
    diagonal_to (main_frame_back_x, something_xz [1] + (main_frame_back_x - something_xz [0])),
    vertical_to (0),
    ] + differing + [
    arc_radius_to (main_frame_around_pivot_radius, something_xz),
   ]).as_xz().to_wire().to_face().fancy_extrude (vector (0, 1, 0), bounds (band_center_y if front else -500, 500 if front else band_center_y))
   
  main_frame_part = main_frame_part.cut (main_frame_missing_part).common (main_frame_profile_filter (True).fuse (main_frame_profile_filter (False)))
  
  targeting_stick_hole = box (
    centered (500),
    bounds (band_lever_bottom_y - wheel_axle_leeway -2 - popsicle_stick_thickness,
            band_lever_bottom_y - wheel_axle_leeway -2),
    bounds (wheel_housing_right_z - wheel_axle_leeway - 2 - popsicle_stick_width,
            wheel_housing_right_z - wheel_axle_leeway - 2),
  ).makeOffsetShape (tight_leeway, 0.03, join=2)
  
  main_frame_part = main_frame_part.cut (targeting_stick_hole)

  catch_tip_stretched_xy = catch_tip_xy + vector (handle_motion_distance, 0)
  '''prong_tip_xy = vector (catch_tip_stretched_xy + vector (-(2+catch_tip_deflection_distance)/2, 2))

  prong_part = FreeCAD_shape_builder ().build ([
    start_at (prong_tip_xy),
    diagonal_to(catch_tip_stretched_xy + vector (0, - catch_tip_deflection_distance)),
    vertical_to (wheel_housing_bottom_y - main_frame_strut_thickness/2),
    horizontal_to (main_frame_back_x),
    vertical_to (prong_tip_xy [1]),
    close(),
  ]).to_wire().to_face().fancy_extrude (vector (0, 0, 1), centered (wheel_thickness))

  main_frame_part = main_frame_part.fuse (prong_part)'''

  prong_part = box (100, popsicle_stick_thickness+0.4, centered (popsicle_stick_width)).rotated (vector(), vector (0, 0, 1), math.atan2 (-2, 1)*360/math.tau).translated (catch_tip_stretched_xy + vector (0, - catch_tip_deflection_distance))

  prong_hole_part = prong_part.makeOffsetShape (tight_leeway, 0.03, join=2)

  for increment in range (5):
    main_frame_part = main_frame_part.cut (prong_hole_part.translated (vector (- increment*popsicle_stick_thickness*2, 0, 0)))


  band_lever_axle_part = FreeCAD_shape_builder().build ([
    start_at (vector (angle = math.tau*5/8, length = wheel_axle_radius)),
    arc_radius_to (-wheel_axle_radius,vector (angle = math.tau*3/8, length = wheel_axle_radius), -1),
    close(),
  ]).as_xz().to_wire().to_face().fancy_extrude (vector (0, 1, 0), bounds (band_lever_bottom_y - wheel_axle_leeway - main_frame_strut_thickness*1.5, band_lever_top_y + wheel_axle_leeway + main_frame_strut_thickness)).translated (vector (band_lever_pivot_xz [0], 0, band_lever_pivot_xz [1]))

  main_frame_part = main_frame_part.cut (band_lever_axle_part.makeOffsetShape (tight_leeway, 0.03))

  main_frame_part = main_frame_part.fuse (main_frame_part.mirror(vector(), vector(0,0,1)))
  
  
  frame_handle_peg = FreeCAD_shape_builder().build ([
    start_at (vector (angle = math.tau*5/8, length = wheel_axle_radius)),
    arc_radius_to (-wheel_axle_radius,vector (angle = math.tau*3/8, length = wheel_axle_radius), -1),
    close(),
  ]).as_yz().to_wire().to_face().fancy_extrude (vector (1, 0, 0), bounds (main_frame_back_x -10, main_frame_back_x + main_frame_strut_thickness + 2))
  frame_handle_peg_shadow = frame_handle_peg.makeOffsetShape (tight_leeway, 0.03)
  for flip in [-1, 1]:
    for y, z in [(main_frame_top_y -10, -30), (main_frame_bottom_y +20, -16)]:
      translation = vector (0, y, z*flip)
      shadow = frame_handle_peg_shadow.translated (translation)
      main_frame_part = main_frame_part.cut (shadow)
      handle_fixed_part = handle_fixed_part.cut (shadow)
      Part.show(frame_handle_peg.translated (translation), "FrameHandlePeg")
        

  '''stick_test = FreeCAD_shape_builder (zigzag_length_limit = 3, zigzag_depth = 1).build ([
    start_at(0,0),
    horizontal_to (100),
    vertical_to (10),
    horizontal_to (0),
    close(),
  ]).to_wire().to_face().fancy_extrude (vector (0, 0, 6))

  #Part.show (stick_test, "StickTest")'''

  


  Part.show (wheel, "Wheel")
  Part.show (wheel_housing_main, "WheelHousingMain")

  #wheel_housing_other.translate (vector (0, 0, 10))
  Part.show (wheel_housing_other, "WheelHousingOther")
  Part.show (axle_part, "Axle")

  #channel_holder_part.translate (vector (-50, 0, 0))
  #Part.show (channel_holder_part, "ChannelHolder")

  test_box = Part.makeBox (12, 12, 100)
  test_box.translate (vector (wheel_drag_bar_right -6, wheel_drag_bar_height -6, 0))
  Part.show (wheel_housing_other.common(test_box), "AxleHoleTest")

  Part.show (band_lever_part, "BandLever")
  Part.show (band_lever_part.rotated (band_lever_pivot_center, vector (0, 1, 0), -band_lever_rotation_angle*360/math.tau), "BandLeverStretched")
  Part.show (band_lever_peg_part, "BandLeverPeg")
  Part.show (band_lever_axle_part, "BandLeverAxle")
  Part.show (handle_pivot_axle_part, "HandlePivotAxle")
  Part.show (handle_link_axle_part, "HandleLinkAxle")

  Part.show (main_frame_part, "MainFrame")
  
  Part.show (link_part, "Link")
  Part.show (handle_lever_part, "HandleLever")
  Part.show (handle_lever_stretched_part, "HandleLeverStretched")
  Part.show (handle_fixed_part, "Handle")

  Part.show(prong_part, "ProngExample")

  Part.show (box (bounds (farthest_left - 10, farthest_left), centered (6, on = band_center_y), centered (300)), "PutativeTarget")

  #Part.show (main_frame_missing_part_filter, "Debug")
  #Part.show (band_lever_peg_part.cut(band_lever_peg_cut_part), "Debug2")

  test_box = FreeCAD_shape_builder (zigzag_length_limit = 5, zigzag_depth = 1).build ([
    start_at (-100, wheel_housing_right_z - wheel_axle_leeway - main_frame_strut_thickness - 8),
    horizontal_to (100),
    vertical_to(-(wheel_housing_right_z - wheel_axle_leeway - main_frame_strut_thickness - 8)),
    horizontal_to (-100),
    close(),
  ]).as_yz().to_wire().to_face().fancy_extrude (vector (1, 0, 0), centered (50, on=main_frame_back_x))
  Part.show (main_frame_part.common(test_box), "ChannelTest")

  test_box = box(centered (20), centered (90), centered (20)).translated (band_lever_pivot_center)
  Part.show (main_frame_part.common(test_box), "AxleHolesTest")



def make_manual_snapper():
  handle_thickness = 22
  handle_fixed_size_x = 15
  handle_side_thickness = 2
  
  handle_fixed_profile = FreeCAD_shape_builder().build ([
    start_at (- handle_fixed_size_x, - handle_thickness/2),
    bezier ([(0, - handle_thickness/2), (0, handle_thickness/2), (- handle_fixed_size_x, handle_thickness/2)]),
    horizontal_to (-20 + handle_side_thickness/2),
    bezier([
      (-20, handle_thickness/2),
      (-20, -handle_thickness/2),
      (-20 + handle_side_thickness/2, -handle_thickness/2),
      ]),
    close(),
  ]).as_xz().to_wire()
  handle_fixed_profile.translate (vector (- handle_fixed_profile.BoundBox.XMax, 0, 0))
  
  handle_fixed_web_radius = 15
  web_xy = vector(0, 0)
  foo_xy = web_xy + vector (handle_fixed_web_radius, 0) + vector (length = handle_fixed_web_radius, angle = math.tau*3/8)
  bar_xy = vector (foo_xy [0], web_xy[1]-(foo_xy [1]-web_xy[1]))
  handle_fixed_start_xy = vector (50, 100)
  handle_curve_end_xy = web_xy + vector (40, -80)
  handle_fixed_curve = FreeCAD_shape_builder().build ([
    start_at (handle_fixed_start_xy),
    bezier ([handle_fixed_start_xy + vector (0, -50), foo_xy + vector (25, 25), foo_xy]),
    arc_through_to (web_xy, bar_xy),
    bezier ([bar_xy + vector (25, -25), handle_curve_end_xy]),
  ]).to_wire()
  handle_curve_shadow = handle_fixed_curve.makeOffset2D(handle_fixed_size_x, openResult = True).fancy_extrude (vector (0, 0, 1), centered (500)).extrude(vector(500, 0, 0))
  handle_fixed_profile.translate (handle_fixed_start_xy)
  handle_fixed_part = handle_fixed_curve.makePipeShell ([handle_fixed_profile], True, False, 1)
  
  handle_front = FreeCAD_shape_builder().build ([
    start_at (handle_thickness/2, handle_thickness/2),
    arc_through_to ((0, 0), (handle_thickness/2, -handle_thickness/2)),
    horizontal_to (90),
    vertical_to (handle_thickness/2),
    close(),
  ]).as_xz().to_wire().to_face().extrude (vector (0, 500, 0)).rotated (vector (), vector (0, 0, 1), 25).translated (vector (handle_curve_end_xy [0] - 35, handle_curve_end_xy [1] - 10, 0))
  
  handle_fixed_part = handle_fixed_part.common(handle_front)
  handle_part = handle_fixed_part.fuse ([handle_front.cut (handle_curve_shadow)])
  handle_part.rotate(vector (), vector (0, 0, 1), -10)
  handle_part.translate(vector (7 + 30, -12, 0))
  handle_part_uncut = handle_part
  handle_part = handle_part.cut(box(centered(500), bounds(0, 500), centered(500)))
  
  finger_leeway = 25
  full_slack_length = 180
  cylinder_radius = 5
  slot_length = 5
  slot_width = 0.5
  slot_wall_min_thickness = 2
  strut_thickness = cylinder_radius *2 + slot_width + slot_wall_min_thickness #10
  shield_thickness = 1
  waste_length_each_end = cylinder_radius*math.tau/4 + slot_length
  usable_slack_length = full_slack_length - waste_length_each_end*2
  band_width = 6
  band_leeway = 1.5
  cylinder_height = band_width + band_leeway*2
  
  cylinder_base_center = vector (0, strut_thickness + finger_leeway, usable_slack_length/2)
  cylinder = Part.makeCylinder (cylinder_radius, cylinder_height, cylinder_base_center, vector(0, 1, 0))
  cylinder_and_slot = cylinder.fuse ([
    box (
      bounds (cylinder_base_center [0], cylinder_base_center [0] + slot_length),
      bounds (cylinder_base_center [1], cylinder_base_center [1] + cylinder_height),
      bounds (cylinder_base_center [2], cylinder_base_center [2] + cylinder_radius),
    ),
    box (
      bounds (cylinder_base_center [0], cylinder_base_center [0] + slot_length),
      bounds (cylinder_base_center [1], cylinder_base_center [1] + cylinder_height),
      bounds (cylinder_base_center [2] + cylinder_radius + slot_width, cylinder_base_center [2] + cylinder_radius + slot_width + slot_wall_min_thickness),
    ),
    box (
      bounds (cylinder_base_center [0], cylinder_base_center [0] + slot_length),
      bounds (cylinder_base_center [1], cylinder_base_center [1] + band_leeway),
      bounds (cylinder_base_center [2] + cylinder_radius, cylinder_base_center [2] + cylinder_radius + slot_width),
    ),
  ])
  
  foo= (
    cylinder_base_center [1] - strut_thickness*math.sin (math.tau/8),
    cylinder_base_center [2] - cylinder_radius + strut_thickness*math.sin (math.tau/8),
  )
  bar = (
    cylinder_base_center [1] + cylinder_height + strut_thickness*math.sin (math.tau/8),
    cylinder_base_center [2] - cylinder_radius + strut_thickness*math.sin (math.tau/8),
  )
  #TODO fix duplicate code id 98450njdfs
  strut_front_filter_shape = FreeCAD_shape_builder().build ([
    start_at (bar[1] + bar[0],0),
    diagonal_to (bar),
    arc_radius_to (strut_thickness, (cylinder_base_center [1] + cylinder_height, cylinder_base_center [2] - cylinder_radius + strut_thickness)),
    horizontal_to (cylinder_base_center [1]),
    arc_radius_to (strut_thickness, foo),
    diagonal_to (0, foo [1] - foo [0]),
    vertical_to (0),
  ])
  #TODO fix duplicate code id 98450njdfs
  strut_shape = FreeCAD_shape_builder().build ([
    start_at (strut_thickness, 0),
    vertical_to (20),
    bezier ([
      (strut_thickness, 20 + 20),
      (cylinder_base_center [1] - 20, cylinder_base_center [2] - cylinder_radius - 20), 
      (cylinder_base_center [1], cylinder_base_center [2] - cylinder_radius),
    ]),
    vertical_to (cylinder_base_center [2] - cylinder_radius + strut_thickness),
    arc_radius_to (strut_thickness, foo),
    diagonal_to (0, foo [1] - foo [0]),
    vertical_to (0),
  ])
  foo = strut_shape.mirror(vector(), vector(0,1))
  strut_wire = Part.Wire(strut_shape.Edges + list(reversed(foo.Edges))).as_yz()
  foo = strut_front_filter_shape.mirror(vector(), vector(0,1))
  strut_front_filter_wire = Part.Wire(strut_front_filter_shape.Edges + list(reversed(foo.Edges))).as_yz()

  #Part.show(strut_wire)
  
  strut_part = strut_wire.to_face().fancy_extrude (vector (1, 0, 0), centered (500))
  strut_front_filter_part = strut_front_filter_wire.to_face().fancy_extrude (vector (1, 0, 0), centered (500))
  
  oval_center =vector (cylinder_base_center [0], 0, 0)
  top_filter_oval = Part.Wire([Part.Ellipse (
    oval_center,
    cylinder_base_center [2] + strut_thickness,
    cylinder_radius + finger_leeway + shield_thickness,
  ).toShape()]).as_xz().rotated (oval_center, vector (0, 1, 0), 90)
  shield_inside_part = top_filter_oval.makeOffset2D (- shield_thickness).to_face().fancy_extrude (vector (0, 1, 0), centered (500))
  far = cylinder_base_center [0] - cylinder_radius - finger_leeway - shield_thickness
  side_filter_wire = FreeCAD_shape_builder().build ([
    start_at (500, 0),
    vertical_to (cylinder_base_center [1] + cylinder_height + finger_leeway),
    horizontal_to (far + finger_leeway/2),
    diagonal_to (far, cylinder_base_center [1] + cylinder_height + finger_leeway/2),
    vertical_to (cylinder_base_center [1] - finger_leeway/2),
    diagonal_to (far + (cylinder_base_center [1] - finger_leeway/2), 0),
    close(),
  ]).to_wire()
  shield_inside_part = shield_inside_part.common (side_filter_wire.makeOffset2D (- shield_thickness).to_face().fancy_extrude (vector (0, 0, 1), centered (500)))
  #Part.show(top_filter_oval)
  shield_part = shield_inside_part.makeOffsetShape(shield_thickness, 0.03).cut(shield_inside_part).common(box(
    bounds (-500, cylinder_base_center [0] - cylinder_radius*2),
    bounds (-500, cylinder_base_center [1] + cylinder_height + finger_leeway - 2.5),
    centered (500),
  )).common (strut_front_filter_part)
  strut_part = strut_part.common (top_filter_oval.to_face().fancy_extrude (vector (0, 1, 0), centered (500))).common(side_filter_wire.to_face().fancy_extrude (vector (0, 0, 1), centered (500)))
  #Part.show(strut_part)
  
  danger_slit = FreeCAD_shape_builder().build ([
    start_at (cylinder_base_center [0], cylinder_base_center [1]),
    vertical_to (cylinder_base_center [1] + cylinder_height),
    diagonal_to (cylinder_base_center [0] - 80, cylinder_base_center [1] + cylinder_height + 20),
    vertical_to (cylinder_base_center [1] - 20),
    close(),
  ]).to_wire().to_face().fancy_extrude (vector (0, 0, 1), centered (500)).common (
    FreeCAD_shape_builder().build ([
    start_at (cylinder_base_center [0], cylinder_base_center [2]),
    diagonal_to (-cylinder_base_center [2]*1.5, 0),
    diagonal_to (cylinder_base_center [0], -cylinder_base_center [2]),
    close(),
  ]).as_xz().to_wire().to_face().fancy_extrude (vector (0, 1, 0), centered (500))
  )
  
  #Part.show (danger_slit)
  
  shield_part = shield_part.cut (danger_slit)
  
  
  slider_profile =FreeCAD_shape_builder().build ([
    start_at (0, 4),
    vertical_to (-4),
    bezier ([
      (2, -2),
      (3, -3),
    ]),
    bezier ([
      (4, -4),
      (8, 0),
    ]),
    bezier ([
      (4, 4),
      (3, 3)
    ]),
    bezier ([
      (2, 2),
      (0, 4)
    ]),
    #close()
  ]).as_yz().to_wire().to_face()
  slider_channel_profile = slider_profile.makeOffset2D(0.3)
  slider = slider_profile.extrude (vector (35, 0, 0))
  slider_channel = slider_channel_profile.extrude (vector (35, 0, 0))
  handle_sliders = slider.translated (vector (0, 0, handle_thickness/2 - 4))
  slider_channels = slider_channel.translated (vector (0, 0, handle_thickness/2 - 4))
  handle_sliders = handle_sliders.fuse (handle_sliders.mirror (vector(), vector (0, 0, 1)))
  slider_channels = slider_channels.fuse (slider_channels.mirror (vector(), vector (0, 0, 1)))
  #Part.show (handle_sliders, "sliders")
  handle_part = handle_part.fuse (handle_sliders.common (handle_part_uncut ))
  #Part.show (slider_channels)
  
  # note: the way I cut the slider channel here doesn't leave leeway where the 2 flat surfaces meet, but since I did a test print with this mistake included, and the test print fit snugly, I'm leaving it.
  snapper = strut_part.fuse([cylinder_and_slot, cylinder_and_slot.mirror (vector(), vector (0, 0, 1)), shield_part]).cut (slider_channels)

  Part.show(snapper)
  Part.show (handle_part)
  
  Part.show (snapper.common (box (
    centered (15), bounds (-5, cylinder_height + 5), centered (20),
  ).translated (cylinder_base_center)))
  
  Part.show (snapper.common (box (
    bounds (-394, -10), bounds (-15, 25), bounds(-40, -10),
  ).translated (cylinder_base_center)))  
  
  
  slider_test_box = box (bounds (-5, 100), centered (30), centered (handle_thickness + 10)).rotated (vector (15, 0, 0), vector (0, 0, 1), 15)
  
  Part.show (snapper.common (slider_test_box))
  Part.show (handle_part.common (slider_test_box))
    
    
    
    
    

def make_clamp_enhancer ():
  inner_x = 0
  outer_x = 6.5
  tip_corner_x = outer_x - 2.5
  curve_middle_x = 1.5
  
  curve_middle_z = 0
  curve_edge_z = 4
  flat_edge_z = 11.5
  tip_z = 16
  plate_length = tip_z
  plate_width = plate_length
  grip_leeway = 0.5
  plate_min_thickness = 0.45
  plate_left_x = inner_x - grip_leeway - plate_min_thickness
  clip_right_x = outer_x + grip_leeway + plate_min_thickness
  
  thingy_width = 9.2
  clip_width = thingy_width + (grip_leeway + plate_min_thickness)*2 
  
  cone_radius_angle = math.tau/18
  spike_height = 3
  spike_radius = spike_height*math.tan(cone_radius_angle)
  print (spike_radius)
  
  clamp_ish = FreeCAD_shape_builder ().build ([
    start_at (curve_middle_x, curve_middle_z -10),
    vertical_to (curve_middle_z),
    diagonal_to (inner_x, curve_edge_z),
    vertical_to (flat_edge_z),
    diagonal_to (tip_corner_x, tip_z),
    horizontal_to (outer_x),
    vertical_to (curve_middle_z -10),
    close(),    
  ]).as_xz().to_wire().to_face().fancy_extrude (vector (0, 1, 0), centered (thingy_width))
  #Part.show (clamp_ish, "Clampish")
  
  plate = FreeCAD_shape_builder ().build ([
    start_at (curve_middle_x, curve_middle_z),
    vertical_to (tip_z),
    horizontal_to (plate_left_x),
    vertical_to (curve_middle_z),
    close(),    
  ]).as_xz().to_wire().to_face().fancy_extrude (vector (0, 1, 0), centered (plate_width))
  #Part.show (plate, "Plate")
  
  def spike(y, z):
    return Part.makeCone (spike_radius, 0, spike_height, vector(plate_left_x + plate_min_thickness/2, y, z), vector(math.cos(math.tau/2 + cone_radius_angle), 0, math.sin(math.tau/2 + cone_radius_angle)))

  spikes = [
  spike(((y-2)/4)*(plate_width-spike_radius*2), (z/4)*(plate_length-spike_radius*2) + spike_radius)
  for y in range(5) for z in range (5)]
  
  clips_box = box (
    bounds (plate_left_x, clip_right_x),
    centered (clip_width),
    bounds (curve_middle_z, tip_z),
  ).cut(
  box (
    bounds (outer_x, outer_x + 100),
    centered (thingy_width - 2),
    centered (500),))
  #Part.show (clips_box, "ClipsBox")
  
  result = plate.fuse (spikes).fuse (clips_box)
  #Part.show(clamp_ish.makeOffsetShape (grip_leeway, 0.03, join = 2))
  result = result.cut (clamp_ish.makeOffsetShape (grip_leeway, 0.03))
  result = result.makeChamfer(1, [edge for edge in result.Edges if
        edge.BoundBox.XMin == curve_middle_x
    and edge.BoundBox.XMax == curve_middle_x
    and abs(edge.BoundBox.YMax)*2 > plate_width*0.99
    and abs(edge.BoundBox.YMin)*2 > plate_width*0.99
    ])
  result = result.makeFillet(grip_leeway + plate_min_thickness, [edge for edge in result.Edges if
        edge.BoundBox.XMin == clip_right_x
    and edge.BoundBox.XMax == clip_right_x
    and abs(edge.BoundBox.YMax)*2 > clip_width*0.99
    and abs(edge.BoundBox.YMin)*2 > clip_width*0.99
    ])
  result = result.mirror(vector(), vector(0,0,1))
  
  
  Part.show (result, "Enhancer")

#make_snapper()
#make_clamp_enhancer()
make_manual_snapper()



'''
Desired features:

bounds() but specifying just one bound and a size
rotations specify either radians or degrees rather than "angle"
default to rotating in the xy plane
"horizontal_by" (no, actually a more sophisticated rewrite of shape builder)
.mirror_fuse() curse
fillet/chamfer curse that defaults to using all of the edges and may take a filter lambda

'''


document().recompute()
Gui.SendMsgToActiveView("ViewFit")
#Gui.activeDocument().setEdit("Sketch")
#Gui.activeDocument().activeView().viewIsometric()

