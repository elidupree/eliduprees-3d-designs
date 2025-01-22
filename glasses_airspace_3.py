
import math

from pyocct_system import *
from face_depthmap_loader import front_depthmap_sample_point, front_depthmap_sample_y, side_depthmap_sample_point, resample_curve_front, resample_curve_side, resample_point_frac
from svg_utils import load_Inkscape_BSplineCurve

initialize_pyocct_system()

def front_curve_from_layout_file(id):
    # I've laid out some curves as front-views in Inkscape:
    return load_Inkscape_BSplineCurve("glasses_airspace_layout.svg", id) @ Mirror(Right) @ Rotate(Left, Degrees(90))

@run_if_changed
def approx_face_surface():
    """A version of the face that's an actual BSplineSurface, for display"""
    return BSplineSurface([[front_depthmap_sample_point(x,z) for z in range(-42, 31, 2)] for x in range(-64,65,2)])

@run_if_changed
def window_to_seal_or_face_source():
    return resample_curve_front(front_curve_from_layout_file("window_to_seal"), max_length=0.2)

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

pframe_back_y = 54

@run_if_changed
def face_to_seal_curve():
    forehead = resample_curve_front(window_to_seal_or_face_source, start_distance = 0, end_x = -40, end_max_by = "z", max_length=0.2)
    temple = resample_curve_side(Segment(Point(0, pframe_back_y, 5), Point(0, pframe_back_y, -22)), max_length=0.2)
    cheek = resample_curve_front(window_to_seal_or_face_source, start_x = -60, start_min_by = "z", end_z = -20, end_max_by = "x", max_length=0.2)
    return merge_curves([
        forehead,
        face_joiner_curve(forehead, temple, 0, 1),
        temple,
        face_joiner_curve(temple, cheek, 1, 0),
        cheek,
    ])


earpiece_top_front_outer = Point(-65.0, -1.2, 4.8)
earpiece_height = 3.30
top_of_frame_z = earpiece_top_front_outer[2] + 10
approx_earpieces_vec = Vector(-10.5, 68, 0)

print (f"forehead y: {front_depthmap_sample_y(-28, 14)}")


@run_if_changed
def approx_earpieces_outer_face():
    return Vertex(earpiece_top_front_outer).extrude(Down*earpiece_height).extrude(approx_earpieces_vec)
@run_if_changed
def approx_earpieces():
    e = approx_earpieces_outer_face.extrude(Right*0.9)
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


gframe_reference_point = Point(0, -6, 14.8)

@run_if_changed
def gframe_assumed_plane():
    # ps = gframe_to_window_legacy_curve.subdivisions(max_length=1)
    # gframe_top = max(ps, key=lambda f: f[2])
    # gframe_bottom = min(ps, key=lambda f: f[2])
    # gframe_up = Direction(gframe_bottom, gframe_top)
    # print(Point(0, gframe_top[1], gframe_top[2]),
    #       Direction(0, -gframe_up[2], gframe_up[1]))
    return Plane(
        gframe_reference_point,
        Direction(0, -42, -7.6)
    )


gframe_front_curves_layout_earpiece_y = 225.56

@run_if_changed
def gframe_to_window_curve():
    return front_curve_from_layout_file("gframe_to_window").map_poles(lambda p: (p @ Translate(Up*(gframe_front_curves_layout_earpiece_y + earpiece_top_front_outer[2]))).projected(onto=gframe_assumed_plane, by=Back))
    # return BSplineCurve([p.projected(gframe_assumed_plane) for p in reversed(list(gframe_to_window_legacy_curve.poles()))], BSplineDimension(periodic=True))

@run_if_changed
def gframe_exclusion_curve():
    return front_curve_from_layout_file("gframe_exclusion").map_poles(lambda p: (p @ Translate(Up*(gframe_front_curves_layout_earpiece_y + earpiece_top_front_outer[2]))).projected(onto=gframe_assumed_plane, by=Back))

# preview(approx_face_surface, gframe_to_window_curve)
class WindowTangentLine:
    def __init__(self, gframe_d, pframe_d):
        self.gframe_d = gframe_d
        self.pframe_d = pframe_d
        self.displacement = (pframe_d.position - gframe_d.position)
        gframe_outwards = gframe_d.tangent @ Rotate(gframe_assumed_plane.normal(), Degrees(-90))
        # preview(approx_face_surface, gframe_to_window_curve, Edge(gframe_d.position, gframe_d.position + gframe_outwards*1), Edge(gframe_d.position, gframe_d.position -gframe_assumed_plane.normal()*1))
        # print(gframe_d.tangent, gframe_outwards)
        self.normal_distance = self.displacement.dot(gframe_outwards)
        self.tangent_distance = self.displacement.dot(gframe_d.tangent)
        self.fallaway_distance = self.displacement.dot(-gframe_assumed_plane.normal())
        self.fallaway_slope = self.fallaway_distance / self.normal_distance
        self.skew_slope = self.tangent_distance / self.normal_distance
        self.inferred_fallaway_slope_derivative = -self.fallaway_slope*self.skew_slope
        # print (vars(self))

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
    def mapper(p):
        d = face_to_seal_curve.derivatives(closest=p)
        return position_fn(d, putative_normal(d))
    return face_to_seal_curve.map_poles(mapper)


@run_if_changed
def pframe_to_seal_curve():
    def position_fn(d, normal):
        p = d.position
        cheek_level = smootherstep(p[2], 0, -1)

        cheek_smile_badness = cheek_level*(
                min(smootherstep(p[2], -30, -43), smootherstep(p[0], -70, -50)) * 4
        )
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
def gframe_angle_jump():
    candidates = zeroes_on_curve(gframe_to_window_curve, lambda d: ((gframe_angle(d) + math.tau) % math.tau) - math.pi)
    print([gframe_angle(c) for c in candidates])
    return candidates[1].parameter + 0.001


def gframe_angular_subdivisions(amount):
    increment = math.tau / amount
    plen = gframe_to_window_curve.LastParameter()
    # print (gframe_to_window_curve.FirstParameter(), gframe_to_window_curve.LastParameter())
    d = gframe_to_window_curve.derivatives(parameter=gframe_angle_jump)
    result = []
    step_size = 1
    for i in range(amount):
        angle = -math.pi + (i+0.5)*increment
        while gframe_angle(d) < angle:
            step_size = 1
            if d.parameter < gframe_angle_jump:
                step_size = min(step_size, (gframe_angle_jump-d.parameter)/2)
            d = gframe_to_window_curve.derivatives(parameter=(d.parameter + step_size) % plen)
        while step_size > 0.001:
            step_size *= 0.5
            d2 = gframe_to_window_curve.derivatives(parameter=(d.parameter - step_size) % plen)
            if gframe_angle(d2) >= angle:
                d = d2
        result.append(d)
    return result


@run_if_changed
def pframe_to_window_curve_unsmoothed():
    return faceish_curve(pframe_to_window_curve_unsmoothed_position_fn)


@run_if_changed
def pframe_to_window_curve_patchwork():
    return
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
    preview(face_to_seal_curve, approx_earpieces, approx_face_surface, gframe_to_window_curve, pframe_to_seal_curve, pframe_to_window_curve_unsmoothed, cheek_extrapolate_tangent_line.edge(), forehead_tangent_line.edge(), surface)

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
    def tangent_line(**kwargs):
        pframe_d = pframe_to_window_curve_unsmoothed.derivatives(**kwargs)
        ts = possible_tangent_lines_from_pframe_d(pframe_d)
        return min(ts, key=lambda t: t.pframe_d.position[0])
    def tangent_line_entry(**kwargs):
        t = tangent_line(**kwargs)
        return (Point(gframe_angle(t.gframe_d), t.fallaway_slope), t.inferred_fallaway_slope_derivative)

    def max_acceleration(slope, vel):
        return slope + (2*vel*vel)/slope
    
    def maxish_deceleration_over_period(dx, slope, vel):
        valid, invalid = 0, max_acceleration(slope, vel)
        while invalid-valid > 0.001:
            c = Between(valid, invalid)
            later_vel = vel + dx*c
            later_slope = slope + vel*dx + 0.5*dx*c*c
            if c <= max_acceleration(later_slope, later_vel):
                valid = c
            else:
                invalid = c
        return valid

    def tightest(x, already_determined, tightness=1.0):
        np, nd = already_determined
        diff = x - np[0]
        max_accel = max_acceleration(np[1], nd) if diff*nd > 0 else maxish_deceleration_over_period(diff, np[1], nd)
        max_accel *= tightness
        print(already_determined, diff, max_accel)
        d = nd + max_accel * diff
        y = np[1] + nd*diff + max_accel*diff*diff*0.5
        # print (np, nd, diff, max_accel, d, y)
        return Point(x, y), d
    
    # preview(approx_face_surface, gframe_to_window_curve, [tangent_line(x=x, min_by="z").edge() for x in subdivisions(-35, -65, amount=10)])

    forehead = tangent_line_entry(parameter=0)
    forehead = (Point(forehead[0][0], 0), 0)
    cheek = tangent_line_entry(x=-65, min_by="z")
    cheek2 = tangent_line_entry(x=-40, min_by="z")
    # end = tangent_line_entry(x=hard_force_gframe_plane_x, min_by="z")
    end = (Point(math.pi*0.6, 0), 0)
    # preview(tangent_line(x=hard_force_gframe_plane_x, min_by="z").edge(), approx_face_surface, gframe_to_window_curve)

    m = min(max_acceleration(cheek[0][1], cheek[1]), max_acceleration(cheek2[0][1], cheek2[1]))
    assert((cheek2[1]-cheek[1])/(cheek2[0][0] - cheek[0][0]) < m)

    print(forehead, cheek, cheek2, end)
    tight_segment1 = [cheek]
    for x in subdivisions(cheek[0][0], 0, amount=15)[1:]:
        if tight_segment1[-1][0][1] > 2:
            break
        tight_segment1.append(tightest(x, tight_segment1[-1]))
    tight_segment2 = [cheek2]
    while tight_segment2[-1][1] < -0.02:
        step_size = 0.1
        while True:
            x = tight_segment2[-1][0][0] + step_size
            prev_slope = tight_segment2[-1][0][1]
            prev_d = tight_segment2[-1][1]
            candidate = tightest(x, tight_segment2[-1])
            if prev_slope*0.9 < candidate[0][1] and candidate[1] < prev_d*0.9:
                step_size /= 16
                tightness = 1-(tight_segment2[-1][0][1]/cheek2[0][1])/10
                candidate = tightest(tight_segment2[-1][0][0] + step_size, tight_segment2[-1], tightness)
                tight_segment2.append(candidate)
                break
            step_size /= 2
            if step_size < 0.00001:
                print(prev_slope, prev_d, candidate)
                assert False
    tight_segment2 = tight_segment2[:-1]
    # for x in subdivisions(cheek2[0][0], Between(cheek2[0][0], end[0][0]), amount=30)[1:]:
    #     tight_segment2.append(tightest(x, tight_segment2[-1]))
    #     if :
    #         break
    print([p[0][0] for p in tight_segment1])
    print([p[0][0] for p in tight_segment2])
    interpolated_points = ([
        forehead,
        (Point(forehead[0][0]+0.3, 0.5), 10),
        (Point(-0.85, 6), 0),
        ]+tight_segment1[::-1]+tight_segment2+[
        # (Point(0, 3.8), -4),
        # (Point(0.29, 1.696), -4.2),
        # (Point(0.9, 0.15), -3),
        # cheek2,
        end,
    ])
    # tangent_magnitudes = [1/max(1, abs(p[1]/p[0][1])) for p in interpolated_points]
    # for (ai, ap), (bi, bp) in pairs(enumerate(interpolated_points)):
    #     mag = (bp[0][0] - ap[0][0]) / 2
    #     tangent_magnitudes[ai] = min(mag, tangent_magnitudes[ai])
    #     tangent_magnitudes[bi] = min(mag, tangent_magnitudes[bi])

    # preview(Wire(
    #     [Interpolate([a,b],tangents=[Vector(1, da),Vector(1,db)/5]) for (a,da),(b,db) in pairs(interpolated_points)]
    # ))
    # result = Interpolate(
    #     [p[0] for p in interpolated_points],
    #     parameters=[p[0][0] for p in interpolated_points],
    #     tangents=[None if p[1] is None else Vector(1, p[1]).normalized()*mag for p,mag in zip(interpolated_points, tangent_magnitudes)]
    # )
    # preview(result, [Edge(p[0], p[0]+Vector(1, p[1])*0.1) for p in interpolated_points])
    def control_point(a,b,da,db):
        result = a+Vector(1, da)*(b[0]-a[0])/3
        if result[1] < 0:
            return a-Vector(1, da)*a[1]/da
        return result
    print( [
        [a, control_point(a,b,da,db), control_point(b,a,db,da), b] for (a,da),(b,db) in pairs(interpolated_points)
    ])
    result = [
        BezierCurve([a, control_point(a,b,da,db), control_point(b,a,db,da), b]) for (a,da),(b,db) in pairs(interpolated_points)
    ]
    preview(Wire(result))
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

window_extended_surface, facecurve_extended_surface, window_extended_sections, facecurve_extended_sections = None, None, None, None
@run_if_changed
def pframe_to_window_curve():
    sections = []
    curve_start, curve_end = manually_defined_fallback_slope_curve[0].StartPoint()[0], manually_defined_fallback_slope_curve[-1].EndPoint()[0]
    prev_skew_angle = None
    bads = []
    records = []
    start_flats = []
    end_flats = []
    for gframe_d in gframe_angular_subdivisions(360):
        angle = gframe_angle(gframe_d)
        # print(angle)
        slope_curve_d = None
        if curve_start < angle < curve_end:
            for c in manually_defined_fallback_slope_curve:
                if c.StartPoint()[0] <= angle <= c.EndPoint()[0]:
                    slope_curve_d = c.derivatives(x=angle)
                    break
            slope = slope_curve_d.position[1]
            if slope < 0.001:
                slope_curve_d = None
        if slope_curve_d is not None:
            slope_derivative = slope_curve_d.tangent[1]/slope_curve_d.tangent[0]
            skew_slope = -slope_derivative/slope
            skew_angle = math.atan(skew_slope) + angle
            # print(skew_slope)
            if prev_skew_angle is not None and skew_angle <= prev_skew_angle:
                badness = prev_skew_angle - skew_angle
                bads.append((angle, slope, badness))
            prev_skew_angle = skew_angle

            gframe_outwards = gframe_d.tangent @ Rotate(gframe_assumed_plane.normal(), Degrees(-90))
            records.append((gframe_d, math.atan(skew_slope)))
            sections.append([gframe_d.position,
                             gframe_d.position
                             + (gframe_outwards*1
                                + gframe_d.tangent*skew_slope
                                + -gframe_assumed_plane.normal()*slope).normalized()*100])
        else:
            (start_flats if len(records) == 0 else end_flats).append(gframe_d)

    flats = end_flats + start_flats
    # remaining = gframe_to_window_curve.subdivisions(output="derivatives", start_parameter=records[-1][0].parameter, end_parameter=records[0][0].parameter, wrap=0, max_length=1)
    flat_sections = []
    for gframe_d, skew_radians in zip(flats, subdivisions(records[-1][1], records[0][1], amount=len(flats))):
        # print(skew_radians)
        gframe_outwards = gframe_d.tangent @ Rotate(gframe_assumed_plane.normal(), Degrees(-90))
        flat_sections.append([gframe_d.position,
                         gframe_d.position
                         + (gframe_outwards*1 @ Rotate(gframe_assumed_plane.normal(), Radians(skew_radians))).normalized()*100])

    sections = flat_sections[100:] + sections + flat_sections[:100]

    if bads:
        print("Worst badness:", max(bads, key=lambda triple: triple[2]))
        preview(Wire(manually_defined_fallback_slope_curve), [Edge(Point(angle, slope, 0), Point(angle, slope, 10*math.log(badness + 1))) for angle, slope, badness in bads])

    global window_extended_surface, facecurve_extended_surface, window_extended_sections, facecurve_extended_sections
    window_extended_sections = sections
    window_surface = BSplineSurface(sections, v=BSplineDimension(degree=1), u=BSplineDimension(periodic=True))
    facecurve_sections = facecurve_extended_sections = [[d.position, d.position + putative_normal(d)*100] for d in face_to_seal_curve.subdivisions(output="derivatives", max_length=1)]
    facecurve_surface = BSplineSurface(facecurve_sections, v=BSplineDimension(degree=1))
    preview(window_surface, facecurve_surface)
    # preview (facecurve_surface.intersections(window_surface).curves)
    window_extended_surface = window_surface
    facecurve_extended_surface = facecurve_surface
    return facecurve_surface.intersections(window_surface).curve().reversed()
    # preview(manually_defined_fallback_slope_curve)
    # preview(surface)


@run_if_changed
def approx_nose_surface():
    # generate a pretty precise approximation of the surface right around the nose
    return BSplineSurface([[front_depthmap_sample_point(x,z) for z in subdivisions(-27, 0, max_length=0.6)] for x in subdivisions(-15, 0, max_length=0.6)])

window_sections = None
@run_if_changed
def window_surface():
    sections = []
    right_blockers = [Plane(Origin, Right), approx_nose_surface]
    for a,b in window_extended_sections:
        s = Segment(a, b)
        blockages = s.intersections(facecurve_extended_surface).points
        if b[0] > a[0]:
            blockages.extend(p for b in right_blockers for p in s.intersections(b).points)
        b = min(blockages, key=lambda b: a.distance(b))
        sections.append([a,b])
    global window_sections
    window_sections = sections
    window_surface = BSplineSurface(sections, v=BSplineDimension(degree=1), u=BSplineDimension(periodic=True))
    # preview(window_surface)
    return window_surface

@run_if_changed
def window_solid():
    sections = [[],[],[],[]]
    thickness = 0.5
    for a,b in window_sections:
        normal = window_surface.normal(closest = a)
        a2, b2 = a+normal*thickness, b+normal*thickness
        sections[0].append([a,a2])
        sections[1].append([a2,b2])
        sections[2].append([b2,b])
        sections[3].append([b,a])

    return Solid(Shell([Face(BSplineSurface(s, v=BSplineDimension(degree=1), u=BSplineDimension(periodic=True))) for s in sections]))


@run_if_changed
def pframe_extended():
    sections = []
    # thickness = 4
    overlap_to_cut_later = 0.25
    print (pframe_to_seal_curve.LastParameter(), face_to_seal_curve.LastParameter())
    assert (pframe_to_seal_curve.LastParameter() == face_to_seal_curve.LastParameter())
    assert (pframe_to_seal_curve.FirstParameter() == face_to_seal_curve.FirstParameter())
    gframe_shadow = gframe_to_window_curve.extrude(Back*20)

    for d in pframe_to_seal_curve.subdivisions(output="derivatives", max_length=1):
        a = d.position
        f = face_to_seal_curve.position(parameter=d.parameter)
        normal = Direction(f,a)
        inwards = -facecurve_extended_surface.normal(closest = a)
        print(normal)
        try:
            b = RayIsh(a, normal).intersections(window_extended_surface).point() + normal*overlap_to_cut_later
            b2 = RayIsh(a+inwards*2.5, normal).intersections(window_extended_surface).point() + normal*overlap_to_cut_later
        except RuntimeError:
            preview(pframe_to_seal_curve, a, a+inwards*2.5, window_extended_surface)
        # b = a + normal * 20
        a2 = a+inwards*4
        gframe_overlap = Segment(a,a2).intersections(gframe_shadow)
        if gframe_overlap.points:
            a2 = gframe_overlap.point()
        sections.append(Wire([a,a2,b2,b], loop=True))
    # preview(sections)
    return Loft(sections, solid=True)


@run_if_changed
def pframe():
    # preview(pframe_extended)
    return pframe_extended.cut(Face(window_extended_surface).extrude(Front*100))
# preview(window_solid, pframe_extended)

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

# slope_graph_points_patchwork = None
# @run_if_changed
# def sweep_illustration_patchwork():
#     global slope_graph_points_patchwork
#     c,slope_graph_points_patchwork = sweep_illustration(pframe_to_window_curve_patchwork)
#     return c
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


def bsplinecurve_offset(curve, normal, offset, **kwargs):
    pairs = []
    bads = []
    prev = None
    bad_idxs = set()
    ds = curve.subdivisions(output="derivatives", max_length=0.4, **kwargs)
    for i,d in enumerate(ds):
        a = d.position
        b = a + (d.tangent @ Rotate(normal, Degrees(90)))*offset
        # good_idx = len(pairs) - 1
        # while good_idx > 0 and (b - pairs[good_idx][0].position).dot(pairs[good_idx][0].tangent) <= 0:
        #     good_idx -= 1
        # bad_idxs = range(good_idx+1, len(pairs))
        # for bad_idx,p in zip(, curve.subdivisions(start_parameter=prev.parameter, end_parameter=d.parameter, amount =len (bads)+2)[1:-1]):
        #     pairs[bad_idx]((bad, p))
        # bads = []

        for j,prev in enumerate(ds[i-15:i]):
            if (b - prev.position).dot(prev.tangent) <= 0.01:
                bad_idxs.add(i)
                bad_idxs.add(i-15+j)
                # continue


        prev = d
        pairs.append((a, b))

    bad_idxs = sorted(bad_idxs, reverse=True)
    print(bad_idxs)
    while bad_idxs:
        good_idx1 = bad_idxs[-1] - 1
        assert (good_idx1 < len(pairs))
        good_idx2 = bad_idxs[-1]
        while bad_idxs and bad_idxs[-1] == good_idx2:
            good_idx2 += 1
            bad_idxs.pop()
            # print(good_idx2, bad_idxs)
        bad_idx_block = range(good_idx1+1, good_idx2)
        print(bad_idxs, bad_idx_block)
        for bad_idx,p in zip(bad_idx_block, subdivisions(pairs[good_idx1][1], pairs[good_idx2][1], amount =len (bad_idx_block)+2)[1:-1]):
            # print(bad_idx, p)
            pairs[bad_idx] = (pairs[bad_idx][0], p)

    return pairs



@run_if_changed
def gframe_snuggler():
    a = Wire(gframe_to_window_curve)
    b = a.offset2D(4)
    c = a @ Translate(Back*4)
    exclusion = Face(Wire(gframe_exclusion_curve, loop=True)).extrude(Back*10)
    # preview(a,b,c,exclusion, Wire(gframe_exclusion_curve).offset2D(-4, open=True))

    a = Wire(gframe_exclusion_curve)
    b = a.offset2D(-4, open=True)
    c = a @ Translate(Back*4)

    pairs = bsplinecurve_offset(gframe_exclusion_curve, gframe_assumed_plane.normal(), -4, start_x = -10, start_max_by="z", end_x = -15, end_min_by="z")
    a = [p[0] for p in pairs]
    b = [p[0]+Back*4 for p in pairs]
    c = [p[1] for p in pairs]
    def foo(p,q,r):
        ps = gframe_to_window_curve.intersections(Plane(p, Direction((p-q).cross(r-q)))).points
        if not ps:
            preview(p,q,r,gframe_to_window_curve, gframe_exclusion_curve)
        return min(ps, key=lambda t:p.distance(t))
    d = [ foo(p,q,r) for p,q,r in zip(a, b, c)]
    c = [window_extended_surface.intersections(Segment(p, q)).point() for p,q in zip(b, c)]
    faces = [
        Face(BSplineSurface([a, d], u=BSplineDimension(degree = 1))),
        Face(BSplineSurface([d, c], u=BSplineDimension(degree = 1))),
        Face(BSplineSurface([c, b], u=BSplineDimension(degree = 1))),
        Face(BSplineSurface([b, a], u=BSplineDimension(degree = 1))),
        Face(Wire([l[0] for l in [a,b,c]], loop=True)),
        Face(Wire([l[-1] for l in [a,b,c][::-1]], loop=True)),
    ]
    # preview(exclusion, faces)
    # s = Face(s).extrude(Front*10)
    s = Solid(Shell(faces))
    # preview(exclusion, s)
    # s = s.cut(Face(window_extended_surface).extrude(Front*20))
        #.cut(HalfSpace(gframe_reference_point, gframe_assumed_plane.normal()))
    # f = Loft(b, c, ruled=True)
    # preview(exclusion, s)
    # f = Loft([Wire(p, gframe_exclusion_curve.position(closest=p)@Translate(Back*4)) for e in b.edges() for p in ])
    # preview(exclusion, f)
    return s

@run_if_changed
def gframe_housing():
    plate = bsplinecurve_offset(gframe_to_window_curve, gframe_assumed_plane.normal(), 1, start_x = -16, start_min_by="z", end_x = -63, end_min_by="z", wrap=1)
    plate = BSplineSurface(plate, v=BSplineDimension(degree = 1))
    plate = Face(plate).extrude(Back*0.5)
    earpiece_stop = Vertex(earpiece_top_front_outer).extrude(Front*10).extrude(Left*0.2,Right*2).extrude(Down*4,Up*0.6).cut(HalfSpace(gframe_reference_point, gframe_assumed_plane.normal()))
    result = Compound(plate, gframe_snuggler, earpiece_stop)
    # save_STL("gframe_housing", result)
    # export("gframe_housing.stl", "gframe_housing_1.stl")
    return result
    # preview(gframe_to_window_curve,

@run_if_changed
def earpiece_strut():
    return Vertex(earpiece_top_front_outer).extrude(Down*earpiece_height).extrude(approx_earpieces_vec * (pframe_back_y - 4 - earpiece_top_front_outer[1]) / approx_earpieces_vec.length()).extrude(Left*0.4, Left*10).cut(Face(window_extended_surface).extrude(Front*100))

@run_if_changed
def prototype_3d_printable():
    earpiece_cut = approx_earpieces_outer_face.extrude(Right*10)
    # preview(pframe, window_solid, earpiece_cut)
    pframe2 = pframe.cut(earpiece_cut)
    window2 = window_solid.cut(earpiece_cut)
    # preview(pframe2, window2)
    left_half = Compound(pframe2, window2, gframe_housing, earpiece_strut)
    result = Compound(left_half, left_half @ Mirror(Right))
    save_STL("prototype_3d_printable", result)
    # export("prototype_3d_printable.stl", "prototype_3d_printable_4.stl")
    return result

# s = gframe_to_window_curve.subdivisions(max_length=1)
# frame_top = max(s, key=lambda f: f[2])
# frame_bottom = min(s, key=lambda f: -f[0])
# print(frame_bottom[0])

preview(face_to_seal_curve, approx_earpieces, approx_face_surface, gframe_to_window_curve, pframe_to_seal_curve, pframe_to_window_curve,
        # dpairs_to_surface(corresponding_curve_dpairs(pframe_to_window_curve.subdivisions(start_distance=0, end_x = hard_force_gframe_plane_x, end_min_by="z", output="derivatives",max_length=0.2), gframe_to_window_curve.subdivisions(start_closest = Point(0,0,9999), end_x = hard_force_gframe_plane_x, end_min_by="z", output="derivatives",max_length=0.01, wrap=1))),

        sweep_illustration_smooth, Compound(prototype_3d_printable.wires())
        )