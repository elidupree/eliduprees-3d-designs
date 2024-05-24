import math

from pyocct_system import *
from svg_utils import Inkscape_BSplineCurve

initialize_pyocct_system()

inch = 25.4


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
c 3.71658,-0.706818 7.43317,-1.413637 11.14975,-2.120455 4.62474,-0.399428 9.24949,-0.798857 13.87423,-1.198285 6.27645,1.634828 12.55289,3.269656 18.82934,4.904484 1.72192,4.860918 3.44384,9.721835 5.16576,14.582753 -1.45882,2.870321 -2.91765,5.74064 -4.37647,8.610962 -0.16961,2.09395 -0.33922,4.1879 -0.50883,6.281849 0.69478,3.765918 1.38957,7.531836 2.08435,11.297754 -2.14197,4.037346 -4.28395,8.074692 -6.42592,12.112038 -6.32464,1.303026 -12.64927,2.606053 -18.97391,3.909079 -7.37407,-4.338641 -14.74815,-8.677281 -22.12222,-13.015922 -3.24215,-6.247936 -6.48431,-12.495871 -9.72646,-18.743807 0.57693,-4.778699 1.15386,-9.557399 1.73079,-14.336098 1.11801,-2.86468 2.23601,-5.729359 3.35402,-8.594039 1.98186,-1.230104 3.96371,-2.460209 5.94557,-3.690313
z""") @ Translate(-flat_face_curve_pupil_x, -flat_face_curve_pupil_y, 0)


@run_if_changed
def face_curve_outer_flat_source():
    return Inkscape_BSplineCurve("""m 254.90448,123.39286
c 0,0 10.69532,6.16224 16.04299,9.24337 4.49542,4.19904 9.88989,9.23787 13.48623,12.59711 3.76959,5.74527 9.42395,14.36314 14.13593,21.54472 7.33722,3.86965 14.67443,7.7393 22.01163,11.60894 9.35942,-1.94822 18.71885,-3.89644 28.07827,-5.84466 5.17226,-7.47216 10.34452,-14.94431 15.51678,-22.41648 5.07892,-0.96096 10.15784,-1.92193 15.23675,-2.88289 1.4986,-1.08899 2.99719,-2.17797 4.4958,-3.26697 3.77354,-1.0475 7.54704,-2.09498 11.32056,-3.14247 3.40276,-1.49261 6.80551,-2.98522 10.20827,-4.47784 2.85921,0.83488 5.71842,1.66976 8.57763,2.50464 1.32718,-1.36994 2.65436,-2.73987 3.98155,-4.10981 2.5974,-2.35524 5.19477,-4.71046 7.79217,-7.0657 1.85923,-0.0653 3.71844,-0.13057 5.57767,-0.19585 3.05997,-0.65319 6.11991,-1.30637 9.17987,-1.95956""")

@run_if_changed
def face_curve_inner_front_source():
    return Inkscape_BSplineCurve("""m 268.02832,24.955572
c 1.90795,-0.964529 3.81589,-1.929057 5.72384,-2.893586 5.8667,-0.833445 11.73339,-1.666889 17.60009,-2.500334 5.94082,1.679251 11.88164,3.358503 17.82247,5.037754 1.15228,3.940092 2.30457,7.880184 3.45686,11.820276 -2.28254,3.3798 -4.56508,6.759601 -6.84762,10.139401 1.59636,4.225311 3.19272,8.450623 4.78908,12.675933 -1.78975,3.738101 -3.5795,7.476203 -5.36925,11.214303 -5.36443,0.459588 -10.72886,0.919176 -16.09328,1.378764 -5.99589,-3.530735 -11.99178,-7.06147 -17.98767,-10.592205 -3.2268,-4.91319 -6.45359,-9.82638 -9.68039,-14.73957 0.39923,-4.294844 0.79846,-8.589689 1.19769,-12.884533 1.26213,-2.275825 2.52427,-4.55165 3.7864,-6.827475 0.53393,-0.609576 1.06785,-1.219152 1.60178,-1.828728
z""") @ Translate(-flat_face_curve_pupil_x, -flat_face_curve_pupil_y, 0)


@run_if_changed
def face_curve_inner_flat_source():
    return Inkscape_BSplineCurve("""m 469.49164,124.14049
c 1.63582,-0.003 3.27165,-0.006 4.90747,-0.009 3.43402,0.99116 6.86804,1.98233 10.30206,2.97349 5.80771,6.5267 11.61542,13.0534 17.42313,19.58009 4.06664,5.0519 8.13328,10.10381 12.19992,15.1557 7.37421,3.78792 14.74841,7.57584 22.12262,11.36376 7.60774,-5.14277 15.21547,-10.28553 22.82321,-15.4283 2.94457,-3.79535 5.88915,-7.5907 8.83372,-11.38605 5.66441,0.29561 11.32882,0.59121 16.99323,0.88682 4.70043,-0.38167 9.40085,-0.76333 14.10128,-1.145 6.47137,-0.97042 12.94275,-1.94083 19.41411,-2.91125 -0.0273,-3.93267 -0.0546,-7.86533 -0.082,-11.79801 2.10844,-2.42719 4.21687,-4.85437 6.3253,-7.28154 1.80828,-0.003 3.61657,-0.007 5.42485,-0.0104""")


@run_if_changed
def frame_depth_curve():
    return Inkscape_BSplineCurve("""m 271.13649,331.12171
c 0,0 16.74533,-0.41447 25.118,-0.62171 10.7413,1.59535 21.48257,3.1907 32.22388,4.78606 4.22569,-0.55427 8.45135,-1.10853 12.67704,-1.6628 3.89918,0.14369 7.79834,0.28737 11.69751,0.43106 1.88283,0.0942 3.76565,0.18837 5.64847,0.28255 8.16622,-0.54562 16.33238,-1.09125 24.49861,-1.63687 7.4853,-0.034 14.97054,-0.0681 22.45583,-0.10212 4.89167,-0.0519 9.7833,-0.10387 14.67496,-0.15581 2.41099,-0.0237 4.82197,-0.0475 7.23296,-0.0712""")


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


# measurements I made:
# xy angle: 1/21
# yz angle: 8 degrees
right_lens_aggregate_outwards_normal = Direction(-1/21, -1, -Degrees(8).sin())


@run_if_changed
def glasses_outer_curve_from_2_scans():
    return BSplineCurve([from_image_points(front, top) for front, top in
                         zip(glasses_outer_front_view_curve_source.poles(), glasses_top_view_curve_source.poles())],
                        BSplineDimension(periodic=True))


@run_if_changed
def glasses_outer_curve():
    samples = [glasses_outer_curve_from_2_scans.position (distance= distance) for distance in subdivisions (0,glasses_outer_curve_from_2_scans.length(), max_length =0.5)[:-1]]
    best, _ = max (enumerate (samples), key = lambda pair: (pair[1] - Origin).dot(Vector(-1.5, 0, 1)))
    # preview (glasses_outer_curve_from_2_scans, samples [best])
    samples = samples[best:] + samples[:best]
    def planar_distance (a, b):
        return (a - b).projected_perpendicular(right_lens_aggregate_outwards_normal).length()
    planar_length = sum(planar_distance(a, b) for a, b in pairs (samples, loop = True))

    depth_curve_poles = [p for p in frame_depth_curve.poles()]
    depth_curve_left = depth_curve_poles[0][0]
    depth_curve_right = depth_curve_poles[-1][0]
    depth_curve_skew = depth_curve_poles[-1][1] - depth_curve_poles[0][1]
    depth_curve_planar_length = depth_curve_right - depth_curve_left
    correction_factor = depth_curve_planar_length / planar_length

    bad_frame_depth_average = sum((sample - Origin) . projected (right_lens_aggregate_outwards_normal).length() for sample in samples )/ len (samples)
    bad_frame_average_depth_plane = Plane(Origin + right_lens_aggregate_outwards_normal * bad_frame_depth_average, right_lens_aggregate_outwards_normal)
    depth_curve_average = sum(p [1] for p in depth_curve_poles)/len(depth_curve_poles)

    running_distance = 0
    result = []
    for a, b in pairs (samples, loop = True):
        depth_curve_distance = running_distance*correction_factor
        depth_curve_frac = depth_curve_distance / depth_curve_planar_length
        depth_point = frame_depth_curve.intersections (Plane(Origin + Right*(depth_curve_left + depth_curve_distance), Right)).point()
        depth = - (depth_point[1] - (depth_curve_skew * depth_curve_frac) - depth_curve_average)
        
        print(depth_curve_frac, depth)

        result.append (
            a.projected(bad_frame_average_depth_plane) + right_lens_aggregate_outwards_normal*depth
        )

        running_distance += planar_distance (a, b)

    return BSplineCurve(result, BSplineDimension(periodic=True))



pupillary_distance = 67


def face_curve(front, flat):
    flat_poles = [a for a in flat.poles()]
    front_length = front.length()
    left_x = flat_poles[0][0]
    right_x = flat_poles[-1][0]
    correction_factor = front_length/(right_x - left_x)
    print("Correction factor:", correction_factor)
    skew = (flat_poles[-1][1] - flat_poles[0][1]) / (right_x - left_x)
    assert (abs(1 - correction_factor) < 0.02)
    result = []
    for distance in subdivisions(0, flat.length(), max_length = 10)[:-1]:
        flat_position = flat.position(distance = distance)
        flat_x = (flat_position[0] - left_x)
        front_position = front.position(distance = flat_x * correction_factor)
        result.append (Point(
            (-front_position[0]) - pupillary_distance/2 - 2,
            (flat_position[1] - skew*flat_x) - 135,
            -front_position[1] - 8,
        ))
    # return BSplineCurve(result, BSplineDimension(periodic = True)) @ Rotate(Back, Degrees(17.5)) @ Rotate(Right, Degrees(-14.5))
    return BSplineCurve(result, BSplineDimension(periodic = True)) @ Rotate(Back, Degrees(8.5)) @ Rotate(Right, Degrees(-7.7)) # @ Rotate(Up, Degrees(4))


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
    # export("frame.stl", "frame_test_1.stl")
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
    # export("face_curve_test.stl", "face_curve_test_3.stl")
    return result


@run_if_changed
def printed_full_shield():
    wall_thickness = 0.7
    model_up = -right_lens_aggregate_outwards_normal
    frame_inset = 1.5
    frame_thickness = 2.0
    frame_funnel = 1.5
    frame_leeway = 0.5
    
    sections = []
    # for now, not [:-1] because Loft doesn't support loops
    p0 = p1 = Point(100,0,0)
    pd0 = pd1 = Vector(100,0,0)
    distance = 0
    default_increment = 4
    increment = default_increment
    length = face_curve_outer.length()
    done = False
    while not done:
        da = face_curve_outer.derivatives(distance = distance)
        a = da.position
        b = face_curve_inner.position(closest = a)

        face_tangent = Direction (a, b)

        inner = a + face_tangent*inch/8
        outer = a - face_tangent*inch/8
        on_frame_d = glasses_outer_curve.derivatives(closest = a)
        frame_outwards = Direction((on_frame_d.tangent*1).projected_perpendicular (model_up) @ Rotate(model_up, Turns(-1/4)))
        on_frame = on_frame_d.position + frame_outwards * frame_leeway
        frame_first_point = on_frame + model_up * frame_inset + frame_outwards * (wall_thickness - frame_inset)

        through = Direction((inner - outer).cross(on_frame - outer))

        diagonal = model_up @ Rotate(through, Turns(-1/8))

        try:
            join_location = Segment(frame_first_point, outer).intersections(Plane(inner, diagonal)).point()
        except RuntimeError:
            join_location = outer
            # preview(face_curve_outer, Segment(on_frame, outer), inner, inner + through*1, inner + through*3, RayIsh(inner, diagonal, length = 4))

        # uhh = Segment(on_frame, outer).intersections(Plane(, model_up @ Rotate(through, Turns(1/8)))).point()

        close = ((a - p0).length() < 5 and (da.tangent*1 - pd0).length() < 0.1 and
            (on_frame - p1).length() < 5 and (on_frame_d.tangent*1 - pd1).length() < 0.1)
        done = (distance == length)
        # print(close, distance/length, done)

        # print(close)
        if not close and distance != 0 and increment > 0.1:
            increment /= 2
            distance -= increment
            continue

        p0, p1, pd0, pd1 = a, on_frame, da.tangent*1, on_frame_d.tangent*1
        increment = default_increment
        distance += increment
        if distance > length:
            distance = length

        sections.append (Wire([
            # join_location + Direction((face_tangent*1).projected_perpendicular(model_up)) * wall_thickness,
            join_location - frame_outwards * wall_thickness,
            inner, outer,
            frame_first_point,
            on_frame + frame_outwards * wall_thickness,
            on_frame - model_up * frame_thickness + frame_outwards * wall_thickness,
            on_frame - model_up * (frame_thickness + frame_funnel) + frame_outwards * (frame_funnel + wall_thickness),
            on_frame - model_up * (frame_thickness + frame_funnel) + frame_outwards * frame_funnel,
            on_frame - model_up * frame_thickness,
            on_frame,
            on_frame + model_up * frame_inset - frame_outwards * frame_inset,
        ], loop = True))


    # preview(sections)
    model_right = Direction((Right*1).projected_perpendicular(model_up))
    model_back = model_up.cross(model_right)
    result = Loft (sections, solid = True) @ Transform(
        model_right,
        model_back,
        model_up,
    ).inverse()
    # save_STL("printed_full_shield", result)
    # export("printed_full_shield.stl", "printed_full_shield_4.stl")
    # preview(result)
    return result


vf_model_up = -right_lens_aggregate_outwards_normal

@run_if_changed
def vf_model_base():
    return Plane(Origin - vf_model_up * 8, vf_model_up)


@run_if_changed
def lens_support_for_vacuum_forming():
    wall_thickness = 2
    frame_thickness = 2.0
    model_up = vf_model_up
    model_base = vf_model_base
    rows = []
    for distance in subdivisions(0, glasses_outer_curve.length(), max_length = 0.2):
        d = glasses_outer_curve.derivatives(distance=distance)
        outwards = Direction((d.tangent*1).projected_perpendicular (model_up) @ Rotate(model_up, Turns(-1/4)))
        a = d.position - model_up * frame_thickness
        b = a - outwards * wall_thickness
        c = b.projected(model_base)
        e = a.projected(model_base)
        rows.append([a,b,c,e])

    result = Solid(Shell([Face(BSplineSurface(pairs, BSplineDimension(periodic = True), BSplineDimension(degree = 1))) for pairs in zip(*(pairs(row, loop=True) for row in rows))]))

    model_right = Direction((Right*1).projected_perpendicular(model_up))
    model_back = model_up.cross(model_right)
    result = result @ Transform(
        model_right,
        model_back,
        model_up,
    ).inverse()

    # save_STL("lens_support_for_vacuum_forming", result)
    # export("lens_support_for_vacuum_forming.stl", "lens_support_for_vacuum_forming_2.stl")
    preview (result)
    return result


@run_if_changed
def vacuum_forming_mold():
    model_up = vf_model_up
    model_base = vf_model_base
    frame_expansion = 5
    frame_sides_leeway = 0.35 #0.5
    frame_thickness_leeway = 1.5

    nose_exclusion = from_image_coordinates(94, 33, 98) + Right*3
    ear_exclusion = from_image_coordinates(54, 25, 102) + Left*5
    poles = [p for p in glasses_outer_curve.poles()][::5]
    lens_center = Vector()
    for p in poles:
        lens_center = lens_center + (p - Origin)
    lens_center = Origin + lens_center/len(poles)
    base_center = lens_center.projected(model_base)

    cg_poles = [
        p + model_up*frame_thickness_leeway + model_up @ Rotate(Right, Turns(1/4)) * frame_expansion * (-1 if p[2] < 0 else 1)
        for p in poles
        if (p - nose_exclusion).dot(Vector(1, 0, -0.1)) < 0
        and (p - ear_exclusion).dot(Vector(-1, 0, 0.1)) < 0
    ]
    clipped_glasses_curve = BSplineCurve(cg_poles, BSplineDimension (periodic = True))
    base_curve = BSplineCurve([p.projected(model_base) for p in cg_poles], BSplineDimension (periodic = True))
    expanded_base_curve = Edge(base_curve).offset2D(2)

    rows = []
    cut_rows = []
    for turns in subdivisions(0, 1, amount = 100):
        lots = 500
        angle = Turns(turns)
        anglewards = Direction(model_up.cross(Right)) @ Rotate(model_up, angle)
        sheet = BSplineSurface(
            [
                [lens_center - model_up*lots, lens_center + model_up*lots],
                [lens_center - model_up*lots + anglewards*lots, lens_center + model_up*lots + anglewards*lots],
            ]
            , BSplineDimension(degree = 1), BSplineDimension(degree = 1)
        )
        try:
            gorig = glasses_outer_curve.intersections (sheet).point()
            cg = clipped_glasses_curve.intersections (sheet).point()
            f = face_curve_outer.intersections (sheet).point()
            g = face_curve_inner.intersections (sheet).point()
            base = base_curve.intersections (sheet).point()
            ebase = expanded_base_curve.intersections (sheet).point()
        except RuntimeError:
            preview(sheet, clipped_glasses_curve, face_curve_outer, face_curve_inner, base_curve, expanded_base_curve)
        face_tangent = Direction (f, g)
        inner = f + face_tangent*inch/8*1.4
        outer = f - face_tangent*inch/8*1.4

        ob = outer.projected(model_base)
        l = (ob - base_center).length()
        h = (outer - ob).length()
        l2 = l + h*0.25

        if (ebase - base_center).length() < l2:
            ebase = base_center + anglewards*l2

        rows.append(
            subdivisions(base, cg, amount = 4)
            + subdivisions(inner, outer, amount = 7)
            # + subdivisions(ebase, base, amount = 4)[:-1]
            + [ebase]
            # + subdivisions(ebase + model_up*8, ebase, amount = 4)
        )
        h = gorig+anglewards*frame_sides_leeway+model_up*frame_thickness_leeway
        j = lens_center+anglewards*1+model_up*frame_thickness_leeway
        cut_rows.append([
            h, j, j.projected(model_base), h.projected(model_base)
        ])

    surf = BSplineSurface(rows,
                          BSplineDimension(periodic=True),
                          # BSplineDimension(periodic=True)
                          )
    ebe = BSplineCurve([r[-1] for r in rows], BSplineDimension(periodic=True))
    be = BSplineCurve([r[0] for r in rows[::-1]], BSplineDimension(periodic=True))
    face2 = Face(ebe, holes = [be])

    cut = Solid(Shell([Face(BSplineSurface(pairs, BSplineDimension(periodic = True), BSplineDimension(degree = 1))) for pairs in zip(*(pairs(row, loop=True) for row in cut_rows))]))

    result = Solid(Shell(Face(surf), face2).reversed()).cut(cut)
    earpiece_cut = Vertex(earpiece_reference_point).extrude(Up*frame_sides_leeway, Down*(earpiece_depth+frame_sides_leeway)).extrude(Front*100, Back*12).extrude(Left*4, Right*1)
    result = result.cut(earpiece_cut)
    bridge_cut = Vertex(from_image_coordinates(106, 21, 93)).extrude(Down*(10)).extrude(Front*100, Back*4).extrude(Left*10, Right*10)
    result = result.cut(bridge_cut)

    # nosepiece_cut_tip = from_image_coordinates(98, 34, 105)
    # nosepiece_cut_radius = 7
    # nosepiece_cut = Face(Circle(Axes(nosepiece_cut_tip + Front*(nosepiece_cut_radius - 3), Right), nosepiece_cut_radius)).extrude(Left*10, Right*10)
    # result = result.cut(nosepiece_cut)
    # preview(Solid(Shell(Face(surf))), cut)

    model_right = Direction((Right*1).projected_perpendicular(model_up))
    model_back = model_up.cross(model_right)
    result = result @ Transform(
        model_right,
        model_back,
        model_up,
    ).inverse()


    # save_STL("vacuum_forming_mold", result)
    # export("vacuum_forming_mold.stl", "vacuum_forming_mold_2.stl")
    preview(glasses_outer_curve, clipped_glasses_curve, result)
    return result


face_interface_mold, lens_interface_mold, shield_cutout = None,None,None
@run_if_changed
def multiple_vacuum_forming_molds():
    global face_interface_mold, lens_interface_mold, shield_cutout

    lens_mold_up = -right_lens_aggregate_outwards_normal
    face_mold_up = Direction(0.7, 1, 0)
    frame_thickness = 2.0

    def center_stuff(up, curve, extra_depth):
        center = Vector()
        points = [curve.position (distance = d) for d in subdivisions (0, curve.length(), amount = 100)]
        for p in points:
            center = center + (p - Origin)
        center = Origin + center/len(points)
        lowest = min((p - center).dot(up) for p in points)
        bottom = center + up * (lowest - extra_depth)
        base = Plane(bottom, up)
        return center, bottom, base

    lens_center, lens_mold_base_point, lens_mold_base = center_stuff(lens_mold_up, glasses_outer_curve, frame_thickness + 3)
    face_center, face_mold_base_point, face_mold_base = center_stuff(face_mold_up, face_curve_outer, 5)

    def sheets(center, up):
        for turns, is_wraparound in zip(subdivisions(0, 1, amount = 200), [False]*199 + [True]):
            lots = 500
            angle = Turns(turns)
            anglewards = Direction(up.cross(Right)) @ Rotate(up, angle)
            yield angle, anglewards, BSplineSurface(
                [
                    [center - up*lots, center + up*lots],
                    [center - up*lots + anglewards*lots, center + up*lots + anglewards*lots],
                ]
                , BSplineDimension(degree = 1), BSplineDimension(degree = 1)
            ), is_wraparound


    lens_rows = []
    lens_shadow_points = []
    trough_depth = 2
    wall_thickness = 1.5
    for angle, anglewards, sheet, is_wraparound in sheets(lens_center, lens_mold_up):
        if is_wraparound:
            continue
        p = glasses_outer_curve.intersections (sheet).point()
        d = glasses_outer_curve.derivatives (closest = p)
        frame_outwards = Direction((d.tangent*1).projected_perpendicular (lens_mold_up) @ Rotate(lens_mold_up, Turns(-1/4)))

        a = p - lens_mold_up * frame_thickness - frame_outwards*wall_thickness
        b = p - lens_mold_up * frame_thickness
        c = b - lens_mold_up * trough_depth
        d = c + frame_outwards * 3
        e = d + lens_mold_up * trough_depth
        f = e + frame_outwards * wall_thickness
        g = f.projected(lens_mold_base)
        h = a.projected(lens_mold_base)
        lens_rows.append([h,a,b,c,d,e,f,g])
        lens_shadow_points.append(p.projected(lens_mold_base))
    
    lens_shadow = Face(BSplineCurve(lens_shadow_points, BSplineDimension(periodic = True))).extrude (lens_mold_up*500)

    face_rows = []
    previous = None
    unrolled_rows = []
    rolled_rows = []
    for angle, anglewards, sheet, is_wraparound in sheets(face_center, face_mold_up):
        f = face_curve_outer.intersections (sheet).point()
        g = face_curve_inner.intersections (sheet).point()
        face_tangent = Direction (f, g)
        inner = f + face_tangent*inch/8
        outer = f - face_tangent*inch/8
        beyond_inner = inner + face_tangent*inch/8*0.4
        beyond_outer = outer - face_tangent*inch/8*0.4
        # assert((inner - face_mold_base_point).dot(face_mold_up) > 0)
        # assert((outer - face_mold_base_point).dot(face_mold_up) > 0)
        # assert(abs(anglewards.dot(face_mold_up) - 0) < 0.00001)
        ib = inner.projected (face_mold_base, by = Direction(face_mold_up + anglewards/3))
        ob = outer.projected (face_mold_base, by = Direction(face_mold_up - anglewards*0.55))

        partner = glasses_outer_curve.position(closest = outer) - lens_mold_up*(frame_thickness + trough_depth)

        if not is_wraparound:
            face_rows.append(
                [ib]
                + subdivisions(beyond_inner, beyond_outer, amount = 7)
                + [ob]
            )
            rolled_rows.append([outer, partner, partner + anglewards * 0.6, outer + anglewards * 0.6])

        if previous is None:
            unrolled_rows.append([Origin, Origin + Back*(partner - outer).length()])
        else:
            pouter, ppartner = previous
            pdir = Direction (pouter, ppartner)
            yo = (outer - pouter).dot(pdir)
            xo = (outer - pouter).projected_perpendicular(pdir).length()
            yp = (partner - ppartner).dot(pdir)
            xp = (partner - ppartner).projected_perpendicular(pdir).length()
            uo, up = unrolled_rows[-1]
            udiry = Direction(uo, up)
            udirx = udiry @ Rotate(Up, Turns(1/4))
            unrolled_rows.append([
                uo + udirx * xo + udiry * yo,
                up + udirx * xp + udiry * yp,
            ])
        previous = (outer, partner)
    unrolled_shield = Wire([row[0] for row in unrolled_rows] + [row[1] for row in unrolled_rows[::-1]], loop = True)
    rolled_shield = Solid(Shell([Face(BSplineSurface(pairs, BSplineDimension(periodic = True), BSplineDimension(degree = 1))) for pairs in zip(*(pairs(row, loop=True) for row in rolled_rows))]))

    def to_mold(rows, v = BSplineDimension()):
        surf = BSplineSurface(rows,
                              BSplineDimension(periodic=True),
                              v
                              # BSplineDimension(periodic=True)
                              )
        ebe = BSplineCurve([r[-1] for r in rows], BSplineDimension(periodic=True))
        be = BSplineCurve([r[0] for r in rows[::-1]], BSplineDimension(periodic=True))
        # preview(ebe, be)
        face2 = Face(ebe, holes = [be])
        # preview(face2, surf)

        return Solid(Shell(Face(surf), face2).reversed())

    face_mold = to_mold(face_rows)
    # lens_mold = to_mold(lens_rows, BSplineDimension(degree = 1))
    lens_mold = Solid(Shell([Face(BSplineSurface(pairs, BSplineDimension(periodic = True), BSplineDimension(degree = 1))) for pairs in zip(*(pairs(row, loop=True) for row in lens_rows))]).reversed())

    below_lens_base = Face(lens_mold_base).extrude(lens_mold_up*-500)

    earpiece_block = Vertex(earpiece_reference_point).extrude(Up*wall_thickness, Down*(earpiece_depth+wall_thickness)).extrude(Front*100, Back*3).extrude(Left*(4 + wall_thickness), Right*1)
    earpiece_cut = Vertex(earpiece_reference_point).extrude(Down*earpiece_depth).extrude(Front*100, Back*12).extrude(Left*4, Right*1)
    earpiece_block = earpiece_block.cut(earpiece_cut).cut(below_lens_base).cut(lens_shadow)

    bridge_point = from_image_coordinates(101, 29, 93)
    bridge_depth = 6
    bridge_block = Vertex(bridge_point).extrude(Down*wall_thickness*3, Up*(bridge_depth+wall_thickness*3)).extrude(Front*100, Back*10).extrude(Left*5, Right*5)
    bridge_cut = Vertex(bridge_point).extrude(Up*bridge_depth).extrude(Front*100, Back*12).extrude(Left*10, Right*10)
    # preview(lens_mold.wires(), bridge_block.cut(bridge_cut).cut(below_lens_base).cut(lens_shadow), (lens_shadow @ Translate(Right*wall_thickness)).wires())
    bridge_block = bridge_block.cut(bridge_cut).cut(below_lens_base).cut(lens_shadow).intersection(lens_shadow @ Translate(Right*wall_thickness)).intersection(below_lens_base @ Translate(lens_mold_up*10))
    lens_mold = Compound(lens_mold, earpiece_block, bridge_block)

    face_interface_mold = face_mold
    lens_interface_mold = lens_mold
    shield_cutout = unrolled_shield
    # save_STL("face_interface_mold", face_interface_mold)
    # export("face_interface_mold.stl", "face_interface_mold_1.stl")
    # save_STL("lens_interface_mold", lens_interface_mold)
    # export("lens_interface_mold.stl", "lens_interface_mold_1.stl")
    # save_STL("rolled_shield", rolled_shield)
    # export("rolled_shield.stl", "rolled_shield_1.stl")
    save_inkscape_svg("unrolled_shield", unrolled_shield)
    export("unrolled_shield.svg", "unrolled_shield_4.svg")

    preview (lens_mold, face_mold, unrolled_shield, rolled_shield)





def marker_points(curve, flat_source, offset=0):
    flat_poles = [a for a in flat_source.poles()]
    left_x = flat_poles[0][0]
    right_x = flat_poles[-1][0]
    flat_length = (right_x - left_x)
    prev = None
    projected_length = 0
    for distance in subdivisions(0, curve.length(), max_length = 0.1):
        p = curve.position(distance=distance)
        if prev is not None:
            projected_length += (p - prev).projected_perpendicular(Front).length()
        prev = p

    period = 164/18
    prev = None
    dist = 0
    next = offset
    result = []
    for distance in subdivisions(0, curve.length(), max_length = 0.1):
        p = curve.position(distance=distance)
        if prev is not None:
            dist += (p - prev).projected_perpendicular(Front).length() * flat_length / projected_length
            if dist >= next:
                result.append (Segment(p, p + Back*3))
                next += period
        prev = p
    print("Total distance:", dist)

    return result


preview(face_curve_outer, face_curve_inner, face_curve_test,
        #frame,
        marker_points(face_curve_outer, face_curve_outer_flat_source), marker_points(face_curve_inner, face_curve_inner_flat_source, 3),
glasses_outer_front_view_curve_source, [p for p in glasses_outer_front_view_curve_source.poles()][:-1], glasses_top_view_curve_source, [p for p in glasses_top_view_curve_source.poles()], glasses_outer_curve, glasses_outer_curve_from_2_scans.position(distance=0), [p for p in glasses_outer_curve_from_2_scans.poles()], simple_wall,

        RayIsh (Origin, Up, 50),
        RayIsh (Origin, Left, 50),
        RayIsh (Origin, Front, 50),
        RayIsh (Origin, right_lens_aggregate_outwards_normal, 75),
        RayIsh (Origin, Direction(0, fy, fz), 25),
        RayIsh (Origin, Direction(0, ty, tz), 25),
        )
