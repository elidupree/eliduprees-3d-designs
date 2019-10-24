import json
import numpy
import math
from utils import *

class Foo(object):
  pass
a = Foo()


### Measured constants ###

a.fan_width = 120.5
a.fan_depth = 31.0
a.foam_thickness = 6
a.acoustic_tile_thickness = 15
a.prefilter_thickness = 16
a.wall_groove_tolerance_one_sided = 0.17

a.circular_intake_diameter = 70
a.circular_intake_left = 57
a.circular_intake_back = 69


### Chosen constants ###

a.wall_thickness = 0.8
a.thin_wall_thickness = 0.4
a.min_air_passage_thickness = 19
a.acoustic_tile_air_gap = 3
a.groove_depth = 3
a.bump_spacing = 12
a.between_bumps = 36
a.prefilter_border = 9
a.foam_restraining_lip_length = a.foam_thickness/2
a.foam_restraining_lip_backoff = 13.3
a.extra_exit_foam_restraining_lip_backoff = 25
a.foam_restraining_triangle_tail = a.foam_thickness*2
a.exit_connector_length = 12
a.zigzag_slope = 0.5

### Inferred stuff ###

a.wall_radius = a.wall_thickness / 2
a.thin_wall_radius = a.thin_wall_thickness / 2
a.circular_intake_radius = a.circular_intake_diameter/2
a.acoustic_tile_space = a.acoustic_tile_thickness + 2*a.acoustic_tile_air_gap
a.foam_restraining_triangle_width = a.foam_thickness + a.thin_wall_thickness


### 2d points ###

a.below_fan = 0
a.above_fan      =      a.below_fan + a.wall_thickness + a.foam_thickness + a.fan_depth + a.foam_thickness
a.above_intake   =      a.above_fan + a.wall_thickness + a.foam_restraining_triangle_width  + a.min_air_passage_thickness
a.below_entrance =   a.above_intake + a.wall_thickness + a.acoustic_tile_space
a.above_entrance = a.below_entrance + a.wall_thickness + a.foam_restraining_triangle_width  + a.min_air_passage_thickness
a.above_exit     = a.above_entrance + a.wall_thickness + a.acoustic_tile_space
a.below_exit_connector = a.above_exit - a.exit_connector_length

a.below_prefilter = a.above_entrance - a.foam_restraining_triangle_width #a.above_entrance
a.above_prefilter = a.below_prefilter + a.wall_thickness + a.prefilter_thickness

a.fan_right = 0
a.entrance_right =      a.fan_right - a.wall_thickness - a.foam_thickness - a.fan_width - a.acoustic_tile_air_gap
a.entrance_left  = a.entrance_right - a.wall_thickness - a.min_air_passage_thickness - a.foam_thickness
a.exit_right     =  a.entrance_left - a.wall_thickness - a.acoustic_tile_space
a.exit_left      =     a.exit_right - a.wall_thickness - a.min_air_passage_thickness - a.foam_restraining_triangle_width 
a.prefilter_left = a.entrance_right + a.foam_restraining_lip_backoff #a.foam_thickness*2
a.prefilter_right = a.fan_right + a.acoustic_tile_air_gap 

### More inferred stuff ###

a.left_of_circular_intake = a.fan_right - a.wall_radius - a.foam_thickness - a.circular_intake_left - a.circular_intake_radius
a.below_circular_intake = 0 + a.wall_radius + a.foam_thickness + a.fan_width - a.circular_intake_back - a.circular_intake_radius
print(a.below_circular_intake )
a.exit_radius = a.above_fan - a.below_fan

a.total_depth = a.wall_thickness + a.foam_thickness + a.fan_width + a.foam_thickness

class zigzag():
  pass
def apply_zigzag(vertices):
  result = []
  for index, vertex in enumerate (vertices):
    if vertex is not zigzag:
      result.append (numpy.array (vertex, dtype= numpy.double))
    else:
      previous = numpy.array (vertices [index -1], dtype= numpy.double)
      next = numpy.array (vertices [index +1], dtype = numpy.double)
      delta = next - previous
      length = numpy.linalg.norm (delta)
      tangent = delta/length
      normal = numpy.array ([tangent[1], - tangent[0]])
      # because zig_length = length / (num_zigs*2),
      # and we want a.acoustic_tile_air_gap / zig_length = a.zigzag_slope,
      # we want a.acoustic_tile_air_gap / (length / (num_zigs*2)) = a.zigzag_slope
      # a.acoustic_tile_air_gap*num_zigs*2 = a.zigzag_slope*length
      # num_zigs = a.zigzag_slope*length/(a.acoustic_tile_air_gap*2)
      num_zigs = int(round (a.zigzag_slope*length/(a.acoustic_tile_air_gap*2)))
      zig_length = length / (num_zigs*2)
      print(tangent, length, zig_length, normal)
      for zig_index in range (num_zigs):
        result.append (previous + tangent*zig_length*(zig_index+0.5)*2 + normal*a.acoustic_tile_air_gap)
        if zig_index < num_zigs-1:
          result.append (previous + tangent*zig_length*(zig_index+1)*2)
  return result
  
outer_wall = apply_zigzag ([
    [a.exit_left, a.above_exit],
    [a.exit_left, a.below_exit_connector],
    zigzag,
    [a.exit_left, a.below_fan + a.exit_radius + a.foam_restraining_lip_backoff + a.extra_exit_foam_restraining_lip_backoff + a.foam_restraining_triangle_tail],
    zigzag,
    [a.exit_left, a.below_fan + a.exit_radius + a.foam_restraining_lip_backoff + a.extra_exit_foam_restraining_lip_backoff],
    zigzag,
    [a.exit_left, a.above_fan],
    zigzag,
    [a.exit_left, a.below_fan],
    zigzag,
    [a.exit_left + a.exit_radius, a.below_fan],
    zigzag,
    [a.exit_left + a.exit_radius + a.foam_restraining_lip_backoff, a.below_fan],
    zigzag,
    [a.exit_left + a.exit_radius + a.foam_restraining_lip_backoff + a.foam_restraining_triangle_tail, a.below_fan],
    zigzag,
    [a.fan_right, a.below_fan],
    zigzag,
    [a.fan_right, a.above_intake],
    zigzag,
    [a.entrance_right, a.above_intake],
    zigzag,
    [a.entrance_right, a.below_entrance],
    zigzag,
    [a.prefilter_right, a.below_entrance],
    [a.prefilter_right, a.above_prefilter],
    [a.prefilter_right - a.prefilter_border, a.above_prefilter],
  ])
entrance_wall = apply_zigzag ([
    [a.prefilter_left + a.prefilter_border, a.above_prefilter],
    [a.prefilter_left, a.above_prefilter],
    [a.prefilter_left, a.above_entrance],
    zigzag,
    [a.entrance_right, a.above_entrance],
    zigzag,
    [a.entrance_left, a.above_entrance],
    zigzag,
    [a.entrance_left, a.below_entrance],
    zigzag,
    [a.entrance_left, a.above_intake],
    zigzag,
    [a.entrance_left, a.above_fan],
  ])
exit_wall = apply_zigzag ([
   [a.left_of_circular_intake - a.wall_radius, a.above_fan],
   [a.entrance_left, a.above_fan],
    zigzag,
    [a.exit_right, a.above_fan],
    zigzag,
    [a.exit_right, a.below_exit_connector],
    [a.exit_right, a.above_exit],
  ])
tile_stop_walls_near_prefilter_source = apply_zigzag ([
  [a.exit_right, a.above_exit],
  zigzag,
  [a.prefilter_left, a.above_exit],
  [a.prefilter_left, a.above_entrance],
])
walls_source = [
  outer_wall,
  exit_wall,
  entrance_wall,
  tile_stop_walls_near_prefilter_source,
  [
    [a.prefilter_left, a.above_entrance],
    [a.prefilter_left, a.below_prefilter],
    [a.prefilter_left + a.prefilter_border, a.below_prefilter],
  ],
  [
    [a.prefilter_right, a.below_prefilter],
    [a.prefilter_right - a.prefilter_border, a.below_prefilter],
  ],
]
exterior_walls_source = [
  outer_wall,
  entrance_wall + exit_wall[2:],
]
a.floor_points = outer_wall + entrance_wall + exit_wall[2:]

a.walls = []
for strip in walls_source:
  for index in range (len (strip) - 1):
    a.walls.append (strip [index: index +2])

a.tile_stop_walls_near_prefilter = []
for index in range (len (tile_stop_walls_near_prefilter_source) - 1):
    a.tile_stop_walls_near_prefilter.append (tile_stop_walls_near_prefilter_source [index: index +2])
    
a.exterior_walls = []
for strip in exterior_walls_source:
  for index in range (len (strip) - 1):
    a.exterior_walls.append (strip [index: index +2])

scad = scad_variables (vars(a)) +"""
$fn = 64;
module curve_flat(radius, thin_wall_thickness_override) {
  intersection() {
    radius_boost = (thin_wall_thickness_override-thin_wall_thickness)/2;
    outer_radius = radius + radius_boost;
    inner_radius = outer_radius - thin_wall_thickness_override;
    $fn=256;
    translate ([radius, radius]) difference() {
      //radius = wall_radius + acoustic_tile_air_gap;
      
      
      scale(outer_radius/radius) circle (r= radius ) ;
      scale(inner_radius/radius) circle (r= radius ) ;
    }
    translate([-radius_boost,-radius_boost])
      square(outer_radius + radius_boost);
  }
}

module foam_restraining_bracket(triangle, thin_wall_thickness_override) {
  module origin_circle()
    circle (r= thin_wall_thickness_override/2);
  module corner_circle()
    translate ([0, foam_thickness + wall_radius + thin_wall_radius]) origin_circle(); 
  intersection() {
    translate([-foam_thickness*3, -wall_radius]) square([foam_thickness*6, foam_thickness*3]);
  union() {hull() {
    origin_circle();
    corner_circle();
  }
  if(triangle) hull() {
    corner_circle();
    translate ([foam_restraining_triangle_tail, 0]) origin_circle(); 
  }
  hull() {
    corner_circle();
    translate ([-foam_restraining_lip_length, 0]) corner_circle(); 
  }}
  }
}

module naive_walls_flat(w) {
  for (wall = w) {
    hull() {
      translate (wall[0]) circle(wall_radius);
      translate (wall[1]) circle(wall_radius);
    }
  }
}

module walls_flat(thin_wall_thickness_override) {
  naive_walls_flat(walls);
  translate ([entrance_left, above_fan]) curve_flat (entrance_right - entrance_left, thin_wall_thickness_override);
  translate ([entrance_left, above_entrance]) mirror ([0, 1]) curve_flat (entrance_right - entrance_left, thin_wall_thickness_override);
  translate ([exit_left, below_fan]) curve_flat (exit_radius, thin_wall_thickness_override);
  
  translate ([entrance_right+foam_restraining_lip_backoff, above_fan]) foam_restraining_bracket(true, thin_wall_thickness_override);
  translate ([entrance_right+foam_restraining_lip_backoff, above_entrance]) mirror ([0, 1]) foam_restraining_bracket(false, thin_wall_thickness_override);
  translate ([exit_left+exit_radius+foam_restraining_lip_backoff, below_fan]) foam_restraining_bracket(true, thin_wall_thickness_override);
  translate ([exit_left, below_fan+exit_radius+foam_restraining_lip_backoff+extra_exit_foam_restraining_lip_backoff]) mirror ([-1, 1]) foam_restraining_bracket(true, thin_wall_thickness_override);
}

module floor_flat() union() {
  polygon (points = floor_points);
  naive_walls_flat(exterior_walls);
}
module interior() linear_extrude (height = total_depth, convexity = 10) floor_flat();

module bump() {
  radius = wall_radius + acoustic_tile_air_gap;
  shorter = radius/2;
  module flat() polygon(points = [
    [radius, 0],
    [radius, shorter],
    [shorter, radius],
    [-shorter, radius],
    [-radius, shorter],
    [-radius, 0],
  ]);
  module shape() {
    height = norm([radius,shorter])*2;
    linear_extrude(height = 2, center = true) flat();
    translate ([0, 0, 1]) linear_extrude(height = height, scale = 0) flat();
    mirror([0,0,1]) translate ([0, 0, 1]) linear_extrude(height = height, scale = 0) flat();
  }
  difference() {
    shape();
    scale((radius - thin_wall_thickness)/radius) shape();
  }
}
module bumps()// difference()
{
  $fn = 8;

  for (wall = concat(exterior_walls, tile_stop_walls_near_prefilter)) {
    //echo(wall);
   center = (wall [1] + wall [0])/2;
   delta = wall [1] - wall [0];
   length = norm (delta);
   if (
     (center [0] <= prefilter_left || center [1] <= below_entrance)
     && length >= bump_spacing*1.2
     ) {
    
    angle = atan2(delta[1], delta[0]);
    
    tangent = delta/length;
    used_length = length - bump_spacing*2;
    used_depth = total_depth - bump_spacing*2;
    rows = 1+round(used_depth/between_bumps);
    columns = max(
      used_length > bump_spacing ? 2 : 1,
      1+round(used_length/between_bumps)
    );
    //echo (rows, columns);
    for (column = [0: columns -1]) {
      horizontal_position = wall [0] + tangent*((columns <= 1) ?
        (length / 2)
        : (bump_spacing + used_length*column/(columns -1)));
      /*for (row = [0: rows - 1
      ]) {
        vertical_position = (bump_spacing + used_depth*row/(rows -1));
        position = concat(horizontal_position, [vertical_position]);
        //difference(){
        translate (position) {
          rotate([0, 0, angle+180]) bump();
        }
        //  interior();
        //}
      }*/
      
      translate (concat(horizontal_position, [-wall_radius]))
        rotate([0, 0, angle+180])
        cube([wall_thickness, wall_radius + acoustic_tile_air_gap, total_depth]);
    }
   }
  }
 // interior();
}

module fan_restricting_wall_flat() {
  translate ([left_of_circular_intake, 0]) square ([fan_right - left_of_circular_intake, below_circular_intake]);
  translate ([left_of_circular_intake-wall_thickness, 0]) square ([wall_thickness, total_depth-wall_radius]);
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

module prefilter_side_walls(cutaway) {
  for (y = [above_prefilter, below_prefilter]) {
    translate ([prefilter_left + cutaway, y - wall_radius, 0])
      cube ([(prefilter_right - prefilter_left) - 2*cutaway, wall_thickness, prefilter_border+wall_thickness]);
  }
}

module all_walls() {
  linear_extrude (height = total_depth - wall_radius, convexity = 10) walls_flat(thin_wall_thickness);
  fan_restricting_wall();
  translate ([0, 0, -wall_radius]) prefilter_side_walls(0);
}

module lid() {
  translate([0,0,-groove_depth]) intersection() {
    interior();
    thickness_override = wall_thickness * 2;
    linear_extrude (height = groove_depth, convexity = 10) difference () {
      offset(r=wall_groove_tolerance_one_sided + wall_thickness) walls_flat(thickness_override);
      offset(r=wall_groove_tolerance_one_sided) walls_flat(thickness_override);
    }
  }
  linear_extrude (height = wall_thickness, convexity = 10) floor_flat();
  translate ([0, 0, - prefilter_border]) prefilter_side_walls(prefilter_border + wall_radius + wall_groove_tolerance_one_sided);
}

module grating() {
  left = prefilter_left + prefilter_border + wall_radius;
  right = prefilter_right - prefilter_border - wall_radius;
  bottom = 0 + prefilter_border + wall_radius;
  top = total_depth - prefilter_border - wall_radius - wall_groove_tolerance_one_sided;
  width = right - left;
  height = top - bottom;
  increment = (left - right) / 6;
  module area() {
    translate ([left, bottom]) square ([width, height]) ;
  }
  module flat() intersection() {
    for (direction = [-1, 1]) {
      for (index = [-6:6]) {
        center = (left + right)/2 + increment*index;
        translate ([center, (top + bottom)/2]) rotate (atan2(increment, height/4)*direction) square ([wall_thickness, height*2], center = true);
      }
    }
    area();
  }
  translate ([0, below_prefilter]) rotate ([90, 0, 0]) linear_extrude (height = wall_thickness, center = true, convexity = 10) flat();
}

//!bump();
intersection() {
union() {
  linear_extrude (height = wall_thickness, center = true, convexity = 10) floor_flat();
  all_walls();
  bumps();
  *grating();
}
*translate ([entrance_right - 5 + 5, below_fan - 5, wall_radius-.56]) cube([(fan_right - entrance_right)/1 + 10, 25, total_depth/1]);
*translate ([prefilter_left - 5, below_prefilter - 5, wall_radius-.56]) cube([prefilter_right - prefilter_left + 10, 30, 200]);
}

*rotate([0, 180, 0]) intersection()
{
lid();
*translate ([entrance_right - 5 + 5, below_fan - 5, -100]) cube([(fan_right - entrance_right)/1 + 10, 10, 100+0.56]);
}

//rotate([0, 180, 0]) lid();

//translate ([-165, 150, 120 -259/2]) cube ([165, 40.64, 259]);
//color ("blue") translate ([-215, -5]) square (220);
//color ("blue") translate ([40, -5]) square (220);

"""

print (a.exit_left, a.above_entrance, a.total_depth)
print (a.prefilter_right - a.prefilter_left)

with open ("./target/generated.scad", "w") as file:
  file.write (scad);

print("done building air purifier stuff")

#junk junk junk
#(Dragon sometimes freezes up, and I think it happens more when it's near the end of the file, so…)
