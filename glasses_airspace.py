import math

from pyocct_system import *
from svg_utils import Inkscape_BSplineCurve

initialize_pyocct_system()

@run_if_changed
def glasses_outer_front_view_curve_source():
    return Inkscape_BSplineCurve("""m -14.546601,61.957488
c 7.0365884,-1.023798 14.07317534,-2.047597 21.1097627,-3.071396 5.3566143,0.31431 10.7132273,0.62862 16.0698423,0.942929 6.30703,3.089823 12.614057,6.179645 18.921086,9.269467 -2.619103,7.046988 -5.238206,14.093976 -7.857309,21.140964 -3.878571,4.002399 -7.757142,8.004798 -11.635714,12.007198 -5.751966,-0.21241 -11.503929,-0.42481 -17.2558952,-0.63722 -4.51024905,-1.652669 -9.0204947,-3.305336 -13.5307436,-4.958004 -2.0785282,-5.275179 -4.1570552,-10.550355 -6.2355842,-15.825534 -0.848221,-5.343144 -1.696443,-10.686286 -2.544664,-16.029429 0.986406,-0.946325 1.972812,-1.89265 2.959219,-2.838975
z""")

@run_if_changed
def glasses_top_view_curve_source():
    return Inkscape_BSplineCurve("""m -7.9251117,74.227286
c 3.1958193,-0.962571 8.67520328,-2.41829 14.093202,-3.35285 5.4179987,-0.93456 10.7746127,-1.347962 16.3283627,-1.364965 5.55375,-0.017 11.304633,0.362392 13.20421,1.602587 1.899578,1.240195 -0.05215,3.341188 -2.967303,4.610136 -2.915151,1.268948 -6.793721,1.705852 -11.60899,2.185136 -4.815269,0.479285 -10.567233,1.000951 -15.6983395,1.785619 -5.13110657,0.784669 -9.6413531,1.83234 -12.6205938,1.818299 -2.9792407,-0.01404 -4.4274687,-1.08979 -5.1307807,-2.163836 -0.703313,-1.074045 -0.661704,-2.146375 -0.184772,-2.917253 0.476931,-0.770879 1.389185,-1.240302 4.5850043,-2.202873
z""")

# y = distance from the lenses towards the earpieces
# z = distance upward
# (12.9 - front_y) = -9y/* + 72z/*
# (94.4 - top_y) = 7.7z/* + -72y/*
print ([p for p in glasses_outer_front_view_curve_source.poles()])
def from_image_coordinates(front_x, front_y, top_y):
    fy = -9
    fz = 72
    ty = -72
    tz = 7.7
    fd = math.sqrt(fy**2 + fz**2)
    td = math.sqrt(ty**2 + tz**2)
    fy /= fd
    fz /= fd
    ty /= td
    tz /= td
    front_y = (12.9 - front_y)
    top_y = (94.4 - top_y)
    # front_y = y*fy+z*fz,
    # y = (front_y-z*fz)/fy
    # y = (top_y-z*tz)/ty
    # fy*(top_y-z*tz) = ty*(front_y-z*fz)
    # z*fz*ty - z*tz*fy = ty*front_y-fy*top_y
    z = (ty*front_y-fy*top_y) / (fz*ty - tz*fy)
    y = (front_y-z*fz)/fy
    return Point (front_x, y, z)
def from_image_points(front, top):
    return from_image_coordinates(front[0], front[1], top[1])

@run_if_changed
def glasses_outer_curve():
    return BSplineCurve([from_image_points(front, top) for front, top in zip (glasses_outer_front_view_curve_source.poles(), glasses_top_view_curve_source.poles())], BSplineDimension(periodic = True))

preview (glasses_outer_front_view_curve_source, glasses_outer_curve)
