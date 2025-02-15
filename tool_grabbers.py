import math

from pyocct_system import *
initialize_pyocct_system()


spring_full_diameter = 5
spring_full_radius = spring_full_diameter/2
pivot_to_springonarm = 7
spring_overset = 1
pivot_to_springonbase = 12
usable_grip_length = 40
grip_curve_depth = 5
target_tool_diameter = 10
arm_thickness = 5

pivot = Origin
spring_on_arm = pivot + Vector(-spring_overset, 0, pivot_to_springonarm)
spring_on_base = pivot + Vector(-spring_overset, 0, -pivot_to_springonbase)
trigger_pivot = pivot + Vector(pivot_to_springonbase, 0, spring_full_radius + arm_thickness/2)
far_right_of_base = pivot[0] + (pivot_to_springonarm + spring_full_radius + usable_grip_length)
trigger_slider_end = Point(far_right_of_base - arm_thickness/2, 0, spring_on_base[2])

peg_radius = 1.5

inner_width = spring_full_diameter+2
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
    def peg(p, f = full_width):
        return Face(Circle(Axes(p, Front), peg_radius)).extrude(Front*f, centered=True)
    return [peg(spring_on_arm, mid_width), peg(spring_on_base), peg(pivot).cut(peg(pivot, inner_width)), peg(trigger_pivot, mid_width)]

@run_if_changed
def tool_grabber_arm():
    grip_ref = Point(pivot[0] + pivot_to_springonbase-target_tool_diameter, 0, spring_on_arm[2] + spring_full_radius)
    curve_points = [grip_ref + v for v in [
        Vector(grip_curve_depth,0,0),
        Vector(0,0,usable_grip_length*0.3),
        Vector(0,0,usable_grip_length*0.5),
        Vector(0,0,usable_grip_length*0.7),
        Vector(grip_curve_depth,0,usable_grip_length),
    ]]
    build_plane = Plane(spring_on_arm + Left*(spring_full_radius+1), Right)
    arm = Face(Wire([
        BSplineCurve(curve_points),
        curve_points[-1].projected(build_plane),
        (pivot + Down*(arm_thickness/2)).projected(build_plane),
        pivot + Vector(arm_thickness/2, 0, -arm_thickness/2),
        trigger_pivot + Vector(arm_thickness/2, 0, -arm_thickness/2),
        trigger_pivot + Vector(arm_thickness/2, 0, arm_thickness/2),
    ], loop=True)).extrude(Front*mid_width, centered=True)

    arm = arm.cut (Vertex(spring_on_arm).extrude(Left*100, centered=True).extrude(Up*6, Down*100).extrude(Back*inner_width, centered=True))
    arm = Fillet(arm, [(e, 2) for e in arm.edges() if all_equal((e[0],e[2]) for e in e.vertices())])
    arm = arm.cut (pegs)
    return arm


@run_if_changed
def tool_grabber_trigger():
    # hack: make it disambiguate a plane
    trigger = Wire(trigger_pivot, trigger_pivot+Right*0.01, trigger_slider_end).offset2d(arm_thickness/2, fill=True).extrude(Back*inner_width, centered=True)
    return trigger

@run_if_changed
def tool_grabber_base():
    base = Vertex(spring_on_base).extrude(Up*arm_thickness, centered=True).extrude(Left*(arm_thickness/2), Right*20).extrude(Back*full_width, centered=True)

    base = base.cut (Vertex(spring_on_arm).extrude(Up*100, centered=True).extrude(Left*6, Right*100).extrude(Back*mid_width, centered=True))
    return base


preview(
    tool_grabber_arm, tool_grabber_base, pegs, tool_grabber_trigger,
    (tool_grabber_arm @ Rotate(Axis(pivot, Front), Degrees(-90))).wires()
        # [s @ Translate(Back * 50) for s in [tool_grabber_arm @ Rotate(Axis(pivot, Front), Degrees(-90)), tool_grabber_base, tool_grabber_trigger] + pegs]
        )