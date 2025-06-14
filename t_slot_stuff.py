import math

from pyocct_system import *
from pyocct_utils import inch, flat_ended_tube_BSplineSurface_to_solid
from t_slots import t_profile_straight, slot_depth_range, t_profile_curve_flared
from thread_sweeping import ScrewThreadSurface

initialize_pyocct_system()

@run_if_changed
def slide_in_quarter_twenty_nut():
    body = (t_profile_straight() @ Rotate(Left, Degrees(90))).extrude (Front*inch/2, centered=True)
    thread = flat_ended_tube_BSplineSurface_to_solid(ScrewThreadSurface(length = slot_depth_range[1], pitch=inch/20, radius_fn=lambda t: Between(inch/4, inch*0.1905, t.frac_from_crest_to_trough)/2).generate()) @ Rotate(Left, Degrees(180))
    # preview(body, thread)

    return body.cut(thread)

#@run_if_changed
def save_slide_in_quarter_twenty_nut():
    save_STL("slide_in_quarter_twenty_nut", slide_in_quarter_twenty_nut, linear_deflection=0.1)
    export("slide_in_quarter_twenty_nut.stl", "slide_in_quarter_twenty_nut_1.stl")

def spacer_for_screw_mount(spacer_thickness, screw_hole_radius):
    section = Wire(t_profile_curve_flared(), [
        Point(-10, 0),
        Point(-10, -spacer_thickness),
        Point(10, -spacer_thickness),
        Point(10, 0),
    ], loop=True)
    block = Face(section).extrude(Up*20)
    # preview(block, [(e @ Translate(Up*i)) for i,e in enumerate(block.edges())])
    # preview(block, [e for e in block.edges() if all_equal(p[2] for p in e.vertices())])
    # block = Chamfer(block, [(e, 1) for e in block.edges() if all_equal(p[2] for p in e.vertices())] + [(e, 1) for e in block.edges() if all_equal((p[0], p[1]) for p in e.vertices())])
    # preview(block)
    # block = Chamfer(block, [(e, 2) for e in block.edges() if all_equal((p[0], p[1]) for p in e.vertices())])
    screw_hole = Face(Circle(Axes(Point(0, 0, 10), Back), screw_hole_radius)).extrude(Back*100, centered=True)
    return block.cut(screw_hole)

@run_if_changed
def spacers_for_ceiling_monitor_mount():
    all_spacers = [spacer_for_screw_mount(d, inch*7/64) @ Translate(Left*i*30) for i,d in enumerate([8.9, 8.3, 8.3, 6.85, 6.5, 5.9])]
    save_STL("spacer_for_ceiling_monitor_mount_test", all_spacers[0], linear_deflection=0.1)
    export("spacer_for_ceiling_monitor_mount_test.stl", "spacer_for_ceiling_monitor_mount_test_3.stl")

    remaining_spacers = Compound(all_spacers[5:])
    save_STL("remaining_spacers_for_ceiling_monitor_mount", remaining_spacers, linear_deflection=0.1)
    export("remaining_spacers_for_ceiling_monitor_mount.stl", "remaining_spacers_for_ceiling_monitor_mount_3_2.stl")
    preview(all_spacers[0], remaining_spacers)

preview(slide_in_quarter_twenty_nut)