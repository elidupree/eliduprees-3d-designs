import math

from pyocct_system import *
initialize_system (globals())

from air_adapters import elidupree_4in_threshold, elidupree_4in_leeway_one_sided, elidupree_4in_intake_inner_radius, elidupree_4in_output_outer_radius



object_height = 8
top_nose_width = 25
top_nose_length = 26
bottom_nose_width = 29
bottom_nose_length = 28
#cloth_leeway = 3
wing_length = 80
wing_dir_1 = Left @ Rotate(Up, degrees = 15)
wing_degrees_2 = 65
wing_dir_2 = Left @ Rotate(Up, degrees = wing_degrees_2)
wing_corner_frac = 0.6
wing_base = Point(-bottom_nose_width/2, 0, 0)
wing_offset_1 = wing_dir_1 * (wing_length*wing_corner_frac)
wing_offset_2 = wing_dir_2 * (wing_length*(1-wing_corner_frac))

class Ender3: pass
class Shapeways: pass
target_printing_system = Ender3
target_printing_system = Shapeways


def control_points(height_fraction):
  corner_curvyness = 0.5
  nose_coordinates = [
    #(-1 - corner_curvyness, 0),
    (-1- corner_curvyness/5, corner_curvyness/5),
    (-1, corner_curvyness),
    (-0.5, 0.95),
    (-0.2, 1),
  ]
  x_scale = Between(bottom_nose_width, top_nose_width, height_fraction)/2.0
  y_scale = Between(bottom_nose_length, top_nose_length, height_fraction)
  z = Between(-1, object_height + 1, height_fraction)
  nose_points = [Point(x*x_scale, y*y_scale, z) for x,y in nose_coordinates]
  nose_points = [nose_points[0] + wing_dir_1*x_scale*corner_curvyness] + nose_points
  nose_points = [wing_base + vector(0,0,z) + wing_offset_1] + nose_points
  nose_points = [nose_points[0] + wing_offset_2] + nose_points
  on_edge = height_fraction == 0.0 or height_fraction == 1.0
  left_end_coordinates = [
    vector(0,0,0),
    vector(-5, 0, 0),
    vector(-5, 0, 0) + vector(-3, 8, 0)*(0.6 if on_edge else 1.0),
  ]
  nose_points = (
    [nose_points[0] + v @ Rotate(Up, degrees = wing_degrees_2) for v in left_end_coordinates[::-1]]
    + nose_points
  )
  nose_points = nose_points + [p@Reflect(Right) for p in nose_points[::-1]]
  
  curve = BSplineCurve(nose_points)
  resampled = [curve.value(distance = d) for d in subdivisions(0, curve.length(), amount = 120)]
  result = []
  
  loop_corner_base = wing_base + wing_offset_1 + wing_offset_2
  
  for i, point in enumerate(resampled):
    normal = curve.derivatives(closest = point).tangent @ Rotate(Up, degrees=90)
    if normal is not None:
      cheekness = min(1, max(0, abs(point[0]) - bottom_nose_width/2 - 4) / (15))
      tipness = min(1, max(0, (point[1] - top_nose_length/2) / (top_nose_length/3)))
      loopness = -(point - loop_corner_base)[1]
      loopness = min(1, max(0, (loopness + 10) / 10))
      thick = 1.2
      tip = 1.0
      thin = 0.61 if target_printing_system is Ender3 else 0.8
      here_thickness = (thin
        + loopness * (thick - thin)
        + (1-cheekness) * (thick - thin)
        + tipness * (tip - thick)
      )

      if on_edge:
        point = point + normal * (-2 + cheekness*3 + loopness*1)
      result.append((point, normal, here_thickness))

  return result
    
  


@run_if_changed
def make_solid():
  points = [
    control_points(fraction) for fraction in subdivisions(0.0, 1.0, amount=5)
  ]

  points_0 = [[a for a,b,c in row] for row in points]
  surface_0 = BSplineSurface(points_0)
  if target_printing_system is Ender3:
    points_1 = [[a + b*c for a,b,c in row] for row in points]
  if target_printing_system is Shapeways:
    def q(a,b,c):
      normal = surface_0.normal(surface_0.parameter(a))
      assert normal.dot(b) > 0
      return a + surface_0.normal(surface_0.parameter(a))*c
    points_1 = [[q(a,b,c) for a,b,c in row] for row in points]
  faces = [
    Face(surface_0),
    Face(BSplineSurface(points_1)),
  ]
  
  #preview(surface)
  #preview(Compound(faces[0], faces[1], Loft(faces[0].outer_wire(), faces[1].outer_wire(), ruled=True).faces()))
  
  shell = Shell(faces[0].complemented(), faces[1], Loft(faces[0].outer_wire(), faces[1].outer_wire(), ruled=True).faces())
  
  solid = Solid(shell)
  solid = Difference(solid, HalfSpace(Origin+Up*object_height, Up))
  solid = Difference(solid, HalfSpace(Origin, Down))
  save ("solid", solid)

@run_if_changed
def make_final():
  
  hole_border_thickness = 2.2
  hole = (
    Vertex(wing_base + wing_offset_1 + wing_offset_2 + vector(0,0,hole_border_thickness))
      .extrude(Up*(object_height-hole_border_thickness*2))
      .extrude((Left*50) @ Rotate(Up, degrees = wing_degrees_2))
      .extrude((Back*3) @ Rotate(Up, degrees = wing_degrees_2))
      @ Translate((Back*3) @ Rotate(Up, degrees = wing_degrees_2))
    )
  hole = Fillet(hole, [(edge, 1.3) for edge in hole.edges()])
  hole = Union(hole, hole @ Reflect(Right))
  final = Difference(solid, hole)

  save ("cloth_mask_restrainer", final)
  save_STL("cloth_mask_restrainer", final, linear_deflection = 0.02, angular_deflection = 0.2)
  
preview(cloth_mask_restrainer)
  
    

