import math

from pyocct_system import *
from pyocct_utils import inch
initialize_pyocct_system()

min_thickness = 3
generous_thickness = 8
catch_height = 3
box_length = 21.25*inch

def rounded_ends_thing(x1, x2, small_radius):
    return Compound(
        [Face(Circle(Axes(Point(x,0,0),Up),small_radius)) for x in [x1, x2]],
        Edge(Point(x1, 0, 0), Point(x2, 0, 0)).extrude(Back*small_radius*2, centered=True)
    )


# 0,0,0 is "end of box, middle, ceiling"
# @run_if_changed
def screw_cut(which_hook):
    wide_cut_radius = 8
    x1 = -wide_cut_radius - min_thickness
    x2 = x1 - 5
    screw_flat_thickness=1*4
    downish = Direction(0.06, 0, -1) # the ceiling slants a little bit, making it so that a perfectly vertical (wall-parallel) driver would not reach the screw head without this slant
    parts = [rounded_ends_thing(x1, x2, inch*0.11).extrude(Down*100)]
    cutaway_square = which_hook=="middle_narrow"
    if not cutaway_square:
        parts.append(Face(Circle(Axes(Point(x1,0,0-screw_flat_thickness),Up),wide_cut_radius)).extrude(downish*100))
    return Compound(
        parts,
        Wire([Point(x1 + (wide_cut_radius if cutaway_square else 0),0,0-screw_flat_thickness), Point(x2-wide_cut_radius,0,0-screw_flat_thickness), Point(x2-wide_cut_radius-50,0,0-screw_flat_thickness-50)]).extrude(downish*100).extrude(Back*wide_cut_radius*2, centered = True)
    )

def hook(box_lip_thickness_with_leeway, box_lip_height_with_leeway, width, inset_space, screw_spacing, which_hook, bend_accommodation=0):
    circularish = math.sqrt(box_lip_height_with_leeway**2 - (inset_space+box_lip_thickness_with_leeway)**2)
    result = Face(Wire([
        Point(-inset_space-bend_accommodation,0,0),
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
    if which_hook == "corner":
        result = result.cut(screw_cut(which_hook) @ Translate(Left*(inset_space+bend_accommodation)))
    elif which_hook == "middle_narrow":
        result = result.cut([screw_cut(which_hook) @ Translate(Left*(inset_space+bend_accommodation+2) + Back*screw_spacing*d)
                             for d in [-1,1]])
    else:
        result = result.cut([screw_cut(which_hook) @ Translate(Left*(inset_space+bend_accommodation) + Back*screw_spacing*d)
                             @ Rotate(Up, Degrees(3*d))
                             for d in [-1,1]])
    if which_hook == "middle_narrow":
        # special case to work around Cura bug, augh
        a = Axes(Origin+Right*(-8-width/10), Up)
        f = Face(Circle(a, width*0.51))
        result = result.intersection(f.extrude(Down*100))
    else:
        result = result.intersection(rounded_ends_thing(-5-width/10, -10-width/10-inset_space,width/2).extrude(Down*100))
    # result = Vertex (Origin).extrude
    return result


corner_box_lip_thickness_with_leeway = 4
# could be 37, strictly; add 3 to cope with ceiling-induced irregularities in the _angle_ it gets mounted
corner_box_lip_height_with_leeway = 42 # 40 was not-quite-enough, technically worked but had a bit of a "clicky squeeze past in one place"
corner_hook_full_height = corner_box_lip_height_with_leeway+catch_height+generous_thickness
@run_if_changed
def corner_hook():
    return hook(corner_box_lip_thickness_with_leeway, corner_box_lip_height_with_leeway, 40, 0, "single", "corner", bend_accommodation=7)

needed_extra_leeway = sum([
    corner_box_lip_thickness_with_leeway, # to get past corner_hook
    min_thickness, # to get past corner_hook
    math.sqrt(box_length**2 + corner_hook_full_height**2) - box_length, #amount the box gets longer from being tilted to get past the corner hook
    3, # play it safe
])
print("needed_extra_leeway", needed_extra_leeway)
@run_if_changed
def middle_hook_straddle():
    # width can theoretically be up to ~118 but we use less so it's easy to aim
    return hook(6, 50, 90, needed_extra_leeway, 34, "middle_straddle")
@run_if_changed
def middle_hook_narrow():
    # width can theoretically be up to ~118 but we use less so it's easy to aim
    return hook(6, 50, 80, needed_extra_leeway, 16, "middle_narrow")

@run_if_changed
def wedge():
    f = Wire([
        BSplineCurve([
            Point(-1, -1, 0),
            Point(-8, -1, 0),
            Point(-14, -8, 0),
            Point(-14, -15, 0),
            Point(-14, -24, 0),
            Point(-11, -29, 0),
        ]),
        Point(0, -29, 0),
    ], loop=True).offset2d(1.0, fill=True)
    handle = Wire([
            Point(-6, -30, 0),
            Point(-10, -30, 0),
            Point(-10, -50, 0),
            Point(-6, -50, 0),
        ], loop=True).offset2d(1.0, fill=True)
    block = Face(Wire([
        BSplineCurve([
            Point(0, -4, 0),
            Point(-7, -6, 0),
            Point(-10, -9, 0),
            Point(-10, -15, 0),
        ]),
        Point(-10, -29, 0),
        Point(0, -29, 0),
    ], loop=True))
    return Compound(f, handle, block).extrude(Down*10)

save_STL("corner_hook", corner_hook, linear_deflection=0.2)
export("corner_hook.stl", "corner_hook_2.stl")
save_STL("middle_hook_straddle", middle_hook_straddle, linear_deflection=0.2)
export("middle_hook_straddle.stl", "middle_hook_straddle_3.stl")
save_STL("middle_hook_narrow", middle_hook_narrow, linear_deflection=0.2)
export("middle_hook_narrow.stl", "middle_hook_narrow_3.stl")
save_STL("wedge", wedge, linear_deflection=0.2)
export("wedge.stl", "wedge_1.stl")
preview(corner_hook @ Translate(Back*90), middle_hook_straddle, middle_hook_narrow @ Translate(Front*90), wedge)

