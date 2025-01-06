import math
from gcode_stuff.gcode_utils import *
from pyocct_system import *
initialize_pyocct_system()
from face_depthmap_loader import depthmap_sample, depthmap_samples_smoothed
from single_wall_layer_optimizer import SingleWallLayers
from pyocct_utils import wallify

@run_if_changed
def smoothed_face_surface():
  points = [
    [cell for cell in row if cell is not None] for row in depthmap_samples_smoothed(1.5)]
  maxl = max(len(row) for row in points)
  points = [row for row in points if len(row) >= maxl/2]
  minl = min(len(row) for row in points)
  def interpolated(row, idx):
    f = math.floor(idx)
    frac = idx - f
    if f+1 == len(row):
      return row[-1]
    return Between(row[f], row[f+1], frac)

  return BSplineSurface([
    [interpolated(row, idx) for idx in subdivisions(0,len(row)-1,amount = minl)]
    for row in points])

def rectangle_of_surface(surface, x0, z0, x1, z1, layers, columns):
  a0 = surface.intersections(RayIsh(Point(x0,-150,z0), Back)).point()
  a1 = surface.intersections(RayIsh(Point(x1,-150,z1), Back)).point()
  u0,v0 = surface.parameter(closest=a0)
  u1,v1 = surface.parameter(closest=a1)
  return [(v, subdivisions(u0, u1, amount=columns))
          for v in subdivisions(v0, v1, amount=layers)]

@run_if_changed
def best_angle():
  angles = []
  for v, row in rectangle_of_surface(smoothed_face_surface,-40,-50,40,70,100,20):
    for u in row:
      normal = smoothed_face_surface.normal(parameter=(u,v))
      angles.append(math.atan2(normal[2],normal[1]))

  return -Between(max(angles), min(angles))


# preview(smoothed_face_surface, RayIsh(Origin, Front, 100) @ Rotate(Right, Radians(best_angle)))

@run_if_changed
def best_angle_surface():
  return smoothed_face_surface @ Rotate(Right, Radians(best_angle))
@run_if_changed
def best_angle_col_curves():
  u0,v0 = best_angle_surface.parameter(closest=Origin)
  return [
    best_angle_surface.UIso(u) for u in subdivisions (u0 - 48, u0 + 48, amount=97)
  ]

# preview(best_angle_col_curves)

@run_if_changed
def resampled_cut_surface():
  def row(z):
    plane = Plane(Origin+Up*z, Up)
    result = []
    for curve in best_angle_col_curves:
      points = curve.intersections(plane).points
      if len(points) == 1:
        result.append(points[0])
      else:
        result.append(None)
    return result

  rows = [
    row(z) for z in range(-100, 40, 1)
  ]

  for scan in [list(reversed(range(0, len(rows[0])//2))),list(range(len(rows[0])//2, len(rows[0])))]:
    for colscan in [reversed(range(0, len(best_angle_col_curves)//2)),range(len(best_angle_col_curves)//2, len(best_angle_col_curves))]:
      prev_diffs = [None]*len(scan)
      for col in colscan:
        diffs = []
        for ((i0, i1), prev_diff) in zip(pairs(scan), prev_diffs):
          p0 = rows[i0][col]
          if rows[i1][col] is None:
            rows[i1][col] = p0 + Between(diff, prev_diff, 0.8)
          diff = rows[i1][col]-p0
          diffs.append(diff)
        prev_diffs = diffs
  result = BSplineSurface(rows)
  # preview(result)
  save_STEP("resampled_cut_surface", Face(result))
  thickened_1 = Compound(wallify(rows[i:i+11], 1.3, loop=False) for i in range(0, len(rows), 10))
  preview(thickened_1, Face(result).wires())
  save_STL("face_depthmap_thick", thickened_1, linear_deflection=0.1)
  export("face_depthmap_thick.stl", "face_depthmap_thick_1.stl")
  return result

@run_if_changed
def optimized_single_wall():
  layers = SingleWallLayers(resampled_cut_surface, 400, 100)
  _,report = layers.loss(undesired_thickness=0.25, undesired_thinness=0.05, undesired_overhang=0.1, undesired_slope=1/50, do_report=True)
  print(report)

preview(resampled_cut_surface, best_angle_col_curves[::5])

def layer_points(z, zbase):
  result = []
  prev_y = None
  cutoff = 58 - max(0, (z - 8)*0.4)
  def do_cutoff_midpoint(good, xg, bad, xb):
    frac = (good - cutoff)/(good - bad)
    result.append(Point(Between(xg, xb, frac),cutoff,z - zbase))
  for x in range(-100,101):
    y = depthmap_sample_interpolated(x, z)
    if y is not None:
      if y <= cutoff:
        if prev_y is not None and prev_y > cutoff:
          do_cutoff_midpoint(y, x, prev_y, x-1)
        result.append(Point(x,y,z - zbase))
      elif prev_y is not None and prev_y <= cutoff:
        do_cutoff_midpoint(prev_y, x-1, y, x)
    prev_y = y
  return result
def points(layer_height):
  zbase = -35
  z = zbase
  result = []
  while z < 70:
    l = layer_points(z, zbase - layer_height)
    z += layer_height
    if len(result) % 2 == 0:
      result.append(l)
    else:
      result.append(l[::-1])
  return result

def gcode(line_width, layer_height):
  layers = points(layer_height)
  commands = [
    'G92 E0    ; Set extruder reference point',
    'M106 S255 ; Fan 100%',
  ]
  extrusion = 0
  for layer in layers:
    if len(layer) == 0:
      continue
    commands.append(fastmove(*layer[0]))
    prev = layer[0]
    for p in layer[1:]:
      extrusion += (p - prev).length() * layer_height * line_width
      commands.append(g1(*p,extrusion))
      prev = p

  return wrap_gcode("\n".join(commands))

export_string(gcode(0.5, 0.3), "face_depthmap_singlewall.gcode")
print("done!")


