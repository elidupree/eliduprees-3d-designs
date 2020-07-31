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
strong_filter_size = Vector (strong_filter_length, strong_filter_width, strong_filter_seal_depth_squished)
strong_filter_min = Point (0, 0, 0)
strong_filter_max = strong_filter_min + strong_filter_size


@cached






view = False
#view = True
if view:
  from OCCT.Visualization.QtViewer import ViewerQt
  v = ViewerQt(width=2000, height=1500)
  v.display_shape(unwrap(final_shape))
  v.start()