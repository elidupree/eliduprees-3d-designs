import math

from pyocct_system import *
from pyocct_utils import inch
initialize_pyocct_system()

def ruler_holder(*, ruler_thickness, grip_depth, total_depth, total_width):
    base_thickness = 4
    thickness = 10
    leeway_ruler_thickness = ruler_thickness + grip_depth/20
    curve = BSplineCurve([
        Point(base_thickness, leeway_ruler_thickness/2),
        Point(grip_depth, leeway_ruler_thickness/2),
        Point(Between(grip_depth, total_depth), leeway_ruler_thickness/2),
        Point(total_depth, total_width/2 - 2),
        Point(total_depth, total_width/2),
        Point(total_depth - 2, total_width/2),
    ])

    block = Face(Wire([
        Point(0, -total_width/2),
        Point(total_depth - 2, -total_width/2),
        curve.reversed() @ Mirror(Back),
        Point(base_thickness, leeway_ruler_thickness/2),
        curve,
        Point(0, total_width/2),
    ], loop=True)).extrude(Up*thickness)

    profile = Edge(BSplineCurve([
        Point(total_depth, 0, 0),
        Point(total_depth, 0, 2),
        Point(total_depth/2, 0, 4),
        Point(2, 0, 5),
        Point(2, 0, thickness),
        Point(1, 0, thickness),
        Point(0, 0, thickness),
        ])).extrude(Left*50).extrude(Back*50, centered=True)
    
    return Intersection(block, profile)

@run_if_changed
def big_ruler_holder():
    return ruler_holder(
        ruler_thickness = 1.2,
        grip_depth = 8,
        total_depth = 20,
        total_width = inch,
    )

save_STL("big_ruler_holder", big_ruler_holder)
export("big_ruler_holder.stl", "big_ruler_holder_1.stl")
preview(big_ruler_holder)