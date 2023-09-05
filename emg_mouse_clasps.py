import math

from pyocct_system import *

initialize_pyocct_system()
from svg_utils import Inkscape_BSplineCurve
from pyocct_utils import wallify


@run_if_changed
def ankle_curve():
    return Inkscape_BSplineCurve("""m 4.80573,36.395261
c 0.760558,2.347543 1.521115,4.695085 3.130229,6.738049 1.609114,2.042965 4.558312,4.129023 6.512417,4.735058 1.954105,0.606036 4.62445,0.36041 7.468315,-1.430862 2.843866,-1.791272 5.861249,-5.12819 7.636501,-7.159525 1.775251,-2.031335 4.148306,-4.893998 5.957293,-6.464833 1.808987,-1.570836 5.201737,-3.829499 7.250449,-4.995155 2.048712,-1.165656 3.318642,-1.614637 6.646659,-1.218649 3.328017,0.395987 8.713719,1.636896 12.694984,3.074403 3.981265,1.437506 6.557613,3.07144 9.905213,7.526499 3.3476,4.455059 7.4661,11.730786 9.32538,18.363192 1.85928,6.632406 1.45917,12.621045 -0.33283,18.490961 -1.79201,5.869917 -4.97588,11.620938 -8.88555,16.283898 -3.90967,4.66297 -8.545125,8.23784 -14.88632,9.50758 -6.341195,1.26974 -14.388021,0.23436 -20.598352,-2.83223 -6.210331,-3.06659 -10.583915,-8.16425 -13.488872,-12.01408 -2.904958,-3.849833 -4.341197,-6.45172 -6.359183,-7.852993 -2.017986,-1.401273 -4.6177,-1.601917 -6.641988,-1.279965 -2.024287,0.321953 -3.473138,1.1665 -4.65281,2.439889 -1.179673,1.273389 -2.09016,2.975613 -3.000649,4.677839""") @ Mirror(Back)


def clasp(curve, electrode_locations):
    rows = []
    ease_width = 6
    ease_depth = 3
    clasp_width = 40
    for z, outset in [(0, ease_depth), (ease_width, 0), (clasp_width/2,0), (clasp_width-ease_width,0), (clasp_width,ease_depth)]:
        row = []
        rows.append(row)
        for d in subdivisions(0, curve.length(), max_length = 4):
            d = curve.derivatives(distance = d)
            row.append(d.position + Up*z + (d.tangent @ Rotate(Up, Degrees(90)))*outset)
    #preview(Face(BSplineSurface(rows)).edges(), wallify(rows, 1.2, loop = False))
    result = wallify(rows, 1.4, loop = False)

    for x,y in electrode_locations:
        d = curve.derivatives(closest = Point(x,y,0))
        result = result.cut(Vertex(d.position + Up*(clasp_width/2 + 5.7)).extrude(d.tangent*6.5, centered=True).extrude(d.tangent*10 @ Rotate(Up, Degrees(90)), centered=True).extrude(Up*200))
        #preview(result)

    return result



@run_if_changed
def ankle_clasp():
    result = clasp(ankle_curve, [(50, -100), (78, -48)])
    save_STL("ankle_clasp", result)
    return result



preview(ankle_clasp, Vertex(Origin).extrude(Right*100).extrude(Front*118))