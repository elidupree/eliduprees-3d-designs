import math

from pyocct_system import *

initialize_pyocct_system()

cup_bottom_diameter = 64
cup_top_diameter = 71
cup_bottom_radius = cup_bottom_diameter / 2
cup_top_radius = cup_top_diameter / 2
cup_approx_height = 190

grip_height = 30
grip_leeway = 1
num_flares = 7
flare_depth = 10


@run_if_changed
def cup_holder_solid():
    rows = []
    for z,expand  in [(0,0),(15,0),(30,0),(40,10),(45,20)]:
        row = []
        rows.append (row)
        inner_radius = cup_bottom_radius + grip_leeway + expand
        center = Point(0,0,z)
        for increment in range(num_flares):
            radians = math.tau * increment / num_flares
            normal = Right @ Rotate(Up, radians=radians)
            base = center + normal * inner_radius
            tangent = Back @ Rotate(Up, radians=radians)
            flare_rounding = 5
            row.append(base - tangent * flare_rounding)
            row.append(base)
            row.append(base + tangent * flare_rounding)

            radians = math.tau * (increment + 0.5) / num_flares
            normal = Right @ Rotate(Up, radians=radians)
            base = center + normal * (inner_radius + flare_depth)
            tangent = Back @ Rotate(Up, radians=radians)
            flare_rounding = 3 + expand/3
            row.append(base - tangent * flare_rounding)
            #row.append(base)
            row.append(base + tangent * flare_rounding)

    bottom = Circle(Axes(Origin, Up), cup_bottom_radius)
    bottom2 = Circle(Axes(Origin, Up), cup_bottom_radius + grip_leeway)
    surface = BSplineSurface(rows, v = BSplineDimension (periodic = True))
    flats = [Face(Edge( BSplineCurve(r, BSplineDimension (periodic = True)))) for r in [rows[0], rows[-1]]]
    result = Solid (Shell (Face(surface), flats).complemented())
    #preview(bottom, bottom2, result)
    save_STL("cup_holder_solid", result)
    return result

preview (cup_holder_solid)