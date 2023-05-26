import math

from pyocct_system import *
initialize_system (globals())

inch = 25.4
overlay = inch/2
existing_piece_height = inch*7/4

class Window:
  def __init__(self, bottom_width, left_height, right_height, top_width = None, left_insulation = 0, right_insulation = 0, exact_sized = False):
    self.bottom_width = bottom_width
    top_width = top_width or bottom_width
    self.top_width = top_width
    self.left_height = left_height
    self.right_height = right_height
    self.left_insulation = left_insulation
    self.right_insulation = right_insulation
    
    bottom_extension = 0 if exact_sized else overlay
    
    self.wood_corners = [
      Point(0, -bottom_extension),
      Point(0, left_height),
      Point(top_width, right_height),
      Point(bottom_width, -bottom_extension),
    ]
    
    self.wood_shape = Wire(self.wood_corners, loop = True)
    
    d = self.wood_corners[2] - self.wood_corners[1]
    slope = d[1]/d[0]
    il = -left_insulation
    ir = bottom_width + right_insulation
    
    self.insulation_shape = Wire([
      Point(il, 0),
      Point(il, left_height - existing_piece_height - slope *left_insulation),
      Point(ir, left_height - existing_piece_height + slope*right_insulation),
      Point(ir, 0),
    ], loop = True)
    
    
    
windows = [
  Window(525+115, 63, 84, left_insulation = 20, right_insulation = 10),
  Window(554+115, 85, 112, left_insulation = 10),
  Window(285+115, 44, 58, right_insulation = 10),
  Window(701+115, 60, 90, exact_sized = True),
  Window(290+115, 92, 108, top_width = 287+115),
  
  Window(407, 46, 63, right_insulation = 10),
  Window(816, 67, 107, exact_sized = True),
  Window(405, 108, 126, left_insulation = 10),
  
  Window(651, 89, 119, top_width = 638, left_insulation = 49),
  Window(410, 120, 105, right_insulation = 10),
  Window(816, 104, 73, exact_sized = True),
  Window(392, 74, 60, top_width = 387, left_insulation = 10),
]

result = Compound([
  w
  for i,window in enumerate (windows)
  for w in [window.wood_shape@Translate(Front*i*200), window.insulation_shape@Translate(Front*i*200)]
])

preview (result)

