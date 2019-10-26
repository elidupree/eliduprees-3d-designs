import json
import numpy
import math
from utils import *

class Foo(object):
  pass
a = Foo()


class Circle:
  def __init__(self, inner_radius = None, outer_radius = None):
    assert ((inner_radius is None) != (outer_radius is None))
    self.inner_radius_source = inner_radius
    self.outer_radius_source = outer_radius
  
  def inner_radius(self, thickness):
    if self.inner_radius_source is None:
      return self.outer_radius_source - thickness
    return self.inner_radius_source
  
  def outer_radius(self, thickness):
    if self.outer_radius_source is None:
      return self.inner_radius_source + thickness
    return self.outer_radius_source
    
  def critical_angles (self, thickness):
    return []
    
  def outer_distance(self, angle, thickness):
    return self.outer_radius(thickness)
  
  def inner_distance(self, angle, thickness):
    return self.inner_radius(thickness)

class Rectangle:
  def __init__(self, inner_size = None, outer_size = None):
    assert ((inner_size is None) != (outer_size is None))
    self.inner_size_source = inner_size
    self.outer_size_source = outer_size
  
  def inner_size(self, thickness):
    if self.inner_size_source is None:
      return (
        self.inner_size_source[0] - thickness,
        self.inner_size_source[1] - thickness,
      )
    return self.inner_size_source
  
  def outer_size(self, thickness):
    if self.outer_size_source is None:
      return (
        self.inner_size_source[0] + thickness,
        self.inner_size_source[1] + thickness,
      )
    return self.outer_size_source
    
  def critical_angles (self, thickness):
    results = []
    for angle in (
      math.atan2(size [1]*y_factor, size[0]*x_factor)
      for size in [self.inner_size(thickness), self.outer_size(thickness)]
        for x_factor in [-1, 1]
          for y_factor in [-1, 1]
    ):
      if not any(abs (angle - preexisting_angle) < math.tau/100000 for preexisting_angle in results):
        results.append (angle)
    return results
    
  def distance (self, size, angle):
    if size[0]*abs(math.sin(angle)) > size[1]*abs(math.cos(angle)):
      return (size[1]/2)/abs(math.sin(angle))
    else:
      return (size[0]/2)/abs(math.cos(angle))
  
  def outer_distance(self, angle, thickness):
    return self.distance (self.outer_size(thickness), angle) 
  
  def inner_distance(self, angle, thickness):
    return self.distance (self.inner_size(thickness), angle)

def adapt_anything(first, second, thickness, num_angles, num_slices, step_function, shallowest_angle_allowed):
 assert (num_slices % 2 == 1)
 a.adapter_outer_points = []
 a.adapter_inner_points = []
 a.adapter_faces = []
 a.num_slices = 100
 a.num_sides = 32
 
 critical_angles = first.critical_angles(thickness) + second.critical_angles(thickness)
 periodic_angles = ((float (index)/num_angles - 0.5)*math.tau for index in range (num_angles))
 angles = critical_angles + [angle for angle in periodic_angles if not any(abs (angle - critical_angle) < math.tau/10000 for critical_angle in critical_angles)]
 angles.sort()
 print(angles)
 
 for slice_index in range (num_slices):
  slice_fraction = float (slice_index)/float (num_slices -1)
  first_proportion = step_function (0, 1, slice_fraction)
  second_proportion = 1 - first_proportion
  first_side_index = len (a.adapter_outer_points)
  
  if slice_index == 0:
    a.adapter_faces.append (list (range (len (angles))))
  
  vertical_position = numpy.array ([0, 0, slice_fraction])

  
  for side_index in range (len (angles)):
    side_index_1 = (side_index + num_slices - (slice_index)//2) % len(angles)
    side_index_2 = (side_index + num_slices - (slice_index + 1)//2) % len(angles)
    angle = (
      angles [side_index_1]
      + (((angles [side_index_2] - angles[side_index_1] + math.tau*2.5) % math.tau) - math.tau*0.5) / 2
    )
    angle_vector = numpy.array ([
      math.cos (angle),
      math.sin (angle),
      0
    ])
    
    if slice_index >0:
      a.adapter_faces.append ([
        first_side_index + side_index,
        first_side_index + (side_index + 1) % len (angles),
        previous_first_side_index + side_index,
      ])
      a.adapter_faces.append ([
        first_side_index + side_index,
        previous_first_side_index + side_index,
        previous_first_side_index + (side_index + len (angles) - 1) % len (angles),
      ])
    
    if abs(first.outer_distance (angle, thickness)) > 300 or  abs(second.outer_distance (angle, thickness)) > 300:
      print(angle, thickness, first.outer_distance (angle, thickness), second.outer_distance (angle, thickness))
    
    a.adapter_outer_points.append (
      vertical_position
      + angle_vector*first_proportion*first.outer_distance (angle, thickness)
      + angle_vector*second_proportion*second.outer_distance (angle, thickness)
    )
    a.adapter_inner_points.append (
      vertical_position
      + angle_vector*first_proportion*first.inner_distance (angle, thickness)
      + angle_vector*second_proportion*second.inner_distance (angle, thickness)
    )
  
  if slice_index == num_slices - 1:
    a.adapter_faces.append (list (reversed (range (first_side_index, first_side_index+ len (angles)))))
  previous_first_side_index = first_side_index
  
 
 shallowest_normal_sin = max(
   abs(normalize(numpy.cross(points[face[1]] - points[face[0]], points[face[2]] - points[face[0]]))[2])
   for face in a.adapter_faces[1:-1]
     for points in [a.adapter_inner_points, a.adapter_outer_points]
 )
 shallowest_sin = math.sqrt(1 - shallowest_normal_sin**2)
 print(shallowest_sin , math.sin(shallowest_angle_allowed))
 if shallowest_sin < math.sin(shallowest_angle_allowed):
   shallowest_slope = shallowest_sin / math.sqrt(1 - shallowest_sin**2)
   allowed_slope = math.tan(shallowest_angle_allowed)
   factor = allowed_slope / shallowest_slope
   print(shallowest_slope, allowed_slope )
   for points in [a.adapter_inner_points, a.adapter_outer_points]:
     for point in points:
       point[2] *= factor
 
 return scad_variables (vars(a)) +"""
 difference() {
   polyhedron (points = adapter_outer_points, faces = adapter_faces, convexity = 10);
   polyhedron (points = adapter_inner_points, faces = adapter_faces, convexity = 10);
 }
 """


elidupree_4in_threshold = 51.416
elidupree_4in_leeway_one_sided = 0.2
def elidupree_4in_intake():
  return Circle(inner_radius = elidupree_4in_threshold + elidupree_4in_leeway_one_sided)
def elidupree_4in_output():
  return Circle(outer_radius = elidupree_4in_threshold - elidupree_4in_leeway_one_sided)
def hepa_filter():
  return Rectangle(inner_size=[165, 259])

with open ("./target/generated.scad", "w") as file:
  file.write (adapt_anything(
    hepa_filter(),
    elidupree_4in_output(),
    0.8,
    65,
    65,
    smootherstep,
    math.tau/8,
    ));

print("done building air purifier stuff")

#junk junk junk
#(Dragon sometimes freezes up, and I think it happens more when it's near the end of the file, so…)
