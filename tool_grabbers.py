import math

from pyocct_system import *
initialize_pyocct_system()


spring_diameter_with_leeway = 5
spring_radius_with_leeway = spring_diameter_with_leeway / 2
pivot_to_springonarm = 7
spring_backset = 1
pivot_to_springonbase = 12
usable_grip_length = 40
grip_curve_depth = 5
target_tool_diameter = 10
slide_leeway_between = 0.2

min_wall_thickness = 1
trigger_thickness = spring_diameter_with_leeway + min_wall_thickness*2
grippads_on_base_thickness = spring_diameter_with_leeway + min_wall_thickness + 1

peg_radius = 0.5
min_peg_holder_radius = 3

pivot = Origin
# spring_on_arm = pivot + Vector(-spring_backset, 0, pivot_to_springonarm)
spring_on_base = pivot + Vector(-spring_backset, 0, -pivot_to_springonbase)
base_bottom_z = spring_on_base[2] - max(min_peg_holder_radius, spring_radius_with_leeway)
grippads_on_base_top_z = base_bottom_z + grippads_on_base_thickness
trigger_pivot = pivot + Vector(pivot_to_springonbase, 0, 4)
far_right_of_base = pivot[0] + (pivot_to_springonarm + max(min_peg_holder_radius, spring_radius_with_leeway) + usable_grip_length)
spring_on_trigger = Point(far_right_of_base - min_peg_holder_radius, 0, spring_on_base[2])

inner_width = trigger_thickness
full_width = 25
mid_width = inner_width+3*2
full_width = mid_width+3*2
#
# curved_grip_points = [
#     Vector(-50, 0, 0),
#     Vector(-35, 0, 5),
#     Vector(-25, 0, 5),
#     Vector(-15, 0, 5),
#     Vector(0, 0, 0),
# ]

@run_if_changed
def pegs():
    def peg(p, foldback_dir, f = full_width):
        main = Face(Circle(Axes(p, Front), peg_radius)).extrude(Front*f, centered=True)
        foldbacks = [Vertex(p + Back*y).extrude(Back*(peg_radius*4), centered=True).extrude(foldback_dir*5).extrude(foldback_dir.cross(Back)*(peg_radius*2), centered=True) for y in [-f/2, f/2]]
        return Compound(main, foldbacks)
    return [
        peg(spring_on_trigger, Left),
        peg(spring_on_base, Right),
        peg(pivot, Down), #.cut(peg(pivot, inner_width)),
        peg(trigger_pivot, Left, mid_width)
    ]

@run_if_changed
def tool_grabber_arm():
    grip_ref = Point(pivot[0] - (pivot[2] - grippads_on_base_top_z) + target_tool_diameter, 0, trigger_pivot[2] + max(min_peg_holder_radius, spring_radius_with_leeway))
    curve_points = [grip_ref + v for v in [
        Vector(grip_curve_depth,0,0),
        Vector(0,0,usable_grip_length*0.3),
        Vector(0,0,usable_grip_length*0.5),
        Vector(0,0,usable_grip_length*0.7),
        Vector(grip_curve_depth,0,usable_grip_length),
    ]]
    build_plane = Plane(spring_on_base + Left * min_peg_holder_radius, Right)
    arm = Face(Wire([
        BSplineCurve(curve_points),
        curve_points[-1].projected(build_plane),
        (pivot + Down*min_peg_holder_radius).projected(build_plane),
        pivot + Vector(min_peg_holder_radius, 0, -min_peg_holder_radius),
        trigger_pivot + Vector(min_peg_holder_radius, 0, -min_peg_holder_radius),
        trigger_pivot + Vector(min_peg_holder_radius, 0, min_peg_holder_radius),
    ], loop=True)).extrude(Front*mid_width, centered=True)

    arm = Fillet(arm, [(e, 2) for e in arm.edges() if all_equal((e[0],e[2]) for e in e.vertices()) and e.bounds().min()[0] > pivot[0]])
    arm = arm.cut (Vertex(trigger_pivot).extrude(Up*20, centered=True).extrude(Left*5, Right*100).extrude(Back*(inner_width+2*slide_leeway_between), centered=True))
    arm = arm.cut (pegs)
    save_STL("tool_grabber_arm", arm)
    return arm


@run_if_changed
def tool_grabber_trigger():
    trigger_right = Direction(trigger_pivot, spring_on_trigger)
    trigger_up = trigger_right @ Rotate(Front, Degrees(90))
    trigger_length = trigger_pivot.distance(spring_on_trigger)
    trigger_bottom = Vertex(trigger_pivot).extrude(trigger_right*-min_peg_holder_radius, trigger_right*(trigger_length + min_peg_holder_radius))@Translate(trigger_up*-spring_radius_with_leeway)

    trigger = (
        trigger_bottom.extrude(Back*trigger_thickness, centered=True).extrude(trigger_up*(spring_diameter_with_leeway+min_wall_thickness))
    )

    trigger = Chamfer(trigger, [(e, 2.5) for e in trigger.edges() if all_equal((e[0],e[2]) for e in e.vertices())])

    trigger = trigger.cut(pegs + [
        trigger_bottom.extrude(Back*spring_diameter_with_leeway, centered=True).extrude(trigger_up*spring_diameter_with_leeway),
        # HalfSpace(Point(0,0,base_bottom_z), Down)
    ])

    save_STL("tool_grabber_trigger", trigger)
    return trigger

@run_if_changed
def tool_grabber_base():
    a = Point(spring_on_base[0] - min_peg_holder_radius, 0, base_bottom_z)
    grippads = Vertex(a).extrude(Up*grippads_on_base_thickness).extrude(Right*(far_right_of_base - a[0])).extrude(Back*full_width, centered=True)

    grippads = grippads.cut (Vertex(spring_on_base).extrude(Up*100, centered=True).extrude(Left*6, Right*100).extrude(Back*(inner_width+2*slide_leeway_between), centered=True))

    pivot_struts = Face(Wire([
        spring_on_base,
        pivot,
        spring_on_base + Right*pivot_to_springonbase
    ],loop=True)).offset2d(min_peg_holder_radius, fill=True).extrude(Back*full_width, centered=True)

    stop = Edge(a, Point(a[0], 0, pivot[2] - min_peg_holder_radius - slide_leeway_between)).extrude(Right*min_wall_thickness).extrude(Back*full_width, centered=True)

    pivot_struts = pivot_struts.cut (Vertex(spring_on_base).extrude(Up*100, centered=True).extrude(Left*100, centered=True).extrude(Back*(mid_width+2*slide_leeway_between), centered=True))
    base = Compound(grippads, pivot_struts, stop).cut(pegs)
    save_STL("tool_grabber_base", base)
    return base

# export("tool_grabber_arm.stl", "tool_grabber_arm_1.stl")
# export("tool_grabber_trigger.stl", "tool_grabber_trigger_1.stl")
# export("tool_grabber_base.stl", "tool_grabber_base_1.stl")

preview(
    tool_grabber_arm,
    tool_grabber_base,
    tool_grabber_trigger,
    # pegs,
    (tool_grabber_arm @ Rotate(Axis(pivot, Front), Degrees(-90))).wires()
        # [s @ Translate(Back * 50) for s in [tool_grabber_arm @ Rotate(Axis(pivot, Front), Degrees(-90)), tool_grabber_base, tool_grabber_trigger] + pegs]
        )