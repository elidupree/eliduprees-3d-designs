import math

from pyocct_system import *

initialize_pyocct_system()

@run_if_changed
def deforming_slot():
    zigs = 10
    zig_length = 3
    gap_thickness = 0.3
    deform_length = 14
    final_angle = Degrees (90-45/2)
    def hoop(frac):
        angle = final_angle * frac
        z = deform_length * (1 - frac)
        zig = Vector(zig_length, 0, 0) @ Rotate(Up, angle)
        points = [Point(zig[0] * (i - 0.5*(zigs-1)), zig[1]/2 * (1 if i % 2 == 0 else -1), z) for i in range(zigs)]
        dy = gap_thickness * zig_length / zig[0] / 2
        # outer_points = [Point(*i) for i in [-1, 1]]
        return Wire(
            [p + Back*dy for p in points]
            + [p + Front*dy for p in points[::-1]]
            , loop = True
        )
    hoops = [hoop(frac) for frac in subdivisions(0, 1, amount=7)]
    slot = Loft(hoops, solid=True)
    #preview(slot)
    solid = Vertex(Origin).extrude (Left * (zigs*zig_length + 6), centered=True).extrude (Back * (zig_length + 12), centered=True).extrude(Up*deform_length)
    result = solid.cut(slot)
    save_STL("deforming_slot", result)
    preview(result)

@run_if_changed
def single_fold_deforming_slot():
    zig_length = 5
    sheet_width = 15
    throat_depth = sheet_width - zig_length*2
    deform_length = 50
    gap_thickness = 0.3
    final_angle = Degrees (135)
    wall_thickness = 6

    def hoop(frac):
        angle = final_angle * frac
        ha = angle/2
        z = deform_length * (1 - frac)
        middle = Origin + Up*z
        zig = Vector(zig_length/2, 0, 0) @ Rotate(Up, angle)
        c = middle + zig
        b = middle - zig
        a = b + Left*throat_depth
        d = c + Right*zig_length
        e = d + Back*zig_length
        def points(side):
            return [
                a + Back*1*side,
                a + Back*1*side + Right*gap_thickness,
                a + Back*side*gap_thickness/2 + Right*gap_thickness,
                b + side*(Back*gap_thickness/2 + Left*ha.sin()/ha.cos()*gap_thickness/2),
                c + side*(Back*gap_thickness/2 + Left*ha.sin()/ha.cos()*gap_thickness/2),
                d + Back*side*gap_thickness/2 + Left*side*gap_thickness/2,
                e + Back*side*gap_thickness/2 + Left*side*gap_thickness/2,
            ]
        outer_points = [
            a + Back*wall_thickness + Left*wall_thickness,
            #a + Back*wall_thickness*side + Right*wall_thickness,
            e + Front*gap_thickness/2 + Left*wall_thickness,
            e + Front*gap_thickness/2 + Right*wall_thickness,
            d + Front*wall_thickness + Right*wall_thickness,
            a + Front*wall_thickness + Right*wall_thickness,
            a + Front*wall_thickness + Left*wall_thickness,
        ]

        # outer_points = [Point(*i) for i in [-1, 1]]
        return Wire(
            points(1) + points(-1)[::-1]
            , loop = True
        ), Wire(outer_points, loop = True)
    hoops = [hoop(frac) for frac in subdivisions(0.01, 1, amount=7)]
    slot = Loft([h[0] for h in hoops], solid=True)
    preview(slot)
    solid = Loft([h[1] for h in hoops], solid=True)
    result = solid.cut(slot)
    save_STL("single_fold_deforming_slot", result)
    preview(result)