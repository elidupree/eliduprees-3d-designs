import json
import numpy
import math
from utils import *


with open ("./target/generated.scad", "w") as file:
  file.write ('''
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
  ''');

print("done building experiment(s)")

#junk junk junk
#(Dragon sometimes freezes up, and I think it happens more when it's near the end of the file, so…)
