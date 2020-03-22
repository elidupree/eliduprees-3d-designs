import Mesh

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
  
  scale = 74.3/(bridge - lips).Length
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
  import datetime
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
  
  import os.path
  import os
  import json
  data_path = os.path.join(os.path.dirname(os.path.dirname(eliduprees_3d_designs_path)), "data")
  face_path = os.path.join(data_path, "face.json")
  temp_path = os.path.join(data_path, "face.json.temp")
  
  FreeCAD.Console.PrintMessage (f"Began updating depthmap at {datetime.datetime.now()}\n")
  try:
    with open(face_path) as file:
      rows = json.load(file)
  except FileNotFoundError:
    rows = []
  
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
    os.replace(temp_path, face_path)
  FreeCAD.Console.PrintMessage (f"Done updating depthmap at {datetime.datetime.now()}\n")
 
  def face_depth (coordinates):
    def raw(x,y):
      return rows[-face_bottom + y][-face_left - abs(x)]
    x,y = coordinates[0], coordinates[1]
    floorx = math.floor(x)
    floory = math.floor(y)
    xfrac = x - floorx
    yfrac = y - floory
    return (
      raw(floorx, floory) * (1-xfrac) * (1-yfrac)
      + raw(floorx, floory+1) * (1-xfrac) * yfrac
      + raw(floorx+1, floory) * xfrac * (1-yfrac)
      + raw(floorx+1, floory+1) * xfrac * yfrac
    )
  
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
    [1]*(len (surface_rows) + degree + 1),
    [1]*(len(surface_rows[0]) + degree + 1),
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


def run(g):
  for key, value in g.items():
    globals()[key] = value
  face4_thing()
  
  
  