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

Notes after prototype #2:
* It's cozy!
* Probably make the unrolled-window's obligatory cut be at the glasses earpieces, for assembly reasons; make appropriate holes for the spring hinges/etc (...or maybe we could even "dodge" the hinges by moving inside instead of following the current frame-curve everywhere? exact meeting with the frame isn't so important now that we want to leave a gap there on purpose)
* 3D printed 5mm-ish thick strut along the whole top and sides for rigidity (use tiny nozzle for weight reasons)
* that and 3D printed parts at the beside-nose-points can have spurs for mounting rubber
* we can actually bring the window closer to the face near the mouth; it only gets disturbed by smiles starting near the corners of the mouth, not anywhere medial of that
* on the other hand, the outer cheeks want slightly more leeway (2mm?)
* the rubber parts want to be near-zero force all the time and don't need rigorous joints
"""

import math

from pyocct_system import *
from face_depthmap_loader import depthmap_sample_smoothed
from svg_utils import load_Inkscape_BSplineCurve

initialize_pyocct_system()

def depthmap_sample_y(x, z):
    """Pick a standardized interpretation of the depth map.
    
    It might theoretically be beneficial to use the recorded asymmetries of my face,
    rather than erasing them, but intuitively I would rather have the device be symmetric,
    and also it's possible that the recorded asymmetries are error (which could be canceled out)
    rather than a true signal. So just average the two sides.
    
    "average of depthmap" isn't necessarily the optimal way to enforce symmetries
    (it has directional biases) but I don't care enough to perfect it.
    """
    return Between(depthmap_sample_smoothed(x, z, 2), depthmap_sample_smoothed(-x, z, 2))
def depthmap_sample_point(x, z):
    return Point(x, depthmap_sample_y(x, z), z)

@run_if_changed
def approx_face_surface():
    """A version of the face that's an actual BSplineSurface, so we can do surface operations with it.
    
    We currently use this to make an planar-curve and to calculate normals. Those aren't perfectly accurate to the depthmap, so you have to correct for them."""
    return BSplineSurface([[depthmap_sample_point(x,z) for z in range(-42, 31, 2)] for x in range(-64,65,2)])


earpiece_top_front_outer = Point(65.0, -0.9, 4.8)
earpiece_height = 3.30
top_of_frame_z = earpiece_top_front_outer[2] + 11

print (f"forehead y: {depthmap_sample_y(-28, 14)}")


@run_if_changed
def approx_earpieces():
    e = Vertex(earpiece_top_front_outer).extrude(Down*earpiece_height).extrude(Vector(12.5, 68, 0)).extrude(Left*0.9)
    return Compound(e, e @ Mirror(Right))


@run_if_changed
def frame_to_window_curve():
  # For now, shamelessly render a computed output from the previous legacy code:
  loaded = read_brep ("glasses_frame_to_window_curve.brep").curve()[0]
  s = loaded.subdivisions(max_length=1)
  frame_top = max(s, key=lambda f: f[2])
  # frame_bottom = min(s, key=lambda f: f[2])
  result = loaded @ Rotate(Axis(frame_top, Left), Degrees(2.3)) @ Translate(Up*(top_of_frame_z - frame_top[2]))
  closest_face_encounter = max((f[1] - depthmap_sample_y(f[0], f[2])) for f in result.subdivisions(max_length=1))
  print(f"closest_face_encounter: {closest_face_encounter}")
  face_leeway = 2
  frame_thickness = 2
  extra_leeway = 2
  result = result @ Translate(Back*(-(face_leeway + frame_thickness + extra_leeway) - closest_face_encounter))
  frame_near_earpiece_point = result.position(closest=earpiece_top_front_outer)
  print(f"earpiece y wrongness: {earpiece_top_front_outer[1] - (frame_near_earpiece_point[1] + extra_leeway + frame_thickness/2)}")
  # preview(approx_face_surface, approx_earpieces, result)
  return result


@run_if_changed
def nose_break_point():
    """The highest point on the nose wear a straight line between the frame-to-window curve
    would collide with the nose.
    
    Computed to precisely agree with the depth map by binary search."""
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


# Pick a theoretical approximate source of vision, for analyzing vision angles.
eyeball_radius = 12
eyeball_center = depthmap_sample_point(-33.5, -2) + Back*eyeball_radius


@run_if_changed
def frame_eye_lasers():
    """Illustrate theoretical vision angles."""
    return Compound([Edge(eyeball_center, Between(eyeball_center, frame_to_window_curve.position(distance=d), 1.2)) for d in subdivisions(0, frame_to_window_curve.length(), max_length = 10)[:-1]])


@run_if_changed
def window_pairs():
    """Big function that describes the window as a list of pairs, where each pair is
      (point on the window-to-face-or-seal curve, point on frame-to-window curve)."""
    
    # Start by laying out the window-to-face-or-seal curve.

    # First, there's the nose. We arbitrarily aim to make this planar.
    # Since the plane should agree with the frame-to-frame lines, find the tangent.
    frame_tangent = frame_to_window_curve.derivatives(closest=nose_break_point).tangent
    nose_flat_normal = Direction((frame_tangent*1).projected_perpendicular(Left) @ Rotate(Left, degrees=90))

    # ...actually use a more precise approximation of the surface right around the nose.
    approx_nose_surface = BSplineSurface([[depthmap_sample_point(x,z) for z in subdivisions(nose_break_point[2]-20, nose_break_point[2]+1,max_length=0.2)] for x in subdivisions(-10,10,max_length=0.2)])
    nose_flat_curve = approx_nose_surface.intersections(Plane(nose_break_point, nose_flat_normal)).curve()
    nose_flat_curve_points = nose_flat_curve.subdivisions(start_x = 0, end_z = -12, end_min_by = lambda p: p[0], max_length=1)

    # Then, we do the "main curve." I've laid this out as a front-view in Inkscape:
    main_curve = load_Inkscape_BSplineCurve("glasses_airspace_layout.svg", "window_to_seal") @ Mirror(Right) @ Rotate(Left, Degrees(90))
    main_curve_points = main_curve.subdivisions(max_length=1)[::-1]

    # Given the essentially "front view" points above, we now want to put points in 3D space.
    # Naively, we project these points directly onto the depthmap.
    # But in certain places, we want to avoid face contact,
    # e.g. so the thing doesn't get disturbed when I smile.
    # beside_nose_point = Point(-20, 0, -25)
    def faceish_point(p):
        face = depthmap_sample_point(p[0], p[2])
        # TODO: clean up this code somewhat.
        mouth_smile_badness = smootherstep(p[2], -25, -55)*2
        cheek_smile_badness = min(smootherstep(p[2], -7, -32), smootherstep(p[0], -19, -33)) * 7
        brow_badness = 0 if p[2] < 0 else smootherstep((60-abs(p[0]))/25)*15
        badness = max(mouth_smile_badness, cheek_smile_badness, brow_badness)
        if badness <= 0:
            return face
        else:
            # Near the nose, we don't actually want to move in the normal direction - just straight to the front.
            # Same at the outside of the cheeks, which don't need to be quite as wide.
            normal = Between(Front*1, (approx_face_surface.normal(closest=face)*1).projected_perpendicular(Up), smootherstep(p[0], -24, -40)*0.5)
            return face + normal*badness

    nose_flat_faceish_points = [faceish_point(p) for p in nose_flat_curve_points]
    main_curve_faceish_points = [faceish_point(p) for p in main_curve_points]

    # Between the nose part and main part, add a bit of a curve for smoothness.
    fill_in_curve = Interpolate([nose_flat_curve_points[-1], main_curve_points[0]], tangents = [(nose_flat_faceish_points[-1] - nose_flat_faceish_points[-2]).normalized(),(main_curve_faceish_points[1] - main_curve_faceish_points[0]).normalized()])
    fill_in_points = [faceish_point(p) for p in fill_in_curve.subdivisions(max_length = 1)[1:-1]]
    all_points = nose_flat_faceish_points + fill_in_points + main_curve_faceish_points

    # Naively, map each window-to-face-or-seal point to the closest frame-to-window curve point...
    all_pairs = [(p, frame_to_window_curve.position(closest=p)) for p in all_points]
    # preview(Compound([Edge(*p) for p in all_pairs]), fill_in_curve, approx_face_surface)

    # ...but the rest of this function will be about the caveats to that.
    first_normal_index = 0
    for i, (p, f) in enumerate(all_pairs):
        if f[2] < nose_break_point[2] - 5:
            first_normal_index = i
            break

    frame_top = max([p[1] for p in all_pairs], key=lambda f: abs(frame_to_window_curve.derivatives(closest=f).tangent[0]) if f[2] > 0 else 0)

    def forehead_triangle_alignedness_if_its_bottom_is_at(d):
        f = d.position
        w = all_points[-1]
        f_tangent = d.tangent
        if f_tangent[0] < Direction(f, w)[0]:
            return 0
        # return 9-abs(f[2] - -4)
        triangle_normal = Direction(Left.cross(f - w))
        # move_f_normal = Direction(f_tangent.cross(f - w))
        below_triangle_normal = Direction(Right.cross(f_tangent))
        # if p:
        #     print(triangle_normal, move_w_normal, move_f_normal)
        return abs(below_triangle_normal.dot(triangle_normal))
            # max(abs(move_f_normal.dot(triangle_normal))

    ds = frame_to_window_curve.subdivisions(output = "derivatives", start_closest = nose_break_point, end_closest = frame_top, wrap = "closest", max_length = 0.2)
    best_triangle_bottom = max(ds, key=forehead_triangle_alignedness_if_its_bottom_is_at)
    # print(best_triangle_bottom.position)
    # print(alignedness(best_triangle_bottom))
    # preview(Compound([Edge(*p) for p in all_pairs]),
    #         best_triangle_bottom.position,
    #         frame_top,
    #         Compound([Edge(d.position, d.position + Front*(1+alignedness(d)*20)) for d in ds]))
    print(f"Frame top: {frame_top}")
    best_triangle_bottom = best_triangle_bottom.position
    triangle_hecker = Direction(Left.cross(all_points[-1] - best_triangle_bottom).cross(all_points[-1] - best_triangle_bottom))
    # print(triangle_hecker)
    last_normal_index = None
    for i, (w, f) in reversed(list(enumerate(all_pairs))):
        hecked = frame_to_window_curve.position(on=Plane(w, triangle_hecker), min_by=lambda p: p.distance(w))
        if hecked[0] > f[0]:
            all_pairs[i] = (w, hecked)
        else:
            last_normal_index = i
            break

    a = frame_to_window_curve.distance(closest = best_triangle_bottom)
    # b = frame_to_window_curve.distance(closest = all_pairs[last_normal_index][1])
    d = a - 0.001
    for i, (w, f) in reversed(list(enumerate(all_pairs))):
        hecked = frame_to_window_curve.position(distance=d)
        if hecked[0] < f[0]:
            all_pairs[i] = (w, hecked)
        else:
            break
        d -= 0.2

    a = frame_to_window_curve.distance(closest = best_triangle_bottom)
    b = frame_to_window_curve.distance(closest = nose_break_point)
    for d in subdivisions(a+0.001, b, max_length = 1)[:-1]:
        f = frame_to_window_curve.position(distance=d)
        # all_pairs.append((f.projected(onto=Plane(Origin, Right)), f))

    for i,f in enumerate(frame_to_window_curve.subdivisions(start_closest = nose_break_point, end_closest = all_pairs[first_normal_index][1], wrap="closest", amount=first_normal_index+1)[:-1]):
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

    # The window surface will be wrong/nonsmooth if certain parts of the frame-to-window curve get too densely or too sparsely packed with corresponding points. Gradient-descend that away:
    distances = [frame_to_window_curve.distance(closest = f) for _w,f in all_pairs]
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
                # print(r, i, toolittle)
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
    # preview(Compound([Edge(*p) for p in all_pairs]), frame_to_window_curve.position(distance=0),approx_face_surface)
    # preview(combined_curve, all_pairs[last_normal_index], all_pairs[first_normal_index])
    return all_pairs

@run_if_changed
def window_eye_lasers():
    return Compound([Edge(eyeball_center+Front*4, Between(eyeball_center+Front*4, w, 1.2)) for w,f in window_pairs[::5]])

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
    quads = [[w1, w2, f2, f1] for (w1,f1),(w2,f2) in zip(window_pairs[1:]+window_pairs[:2], new_pairs+new_pairs[:1])]
    # faces = [zip(a,b) for a,b in pairs(quads)]
    wires = [Wire(q, loop=True) for q in quads]
    result = Loft(wires, solid=True, ruled=True)
    result = result.cut(Vertex(earpiece_top_front_outer).extrude(Down*earpiece_height).extrude(Left*500, centered=True).extrude(Back*100))
    # preview(result)
    mirror = result @ Mirror(Right)
    # result = Compound(result, mirror)
    save_STL("window_shaped_3d_printable", result)
    # export("window_shaped_3d_printable.stl", "window_shaped_3d_printable_3.stl")
    preview(result, mirror, Compound([Edge(*p) for p in window_pairs]), frame_to_window_curve.position(distance=0), approx_face_surface, frame_eye_lasers, window_eye_lasers, approx_earpieces)



print(nose_break_point)
preview(nose_break_point, Edge(nose_break_point, nose_break_point@Mirror(Right)), frame_to_window_curve, frame_to_window_curve@Mirror(Right), BSplineCurve([depthmap_sample_point(0,z) for z in range(-30, 30, 2)]),
        approx_face_surface, window_end_curve)
