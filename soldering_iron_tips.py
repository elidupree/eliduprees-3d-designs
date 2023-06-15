import math

from pyocct_system import *
initialize_pyocct_system()

receiver_length = 26
receiver_socket_depth = 24 #tight: 23.4ish
receiver_inner_diameter = 4 #tight: 3.6ish
receiver_outer_diameter = 6 
head_maximum_diameter = 5 #tight: 5.4ish

receiver_cylinder = Face(Circle(Axes(Origin, Down), receiver_outer_diameter/2)).extrude(Down*receiver_length)
receiver_socket_cut = Face(Circle(Axes(Origin, Down), receiver_inner_diameter/2)).extrude(Down*(receiver_length - receiver_socket_depth), Down*receiver_length)
receiver = receiver_cylinder.cut(receiver_socket_cut)

phillips_base = 1

base = Face(Circle(Axes(Origin, Up), head_maximum_diameter/2)).extrude(Up*phillips_base)
pa = 3.2/2 #3.3
pb = 2.1/2 #2.2
pc = 1.1
pd = 1.55 # 1.6
pw = 0.9 # 0.9-1.0
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

phillips_head_head = Chamfer(phillips_head_head, [
  (e, 0.6) for e in phillips_head_head.edges() if e.bounds().max()[2] < 0.1-receiver_length and e.bounds().size()[0] < receiver_outer_diameter - 0.1
])

#save("phillips_head_head", phillips_head_head)
save_STL("phillips_head_head", phillips_head_head)
preview(phillips_head_head)