import json
import numpy
import math
from utils import *



fan_width = 120.5
fan_depth = 31.0
foam_thickness = 9
wall_thickness = 3.0
wall_radius = wall_thickness / 2
min_air_passage_thickness = 19
acoustic_tile_thickness = 13
acoustic_tile_air_gap = 3
acoustic_tile_space = acoustic_tile_thickness + 2*acoustic_tile_air_gap

# 2d points
below_fan = 0
above_fan      =      below_fan + wall_thickness + foam_thickness + fan_depth + foam_thickness
above_intake   =      above_fan + wall_thickness + foam_thickness + min_air_passage_thickness
below_entrance =   above_intake + wall_thickness + acoustic_tile_space
above_entrance = below_entrance + wall_thickness + foam_thickness + min_air_passage_thickness

fan_right = 0
entrance_right =      fan_right - wall_thickness - foam_thickness - fan_width - acoustic_tile_air_gap
entrance_left  = entrance_right - wall_thickness - min_air_passage_thickness - foam_thickness
exit_right     =  entrance_left - wall_thickness - acoustic_tile_space
exit_left      =     exit_right - wall_thickness - min_air_passage_thickness

circular_intake_diameter = 70
circular_intake_radius = circular_intake_diameter/2
circular_intake_left = 57
circular_intake_back = 69
left_of_circular_intake = fan_right - wall_radius - foam_thickness - circular_intake_left - circular_intake_radius


walls_source = [
  [
    [exit_left, above_entrance],
    [exit_left, below_fan],
    [fan_right, below_fan],
    [fan_right, above_intake],
    [entrance_right, above_intake],
    [entrance_right, below_entrance],
    [fan_right, below_entrance],
  ],
  [
    [exit_right, above_entrance],
    [exit_right, above_fan],
    [left_of_circular_intake, above_fan],
  ],
  [
    [entrance_left, above_fan],
    [entrance_left, above_entrance],
    [fan_right, above_entrance],
  ],
]

walls_separate = []
for strip in walls_source:
  for index in range (len (strip) - 1):
    walls_separate.append (strip [index: index +2])

scad = scad_variables ({
"walls": walls_separate,
"wall_thickness": wall_thickness,
}) +"""
module walls()
  for (wall = walls) {
    hull() {
      translate (wall[0]) square (wall_thickness, center = true);
      translate (wall[1]) square (wall_thickness, center = true);
    }
  }
  
union() {

  linear_extrude (height = wall_thickness, center = true, convexity = 10) hull() walls();
  linear_extrude (height = 120, convexity = 10) walls();
}


"""

print (exit_left, above_entrance)

with open ("./target/generated.scad", "w") as file:
  file.write (scad);

print("done building air purifier stuff")

#junk junk junk
#(Dragon sometimes freezes up, and I think it happens more when it's near the end of the file, so…)
