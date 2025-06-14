import math

from pyocct_system import *

initialize_pyocct_system()

cordlock_radius = 6
cord_radius = 2
assumed_slat_thickness = 6
grabber_length = 40

@run_if_changed
def blinds_hinge():
    solid_thickness = 2
    springy_thickness = 0.7

    grabber_total_thickness = assumed_slat_thickness + springy_thickness*2
    grabber_corner = Point(cord_radius, cord_radius*2 + grabber_total_thickness + solid_thickness)
    total_height = solid_thickness*2 + cord_radius*2

    main_profile = Compound([
        Face(Circle(Axes(Origin, Up), cordlock_radius+solid_thickness)),
        Face(Wire([
            Origin + Right*cord_radius,
            grabber_corner + Vector(0, 0),
            grabber_corner + Vector(0, grabber_length),
            grabber_corner + Vector(springy_thickness, grabber_length),
            grabber_corner + Vector(springy_thickness, 0),
            grabber_corner + Vector(grabber_total_thickness-springy_thickness, 0),
            grabber_corner + Vector(grabber_total_thickness-springy_thickness, grabber_length),
            grabber_corner + Vector(grabber_total_thickness, grabber_length),
            grabber_corner + Vector(grabber_total_thickness, 0),
            Point(cordlock_radius+solid_thickness, 0, 0)], loop=True)),
    ]).cut(Face(Circle(Axes(Origin, Up), cordlock_radius)))

    cord_shadow = Vertex(0,0,total_height/2).extrude(Right*cord_radius, Left*100).extrude(Up*cord_radius*2, centered=True).extrude(Back*100, centered=True)

    result = main_profile.extrude(Up*total_height)
    result = result.cut([cord_shadow, cord_shadow @ Rotate(Up, Degrees(135))])

    tooth = Vertex(Origin).extrude(Front*2).extrude(Up*2).extrude(Right*(grabber_total_thickness - springy_thickness - 0.2))
    tooth_point = Point(grabber_total_thickness - springy_thickness - 0.2, -1, 1)
    dx = 0.6
    tooth = tooth.cut([
        HalfSpace(tooth_point, d)
        for d in [Direction(dx,1,0), Direction(dx,-1,0)]
    ])
    tooth = tooth.cut([
        HalfSpace(tooth_point, d)
        for d in [Direction(dx,0,1), Direction(dx,0,-1)]
    ])

    result = Compound(result, [tooth @ Translate(grabber_corner - Origin + Back*grabber_length*f) for f in [0.6,1.0]])
    result = Compound(result, [tooth @ Mirror(Right) @ Translate(grabber_corner + Right*grabber_total_thickness - Origin + Back*grabber_length*f) for f in [0.5,0.9]])
    save_STL("blinds_hinge", result)
    export("blinds_hinge.stl", "blinds_hinge_1.stl")

    preview(result)