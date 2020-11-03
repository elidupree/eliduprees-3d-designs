import math

from pyocct_system import *
initialize_system (globals())

from air_adapters import elidupree_4in_threshold, elidupree_4in_leeway_one_sided, elidupree_4in_intake_inner_radius, elidupree_4in_output_outer_radius



object_height = 15
top_nose_width = 25
top_nose_length = 20
bottom_nose_width = 30
bottom_nose_length = 25
#cloth_leeway = 3
wing_length = 80

wall_thickness = 1.0


def control_points(fraction):
  corner_curvyness = 0.3
  nose_coordinates = [
    (-1 - corner_curvyness, 0),
    (-1, 0),
    (-1, corner_curvyness),
    (-0.6, 0.9),
    (-0.1, 1),
  ]
  x_scale = Between(bottom_nose_width, top_nose_width, fraction)/2.0
  y_scale = Between(bottom_nose_length, top_nose_length, fraction)
  z = Between(-1, object_height + 1, fraction)
  nose_points = [Point(x*x_scale, y*y_scale, z) for x,y in nose_coordinates]
  left_end_coordinates = [
    (0,0),
    (-2, 0),
    (-5, 8),
  ]
  nose_points = (
    [nose_points[0] + Left*wing_length + Vector(x, y, 0) for x,y in left_end_coordinates[::-1]]
    + nose_points
  )
  nose_points = nose_points + [p@Reflect(Right) for p in nose_points[::-1]]
  
  if fraction == 0.0 or fraction == 1.0:
    curve = BSplineCurve(nose_points)
    for i, point in enumerate(nose_points):
      normal = curve.derivatives(closest = point).tangent @ Rotate(Up, degrees=-90)
      if normal is not None:
        nose_points[i] = point - normal * (2.0 if point[1] > 1 else 1.0)
  return nose_points
    
  


@run_if_changed
def make():
  surface = BSplineSurface([
    control_points(fraction) for fraction in subdivisions(0.0, 1.0, amount=7)
  ])
  #preview(surface)
  
  solid = Offset(Face(surface), wall_thickness, fill=True)
  solid = Difference(solid, HalfSpace(Origin+Up*object_height, Up))
  solid = Difference(solid, HalfSpace(Origin, Down))
  
  hole = Difference(
    Box(
      Point(-500, 3.0, 2.0),
      Point(500, 6.0, object_height - 2.0),
    ),
    Box(
      Point(-bottom_nose_width, -500, -500),
      Point(bottom_nose_width, 500, 500),
    )
  )
  #solid = Difference(solid, hole)
  preview(solid)
  save ("cloth_mask_restrainer", solid)
  save_STL("cloth_mask_restrainer", solid)
  
  
    

preview(manual_rubber_band_snapper)
