"""

PRINTING NOTES:

The purple PETG is more viscous than my usual. I had to use slower printing speed, or it'd under-extrude.

Cura settings I customized for this:
* 30 print speed, 10 initial layer speed
* zero horizontal expansion
* 0.1 layer height, to be precise and get away with big overhangs
* a raft, with only 0.2mm air gap

I also saved the Cura project in the exports directory.

========================
     ASSEMBLY NOTES:
========================

Clean up the print using end-nippers, rotary tool abrasive spongy wheels to scrub off the coarse stringing, rotary tool sanding drum for fine smoothing. You particularly want to smooth down any pointy bits on the surfaces that might contact the flat parts, the face, or the glasses lens/frame.

Use pointy soldering iron tip to puncture the sewing-holes. Be careful not to let the heat bend the frame, or mess up the window-slots more than they already are.

Use pointy soldering iron tip to clean up the window-slots.

Prepare the unrolled rubber pieces:
* Painter's tape on both sides of a 0.35mm sheet of TPE that was sold as an exercise band.
* Pre-slit the holes on the paper printouts, so they will be easier to remove from a needle/thread later. (Probably not important, you could just tear it)
* Double-sided tape the paper printouts onto it (tape don't overlap the hole locations), and cut slightly oversized.
* Very lightly score the tape on the other side, to remove later so that the glue can adhere to the TPE in only the frame-contact area, and not the face-contact area.

Prepare the unrolled window:
* Painter's tape on both sides of a 0.3mm sheet of clear polycarbonate, sold as 0.010" polycarbonate.
* Cut 1mm undersized in most places, to compensate for the 0.6mm slot-wall and some imprecision/glue volume in the slot. Theoretically this leaves the sheet 0.6mm deep in a 1mm slot.
* Cut exact-sized in the places that don't have a slot. Measure the actual print for this, so you optimally align with any printing errors. (Not actually that important)
* Score the tape near the edges, to remove later so that the glue can adhere to the edges, but not most of the surface.

Sew the rubber to the frame:
* Have the soldering iron (and other print-fixing tools) on hand in case you need to fix any holes.
* Use thread that won't be melted by the soldering iron if you need to fix the print later.
* With your needle you can puncture the TPE at the locations marked by the paper printout.
* As you go, peel back some painter's tape (the full non-frame-side and half the frame-side, so they don't get sewn down) and lay down bits of shoe goo under the TPE.
* After each section, reapply the painter's tape to the non-frame side of the TPE to protect it for next step.

Glue the window to the frame:
* Have the soldering iron (and other print-fixing tools) on hand in case you need to fix anything.
* Set the edge of the window into the slots everywhere to make sure it works. Then remove it, and start applying shoe goo, reinserting it to the slots, and taping the window to the frame with more painter's tape.


=================================
     PROTOYTPE OBSERVATIONS:
=================================

The print-assembly process was way too much work, and the dimensions came out slightly inconsistent with the model. I've thought of a way to do it with flat sheets instead of the 3D print, which should be easier.

The prototype largely worked for its intent, but:
* it's annoying to blow my nose
* the TPE rubber eventually got wavy, making the seal worse unless I present to my face
* when pressed to my face with force, it always wants to slide up the nose, putting it in the wrong position. I want to block this motion; to block it, you would need a point on the face whose normal is downwards. Most such points allow a lot of skin movement, and thus make bad contact points. The one exception I've found is the concavities right next to the nose, in the eye socket. This seems like a viable place to make a contact-point; it could even replace glasses' built-in nosepieces. This is achievable as a separate 3D print that interfaces directly with the glasses frame, and can also interface with future airspace things if that's helpful.
* the forehead is a little too tall when I'm wearing the PAPR; it would probably be fine to lower it without much other changes. The sides also annoyingly catch on the PAPR; overall I would be happier if it was slimmed down.
* While wearing the PAPR, my eyes still dry out! I believe this is mainly a matter of not being sealed well enough; the gaps around the glasses definitely seem to be contributing here, so we should seal them in the next version (a jury-rigged plug was partially helpful). The bulk also may be helping force air go to through the things rather than around.
* The lenses stick out enough that they can be scratched by a flat surface; in the next version, I should make a lip that protrudes enough to set them down flat on their face.

"""

import math

from pyocct_system import *
from face_depthmap_loader import front_depthmap_sample_point, front_depthmap_sample_y, front_depthmap_normal, side_depthmap_sample_point, side_depthmap_sample_x, resample_curve_front, resample_curve_side, resample_point_frac, nose_grip_2_sample_point
from svg_utils import load_Inkscape_BSplineCurve
from unroll import UnrolledSurface, unroll_quad_strip

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
earpiece_thickness = 0.85
top_of_frame_z = earpiece_top_front_outer[2] + 10
approx_earpieces_vec = Vector(-10.5, 68, 0)

print (f"forehead y: {front_depthmap_sample_y(-28, 14)}")
print (f"near ear x: {side_depthmap_sample_x(pframe_back_y, earpiece_top_front_outer[2])}")


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
                smootherstep(p[0], -70, -50) * 4
                - smootherstep(p[0], -40, -19) * 1
                - smootherstep(p[0], -40, -39) * smootherstep(p[2], -43, -30) * 3
        )
        leeway = 3 + cheek_smile_badness
        return p + normal * leeway

    return faceish_curve(position_fn)

# preview(approx_face_surface, pframe_to_seal_curve)
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
        # print(already_determined, diff, max_accel)
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

    # print(forehead, cheek, cheek2, end)
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
    # print([p[0][0] for p in tight_segment1])
    # print([p[0][0] for p in tight_segment2])
    p2 = (Point(forehead[0][0]+0.08, 0.5), 10)
    # print(p2)
    interpolated_points = ([
        forehead,
        p2,
        # tightest(p2[0][0]+0.03, p2, 0.8),
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
    # print( [
    #     [a, control_point(a,b,da,db), control_point(b,a,db,da), b] for (a,da),(b,db) in pairs(interpolated_points)
    # ])
    result = [
        BezierCurve([a, control_point(a,b,da,db), control_point(b,a,db,da), b]) for (a,da),(b,db) in pairs(interpolated_points)
    ]
    # preview(Wire(result))
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
    # preview(window_surface, facecurve_surface)
    # preview (facecurve_surface.intersections(window_surface).curves)
    window_extended_surface = window_surface
    facecurve_extended_surface = facecurve_surface
    return facecurve_surface.intersections(window_surface).curve().reversed()
    # preview(manually_defined_fallback_slope_curve)
    # preview(surface)


# preview(window_extended_surface, pframe_to_seal_curve)

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
def pframe_to_seal_canonical_ds():
    return pframe_to_seal_curve.subdivisions(output="derivatives", max_length=1)

@run_if_changed
def pframe_to_seal_canonical_normals():
    return [Direction(face_to_seal_curve.position(parameter=d.parameter),d.position) for d in pframe_to_seal_canonical_ds]

@run_if_changed
def pframe_to_seal_canonical_inwards_directions():
    return [-facecurve_extended_surface.normal(closest = d.position) for d in pframe_to_seal_canonical_ds]

@run_if_changed
def pframe_to_window_corner_canonical_points():
    return [RayIsh(d.position, normal).intersections(window_extended_surface).point() for d, normal in zip(pframe_to_seal_canonical_ds, pframe_to_seal_canonical_normals)]

@run_if_changed
def pframe_to_window_inset_canonical_points():
    return [RayIsh(d.position+inwards*2.5, normal).intersections(window_extended_surface).point() for d, normal, inwards in zip(pframe_to_seal_canonical_ds, pframe_to_seal_canonical_normals, pframe_to_seal_canonical_inwards_directions)]

@run_if_changed
def pframe_faceward_not_obstructing_gframe_points():
    gframe_shadow = gframe_exclusion_curve.extrude(Back*20)

    def f(d, inwards):
        a = d.position
        a2 = a+inwards*4
        gframe_overlap = Segment(a,a2).intersections(gframe_shadow)
        if gframe_overlap.points:
            return gframe_overlap.point()
        return a2

    return [f(*t) for t in zip(pframe_to_seal_canonical_ds, pframe_to_seal_canonical_inwards_directions)]

assert (pframe_to_seal_curve.LastParameter() == face_to_seal_curve.LastParameter())
assert (pframe_to_seal_curve.FirstParameter() == face_to_seal_curve.FirstParameter())

pframe_window_slot_depth = 1.0
# The actual material I'm planning to use is 0.3mm thick. Technically maybe it should be a different thickness in the face-normal direction because of the different relative angles of the window surface, but those are all reasonably close to 90 degrees. Anyway, for ease of assembly, we make the slot significantly thicker than that and don't worry about the slight differences in angle, just fill the gap with sealant in the physical assembly.
pframe_window_slot_thickness = 0.5
pframe_window_slot_wall_thickness = 0.6
pframe_window_slot_slant = 0 #0.4

@run_if_changed
def pframe():
    sections = []
    # thickness = 4
    # overlap_to_cut_later = 0.25
    thicknesses = []
    for d, normal, inwards, window_corner, window_inset, faceward_point in zip(pframe_to_seal_canonical_ds, pframe_to_seal_canonical_normals, pframe_to_seal_canonical_inwards_directions, pframe_to_window_corner_canonical_points, pframe_to_window_inset_canonical_points, pframe_faceward_not_obstructing_gframe_points):
        window_inwards = Direction(window_corner, window_inset)
        w0 = window_inset
        w1 = window_corner + window_inwards*pframe_window_slot_wall_thickness
        w2 = w1 + normal*pframe_window_slot_thickness
        w3 = w2 + window_inwards*pframe_window_slot_depth + normal*pframe_window_slot_slant
        w4 = w3 + normal*(pframe_window_slot_wall_thickness - pframe_window_slot_slant)
        w5 = window_corner + normal*(pframe_window_slot_thickness+pframe_window_slot_wall_thickness)
        thicknesses.append(d.position.distance(window_corner))
        sections.append(Wire([
            d.position,
            faceward_point,
            window_inset,
            w1, w2, w3, w4, w5
        ], loop=True))
    print(min(thicknesses))
    # preview(sections)
    return Loft(sections, solid=True)

@run_if_changed
def rubber_holding_nub():
    ps = [
        Point(1.1, 0),
        Point(0.8, 0.5),
        Point(0.55, 0.5),
        Point(0.35, 0.5),
        Point(0.35, 0.35),
        Point(0.30, 0.35),
        Point(0, 0.35),
        Point(0, 0.40),
        Point(0, 0.45),
        Point(-0.2, 0.45),
    ]
    solid = Face(BSplineCurve(ps + [p @ Mirror(Back) for p in ps[::-1]])).extrude(Down*1,Up*0.35)
    return solid.cut(HalfSpace(Point(0,0,-0.35), Direction(0.5,0,-1)))
# preview(rubber_holding_nub, Vertex(Origin).extrude(Back*1), Vertex(Point(0.35,0,0)).extrude(Back*1), Vertex(Point(0.7,0,0)).extrude(Back*1))

@run_if_changed
def hole_for_rubber_holding_staple():
    return Face(Circle(Axes(Origin, Right), 0.2)).extrude(Right*0.5, centered=True)
    # return Vertex(Origin).extrude(Up*0.4, centered=True).extrude(Back*0.4, centered=True).extrude(Right*0.3, centered=True)

# @run_if_changed
# def pframe():
#     # preview(pframe_extended)
#     return pframe_extended.cut(Face(window_extended_surface).extrude(Front*100))
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
        b = a + (d.tangent @ Rotate(normal, Degrees(90)))*offset(d)
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
    
    def bigness(p):
        base = 3 + ((p[2] + 24)/42)
        # frac = max(0, (p - Point(-30,0,0)).dot(Direction(1,0,-0.2)) / 22)
        # print(frac)
        frac = 0
        return base * (1 - (frac**2)*0.75)
    pairs = bsplinecurve_offset(gframe_exclusion_curve, gframe_assumed_plane.normal(), lambda d: -bigness(d.position), start_x = -16, start_max_by="z", end_x = -15, end_min_by="z")
    a = [p[0] for p in pairs]
    b = [p[0]+Back*bigness(p[0]) for p in pairs]
    c = [p[1] for p in pairs]
    # preview(BSplineCurve(a),BSplineCurve(b),BSplineCurve(c))
    def foo(p,q,r):
        ps = gframe_to_window_curve.intersections(Plane(p, Direction((p-q).cross(r-q)))).points
        if not ps:
            preview(p,q,r,gframe_to_window_curve, gframe_exclusion_curve)
        return min(ps, key=lambda t:p.distance(t))
    d = [ foo(p,q,r) for p,q,r in zip(a, b, c)]
    c = [window_extended_surface.intersections(Segment(p, q)).point() for p,q in zip(b, c)]
    # s = Loft([Wire([a,d,c,b], loop = True) for a,b,c,d in zip(a,b,c,d)], solid=True)
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
def gframe_window_gripper():
    sections = []
    gcurve = BSplineCurve([g for g,p in window_extended_sections], BSplineDimension(periodic=True))
    pcurve = BSplineCurve([p for g,p in window_extended_sections], BSplineDimension(periodic=True))
    for gd in gcurve.subdivisions(output = "derivatives", start_x = -16, start_max_by="z", end_x = -50, end_min_by="z", max_length = 0.2, wrap=0):
        g = gd.position
        p = pcurve.position(parameter = gd.parameter)
        dir = Direction((p - g).projected_perpendicular(gd.tangent))
        window_normal = dir.cross(gd.tangent)

        b = g + window_normal*(pframe_window_slot_thickness + pframe_window_slot_wall_thickness)
        c = b + dir*(pframe_window_slot_depth + pframe_window_slot_wall_thickness)
        d = c - window_normal*(pframe_window_slot_wall_thickness - pframe_window_slot_slant)
        e = d - dir*pframe_window_slot_depth - window_normal*pframe_window_slot_slant
        f = e - window_normal*pframe_window_slot_thickness
        sections.append(Wire([g,b,c,d,e,f], loop = True))
    return Loft(sections, solid=True)


def gframe_snap(x):
    d = gframe_exclusion_curve.derivatives(x=x, max_by="z")
    inwards = d.tangent @ Rotate(gframe_assumed_plane.normal(), Degrees(90))
    a=d.position
    b=a+Back*3.5
    c=b+inwards*1.0
    e=c+Back*0.5
    f=e+Back*0.5
    g=f-inwards*1.4+Back*0.8
    return Edge(BSplineCurve([a,b,c,e,f,g])).extrude(-inwards*1).extrude(d.tangent*5, centered=True)


@run_if_changed
def gframe_housing():
    plate = bsplinecurve_offset(gframe_to_window_curve, gframe_assumed_plane.normal(), lambda p: 1, start_x = -19, start_max_by="z", end_x = -63, end_min_by="z", wrap=0)
    plate = BSplineSurface(plate, v=BSplineDimension(degree = 1))
    plate = Face(plate).extrude(Back*0.5)
    earpiece_stop = Vertex(earpiece_top_front_outer).extrude(Front*10).extrude(Left*0.2,Right*2).extrude(Down*4,Up*0.6).cut(HalfSpace(gframe_reference_point, gframe_assumed_plane.normal()))
    # preview(plate, gframe_snuggler, earpiece_stop, gframe_window_gripper)
    result = Compound(plate, gframe_snuggler, earpiece_stop, gframe_window_gripper, gframe_snap(-20), gframe_snap(-55))
    # save_STL("gframe_housing", result)
    # export("gframe_housing.stl", "gframe_housing_1.stl")
    return result
    # preview(gframe_to_window_curve,


window_split_top_z = earpiece_top_front_outer[2] - earpiece_height/2 + pframe_window_slot_wall_thickness/2
window_split_bottom_z = window_split_top_z - pframe_window_slot_thickness
@run_if_changed
def earpiece_strut():
    # mirror = Mirror(Axes(earpiece_top_front_outer + Down*earpiece_height/2, Up))
    def section(y):
        a = earpiece_top_front_outer + approx_earpieces_vec * y / approx_earpieces_vec[1]
        def points(a, inwards):
            b = RayIsh(a, Left).intersections(window_extended_surface).point()
            c = b + inwards*(earpiece_height - pframe_window_slot_wall_thickness)/2
            d = c + Left*pframe_window_slot_thickness
            e = d - inwards*pframe_window_slot_depth
            f = e + Left*pframe_window_slot_wall_thickness
            return [a,b,c,d,e,f]
        return Wire(points(a, Down) + points(a + Down*earpiece_height, Up)[::-1], loop = True)

    sections = [
        section(y) for y in subdivisions(-2.3, (pframe_back_y - 5.5 - earpiece_top_front_outer[1]), max_length=2.5)
    ]

    return Loft(sections, solid=True)

# preview(earpiece_strut, pframe, gframe_housing)

@run_if_changed
def unrolled_shield():
    # nose_split = approx_nose_surface.intersections(gframe_assumed_plane).curve().position(x=0)
    # preview(Compound([Edge(a@Translate(Front*i/50), b@Translate(Front*i/50)) for i,(a,b) in enumerate(window_sections)]))
    print(len(window_sections))
    sections = []
    def do_section(cutoff, direction, section):
        is_cut = [section[0][0] < -40 and (p - cutoff).dot(direction) > 0 for p in section]
        print(is_cut)
        if is_cut == [False, False]:
            sections.append(section)
            return "included"
        elif not all(is_cut):
            a,b = section
            mid = a.projected(Plane(cutoff, direction), by=Direction(a, b))
            if is_cut[0]:
                sections.append([mid, b])
            else:
                sections.append([a, mid])
            return "split"
        return "excluded"

    split_idx = min(range(len(window_sections)), key=lambda i: window_sections[i][1].distance(Point(-999,0,999)))
    for section in window_sections[split_idx:]:
        do_section(Point(0, 0, window_split_bottom_z), Up, section)
    for section in window_sections:
        if do_section(Point(0, 0, window_split_top_z), Down, section) == "excluded":
            break
    # preview(Compound(Edge(*edge) for edge in sections))
    result = unroll_quad_strip(sections).unrolled_wire()

    save_inkscape_svg("unrolled_window", result)
    # export("unrolled_window.svg", "unrolled_window_1.svg")
    return result


seal_holes = None
@run_if_changed
def unrolled_seal():
    endpoints = [
        0,
        face_to_seal_curve.parameter(z = earpiece_top_front_outer[2]-earpiece_height/2),
        face_to_seal_curve.LastParameter(),
    ]
    endpoint_distances = [face_to_seal_curve.distance(parameter = p) for p in endpoints]
    pieces = []
    holes = []
    hole_inset = 1.7
    for a,b in pairs(endpoint_distances):
        seal_hole_distances = subdivisions(a+hole_inset, b-hole_inset, max_length=5)
        seal_hole_locations = []
        for dist in seal_hole_distances:
            d = face_to_seal_curve.derivatives(distance=dist)
            p = d.position
            p2 = pframe_to_seal_curve.position(parameter=d.parameter)
            normal = Direction(p, p2)
            outwards = Direction(d.tangent.cross(normal))
            w = RayIsh(p, normal).intersections(window_extended_surface).point()
            hole_location = w + normal*(pframe_window_slot_thickness+pframe_window_slot_wall_thickness - hole_inset)
            seal_hole_locations.append(hole_location)
            try:
                w2 = RayIsh(p - outwards*1, normal).intersections(window_extended_surface).point()
            except RuntimeError:
                preview(p, RayIsh(p - outwards*5, normal, 5), window_extended_surface)
            window_outwards = Direction(w2, w)
            # "outwards" makes the shortest hole,
            # but don't allow it to go closer to the window
            if window_outwards.dot(normal) > outwards.dot(normal):
                dim1 = window_outwards
            else:
                dim1 = outwards
            dim2 = Direction(dim1.cross(gframe_assumed_plane.normal()))
            dim3 = Direction(dim1.cross(dim2))
            # print(d.tangent.dot(normal))
            holes.append(
                # rubber_holding_nub
                hole_for_rubber_holding_staple
                @ Transform(dim1, dim2, dim3, hole_location))

        latest_edge = None
        next_seal_hole_dist_idx = 0
        unrolled_seal_hole_locations = []
        for d in face_to_seal_curve.subdivisions(output="derivatives", start_distance=a, end_distance=b, max_length=1):
            p = d.position
            p2 = pframe_to_seal_curve.position(parameter=d.parameter)
            normal = Direction(p, p2)
            w = RayIsh(p, normal).intersections(window_extended_surface).point()
            beyond_w = w + normal*(pframe_window_slot_thickness+pframe_window_slot_wall_thickness)
            section = [p, beyond_w]
            
            if latest_edge is None:
                piece = UnrolledSurface(*section)
                latest_edge = piece.edges[0]
            else:
                if next_seal_hole_dist_idx < len(seal_hole_distances):
                    next_seal_hole_dist = seal_hole_distances[next_seal_hole_dist_idx]
                    if next_seal_hole_dist < face_to_seal_curve.distance(parameter=d.parameter):
                        unrolled_seal_hole_locations.append(latest_edge.relative_point(seal_hole_locations[next_seal_hole_dist_idx]))
                        next_seal_hole_dist_idx += 1
                latest_edge = piece.extend_edge_to_quad(latest_edge, *section)[1]
        piece_wires = [piece.unrolled_wire()] + [Wire(Circle(Axes(p.u, Up), 0.2)) for p in unrolled_seal_hole_locations]
        pieces.append([w @ Translate(Right*len(pieces)*50) for w in piece_wires])
        
    # sections[0] = sections[0][::-1][:-1] + sections[0]
    global seal_holes
    seal_holes = Compound(holes)
    # preview(pieces)
    save_inkscape_svg("unrolled_seal", pieces, max_length=0.05)
    export("unrolled_seal.svg", "unrolled_seal_2.svg")
    return pieces


@run_if_changed
def pframe_with_snap_in_earpiece_slots():
    leeway = 0.1
    pinch = 0 #0.12
    a = earpiece_top_front_outer + Up*leeway
    b = a + Right*(earpiece_thickness/2 + leeway)
    b2 = b + Right*(earpiece_thickness/2 + leeway)
    c = b2 + Down*pinch
    d = c+Right*0.2
    e = d+Right*0.2
    f = e + Up*pinch
    g = f+Right*2
    h = g+Right*10
    ps = [a,b,b2,c,d,e,f,g,h]
    mirror = Mirror(Axes(earpiece_top_front_outer + Down*earpiece_height/2, Up))
    earpiece_cut = Face(Wire(
        BSplineCurve(ps + [p @ mirror for p in reversed(ps)]),
        loop=True
    )).extrude(approx_earpieces_vec)
    # print("hmm...")
    # preview(seal_holes)
    return pframe.cut([earpiece_cut, seal_holes])



@run_if_changed
def prototype_3d_printable():
    left_half = Compound(pframe_with_snap_in_earpiece_slots, window_solid, gframe_housing, earpiece_strut)
    result = Compound(left_half, left_half @ Mirror(Right))
    # save_STL("prototype_3d_printable", result, linear_deflection=0.03)
    # export("prototype_3d_printable.stl", "prototype_3d_printable_5.stl")
    return result



def wire_subdivisions(wire, **kwargs):
    results = []
    start_lengths = [0]
    start_lengths_on_curves = []
    curves = list(oriented_edge_curves(wire))
    for c, a, b in curves:
        if a > b:
            b,a=a,b
        length = c.length()
        start_lengths.append(start_lengths[-1] + c.length(a,b))
        start_lengths_on_curves.append(c.length(0, a))

    for d in subdivisions(0, start_lengths[-1], **kwargs):
        for s, (c, a, b), sc in zip(start_lengths, curves, start_lengths_on_curves):
            # print(d, s, a, b)
            if d > s:
                if a < b:
                    results.append((d, c.derivatives(distance=sc + (d-s)), False))
                else:
                    results.append((d, c.derivatives(distance=sc - (d-s)), True))
                break
    return start_lengths[-1], results

def support_for_wire(wire):
    length, points = wire_subdivisions(wire, max_length=0.5)
    periods = math.ceil(length / 30)
    build_reference_point = gframe_reference_point + gframe_assumed_plane.normal()*(pframe_window_slot_thickness+pframe_window_slot_wall_thickness)
    build_plane = Plane(build_reference_point, gframe_assumed_plane.normal())
    sections = []
    thickness = 0.5
    max_slope = 0.3
    prev_sideways = None
    bottom_edge = []
    for dist,derivs,reversed in points:
        p = derivs.position
        height = (build_reference_point - p).dot(gframe_assumed_plane.normal())
        # tiny separation to ease breaking-off later
        if height > 0.5:
            p = p + gframe_assumed_plane.normal() * min(0.1, height - 0.5)
        height2 = (build_reference_point - p).dot(gframe_assumed_plane.normal())
        assert 0 <= height2 <= height
        wiggle_factor = min(3, height) * max_slope
        assert wiggle_factor >= 0
        wiggledness = math.sin(periods * dist * math.tau / length)*wiggle_factor
        # print(wiggledness )
        sideways = Direction(derivs.tangent.cross(gframe_assumed_plane.normal()))
        if reversed:
            sideways = -sideways
        if prev_sideways is not None:
            assert prev_sideways.dot(sideways) > 0
        prev_sideways = sideways
        p2 = p.projected(build_plane) + sideways*wiggledness
        sections.append(Wire([
            p + sideways*thickness/2,
            p2 + sideways*thickness/2,
            p2 - sideways*thickness/2,
            p - sideways*thickness/2,
        ], loop = True))
        if height > 0.5:
            bottom_edge.append(p2)
    wall = Loft (sections, solid = True, ruled=True)
    # preview(Compound(sections[::2]), Loft (sections, solid = True, ruled=True))
    raft = Face(Wire(bottom_edge).offset2d(1.5)).extrude(Up*0.2)
    # return wall
    return Compound(wall, raft)


@run_if_changed
def frame_outer_support():
    es = sorted(pframe.edges(), key = lambda e: e.bounds().min()[0])
    # preview(pframe, es[2])
    return support_for_wire(Wire(es[2]))
@run_if_changed
def frame_inner_support():
    pieces = []
    es = sorted(gframe_snuggler.edges(), key = lambda e: e.bounds().min()[2])
    top = es[0].cut(HalfSpace(Point(0, 0, -10), Down)).cut(HalfSpace(Point(-52, 0, 0), Left))
    bot = es[0].cut(HalfSpace(Point(0, 0, -10), Up)).cut(HalfSpace(Point(-55, 0, 0), Left)).cut(HalfSpace(Point(-21, 0, 0), Right))
    # .intersection(Vertex(-30, -10, -10).extrude(Left*20).extrude(Down*50).extrude(Back*20))
    pieces.append(support_for_wire(top))
    pieces.append(support_for_wire(bot))

    # preview(gframe_snuggler, es[2])
    # top = es[2].cut(HalfSpace(Point(0, 0, -10), Down)).cut(HalfSpace(Point(-52, 0, 0), Left))
    bot = es[2].cut(HalfSpace(Point(0, 0, -10), Up)).cut(HalfSpace(Point(-45, 0, 0), Left)).cut(HalfSpace(Point(-21, 0, 0), Right))
    # pieces.append(support_for_wire(top))
    pieces.append(support_for_wire(bot))
    # preview(gframe_snuggler, pieces)
    # preview(gframe_snuggler, bot, support_for_wire(bot))


    es2 = sorted(gframe_window_gripper.edges(), key = lambda e: e.bounds().min()[0])
    side = es2[2].cut(HalfSpace(Point(-58,0,0), Direction(1, 0, -0.1)))
    pieces.append(support_for_wire(side))
    return Compound(pieces)

@run_if_changed
def frame_3d_printable():
    left_half = Compound(pframe_with_snap_in_earpiece_slots, gframe_housing, earpiece_strut, frame_outer_support, frame_inner_support)
    result = Compound(left_half, left_half @ Mirror(Right))
    # save_STL("frame_3d_printable", result, linear_deflection=0.03)
    # export("frame_3d_printable.stl", "frame_3d_printable_3.stl")
    return result

@run_if_changed
def nose_support():
    front_curve = front_curve_from_layout_file("nose_support") @ Translate(Front*10)
    upish = Left.cross(gframe_assumed_plane.normal())
    def f(x,z):
        n =nose_grip_2_sample_point(x,z)
        if n is None:
          return Point(x, -20,  z)
        return n
    relevant_face_surface = BSplineSurface([[f(x,z) for z in subdivisions(-15, 15, max_length=0.5)] for x in subdivisions(-22, 22, max_length=0.5)])
    # preview(relevant_face_surface)
    # relevant_face_surface_old = BSplineSurface([[front_depthmap_sample_point(x,z,1) for z in subdivisions(-15, 15, max_length=0.5)] for x in subdivisions(-22, 22, max_length=0.5)])
    # preview(relevant_face_surface, relevant_face_surface_old)
    # preview(relevant_face_surface, approx_face_surface)
    gframe_offset = Vector(0,-4,-5)
    front_ref = Point(0,0,3.6).projected(onto=gframe_assumed_plane, by=Front) @ Translate(gframe_offset)

    contact_surface = Intersection(Face(Wire(front_curve, front_curve.reversed() @ Mirror(Left))).extrude(Back*100), Face(relevant_face_surface))
    contact_plate = Compound(
        contact_surface.extrude(Front*2),
        Intersection(contact_surface, HalfSpace(Origin, Left)).extrude(Front*2 + Left*1),
        Intersection(contact_surface, HalfSpace(Origin, Right)).extrude(Front*2 + Right*1),
    )
    
    front_surface = Vertex(front_ref).extrude(Left*18, centered=True).extrude(upish*2.5, -upish*3)
    gframe_exclusion = Face(Wire(gframe_exclusion_curve @ Translate(gframe_offset), loop=True))
    gframe_exclusion = Compound(gframe_exclusion, gframe_exclusion @ Mirror(Left))
    gframe_exclusion = Compound(gframe_exclusion @ Translate(upish*0.1), gframe_exclusion @ Translate(-upish*0.1))
    front_surface = front_surface.cut(gframe_exclusion)
    front_surface = front_surface.cut(Vertex(front_ref).extrude(Left*2.5, centered=True).extrude(upish*10, centered=True))
    block = front_surface.extrude(Back*100)
    block = Intersection(block, contact_surface.extrude(Front*100))
    
    result=Compound(contact_plate, block)
    save_STL("nose_support", result)
    export("nose_support.stl", "nose_support_4.stl")

    preview(relevant_face_surface, front_curve, resample_curve_front(front_curve, max_length=0.2), front_ref, contact_plate, block, gframe_exclusion_curve @ Translate(gframe_offset), approx_face_surface @ Translate(Back*2))

@run_if_changed
def blue_light_layout_scratchpad():
    x = -67/2
    highest_view_slope_with_relaxed_brows = 2/3
    highest_view_direction_with_relaxed_brows = Direction(0, -1, highest_view_slope_with_relaxed_brows)
    highest_view_slope_with_raised_brows = 1.1
    highest_view_direction_with_raised_brows = Direction(0, -1, highest_view_slope_with_raised_brows)
    brow_raise_distance = 5
    eye_to_brow_y = brow_raise_distance / (highest_view_slope_with_raised_brows - highest_view_slope_with_relaxed_brows)
    brow_y = 6
    eye_y = brow_y + eye_to_brow_y
    print(eye_to_brow_y)
    # print(front_depthmap_normal(x, 0))
    # limiting_brow_point_z = max(subdivisions(8,20,max_length=0.1), key=lambda z: (front_depthmap_normal(x, z).dot(Direction(0, -highest_view_slope_with_relaxed_brows, -1))))
    # limiting_brow_point = front_depthmap_sample_point(x, limiting_brow_point_z)
    relaxed_brow_point = min([front_depthmap_sample_point(x, z) for z in subdivisions(0,15,max_length=0.1)], key=lambda p: abs(p[1] - brow_y))
    print(relaxed_brow_point)
    eye_point = Point(x, eye_y, relaxed_brow_point[2] - highest_view_slope_with_relaxed_brows*eye_to_brow_y)
    highest_view_ray_with_relaxed_brows = RayIsh(eye_point, highest_view_direction_with_relaxed_brows, length=70)
    highest_view_ray_with_raised_brows = RayIsh(eye_point, highest_view_direction_with_raised_brows, length=70)
    lowest_invisible_point = highest_view_ray_with_raised_brows.intersections(approx_face_surface).point()
    lowest_permitted_invisible_point = min([p for p in [front_depthmap_sample_point(x, z) + Front*3 for z in subdivisions(0,30,max_length=0.1)] if (p - eye_point).projected_perpendicular(highest_view_direction_with_raised_brows)[2] > 0], key=lambda p: p[2])
    # lowest_invisible_point[2]
    gframe_top = Point(x, -6, 15)

    d1 = gframe_top-lowest_permitted_invisible_point
    a1 = atan2(d1[2], d1[1])

    d2 = gframe_top-eye_point
    a2 = atan2(d2[2], d2[1])

    a3 = Radians((a1.radians + a2.radians) / 2)
    mirror_normal = Front @ Rotate(Left, a3)
    mirror_tangent = Up @ Rotate(Left, a3)
    mirror = RayIsh(gframe_top, mirror_tangent, length=30)
    save_inkscape_svg("blue_light_layout_scratchpad", [Edge(e) @ Transform(Up, Right, Back) for e in [mirror, highest_view_ray_with_relaxed_brows, highest_view_ray_with_raised_brows, BSplineCurve([eye_point, gframe_top, lowest_permitted_invisible_point], BSplineDimension(degree=1)), approx_face_surface.intersections(Segment(Point(x, 100, 0), Point(x, -100, 0)).extrude(Up*30)).curve()]], max_length=0.05)
    export("blue_light_layout_scratchpad.svg", "blue_light_layout_scratchpad.svg")


    preview(approx_face_surface, gframe_to_window_curve, highest_view_ray_with_relaxed_brows, highest_view_ray_with_raised_brows, lowest_invisible_point, lowest_permitted_invisible_point, gframe_top, mirror)
# preview(unrolled_seal)
# s = gframe_to_window_curve.subdivisions(max_length=1)
# frame_top = max(s, key=lambda f: f[2])
# frame_bottom = min(s, key=lambda f: -f[0])
# print(frame_bottom[0])


preview(prototype_3d_printable)
preview(frame_3d_printable, approx_face_surface, approx_earpieces)
preview(face_to_seal_curve, approx_earpieces, approx_face_surface, gframe_to_window_curve, pframe_to_seal_curve, pframe_to_window_curve,
        # dpairs_to_surface(corresponding_curve_dpairs(pframe_to_window_curve.subdivisions(start_distance=0, end_x = hard_force_gframe_plane_x, end_min_by="z", output="derivatives",max_length=0.2), gframe_to_window_curve.subdivisions(start_closest = Point(0,0,9999), end_x = hard_force_gframe_plane_x, end_min_by="z", output="derivatives",max_length=0.01, wrap=1))),

        sweep_illustration_smooth, Compound(prototype_3d_printable.wires())
        )