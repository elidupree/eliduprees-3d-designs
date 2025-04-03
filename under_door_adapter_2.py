import math

from pyocct_system import *
from pyocct_utils import two_BSplineSurfaces_to_solid
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

    save_STL("hose_to_bearing", result, linear_deflection=0.02)
    export("hose_to_bearing.stl", "hose_to_bearing_2.stl")
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
    save_STL("hose_to_bearing_id", result, linear_deflection=0.02)
    export("hose_to_bearing_id.stl", "hose_to_bearing_id_1.stl")
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


save_STL("tube_top_plate", tube_top_plate, linear_deflection=0.2)
export("tube_top_plate.stl", "tube_top_plate_1.stl")
save_STL("tube_bottom_solid", tube_bottom_solid, linear_deflection=0.2)
export("tube_bottom_solid.stl", "tube_bottom_solid_1.stl")
preview(bottom_of_door, tube_footprint(0), tube_top_plate, tube_bottom_solid)

