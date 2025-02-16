import math

from pyocct_system import *
from pyocct_utils import stitch_unordered_edges_to_wire
initialize_pyocct_system()


spring_diameter_with_leeway = 5.7
spring_radius_with_leeway = spring_diameter_with_leeway / 2
pivot_to_springonarm = 7
spring_backset = 1
pivot_to_springonbase = 12
usable_grip_length = 40
grip_curve_depth = 5
target_tool_diameter = 5
slide_leeway_between = 0.3

min_wall_thickness = 1.4
trigger_thickness = spring_diameter_with_leeway + min_wall_thickness*2
grippads_on_base_thickness = spring_diameter_with_leeway + min_wall_thickness + 1

pivot_peg_radius = 0.8
min_peg_holder_radius = 3
spring_peg_radius = 1

pivot_to_trigger_pivot = pivot_to_springonbase - 2

pivot = Origin
# spring_on_arm = pivot + Vector(-spring_backset, 0, pivot_to_springonarm)
spring_on_base = pivot + Vector(-spring_backset, 0, -pivot_to_springonbase)
slide_surface_z = spring_on_base[2] - max(min_peg_holder_radius, spring_radius_with_leeway) - slide_leeway_between
grippads_on_base_top_z = slide_surface_z + grippads_on_base_thickness
trigger_pivot = pivot + Vector(pivot_to_trigger_pivot, 0, 0)
far_right_of_base = pivot[0] + (trigger_pivot[2] + max(min_peg_holder_radius, spring_radius_with_leeway) + usable_grip_length - pivot[2])
# the -2 is an ad hoc number to make sure it doesn't overshoot; the real math is annoying)
spring_on_trigger = Point(far_right_of_base - min_peg_holder_radius - 2, 0, spring_on_base[2])

inner_width = trigger_thickness
# full_width = 25
mid_width = inner_width+3*2
full_width = mid_width+3*2
print(inner_width, mid_width, full_width)
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
    def peg(p, insertion_dir, f = full_width):
        insertion_center = p + insertion_dir*1
        # hack - make it disambiguate a plane
        main = Wire(p,p+Up*0.001,insertion_center).offset2d(pivot_peg_radius, fill=True).extrude(Front*(f - 2*0.6), centered=True)
        # foldbacks = [Vertex(p + Back*y).extrude(Back*(pivot_peg_radius*4), centered=True).extrude(foldback_dir*5).extrude(foldback_dir.cross(Back)*(pivot_peg_radius*2), centered=True) for y in [-f/2, f/2]]
        insertion = Face(Circle(Axes(insertion_center, Front), pivot_peg_radius)).extrude(Front*(f/2))
        return Compound(main, insertion)
    return [
        # peg(spring_on_trigger, Left),
        # peg(spring_on_base, Right),
        peg(pivot, Direction(1, 0, -1)), #.cut(peg(pivot, inner_width)),
        peg(trigger_pivot, Direction(1, 0, 1), mid_width)
    ]

@run_if_changed
def tool_grabber_arm():
    grip_ref = Point(pivot[0] + (pivot[2] - grippads_on_base_top_z) - target_tool_diameter, 0, trigger_pivot[2] + max(min_peg_holder_radius, spring_radius_with_leeway))
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
        # pivot + Vector(min_peg_holder_radius, 0, -min_peg_holder_radius),
        # pivot + Vector(min_peg_holder_radius, 0, 0.4*min_peg_holder_radius),
        trigger_pivot + Vector(min_peg_holder_radius, 0, -min_peg_holder_radius),
        trigger_pivot + Vector(min_peg_holder_radius, 0, min_peg_holder_radius),
    ], loop=True)).extrude(Front*mid_width, centered=True)

    arm = Fillet(arm, [(e, min_peg_holder_radius*0.9) for e in arm.edges() if all_equal((e[0],e[2]) for e in e.vertices()) and e.bounds().min()[0] > pivot[0]])
    arm = arm.cut (Vertex(trigger_pivot).extrude(Up*20, centered=True).extrude(Left*5, Right*100).extrude(Back*(inner_width+2*slide_leeway_between), centered=True))
    sprue_edges = Compound([e for e in arm.edges() if mid_width*0.15 < e.bounds().min()[1] and e.bounds().max()[1] < mid_width*0.45]).cut(HalfSpace(trigger_pivot + Left*4, Left))
    arm = arm.cut (pegs)

    # preview(arm, stitch_unordered_edges_to_wire(sprue_edges.edges()))
    sprue = stitch_unordered_edges_to_wire(sprue_edges.edges()).offset2D(0.25, fill=True).extrude(Front*0.2, Front*(trigger_thickness+2*(slide_leeway_between-0.2))) @ Translate(Left*0.25)

    diag = Direction(-1, 0, 1)
    catch = Face(Wire([
        trigger_pivot+diag*1,
        trigger_pivot+Back*1.8+diag*1.8,
        trigger_pivot+Back*1.8+diag*1,
        trigger_pivot-diag*2],loop=True)).extrude (Vector(-1,0,-1)*3, centered = True)@Translate(Back*mid_width/2)
    # preview(arm, sprue)
    arm = Compound(arm, sprue, catch)
    # preview(arm)

    save_STL("tool_grabber_arm", arm)
    return arm


def spring_grip_prong(base, up, snag):
    return Face(Wire([
        base + snag*2,
        base + snag*2 + up*(spring_radius_with_leeway-2),
        base + up*spring_radius_with_leeway,
        base + snag*2 + up*(spring_radius_with_leeway+2),
        base - snag*2 + up*(spring_radius_with_leeway+2),
        base - snag*(spring_radius_with_leeway+2)
    ], loop=True)).extrude(Back*3, centered=True)


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

    trigger = trigger.cut([
        trigger_bottom.extrude(Back*spring_diameter_with_leeway, centered=True).extrude(trigger_up*spring_diameter_with_leeway),
        # HalfSpace(Point(0,0,slide_surface_z), Down)
    ])
    # trigger = Compound(trigger, Face(Circle(Axes(spring_on_trigger, Front), spring_peg_radius)).extrude(Front*trigger_thickness, centered=True))

    trigger = Chamfer(trigger, [(e, 0.4) for e in trigger.edges() if all_equal((e[1]) for e in e.vertices())])

    trigger = Compound(trigger, spring_grip_prong(spring_on_trigger + trigger_up*spring_radius_with_leeway - trigger_right*1, -trigger_up, trigger_right))

    trigger = trigger.cut(pegs)
    # preview(trigger)

    save_STL("tool_grabber_trigger", trigger)
    return trigger

@run_if_changed
def tool_grabber_base():
    a = Point(spring_on_base[0] - min_peg_holder_radius, 0, slide_surface_z)
    grippads = Vertex(a).extrude(Up*grippads_on_base_thickness).extrude(Right*(far_right_of_base - a[0])).extrude(Back*full_width, centered=True)

    cut_for_trigger = Vertex(spring_on_base).extrude(Up*100, centered=True).extrude(Left*2, Right*100).extrude(Back*(trigger_thickness+2*slide_leeway_between), centered=True)
    # grippads = grippads.cut (cut_for_trigger)

    pivot_struts = Face(Wire([
        spring_on_base,
        pivot,
        spring_on_base + Right*pivot_to_springonbase
    ],loop=True)).offset2d(min_peg_holder_radius, fill=True).extrude(Back*full_width, centered=True)

    # stop = Edge(a, Point(a[0], 0, pivot[2] - min_peg_holder_radius)).extrude(Right*3).extrude(Back*full_width, centered=True)

    # pivot_struts = pivot_struts.cut (cut_for_trigger)

    pivot_struts = pivot_struts.cut (Vertex(pivot + Down*min_peg_holder_radius).extrude(Left*100, centered=True).extrude(Back*(mid_width+2*slide_leeway_between), centered=True).extrude(Up*100))

    base = Compound(grippads, pivot_struts,
                    # stop
                    )

    base = base.cut(
        [
            pegs,
            cut_for_trigger,
            # Intersection(
                Face(Circle(Axes(pivot, Front), pivot.distance(trigger_pivot) + min_peg_holder_radius + 1)).extrude(Back*(mid_width+2*slide_leeway_between), centered=True),
            #     HalfSpace(pivot, Right)
            # )
        ])
    # base = Compound(grippads, pivot_struts,
    #                 # stop
    #                 ).cut(pegs)
    slide_surface_thickness = 0.6
    prong = spring_grip_prong(a + Right*11, Up, Left)
    slide_surface = Vertex(a).extrude(Down*slide_surface_thickness).extrude(Right*(far_right_of_base - a[0])).extrude(Back*full_width, centered=True)
    # preview (prong, slide_surface, [Compound((tool_grabber_arm @ Rotate(Axis(pivot, Front), Degrees(-x))).wires()) for x in [0, 45, 60, 70, 90]])
    k = trigger_pivot[2]+min_peg_holder_radius+5 - slide_surface_z
    catch = (Face(Wire([
        Point(0, 0, slide_surface_z),
        Point(0, 1.2, slide_surface_z),
        Point(0, 1.2, trigger_pivot[2]+min_peg_holder_radius+1.5),
        Point(0, 2.8, trigger_pivot[2]+min_peg_holder_radius+0.6),
        Point(0, 2.8, trigger_pivot[2]+min_peg_holder_radius+1.2),
        Point(0, 1.2, trigger_pivot[2]+min_peg_holder_radius+5),
        Point(0, 0, trigger_pivot[2]+min_peg_holder_radius+5),
    ], loop=True)) @ Translate(trigger_pivot[0] + 2, -full_width/2, 0)).extrude(Vector(-k, 0, -k)).cut(HalfSpace(Point(0, 0, slide_surface_z), Down)).cut(HalfSpace(Point(0, 0, trigger_pivot[2]+min_peg_holder_radius), Up)).cut(HalfSpace(Point(trigger_pivot[0]-min_peg_holder_radius-5, 0, 0), Left))

    base = Compound(base,
                    prong,
                    # catch,
                    catch @ Mirror(Back),
           slide_surface)
    save_STL("tool_grabber_base", base)
    return base

# export("tool_grabber_arm.stl", "tool_grabber_arm_3.stl")
# export("tool_grabber_trigger.stl", "tool_grabber_trigger_3.stl")
# export("tool_grabber_base.stl", "tool_grabber_base_3.stl")

preview(
    tool_grabber_arm,
    tool_grabber_base,
    tool_grabber_trigger,
    # pegs,
    [Compound((tool_grabber_arm @ Rotate(Axis(pivot, Front), Degrees(-x))).wires()) for x in [45, 90]]
        # [s @ Translate(Back * 50) for s in [tool_grabber_arm @ Rotate(Axis(pivot, Front), Degrees(-90)), tool_grabber_base, tool_grabber_trigger] + pegs]
        )