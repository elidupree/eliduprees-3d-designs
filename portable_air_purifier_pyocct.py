import sys

from pyocct_system import *
initialize_system (globals(), sys.argv[1])


wall_thickness = 0.8

# extra leeway in addition to the wall expansion, for rigid parts that need to fit into a slot, so that printing irregularities don't make them not fit
tight_leeway = 0.15

strong_filter_length = 151.9 + tight_leeway*2
strong_filter_width = 101 + tight_leeway*2
strong_filter_depth_without_seal = 14
strong_filter_seal_depth_expanded = 2
strong_filter_seal_squish_distance = 0.5
strong_filter_seal_depth_squished = strong_filter_seal_depth_expanded - strong_filter_seal_squish_distance
 
fan_thickness = 28 + tight_leeway*2
fan_width = 79.7 + tight_leeway*2
fan_length = 78.9 + tight_leeway*2
fan_exit_width = 26 + tight_leeway*2
fan_exit_length = 8
fan_intake_circle_measured_radius = 24.4
fan_intake_circle_center_from_front = tight_leeway + 40.3
fan_intake_circle_center_from_left = tight_leeway + 44
fan_intake_circle_center_to_back = fan_length - fan_intake_circle_center_from_front
fan_intake_circle_center_to_right = fan_width - fan_intake_circle_center_from_left

battery_thickness = 27.8 + tight_leeway*2
battery_width = 85.5 + tight_leeway*2
battery_length = 144.2 + tight_leeway*2
battery_cord_diameter = 3.5
battery_socket_diameter = 11.4
battery_socket_length = 38.2

fan_cord_socket_slit_width = 15
fan_cord_socket_slit_length = 40

strong_filter_rim_inset = 6
strong_filter_airspace_wall_inset = strong_filter_rim_inset
strong_filter_size = Vector (strong_filter_length, strong_filter_width, strong_filter_seal_depth_squished)
strong_filter_min = Point (0, 0, 0)
strong_filter_max = strong_filter_min + strong_filter_size
strong_filter_center = strong_filter_min + (strong_filter_size/2)

CPAP_outer_radius = (21.5/2)
CPAP_inner_radius = CPAP_outer_radius-wall_thickness


def loop_pairs(points):
  return [(a,b) for a,b in zip(points, points[1:] + points[:1])]
def all_equal(iterable):
  i = iter(iterable)
  try:
    first = next(i)
  except StopIteration:
    return True
  return all(v == first for v in i)
  
def range_thing(increments, start, end):
  dist = end - start
  factor = 1/(increments - 1)
  return (start + dist*i*factor for i in range(increments))

@cached
def strong_filter_output_solid():
  inset = vector(strong_filter_airspace_wall_inset, strong_filter_airspace_wall_inset, 0)
  rect_min = strong_filter_min + inset
  rect_max = strong_filter_max - inset
  corners = [
    Point (rect_min[0], rect_min[1], 0),
    Point (rect_min[0], rect_max[1], 0),
    Point (rect_max[0], rect_max[1], 0),
    Point (rect_max[0], rect_min[1], 0),
  ]
  pairs = loop_pairs(corners)
  CPAP_center = Point (strong_filter_center[0] - 30, strong_filter_center[1], 0)
  top_z = 30
  
  def face(pair):
    delta = pair[1] - pair[0]
    filter_poles = [[pos + vector(0,0,z) for pos in range_thing(10, *pair)] for z in range_thing(4, 0, 5)] 
    CPAP_poles = [[CPAP_center + vector(0,0,z) + (pos - CPAP_center).Normalized()*CPAP_inner_radius for pos in range_thing(10, *pair)] for z in range_thing(4, 15, top_z)]
    
    return Face(BSplineSurface(filter_poles + CPAP_poles))
  
  faces = [face(pair) for pair in pairs]
  bottom_face = Face (Wire ([Edge (*pair) for pair in pairs]))
  top_face = Face (Wire ([
    next(edge for edge in f.Edges() if all(
      v[2] == top_z for v in edge.Vertices()
    ))
    for f in faces
  ]))
  #return Compound(faces)
  #shell = Shell(faces)
  #solid = thicken_shell_or_face(shell, wall_thickness)
  
  solid = Solid(Shell(faces + [bottom_face, top_face]))
  thick = thicken_solid(solid, [f for f in solid.Faces() if all_equal(v[2] for v in f.Vertices())], wall_thickness)
  mirrored = solid @ Mirror(Axes(strong_filter_center, Direction(1,0,0)))
  solid = Union(solid, mirrored)
  return thicken_solid(solid, [f for f in solid.Faces() if all_equal(v[2] for v in f.Vertices())], wall_thickness)
  
  


final_shape = strong_filter_output_solid

print (final_shape)
view = False
view = True
if view:
  from OCCT.Visualization.QtViewer import ViewerQt
  v = ViewerQt(width=2000, height=1500)
  v.display_shape(unwrap(final_shape))
  v.start()