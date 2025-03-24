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

@run_if_changed
def washers_sharpening_jig():
    rise = 1
    run = 2
    inner_diameter = 6.35 #6.55
    outer_diameter = 12.78
    inner_profile = Face(Circle(Axes(Origin, Up), inner_diameter/2))
    outer_profile = Face(Circle(Axes(Origin, Up), outer_diameter/2))
    chunk_joiner_profile = Intersection(inner_profile, inner_profile @ Translate(Left*run))
    chunk_joiner = chunk_joiner_profile.extrude(Down*rise)
    chunk = Compound(
        inner_profile.extrude(Up*0.5, centered=True),
        chunk_joiner,
    )
    one_step = Vector(run, 0, rise)
    chunks = Compound(chunk @ Translate(one_step*i) for i in range(10))
    
    z_plane_cuts = [
        HalfSpace(Origin+s*inner_diameter/2/math.sqrt(2), s) for s in [Front, Back]
    ]
    # build_plate_cut = HalfSpace(Origin+Back*inner_diameter/2/math.sqrt(2), Back)

    along = Direction(run, 0, rise)
    along_profile = Face(Circle(Axes(Origin, along), inner_diameter/2)).cut(z_plane_cuts).extrude(along*100, centered=True)
    towards_sander = along @ Rotate(Front, Degrees(90))
    
    stop = Compound(
        Face(Circle(Axes(Origin, Up), inner_diameter/2 + 1)).extrude(Down*rise*0.5, Down*rise*1.5),
        inner_profile.extrude(Down*rise*0.5)
    ).cut(z_plane_cuts)
    
    shaft_handle = chunk_joiner_profile.extrude(towards_sander*-50).cut(z_plane_cuts) @ Translate(one_step*10)

    shaft = Compound(Intersection(chunks, along_profile), stop, shaft_handle)
    save_STL("washers_sharpening_shaft", shaft)
    export("washers_sharpening_shaft.stl", "washers_sharpening_shaft_2.stl")

    wand_cut_chunk = outer_profile.extrude(Up*rise, centered=True)
    wand = Vertex(Origin+towards_sander*1).extrude(-one_step*4, one_step*7).extrude(towards_sander*-30).extrude(Back*(outer_diameter/math.sqrt(2)), centered=True).cut([wand_cut_chunk @ Translate(one_step*i) for i in range(5)]).cut(stop)
    descender = min(wand.faces(), key=lambda f: f.bounds().max()[1]).extrude(Front*1.5)
    # preview(descender, wand.wires())
    wand = Compound(wand, descender)
    save_STL("washers_sharpening_wand", wand)
    export("washers_sharpening_wand.stl", "washers_sharpening_wand_2.stl")

    preview(shaft)
    return Compound(shaft, wand)

preview(washers_sharpening_jig)