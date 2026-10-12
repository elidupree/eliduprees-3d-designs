import math

from pyocct_system import *

from face_depthmap_loader import front_depthmap_sample_point

initialize_pyocct_system()

# @run_if_changed
# def multiple_faces():
#     return LoadSTL("private/standardfacelayout_multiple_faces.stl")

# preview(Intersection(multiple_faces, Plane(Origin, Up)))

@run_if_changed
def face5():
    return LoadSTL("private/standardfacelayout_face5.stl", point_filter = lambda p: -130 < p[2] < 120 and 90 < p[1] < 130)

# preview(face5)

@run_if_changed
def cross_section_heights():
    return list(range(-130, 100, 5))

border_y = 110

@run_if_changed
def face5_surround_points():
    vertices = [v.point() for v in face5.vertices()]
    left = [v for v in vertices if v[0] < 0]
    right = [v for v in vertices if v[0] > 0]
    result = []
    for z in cross_section_heights:
        vs = [min(vs, key = lambda v: v.distance(Point(v[0],border_y,z))) for vs in [left,right]]
        result.append([Point(v[0], border_y, z) for v in vs])
    return result

# preview(Compound(Intersection (Face(w), Face(Plane(Origin, Front))) for w in face5.wires()))
# preview ( Intersection (face5, Face(Plane(Origin, Front))))
@run_if_changed
def curves():
    result = []
    for z, (l, r) in zip(cross_section_heights, face5_surround_points):
        breadth = min(-l[0], r[0])
        for attempt in subdivisions (breadth, 0, amount=60):
            depthmap_points = []
            for x in subdivisions(-64, 64, amount=40):
                p = front_depthmap_sample_point(x, z)
                if p is None:
                    break
                depthmap_points.append(p)
            if len(depthmap_points) == 40:
                break
        else:
            depthmap_points = subdivisions(l, r, amount=42)[1:-1]

        row = [l] + depthmap_points + [r]
        result.append (BSplineCurve (row))
    return result
preview (curves, face5)
triangulation = LoadSTL_Triangulation("private/standardfacelayout_face5.stl")
vertices = [Vertex (point) for point in triangulation.nodes() if 0 < point[2] - 40 < 5]
preview(face5, Compound(vertices), Edge(Origin, Origin+Left*100) @ Translate(Back*110))
faces = [Wire (*(vertices [index - 1] for index in triangle.Get (0, 0, 0))) for triangle in triangulation.triangles()]