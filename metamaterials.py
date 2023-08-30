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
        radians = final_angle.radians * frac
        z = deform_length * (1 - frac)
        zig = Vector(zig_length, 0, 0) @ Rotate(Up, Radians(radians))
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