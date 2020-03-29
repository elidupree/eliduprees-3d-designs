import Mesh
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


def depth_map(face, depthmap_path):
  depthmap_path = os.path.join(data_path, depthmap_path)
  
  FreeCAD.Console.PrintMessage (f"Began updating depthmap at {datetime.datetime.now()}\n")
  try:
    with open(depthmap_path) as file:
      rows = json.load(file)
  except FileNotFoundError:
    rows = []
  
  
  temp_path = depthmap_path+".temp"
  
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
  
  while len(rows) <= face_top - face_bottom:
    vertical_index = len(rows)
    rows.append([
      entry (horizontal_index, vertical_index)
      for horizontal_index in range (-face_left - face_left + 1)])
    FreeCAD.Console.PrintMessage (f"{vertical_index}: {str(rows[-1])}\n")
    with open(temp_path, "w") as file:
      json.dump(rows, file)
      file.flush()
      os.fsync(file.fileno())
    os.replace(temp_path, depthmap_path)
  FreeCAD.Console.PrintMessage (f"Done updating depthmap at {datetime.datetime.now()}\n")
  
  return rows


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

def do_prototype_mask_1(face, data_filename):
  rows = depth_map(face, data_filename)
  
  def raw_face_depth(x,y):
    return rows[-face_bottom + y][-face_left - abs(x)]
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
  
  #offset_surface = surface.toShape().makeOffsetShape (0.5, 0.03, fill = False)
  
  offset_surface = Part.BSplineSurface()
  def offset_surface_position (surface_position):
    #FreeCAD.Console.PrintMessage (f"{u}, {v}\n")
    (u,v) = surface.parameter (surface_position)
    return surface_position - surface.normal (u,v)*0.5
  offset_surface_rows = [
    [offset_surface_position (face_vector((x,y))) for x in range(face_left, -face_left + 1, 3)]
      for y in range(-60, 30, 3)]
  offset_surface.buildFromPolesMultsKnots(offset_surface_rows,
    [1]*(len (offset_surface_rows) + degree + 1),
    [1]*(len(offset_surface_rows[0]) + degree + 1),
    udegree = degree,
    vdegree = degree,)
  
  FreeCAD.Console.PrintMessage (f"Done offset surface at {datetime.datetime.now()}\n")
  '''#Part.show (surface.toShape().makeOffsetShape (0.5, 0.03, fill = False), "shell")
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


def face4_thing():
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
  
  document().addObject ("Mesh::Feature", "face").Mesh = face
  
  
  face_original = Mesh.Mesh(eliduprees_3d_designs_path+"private/face5-d7.obj")
  face_original = max (face_original.getSeparateComponents(), key = lambda component: component.CountFacets)
  document().addObject ("Mesh::Feature", "face_original").Mesh = face_original
  
  
  flipped = face.copy();
  
  flip_matrix = FreeCAD.Matrix()
  flip_matrix.scale (-1, 1, 1)
  
  flipped.transform (flip_matrix )
  flipped.flipNormals()
  
  document().addObject ("Mesh::Feature", "flipped").Mesh = flipped
  
  
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
  
  def raw_face_depth(x,y):
    return rows[-face_bottom + y][-face_left - abs(x)]
  def face_depth (coordinates):
    return interpolated(coordinates, raw_face_depth)
  
  def face_vector (coordinates):
    return vector(coordinates[0], coordinates[1], face_depth (coordinates))
  
  
  # depth(10, 0) should be about 15mm
  # depth(14, 0) should be about 19mm
  FreeCAD.Console.PrintMessage (f"?? {face_depth (vector(0, -6))}, {face_depth (vector(10, -6))}, {face_depth (vector(14, -6))}\n")
  
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
  vertical_marks = nose_denser(face_bottom, -55, 15, face_top)
    
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
   
  #Part.show (surface.toShape(), "surface")
  
  eyeball_radius = 30
  eyeball_filter = Part.makeSphere (eyeball_radius, vector (-30, -8, -8 - eyeball_radius))
  eyeball_filter = eyeball_filter.fuse (eyeball_filter.mirror (vector(), vector (1, 0, 0)))
  
  surface_filtered = surface.toShape().cut(eyeball_filter)
  
  Part.show (surface_filtered, "surface_without_eyeballs")
  
  mask_cheeks_top = -26.4
  
  #test_print_box = box(centered (30), bounds(-16, 8), centered(200))
  test_print_box = box(centered (22.8), bounds(-35, 18), centered(200)).fuse ([
    box(centered (70), bounds(-35, -5), centered(200)),
    box(centered (136), bounds(-60, mask_cheeks_top), centered(200)),
  ]).cut(
    box(centered (43), bounds(-60, -41), centered(200)),
  )
  surface_filtered = surface_filtered.common(test_print_box)
  Part.show (surface_filtered, "surface_for_test_print")
  FreeCAD.Console.PrintMessage (f"Done making surface mesh at {datetime.datetime.now()}\n")
  
  def tube_bottom (top):
    direction = (top-pupil_location)
    height = top [1] - (-60)
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
    for iteration in range(100):
      bottom = tube_bottom (result)
      middle = (result + bottom)/2
      length = (bottom - result).Length
      num_samples = 10
      samples = [result  + (bottom-result) * (i+0.5) / num_samples for i in range(num_samples)]
      # +0.5 is just a hacky correction for the volume of the other mask part;
      # properly, this would be the depth of the offset surface rather than just face_depth
      average_depth = sum(sample [2] - (face_depth (sample) + 0.5) for sample in samples)/num_samples
      approximate_area = average_depth*length
      # experimentally determined that pinching one spot to 60mm^2 didn't reduce airflow much;
      # use 80mm^2 for some leeway
      if approximate_area >= 80 or bottom[0] >= 0 or bottom[0] <= -68:
        return result
      result[2] += 0.1
    FreeCAD.Console.PrintError (f"Something weird happened in picking tube coordinates for {coordinates}\n")
  
  pupil_location = vector (-36, -5, -20)
  tube_top = (
    [refined_tube_top(input) for input in approx_density (vector (-68, mask_cheeks_top), vector (-21.5, -41), 0.2)]
    #+ [refined_tube_top(input) for input in approx_density (vector (-25, mask_cheeks_top), vector (-21.5, -41), 0.2)]
    + [refined_tube_top(vector(x, -41)) for x in approx_density (-21.5, 0, 0.5) + [0, 0, 0]]
  )
  
  FreeCAD.Console.PrintMessage (f"tube_top{tube_top[-1]}\n")
  
  tube_horizontal_degree = 3
  tube_vertical_degree = 3
  
  tube_side_samples = 11
  tube_points = tube_side_samples*2 + tube_vertical_degree*4 - 4
  CPAP_end_center = vector(-77, -90, -90)
  CPAP_up = vector(0, 1, -0.5).normalized()
  CPAP_out = vector(-1,0,0)
  CPAP_forwards = CPAP_up.cross (CPAP_out)
  CPAP_outer_radius = 21.5/2
  pure_CPAP_rows = 6
  
  def CPAP_point(index, row_index):
    angle = (index - -4)*math.tau/tube_points
    return CPAP_end_center + (CPAP_up*math.cos (angle) + CPAP_out*math.sin (angle)) * CPAP_outer_radius + row_index*CPAP_forwards*5
  
  def CPAP_row (row_index):
    return [CPAP_point(index, row_index) for index in range (tube_points)]
  def tube_row(row_index, top):
    bottom =tube_bottom(top)
    samples = [top + (bottom - top) * (i) / (tube_side_samples-1) for i in range(tube_side_samples)]
    for sample in samples:
      if sample [0] >0:
        sample [0] = 0.0
      radius = 30
      max_z = (27.6 - radius) + math.sqrt (radius*radius - (-41 - sample [1])**2)
      if sample [2] >max_z:
        sample [2] = max_z
      #if sample [0] <-68:
        #sample [0] = -68.0
        
    
    bottom = samples [-1]
    corner = face_vector(samples [-1])
    top_back = face_vector(samples [0])
    result = (
      [top] * tube_vertical_degree
      + samples [1: -1]
      + [bottom] * tube_vertical_degree
      + [corner] * tube_vertical_degree
      + [face_vector (sample) for sample in samples [-2:0:-1]]
      + [top_back] * tube_vertical_degree
    )
    for index, point in enumerate (result):
      if point[0] <-68:
        result [index] = CPAP_point (index, row_index)
    if len (result) != tube_points:
      FreeCAD.Console.PrintError (f"The tube_row code is wrong {len (result)} != {tube_points}\n")
    return result
  tube_rows = [CPAP_row (index) for index in range (pure_CPAP_rows)] + [tube_row(pure_CPAP_rows + index, top) for index, top in enumerate (tube_top)]
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
  Part.show (tube_surface.toShape(), "tube_surface")
    
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
  
  #offset_surface = surface_filtered.makeOffsetShape (-0.5, 0.03, fill = True)
  #Part.show (offset_surface, "solid_for_test_print")
  
  FreeCAD.Console.PrintMessage (f"Done at {datetime.datetime.now()}\n")


def run(g):
  for key, value in g.items():
    globals()[key] = value
  globals()["data_path"] = os.path.join(os.path.dirname(os.path.dirname(eliduprees_3d_designs_path)), "data")
  face4_thing()
  
  
  