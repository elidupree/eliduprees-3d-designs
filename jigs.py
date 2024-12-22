import math

from pyocct_system import *

initialize_pyocct_system()

inch = 25.4

@run_if_changed
def arms_bolt_hexer_jig():
    tool_shank_diameter = 4.5
    tool_shank_diameter_2 = 3.4
    # tool_nub_depth = 1.75
    housing_od = 33.6
    housing_or = housing_od / 2
    enclosure_or = housing_or + 1
    enclosure_od = enclosure_or*2
    lots = 100

    housing_shadow = Compound(
        Vertex(Origin).extrude(Back*housing_od, centered=True).extrude (Left*housing_od),
        Face(Circle(Axes(Origin, Up), housing_or)),
    ).extrude(Down*lots)

    housing_enclosure = Compound(
        Vertex(Origin).extrude(Back*enclosure_od, centered=True).extrude (Left*housing_or),
        Face(Circle(Axes(Origin, Up), enclosure_or)),
    ).extrude (Down*5, Up*5.5).cut([
        housing_shadow,
        Face(Circle(Axes(Origin, Up), housing_or-0.3)).extrude(Up*lots),
    ])

    notch = Compound(
        Vertex(Origin).extrude(Right*lots).extrude (Up*tool_shank_diameter_2*0.7, Up*lots).extrude(Back*tool_shank_diameter, centered=True),
        Vertex(Origin).extrude(Right*lots).extrude (Up*lots).extrude(Back*tool_shank_diameter_2, centered=True)
    )

    housing_enclosure = housing_enclosure.cut([notch @ Rotate(Up, Degrees(-17+i*60)) for i in range(-1, 2)])

    save_STL("arms_bolt_hexer_jig", housing_enclosure)
    # export("arms_bolt_hexer_jig.stl", "arms_bolt_hexer_jig_1.stl")
    return housing_enclosure
    # cuts =
preview(arms_bolt_hexer_jig)