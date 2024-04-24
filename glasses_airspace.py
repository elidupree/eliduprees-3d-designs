import math

from pyocct_system import *
from svg_utils import Inkscape_BSplineCurve

initialize_pyocct_system()


@run_if_changed
def glasses_outer_front_view_curve_source():
    return Inkscape_BSplineCurve("""m -14.546601,61.957488
c 7.0365884,-1.023798 14.07317534,-2.047597 21.1097627,-3.071396 5.3566143,0.31431 10.7132273,0.62862 16.0698423,0.942929 6.30703,3.089823 12.614057,6.179645 18.921086,9.269467 -2.619103,7.046988 -5.238206,14.093976 -7.857309,21.140964 -3.878571,4.002399 -7.757142,8.004798 -11.635714,12.007198 -5.751966,-0.21241 -11.503929,-0.42481 -17.2558952,-0.63722 -4.51024905,-1.652669 -9.0204947,-3.305336 -13.5307436,-4.958004 -2.0785282,-5.275179 -4.1570552,-10.550355 -6.2355842,-15.825534 -0.848221,-5.343144 -1.696443,-10.686286 -2.544664,-16.029429 0.986406,-0.946325 1.972812,-1.89265 2.959219,-2.838975
z""") @ Translate(63.494634, -47.791172, 0)


@run_if_changed
def glasses_top_view_curve_source():
    return Inkscape_BSplineCurve("""m -10.208677,74.720433
c 5.4793845,-1.455719 10.95876852,-2.911437 16.4381523,-4.367155 5.3566137,-0.413402 10.7132277,-0.826804 16.0698427,-1.240206 5.750885,0.379396 11.501768,0.758791 17.252653,1.138187 -1.95173,2.100994 -3.90346,4.201987 -5.85519,6.30298 -3.878572,0.436903 -7.757142,0.873806 -11.635714,1.31071 -5.751966,0.521666 -11.50393,1.043332 -17.2558952,1.564998 -4.51024787,1.047671 -9.0204943,2.095342 -13.5307436,3.143013 -1.4482322,-1.075753 -2.8964602,-2.151502 -4.3446942,-3.227257 0.04161,-1.072336 0.08322,-2.144666 0.124827,-3.216999 0.912254,-0.469424 1.824508,-0.938847 2.736762,-1.408271
z""") @ Translate(63.494634, 24.361793, 0)



flat_face_curve_pupil_x = 284
flat_face_curve_pupil_y = 43

@run_if_changed
def face_curve_outer_front_source():
    return Inkscape_BSplineCurve("""m 267.97761,18.638847
c 3.71658,-0.706818 7.43316,-1.413636 11.14975,-2.120455 4.62474,-0.399428 9.24948,-0.798856 13.87423,-1.198285 7.44779,1.875986 14.89556,3.75197 22.34334,5.627954 1.10118,9.239522 2.20235,18.479043 3.30353,27.718565 -2.96848,8.220855 -5.93696,16.441711 -8.90544,24.662566 -6.98237,1.229945 -13.96474,2.459889 -20.94711,3.689834 -7.37407,-4.338641 -14.74815,-8.677281 -22.12222,-13.015922 -3.24215,-6.247936 -6.48431,-12.495871 -9.72646,-18.743807 0.57693,-4.778699 1.15386,-9.557399 1.73079,-14.336098 1.11801,-2.864678 2.23602,-5.729359 3.35402,-8.594039 1.98186,-1.230105 3.96372,-2.460209 5.94557,-3.690313
z""") @ Translate(-flat_face_curve_pupil_x, -flat_face_curve_pupil_y, 0)


@run_if_changed
def face_curve_outer_flat_source():
    return Inkscape_BSplineCurve("""m 254.90448,123.39286
c 0,0 19.68614,9.11073 29.52922,13.6661 3.7129,10.5104 7.4258,21.02078 11.1387,31.53117 16.67258,3.19809 33.34514,6.39617 50.01771,9.59426 6.1954,-9.59979 12.39079,-19.19956 18.5862,-28.79936 5.07892,-0.71402 10.15784,-1.42804 15.23675,-2.14206 1.4986,-1.42247 2.99719,-2.84494 4.4958,-4.26741 3.77354,-0.71402 7.54704,-1.42802 11.32056,-2.14203 3.40276,-1.49261 6.80551,-2.98522 10.20827,-4.47784 2.85921,0.83488 5.71842,1.66976 8.57763,2.50464 2.37722,-1.69533 4.75443,-3.39065 7.13166,-5.08598 1.74693,-1.88071 3.49384,-3.76142 5.24077,-5.64213 2.45137,-0.36058 4.90273,-0.72116 7.35411,-1.08174 2.26825,-0.50703 4.53648,-1.01405 6.80472,-1.52107""")

@run_if_changed
def face_curve_inner_front_source():
    return Inkscape_BSplineCurve("""m 268.02832,24.955572
c 1.90795,-0.964532 3.81589,-1.929057 5.72384,-2.893586 5.8667,-0.833446 11.73339,-1.666889 17.60009,-2.500334 6.8178,1.825415 13.6356,3.650829 20.4534,5.476243 0.55062,7.587858 1.10125,15.175716 1.65187,22.763574 -1.92299,7.622365 -3.84597,15.24473 -5.76896,22.867095 -6.19268,0.386506 -12.38537,0.773013 -18.57805,1.159519 -5.99589,-3.530735 -11.99178,-7.06147 -17.98767,-10.592205 -3.2268,-4.91319 -6.45359,-9.82638 -9.68039,-14.73957 0.39923,-4.294844 0.79846,-8.589689 1.19769,-12.884533 1.26213,-2.275825 2.52427,-4.55165 3.7864,-6.827475 0.53392,-0.609572 1.06785,-1.219151 1.60178,-1.828728
z""") @ Translate(-flat_face_curve_pupil_x, -flat_face_curve_pupil_y, 0)


@run_if_changed
def face_curve_inner_flat_source():
    return Inkscape_BSplineCurve("""m 469.49164,124.84096
c 1.63582,-0.003 3.27164,-0.006 4.90747,-0.009 3.43402,1.25773 6.86804,2.51546 10.30206,3.7732 5.80772,5.83878 11.61542,11.67756 17.42313,17.51634 4.06664,5.0519 8.13328,10.1038 12.19992,15.1557 7.82675,2.78369 15.65351,5.56737 23.48026,8.35106 7.15519,-3.7172 14.31038,-7.43439 21.46557,-11.15159 2.94457,-3.79535 5.88915,-7.5907 8.83372,-11.38605 5.66441,-2.27121 11.32882,-4.54243 16.99323,-6.81364 4.70043,-1.71507 9.40085,-3.43015 14.10128,-5.14522 3.38236,0.49984 6.76472,0.99968 10.14709,1.49952 2.33821,-2.48578 4.67643,-4.97157 7.01464,-7.45736 2.83191,-1.44409 5.6638,-2.88816 8.49571,-4.33225 1.80828,-0.003 3.61657,-0.007 5.42485,-0.0104""")


print(face_curve_outer_front_source.length(), face_curve_inner_front_source.length())


# y = distance from the lenses towards the earpieces
# z = distance upward
# (12.9 - front_y) = -9y/* + 72z/*
# (94.4 - top_y) = 7.7z/* + -72y/*
print([p for p in glasses_outer_front_view_curve_source.poles()])


fy = -9
fz = 72
ty = -72
tz = 7.7
fd = math.sqrt(fy ** 2 + fz ** 2)
td = math.sqrt(ty ** 2 + tz ** 2)
fy /= fd
fz /= fd
ty /= td
tz /= td


def from_image_coordinates(front_x, front_y, top_y):
    front_y = (31 - front_y)
    top_y = (100 - top_y)
    # front_y = y*fy+z*fz,
    # y = (front_y-z*fz)/fy
    # y = (top_y-z*tz)/ty
    # fy*(top_y-z*tz) = ty*(front_y-z*fz)
    # z*fz*ty - z*tz*fy = ty*front_y-fy*top_y
    z = (ty * front_y - fy * top_y) / (fz * ty - tz * fy)
    y = (front_y - z * fz) / fy
    return Point(front_x - 110, y, z)


def from_image_points(front, top):
    return from_image_coordinates(front[0], front[1], top[1])


@run_if_changed
def glasses_outer_curve():
    return BSplineCurve([from_image_points(front, top) for front, top in
                         zip(glasses_outer_front_view_curve_source.poles(), glasses_top_view_curve_source.poles())],
                        BSplineDimension(periodic=True))


pupillary_distance = 67


def face_curve(front, flat):
    flat_poles = [a for a in flat.poles()]
    front_length = front.length()
    left_x = flat_poles[0][0]
    right_x = flat_poles[-1][0]
    correction_factor = front_length/(right_x - left_x)
    print(correction_factor)
    skew = (flat_poles[-1][1] - flat_poles[0][1]) / (right_x - left_x)
    assert (abs(1 - correction_factor) < 0.02)
    result = []
    for distance in subdivisions(0, flat.length(), max_length = 10)[:-1]:
        flat_position = flat.position(distance = distance)
        flat_x = (flat_position[0] - left_x)
        front_position = front.position(distance = flat_x * correction_factor)
        result.append (Point(
            (-front_position[0]) - pupillary_distance/2,
            (flat_position[1] - skew*flat_x) - 125,
            -front_position[1],
        ))
    return BSplineCurve(result, BSplineDimension(periodic = True))


@run_if_changed
def face_curve_outer():
    return face_curve(face_curve_outer_front_source, face_curve_outer_flat_source)


@run_if_changed
def face_curve_inner():
    return face_curve(face_curve_inner_front_source, face_curve_inner_flat_source) @ Translate(Front*1)


@run_if_changed
def simple_wall():
    corners = [[], [], [], []]
    # for distance in subdivisions (0, glasses_outer_curve.length(), max_length =3):
    for p in glasses_outer_curve.poles():
        # d = glasses_outer_curve.derivatives(distance=distance)
        d = glasses_outer_curve.derivatives(closest = p)
        back = Direction(0.2,1,0)
        sideways = Direction((d.normal * -1).projected_perpendicular (back))
        backwards = back*40 - sideways*5
        for sink, thing in zip (corners, [
            p,
            p + backwards,
            p + sideways * 0.8 + backwards,
            p + sideways * 0.8,
        ]):
            sink.append(thing)

    faces = [Face (BSplineSurface(pair, BSplineDimension(degree = 1), BSplineDimension(periodic = True))) for pair in pairs(corners, loop = True)]
    # preview (faces)
    return Solid (Shell (faces))
    return faces


earpiece_reference_point = from_image_coordinates(46.8, 22.3, 99.9)
earpiece_depth = 3.5


@run_if_changed
def frame():
    return None
    frame_sections = []
    shadow_sections = []
    wall_thickness = 0.7
    for distance in subdivisions(0, glasses_outer_curve.length(), max_length = 0.2):
        d = glasses_outer_curve.derivatives(distance=distance)
        back = Direction(0.2,1,0.1)
        sideways = Direction((d.normal * -1).projected_perpendicular (back))
        forwards = Direction(-sideways.cross(d.tangent))
        inset = 0.5
        push_forward = 1.3
        frame_sections.append (Wire ([
            d.position - forwards * wall_thickness - sideways * inset,
            d.position - sideways * inset,
            d.position,
            d.position + forwards * push_forward,
            d.position + forwards * push_forward + sideways * wall_thickness,
            d.position - forwards * wall_thickness + sideways * wall_thickness,
            ], loop = True))
        shadow_thickness = 50
        shadow_sections.append (Wire ([
            d.position - forwards * shadow_thickness - sideways * inset,
            d.position - sideways * inset,
            d.position,
            d.position + forwards * push_forward,
            d.position + forwards * push_forward + sideways * shadow_thickness,
            d.position - forwards * shadow_thickness + sideways * shadow_thickness,
            ], loop = True))

    frame = Loft (frame_sections, solid = True)
    shadow = Loft (shadow_sections, solid = True)
    earpiece_grip = Vertex(earpiece_reference_point).extrude(Up*3, Down*(earpiece_depth + 3)).extrude(Back*1, Back*(2+wall_thickness)).extrude(Left*3, Right*2)
    earpiece_cut = Vertex(earpiece_reference_point).extrude(Down*earpiece_depth).extrude(Back*10).extrude(Left*10, Right*10)
    earpiece_grip = Intersection(earpiece_grip.cut(earpiece_cut), shadow)
    # preview(frame, shadow, earpiece_cut)
    result = Compound(
        frame,
        earpiece_grip
    )
    save_STL("frame", result)
    export("frame.stl", "frame_test_1.stl")
    return result


@run_if_changed
def face_curve_test():
    wall_thickness = 0.7

    poles = [[],[]]
    for distance in subdivisions(0, face_curve_outer.length(), max_length = 0.2)[:-1]:
        a = face_curve_outer.position(distance = distance)
        b = face_curve_inner.position(closest = a)
        poles [0].append (a)
        poles [1].append (b)

    result = Face(BSplineSurface(poles, BSplineDimension (degree =1), BSplineDimension (periodic = True)))
    result = result.extrude(Front*wall_thickness)

    save_STL("face_curve_test", result)
    export("face_curve_test.stl", "face_curve_test_1.stl")
    return result



preview(face_curve_outer, face_curve_inner, face_curve_test,
        #frame,
glasses_outer_front_view_curve_source, [p for p in glasses_outer_front_view_curve_source.poles()][:-1], glasses_top_view_curve_source, [p for p in glasses_top_view_curve_source.poles()], glasses_outer_curve, [p for p in glasses_outer_curve.poles()], simple_wall, RayIsh (Origin, Direction(0, fy, fz), 50), RayIsh (Origin, Direction(0, ty, tz), 50))
