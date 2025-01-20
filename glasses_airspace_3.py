
import math

from pyocct_system import *
from face_depthmap_loader import front_depthmap_sample_point, front_depthmap_sample_y, side_depthmap_sample_point, resample_curve_front, resample_curve_side, resample_point_frac
from svg_utils import load_Inkscape_BSplineCurve

initialize_pyocct_system()

def front_curve_from_layout_file(id):
    # I've laid out some curves as front-views in Inkscape:
    not_on_face = load_Inkscape_BSplineCurve("glasses_airspace_layout.svg", id) @ Mirror(Right) @ Rotate(Left, Degrees(90))

    return resample_curve_front(not_on_face, max_length=0.2)

@run_if_changed
def approx_face_surface():
    """A version of the face that's an actual BSplineSurface, for display"""
    return BSplineSurface([[front_depthmap_sample_point(x,z) for z in range(-42, 31, 2)] for x in range(-64,65,2)])

@run_if_changed
def window_to_seal_or_face_source():
    return front_curve_from_layout_file("window_to_seal")

def smooth_joiner_curve(a, b):
    da = a.derivatives(parameter=a.LastParameter())
    db = b.derivatives(parameter=b.FirstParameter())
    return Interpolate([da.position, db.position], tangents = [da.tangent*1, db.tangent*1])

def face_joiner_curve(a, b, sa, sb):
    not_on_face = smooth_joiner_curve(a,b)
    def fix(curve):
        l = curve.length()
        points = []
        for d in subdivisions(0, l, max_length=0.2):
            p = curve.position(distance=d)
            sideness = Between(sa, sb, smootherstep(d/l, 0.3, 0.7))
            points.append(resample_point_frac(p, sideness))
        return BSplineCurve(points)
    return fix(fix(not_on_face))

def merge_curves(curves):
    d = [list(c.poles()) for c in curves]
    return BSplineCurve([p for c in [d[0]]+[ps[1:] for ps in d[1:]] for p in c])

@run_if_changed
def face_to_seal_curve():
    forehead = resample_curve_front(window_to_seal_or_face_source, start_distance = 0, end_x = -40, end_max_by = "z", max_length=0.2)
    temple = resample_curve_side(Segment(Point(0, 54, 5), Point(0, 54, -22)), max_length=0.2)
    cheek = resample_curve_front(window_to_seal_or_face_source, start_x = -60, start_min_by = "z", end_z = -20, end_max_by = "x", max_length=0.2)
    return merge_curves([
        forehead,
        face_joiner_curve(forehead, temple, 0, 1),
        temple,
        face_joiner_curve(temple, cheek, 1, 0),
        cheek,
    ])


earpiece_top_front_outer = Point(65.0, -1.2, 4.8)
earpiece_height = 3.30
top_of_frame_z = earpiece_top_front_outer[2] + 12

print (f"forehead y: {front_depthmap_sample_y(-28, 14)}")


@run_if_changed
def approx_earpieces():
    e = Vertex(earpiece_top_front_outer).extrude(Down*earpiece_height).extrude(Vector(12.5, 68, 0)).extrude(Left*0.9)
    return Compound(e, e @ Mirror(Right))


@run_if_changed
def gframe_to_window_legacy_curve():
    # For now, shamelessly render a computed output from the previous legacy code:
    loaded = read_brep ("glasses_frame_to_window_curve.brep").curve()[0]
    s = loaded.subdivisions(max_length=1)
    frame_top = max(s, key=lambda f: f[2])
    # frame_bottom = min(s, key=lambda f: f[2])
    result = loaded @ Rotate(Axis(frame_top, Left), Degrees(2.3)) @ Translate(Up*(top_of_frame_z - frame_top[2]))
    closest_face_encounter = max((f[1] - front_depthmap_sample_y(f[0], f[2])) for f in result.subdivisions(max_length=1))
    print(f"closest_face_encounter: {closest_face_encounter}")
    face_leeway = 2
    frame_thickness = 2
    extra_leeway = 1
    result = result @ Translate(Back*(-(face_leeway + frame_thickness + extra_leeway) - closest_face_encounter))
    frame_near_earpiece_point = result.position(closest=earpiece_top_front_outer)
    print(f"earpiece y wrongness: {earpiece_top_front_outer[1] - (frame_near_earpiece_point[1] + extra_leeway + frame_thickness/2)}")
    # preview(approx_face_surface, approx_earpieces, result)
    return result


@run_if_changed
def gframe_assumed_plane():
    ps = gframe_to_window_legacy_curve.subdivisions(max_length=1)
    gframe_top = max(ps, key=lambda f: f[2])
    gframe_bottom = min(ps, key=lambda f: f[2])
    gframe_up = Direction(gframe_bottom, gframe_top)

    return Plane(
        Point(0, gframe_top[1], gframe_top[2]),
        Direction(0, -gframe_up[2], gframe_up[1])
    )

@run_if_changed
def gframe_to_window_curve():
    return BSplineCurve([p.projected(gframe_assumed_plane) for p in reversed(list(gframe_to_window_legacy_curve.poles()))], BSplineDimension(periodic=True))


class WindowTangentLine:
    def __init__(self, gframe_d, pframe_d):
        self.gframe_d = gframe_d
        self.pframe_d = pframe_d
        self.displacement = (pframe_d.position - gframe_d.position)
        gframe_outwards = gframe_d.tangent @ Rotate(gframe_assumed_plane.normal(), Degrees(-90))
        # print(gframe_d.tangent, gframe_outwards)
        self.normal_distance = self.displacement.dot(gframe_outwards)
        self.tangent_distance = self.displacement.dot(gframe_d.tangent)
        self.fallaway_distance = self.displacement.dot(-gframe_assumed_plane.normal())
        self.fallaway_slope = self.fallaway_distance / self.normal_distance
        self.skew_slope = self.tangent_distance / self.normal_distance
        self.inferred_fallaway_slope_derivative =  -self.fallaway_slope*self.skew_slope

    def edge(self):
        return Edge(self.pframe_d.position, self.gframe_d.position)


def zeroes_on_curve(curve, fn, epsilon = 0.0001):
    """Find zeroes of fn on the curve by binary search, assuming that it'll be monotonic between knots. fn is passed a CurveDerivatives. Assumes it will not hit knots exactly"""
    results = []
    for a,b in pairs(curve.knots(), loop=curve.IsPeriodic()):
        da, db = curve.derivatives(parameter=a), curve.derivatives(parameter=b)
        fa, fb = fn(da), fn(db)
        apos = fa > 0
        bpos = fb > 0
        if apos == bpos: continue
        while da.position.distance(db.position) > epsilon:
            c = Between(a, b)
            dc = curve.derivatives(parameter=c)
            fc = fn(dc)
            if (fc > 0) == bpos:
                b,db,fb = c,dc,fc
            else:
                a,da,fa = c,dc,fc
        results.append(da)
    return results


def gframe_corresponding_points(d1):
    def twistedness(d2):
        return d1.tangent.cross(d2.tangent).dot(d2.position - d1.position)
    results = [d2 for d2 in zeroes_on_curve(gframe_to_window_curve, twistedness) if d2.tangent.dot(d1.tangent) > 0]
    if len(results) != 1:
        print(f"Warning: {len(results)} corresponding points")
    # return min(results, key=lambda d2: d2.position.distance(d1.position))
    return results


def possible_tangent_lines_from_pframe_d(pframe_d):
    return [WindowTangentLine(gframe_d, pframe_d) for gframe_d in gframe_corresponding_points(pframe_d)]


def putative_normal(face_curve_d):
    p = face_curve_d.position
    cheek_level = smootherstep(p[2], 0, -1)

    # choose a "normal" in a manner that
    # ignores the foibles of the face:
    return Direction(Point(cheek_level*smootherstep(p[0],-40,-20)*-40, 85, p[2]), p)

def faceish_curve(position_fn):
    points = []
    for p in face_to_seal_curve.poles():
        d = face_to_seal_curve.derivatives(closest=p)
        points.append(position_fn(d, putative_normal(d)))
    return BSplineCurve(points)


@run_if_changed
def frame_to_seal_curve():
    def position_fn(d, normal):
        p = d.position
        cheek_level = smootherstep(p[2], 0, -1)

        cheek_smile_badness = cheek_level*min(smootherstep(p[0], -19, -40), smootherstep(p[0], -70, -50)) * 4
        leeway = 3 + cheek_smile_badness
        return p + normal * leeway

    return faceish_curve(position_fn)


hard_force_gframe_plane_x = -20

def pframe_to_window_curve_unsmoothed_position_fn(d, normal):
    p = d.position
    cheek_level = smootherstep(p[2], 0, -1)

    leeway = 8
    # convexity_bulge = smootherstep(abs(p[2] + 5), 40, 0) * 4
    # leeway = 8 + convexity_bulge
    force_gframe_plane = smootherstep(p[0], -35, hard_force_gframe_plane_x)
    gframe_plane_leeway = p.projected(onto = gframe_assumed_plane, by = normal).distance(p)
    leeway = Between(leeway, gframe_plane_leeway, force_gframe_plane)
    return p + normal * leeway


def gframe_angle(gframe_d):
    gnormal = gframe_assumed_plane.normal()
    upish = Direction(gnormal.cross(Up).cross(gnormal))
    angle = math.atan2(gframe_d.tangent.dot(Right), gframe_d.tangent.dot(-upish))
    # print(gframe_d.tangent, angle)
    return angle

@run_if_changed
def pframe_to_window_curve_unsmoothed():
    return faceish_curve(pframe_to_window_curve_unsmoothed_position_fn)


@run_if_changed
def pframe_to_window_curve_patchwork():
    ts = possible_tangent_lines_from_pframe_d(pframe_to_window_curve_unsmoothed.derivatives(x=-65, min_by="z"))
    cheek_extrapolate_tangent_line = min(ts, key=lambda t: t.pframe_d.position[0])
    ts = possible_tangent_lines_from_pframe_d(pframe_to_window_curve_unsmoothed.derivatives(parameter=0))
    forehead_tangent_line = min(ts, key=lambda t: t.pframe_d.position[0])

    start_angle = gframe_angle(forehead_tangent_line.gframe_d)
    # sx = 0
    # sy = 0
    # sd = 0
    # sy = start_slope = forehead_tangent_line.fallaway_slope
    # sd = start_slope_derivative = forehead_tangent_line.inferred_fallaway_slope_derivative
    end_angle = gframe_angle(cheek_extrapolate_tangent_line.gframe_d)
    # sx = 0
    ex = end_angle - start_angle
    ey = end_slope = cheek_extrapolate_tangent_line.fallaway_slope
    ed = end_slope_derivative = cheek_extrapolate_tangent_line.inferred_fallaway_slope_derivative

    # algebra:
    # want simplest fallback-slope fn possible;
    # constraints are value and derivative at start and end
    # 4 constraints = cubic
    # aex^3 + bex^2 = ey
    # 3aex^2 + 2bex = ed
    # a = (ey - bex)/(ex^3)
    # or b = ey/ex^2 - aex
    # and
    # a = (ed - 2bex)/(3ex^2)
    # or b = (ed - 3aex^2)/(2ex)
    # b = (edex - 3ey)/(ex (-3 + 2ex))
    # or a = (edex - 2ey)/ex^3

    # aex^3 + bex^2 + sdex + sy = 0
    # -(sd + 2bex)/(3ex^2)ex^3 + bex^2 + sdex + sy = 0
    # b = -(3sy + 2sdex)/ex^2

    a = (ed*ex - 2*ey)/(ex*ex*ex)
    b = ey/(ex*ex) - a*ex
    def slope_fn(x):
        return a*x*x*x + b*x*x
    def slope_derivative_fn(x):
        return 3*a*x*x + 2*b*x

    # print(gframe_assumed_plane.normal())
    print(start_angle, end_angle, ey, ed)
    print(a,b)
    print(slope_fn(ex), ey)
    print(slope_derivative_fn(ex), ed)

    sections = []
    for gframe_d in gframe_to_window_curve.subdivisions(output="derivatives", start_parameter = forehead_tangent_line.gframe_d.parameter, end_parameter = cheek_extrapolate_tangent_line.gframe_d.parameter, max_length=0.1, wrap=1):
        angle = gframe_angle(gframe_d)
        x = angle - start_angle
        # print(x)
        slope = slope_fn(x)
        slope_derivative = slope_derivative_fn(x)
        skew_slope = -slope_derivative/slope
        # s=-d/f sf=-d d=-f/s
        # print(slope)
        gframe_outwards = gframe_d.tangent @ Rotate(gframe_assumed_plane.normal(), Degrees(-90))
        sections.append([gframe_d.position,
                         gframe_d.position
                         + (gframe_outwards*1
                         + gframe_d.tangent*skew_slope
                         + -gframe_assumed_plane.normal()*slope).normalized()*100])
    # preview(Compound(Edge(*e) for e in sections))
    surface = BSplineSurface(sections, v=BSplineDimension(degree=1))

    print([(t.fallaway_slope, t.inferred_fallaway_slope_derivative) for t in (forehead_tangent_line, cheek_extrapolate_tangent_line)])
    # preview(face_to_seal_curve, approx_earpieces, approx_face_surface, gframe_to_window_curve, frame_to_seal_curve, pframe_to_window_curve_unsmoothed, cheek_extrapolate_tangent_line.edge(), forehead_tangent_line.edge(), surface)

    # noseish_parameter = gframe_to_window_curve.parameter(closest=Point(100, 0, 0))
    def position_fn(d, normal):
        print (d.parameter, forehead_tangent_line.pframe_d.parameter, cheek_extrapolate_tangent_line.pframe_d.parameter)
        if d.parameter <= forehead_tangent_line.pframe_d.parameter:
            return d.position.projected(onto=gframe_assumed_plane, by=normal)
        elif d.parameter >= cheek_extrapolate_tangent_line.pframe_d.parameter:
            return pframe_to_window_curve_unsmoothed_position_fn(d, normal)
        else:
            # print(gframe_angle(d), end_angle)
            return RayIsh(d.position, normal).intersections(surface).point()
    return faceish_curve(position_fn)


@run_if_changed
def manually_defined_fallback_slope_curve():

    interpolated_points = [
        (Point(-1.3165, 0), 0),
        (Point(-0.5, 4.6), 0),
        (Point(0.29, 1.696), -4.2),
        # (Point(0.9, 0.15), -3),
        (Point(1.2, 0), 0),
    ]
    # result = Wire(
    #     [Interpolate([a,b],tangents=[Vector(1, da),Vector(1,db)/5]) for (a,da),(b,db) in pairs(interpolated_points)]
    # )
    result= Interpolate(
        [p[0] for p in interpolated_points],
        parameters=[p[0][0] for p in interpolated_points],
        tangents=[Vector(1, p[1]) for p in interpolated_points]
    )
    # preview(result)
    return result

    # return BSplineCurve([
    #     Point(-1.306, 0),
    #     Point(-1.25, 0),
    #     Point(-0.5, 7),
    #     Point(0.3, 1.99),
    #     Point(0.5, 1.0),
    #     Point(0.85, 0),
    #     Point(1.1, 0),
    #     # Point(0.95, 0),
    #     # Point(0.965, 0),
    # ])

@run_if_changed
def pframe_to_window_curve():
    sections = []
    curve_start, curve_end = manually_defined_fallback_slope_curve.StartPoint()[0], manually_defined_fallback_slope_curve.EndPoint()[0]
    prev_skew_slope = None
    bads = []
    records = []
    for gframe_d in gframe_to_window_curve.subdivisions(output="derivatives", start_closest=Point(0,0,999), end_closest = Point(999,0,0), wrap=1, max_length=0.1):
        angle = gframe_angle(gframe_d)
        if curve_start < angle < curve_end:
            slope_curve_d = manually_defined_fallback_slope_curve.derivatives(x=angle)
            slope = slope_curve_d.position[1]
            slope_derivative = slope_curve_d.tangent[1]/slope_curve_d.tangent[0]
            skew_slope = -slope_derivative/slope
            # print(skew_slope)
            if prev_skew_slope is not None and skew_slope <= prev_skew_slope:
                badness = prev_skew_slope- skew_slope
                bads.append((angle, slope, badness))
            prev_skew_slope = skew_slope

            gframe_outwards = gframe_d.tangent @ Rotate(gframe_assumed_plane.normal(), Degrees(-90))
            records.append((gframe_d, skew_slope))
            sections.append([gframe_d.position,
                             gframe_d.position
                             + (gframe_outwards*1
                                + gframe_d.tangent*skew_slope
                                + -gframe_assumed_plane.normal()*slope).normalized()*100])

    remaining = gframe_to_window_curve.subdivisions(output="derivatives", start_parameter=records[-1][0].parameter, end_parameter=records[0][0].parameter, wrap=0, max_length=1)
    for gframe_d, skew_slope in zip(remaining, subdivisions(records[-1][1], records[0][1], amount=len(remaining))):
        gframe_outwards = gframe_d.tangent @ Rotate(gframe_assumed_plane.normal(), Degrees(-90))
        sections.append([gframe_d.position,
                         gframe_d.position
                         + (gframe_outwards*1
                            + gframe_d.tangent*skew_slope)])


    if bads:
        print("Worst badness:", max(bads, key=lambda triple: triple[2]))
        preview(manually_defined_fallback_slope_curve, [Edge(Point(angle, slope, 0), Point(angle, slope, 10*math.log(badness + 1))) for angle, slope, badness in bads])

    window_surface = BSplineSurface(sections, v=BSplineDimension(degree=1), u=BSplineDimension(periodic=True))
    facecurve_surface = BSplineSurface([[d.position, d.position + putative_normal(d)*100] for d in face_to_seal_curve.subdivisions(output="derivatives", max_length=1)], v=BSplineDimension(degree=1))

    return facecurve_surface.intersections(window_surface).curve().reversed()
    # preview(manually_defined_fallback_slope_curve)
    # preview(surface)


def corresponding_curve_dpairs(ds1, ds2, target_length = 1):
    """Get a smooth rollable surface that joints the two curves, as a list of CurveDerivatives-pairs where the tangents are near-coplanar.

    Assumes that the first-and-last elements of ds1 and ds2 are already coplanar."""
    def twistedness(d1, d2):
        return abs(d1.tangent.cross(d2.tangent).dot(d2.position - d1.position))
    result = [[ds1[0], ds2[0]]]
    i1,i2 = 1,1
    while i1+1 < len(ds1) and i2+1 < len(ds2):
        while ds1[i1].position.distance(result[-1][0].position) < target_length and ds1[i1].position.distance(result[-1][0].position) < target_length:
            if twistedness(ds1[i1], ds2[i2+1]) < twistedness(ds1[i1+1], ds2[i2]):
                i2 += 1
            else:
                i1 += 1
            if not (i1+1 < len(ds1) and i2+1 < len(ds2)): break
        if ds1[i1] is result[-1][0]:
            i1 += 1
        if ds2[i2] is result[-1][1]:
            i2 += 2
        result.append([ds1[i1], ds2[i2]])
    # result.append([ds1[-1], ds2[-1]])
    return result


def dpairs_to_surface(dpairs):
    # print(dpairs)
    return BSplineSurface([[d.position for d in dpair] for dpair in dpairs], u = BSplineDimension(degree=1), v = BSplineDimension(degree=1))



def sweep_illustration(curve):
    edges = []
    slope_graph_points = []
    # for d in pframe_to_window_curve.subdivisions(output="derivatives", end_x = hard_force_gframe_plane_x-0.1, end_min_by="z", max_length=5):
    for d in curve.subdivisions(output="derivatives", end_x = hard_force_gframe_plane_x-0.1, end_min_by="z", max_length=5):
        t = min(possible_tangent_lines_from_pframe_d(d), key=lambda t: t.gframe_d.position[0])
        slope_graph_points.append(Point(gframe_angle(t.gframe_d), t.fallaway_slope))
        edges.append(t.edge())
    # print(slope_graph_points)
    return Compound(edges), slope_graph_points

slope_graph_points_patchwork = None
@run_if_changed
def sweep_illustration_patchwork():
    global slope_graph_points_patchwork
    c,slope_graph_points_patchwork = sweep_illustration(pframe_to_window_curve_patchwork)
    return c
slope_graph_points_smooth = None
@run_if_changed
def sweep_illustration_smooth():
    global slope_graph_points_smooth
    c,slope_graph_points_smooth = sweep_illustration(pframe_to_window_curve)
    return c


# preview( BSplineCurve(slope_graph_points_patchwork), BSplineCurve(slope_graph_points_smooth), Edge(Point(-math.pi,-1,0), Point(math.pi,-1,0)), Edge(Origin, Point(0,10,0)), Compound([Edge(Point(-0.5,y*0.1,0),Point(0.5,y*0.1,0)) for y in range(30)]),
#          # BSplineCurve([
#          #     Point(-1.306, 0),
#          #     Point(-0.9, 0),
#          #     Point(0, 6),
#          #     Point(0.3, 1.5),
#          #     Point(0.5, 1.0),
#          #     Point(0.9, 0),
#          #     Point(1.1, 0),
#          #     # Point(0.95, 0),
#          #     # Point(0.965, 0),
#          # ])
#          manually_defined_fallback_slope_curve
#          )

preview(face_to_seal_curve, approx_earpieces, approx_face_surface, gframe_to_window_curve, frame_to_seal_curve, pframe_to_window_curve,
        # dpairs_to_surface(corresponding_curve_dpairs(pframe_to_window_curve.subdivisions(start_distance=0, end_x = hard_force_gframe_plane_x, end_min_by="z", output="derivatives",max_length=0.2), gframe_to_window_curve.subdivisions(start_closest = Point(0,0,9999), end_x = hard_force_gframe_plane_x, end_min_by="z", output="derivatives",max_length=0.01, wrap=1))),

        sweep_illustration_smooth
        )