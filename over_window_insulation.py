import math

from pyocct_system import *
initialize_system (globals())

inch = 25.4
openable_leeway = inch/4
non_openable_overlay = inch*3/4
existing_piece_height = inch*7/4

class Window:
  def __init__(self, name, bottom_width, left_height, right_height, top_width = None, left_insulation = 0, right_insulation = 0, openable = False):
    self.name = name
    self.bottom_width = bottom_width
    top_width = top_width or bottom_width
    self.top_width = top_width
    self.left_height = left_height
    self.right_height = right_height
    self.left_insulation = left_insulation
    self.right_insulation = right_insulation
    
    bottom_extension = -openable_leeway if openable else non_openable_overlay
    
    self.wood_corners = [
      Point(0, -bottom_extension),
      Point(0, left_height),
      Point(top_width, right_height),
      Point(bottom_width, -bottom_extension),
    ]
    
    self.wood_shape = Wire(self.wood_corners, loop = True)
    
    d = self.wood_corners[2] - self.wood_corners[1]
    self.slope = slope = d[1]/d[0]
    il = -left_insulation
    ir = bottom_width + right_insulation
    
    self.insulation_shape = Wire([
      Point(il, 0),
      Point(il, left_height - existing_piece_height - slope *left_insulation),
      Point(ir, right_height - existing_piece_height + slope*right_insulation),
      Point(ir, 0),
    ], loop = True)
    
    
    
windows = [
  #library left
  Window("L1", 525+115, 63, 84, left_insulation = 20, right_insulation = 10),
  Window("L2", 554+115, 85, 112, left_insulation = 10),
  
  #library right
  Window("L3", 285+115, 44, 58, right_insulation = 10),
  Window("L4", 701+115, 60, 90, openable = True),
  Window("L5", 290+115, 92, 108, top_width = 287+115),
  
  #woodstove room
  Window("W1", 407, 46, 63, right_insulation = 10),
  Window("W2", 816, 67, 107, openable = True),
  Window("W3", 405, 108, 126, left_insulation = 10),
  
  #dining room
  Window("D1", 649, 89, 119, top_width = 642, left_insulation = 49),
  
  Window("D2", 410, 120, 105, right_insulation = 10),
  Window("D3", 816, 104, 73, openable = True),
  Window("D4", 392, 74, 60, top_width = 382, left_insulation = 10),
]

print (list (abs(window.slope) for window in windows))
print (sorted (abs(window.slope) for window in windows))

windows.sort(key = lambda w: w.bottom_width)
print([w.name for w in windows])
result = []
offset = vector()
for window in windows:
  result.append (window.wood_shape@Translate(offset - (window.wood_shape.vertices()[0].point() - Origin)))
  offset = offset + vector(2,2)

offset = offset + vector(0,150)

for window in windows:
  result.append (window.insulation_shape@Translate(offset - (window.insulation_shape.vertices()[0].point() - Origin)))
  offset = offset + vector(2,2)


save_inkscape_svg("result", result)
preview (result)

