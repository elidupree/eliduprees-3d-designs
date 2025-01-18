
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
        Direction(0, gframe_up[2], -gframe_up[1])
    )

@run_if_changed
def gframe_to_window_curve():
    return BSplineCurve([p.projected(gframe_assumed_plane) for p in gframe_to_window_legacy_curve.poles()], BSplineDimension(periodic=True))


hard_force_gframe_plane_x = -20
frame_to_seal_curve, pframe_to_window_curve = None, None
@run_if_changed
def pframe_to_window_curve():
    global frame_to_seal_curve, pframe_to_window_curve
    frame_to_seal_points = []
    pframe_to_window_points = []
    for d in face_to_seal_curve.subdivisions(output="derivatives", max_length=1):
        p = d.position
        # ignore the foibles of the face:
        cheek_level = smootherstep(p[2], 0, -1)
        normal = Direction(Point(cheek_level*smootherstep(p[0],-40,-20)*-40, 85, p[2]), p)
        cheek_smile_badness = cheek_level*min(smootherstep(p[0], -19, -40), smootherstep(p[0], -70, -50)) * 4
        leeway = 3 + cheek_smile_badness
        frame_to_seal = p + normal * leeway
        frame_to_seal_points.append(frame_to_seal)

        convexity_bulge = smootherstep(abs(p[2] + 5), 40, 0) * 4
        leeway = 8 + convexity_bulge
        force_gframe_plane = cheek_level*smootherstep(p[0], -35, hard_force_gframe_plane_x)
        gframe_plane_leeway = p.projected(onto = gframe_assumed_plane, by = normal).distance(p)
        leeway = Between(leeway, gframe_plane_leeway, force_gframe_plane)
        pframe_to_window = p + normal * leeway
        pframe_to_window_points.append(pframe_to_window)
    frame_to_seal_curve = BSplineCurve(frame_to_seal_points)
    pframe_to_window_curve = BSplineCurve(pframe_to_window_points)


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


preview(face_to_seal_curve, approx_earpieces, approx_face_surface, gframe_to_window_curve, frame_to_seal_curve, pframe_to_window_curve, dpairs_to_surface(corresponding_curve_dpairs(pframe_to_window_curve.subdivisions(start_distance=0, end_x = hard_force_gframe_plane_x, end_min_by="z", output="derivatives",max_length=0.2), gframe_to_window_curve.subdivisions(start_closest = Point(0,0,9999), end_x = hard_force_gframe_plane_x, end_min_by="z", output="derivatives",max_length=0.05, wrap=-1))))