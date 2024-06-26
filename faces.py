import Mesh
import MeshPart
import datetime
import os.path
import os
import json

face_top = 92
face_left = -75
face_bottom = -124
face_front = 21
face_back = -165

face_box = Mesh.createBox(
    -face_left - face_left,
    face_top - face_bottom,
    face_front - face_back,
  )
face_box.translate (0, (face_top + face_bottom)/2, (face_front + face_back)/2)


def positioned_face_mesh (file_path, bridge, lips, left, right, flat_point, flat_point_mult=1):
  face =Mesh.Mesh(eliduprees_3d_designs_path+ file_path)
  face = max (face.getSeparateComponents(), key = lambda component: component.CountFacets)
  import datetime
  FreeCAD.Console.PrintMessage (f"Began at {datetime.datetime.now()}\n")
  
  scale = 75.5/(bridge - lips).Length
  face.translate(-bridge[0], -bridge[1], -bridge[2])
  scale_matrix = FreeCAD.Matrix()
  scale_matrix.scale (scale, scale, scale)
  face.transform (scale_matrix)
  
  horizontal = (right - left).normalized()
  forwards = (flat_point - left).cross (horizontal).normalized()
  vertical = -flat_point_mult*horizontal.cross (forwards)
  
  
  rotate_matrix = FreeCAD.Matrix(
    horizontal [0], vertical [0], forwards [0], 0,
    horizontal [1], vertical [1], forwards [1], 0,
    horizontal [2], vertical [2], forwards [2], 0,
  ).inverse()
  
  face.transform (rotate_matrix)
  if flat_point_mult == -1:
    face.flipNormals()
      
  return face



def face2_thing():
  
  FreeCAD.Console.PrintMessage (f"Began at {datetime.datetime.now()}\n")
  
  face = positioned_face_mesh (
    "private/face2.obj",
    bridge = vector (- 0.413, - 0.168, 4.833),
    lips = vector (0.795, - 0.071, 5.032),
    left = vector (20.383, 38.773, 10.240),
    right = vector (20.918, - 27.254, 33.146),
    flat_point = vector (133, 9, 35),
  )
  
  #face = face.intersect (face_box)

  document().addObject ("Mesh::Feature", "face").Mesh = face
  #document().addObject ("Mesh::Feature", "face_box").Mesh = face_box
  
  do_prototype_mask_1(face, "face.json")


def cached_rows (cache_local_path, num_rows, generate_row):
  cache_path = os.path.join(data_path, cache_local_path)
  
  FreeCAD.Console.PrintMessage (f"Began updating {cache_local_path} at {datetime.datetime.now()}\n")
  try:
    with open(cache_path) as file:
      rows = json.load(file)
  except FileNotFoundError:
    rows = []
  
  
  temp_path = cache_path+".temp"
  
  if len (rows) > 0:
    # always verify the first row
    new_first_row = generate_row(0)
    if rows [0] != generate_row(0):
      FreeCAD.Console.PrintMessage (f"Existing data in {cache_local_path} doesn't match the current function results; regenerating all rows\n")
      FreeCAD.Console.PrintMessage (f"Note: Old first row was {rows[0]}\n")
      FreeCAD.Console.PrintMessage (f"Note: Knew first row was {new_first_row}\n")
      rows = [new_first_row]
  
  if len (rows) == num_rows:
    FreeCAD.Console.PrintMessage (f"All data was already generated for {cache_local_path}; assuming it's correct\n")
  
  while len(rows) < num_rows:
    row_index = len(rows)
    rows.append(generate_row(row_index))
    FreeCAD.Console.PrintMessage (f"{row_index}: {str(rows[-1])}\n")
    with open(temp_path, "w") as file:
      json.dump(rows, file)
      file.flush()
      os.fsync(file.fileno())
    os.replace(temp_path, cache_path)
  FreeCAD.Console.PrintMessage (f"Done updating {cache_local_path} at {datetime.datetime.now()}\n")
  
  return rows

def depth_map(face, depthmap_path):
  def entry (horizontal_index, vertical_index):
    ray_start = (
      face_left + horizontal_index,
      face_bottom + vertical_index,
      face_front)
    try:
      v = next(iter(face.nearestFacetOnRay (ray_start, (0,0,-1)).values()))
      return v[2]
    except StopIteration:
      return 0
  
  def row (vertical_index):
    return [
      entry (horizontal_index, vertical_index)
      for horizontal_index in range (-face_left - face_left + 1)
    ]
  
  return cached_rows(depthmap_path, face_top - face_bottom + 1, row)


def interpolated(coordinates, raw):
    x,y = coordinates[0], coordinates[1]
    floorx = math.floor(x)
    floory = math.floor(y)
    xfrac = x - floorx
    yfrac = y - floory
    def filtered(x, y, xf, yf):
      if xf == 0 or yf == 0:
        return 0
      else:
        return raw(x, y) * xf * yf
    return (
      filtered(floorx, floory, (1-xfrac), (1-yfrac))
      + filtered(floorx, floory+1, (1-xfrac), yfrac)
      + filtered(floorx+1, floory, xfrac, (1-yfrac))
      + filtered(floorx+1, floory+1, xfrac, yfrac)
    )

def surface_point_along_line (surface, start, direction):
  line = Part.Line (start, start + direction)
  points, unknown = surface.intersect (line)
  return vector (points [0])
  
def do_prototype_mask_1(face, data_filename):
  rows = depth_map(face, data_filename)
  
  def raw_face_depth(x,y):
    try:
      return rows[-face_bottom + y][-face_left - abs(x)]
    except IndexError:
      return 0
  def face_depth (coordinates):
    return interpolated(coordinates, raw_face_depth)
  
  def face_vector (coordinates):
    return vector(coordinates[0], coordinates[1], face_depth (coordinates))
      
  '''size = 7
  rows = [[
    entry (horizontal_index, vertical_index)
    for horizontal_index in range (-size, size + 1)]
    for vertical_index in range (-size, size+1)]'''
    
  #FreeCAD.Console.PrintMessage (str(rows)+"\n")
  
  surface = Part.BSplineSurface()
  degree = 3
  surface_rows = [
    [face_vector((x,y)) for x in range(face_left, -face_left + 1, 3)]
      for y in range(-60, 30, 3)]
  surface.buildFromPolesMultsKnots(surface_rows,
    [1]*(len (surface_rows) + degree + 1),
    [1]*(len(surface_rows[0]) + degree + 1),
    udegree = degree,
    vdegree = degree,)
  
  FreeCAD.Console.PrintMessage (f"Done building surface at {datetime.datetime.now()}\n")
   
  Part.show (surface.toShape(), "surface")
  
  #offset_surface = surface.toShape().makeOffsetShape (mask_thickness, 0.03, fill = False)
  
  offset_surface = Part.BSplineSurface()
  def offset_surface_position (surface_position):
    #FreeCAD.Console.PrintMessage (f"{u}, {v}\n")
    (u,v) = surface.parameter (surface_position)
    return surface_position - surface.normal (u,v)*mask_thickness
  offset_surface_rows = [
    [offset_surface_position (face_vector((x,y))) for x in range(face_left, -face_left + 1, 3)]
      for y in range(-60, 30, 3)]
  offset_surface.buildFromPolesMultsKnots(offset_surface_rows,
    [1]*(len (offset_surface_rows) + degree + 1),
    [1]*(len(offset_surface_rows[0]) + degree + 1),
    udegree = degree,
    vdegree = degree,)
  
  FreeCAD.Console.PrintMessage (f"Done offset surface at {datetime.datetime.now()}\n")
  '''#Part.show (surface.toShape().makeOffsetShape (mask_thickness, 0.03, fill = False), "shell")
  bh = Part.Shape([Part.Circle(vector(), forwards, 30)]).to_wire().to_face().fancy_extrude(forwards, centered(303))
  foo = surface.toShape().extrude (forwards*-20)
  bar = offset_surface.extrude (forwards*-18)
  Part.show (bh, "bh")
  #Part.show (bar.common(bh).cut(foo), "shell")
  '''
  
  eye_hole_right = -13
  eye_hole_bottom = -24
  eye_hole_radius = 22
  
  eye_hole = FreeCAD_shape_builder ().build ([
    start_at (eye_hole_right, 200),
    vertical_to (eye_hole_bottom + eye_hole_radius),
    arc_radius_to (-eye_hole_radius,
      (eye_hole_right - eye_hole_radius, eye_hole_bottom)),
    horizontal_to (-200),
    close(),
  ]).to_wire().to_face().fancy_extrude (vector (0, 0, 1), centered (500))
  
  mask_mask = box(centered (110), bounds(-45, 20), centered(200)).cut([
    eye_hole,
    eye_hole.mirror(vector(), vector(1,0,0)),
  ])
  
  FreeCAD.Console.PrintMessage (f"Done making mask mask at {datetime.datetime.now()}\n")
  
  #Part.show (eye_hole)
  Part.show (mask_mask)
  Part.show (offset_surface.toShape(), "offset_surface")
  
  foo = surface.toShape().common(mask_mask).extrude (vector(0, 0, -10))
  FreeCAD.Console.PrintMessage (f"Done making foo at {datetime.datetime.now()}\n")
  bar = offset_surface.toShape().common(mask_mask).extrude (vector(0, 0, -10))
  FreeCAD.Console.PrintMessage (f"Done making bar at {datetime.datetime.now()}\n")
  baz = bar.cut(foo)
  FreeCAD.Console.PrintMessage (f"Done making baz at {datetime.datetime.now()}\n")
  
  Part.show (foo, "foo")
  Part.show (bar, "bar")
  Part.show (baz, "baz")
  
  '''import MeshPart
  surface_mesh = MeshPart.meshFromShape (
    Shape = surface.toShape().extrude (vector(0, 0, -10)),
    MaxLength = 2
  )
  FreeCAD.Console.PrintMessage (f"Done making surface mesh at {datetime.datetime.now()}\n")
  
  offset_surface_mesh = MeshPart.meshFromShape (
    Shape = offset_surface.extrude (vector(0, 0, -10)),
    MaxLength = 2
  )
  FreeCAD.Console.PrintMessage (f"Done making offset_surface mesh at {datetime.datetime.now()}\n")
  
  document().addObject ("Mesh::Feature", "surface_mesh").Mesh = offset_surface_mesh.intersect(surface_mesh)'''
  
  
  FreeCAD.Console.PrintMessage (f"Done at {datetime.datetime.now()}\n")


def face5_thing():
  left1 = vector (0.430, 0.257, 1.438)
  left2 = vector (0.388, 0.247, 1.421)
  left3 = vector (0.415, 0.267, 1.427)
  left1_fraction = 0.8
  left2_fraction = -0.1
  left = left3*(1 - left1_fraction-left2_fraction) + left2*left2_fraction + left1*left1_fraction
  
  bridge1 = vector (0.541, 0.157, 1.530)
  bridge2 = vector (0.542, 0.156, 1.534)
  bridge_fraction = -0.5
  bridge = bridge1*(1 - bridge_fraction) + bridge2*bridge_fraction
  
  face = positioned_face_mesh ("private/face5-d7.obj",
    bridge = bridge,
    lips = vector (0.607, 0.412, 1.512),
    left = left,
    right = vector (0.561, 0.243, 1.658),
    flat_point = vector (0.478, -0.012, 1.561),
    flat_point_mult=-1,
    )
  
  vertical = vector(0.01, 1, 0).normalized()
  horizontal = vector(1, 0, 0.01).normalized()
  forwards = (-vertical ).cross (horizontal)
  
  rotate_matrix = FreeCAD.Matrix(
    horizontal [0], vertical [0], forwards [0], 0,
    horizontal [1], vertical [1], forwards [1], 0,
    horizontal [2], vertical [2], forwards [2], 0,
  ).inverse()
  
  face.transform (rotate_matrix)
  
  flip_matrix = FreeCAD.Matrix()
  flip_matrix.scale (-1, 1, -1)
  face.transform (flip_matrix)
  
  show (face, "face")
  
  
  face_original = Mesh.Mesh(eliduprees_3d_designs_path+"private/face5-d7.obj")
  face_original = max (face_original.getSeparateComponents(), key = lambda component: component.CountFacets)
  show_invisible (face_original, "face_original")
  
  
  flipped = face.copy();
  
  flip_matrix = FreeCAD.Matrix()
  flip_matrix.scale (-1, 1, 1)
  
  flipped.transform (flip_matrix )
  flipped.flipNormals()
  
  show_invisible (flipped, "face_flipped")
  
  
  rows = depth_map(face, "face5_depthmap.json")
  for row in rows:
    for left_idx in range(-face_left):
      row[left_idx] = (row[left_idx] + row[-face_left*2 - left_idx]) * 0.5
  
  
  def make_bump (x, y, radius, depth):
    x = -abs(x)
    floor_radius = math.floor(radius)
    for offset_x in range (- floor_radius, floor_radius+1):
      for offset_y in range (- floor_radius, floor_radius+1):
        distance = math.sqrt (offset_x**2 + offset_y**2)
        if distance <radius:
          adj_dist = distance/radius
          bump_frac = math.exp(1 - 1/(1-adj_dist**2))
          #FreeCAD.Console.PrintMessage (f"adj_dist {adj_dist}, {radius}, {distance}, {bump_frac}\n")
          rows[-face_bottom + y + offset_y][-face_left + x + offset_x] += depth*bump_frac
  
  make_bump (10, -6, 5, -4)
  make_bump (10, 0, 5, -4)
  #make_bump (13, 2, 5, -40)
  make_bump (15, 3, 5, -3)
  make_bump (14, -1, 3, -2)
  
  # counteract greenscreen issues at center of nose
  make_bump (0, -10, 5, -1)
  make_bump (0, -20, 5, -2)
  make_bump (0, -28, 5, -0.5)
  #after prototype 4
  make_bump (0, -22, 2, -2)
  #after prototype 5
  make_bump (0, -23, 9, -1)
  make_bump (0, -27, 9, -0.5)
  make_bump (0, -31, 9, -1)
  
    
  # counteract other greenscreen bumpiness
  make_bump (0, 44, 6, -3)
  
  # enlarge bridge of nose
  make_bump (3, -5, 5, 1.5)
  make_bump (3, -10, 5, 1.5)
  make_bump (3, -15, 5, 1.5)
  make_bump (3, -20, 5, 1.5)
  # enlarge bridge of nose more, based on prototype that included the above
  make_bump (6, -10, 10, 4)
  #after prototype 4
  make_bump (8, -8, 6, 2)
  make_bump (0, -5, 6, 1)
  
  # more tweaks based on prototype that included the above
  make_bump (19, 0, 8, -7)
  make_bump (27, -1, 8, -7)
  make_bump (35, -2, 8, -7)
  make_bump (43, -3, 8, -7)
  make_bump (12, -10, 5, -5)
  make_bump (12, -5, 5, -5)
  #after prototype 4
  #make_bump(10, 0, 7, -3) # reverted for prototype 8
  #make_bump(14, -1, 6, -1.5) # reverted for prototype 8
  make_bump(0, -20, 15, 2)
  make_bump(0, -30, 20, 2)
  # after prototype 8 - make it curl away from the skin around the eyes a bit, to avoid poking
  make_bump(14, -5, 3.5, 4)
  make_bump(14, -8, 3.5, 2)
  
  #after prototype 10
  make_bump(17, -35, 10, 4)
  make_bump(17, -35, 5, 4)
  make_bump(14, -28, 10, 3)
  make_bump(14, -28, 5, 3)
  #make_bump(13, -20, 10, 3)
  make_bump(13, -20, 5, 3)
  make_bump(3, -10, 3, 1)
  
  # after 2.0-rc2
  make_bump(0, -69, 18, -3)
  make_bump(18, -14, 5, -3)
  make_bump(21, -18, 5, -3)
  
  def raw_face_depth(x,y):
    try:
      return rows[-face_bottom + y][-face_left - abs(x)]
    except IndexError:
      return 0
  def face_depth (coordinates):
    return interpolated(coordinates, raw_face_depth)
  
  def face_vector (coordinates):
    return vector(coordinates[0], coordinates[1], face_depth (coordinates))
  
  
  # depth(10, 0) should be about 15mm
  # depth(14, 0) should be about 19mm
  FreeCAD.Console.PrintMessage (f"?? {face_depth (vector(0, -6))}, {face_depth (vector(10, -6))}, {face_depth (vector(14, -6))}\n")
  
  
  mask_thickness = 0.6
  
  def approx_density(a, b, density):
    if type(a) is FreeCAD.Vector:
      length = (b - a).Length
    else:
      length = abs (b - a)
    count = math.ceil(length* density)
    return [a + (b-a) * i / count for i in range(count)]
  def nose_denser(a, b, c, d):
    return approx_density(a, b, 0.2) + approx_density(b, c, 0.5) + approx_density(c, d, 0.2) + [d]
    
  horizontal_marks = nose_denser(face_left, -25, 25, -face_left)
  vertical_marks = nose_denser(-75, -55, 15, 30) # nose_denser(face_bottom, -55, 15, face_top)
    
  surface = Part.BSplineSurface()
  degree = 3
  surface_rows = [
    [face_vector((x,y)) for x in horizontal_marks]
      for y in vertical_marks]
  surface.buildFromPolesMultsKnots(surface_rows,
    [1]*(len (surface_rows) + degree + 1),
    [1]*(len(surface_rows[0]) + degree + 1),
    udegree = degree,
    vdegree = degree,)
    
  #surface.approximate(surface_rows, 0, 5, 2, 0.1)
  
  FreeCAD.Console.PrintMessage (f"Done building surface at {datetime.datetime.now()}\n")
   
  show_invisible (surface.toShape(), "surface")
  
  eyeball_radius = 30
  eyeball_filter = Part.makeSphere (eyeball_radius, vector (-30, -8, -8 - eyeball_radius))
  eyeball_filter = eyeball_filter.fuse (eyeball_filter.mirror (vector(), vector (1, 0, 0)))
  
  surface_filtered = surface.toShape().cut(eyeball_filter)
  
  show_invisible (surface_filtered, "surface_without_eyeballs")
  
  mask_cheeks_top = -26.4
  mask_cheeks_bottom = -60
  
  def rounded_box(*args, radius):
    b = box(*args)
    return b.makeFillet(radius, [edge for edge in b.Edges if 
      edge.BoundBox.XMin == edge.BoundBox.XMax
      and edge.BoundBox.YMin == edge.BoundBox.YMax])
    
  
  #test_print_box = box(centered (30), bounds(-16, 8), centered(200))
  mask_bounds = rounded_box(centered (22.8), bounds(-35, 18), centered(200), radius = 2).fuse ([
    box(centered (70), bounds(-35, -5), centered(200)),
    rounded_box(centered (136), bounds(mask_cheeks_bottom, mask_cheeks_top), centered(200), radius = 5),
  ]).cut(
    rounded_box(centered (43), bounds(-52, -41), centered(200), radius = 4),
  )
  surface_filtered = surface_filtered.common(mask_bounds)
  
  FreeCAD.Console.PrintMessage (f"Done making surface mesh at {datetime.datetime.now()}\n")
  
  
    
  tube_horizontal_degree = 3
  tube_vertical_degree = 3
  
  tube_side_samples = 11
  tube_extra_bottom_samples = 5
  tube_points = tube_side_samples*2 + tube_extra_bottom_samples #+ tube_vertical_degree*4 - 4
  CPAP_end_center = vector(-78, -90, -90)
  CPAP_up = vector(0, 1, -0.5).normalized()
  CPAP_out = vector(-1,0,0)
  CPAP_forwards = CPAP_up.cross (CPAP_out)
  CPAP_outer_radius = (21.5 + (21.5 - 20.7)) / 2 #was just 21.5/2, but rc6 printed slightly warped in a way where the minimum diameter was 20.7, and one of my CPAP hoses was slightly loose on it
  CPAP_wall_thickness = 1.0
  num_pure_CPAP_rows = 6
  tube_surface_bottom = mask_cheeks_bottom + mask_thickness
  
  pupil_location = vector (-36, -5, -25)
  tube_middle_top = -39.5
  
  
  vision_shadow_top = [face_vector (coordinates) for coordinates in (
    approx_density (vector (-68, 10), vector (-68, mask_cheeks_top), 0.2)
    + approx_density (vector (-68, mask_cheeks_top), vector (-21.5, tube_middle_top), 0.2)
    + approx_density (vector(-21.5, tube_middle_top), vector(0, tube_middle_top), 0.5) + [vector(0, tube_middle_top)]
  )]
  vision_shadow_rows = [[top, (top - pupil_location).normalized()*200] for top in vision_shadow_top]
  vision_shadow_surface = Part.BSplineSurface()
  vision_shadow_surface.buildFromPolesMultsKnots(vision_shadow_rows,
      [1]*(len(vision_shadow_rows) + tube_horizontal_degree + 1),
      [1]*(len (vision_shadow_rows[0]) + 1 + 1),
      udegree = tube_horizontal_degree,
      vdegree = 1,
      )
  vision_shadow_face = vision_shadow_surface.toShape()
  vision_solid = vision_shadow_face.extrude (vector (0, 0, 500))
  vision_solid_mirror = vision_solid.mirror (vector(), vector (1, 0, 0))
  vision_shadow_face = vision_shadow_face.cut(vision_solid_mirror)
  vision_shadow_face = vision_shadow_face.fuse (vision_shadow_face.mirror (vector(), vector (1, 0, 0))).common(box(centered(500), bounds(-110, 100), centered(500)))
  show_invisible(vision_shadow_face, "vision_shadow_face")
  #return
  
  
  def tube_bottom (top):
    p = pupil_location.copy()
    if top[0] > 0:
      p[0] = -p[0]
    direction = (top-p)
    height = top [1] - tube_surface_bottom
    result = top - direction*height/direction [1]
    #if result [0] < face_left:
    #  width = top [0] - face_left
    #  result = top - direction*width/direction [0]
    #if result [0] > 0:
    #  width = top [0] - 0
    #  result = top - direction*width/direction [0]
    #if result [2] > 27.6:
    #  result[2] = 27.6
    return result
  def refined_tube_top(coordinates):
    result = face_vector(coordinates)
    for iteration in range(1000):
      bottom = tube_bottom (result)
      middle = (result + bottom)/2
      length = (bottom - result).Length
      num_samples = 10
      samples = [result  + (bottom-result) * (i+0.5) / num_samples for i in range(num_samples)]
      
      angle = (bottom - result)
      angle[1] = 0.0
      angle.normalize()
      def approximate_depth (sample):
        first = face_vector (sample)
        second = face_vector (sample + vector (0.01, 0, 0))
        third = face_vector (sample + vector (0, 0.01, 0))
        approximate_normal = (second - first).cross (third - first)
        approximate_normal [1] = 0.0
        approximate_normal.normalize()
        usable_fraction = abs (approximate_normal.dot(angle))
        #usable_fraction = (usable_fraction*2 + 1.0)/3
        depth = sample [2] - first [2]
        #return depth - 0.5
        return depth*usable_fraction - mask_thickness
        
      
      average_depth = sum(approximate_depth (sample) for sample in samples)/num_samples
      approximate_area = average_depth*length
      # experimentally determined that pinching one spot to 60mm^2 didn't reduce airflow much;
      # we used to use 80mm^2 for some leeway; after observations that it did seem
      # to reduce airflow, we increased it
      if approximate_area >= 120 or bottom[0] >= 0 or bottom[0] <= -68 or coordinates[0] >= 0:
        return result
      result[2] += 0.1
    FreeCAD.Console.PrintError (f"Something weird happened in picking tube coordinates for {coordinates}\n")
  
  
  tube_top_last_part = [refined_tube_top(vector(x, tube_middle_top)) for x in approx_density (-21.5, 0, 0.5) + [0]]
  tube_top = (
    [refined_tube_top(input) for input in approx_density (vector (-68, mask_cheeks_top), vector (-21.5, tube_middle_top), 0.2)]
    #+ [refined_tube_top(input) for input in approx_density (vector (-25, mask_cheeks_top), vector (-21.5, tube_middle_top), 0.2)]
    + tube_top_last_part
  )
  tube_top_unexpanded = [face_vector(c) for c in tube_top]
  
  FreeCAD.Console.PrintMessage (f"tube_top{tube_top[-1]}\n")

  def make_tube_splayed_surface(tube_top):
    tube_splayed_rows = [
      [top, tube_bottom (top)] for top in tube_top
    ]
    tube_splayed_rows = (
      [tube_splayed_rows [0]]*(tube_horizontal_degree - 1)
      + tube_splayed_rows
      + [tube_splayed_rows [-1]]*(tube_horizontal_degree - 1)
    )
    tube_splayed_surface = Part.BSplineSurface()
    tube_splayed_surface.buildFromPolesMultsKnots(tube_splayed_rows,
      [1]*(len(tube_splayed_rows) + tube_horizontal_degree + 1),
      [1]*(len (tube_splayed_rows[0]) + 1 + 1),
      udegree = tube_horizontal_degree,
      vdegree = 1,
      )
    return tube_splayed_surface
  
  tube_splayed_surface = make_tube_splayed_surface(tube_top)
  tube_splayed_surface_unexpanded = make_tube_splayed_surface(tube_top_unexpanded)
  show_invisible (tube_splayed_surface.toShape(), "tube_splayed_surface")
  show_invisible (tube_splayed_surface_unexpanded.toShape(), "tube_splayed_surface_unexpanded")
  
  def tube_resampled_entry (horizontal_index, vertical_index):
    if horizontal_index < len(tube_top):
      top = tube_top [horizontal_index]
    else:
      top = tube_top [-2-(horizontal_index-len(tube_top))].copy()
      top[0] = -top[0]
    bottom = tube_surface_bottom
    close_to_edge_ness = -60 - top[0]
    if close_to_edge_ness > 0:
      bottom += close_to_edge_ness * 0.3
    sample_point =top + vector (0, (bottom - top [1])*vertical_index/(tube_side_samples -1), 0)
    #FreeCAD.Console.PrintMessage (f"sampling at {sample_point}\n")
    if sample_point[0] > 0:
      sample_point[0] = -sample_point[0]
      result = surface_point_along_line (
        tube_splayed_surface_unexpanded,
        sample_point,
        vector (0, 0, -1)
      )
      result[0] = -result[0]
      return result
    else:
      return surface_point_along_line (
        tube_splayed_surface,
        sample_point,
        vector (0, 0, -1)
      )

  def tube_resampled_row (horizontal_index):
    return [
      tube_resampled_entry (horizontal_index, vertical_index)
      for vertical_index in range (tube_side_samples)
    ]
  
  '''tube_resampled_rows = cached_rows (
    "tube_resampled_rows.json",
    len (tube_top),
    tube_resampled_row
  )'''
  
  tube_resampled_rows = [tube_resampled_row (horizontal_index) for horizontal_index in range (len (tube_top) + len(tube_top_last_part) + tube_horizontal_degree)]
  FreeCAD.Console.PrintMessage (f"Done resampling tube at {datetime.datetime.now()}\n")
  
  def CPAP_point(index, row_index):
    angle = (index - -4)*math.tau/tube_points
    return CPAP_end_center + (CPAP_up*math.cos (angle) + CPAP_out*math.sin (angle)) * (CPAP_outer_radius-CPAP_wall_thickness) + row_index*CPAP_forwards*5
  
  def CPAP_row (row_index):
    return [CPAP_point(index, row_index) for index in range (tube_points)]
  def tube_row(samples):
    samples = [sample.copy() for sample in samples]
    for sample in samples:
      radius = 30
      max_z = (32 - radius) + math.sqrt (radius*radius - (-50 - sample [1])**2 - min((sample[0]*1.5)**2, 15*15))
      if sample [2] >max_z:
        sample [2] = max_z
      #if sample [0] <-68:
        #sample [0] = -68.0
    back_samples = [face_vector (sample) - vector(0, 0, 5) for sample in reversed (samples)]
    #FreeCAD.Console.PrintMessage (f"top{top}\n")
    top = samples [0]
    bottom = samples [-1]
    corner = back_samples [0]
    top_back = back_samples [-1]
    result = (
      [top] #* tube_vertical_degree
      + samples [1: -1]
      + [bottom] #* tube_vertical_degree
      + [bottom + (corner - bottom)*(index + 1)/(tube_extra_bottom_samples + 2) for index in range (tube_extra_bottom_samples)]
      + [corner] #* tube_vertical_degree
      + back_samples [1: -1]
      + [top_back] #* tube_vertical_degree
    )
    if len (result) != tube_points:
      FreeCAD.Console.PrintError (f"The tube_row code is wrong {len (result)} != {tube_points}\n")
    for control in result:
      offset = max (0, (control [0] - 20)*1.0)
      control [2] = control [2] - offset
    return result
  
  pure_CPAP_rows = [CPAP_row (index) for index in #[0]*(tube_horizontal_degree - 1)+
      list ( range (num_pure_CPAP_rows))]
  pure_tube_rows = [tube_row(row) for row in tube_resampled_rows]
  transition_rows = [
    [(first + second)*0.5 + vector (-8, 7, 5) for first, second in zip (pure_CPAP_rows [-1], pure_tube_rows [0])]
  ]
  tube_rows = (
    pure_CPAP_rows
    + transition_rows
    +pure_tube_rows[1:]
  )
  FreeCAD.Console.PrintMessage (f"tube_rows{tube_rows[1][-1]}\n")
  
  tube_surface = Part.BSplineSurface()
  tube_surface.buildFromPolesMultsKnots(tube_rows,
    [1]*(len(tube_rows) + tube_horizontal_degree+ 1),
    [1]*(len (tube_rows[0]) + 1),
    udegree = tube_horizontal_degree,
    vdegree = tube_vertical_degree,
    vperiodic=True,
    )
    
  FreeCAD.Console.PrintMessage (f"Done building tube surface at {datetime.datetime.now()}\n")
  show_invisible (tube_surface.toShape(), "tube_surface")
    
  '''offset_surface = Part.BSplineSurface()
  mask_thickness = 0.5
  def offset_surface_position (surface_position):
    #FreeCAD.Console.PrintMessage (f"{u}, {v}\n")
    (u,v) = surface.parameter (surface_position)
    normal = surface.normal (u,v)
    #return surface_position - vector(normal[0], 0, normal[2])*mask_thickness
    return surface_position - normal*mask_thickness
  offset_surface_rows = [
    [offset_surface_position (face_vector((x,y))) for x in horizontal_marks]
      for y in vertical_marks]
  offset_surface.buildFromPolesMultsKnots(offset_surface_rows,
    [1]*(len (offset_surface_rows) + degree + 1),
    [1]*(len(offset_surface_rows[0]) + degree + 1),
    udegree = degree,
    vdegree = degree,)
  
  offset_surface_filtered = offset_surface.toShape().common(test_print_box)
  FreeCAD.Console.PrintMessage (f"Done making offset_surface mesh at {datetime.datetime.now()}\n")
    
  Part.show (surface_filtered.extrude(vector(0, 0, 100)).common(
  offset_surface_filtered .extrude(vector(0,0,-100))), "surface_for_test_print")'''
  
  
  rib_rows = [
    [face_vector (vector(horizontal, vertical)) + vector (0, 0, 1 if (abs (horizontal) == 2 or vertical == -1) else 1.9)*mask_thickness for vertical in approx_density(-1, 18, 1) + [18,18]]
    for horizontal in range (-2, 3)
  ]
  rib_surface = Part.BSplineSurface()
  rib_surface.buildFromPolesMultsKnots(rib_rows,
    [1]*(len(rib_rows) + 1+ 1),
    [1]*(len (rib_rows[0]) +2+ 1),
    udegree = 1,
    vdegree = 2,
    )
  rib_solid = rib_surface .toShape().extrude (vector (0, 0, - mask_thickness*0.95))
  
  elastic_width = 12
  elastic_holder_strut_width = 8
  elastic_holder_width = elastic_width + elastic_holder_strut_width*2
  elastic_space_thickness = 2.5
  elastic_holder_penetration_leeway = mask_thickness*2
  elastic_holder_diameter = 3
  elastic_holder_cylinder_radius = elastic_holder_diameter/2
  elastic_holder_cylinder_curve_thingy = elastic_space_thickness / 2 # fillet, but dragon doesn't understand that word
  elastic_holder_cylinder_center_xz = vector (- elastic_holder_cylinder_radius, elastic_holder_penetration_leeway + elastic_space_thickness + elastic_holder_cylinder_radius)
  diagonal_end_xz = vector (- 12, 0)
  elastic_strut_shape = FreeCAD_shape_builder().build ([
    start_at (0, 0),
    vertical_to (elastic_holder_penetration_leeway + elastic_space_thickness + elastic_holder_cylinder_radius),
    arc_radius_to (elastic_holder_cylinder_radius, point_circle_tangent (diagonal_end_xz, (elastic_holder_cylinder_center_xz, elastic_holder_cylinder_radius), -1)),
    diagonal_to (diagonal_end_xz),
    close(),
  ]).as_xz().to_wire().to_face()
  
  elastic_strut_solid = elastic_strut_shape.fancy_extrude (vector (0, 1, 0), centered (elastic_holder_width))
  
  elastic_strut_cylinder_filter = FreeCAD_shape_builder().build ([
    start_at (elastic_holder_cylinder_radius + elastic_space_thickness, elastic_width/2 - elastic_holder_cylinder_curve_thingy),
    arc_radius_to (elastic_holder_cylinder_curve_thingy, vector (elastic_holder_cylinder_radius, elastic_width/2 - elastic_holder_cylinder_curve_thingy)),
    vertical_to (-(elastic_width/2 - elastic_holder_cylinder_curve_thingy)),
    arc_radius_to (elastic_holder_cylinder_curve_thingy, vector (elastic_holder_cylinder_radius + elastic_space_thickness, -(elastic_width/2 - elastic_holder_cylinder_curve_thingy))),
    close(),
  ]).to_wire().to_face().revolve (vector(), vector (0, 1, 0), 360).translated (vector (elastic_holder_cylinder_center_xz [0], 0,elastic_holder_cylinder_center_xz [1]))
  
  elastic_strut_solid = elastic_strut_solid.cut(elastic_strut_cylinder_filter)
  
  elastic_strut_profile_filter = FreeCAD_shape_builder().build ([
    start_at (elastic_holder_width/2, 0),
    diagonal_to ((elastic_width/2 + 1, elastic_holder_cylinder_center_xz[1] + elastic_holder_cylinder_radius)),
    horizontal_to (-(elastic_width/2 + 1)),
    diagonal_to ((-elastic_holder_width/2, 0)),
    close(),
  ]).as_yz().to_wire().to_face().fancy_extrude (vector (1, 0, 0), centered (100)),
  
  elastic_strut_solid = elastic_strut_solid.common(elastic_strut_profile_filter).translated(vector(0, 0, -mask_thickness))
  
  elastic_strut_right_solid = elastic_strut_solid.rotated (vector(), vector (0, 1, 0), 60).translated (vector(68, -43, -43))
  elastic_strut_left_solid = elastic_strut_solid.mirror(vector(), vector(1, 0, 0)).rotated (vector(), vector (1, 0, 0), -22).rotated (vector(), vector (0, 1, 0), -48).translated (vector(-73, -45, -35.5))
  
    
  filter_slot_theoretical_wall_thickness = 0.5
  filter_slider_thickness = 0.36
  filter_assumed_thickness = 1.5
  filter_slot_inner_thickness = filter_assumed_thickness+filter_slider_thickness*2
  filter_slot_outer_thickness = filter_slot_inner_thickness + filter_slot_theoretical_wall_thickness*2
  filter_slot_grip_size = 1.5
  filter_slot_outer_width = 36
  filter_slot_outer_height = 26
  filter_slot_upper_diagonal_width = 18
  filter_slot_upper_diagonal_height = 26-14
  
  def filter_slot_boundary (vertical_extension = 0):
    return FreeCAD_shape_builder().build ([
      start_at (0, 0),
      horizontal_to (23),
      diagonal_to (filter_slot_outer_width, 9),
      vertical_to (filter_slot_outer_height + vertical_extension),
      horizontal_to (filter_slot_upper_diagonal_width),
      diagonal_to (0, filter_slot_outer_height - filter_slot_upper_diagonal_height + vertical_extension),
      close(),
    ]).to_wire()

  
  filter_slot_outer_boundary = filter_slot_boundary()
  filter_slot_outer_boundary_extended = filter_slot_boundary(10)
  filter_slot_hole_boundary = filter_slot_outer_boundary.makeOffset2D (-(filter_slot_theoretical_wall_thickness + filter_slot_grip_size))
  filter_slot_slider_space = filter_slot_outer_boundary_extended.makeOffset2D (-filter_slot_theoretical_wall_thickness).to_face().fancy_extrude(vector(0,0,1), bounds(filter_slot_theoretical_wall_thickness, filter_slot_theoretical_wall_thickness + filter_slot_inner_thickness))
  filter_slot_outer_shape = filter_slot_outer_boundary.to_face().fancy_extrude(vector(0,0,1), bounds(0, filter_slot_outer_thickness))
  filter_slot_extra_shape = filter_slot_outer_boundary.to_face().fancy_extrude(vector(0,0,1), bounds(-3, 0)).cut(filter_slot_hole_boundary.to_face().fancy_extrude(vector(0,0,1), bounds(-10, 0)))
  filter_slot_cut = filter_slot_hole_boundary.to_face().fancy_extrude(vector(0,0,1), bounds(-1.7, filter_slot_outer_thickness+1)).fuse (filter_slot_slider_space)
  
  filter_slot_precarious_strip_remover = filter_slot_outer_boundary_extended.makeOffset2D (-(filter_slot_theoretical_wall_thickness + filter_slot_grip_size)).to_face().fancy_extrude(vector(0,0,1), bounds(filter_slot_theoretical_wall_thickness, filter_slot_outer_thickness))
  
  filter_slot = filter_slot_outer_shape.cut([filter_slot_cut, filter_slot_precarious_strip_remover])
  #show(filter_slot, "filter_slot1")
  #show(filter_slot_precarious_strip_remover, "filter_slot_precarious_strip_remover")
  
  # this tolerance is affected by the print quality!
  # we set it to 0.9 based on a .28mm-layer-height print,
  # but 0
  filter_slider_tolerance_each_side = 0.5
  filter_slider_boundary_offset = filter_slot_theoretical_wall_thickness+filter_slider_tolerance_each_side
  filter_slider_boundary = filter_slot_outer_boundary.makeOffset2D (- (filter_slider_boundary_offset))
  filter_slider_interior_offset = filter_slider_boundary_offset + filter_slot_grip_size
  filter_slider_boundary_inner = filter_slot_outer_boundary.makeOffset2D (- (filter_slider_interior_offset))
  
  filter_slider_outer_shape = filter_slider_boundary.to_face().fancy_extrude (vector (0, 0, 1), filter_slider_thickness)
  filter_slider = filter_slider_outer_shape.cut(filter_slider_boundary_inner.to_face().fancy_extrude (vector (0, 0, 1), filter_slider_thickness))
  
  filter_slider_bar_width = 1.5
  def filter_slider_bars(start, end, count, dim):
    translation = vector()
    translation[dim] = 1.0
    return [box(
      filter_slider_bar_width if dim == 0 else centered(100),
      filter_slider_bar_width if dim == 1 else centered(100),
      centered(100)).translated (translation * ((start - filter_slider_bar_width) + (index+1)*(end - (start - filter_slider_bar_width))/(count+1))) for index in range (count)]
  
  
  filter_slider = filter_slider.fuse(
    filter_slider_bars(filter_slider_interior_offset, filter_slot_outer_width-filter_slider_interior_offset, 3, 0) +
    filter_slider_bars(filter_slider_interior_offset, filter_slot_outer_height-filter_slider_interior_offset, 2, 1)
  ).common(filter_slider_outer_shape)
  
  filter_slider_upper_diagonal_angle = math.atan2(filter_slot_upper_diagonal_height, filter_slot_upper_diagonal_width)
  filter_slider = filter_slider.translated(vector(0, -filter_slot_outer_height + filter_slot_upper_diagonal_height)).rotated(vector(), vector(0,0,1), -filter_slider_upper_diagonal_angle*360/math.tau - 90).translated(vector(-filter_assumed_thickness/2 + filter_slider_boundary_offset, 0, 0))
  
  filter_slider_upper_diagonal_length = math.sqrt(filter_slot_upper_diagonal_height**2 + filter_slot_upper_diagonal_width**2)
  filter_slider = filter_slider.fuse([
    filter_slider.mirror(vector(), vector (1, 0, 0)),
    box(centered(filter_assumed_thickness), bounds(-21.3305, -0.535184), filter_slider_thickness)
  ])
  
  
  def position_filter_slot(shape):
    shape.rotate(vector(), vector (1, 0, 0), 8)
    shape.rotate(vector(), vector (0, 1, 0), 68)
    shape.translate (vector (5.5, - 59.2, 29.8))  
  
  position_filter_slot(filter_slot)
  position_filter_slot(filter_slot_extra_shape)
  position_filter_slot(filter_slot_cut)
  
  show(filter_slider, "filter_slider")
  
  
  # cuts = ~30sec, final mask solid generation = ~3min
  final = False
  #final = True
  do_cuts = final
  #do_cuts = True
  
  if do_cuts:
    surface_filtered = surface_filtered.cut(filter_slot_cut)
  
  show(filter_slot, "filter_slot", invisible = do_cuts)
  show (surface_filtered, "mask_surface", invisible=final)
  show (rib_solid, "rib", invisible=final)
  show (elastic_strut_right_solid, "elastic_strut_right_solid", invisible=final)
  show (elastic_strut_left_solid, "elastic_strut_left_solid", invisible=final)
  
  if final:
    mask_solid = surface_filtered.makeOffsetShape (-mask_thickness, 0.03, fill = True)
    show(mask_solid, "mask_solid", invisible=True)
    FreeCAD.Console.PrintMessage (f"Done making mask_solid at {datetime.datetime.now()}\n")
  
  tube_offset_surface = tube_surface.toShape().makeOffsetShape (-mask_thickness, 0.03, fill = True)
  show (tube_offset_surface, "tube_offset_surface", invisible = do_cuts)
  FreeCAD.Console.PrintMessage (f"Done making tube_offset_surface at {datetime.datetime.now()}\n")
  
  CPAP_thickener = tube_surface.toShape().common(box(centered(500), bounds(-100, -68), centered(500))).makeOffsetShape (-1.0, 0.03, fill = True)
  show (CPAP_thickener, "CPAP_thickener", invisible = do_cuts)
  FreeCAD.Console.PrintMessage (f"Done making CPAP_thickener at {datetime.datetime.now()}\n")
  
  if do_cuts:
    tube_solid_uncut = tube_offset_surface # Part.makeSolid(tube_offset_surface)
    tube_cut = surface.toShape().extrude(vector (0, 0, -30))
    
    '''air_exit_hole = FreeCAD_shape_builder().build ([
      start_at(-57, 8),
      vertical_to (-8),
      diagonal_to ((-43, 0)),
      close(),
    ]).as_yz().to_wire().to_face().fancy_extrude (vector (1, 0, 0), centered (10))'''
    
    
    tube_cut = tube_cut.fuse([
      #air_exit_hole.rotated (vector(), vector (0, 1, 0), -30).translated (vector (16, 0, 12)),
      #air_exit_hole.rotated (vector(), vector (0, 1, 0), 30).translated (vector (-16, 0, 12)),
      filter_slot_cut
    ])
    tube_solid = tube_solid_uncut.cut(tube_cut)
    elastic_strut_right_solid = elastic_strut_right_solid.cut(tube_cut)
    elastic_strut_left_solid = elastic_strut_left_solid.cut(tube_cut)
    tube_interior_cut = tube_surface.toShape().extrude(vector(0,0,-100))
    show_invisible (tube_interior_cut, "tube_interior_cut")
    #note: the "common" here should actually be "cut", but FreeCAD did the above extrude wrong somehow, so it's reversed
    #filter_slot = filter_slot.common(tube_interior_cut)
    filter_slot_extra_shape = filter_slot_extra_shape.cut(tube_cut).common(tube_interior_cut)
    #tube_solid.re
    FreeCAD.Console.PrintMessage (f"Done cutting tube_offset_surface at {datetime.datetime.now()}\n")
    show_invisible (tube_solid_uncut, "tube_solid_uncut")
    show_invisible (tube_cut, "tube_cut")
    show (tube_solid, "tube_solid", invisible = final)
    show (filter_slot, "filter_slot_cut", invisible = final)
  
  show(filter_slot_extra_shape, "filter_slot_extra", invisible=final)
  
  if final:
    show (Part.Compound ([mask_solid, tube_solid, CPAP_thickener, rib_solid, elastic_strut_right_solid, elastic_strut_left_solid, filter_slot, filter_slot_extra_shape]), "final_solid")
    pass #Part.show (mask_solid.fuse(tube_solid), "final_solid")
  
  
  FreeCAD.Console.PrintMessage (f"Done at {datetime.datetime.now()}\n")
  
  # Printing notes:
  # Use 235C instead of 255C to reduce stringing somewhat (220 was a bit too low)
  # "Combing mode: All" also helps with that
  # It needs to print with support all along the bottom edge, or bits will get bent back and forth a little while printing and make stuff print in slightly the wrong place; I used 50 degrees and added support blockers to avoid unnecessarily supporting stuff above that


def run(g):
  for key, value in g.items():
    globals()[key] = value
  globals()["data_path"] = os.path.join(os.path.dirname(os.path.dirname(eliduprees_3d_designs_path)), "data")
  face5_thing()
  
  
  