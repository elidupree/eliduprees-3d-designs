import math

from pyocct_system import *
initialize_pyocct_system()

fin_thickness = 0.7
fin_wavelength = (83.2 - fin_thickness) / 18
print(f"fin_wavelength: {fin_wavelength}")
tooth_length = 65 #58
num_teeth = 7 #21
tooth_width = fin_wavelength - fin_thickness - 0.2
thickness = 2
handle_width = 25

@run_if_changed
def tooth():
    side = [
        Point(0,0),
        Point(0,tooth_length - 10),
        Point(0,tooth_length - 5),
        Point(tooth_width/2,tooth_length),
    ]
    side_2 = [Point(tooth_width - p[0], p[1]) for p in side[::-1]]
    return Face(Wire([BSplineCurve(side), BSplineCurve(side_2)], loop = True)).extrude (Up*thickness)

@run_if_changed
def comb():
    handle = Vertex(Origin).extrude (Right * (fin_wavelength * (num_teeth-1) + tooth_width)).extrude (Front * handle_width).extrude (Up*thickness)
    result = Compound (handle, [tooth @ Translate(i*fin_wavelength,0,0) for i in range(num_teeth)])

    save_STL("comb", result)
    export("comb.stl", "comb_1.stl")
    preview (result)
    return result
