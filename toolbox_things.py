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

# save_STL("big_ruler_holder", big_ruler_holder)
# export("big_ruler_holder.stl", "big_ruler_holder_1.stl")
# preview(big_ruler_holder)

@run_if_changed
def wheeled_ruler_holder():
    assumed_ruler_thickness = 1.4
    wheel_radius = 4
    axle_hole_radius = 0.5
    axle_holder_radius = wheel_radius-1
    floor_thickness = 2
    wheel_heights = [floor_thickness+wheel_radius+1,floor_thickness+wheel_radius*3+2]
    support_height = max(wheel_heights)+axle_holder_radius
    support_thickness = 10
    num_wheels_wide = 4

    support_width = (num_wheels_wide - 1) * (assumed_ruler_thickness + wheel_radius*2) + axle_holder_radius*2

    pillar = Vertex(Origin).extrude(Back*(axle_holder_radius*2)).extrude(Up*support_thickness).extrude(Right*support_height)

    # block = Vertex(Origin).extrude(Back*support_width).extrude(Up*support_thickness).extrude(Right*support_height)
    floor = Vertex(Origin).extrude(Back*support_width).extrude(Up*support_thickness).extrude(Right*floor_thickness)
    pillar = Fillet(pillar, [(e, axle_holder_radius*0.99) for e in pillar.edges() if e.bounds().min()[0] > 2 and all_equal((v[0],v[1]) for v in e.vertices())])
    # preview(pillar, [Face(Circle(Axes(Point(h, 0, 0), Up), axle_hole_radius)).extrude(Up*2) for h in wheel_heights])
    pillar = pillar.cut([Face(Circle(Axes(Point(h, axle_holder_radius, 0), Up), axle_hole_radius)).extrude(Up*3) for h in wheel_heights])

    profile = Edge(BSplineCurve([
        Point(support_height, 0, 0),
        Point(support_height, 0, 4),
        Point(support_height/2, 0, 4),
        Point(2, 0, 5),
        Point(2, 0, support_thickness),
        Point(1, 0, support_thickness),
        Point(0, 0, support_thickness),
    ])).extrude(Left*50).extrude(Back*100, centered=True)
    
    wheel = Face(Circle(Axes(Origin, Up), wheel_radius)).cut(Face(Circle(Axes(Origin, Up), axle_hole_radius))).extrude(Up*5)

    wheel = Chamfer(wheel, [(e, 1) for e in wheel.edges()])

    pillar = Intersection(pillar, profile)
    floor = Intersection(floor, profile)
    result = Compound(floor,
                      [pillar @ Translate(Back*i*(wheel_radius*2 + assumed_ruler_thickness)) for i in range(num_wheels_wide)])
    # save_STL("wheeled_ruler_holder_bracket", result)
    # export("wheeled_ruler_holder_bracket.stl", "wheeled_ruler_holder_bracket_1.stl")
    # save_STL("wheeled_ruler_holder_wheel", wheel)
    # export("wheeled_ruler_holder_wheel.stl", "wheeled_ruler_holder_wheel_1.stl")
    preview(result, wheel)