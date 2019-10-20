import json
import numpy
import math
from utils import *

def tongue_and_groove():
  return '''
module shape() union () {
  square ([10, 3]);
  square ([3, 8]);
  translate([7, 0]) square ([3, 8]);
  }
  
module shape_extended() union () {
  square ([10, 3]);
  square ([3, 9]);
  translate([7, 0]) square ([3, 9]);
  }

  
//module solid() linear_extrude(height=3) shape();
module inset() offset(r = -1, $fn = 16) shape_extended();

module plug() union(){
  linear_extrude(height=3, convexity = 10) shape();
  linear_extrude(height=5, convexity = 10) inset();
}
module socket() difference(){
  linear_extrude(height=5, convexity = 10) shape();
  translate([0, 0, 3]) linear_extrude(height=5, convexity = 10) inset();
}
plug();

translate([0, 20, 0]) socket();
  '''

def wall_normal(v):
  return normalize (numpy.array ([-v[1], v[0]]))

def wall_sides (vertices, radius):
  sides = [[],[]]
  perpendicular = wall_normal(vertices [1] - vertices [0])
  sides[0].append(vertices [0] - perpendicular*radius)
  sides[1].append(vertices [0] + perpendicular*radius)
  
  for index in range(len(vertices)-2):
    [previous, current, next] = vertices [index: index + 3]
    perpendicular_1 =wall_normal(current - previous)
    perpendicular_2 =wall_normal(next - current)
    # hack - assume only 90degree corners
    sides[0].append(current - (perpendicular_1+perpendicular_2)*radius)
    sides[1].append(current + (perpendicular_1+perpendicular_2)*radius)
    
  perpendicular = wall_normal(vertices [-1] - vertices [-2])
  sides[0].append(vertices [-1] - perpendicular*radius)
  sides[1].append(vertices [-1] + perpendicular*radius)
  return sides
  
def wall_wedge(vertices, radius, length):
  sides = wall_sides (vertices, radius)
  points = [[v[0],v[1],length] for v in vertices] + sides[0] + sides[1]
  number = len (vertices)
  faces = [
    [0, number, 2*number],
    [number -1, 3*number -1, 2*number -1],
  ]
  
  for index in range(len(vertices)-1):
    faces.extend ([
      [index, index +1, index + number +1, index + number],
      [index +1, index, index + 2*number, index + 2*number +1],
      [index + number, index + number +1, index + 2*number +1, index + 2*number],
    ])
  return (points, faces)
  
def pointy_plug_walls():
  wall_vertices = [numpy.array (k, dtype=numpy.double) for k in [
    [0, 13],
    [0, 0],
    [25, 0],
    [25, 13],
  ]]
  
  wedge_points, wedge_faces = wall_wedge (wall_vertices, 1.5, 3)
  sides = wall_sides (wall_vertices, 1.5)
  
  return scad_variables({
    "wedge_points": wedge_points, "wedge_faces": wedge_faces,
    "wall_polygon_points": sides[0] + list(reversed(sides[1])),
  })+'''
module wall_polygon() polygon(points=wall_polygon_points, convexity=10);
module wall_wedge() polyhedron(points=wedge_points, faces=wedge_faces, convexity=10);

module plug() union(){
  linear_extrude(height=4, convexity = 10) wall_polygon();
  translate([0, 0, 4]) wall_wedge();
}
module socket() difference(){
  linear_extrude(height=7, convexity = 10) wall_polygon();
  translate([0, 0, 7]) mirror([0, 0, 1]) wall_wedge();
}
plug();

translate([0, 20, 0]) socket();
  '''

def tube_thing():
  return '''

$fn = 64;
thickness = 1;
r1 = 50;
r2 = 45;
difference() {
union() {
cylinder(r = r1, h = 25);
translate([0, 0, 35]) cylinder(r = r2 , h = 25);
translate([0, 0, 25]) linear_extrude(height = 10, scale = r2 /r1) circle(r=r1);
}
union() {
cylinder(r = r1-thickness, h = 25);
translate([0, 0, 35]) cylinder(r = r2 -thickness, h = 25);
translate([0, 0, 25]) linear_extrude(height = 10, scale = (r2 -thickness)/(r1-thickness)) circle(r=r1-thickness);
}
}
'''


def wall_and_groove_calibrator():
  return '''

wall_width = 0.8;
cube([wall_width, 25, 25]);

translate([5,0,0]) difference() {
  cube([16, 25, 3]);
  for (index = [0:5]) {
    translate([1 + index*2.5, 0, 1]) cube ([wall_width + index*0.1, 25, 2]);
  }
}
    
  '''

  


with open ("./target/generated.scad", "w") as file:
  file.write (wall_and_groove_calibrator());

print("done building experiment(s)")

#junk junk junk
#(Dragon sometimes freezes up, and I think it happens more when it's near the end of the file, so…)
