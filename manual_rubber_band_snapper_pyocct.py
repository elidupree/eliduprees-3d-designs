import math

from pyocct_system import *
initialize_system (globals())

from air_adapters import elidupree_4in_threshold, elidupree_4in_leeway_one_sided, elidupree_4in_intake_inner_radius, elidupree_4in_output_outer_radius



band_width = 6
band_thickness = 1
band_leeway = 1.5

device_width = 90
strut_thickness = 7
finger_leeway = band_width
miss_leeway_slope = 0.2
miss_leeway = band_leeway + miss_leeway_slope * (strut_thickness + finger_leeway)
strut_rounding = 1

grip_slot_width = 0.5
grip_slot_wall_min_thickness = 2

band_space_height = band_width + band_leeway*2
band_space_width = band_thickness + band_leeway*2
cylinder_radius = 5

handle_radius = 6
handle_length = 90



@run_if_changed
def make():
  target_space_height = miss_leeway*2 + band_width
  side_struts_height = strut_thickness*2 + target_space_height
  side_struts_outer_wire = Wire(
      Point(-side_struts_height/2, -device_width/2, 0),
      Point(side_struts_height/2, -device_width/2, 0),
      Point(side_struts_height/2, device_width/2, 0),
      Point(-side_struts_height/2, device_width/2, 0),
      loop = True
    )
  side_struts_face = Face(
    side_struts_outer_wire,
    holes = side_struts_outer_wire.offset2D(-strut_thickness).complemented()
  )
  side_struts = side_struts_face.extrude(Up*strut_thickness)
  side_struts = Chamfer(side_struts, [
    (e, strut_rounding if any(abs(v[0]) != side_struts_height/2 or abs(v[1]) != device_width/2 for v in e.vertices()) or not all_equal((v[0], v[1]) for v in e.vertices()) else strut_thickness*0.7)
    for e in side_struts.edges()
    if not all(v[2] == strut_thickness for v in e.vertices())
  ])
  
  cylinder_outer_point = Point(
      0,
      -device_width/2 + grip_slot_wall_min_thickness + grip_slot_width,
      strut_thickness + finger_leeway + cylinder_radius
    )
  
  cylinder = Face(Wire(Edge(Circle(Axes (
    cylinder_outer_point + Back*cylinder_radius, Left
  ), cylinder_radius)))).extrude(Right*(band_space_height + grip_slot_wall_min_thickness*2), centered=True)
  
  cylinder_block = Vertex(cylinder_outer_point).extrude(Right*(band_space_height + grip_slot_wall_min_thickness*2), centered=True).extrude(Up*cylinder_radius).extrude(Back*cylinder_radius)
  side_wall_base = cylinder_outer_point + Front*grip_slot_width
  side_wall = Face(Wire(
    side_wall_base + Left*band_space_height/2 + Up*cylinder_radius,
    side_wall_base + Left*band_space_height/2,
    Point(
      band_space_height/2,
      side_wall_base[1],
      strut_thickness
    ),
    Point(
      target_space_height/2 + grip_slot_wall_min_thickness,
      side_wall_base[1],
      strut_thickness,
    ),
    side_wall_base + Right*(band_space_height/2 + grip_slot_wall_min_thickness),
    side_wall_base + Up*cylinder_radius + Right*(band_space_height/2 + grip_slot_wall_min_thickness),
    loop = True,
    )).extrude(Front*grip_slot_wall_min_thickness)
  
  bottom_wall_base = cylinder_outer_point + Front*(grip_slot_width + grip_slot_wall_min_thickness)
  bottom_wall = Face(Wire(
    bottom_wall_base + Right*band_space_height/2,
    bottom_wall_base + Down*cylinder_radius + Right*band_space_height/2,
    Point(
      target_space_height/2,
      bottom_wall_base[1],
      strut_thickness
    ),
    Point(
      target_space_height/2 + grip_slot_wall_min_thickness,
      bottom_wall_base[1],
      strut_thickness,
    ),
    bottom_wall_base + Right*(band_space_height/2 + grip_slot_wall_min_thickness),
    loop = True,
    )).extrude(Back*(grip_slot_wall_min_thickness + grip_slot_width + cylinder_radius*2))

  top_wall = (bottom_wall @ Reflect(Left)).intersection(HalfSpace(cylinder_outer_point, Back))
  
  bottom_filler = Face(Wire(
    bottom_wall_base + Up*cylinder_radius + Right*band_space_height/2,
    bottom_wall_base + Right*band_space_height/2,
    bottom_wall_base + Right*(band_space_height/2 + grip_slot_wall_min_thickness),
    bottom_wall_base + Up*cylinder_radius + Right*(band_space_height/2 + grip_slot_wall_min_thickness),
    loop = True,
    )).extrude(Back*(grip_slot_wall_min_thickness + grip_slot_width + 1))

  
  cylinder_etc = Compound(cylinder, cylinder_block, side_wall, bottom_wall, top_wall, bottom_filler)
  
  
  handle_direction = Direction(1, 0, 1)
  handle_perpendicular = Direction(-1, 0, 1)
  handle_base_point = Point(
      target_space_height/2 + strut_thickness/3,
      0,
      strut_thickness/3
    )
  handle = Face(Wire(Edge(Circle(Axes (
    handle_base_point, handle_direction
  ), handle_radius)))).extrude(handle_direction*handle_length)
  handle = Fillet(handle, [(e, handle_radius * 0.99) for e in handle.edges() if e.bounds().min()[2] > handle_length/3])
  handle = handle.intersection(HalfSpace(Origin, Up)).intersection(HalfSpace(Origin+(Right*target_space_height/2), Right))
  
    
  solid = Compound(side_struts, cylinder_etc, cylinder_etc @ Reflect(Front), handle)

  save ("manual_rubber_band_snapper", solid)
  save_STL("manual_rubber_band_snapper", solid)
  
  
    

preview(manual_rubber_band_snapper)
