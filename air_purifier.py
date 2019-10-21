import json
import numpy
import math
from utils import *

class Foo(object):
  pass
a = Foo()

a.fan_width = 120.5
a.fan_depth = 31.0
a.foam_thickness = 9
a.wall_thickness = 0.8
a.wall_radius = a.wall_thickness / 2
a.thin_wall_thickness = 0.4
a.min_air_passage_thickness = 19
a.acoustic_tile_thickness = 13
a.acoustic_tile_air_gap = 3
a.acoustic_tile_space = a.acoustic_tile_thickness + 2*a.acoustic_tile_air_gap

# 2d points
a.below_fan = 0
a.above_fan      =      a.below_fan + a.wall_thickness + a.foam_thickness + a.fan_depth + a.foam_thickness
a.above_intake   =      a.above_fan + a.wall_thickness + a.foam_thickness + a.min_air_passage_thickness
a.below_entrance =   a.above_intake + a.wall_thickness + a.acoustic_tile_space
a.above_entrance = a.below_entrance + a.wall_thickness + a.foam_thickness + a.min_air_passage_thickness

a.fan_right = 0
a.entrance_right =      a.fan_right - a.wall_thickness - a.foam_thickness - a.fan_width - a.acoustic_tile_air_gap
a.entrance_left  = a.entrance_right - a.wall_thickness - a.min_air_passage_thickness - a.foam_thickness
a.exit_right     =  a.entrance_left - a.wall_thickness - a.acoustic_tile_space
a.exit_left      =     a.exit_right - a.wall_thickness - a.min_air_passage_thickness - a.foam_thickness

a.circular_intake_diameter = 70
a.circular_intake_radius = a.circular_intake_diameter/2
a.circular_intake_left = 57
a.circular_intake_back = 69
a.left_of_circular_intake = a.fan_right - a.wall_radius - a.foam_thickness - a.circular_intake_left - a.circular_intake_radius
a.below_circular_intake = 0 + a.wall_radius + a.foam_thickness + a.fan_width - a.circular_intake_back

a.bump_spacing = 12
a.between_bumps = 20

a.total_depth = a.wall_thickness + a.foam_thickness + a.fan_width + a.foam_thickness

outer_wall = [
    [a.exit_left, a.above_entrance],
    [a.exit_left, a.below_fan],
    [a.fan_right, a.below_fan],
    [a.fan_right, a.above_intake],
    [a.entrance_right, a.above_intake],
    [a.entrance_right, a.below_entrance],
    [a.fan_right, a.below_entrance],
  ]
entrance_wall =[
    [a.entrance_left, a.above_fan],
    [a.entrance_left, a.above_entrance],
    [a.fan_right, a.above_entrance],
  ]
exit_wall_partial = [
    [a.exit_right, a.above_entrance],
    [a.exit_right, a.above_fan],
    
  ]
walls_source = [
  outer_wall,
  exit_wall_partial + [[a.left_of_circular_intake - a.wall_radius, a.above_fan]],
  entrance_wall,
]
a.floor_points = outer_wall + list (reversed (entrance_wall)) + list (reversed (exit_wall_partial))

a.walls = []
for strip in walls_source:
  for index in range (len (strip) - 1):
    a.walls.append (strip [index: index +2])

scad = scad_variables (vars(a)) +"""
module walls_flat()
  for (wall = walls) {
    hull() {
      translate (wall[0]) square (wall_thickness, center = true);
      translate (wall[1]) square (wall_thickness, center = true);
    }
  }

module floor_flat() offset (delta = wall_radius) polygon (points = floor_points);
module interior() linear_extrude (height = total_depth, convexity = 10) floor_flat();

module bumps() difference() {
  for (wall = walls) {
    delta = wall [1] - wall [0];
    length = norm (delta);
    tangent = delta/length;
    used_length = length - bump_spacing*2;
    used_depth = total_depth - bump_spacing*2;
    rows = round(used_depth/between_bumps);
    columns = round(used_length/between_bumps);
    echo (rows, columns);
    for (column = [0: max(0, columns -1)]) {
      horizontal_position = wall [0] + tangent*(columns < 1 ?
        (length / 2)
        : (bump_spacing + used_length*column/(columns -1)));
      for (row = [0: rows - 1]) {
        vertical_position = (bump_spacing + used_depth*row/(rows -1));
        position = concat(horizontal_position, [vertical_position]);
        translate (position) difference() {
          sphere (r= wall_radius + acoustic_tile_air_gap) ;
          sphere (r= wall_radius + acoustic_tile_air_gap - thin_wall_thickness) ;
        }
      }
    }
  }
  interior();
}

module fan_restricting_wall_flat() {
  translate ([left_of_circular_intake, 0]) square ([fan_right - left_of_circular_intake, below_circular_intake]);
  difference() {
    translate ([left_of_circular_intake, 0]) square ([circular_intake_radius, below_circular_intake + circular_intake_radius]);
    translate ([left_of_circular_intake + circular_intake_radius, below_circular_intake + circular_intake_radius])
      circle (r= circular_intake_radius); 
  }
}

module fan_restricting_wall()
  translate ([0, above_fan, 0])
  rotate ([90, 0, 0])
  linear_extrude (height = wall_thickness, center = true, convexity = 10)
  fan_restricting_wall_flat();

union() {

  linear_extrude (height = wall_thickness, center = true, convexity = 10) floor_flat();
  linear_extrude (height = total_depth, convexity = 10) walls_flat();
  //bumps();
  fan_restricting_wall();
}

//translate ([-165, 150, 120 -259/2]) cube ([165, 40.64, 259]);
//color ("blue") translate ([-215, -5]) square (220);
//color ("blue") translate ([40, -5]) square (220);

"""

print (a.exit_left, a.above_entrance)

with open ("./target/generated.scad", "w") as file:
  file.write (scad);

print("done building air purifier stuff")

#junk junk junk
#(Dragon sometimes freezes up, and I think it happens more when it's near the end of the file, so…)
