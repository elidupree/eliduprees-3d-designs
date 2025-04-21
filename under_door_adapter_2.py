import math
import token

from pyocct_system import *
from pyocct_utils import two_BSplineSurfaces_to_solid, inch, turn_subdivisions
from thread_sweeping import ScrewThreadSurface, ThreadPosition

initialize_pyocct_system()

hose_od = 46
hose_without_ribs_od = 40
bearing_od = 50
bearing_id = 40
bearing_thickness = 6
hose_rib_thickness = 3.6
hose_rib_period = 6
wall_thickness=1.0

@run_if_changed
def threaded_hose_grip():
    thread_turns = 2.5
    threads_length = thread_turns*hose_rib_period
    def thread_inner_radius(turns, z):
        rib_radius = hose_rib_thickness/2
        axial_distance_from_thread_outermost_point = abs(((z + hose_rib_period*(1.5+turns)) % hose_rib_period) - hose_rib_period/2)
        arc_distance = min(rib_radius/math.sqrt(2), axial_distance_from_thread_outermost_point)
        capped_distance = axial_distance_from_thread_outermost_point-arc_distance
        d = hose_od/2-rib_radius + math.sqrt(rib_radius**2 - arc_distance**2) - capped_distance
        flare = (z/threads_length)**3 * (bearing_od-hose_od)/2
        d += flare
        assert (d >= hose_without_ribs_od/2)
        return d
    def thread_outer_radius(turns, z):
        return bearing_od/2+wall_thickness
    def thread_surface(radius_fn):
        return BSplineSurface([[Point(radius_fn(turns, z), 0, z) @ Rotate(Up, Turns(turns)) for turns in subdivisions(0,1,amount=120)[::-1]] for z in subdivisions(0, threads_length, max_length=0.5)], v=BSplineDimension(periodic=True))

    return two_BSplineSurfaces_to_solid(
        thread_surface(thread_outer_radius),
        thread_surface(thread_inner_radius),
    )
# preview(threaded_hose_grip)

@run_if_changed
def hose_to_bearing():

    result = Face(Circle(Axes(Origin, Up), bearing_od/2+wall_thickness)).extrude(Up*(bearing_thickness
                                                                                     #+hose_rib_period*thread_turns
                                                                                     ))

    result = result.cut(Face(Circle(Axes(Origin, Up), bearing_od/2)).extrude(Up*(bearing_thickness)))
    # result = result.cut(Face(Circle(Axes(Origin, Up), hose_without_ribs_od/2)).extrude(Up*100))
    # thread_hoop = Face(Circle(Axes(Point(hose_od/2 - hose_rib_thickness/2, 0, 0), Back), hose_rib_thickness/2)).extrude(Left*10)
    # thread_profile_points = [
    #     Point(hose_od/2, 0, 0),
    #     Point(hose_od/2, 0, hose_rib_thickness/4),
    #     Point(hose_od/2 - hose_rib_thickness/4, 0, hose_rib_thickness/2),
    #     Point(hose_od/2 - hose_rib_thickness/4 - (hose_rib_period-hose_rib_thickness)/2, 0, hose_rib_period/2),
    # ]
    # thread_profile = BSplineCurve([p @ Mirror(Up) for p in points[1:][::-1]] + points)
    # thread_hoop = Wire([
    #                        thread_profile @ Translate(Up*(turns*hose_rib_period))
    #                        for turns in range(thread_turns+1)
    #                    ]
    #
    #                    + [Point(bearing_od/2+wall_thickness, 0, hose_rib_period * (thread_turns + 0.5)), Point(bearing_od/2+wall_thickness, 0, -hose_rib_period*0.5)], loop=True)
    # thread_hoops = [thread_hoop @ Rotate(Up, Turns(-turns)) @ Translate(Up*(bearing_thickness + (turns-0.5)*hose_rib_period)) for turns in subdivisions(0, 1, max_length=1/120)]
    # thread = Loft(thread_hoops, solid=True, ruled=True)
    # # preview(result, thread)
    # thread = thread.cut([
    #     HalfSpace(Point(0, 0, bearing_thickness), Down),
    #     HalfSpace(Point(0, 0, bearing_thickness+hose_rib_period*thread_turns), Up),
    # ])


    # def thread(start_turns, stop_turns):
    #     thread_hoops = [thread_hoop @ Rotate(Up, Turns(turns)) @ Translate(Up*(bearing_thickness + turns*hose_rib_period)) for turns in subdivisions(start_turns, stop_turns, max_length=1/100)]
    #     return Loft(thread_hoops, solid=True, ruled=True)
    # thread1 = thread(-0.5, thread_turns/2).cut([
    #     HalfSpace(Point(0, 0, bearing_thickness), Down),
    # ])
    # # preview(thread1)
    # thread2 = thread(thread_turns/2, thread_turns+0.5).cut([
    #     HalfSpace(Point(0, 0, bearing_thickness+hose_rib_period*thread_turns), Up),
    # ])

    result = Compound(result, threaded_hose_grip @ Translate(Up*bearing_thickness))

    # save_STL("hose_to_bearing", result, linear_deflection=0.02)
    # export("hose_to_bearing.stl", "hose_to_bearing_2.stl")
    preview(result)

@run_if_changed
def hose_to_bearing_id():
    overhang = hose_od/2 - (bearing_id/2-wall_thickness)
    overhang_height = overhang*0.7
    profile=Wire([
        Point(bearing_id/2-wall_thickness, 0, 0),
        Point(bearing_id/2, 0, 0),
        Point(bearing_id/2, 0, bearing_thickness),
        Point(bearing_od/2+wall_thickness, 0, bearing_thickness),
        Point(bearing_od/2+wall_thickness, 0, bearing_thickness+overhang_height),
        Point(bearing_id/2+overhang-wall_thickness, 0, bearing_thickness+overhang_height),
        Point(bearing_id/2-wall_thickness, 0, bearing_thickness),
    ], loop=True)

    result = profile.revolve(Up)
    # preview(result)
    result = Compound(result, threaded_hose_grip @ Translate(Up*(bearing_thickness+overhang_height)))
    # save_STL("hose_to_bearing_id", result, linear_deflection=0.02)
    # export("hose_to_bearing_id.stl", "hose_to_bearing_id_1.stl")
    preview(result)


definite_space_under_door = 29 # 30 probably works, and it's what I used last time, which worked; 29 plays it nice and safe, especially since I want to hover it rather than dragging on the floor
door_thickness = 34.2
# give some leeway for shims to wedge in or whatever
door_gap_thickness = door_thickness + 2
brace_thickness = 3

hose_od_leeway_radius = bearing_od/2+wall_thickness + 0.5
hose_od_leeway_start_y = -(door_thickness/2 + brace_thickness)
hose_center_y = hose_od_leeway_start_y - hose_od_leeway_radius
hose_center = Point(0, hose_center_y, 0)
tube_front_y = hose_center_y - bearing_id/2

plate_thickness=1.2

@run_if_changed
def bottom_of_door():
    return Vertex(Origin).extrude(Right*100, centered=True).extrude(Back*door_thickness, centered=True).extrude(Up*50)

under_door_halfwidth = 30

@run_if_changed
def tube_footprint_quarter_points():
    return ([
            Point(under_door_halfwidth, 0, 0),
            Point(under_door_halfwidth, -door_thickness/2, 0),
            Point(under_door_halfwidth, -20, 0),
            Point(under_door_halfwidth, -25, 0),
        ]+
        [hose_center + Vector(0,-bearing_id/2,0) @ Rotate(Up, Turns(t)) for t in subdivisions(0.22, 0, amount=20)])

# @run_if_changed
# def tube_footprint():
#     return BSplineCurve(
#         tube_footprint_quarter_points
#         + [p @ Mirror(Right) for p in tube_footprint_quarter_points[1:-1][::-1]]
#         + [p @ Mirror(Origin) for p in tube_footprint_quarter_points]
#         + [p @ Mirror(Back) for p in tube_footprint_quarter_points[1:-1][::-1]]
#         , BSplineDimension(periodic=True))
# preview(tube_footprint)

@run_if_changed
def hose_id_pressurefit():
    return Face(Circle(Axes(hose_center, Up), bearing_id/2)).extrude(Up*(bearing_thickness)).cut(Face(Circle(Axes(hose_center, Up), bearing_id/2-wall_thickness)).extrude(Up*(bearing_thickness)))

def curved_end(inset):
    base_y = -door_gap_thickness/2-brace_thickness+wall_thickness
    return BSplineCurve([
        Point(-under_door_halfwidth+inset, base_y-inset, 0),
        Point(-under_door_halfwidth+inset, base_y-definite_space_under_door+inset, 0),
        Point(0, base_y-definite_space_under_door+inset, 0),
        Point(under_door_halfwidth-inset, base_y-definite_space_under_door+inset, 0),
        Point(under_door_halfwidth-inset, base_y-inset, 0),
    ])

def tube_footprint(inset):
    return Wire([curved_end(inset), curved_end(inset).reversed() @ Mirror(Back)], loop=True)
# preview(tube_footprint.edges())
def circle_to_squareish(inset):
    height=50
    return Loft([Wire(Circle(Axes(hose_center + Up*z, Up), bearing_id/2 - inset)) for z in subdivisions(height, height * 0.8, amount=7)] + [Wire(curved_end(inset), loop=True) @ Translate(0, -z*0.6, z) for z in subdivisions(height*0.1, 0, amount=7)], solid=True)

slot_in_leeway_one_sided = 0.3

@run_if_changed
def circle_to_squareish_outer_solid():
    return circle_to_squareish(0)

@run_if_changed
def circle_to_squareish_solid():
    return circle_to_squareish_outer_solid.cut(circle_to_squareish(wall_thickness))

@run_if_changed
def tube_top_plate():
    slot_in_outer_inset = -2*slot_in_leeway_one_sided-wall_thickness
    plate_frame = Compound(
        Face(tube_footprint(0)).cut(Face(tube_footprint(wall_thickness))).extrude(Down*brace_thickness),
        Face(tube_footprint(slot_in_outer_inset-wall_thickness)).cut(Face(tube_footprint(slot_in_outer_inset))).extrude(Down*brace_thickness),
        Face(tube_footprint(slot_in_outer_inset-wall_thickness)).cut(Face(tube_footprint(wall_thickness))).extrude(Down*plate_thickness))
    middle_plate = Vertex(Origin).extrude(Back*(door_gap_thickness+brace_thickness*2), centered=True).extrude(Left*under_door_halfwidth*2, centered=True).extrude(Down*plate_thickness)
    support_fins = [Vertex(x,0,0).extrude (Back*(door_gap_thickness+brace_thickness*2), centered=True).extrude (Left*wall_thickness, centered=True).extrude(Down*brace_thickness) for x in subdivisions(-under_door_halfwidth, under_door_halfwidth, max_length=12)[1:-1] ]

    brace = Face(Wire([
        BSplineCurve([
        Point(-under_door_halfwidth, -door_gap_thickness/2, 0),
        Point(-under_door_halfwidth, -door_gap_thickness/2 - brace_thickness, 0),
        Point(-under_door_halfwidth, -door_gap_thickness/2 - brace_thickness*3, 0),
        Point(-20, hose_center_y, 0),
        Point(20, hose_center_y, 0),
        Point(under_door_halfwidth, -door_gap_thickness/2 - brace_thickness*3, 0),
        Point(under_door_halfwidth, -door_gap_thickness/2 - brace_thickness, 0),
        Point(under_door_halfwidth, -door_gap_thickness/2, 0),])
    ], loop=True)).extrude(Up*40).cut(circle_to_squareish(wall_thickness/2))
    # preview(brace, circle_to_squareish_outer_solid.wires())
    return Compound(middle_plate, plate_frame, support_fins, circle_to_squareish_solid, circle_to_squareish_solid @ Mirror(Back), brace, brace @ Mirror(Back))

@run_if_changed
def tube_bottom_solid():
    # intended to print as-is with Cura's "spiralize outer contour"
    d = 13
    k = Point(0,d*0.6,-brace_thickness-1.5-d)
    half = Face(curved_end(-wall_thickness - slot_in_leeway_one_sided).cartesian_product(BSplineCurve([
        Point(0,0,-plate_thickness),
        Point(0,0,-brace_thickness),
        Point(0,0,-brace_thickness-0.5),
        Point(0,0,-brace_thickness-1),
        k,
        Point(0,k[1] + (definite_space_under_door + k[2]),-definite_space_under_door),
    ]))).extrude(Back*100).cut(HalfSpace(Origin,Back))
    return Compound(half, half @ Mirror(Back))


# save_STL("tube_top_plate", tube_top_plate, linear_deflection=0.2)
# export("tube_top_plate.stl", "tube_top_plate_1.stl")
# save_STL("tube_bottom_solid", tube_bottom_solid, linear_deflection=0.2)
# export("tube_bottom_solid.stl", "tube_bottom_solid_1.stl")
# preview(bottom_of_door, tube_footprint(0), tube_top_plate, tube_bottom_solid)


@run_if_changed
def through_wall_flange():
    # wires_and_stuff_leeway = 4
    # tube_id = hose_od + wires_and_stuff_leeway
    # flange_od = tube_id + 30*2
    # tube_od = tube_id + 2*2
    # flat = Face(Circle(Axes(Origin, Up), flange_od/2)).cut(Face(Circle(Axes(Origin, Up), tube_id/2))).extrude(Up*2)
    # tube = Face(Circle(Axes(Origin, Up), tube_od/2)).cut(Face(Circle(Axes(Origin, Up), tube_id/2))).extrude(Up*1.8*inch)
    # screw_hole = Face(Circle(Axes(Origin, Up), 5/2)).extrude(Up*1.8*inch)
    # screw_holes = [screw_hole @ Translate((Right*(flange_od/2 - 10)) @ Rotate(Up, Turns(t))) for t in [0, 1/3, 2/3]]
    # result = Compound(flat, tube).cut(screw_holes)

    hole_chamfer = 4
    drywall_thickness=0.5*inch

    tube_id = 53
    hole_id = inch*2.5
    length = inch*2.2

    hole_gripper_profile = Wire([
        Point(hole_id/2 + hole_chamfer, 0, 0),
        Point(hole_id/2, 0, hole_chamfer),
        BSplineCurve([
            Point(hole_id/2, 0, hole_chamfer),
            Point(hole_id/2, 0, drywall_thickness-3),
            Point(hole_id/2, 0, drywall_thickness),
            Point(hole_id/2 + 2, 0, drywall_thickness+3),
            Point(hole_id/2 + 4, 0, drywall_thickness+10),
            Point(hole_id/2 + 4, 0, drywall_thickness+20),
            Point(hole_id/2 + 2, 0, drywall_thickness+30),
            Point(hole_id/2-1, 0, drywall_thickness+37),
            Point(hole_id/2-1, 0, length-5),
            Point(hole_id/2-1, 0, length),
        ]),
    ])

    tube_chamfer = (hole_chamfer + hole_id/2 - tube_id/2 - 1)
    tube_profile = Wire([
        Point(tube_id/2 + tube_chamfer, 0, 0),
        Point(tube_id/2, 0, tube_chamfer),
        Point(tube_id/2, 0, inch),
        Point(tube_id/2 + 3, 0, inch+8),
    ])

    spring_relief_cut = Vertex(Origin).extrude(Up*(drywall_thickness-3), Up*inch*2.0).extrude(Right*100).extrude(Back*2, centered=True)

    spring_relief_cuts = [spring_relief_cut @ Rotate(Up, t) for t in turn_subdivisions(amount=24)]

    hole_gripper = hole_gripper_profile.extrude(Right*wall_thickness).revolve(Up).cut(spring_relief_cuts)
    tube = tube_profile.extrude(Right*wall_thickness).revolve(Up)

    result = Compound(hole_gripper, tube)
    test_region = Vertex(Origin).extrude(Up*inch).extrude(Right*100).extrude(Back*19, centered=True)
    # save_STL("through_wall_flange", result, linear_deflection=0.02)
    # export("through_wall_flange.stl", "through_wall_flange_1.stl")
    # save_STL("through_wall_flange_test", result.intersection(test_region), linear_deflection=0.02)
    # export("through_wall_flange_test.stl", "through_wall_flange_test_1.stl")

    preview(result, test_region.wires())



@run_if_changed
def threaded_hose_snap_holder():
    threads_length = 30
    holder_thickness = 3
    flat_plane = Plane(Origin + Left*(hose_od/2 + holder_thickness), Left)
    def thread_hosegrip_radius(t: ThreadPosition):
        rib_radius = hose_rib_thickness/2
        arc_distance = min(rib_radius/math.sqrt(2), abs(t.z_offset_from_nearest_crest))
        capped_distance = abs(t.z_offset_from_nearest_crest)-arc_distance
        d = hose_od/2-rib_radius + math.sqrt(rib_radius**2 - arc_distance**2) - capped_distance
        flare = max(0, 3*t.frac_along_length - 2, 1 - 3*t.frac_along_length)**2 * 3
        d += flare
        d += smootherstep(t.angle_direction[0], 0.3, 0.9) * 15
        return d
    def holder_inner_radius(t: ThreadPosition):
        # hack: pinch to near-zero on one side so Cura will delete it,
        # rather than risking a boolean op to cut
        result = thread_hosegrip_radius(t)
        if t.angle_direction[0] > 0.6:
            result += holder_thickness - 0.1
        return result
    def holder_outer_radius(t: ThreadPosition):
        result = thread_hosegrip_radius(t) + holder_thickness
        flat_radius = Origin.projected(flat_plane, by=t.angle_direction).distance(Origin)
        return Between(result, flat_radius, smootherstep(t.angle_direction[0], -0.5, -0.8))

    screw_hole = Compound(Face(Circle(Axes(p, Right), rad)).extrude(Right*100) for p, rad in [
        (Origin + Left*(hose_od/2 + holder_thickness), 3),
        (Origin + Left*(hose_od/2 + holder_thickness - 2), 7),
    ])
    # screw_holes = [screw_hole @ Translate(0, 15*dy, z) for dy in [-1, 1] for z in [threads_length - 6, 6]]
    screw_holes = [screw_hole @ Translate(Up*threads_length/2)]

    result = two_BSplineSurfaces_to_solid(
        ScrewThreadSurface(length = threads_length, pitch=hose_rib_period, radius_fn=holder_inner_radius).generate(),
        ScrewThreadSurface(length = threads_length, pitch=hose_rib_period, radius_fn=holder_outer_radius).generate(),
    )
    result = result.cut(screw_holes + [HalfSpace(Origin+Right*17, Right)])
    # save_STL("threaded_hose_snap_holder", result, linear_deflection=0.02)
    # export("threaded_hose_snap_holder.stl", "threaded_hose_snap_holder_2.stl")
    preview(result)
