import math

from pyocct_system import *
initialize_pyocct_system()

hose_od = 46
hose_without_ribs_od = 40
bearing_od = 50
bearing_thickness = 6
hose_rib_thickness = 3.6
hose_rib_period = 6
wall_thickness=1.0

@run_if_changed
def hose_to_bearing():
    thread_turns = 2

    result = Face(Circle(Axes(Origin, Up), bearing_od/2+wall_thickness)).extrude(Up*(bearing_thickness
                                                                                     #+hose_rib_period*thread_turns
                                                                                     ))

    result = result.cut(Face(Circle(Axes(Origin, Up), bearing_od/2)).extrude(Up*(bearing_thickness)))
    result = result.cut(Face(Circle(Axes(Origin, Up), hose_without_ribs_od/2)).extrude(Up*100))

    # thread_hoop = Face(Circle(Axes(Point(hose_od/2 - hose_rib_thickness/2, 0, 0), Back), hose_rib_thickness/2)).extrude(Left*10)
    points = [
        Point(hose_od/2, 0, 0),
        Point(hose_od/2, 0, hose_rib_thickness/4),
        Point(hose_od/2 - hose_rib_thickness/4, 0, hose_rib_thickness/2),
        Point(hose_od/2 - hose_rib_thickness/4 - (hose_rib_period-hose_rib_thickness)/2, 0, hose_rib_period/2),
    ]
    thread_hoop = Wire([
                           BSplineCurve([p @ Mirror(Up) for p in points[1:][::-1]] + points) @ Translate(Up*(turns*hose_rib_period))
                           for turns in range(thread_turns+1)
                       ]

                       + [Point(bearing_od/2+wall_thickness, 0, hose_rib_period * (thread_turns + 0.5)), Point(bearing_od/2+wall_thickness, 0, -hose_rib_period*0.5)], loop=True)
    thread_hoops = [thread_hoop @ Rotate(Up, Turns(-turns)) @ Translate(Up*(bearing_thickness + (turns-0.5)*hose_rib_period)) for turns in subdivisions(0, 1, max_length=1/120)]
    thread = Loft(thread_hoops, solid=True, ruled=True)
    # preview(result, thread)
    thread = thread.cut([
        HalfSpace(Point(0, 0, bearing_thickness), Down),
        HalfSpace(Point(0, 0, bearing_thickness+hose_rib_period*thread_turns), Up),
    ])
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

    result = Compound(result, thread)

    save_STL("hose_to_bearing", result, linear_deflection=0.02)
    export("hose_to_bearing.stl", "hose_to_bearing_1.stl")
    preview(result)