import math

from pyocct_system import *

initialize_pyocct_system()
from svg_utils import Inkscape_BSplineCurve
from pyocct_utils import wallify


@run_if_changed
def ankle_curve():
    return Inkscape_BSplineCurve("""m 4.80573,36.395261
c 0.760558,2.347543 1.521115,4.695085 3.130229,6.738049 1.609114,2.042965 4.558312,4.129023 6.512417,4.735058 1.954105,0.606036 4.62445,0.36041 7.468315,-1.430862 2.843866,-1.791272 5.861249,-5.12819 7.636501,-7.159525 1.775251,-2.031335 4.148306,-4.893998 5.957293,-6.464833 1.808987,-1.570836 5.201737,-3.829499 7.250449,-4.995155 2.048712,-1.165656 3.318642,-1.614637 6.646659,-1.218649 3.328017,0.395987 8.713719,1.636896 12.694984,3.074403 3.981265,1.437506 6.557613,3.07144 9.905213,7.526499 3.3476,4.455059 7.4661,11.730786 9.32538,18.363192 1.85928,6.632406 1.45917,12.621045 -0.33283,18.490961 -1.79201,5.869917 -4.97588,11.620938 -8.88555,16.283898 -3.90967,4.66297 -8.545125,8.23784 -14.88632,9.50758 -6.341195,1.26974 -14.388021,0.23436 -20.598352,-2.83223 -6.210331,-3.06659 -10.583915,-8.16425 -13.488872,-12.01408 -2.904958,-3.849833 -4.341197,-6.45172 -6.359183,-7.852993 -2.017986,-1.401273 -4.6177,-1.601917 -6.641988,-1.279965 -2.024287,0.321953 -3.473138,1.1665 -4.65281,2.439889 -1.179673,1.273389 -2.09016,2.975613 -3.000649,4.677839""") @ Mirror(Back)

@run_if_changed
def foot_curve():
    return Inkscape_BSplineCurve("""m -4.7679883,-8.2985662
c 0,0 7.1650804,6.4340174 10.7476208,9.6510262 0.2674091,5.3034929 0.5882998,11.66768 0.8022273,15.910478 -2.3439713,1.931111 -5.566928,4.586387 -8.789885,7.241662 -3.4843671,3.476849 -6.9687341,6.953698 -9.5028228,9.482319 -0.991156,4.194045 -2.353991,9.960845 -3.716828,15.72765 1.448924,4.13194 2.897847,8.263879 3.95161,11.268927 3.0127711,3.22573 7.4464475,7.972802 11.29788681,12.096482 5.15530669,0.0068 10.13235119,0.01342 15.12267619,0.02003 4.678585,-1.003745 9.320508,-1.999625 14.177978,-3.041748 6.166927,1.704428 11.999889,3.316554 18.00002,4.974883 7.914017,-1.88442 15.827549,-3.768725 23.741561,-5.653143 1.543918,-4.537812 3.087759,-9.075402 4.63166,-13.613165 -0.913295,-2.849779 -1.826576,-5.699514 -2.73986,-8.549261 -2.78573,-2.201586 -5.571455,-4.403168 -8.357207,-6.604771 -3.884198,-2.188286 -7.768343,-4.376541 -11.652523,-6.564814 -0.652026,-4.118986 -1.304049,-8.237953 -1.956076,-12.356942 2.205801,-5.380923 4.411571,-10.761773 6.617388,-16.1427359 6.014917,-3.1965963 18.044581,-9.5896982 18.044581,-9.5896982""").reversed() @ Mirror(Back)

def clasp(curve, electrode_locations):
    rows = []
    ease_width = 6
    ease_depth = 1.5
    clasp_width = 36
    clasp_thickness = 3.0
    for z, outset in [(0, ease_depth), (ease_width, 0), (clasp_width/2,0), (clasp_width-ease_width,0), (clasp_width,ease_depth)]:
        row = []
        rows.append(row)
        for d in subdivisions(0, curve.length(), max_length = 4):
            d = curve.derivatives(distance = d)
            row.append(d.position + Up*z + (d.tangent @ Rotate(Up, Degrees(90)))*outset)
    #preview(Face(BSplineSurface(rows)).edges(), wallify(rows, 1.2, loop = False))
    result = wallify(rows, clasp_thickness, loop = False)

    curve_as_surface = BSplineSurface([[p+a for p in curve.poles()] for a in [Up*1, Up*-1]], u = BSplineDimension(degree=1)) #Edge(curve).extrude(Up*1, centered=True).surface()
    cuts = []
    nubs = []
    for x,y in electrode_locations:
        d = curve.derivatives(closest = Point(x,y,0))
        cuts.append(Vertex(d.position + Up*(clasp_width/2 + 5.7)).extrude(d.tangent*6.5, centered=True).extrude(d.tangent*20 @ Rotate(Up, Degrees(90)), centered=True).extrude(Up*200))
        #preview([[d.position, d.position + d.tangent*1] for dir in [-1, 1]], curve_as_surface)
        #preview([RayIsh(d.position + d.tangent * dir*22.36/2, -d.tangent @ Rotate(Up, Degrees(90))) for dir in [-1, 1]], curve_as_surface)
        edges = [RayIsh(d.position + d.tangent * dir*22.36/2, -d.tangent @ Rotate(Up, Degrees(90))).intersections(curve_as_surface).points[0] for dir in [-1, 1]]
        # assume edges are exactly the right distance from each other - we could perfect it here if needed, but in practice it's only off by 0.0004mm
        print(edges[0].distance(edges[1]))
        middle = Between(*edges)
        along = Direction(edges[1]-edges[0])
        for dir in [-1, 1]:
            nub_reference_location = middle + along*dir*8.975
            base_location = RayIsh(nub_reference_location, along @ Rotate(Up, Degrees(90))).intersections(curve_as_surface).point() + along *clasp_thickness/2 @ Rotate(Up, Degrees(90))
            tip_location = nub_reference_location + (along*-1.2 @ Rotate(Up, Degrees(90)))
            nub = Vertex(tip_location + Up*clasp_width/2).extrude(along*1.65, centered=True).extrude(base_location - tip_location).extrude(Up*12, centered=True)
            # nubs.append(nub)
        #preview(result)
    result = Compound(nubs, result.cut(cuts))

    return result



@run_if_changed
def ankle_clasp():
    result = clasp(ankle_curve, [(40, -100), (78, -48)])
    save_STL("ankle_clasp", result)
    return result


@run_if_changed
def foot_clasp():
    result = clasp(foot_curve, [(45 - 59, -(240 - 191.5))])
    save_STL("foot_clasp", result)
    return result


preview(ankle_clasp, foot_clasp, Vertex(Origin).extrude(Right*100).extrude(Front*118))