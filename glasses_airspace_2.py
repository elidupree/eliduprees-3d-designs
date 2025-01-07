"""
Overall design:

* A thin sheet of clear plastic (the "window") is cut and flexed into a curved surface, which bridges between "close to my face" and "close to the glasses frame".
* At the temple, this is simple.
* At the cheek and forehead, face movements would disturb the glasses if the plastic touched the face. We make the plastic loose to the face, and join the last gap with a thin rubbery sheet (the "seal"). Together with the window, these form the "shield" (full barrier from glasses lens/frame to face).
* At the nose...
  * A certain region is "non-vision angles" anyway. In this region...:
    * the seal ends, while the window sweeps closer and becomes the whole shield (it also forms the end-edge of the seal), at a triple point we can call the "beside-nose-point"
    * right afterwards, the "shield-to-face curve" makes a tight turn to sweep out in *front* of the glasses nosepiece, thereby saving us from the tricky thought of sealing around the nosepiece and/or making it comfortable there
    * once it reaches the exact center of the face, it joins the other lens's curve, allowing the two windows to merge into one object
* The geometry of the 4-way meeting between windows has some contraints.
  * We must assume that each point of the curve within the x=0 plane has dV/dx = (1,0,0).
     * If there are any points _above_ of the top of the glasses frame that have nonzero curvature along this curve, then they "infect" the entire left and right with being a unified generalized cylinder on the left-right axis, which prevents them from forming a complete shield.
     * If there are any points _below_ the top of the glasses frame that have nonzero curvature along this curve, then their location along this curve is fully constrained by the locations of the shield-to-glasses-frame joint, and above them, there must be a *planar* triangle in order to piecewise-combine it with good shapes for the side windows. This is viable (note also that it becomes unconstrained when it runs into the nose, thereby cutting the left-right lines). It also has more global rigidity by being rigid in the left-right direction, which is probably favorable. I don't like the nonsmoothness of a cylinder-to-plane joint though, it feels like it might cause distortion.
     * If there's any nonzero curvature perpendicular to this curve, then THIS curve is forced to be a straight line, and cannot escape its constraints until it forms a straight line (forehead - glasses frame - nose) and then is cut by the glasses frame. This seems surprisingly viable if it forms a generalized cone with focal point inside the nose - the "cut" position dictates a single line and slice of the forehead which must be on conic lines, but all lines in between have leeway to make small adjustments to the focal point for smoothness, if they even need to. But what if the optimal cone just ends up being near-planar anyway?
  * I think I like that second approach best. So:
    * There's a single dictated line that's straight horizontal where the nose-break happens; call it the "nose-break line"
    * Down from there, you sweep over a very small amount of glasses frame while sweeping all the way to the beside-nose-point. Any path along the nose will do as long as it dodges the nosepiece. Going pretty tightly around it feels fine.
    * Frame-endpoints don't technically need to be closest-points-on-frame to the corresponding other endpoints of the window, but doing otherwise just uses more material, which maybe worsens optics; one could later check if adjusting this optimizes any angles...
"""

import math

from pyocct_system import *
from face_depthmap_loader import depthmap_sample_smoothed
from svg_utils import load_Inkscape_BSplineCurve

initialize_pyocct_system()

def depthmap_sample_y(x, z):
    return Between(depthmap_sample_smoothed(x, z, 2), depthmap_sample_smoothed(-x, z, 2))
def depthmap_sample_point(x, z):
    return Point(x, depthmap_sample_y(x, z), z)

@run_if_changed
def approx_face_surface():
    return BSplineSurface([[depthmap_sample_point(x,z) for z in range(-42, 31, 2)] for x in range(-64,65,2)])

@run_if_changed
def frame_to_window_curve():
  # For now, shamelessly render a computed output from the previous legacy code:
  return read_brep ("glasses_frame_to_window_curve.brep").curve()[0]


@run_if_changed
def nose_break_point():
    a,b = 0, -20
    best = None
    while a - b > 0.01:
        z = Between(a, b)
        p = frame_to_window_curve.position(z = z, min_by=lambda p: -p[0])
        if depthmap_sample_y(0, z) < p[1]:
            b = z
            best = p
        else:
            a = z

    return best


eyeball_radius = 12
eyeball_center = depthmap_sample_point(-33.5, -2) + Back*eyeball_radius


@run_if_changed
def frame_eye_lasers():
    return Compound([Edge(eyeball_center, Between(eyeball_center, frame_to_window_curve.position(distance=d), 1.2)) for d in subdivisions(0, frame_to_window_curve.length(), max_length = 10)[:-1]])


@run_if_changed
def window_pairs():
    main_curve = load_Inkscape_BSplineCurve("glasses_airspace_layout.svg", "window_to_seal") @ Mirror(Right) @ Rotate(Left, Degrees(90))

    frame_tangent = frame_to_window_curve.derivatives(closest=nose_break_point).tangent
    nose_flat_normal = Direction((frame_tangent*1).projected_perpendicular(Left) @ Rotate(Left, degrees=90))
    nose_flat_curve = approx_face_surface.intersections(Plane(nose_break_point, nose_flat_normal)).curve()
    a = nose_flat_curve.distance(x = 0)
    b = nose_flat_curve.distance(z = -15, min_by = lambda p: p[0])
    nose_flat_curve_correction = nose_break_point[2] - nose_flat_curve.position(distance=a)[2]
    # print(nose_flat_curve_correction)
    nose_flat_curve_points = [nose_flat_curve.position(distance=d) + Up*nose_flat_curve_correction for d in subdivisions(a,b, max_length=1)]

    main_curve_points = [main_curve.position(distance=d) for d in subdivisions(main_curve.length(), 0, max_length=1)]

    beside_nose_point = Point(-20, 0, -25)
    def faceish_point(p):
        face = depthmap_sample_point(p[0], p[2])
        cheek_badness = (face - beside_nose_point).dot(Direction(-0.15,0,-1)) / 16
        brow_badness = 0 if p[2] < 0 else (60-abs(p[0]))/10
        if cheek_badness <= 0 and brow_badness <= 0:
            return face
        else:
            ishness = smootherstep(max(cheek_badness, brow_badness))
            normal = Between(Front, approx_face_surface.normal(closest=face), smootherstep(p[0], -24, -40)*0.5)
            return face + normal*ishness*6

    all_points = [faceish_point(p) for p in nose_flat_curve_points + main_curve_points]

    all_pairs = [(p, frame_to_window_curve.position(closest=p)) for p in all_points]
    first_normal_index = 0
    for i, (p, f) in enumerate(all_pairs):
        if f[2] < nose_break_point[2] - 5:
            first_normal_index = i
            break

    frame_top = max([p[1] for p in all_pairs], key=lambda f: abs(frame_to_window_curve.derivatives(closest=f).tangent[0]) if f[2] > 0 else 0)
    a = frame_to_window_curve.distance(closest = nose_break_point)
    b = frame_to_window_curve.distance(closest = frame_top)

    def alignedness(d):
        f = d.position
        w = all_points[-1]
        f_tangent = d.tangent
        if f_tangent[0] < Direction(f, w)[0]:
            return 0
        triangle_normal = Direction(Left.cross(f - w))
        # move_f_normal = Direction(f_tangent.cross(f - w))
        below_triangle_normal = Direction(Right.cross(f_tangent))
        # if p:
        #     print(triangle_normal, move_w_normal, move_f_normal)
        return abs(below_triangle_normal.dot(triangle_normal))
            # max(abs(move_f_normal.dot(triangle_normal))


    ds = [frame_to_window_curve.derivatives(distance=d) for d in subdivisions(a, b, max_length = 0.2)]
    best_triangle_bottom = max(ds, key=alignedness)
    # print(best_triangle_bottom.position)
    # print(alignedness(best_triangle_bottom))
    # preview(Compound([Edge(*p) for p in all_pairs]),
    #         best_triangle_bottom.position,
    #         frame_top,
    #         Compound([Edge(d.position, d.position + Front*(1+alignedness(d)*20)) for d in ds]))
    # print(frame_top)
    # triangle_hecker = Direction(Left.cross(all_points[-1] - best_triangle_bottom.position).cross(all_points[-1] - best_triangle_bottom.position))
    # print(triangle_hecker)
    last_normal_index = None
    # for i, (w, f) in reversed(list(enumerate(all_pairs))):
    #     hecked = frame_to_window_curve.position(on=Plane(w, triangle_hecker), min_by=lambda p: p.distance(w))
    #     if hecked[0] > f[0]:
    #         all_pairs[i] = (w, hecked)
    #     else:
    #         last_normal_index = i
    #         break
    a = frame_to_window_curve.distance(closest = best_triangle_bottom.position)
    # b = frame_to_window_curve.distance(closest = all_pairs[last_normal_index][1])
    d = a - 0.001
    for i, (w, f) in reversed(list(enumerate(all_pairs))):
        hecked = frame_to_window_curve.position(distance=d)
        if hecked[0] < f[0]:
            all_pairs[i] = (w, hecked)
        else:
            break
        d -= 0.2

    a = frame_to_window_curve.distance(closest = best_triangle_bottom.position)
    b = frame_to_window_curve.distance(closest = nose_break_point)
    for d in subdivisions(a+0.001, b, max_length = 1)[:-1]:
        f = frame_to_window_curve.position(distance=d)
        all_pairs.append((f.projected(onto=Plane(Origin, Right)), f))

    a = frame_to_window_curve.distance(closest = nose_break_point)
    b = frame_to_window_curve.distance(closest = all_pairs[first_normal_index][1])
    for i,d in enumerate(subdivisions(a, b, amount=first_normal_index+1)[:-1]):
        f = frame_to_window_curve.position(distance=d)
        all_pairs[i] = (all_pairs[i][0], f)

    # awkward_corner = frame_to_window_curve.position(closest = Point(-100, 0, 100))
    # awkward_corner_visitor = min(range(len(all_pairs)), key = lambda i: all_pairs[i][1].distance(awkward_corner))

    # spread = 6
    # l = awkward_corner_visitor - spread
    # m = awkward_corner_visitor + spread
    # a = frame_to_window_curve.distance(closest = all_pairs[l][1])
    # b = frame_to_window_curve.distance(closest = all_pairs[m][1])
    # for i,d in zip(range(l+1, m),
    #                subdivisions(a, frame_to_window_curve.length(), amount=(awkward_corner_visitor-l) + 1)[1:-1] + subdivisions(0, b, amount=(m-awkward_corner_visitor) + 1)[0:-1]):
    #     f = frame_to_window_curve.position(distance=d)
    #     all_pairs[i] = (all_pairs[i][0], f)

    distances = [frame_to_window_curve.distance(closest = f) for w,f in all_pairs]
    il = len(distances)
    dl = frame_to_window_curve.length()
    learning_rate = 0.1
    for r in range(100):
        gradient = [0]*il
        for (i,d),(j,e) in pairs(enumerate(distances), loop=True):
            diff = (((e - d) + 1.5*dl) % dl) - 0.5*dl
            def pull(val):
                gradient[i] += val
                gradient[j] -= val
            toomuch = diff - 1
            if toomuch > 0:
                pull(toomuch)
            toolittle = diff - 0.3
            if toolittle < 0:
                print(r, i, toolittle)
                pull(toolittle)
        for i,g in enumerate(gradient):
            distances[i] = (distances[i] + g*learning_rate + dl) % dl

    for i, d in enumerate(distances):
        all_pairs[i] = (all_pairs[i][0], frame_to_window_curve.position(distance=d))

    # for d in subdivisions(a, c, max_length=1):
    #     f = frame_to_window_curve.position(distance=d)
    #     all_pairs.append((f, f.projected(onto=Plane(Origin, Right))))

    # combined_curve = BSplineCurve(all_points)
    # combined_curve = BSplineSurface(all_pairs, v=BSplineDimension(degree=1))
    # preview(Compound([Edge(*p) for p in all_pairs]), frame_to_window_curve.position(distance=0))
    # preview(combined_curve, all_pairs[last_normal_index], all_pairs[first_normal_index])
    return all_pairs

@run_if_changed
def window_shaped_3d_printable():
    # also copied from old version
    # measurements I made:
    # xy angle: 1/21
    # yz angle: 8 degrees
    right_lens_aggregate_outwards_normal = Direction(-1/21, -1, -Degrees(8).sin())
    build_up = -right_lens_aggregate_outwards_normal
    thickness = 1.2
    def opoint(a1,a2,a3,b2):
        # print (a1, a2, a3, b2)
        out12 = Direction((a2 - a1).cross(a2 - b2))
        out23 = Direction((a3 - a2).cross(a2 - b2))
        average = Direction(Between(out12, out23))
        return RayIsh(a2, average).intersections(Plane(a2+out12*thickness, out12)).point()
        # return a2 + out*1.6
    new_pairs = []
    for i, ((w1,f1),(w2,f2),(w3,f3)) in enumerate(zip(window_pairs, window_pairs[1:]+window_pairs[:1], window_pairs[2:]+window_pairs[:2])):
        # print(f"{i}/{len(window_pairs)}, {w2}")
        new_pairs.append((opoint(w1, w2, w3, f2), opoint(f3,f2,f1, w2)))

    result = Loft([Wire([w1, w2, f2, f1],loop=True) for (w1,f1),(w2,f2) in zip(window_pairs[1:]+window_pairs[:2], new_pairs+new_pairs[:1])], solid=True, ruled=True)

    save_STL("window_shaped_3d_printable", result)
    # export("window_shaped_3d_printable.stl", "window_shaped_3d_printable_1.stl")
    preview(result, Compound([Edge(*p) for p in window_pairs]), frame_to_window_curve.position(distance=0), approx_face_surface, frame_eye_lasers)



print(nose_break_point)
preview(nose_break_point, Edge(nose_break_point, nose_break_point@Mirror(Right)), frame_to_window_curve, frame_to_window_curve@Mirror(Right), BSplineCurve([depthmap_sample_point(0,z) for z in range(-30, 30, 2)]),
        approx_face_surface, window_end_curve)
