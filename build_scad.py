constant_code = """
/*linear_extrude(height=3){offset(0.1){
        polygon(points=[[0,0],[1,0],[1.5,1],[0,1]],paths=[0,3,2,1]);
    };}
  */  
    
/*polygon(points=[[0,0],[1,0],[1.5,1],[0,1]]);*/
/*linear_extrude(height = 20) {
    //square([20, 10], center = true);
    offset(r=0.1){
        polygon(points=[[0,0],[1,0],[1.5,1],[1,0.0001]]);
    }
}*/

//polygon(points=[[0,0],[1,0],[1.5,1],[1,0.0001]]);
/*translate([10, 0, 0])
    linear_extrude(height = 20)
            polygon(points=[[0,0],[1,0],[1.5,1],[0,1]],paths=[0,1,2,1]);*/
            
//TAU = PI*2;
hexagon_long_radius = 15;
hexagon_height = 5;
hexagon_angle = 60;
hexagon_thickness = 1;
module wall_flat() {
  intersection() {
    translate ([hexagon_long_radius, 0]) rotate (hexagon_angle) {square ([9000, hexagon_thickness]);}
    square ([9000, hexagon_height]);
  }
}
module floor_flat() {
  square ([hexagon_long_radius, hexagon_thickness]);
}
module hexagon() {
rotate_extrude ($fn = 6) {union() {floor_flat(); wall_flat();}}
}

hexagon_wall_horizontal_distance = hexagon_height*cos(hexagon_angle);
hexagon_short_radius = hexagon_long_radius*sin(60);
hexagon_outer_short_radius = hexagon_short_radius + hexagon_wall_horizontal_distance;
hexagon_gap = 5;
hexagon_distance = hexagon_outer_short_radius*2 + hexagon_gap;
echo (hexagon_short_radius);

module hexagon_grid() {
for (level = [0:0]) {
for (first = [0:10]) {
  for (second = [0:10]) {
    translate ([
      second*hexagon_distance*sin(60)
      + level*hexagon_distance*cos(60)/2,
      
      first*hexagon_distance
      + (second % 2)*hexagon_distance*0.5
      + level*hexagon_distance*0.5,
      
      level*hexagon_height*2
    ]) hexagon();
  }
}

}}

//hexagon_grid();
module source_head() {
  scale (1000) import("head_fixed.stl", convexity = 10);
}
module cropped_head() {
  import("target/head_cropped.stl", convexity = 10);
}

module nose_cube() {
  translate ([0, -95, 18.5]) cube([40, 40, 18], center = true);
}


module cropped_head_from_source() {
 intersection() {
  translate ([-100, -100, -35]) cube ([200, 130, 120]);
  //translate ([0, -100, -35]) scale ([2, 1, 1]) cylinder (h = 120, r = 130);
  //translate ([0, -100, -35]) scale ([2, 1, 1]) sphere (130);
  
  union() {
    source_head();
    hull() intersection() {
      source_head();
      nose_cube();
    }
  }
 }
}

*cropped_head_from_source();

*difference() {
  translate ([-80, -100, -15]) cube ([150, 100, 73]);
  cropped_head();
}

// hangs forever
*minkowski() {
  cropped_head();
  
  sphere (r = 2, $fn = 12);
}

echo("sin", sin(60), "cos", cos(60));

module wider_nosemask_area() {
  translate ([0, -65, 30]) cube([120, 80, 150], center = true);
}

module nosemask_area() {
  union() {
    translate ([0, -65, 90]) cube([22, 80, 100], center = true);
  }
}

module wider_nosemask_face() {
  intersection() {
    cropped_head();
    wider_nosemask_area();
  }
}

/*module nosemask() {
  intersection() {
    difference() {
      union() {
        for (angle_2 = [90:90]) {
          for (angle = [90:45:270]) {
            translate ([mask_thickness*sin (angle)*sin (angle_2), mask_thickness*cos (angle)*sin (angle_2), mask_thickness*cos (angle_2)]) wider_nosemask_face();
          }
        }
      }
      translate([0.0001, 0.0001, 0.0001]) cropped_head();
    }
    nosemask_area();
  }
}*/
  
module tubing_outer() polyhedron (points = tubing_outer_points, faces = tubing_faces, convexity = 10);
module tubing_hole() polyhedron (points = tubing_inner_points, faces = tubing_faces, convexity = 10);
module nosemask() polyhedron (points = nose_points, faces = nose_faces, convexity = 10);
module nosemask_shadow() polyhedron (points = nose_shadow_points, faces = nose_faces, convexity = 10);

module whole_mask_hole() union() {
  tubing_hole();
  intersection() {
    nosemask_shadow();
    minkowski() {
      translate ([0, 0, 17]) scale([1, 1, 1]) rotate([90,0,0]) cylinder (h=500,r=15);
      translate ([0, 0, 1]) cube([18,2,2], center=true);
    }
  }
}

module elastic_holder() {
  r = 1.5;
  hole = 5;
  rotate([0,90,0]) rotate_extrude(convexity=10) translate([hole+r/2, 0, 0]) circle(r=r, $fn=12);
}
  
//translate ([0, 100, 0]) {
  difference() {
    union() {
      tubing_outer();
      nosemask();
      translate([75,-6,0]) elastic_holder();
      translate([-75,-6,0]) elastic_holder();
    }
    whole_mask_hole();
  }
  %translate ([0,0,0]) cropped_head();
//}
//*translate([0,0,-1.8]) projection(cut = true) translate ([0, 0, - 65]) source_head();
"""


import pprint
import json
import numpy
from scipy import interpolate
import math
from PIL import Image

def normalize (vector):
  return vector/numpy.linalg.norm(vector)
  
def smootherstep(left,right, x):
  f = (x - left) / (right - left)
  if f <= 0: return 0
  if f >= 1: return 1
  return f*f*f*(f*(f*6 - 15) + 10 );


def offset_measurement_points (source_coordinates, epsilon = 0.00001):
  return [
    source_coordinates,
    source_coordinates + [0, epsilon],
    source_coordinates + [epsilon, -epsilon],
    source_coordinates + [-epsilon, -epsilon],
  ]
def offset_from_measurement_points (space_points, offset):
  normal = normalize (numpy.cross(
    space_points [3]-space_points [1],
    space_points [2]-space_points [1]
  ))
  return space_points [0] - normal*offset
# A "surface" is a function that takes x,y coords and returns a 3d vector,
# assumed to be locally Euclidean
def offset_from_surface (surface, source_coordinates, offset, epsilon = 0.00001):
  measurement_points = offset_measurement_points (source_coordinates, epsilon)
  return offset_from_measurement_points ([surface (v) for v in measurement_points], offset)

face_depth_map = Image.open ("face_depthmap.png")
face_depth_map_scale = face_depth_map.height/120

def source_face_depth_nonsymmetrized(x,y):
  def raw(x,y):
    return face_depth_map.getpixel((x, y))[0]
  x = ((face_depth_map.width-1)/2) + x*face_depth_map_scale
  y = (85 - y)*face_depth_map_scale
  floorx = math.floor(x)
  floory = math.floor(y)
  xfrac = x - floorx
  yfrac = y - floory
  return -(
    raw(floorx, floory) * (1-xfrac) * (1-yfrac)
    + raw(floorx, floory+1) * (1-xfrac) * yfrac
    + raw(floorx+1, floory) * xfrac * (1-yfrac)
    + raw(floorx+1, floory+1) * xfrac * yfrac
  )/2.55

def source_face_depth(x,y):
  return (source_face_depth_nonsymmetrized(x,y) + source_face_depth_nonsymmetrized(-x,y)) / 2
  


tubing_thickness = 1
mask_thickness = tubing_thickness
CPAP_connector_outer_radius = 21.5/2

def tubing_surface (coordinates):
  slice_fraction = (coordinates [0] - 0.5)*2
  side_fraction = coordinates [1]
  
  horizontal_radius = 66
  depth_radius = 78
  tail_transition =0.1
  tail_fadeoff = 0.3
  CPAP_proportion = smootherstep((1.0-tail_transition) * (1.0 - tail_fadeoff), 1.0 - tail_transition, abs(slice_fraction))
  away_angle_ish = math.tau*3/4 + (slice_fraction / (1-tail_transition))*math.tau/4
  angular_base_point = numpy.array ([
    horizontal_radius*math.cos (away_angle_ish),
    depth_radius*math.sin (away_angle_ish),
    0
  ])
  face_proportion = smootherstep(60, 50, abs (angular_base_point [0]))
  if face_proportion > 0:
    face_position = sum(
      source_face_depth (angular_base_point [0]+d, 0) for d in range(-5, 6)
    ) / 11
    difference = face_position - angular_base_point [1]
    angular_base_point [1] += difference*face_proportion
  
  tail_fraction = (abs(slice_fraction) - 1 + tail_transition)/tail_transition
  tail_vector = numpy.array ([0, 18, -10])
  CPAP_base_point = numpy.array ([numpy.sign (slice_fraction)*(horizontal_radius), 0, -17]) + tail_vector * tail_fraction
  if CPAP_base_point [2] > angular_base_point [2]:
    CPAP_base_point [2] = angular_base_point [2]
  if CPAP_proportion < 1:
    CPAP_base_point [0] = angular_base_point[0]
  
  
  if CPAP_proportion < 1:
    away = normalize(angular_base_point) #numpy.array ([math.cos (away_angle), math.sin (away_angle), 0])
  else:
    away = numpy.array ([numpy.sign (slice_fraction), 0, 0])
    
  base_point = CPAP_proportion*CPAP_base_point + (1 - CPAP_proportion)*angular_base_point
  perpendicular = normalize(
    CPAP_proportion*normalize (numpy.cross ([1,0,0],tail_vector)) +
    (1 - CPAP_proportion)* numpy.array ([0, 0, 1]))
  
  
  
  CPAP_center = away*CPAP_connector_outer_radius
  angular_center = away*6
  center = CPAP_proportion*CPAP_center + (1 - CPAP_proportion)*angular_center
  
  
  side_angle_ish = side_fraction*math.tau
  CPAP_connector_offset = (
    perpendicular*math.cos (side_angle_ish)
    + away*math.sin (side_angle_ish)
  ) * CPAP_connector_outer_radius
  other_offset = (
    perpendicular*math.cos (side_angle_ish)* 15
    + away*math.sin (side_angle_ish)*6
  )
  offset = CPAP_proportion*CPAP_connector_offset + (1 - CPAP_proportion)*other_offset
  
  return (base_point + center + offset)
  

tubing_outer_points = []
tubing_inner_points = []
tubing_faces = []
num_slices = 100
num_sides = 32

for slice in range (num_slices):
  slice_fraction = float (slice)/float (num_slices -1)
  first_side_index = len (tubing_outer_points)
  
  if slice == 0:
    tubing_faces.append (list (range (num_sides)))
  if slice == num_slices - 1:
    tubing_faces.append (list (reversed (range (first_side_index, first_side_index+num_sides))))

  
  for side in range (num_sides):
    side_fraction = float (side - slice/2)/float (num_sides)
    
    if slice >0:
      tubing_faces.append ([
        first_side_index + side,
        first_side_index + (side + 1) % num_sides,
        previous_first_side_index + side,
      ])
      tubing_faces.append ([
        first_side_index + side,
        previous_first_side_index + side,
        previous_first_side_index + (side + num_sides - 1) % num_sides,
      ])
    
    coordinates = numpy.array ([slice_fraction, side_fraction])
    
    tubing_outer_points.append (tubing_surface (coordinates).tolist())
    tubing_inner_points.append ((offset_from_surface (tubing_surface, coordinates, -tubing_thickness) + [0, 0.0001, 0]).tolist())
  previous_first_side_index = first_side_index


nose_source = [
 (85, [0, 5, 10, 14]),
 (80, [0, 5, 10, 15]),
 (75, [0, 5, 10, 16]),
 (70, [0, 5, 10, 15]),
 (65, [0, 5, 10, 14]),
 (60, [0, 4,8,12]),
 (55, [0, 4,8,11]),
 (50, [0, 4,(8,-1),12]),
 (45, [0, 5, (10, -2), 15]),
 (40, [0, (8, -4), (15, -4), 20, 25]),
 (35, [(0, -1), (8, -3), (15, -7), (20, -2), 30, 40, 47]),
 (25, [(0, -1), (8, -1), (15, -9), (20, -9), (25, -6), (30, -2), 40, 55]),
 (15, [(0, -2), (8, -5), (15, -8), (20, -18), (25, -12), (30, -6), (40, -0), 50, 58]),
 (5, [(0, -12), (8, -12), (15, -15), (20, -15), (25, -12), (30, -6), (40, -0), 50, 60]),
 (0, [(0, -9), (8, -8), (15, -10), (20, -11), (25, -8), (30, -2), (40, -1), (50, -1), (62, -1)]),
 #(5, [(0, -2), (8, -5), (15, -6), (20, -4), (30, -2), 40, 50, 64]),
]

if False:
  pprint.pprint([
    (vertical, [
      (horizontal, None) for horizontal, depth in vertices
    ]) for vertical, vertices in nose_source
  ])

for row_index, (vertical, vertices) in enumerate (nose_source):
  new_vertices = []
  for vertex in vertices:
    if isinstance(vertex, int):
      horizontal = vertex
      depth = source_face_depth(horizontal, vertical)
    else:
      horizontal, depth = vertex
      depth = depth + source_face_depth(horizontal, vertical)
    for flip in [1, -1]:
      new_vertices.append ({
        "source_coordinates": numpy.array ([horizontal*flip, vertical]),
        "face_coordinates": numpy.array ([horizontal*flip, depth, vertical]),
        #"gradient": numpy.array ([gradient [0]*flip, gradient [1]]),
      })
  new_vertices.sort (key= lambda vertex: vertex ["source_coordinates"] [0])
  nose_source [row_index] = (vertical, new_vertices)

#pprint.pprint(nose_source)

def nose_source_vertices():
  return (vertex for (_, vertices) in nose_source for vertex in vertices)

def nose_interpolation (vertex, coordinates):
  print("deprecated")
  relative = coordinates - vertex ["source_coordinates"]
  return numpy.array ([
    coordinates [0],
    vertex ["face_coordinates"] [1] + numpy.dot(relative, vertex ["gradient"]),
    coordinates [1],
  ])

def nose_surface (coordinates):
  closest = min (nose_source_vertices(), key=lambda vertex: numpy.linalg.norm(vertex ["source_coordinates"] - coordinates))
  position = numpy.array ([0.0, 0.0, 0.0])
  closest_distance = numpy.linalg.norm(closest ["source_coordinates"] - coordinates)
  total_weight = 0
  for vertex in nose_source_vertices():
    distance = numpy.linalg.norm(vertex ["source_coordinates"] - coordinates)
    weight = 1 / (distance*distance + 0.000001) #max (0, 2 - distance / (closest_distance + 0.000001))
    total_weight += weight
    position += nose_interpolation (vertex, coordinates)*weight
  position = position/total_weight
    
  return position #numpy.array ([(coordinates [0] - 0.5)*40, -78, 85 - coordinates [1]*40])

def maybe_reverse (reverse, face):
  if reverse:
    face.reverse()
    return face
  else:
    return face

nose_points = []
nose_shadow_points = []
nose_sample_inputs = []
nose_faces = []
nose_mid_representation = []
index = 0
vertical_positions = [84.9 - vertical_index*2 for vertical_index in range(50)]
vertical_positions = [x for x in vertical_positions if x >= nose_source [-1][0]]

edgeinterp = "slinear"
left_edge = interpolate.interp1d(
  x = [vertical for vertical, _ in nose_source],
  y = [vertices [0]["source_coordinates"][0] for _, vertices in nose_source],
  kind = edgeinterp,
)
right_edge = interpolate.interp1d(
  x = [vertical for vertical, _ in nose_source],
  y = [vertices [-1]["source_coordinates"][0] for _, vertices in nose_source],
  kind = edgeinterp,
)

for vertical_index, vertical_position in enumerate (vertical_positions):
  #print (vertical_position)
  left = left_edge(vertical_position) + 1
  right = right_edge(vertical_position) - 1
  front_row = []
  back_row = []
  def do_horizontal (horizontal_position):
    coordinates = numpy.array ([horizontal_position, vertical_position])
    
    front_row.append ({"coordinates": coordinates})
    back_row.append ({"coordinates": coordinates})
  do_horizontal (left)
  for i in range (100):
    horizontal_position = -100 + (2*i + (vertical_index % 2)) * 1
    if horizontal_position > left + 0.2 and horizontal_position <right - 0.2:
      do_horizontal (horizontal_position)
  do_horizontal (right)
  for vertex in front_row + back_row:
    vertex ["index"] = index
    index += 1
  nose_mid_representation.append ([front_row, back_row])
#print(nose_mid_representation )


nose_faces.append (
      [vertex ["index"] for vertex in reversed(nose_mid_representation [0][0])] +
      [vertex ["index"] for vertex in nose_mid_representation [0][1]]
    )
nose_faces.append (
      [vertex ["index"] for vertex in nose_mid_representation [-1][0]] +
      [vertex ["index"] for vertex in reversed(nose_mid_representation [-1][1])]
    )

for vertical_index, rows in enumerate (nose_mid_representation):
  
  
  if vertical_index > 0:
    previous_rows = nose_mid_representation [vertical_index - 1]
    for end in [0, -1]:
      reverse = end== -1
      nose_faces.append (maybe_reverse (reverse, [
          rows[0][end]["index"],
          rows[1][end]["index"],
          previous_rows[0][end]["index"],
        ]))
      nose_faces.append (maybe_reverse (reverse, [
          
          rows[1][end]["index"],
          previous_rows[1][end]["index"],
          previous_rows[0][end]["index"],
        ]))
    
    for which_side, (row, previous_row) in enumerate (zip (rows, previous_rows)):
      row = [a for a in row]
      previous_row = [a for a in previous_row]
      vertex = row.pop()
      previous_row_vertex = previous_row.pop()
      reverse = which_side != 1
      while len(row) > 0 or len(previous_row) > 0:
        prev_ahead = vertex ["coordinates"] [0] > previous_row_vertex ["coordinates"] [0]
        if (prev_ahead and len(row) > 0) or len(previous_row) == 0:
            next_vertex = row.pop()
            nose_faces.append (maybe_reverse (reverse, face = [
              vertex ["index"],
              previous_row_vertex ["index"],
              next_vertex ["index"],
            ]))
            vertex = next_vertex
        else:
            next_vertex = previous_row.pop()
            nose_faces.append (maybe_reverse (reverse, face = [
              vertex ["index"],
              previous_row_vertex ["index"],
              next_vertex ["index"],
            ]))
            previous_row_vertex = next_vertex
      
  
  for which_side, row in enumerate (rows):
    
    for (horizontal_index, vertex) in enumerate (row):
      coordinates = vertex ["coordinates"]
      nose_sample_inputs.extend (offset_measurement_points (coordinates))

nose_samples = interpolate.griddata (
  points = [vertex ["source_coordinates"] for _, vertices in nose_source for vertex in vertices],
  values = [vertex ["face_coordinates"] [1] for _, vertices in nose_source for vertex in vertices],
  xi = nose_sample_inputs,
  method = "cubic",
  fill_value = 60,
)
  
i = 0
for vertical_index, rows in enumerate (nose_mid_representation):
  for which_side, row in enumerate (rows):
    for (horizontal_index, vertex) in enumerate (row):
      sample_inputs = nose_sample_inputs [i: i +4]
      samples = nose_samples [i:i+4]
      i += 4
      #print (samples)
      if which_side == 1:
        point = [sample_inputs [0] [0], samples [0], sample_inputs [0] [1]]
        nose_points.append (point)
        nose_shadow_points.append (point)
      else:
        point = offset_from_measurement_points ([
          numpy.array ([input [0], output, input [1]]) for input, output in zip (sample_inputs, samples)
          ], -mask_thickness)
        nose_points.append (point.tolist())
        point[1] = 0
        nose_shadow_points.append (point.tolist())
        


code = constant_code + f"""
tubing_inner_points = {json.dumps (tubing_inner_points)};
tubing_outer_points = {json.dumps (tubing_outer_points)};
tubing_faces = {json.dumps (tubing_faces)};
nose_points = {json.dumps (nose_points)};
nose_shadow_points = {json.dumps (nose_shadow_points)};
nose_faces = {json.dumps (nose_faces)};
mask_thickness = {mask_thickness};
tubing_thickness = {tubing_thickness};
"""


with open ("./target/generated.scad", "w") as file:
  file.write (code);
print("done")

#junk junk junk
#(Dragon sometimes freezes up, and I think it happens more when it's near the end of the file, so…)
