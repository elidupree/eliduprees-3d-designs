import math

from pyocct_system import *

initialize_pyocct_system()

cordlock_radius = 6.5
cord_radius = 2.5
assumed_slat_thickness_min = 4
assumed_slat_thickness_max = 8
grabber_length = 40

@run_if_changed
def blinds_hinge():
    solid_thickness = 2
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

    a = Point(cordlock_radius, 0, solid_thickness + 7)
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