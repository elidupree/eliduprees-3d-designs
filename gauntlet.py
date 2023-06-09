import math
import numpy as np

from pyocct_system import *
initialize_system (globals())

plate_thickness = 1.0
lots = 100

# TODO: put "stops" to block stuff sliding along the plates from going into knuckle joint

# right hand, thumb then index finger to pinky,
widths = [
  # fingertip
  (17.75, 14.39, 14.98, 14.15, 12.04),
  # knuckle
  (20.61, 16.01, 16.33, 15.37, 14.52),
  #knuckle
  (24.43, 19.05, 18.88, 18.20, 16.33),
]

#Right hand, index finger to pinky, measured from fingertip (with small force) to hopefully representative location at side of knuckle
lengths = [
  # experimental longest reasonable underside of thimble)
  (24.32, 19.21, 19.79, 20.43, 16.43),
  
  #knuckle reference points with straight finger
  (29.91, 26.05, 26.59, 25.19, 24.36),
  (65.07, 49.58, 53.20, 51.50, 43.35),
  (114.63, 93.59, 103.03, 100, 81.80),
]

thicknesses = [
  #middle of fingernail, touch only
  (11.42, 10.87, 12.23, 11.95, 10.26),
  # middle of fingernail, compressed until nontrivial force
  (9.28, 8.92, 9.77, 9.73, 8.54),
  #knuckle nontrivial force
  (16.52, 11.70, 12.23, 11.40, 10.39),
  (23.97, 16.19, 16.43, 16.28, 13.41),
  # this last knuckle measurement might not be so useful
  (None, 25.15, 25.96, 25.23, 22.84),
]

#@run_if_changed
def show_widths_graph():
  import matplotlib.pyplot as plt
  for wrow, trow in zip(widths, thicknesses[1:-1]):
    xs = np.array([w for w in wrow])
    ys = np.array([t for t in trow])
    a,b = np.polyfit(xs, ys, 1)
    print(a, b)
    plt.scatter(xs, ys)
    plt.plot(xs, a*xs+b)
  plt.xlim([0, 30])
  plt.ylim([0, 30])
  plt.show()

#show_widths_graph()

def thimble(back_length, front_length, knuckle_width, tip_width):
  knuckle_thickness = knuckle_width - 4
  tip_thickness = 7.5 + tip_width*0.1
  top_row = [Origin + Left*knuckle_width/2, Origin, Origin + Right*knuckle_width/2,]
  w = knuckle_width
  t = knuckle_thickness
  l = back_length + 2
  
  def row(w, t, l, k, r):
    return [
      Point(-w*k, 0, l),
      Point(0, 0, l),
      Point(w*k, 0, l),
      Point(w/2, t/3, l),
      Point(w/2, t/2, l),
      Point(w/2, t*2/3, l),
      Point(w*r, t, l),
      Point(0, t, l),
      Point(-w*r, t, l),
      Point(-w/2, t*2/3, l),
      Point(-w/2, t/2, l),
      Point(-w/2, t/3, l),
    ]
  
  k = 1/3
  knuckle_row = row(knuckle_width, knuckle_thickness, back_length + 2, 1/3, 1/3)
  middle_row = row(knuckle_width, knuckle_thickness, back_length *0.3, 1/4, 1/4)
  tip_row = row(tip_width, tip_thickness, -0.001, 1/4, 1/4)

  rows = [knuckle_row, middle_row, tip_row]
  surface = BSplineSurface (rows, BSplineDimension (degree = 2), BSplineDimension (periodic = True))
  tip_outline = BSplineCurve (tip_row, BSplineDimension (periodic = True))
  knuckle_outline = BSplineCurve (knuckle_row, BSplineDimension (periodic = True))
  finger_solid = Solid (Shell (
    Face (surface),
    Face (Wire(tip_outline)),
    Face (Wire(knuckle_outline)),
  ))
  r = max(l*2/3, tip_width)
  curve_limit = Face (Circle (Axes(Origin, Front), r)).extrude (Front*lots, centered = True)@Rotate (Front, degrees = 90)@Translate(Up*r)
  finger_solid = Intersection (finger_solid, curve_limit)
  #preview ([f for f in finger_solid.faces() if f.bounds().min()[2] < l-0.01]) #(finger_solid, curve_limit.wires())
  shell = Shell ([f for f in finger_solid.faces() if f.bounds().min()[2] < l-0.01])
  #preview (shell.faces())
  #preview (shell)
  wall = shell.offset (plate_thickness, fill = True)
  exclusion = Vertex(0, 0, back_length).extrude(Left*lots, centered = True).extrude (Up*lots).extrude(vector (0,knuckle_thickness,front_length - back_length)*5, centered=True)
  wall = wall.cut(exclusion)
  #preview (wall)
  return wall
  
@run_if_changed
def do_thimbles():
  thimbles = []
  for index, size in enumerate (zip(lengths[1], lengths[0], widths[1], widths[0])):
    thimbles.append (thimble(*size)@Translate (Left*index*30))
  preview (thimbles)
  save_STL("index_finger_thimble", thimbles[1])
  
  
cloth_passage_leeway = 0.3
stitch_jig_precision = 0.8
stitch_jig_length = stitch_jig_precision
stitch_jig_width = stitch_jig_precision*3
stitch_jig_protrusion_above_plate = 2.0
stitch_window_width = stitch_jig_width + cloth_passage_leeway*2
stitch_window_length = stitch_jig_length + cloth_passage_leeway*2
stitch_wavelength = plate_thickness + stitch_window_length

FDM_compensation = 0.01 # 0.2

@run_if_changed
def make_stitch_test():
  num_stitches = 8
  total_length = stitch_window_length*num_stitches + plate_thickness*(num_stitches+1)
  plate = Vertex (Origin).extrude (Front*12, centered = True).extrude (Right*total_length).extrude (Up*plate_thickness)
  cuts = Compound([Vertex (plate_thickness + index*stitch_wavelength - FDM_compensation, 0, 0).extrude (Right*(stitch_window_length + 2*FDM_compensation)).extrude (Front*(stitch_window_width + 2*FDM_compensation), centered = True).extrude (Up*lots, centered=True) for index in range (num_stitches)])
  plate = plate.cut (cuts)
  
  
  h = plate_thickness + stitch_jig_protrusion_above_plate
  d = -cloth_passage_leeway - stitch_jig_precision
  jig_protrusion = Wire([
    Point(0, stitch_jig_width/2, d),
    Point(0, stitch_jig_width/2, h),
    Point(0, stitch_jig_width/2 - stitch_jig_precision, h),
    Point(0, stitch_jig_width/2 - stitch_jig_precision, h - stitch_jig_precision),
    Point(0, -(stitch_jig_width/2 - stitch_jig_precision), h - stitch_jig_precision),
    Point(0, -(stitch_jig_width/2 - stitch_jig_precision), h),
    Point(0, -stitch_jig_width/2, h),
    Point(0, -stitch_jig_width/2, d),
  ], loop=True)
  jig_protrusion = Face (jig_protrusion).extrude (Right*(stitch_jig_precision))
  jig_protrusion = Fillet (jig_protrusion, [(e, stitch_jig_precision*0.4) for e in jig_protrusion.edges()])
  
  jig_protrusion = jig_protrusion.offset(-FDM_compensation)
  
  jig_base = Vertex (Point(0,0,-cloth_passage_leeway)).extrude (Front*(stitch_jig_width - FDM_compensation*2), centered = True).extrude (Right*total_length).extrude (Down*stitch_jig_precision)
  
  jig = Compound(jig_base, [jig_protrusion @ Translate(Right*(plate_thickness + cloth_passage_leeway + index*stitch_wavelength)) for index in range (num_stitches)])
  
  save_STL("stitch_test_plate", plate)
  save_STL("stitch_test_jig", jig)
  preview (plate, jig)