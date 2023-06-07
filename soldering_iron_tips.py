import math

from pyocct_system import *
initialize_system (globals())

receiver_length = 26
receiver_socket_depth = 24.5
receiver_inner_diameter = 4.5
receiver_outer_diameter = 6
head_maximum_diameter = 5 #5.5

receiver_cylinder = Face(Circle(Axes(Origin, Down), receiver_outer_diameter/2)).extrude(Down*receiver_length)
receiver_socket_cut = Face(Circle(Axes(Origin, Down), receiver_inner_diameter/2)).extrude(Down*(receiver_length - receiver_socket_depth), Down*receiver_length)
receiver = receiver_cylinder.cut(receiver_socket_cut)

phillips_base = 1

base = Face(Circle(Axes(Origin, Up), head_maximum_diameter/2)).extrude(Up*phillips_base)
pa = 3/2
pb = 2/2
pc = 1.15
pd = 1.6
pw = 0.635
p = Face(Wire([
  Origin,
  Point(pa, 0, 0),
  Point(pb, 0, pc),
  Point(pw/2, 0, pd),
  Point(0, 0, pd),
], loop = True)).extrude (Front*pw, centered = True) @ Translate(Up* phillips_base)

phillips_head_head = Compound(
  receiver,
  base,
  [p @ Rotate(Up, degrees = i*90) for i in range(4)]
)

save("phillips_head_head", phillips_head_head)
save_STL("phillips_head_head", phillips_head_head)
preview(phillips_head_head)