import math

from pyocct_system import *
from pyocct_utils import turn_subdivisions

initialize_pyocct_system()

cordlock_radius = 6.5
cord_radius = 2.5
assumed_slat_thickness_min = 4
assumed_slat_thickness_max = 8
grabber_length = 10

# staple_width = 12.68
# staple_thickness = 0.45

# @run_if_changed
def blinds_hinge():
    solid_thickness = 1.5
    springy_thickness = 1
    min_wall_thickness = 0.5

    grabber_total_thickness = assumed_slat_thickness_max + springy_thickness + min_wall_thickness
    grabber_corner = Point(cord_radius, cord_radius*2 + grabber_total_thickness + solid_thickness)
    total_height = solid_thickness*2 + cord_radius*2

    main_profile = Compound([
        Face(Circle(Axes(Origin, Up), cordlock_radius+solid_thickness)),
        Face(Wire([
            Origin + Right*cord_radius,
            grabber_corner + Vector(0, 0),
            # grabber_corner + Vector(0, grabber_length),
            # grabber_corner + Vector(springy_thickness, grabber_length),
            # grabber_corner + Vector(springy_thickness, 0),
            # grabber_corner + Vector(grabber_total_thickness-springy_thickness, 0),
            # grabber_corner + Vector(grabber_total_thickness-springy_thickness, grabber_length),
            # grabber_corner + Vector(grabber_total_thickness, grabber_length),
            grabber_corner + Vector(grabber_total_thickness, 0),
            Point(cordlock_radius+solid_thickness, 0, 0)], loop=True)),
    ]).cut(Face(Circle(Axes(Origin, Up), cordlock_radius)))

    jaws_base = Compound([
        Vertex(Origin).extrude(Up*total_height).extrude(Left*springy_thickness),
        Wire([Point(assumed_slat_thickness_max, 0, 0), Point(assumed_slat_thickness_min, 0, total_height/2), Point(assumed_slat_thickness_max, 0, total_height)]).extrude(Right*min_wall_thickness),
    ]).extrude(Back*grabber_length)

    tooth_length = 3
    tooth = Vertex(Origin).extrude(Front*2).extrude(Up*2).extrude(Right*tooth_length)
    tooth_point = Point(tooth_length, -1, 1)
    dx = 0.6
    tooth = tooth.cut([
        HalfSpace(tooth_point, d)
        for d in [Direction(dx,1,0), Direction(dx,-1,0)]
    ])
    tooth = tooth.cut([
        HalfSpace(tooth_point, d)
        for d in [Direction(dx,0,1), Direction(dx,0,-1)]
    ])

    jaws = Compound(jaws_base, [tooth @ Translate(Back*grabber_length*f) for f in [0.4,1.0]]) @ Translate(Right*springy_thickness)

    cord_shadow = Vertex(0,0,total_height/2).extrude(Right*cord_radius, Left*100).extrude(Up*cord_radius*2, centered=True).extrude(Back*100, centered=True)

    a = Point(cordlock_radius, 0, total_height)
    rough_surface_avoidance_catch = Wire(BSplineCurve([
        a,
        a + Vector(-1, 0, 1),
        a + Vector(-1, 0, 2),
        a + Vector(0, 0, 3),
    ])).extrude(Back*3, centered=True).extrude(Right*springy_thickness)

    result = main_profile.extrude(Up*total_height)
    result = result.cut([cord_shadow, cord_shadow @ Rotate(Up, Degrees(135))])
    result = Compound(result, [rough_surface_avoidance_catch @ Rotate(Up, Degrees(d)) for d in [0, 120, 240]])

    result = Compound(result, jaws @ Translate(grabber_corner - Origin))
    save_STL("blinds_hinge", result)
    export("blinds_hinge.stl", "blinds_hinge_2.stl")

    preview(result)

@run_if_changed
def blinds_hinge_2():
    ring_or = cordlock_radius+1
    ring_cut = Face(Circle(Axes(Origin, Up), cordlock_radius))
    ring_uncut = Face(Circle(Axes(Origin, Up), ring_or))

    flute_distance = 4.08

    base_thickness = 1.2

    pillar_radius = 3/2
    cord_space = 3.5

    pillar_stop_top = base_thickness+cord_space+base_thickness
    pillar = Face(Wire([BSplineCurve([
        Point(pillar_radius, 0, 0),
        Point(pillar_radius, 0, pillar_stop_top-1),
        Point(pillar_radius+1, 0, pillar_stop_top-1),
        Point(pillar_radius+1, 0, pillar_stop_top),
        Point(pillar_radius, 0, pillar_stop_top),
        Point(pillar_radius, 0, pillar_stop_top+6),
        Point(pillar_radius+0.5, 0, pillar_stop_top+6),
        Point(pillar_radius+0.5, 0, pillar_stop_top+7),
        Point(pillar_radius, 0, pillar_stop_top+7),
        Point(pillar_radius, 0, pillar_stop_top+10),
        Point(0, 0, pillar_stop_top+10),
    ]), Origin], loop=True)).revolve(Up)


    def pillar_offset(num_flutes):
        return Vector(flute_distance*num_flutes, pillar_radius+cordlock_radius, 0)


    a = pillar_offset(3)
    b = pillar_offset(6)
    cantilever_base_connector=Face(Wire([
        Point(0, pillar_radius, 0) @ Translate(v) for v in [a,b]
    ] + [
        Point(0, -pillar_radius, 0) @ Translate(b),
        Origin + (Direction(b)@Rotate(Up, Degrees(-90))) * ring_or,
        Point(0, ring_or),
    ], loop=True))
    cantilever_base = Compound(ring_uncut, cantilever_base_connector).cut(ring_cut).extrude(Up*base_thickness)

    cantilever_part = Compound(cantilever_base, [pillar @ Translate(v) for v in [a,b]])

    a = pillar_offset(-1)
    b = pillar_offset(1)
    direct_base_connector=Face(Wire([
                                            Point(0, pillar_radius, 0) @ Translate(v) for v in [a,b]
                                        ] + [
                                            Point(ring_or, 0),
                                            Point(-ring_or, 0),
                                            ], loop=True))
    direct_base = Compound(ring_uncut, direct_base_connector).cut(ring_cut).extrude(Up*base_thickness)
    direct_part = Compound(direct_base, [(pillar @ Translate(v + Down*(cord_space + base_thickness))).cut(HalfSpace(Origin, Down)) for v in [a,b]])

    retainer_grip_profile = BSplineCurve([
        Point(ring_or-1, 0, 0),
        Point(ring_or, 0, base_thickness + cord_space - 1),
        Point(ring_or - 0.7, 0, base_thickness + cord_space - 1),
        Point(ring_or - 0.7, 0, base_thickness + cord_space),
        Point(ring_or, 0, base_thickness + cord_space),
        Point(ring_or+0.3, 0, base_thickness + cord_space),
        Point(ring_or+0.3, 0, base_thickness + cord_space + base_thickness-0.3),
        Point(ring_or, 0, base_thickness + cord_space + base_thickness),
        Point(ring_or - 0.7, 0, base_thickness + cord_space + base_thickness+0.9),
        Point(ring_or - 0.7, 0, base_thickness + cord_space + base_thickness + base_thickness),
        Point(ring_or, 0, base_thickness + cord_space + base_thickness + base_thickness),
        Point(ring_or+2.3, 0, base_thickness + cord_space + base_thickness + base_thickness),
        Point(ring_or+2.3, 0, base_thickness + cord_space + base_thickness),
        Point(ring_or+1, 0, 0),
    ])
    retainer_grip = Face(Wire(retainer_grip_profile, loop=True)).revolve(Up, Degrees(40))
    retainer_base = Face(Circle(Axes(Origin, Up), ring_or+1)).cut(ring_cut).extrude(Up*base_thickness, Down*2)
    retainer_grip_part = Compound([retainer_base, retainer_grip, retainer_grip @ Rotate(Up, Turns(0.5))])

    save_STL("blinds_hinge_cantilever_part", cantilever_part)
    export("blinds_hinge_cantilever_part.stl", "blinds_hinge_cantilever_part.stl")
    save_STL("blinds_hinge_direct_part", direct_part)
    export("blinds_hinge_direct_part.stl", "blinds_hinge_direct_part.stl")
    save_STL("blinds_hinge_retainer_grip_part", retainer_grip_part)
    export("blinds_hinge_retainer_grip_part.stl", "blinds_hinge_retainer_grip_part.stl")
    preview(
        direct_part @ Translate(Up*(cord_space + base_thickness)),
        retainer_grip_part,
        #cantilever_part
            )

# @run_if_changed
def vacuum_pleat_roller():
    length = 20
    axle_radius = 3
    wall_thickness = 0.5
    vacuum_chamber_ir = 16
    vacuum_chamber_or = vacuum_chamber_ir + wall_thickness
    groove_depth = 2
    roller_or = vacuum_chamber_or + groove_depth
    roller_oc = math.tau*roller_or
    groove_approx_period = 4
    num_grooves = round(roller_oc / groove_approx_period)

    slice = Edge(
        Point(vacuum_chamber_ir, 0, 0),
        Point(roller_or, 0, 0),
    ).revolve(Up, Turns(1/num_grooves/2)).extrude(Up*length)

    slices = Compound([slice @ Rotate(Up, a) for a in turn_subdivisions(amount=num_grooves)])

    preview(slices)

# @run_if_changed
def pleat_rollers():
    length = 10
    wall_thickness = 0.5
    groove_depth = 4
    groove_approx_period = 4
    body_radius = 10
    knobs_outer_radius = body_radius + groove_depth
    roller_oc = math.tau*knobs_outer_radius
    num_grooves = round(roller_oc / groove_approx_period)
    straights_extra_length = 0.5
    straights_outer_radius = knobs_outer_radius + straights_extra_length

    def version(prong):
        return Compound([
           prong @ Rotate(Up, a) for a in turn_subdivisions(amount=num_grooves)
        ] + [
            Face(Circle(Axes(Origin, Up), body_radius)).cut(Face(Circle(Axes(Origin, Up), body_radius - wall_thickness*2)))
        ]).extrude(Up*length)

    straight_prong = Vertex(body_radius, 0, 0).extrude(Left*wall_thickness/2, Right*(groove_depth+straights_extra_length)).extrude(Back*wall_thickness, centered=True)

    knob_radius = (groove_approx_period - wall_thickness - 1.0)/2
    knob_prong = Compound(
        Vertex(body_radius, 0, 0).extrude(Left*wall_thickness/2, Right*(groove_depth-wall_thickness/2)).extrude(Back*wall_thickness, centered=True),
        Face(Circle(Axes(Origin + Right*(knobs_outer_radius-knob_radius), Up), knob_radius))
    )

    straight_roller = version(straight_prong)
    knobbed_roller = version(knob_prong)
    knobbed_roller_test = knobbed_roller.cut(HalfSpace(Point(6,0,0), Left))

    save_STL("knobbed_roller_test", knobbed_roller_test)
    export("knobbed_roller_test.stl", "knobbed_roller_test.stl")

    preview(knobbed_roller_test, straight_roller, knobbed_roller @ Rotate(Up, Turns(0.5 + 0.5/num_grooves)) @ Translate(Right*(body_radius+straights_outer_radius)))

