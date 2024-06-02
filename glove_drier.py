import math

from pyocct_system import *

initialize_pyocct_system()

fan_size = 40
tube_od = 8
wall_thickness = 0.9
num_tubes = 10


def fan_hoops(offset):
    return [Vertex(0,0,z).extrude(Left*(fan_size+offset*2), centered=True).extrude(Back*(fan_size+offset*2), centered=True).outer_wire() for z in subdivisions (0, 10, amount = 6)]

def funnel_shape(start, dir, offset):
    tube_hoops = [Wire(Circle(Axes(start+dir*dist, dir), tube_od/2+offset+flare)) for dist, flare in [(-6,1), (-3,-0.5), (0,-0.5), (3,0), (6,0), (9,0), (12,0), (15,1)]]
    return Loft(fan_hoops(offset) + tube_hoops, solid=True, ruled=True)

@run_if_changed
def glove_drier():
    directions = [Right @ Rotate(Up, Turns(t+0.01)) for t in subdivisions(0, 1, amount=num_tubes+1)[:-1]]
    tube_stuff = [(Origin + dir*17 + Up*40, Direction(Up*1 + dir*0.1)) for dir in directions]
    funnels_inner = [funnel_shape(start, dir, 0) for start, dir in tube_stuff]
    funnels_outer = [funnel_shape(start, dir, wall_thickness) for start, dir in tube_stuff]

    # shadows = [Vertex(Origin).extrude (dir*100 @ Rotate(Up, Turns(1/(2*num_tubes)))).extrude (dir*100 @ Rotate(Up, Turns(-1/(2*num_tubes)))).extrude (Up*100) for dir in directions]
    # funnels_inner = [f.intersection(s) for f,s in zip(funnels_inner, shadows)]
    # funnels_outer = [f.intersection(s) for f,s in zip(funnels_outer, shadows)]
    # funnels = [o.cut(i) for o,i in zip(funnels_outer, funnels_inner)]
    # result = Compound(funnels)

    pair_shadows = [Vertex(Origin).extrude (dir*100 @ Rotate(Up, Turns(1/num_tubes))).extrude (dir*100).extrude (Up*100) for dir in directions]
    funnel_pairs = [Compound(o).intersection(s).cut(Compound(i).intersection(s)) for o,i,s in zip(pairs(funnels_outer, loop = True), pairs(funnels_inner, loop = True), pair_shadows)]
    result = Compound(funnel_pairs)

    # result = [funnel_pairs[0] @ Rotate(Up, Turns(t)) for t in subdivisions(0, 1, amount=num_tubes+1)[:-1]]
    # result = Compound(funnels_inner)
    # result = Compound(funnels_outer).cut(Compound(funnels_inner))
    preview(result)
    return result

@run_if_changed
def save():
    save_STL("glove_drier", glove_drier)
    export("glove_drier.stl", "glove_drier_2.stl")