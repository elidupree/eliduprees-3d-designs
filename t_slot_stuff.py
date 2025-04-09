import math

from pyocct_system import *
from pyocct_utils import inch, flat_ended_tube_BSplineSurface_to_solid
from t_slots import t_profile_straight, slot_depth_range
from thread_sweeping import ScrewThreadSurface

initialize_pyocct_system()

@run_if_changed
def slide_in_quarter_twenty_nut():
    body = (t_profile_straight() @ Rotate(Left, Degrees(90))).extrude (Front*inch/2, centered=True)
    thread = flat_ended_tube_BSplineSurface_to_solid(ScrewThreadSurface(length = slot_depth_range[1], pitch=inch/20, radius_fn=lambda t: Between(inch/4, inch*0.1905, t.frac_from_crest_to_trough)/2).generate()) @ Rotate(Left, Degrees(180))
    # preview(body, thread)

    return body.cut(thread)

@run_if_changed
def save_slide_in_quarter_twenty_nut():
    save_STL("slide_in_quarter_twenty_nut", slide_in_quarter_twenty_nut, linear_deflection=0.1)
    export("slide_in_quarter_twenty_nut.stl", "slide_in_quarter_twenty_nut_1.stl")
preview(slide_in_quarter_twenty_nut)