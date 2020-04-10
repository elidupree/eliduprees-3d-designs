import json
import numpy
import math
from utils import *

class Foo(object):
  pass
a = Foo()


print("adapt_anything.py is deprecated; use the FreeCAD versions in air_adpaters.py")


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
        self.outer_size_source[0] - thickness,
        self.outer_size_source[1] - thickness,
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

def adapt_anything(first, second, thickness, num_angles, num_slices, step_function, min_height = 1, shallowest_angle_allowed = math.tau / 32):
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
  
  vertical_position = numpy.array ([0, 0, slice_fraction*min_height])

  
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


elidupree_4in_threshold = 51.616
elidupree_4in_leeway_one_sided = 0.12
hepa_filter_width = 165
hepa_filter_length = 259
dryer_hose_insert_radius = 50
def elidupree_4in_intake():
  return Circle(inner_radius = elidupree_4in_threshold + elidupree_4in_leeway_one_sided)
def elidupree_4in_output():
  return Circle(outer_radius = elidupree_4in_threshold - elidupree_4in_leeway_one_sided)
def cpap_connector():
  return Circle(outer_radius = 21.5/2)
def hepa_filter():
  return Rectangle(inner_size=[hepa_filter_width, hepa_filter_length])
def dryer_hose_insert():
  return Circle(outer_radius = dryer_hose_insert_radius)

dryer_hose_intake_insert = adapt_anything(
    elidupree_4in_intake(),
    dryer_hose_insert(),
    0.8,
    256,
    65,
    lambda a,b,c: smootherstep(1/3, 2/3, c),
    min_height = 75,
    )
    
dryer_hose_output_insert = adapt_anything(
    elidupree_4in_output(),
    dryer_hose_insert(),
    0.8,
    256,
    65,
    lambda a,b,c: smootherstep(1/3, 2/3, c),
    min_height = 75,
    )
    
HEPA_4in_too_big = adapt_anything(
    hepa_filter(),
    elidupree_4in_output(),
    0.8,
    65,
    65,
    smootherstep,
    shallowest_angle_allowed = math.tau / 8
    )
HEPA_4in_component_adapt = adapt_anything(
    elidupree_4in_output(),
    Rectangle(outer_size=[140, 165]),
    
    0.8,
    64,
    33,
    lambda a,b,c: smootherstep(0, 0.8, c),
    min_height = 75,
    )
HEPA_4in_component = (
 """
elidupree_4in_threshold = """+str(elidupree_4in_threshold)+""";
filter_width = """+str(hepa_filter_width)+""";
elidupree_4in_leeway_one_sided = 0.2;
wall_thickness = 0.8;
module outer_cylinder() cylinder (r = elidupree_4in_threshold - elidupree_4in_leeway_one_sided, h = 25);
module inner_cylinder() cylinder (r = elidupree_4in_threshold - elidupree_4in_leeway_one_sided - wall_thickness, h = 25);

diagonals_offset = 15;
bah = 140;

positions = [
  [ bah/2-wall_thickness/2 + diagonals_offset, -diagonals_offset],
  [ bah/2-wall_thickness/2, 0],
  [- bah/2+wall_thickness/2, 0],
  [- bah/2+wall_thickness/2 - diagonals_offset, - diagonals_offset],
];

module wall_circle (point) translate (point
 //+ [0, -wall_thickness]
) circle ( r= wall_thickness/2);
module wall_segment (first, second) hull() { wall_circle (first); wall_circle (second);}

module wall() {
  wall_segment (positions [0], positions [1]);
  //wall_segment (positions [1], positions [2]);
  wall_segment (positions [2], positions [3]);
}
foo = 2.2;
module wall_plus() {
  wall();
  //
  //wall_segment (positions [1], positions [1] + [ foo, 0]);
  //wall_segment (positions [2], positions [2] - [ foo, 0]);
}
module side_wall() {
  rotate ([90, 0, 0]) linear_extrude (height = wall_thickness, convexity = 10, center = true) hull() wall();
}

baz = bah + (foo)*2;
intersection() {
difference() {
  union() {
    """+HEPA_4in_component_adapt+"""
    //outer_cylinder();
    rotate([90,0,0]) linear_extrude (height = filter_width, convexity = 10, center = true) wall_plus();
    //translate([0, 0, -wall_thickness/2]) cube([bah+foo * 2, filter_width + foo*2, wall_thickness], center = true);
    translate([0, 0, -foo])linear_extrude(height = foo, convexity = 10, scale = [(baz+foo * 2)/baz, (filter_width + foo*2)/filter_width]) square([baz, filter_width], center = true);
    translate([0, -(filter_width - wall_thickness)/2,0]) side_wall();
    translate([0, (filter_width - wall_thickness)/2,0]) side_wall();
    //translate (-[filter_width, filter_width, 0]/2) cube ([filter_width, filter_width, wall_thickness]);
  }
  //inner_cylinder();
  //translate([0, 0, -50]) cube([bah-wall_thickness*2, filter_width-wall_thickness*2, 100], center=true);
  rotate ([90, 0, 0]) linear_extrude (height = filter_width-wall_thickness*2, convexity = 10, center = true)difference() {
    polygon(points = positions);
    wall();
  }
}
//translate([0,0,165])cube([200, 200, 200], center = true);
}

""")

with open ("./target/generated.scad", "w") as file:
  file.write (dryer_hose_output_insert);

print("done building air purifier stuff")

#junk junk junk
#(Dragon sometimes freezes up, and I think it happens more when it's near the end of the file, so…)
