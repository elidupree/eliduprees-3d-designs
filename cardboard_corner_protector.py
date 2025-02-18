import math

from pyocct_system import *
initialize_pyocct_system()

cardboard_thickness = 4
wall_thickness = 0.5

protector_length = 40
protector_depth = 10


@run_if_changed
def cardboard_corner_protector():
    block = Vertex(Origin)\
        .extrude(Right*protector_length)\
        .extrude(Back*(cardboard_thickness+2*wall_thickness), centered = True)\
        .extrude(Up*protector_depth)
    cut = Vertex(Origin) \
        .extrude(Right*wall_thickness, Right*protector_length) \
        .extrude(Back*cardboard_thickness, centered = True) \
        .extrude(Up*0.6, Up*protector_depth)

    return block.cut(cut).cut(HalfSpace(Point(protector_length, 0, protector_depth/2), Direction(1,0,1)))

save_STL("cardboard_corner_protector", cardboard_corner_protector)
export("cardboard_corner_protector.stl", "cardboard_corner_protector_1.stl")
preview(cardboard_corner_protector)