import math
import re
from collections import deque

from pyocct_system import *
initialize_pyocct_system()


def SVG_path (text):
  things = deque(re.split("[,\s]", text))
  
  edges = []

  current_handler = None
  current_position = Origin
  first_position = None
  
  def next_number():
    return float(things.popleft())
    
  def next_absolute():
    return Point(next_number(), next_number(), 0)
  def next_relative():
    return current_position + Vector(next_number(), next_number(), 0)
    
  def M():
    nonlocal current_position
    nonlocal first_position
    a,current_position = current_position,next_point()
    if first_position is None:
      first_position = current_position
    else:
      edges.append (Edge (a,current_position))
      
  
  def H():
    nonlocal current_position
    if next_point is next_absolute:
      new = next_number()
    else:
      new = current_position[0] + next_number()
    
    a, current_position = current_position, Point(new, current_position [1], 0)
    edges.append(Edge (a,current_position))
 
  def L():
    nonlocal current_position
    a,b = current_position, next_point()
    edges.append (Edge (a,b))
    current_position = b
  
  def C():
    nonlocal current_position
    a,b,c,d = current_position, next_point(), next_point(), next_point()
    edges.append (Edge (BezierCurve([a,b,c,d])))
    current_position = d
  
  def Z():
    nonlocal current_position
    a,current_position = current_position,first_position
    edges.append(Edge (a,current_position))
  
  handlers = {
    "m": M,
    "h": H,
    "l": L,
    "c": C,
    "z": Z,
  }
  
  while things:
    if things[0].lower() in handlers:
      h = things.popleft()
      if h.isupper():
        next_point = next_absolute
      else:
        next_point = next_relative
      current_handler = handlers[h.lower()]
    else:
      current_handler()

  return Wire (edges)

hat = SVG_path("m -3.07,222.29575 -0.582,-0.778 0.652,-1.285 h 6 l 0.6517471,1.285 -0.582083,0.778")
outline = SVG_path("M 7.3394701,223.81775 C 5.293359,223.80015 2.9114703,221.73169 7.3502959e-4,221.73169 -2.9100002,221.73169 -5.291889,223.80015 -7.338,223.81775 c 3.6242155,0 5.2408537,2.11199 7.33873502959,2.11199 2.09788137041,0 3.71451947041,-2.11199 7.33873507041,-2.11199 z")
eyelid = SVG_path("M 7.3394701,223.81775 C 4.499609,223.85305 2.1705839,222.68419 7.3502959e-4,222.68419 -2.1691139,222.68419 -4.498139,223.85305 -7.338,223.81775")
iris = SVG_path("m -0.00293094,222.68433 c -0.353339,0 -0.713731,0.0355 -1.08093396,0.0909 -0.2097611,0.25285 -0.3245983,0.57104 -0.324665,0.89958 2.713e-4,0.77822 0.63123621,1.40894 1.40945696252,1.40891 0.77822195748,3e-5 1.40918873748,-0.63069 1.40946003748,-1.40891 -5.52e-4,-0.33694 -0.1217945,-0.66253 -0.341754,-0.91777 -0.36439404,-0.0445 -0.72270604,-0.0728 -1.07156404,-0.0728 z")

triangles = [
  SVG_path("m -6.0457291,225.04465 c 0.048256,0.97135 0.6032706,1.43662 0.7442809,2.22419 0.8009458,-0.42169 1.724121,-0.29485 2.479226,-1.01868 -0.2526707,-0.1231 -0.501733,-0.24828 -0.750204,-0.36546 -0.7572078,-0.3571 -1.5281983,-0.67911 -2.4733029,-0.84005 z"),
  SVG_path("m 1.9863962,226.62719 c -0.5902153,1.12773 -1.29522663,1.3283 -1.98566115,2.20941 -0.69043454,-0.88111 -1.39544595,-1.08168 -1.98566125,-2.20941 0.6002255,0.24122 1.2448459,0.41947 1.98566125,0.41947 0.74081535,0 1.38543565,-0.17825 1.98566115,-0.41947 z"),
  SVG_path("m 6.0471991,225.04465 c -0.048256,0.97135 -0.6032706,1.43662 -0.7442809,2.22419 -0.8009458,-0.42169 -1.7241209,-0.29485 -2.479226,-1.01868 0.2526708,-0.1231 0.501733,-0.24828 0.750204,-0.36546 0.7572078,-0.3571 1.5281983,-0.67911 2.4733029,-0.84005 z"),
]

all_edges = recursive_flatten ([hat, outline, eyelid, iris, triangles])


slab = Vertex (0,224, 0).extrude (Back*12, centered = True).extrude (Right*18, centered = True).extrude (Down*1) @ Translate(Down*0.01)

puncture = Face(Wire (
  Origin + Up*0.001,
  Origin + Down*0.25 + Down*0.001,
  Origin + Right*0.25 + Right*0.001,
loop = True)).revolve (Up)

puncture_positions = []
punctures = []
def add_puncture(p):
  if all(p.distance(q) > 0.2 for q in puncture_positions):
    puncture_positions.append (p)
    punctures.append (puncture@Translate (p - Origin))

grooves = []
for wire in all_edges:
  for edge in wire.edges():
    #preview(Loft([Wire(edge), Wire(edge).offset2D(0.01)]))
    c,a,b = edge.curve()
    l = c.length(a, b)
    print(l)
    rows = [[],[],[]]
    for d in subdivisions(a, b, amount = round(l / 0.2)):
      d = c.derivatives(d)
      n = d.tangent @ Rotate(Up, degrees =90)
      rows[0].append(d.position + Down*0.25)
      rows[1].append(d.position + n * 0.25 + Up*0.0005)
      rows[2].append(d.position - n * 0.25 + Up*0.0005)
      
      #punctures.append (puncture@Translate (c.value(d) - Origin))
    caps = [Face(Wire([r[i] for r in rows], loop = True)) for i in [0, -1]]
    sides = [Face (BSplineSurface(pair, BSplineDimension(degree = 1))) for pair in pairs(rows, loop=True)]
    #preview(caps, sides)
    add_puncture(c.value(a))
    add_puncture(c.value(b))
    grooves.append (Solid (Shell(caps + sides).complemented()))

for groove in grooves:
  print("B")
  #preview(slab, puncture)
  slab = slab.cut(groove)
for puncture in punctures:
  print("A")
  #preview(slab, puncture)
  slab = slab.cut(puncture)
preview (all_edges, slab)

#save("engraved_slab", slab)
save_STL("engraved_slab", slab)

####