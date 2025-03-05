import math

from pyocct_system import *
from pyocct_utils import inch
initialize_pyocct_system()

min_thickness = 3
generous_thickness = 8
catch_height = 3
box_length = 21.25*inch

# 0,0,0 is "end of box, middle, ceiling"
@run_if_changed
def screw_cut():
    wide_cut_radius = 8
    x = -wide_cut_radius - min_thickness
    screw_flat_thickness=1*4
    return Compound(
        Face(Circle(Axes(Point(x,0,0),Up),inch*0.1)).extrude(Down*100),
        Face(Circle(Axes(Point(x,0,0-screw_flat_thickness),Up),wide_cut_radius)).extrude(Down*100),
        Vertex(x,0,0-screw_flat_thickness).extrude(Down*100).extrude(Left*100).extrude(Back*wide_cut_radius*2, centered = True)
    )

def hook(box_lip_thickness_with_leeway, box_lip_height_with_leeway, width, inset_space):
    circularish = math.sqrt(box_lip_height_with_leeway**2 - (inset_space+box_lip_thickness_with_leeway)**2)
    result = Face(Wire([
        Point(-inset_space,0,0),
        Point(-inset_space,0,-box_lip_height_with_leeway),
        Point(-inset_space+(box_lip_height_with_leeway-circularish),0,-box_lip_height_with_leeway-catch_height),
        Point(box_lip_thickness_with_leeway,0,-box_lip_height_with_leeway-catch_height),
        Point(box_lip_thickness_with_leeway+catch_height/3,0,-box_lip_height_with_leeway),
        Point(box_lip_thickness_with_leeway + min_thickness,0,-box_lip_height_with_leeway),
        Point(box_lip_thickness_with_leeway + min_thickness,0,-(box_lip_height_with_leeway+catch_height+generous_thickness - 5)),
        Point(box_lip_thickness_with_leeway + min_thickness - 5,0,-(box_lip_height_with_leeway+catch_height+generous_thickness)),
        Point(-generous_thickness-inset_space,0,-(box_lip_height_with_leeway+catch_height+generous_thickness)),
        Point(-generous_thickness-inset_space-(box_lip_height_with_leeway+catch_height+generous_thickness)/2,0,0),
    ], loop = True)).extrude(Back*width, centered = True)
    result = result.cut([screw_cut @ Translate(Left*inset_space + Back*width/4*d) @ Rotate(Up, Degrees(7*d)) for d in [-1,1]])
    result = result.intersection(Face(Circle(Axes(Point(-11-inset_space,0,0),Up),width/2)).extrude(Down*100))
    # result = Vertex (Origin).extrude
    return result


corner_box_lip_thickness_with_leeway = 4
corner_box_lip_height_with_leeway = 38
corner_hook_full_height = corner_box_lip_height_with_leeway+catch_height+generous_thickness
@run_if_changed
def corner_hook():
    return hook(corner_box_lip_thickness_with_leeway, corner_box_lip_height_with_leeway, 60, 0)
@run_if_changed
def middle_hook():
    needed_extra_leeway = sum([
        corner_box_lip_thickness_with_leeway, # to get past corner_hook
        min_thickness, # to get past corner_hook
        math.sqrt(box_length**2 + corner_hook_full_height**2) - box_length, #amount the box gets longer from being tilted to get past the corner hook
        1, # play it safe
    ])
    print("needed_extra_leeway", needed_extra_leeway)
    # width can theoretically be up to ~118 but we use less so it's easy to aim
    return hook(6, 48, 90, needed_extra_leeway)

save_STL("corner_hook", corner_hook, linear_deflection=0.2)
export("corner_hook.stl", "corner_hook_1.stl")
save_STL("middle_hook", middle_hook, linear_deflection=0.2)
export("middle_hook.stl", "middle_hook_2.stl")
preview(corner_hook @ Translate(Back*90), middle_hook)

