import math

from pyocct_system import *
from depthmap2 import load_depthmaps_from_specfile, Depthmap

initialize_pyocct_system()

depthmaps = load_depthmaps_from_specfile("face_mold_depthmaps_spec.json", ["Eli_face_scan_1", "face5", "merged", "outset"])


def depthmap_to_surface(depthmap: Depthmap):
    forehead_cut_point = Point(0, 40, 98)
    forehead_cut_dir = Direction(0, -0.7, 1)
    def sample(x,z):
        p = Point(x, 100, z)
        p2 = depthmap.projected_to_smoothed_surface(p, 1, default=p)
        pf = depthmaps["Eli_face_scan_1"].projected_to_smoothed_surface(p, 1, default=p)
        if pf.distance(p2) > 0.5:
            p2 = Point(x, max(p2[1], depthmap.projected_to_smoothed_surface(Point(-x, 100, z), 1, default=p)[1]), z)
        if p2[1] > 100:
            return p
        if (p2-forehead_cut_point).dot(forehead_cut_dir) > 0:
            return p2.projected(onto=Plane(forehead_cut_point, forehead_cut_dir), by = Back)
        return p2
    resolution = 2
    return BSplineSurface([[sample(x,z) for z in subdivisions(-142, 120, max_length=resolution)] for x in subdivisions(-102,102,max_length=resolution)])

#@run_if_changed
#def face5():
#    return depthmap_to_surface(depthmaps["face5"])

#@run_if_changed
#def Eli_face_scan_1():
#    return depthmap_to_surface(depthmaps["Eli_face_scan_1"])

#@run_if_changed
#def face_merged():
#    return depthmap_to_surface(depthmaps["merged"])

@run_if_changed
def model_boundary_xz():
    left_points = [
        Point(0, 0, 120),
        Point(-60, 0, 120),
        Point(-100, 0, 70),
        Point(-100, 0, 0),
        Point(-85, 0, -70),
        # Point(-50, 0, -140),
        # Point(0, 0, -140),
        Point(-50, 0, -80),
        Point(0, 0, -80),
    ]

    return BSplineCurve(left_points + [p @ Mirror(Right) for p in left_points[-1:0:-1]], BSplineDimension(periodic=True)) @ Translate(Back*100)

@run_if_changed
def face_outset():
    result = depthmap_to_surface(depthmaps["outset"]) 
    preview(result, model_boundary_xz)
    return result

@run_if_changed
def mold_solid():
    solid1 = Face(Edge(model_boundary_xz)).extrude(Back*1, Front*130)
    solid2 = Face(face_outset).extrude(Front*131)
    result = Intersection(solid1, solid2) @ Rotate(Right, Degrees(90)) @ Translate(Down*200 + Front*200)
    preview(result)
    return result

@run_if_changed
def export_mold_solid():
    save_STL("mold_solid", mold_solid)
    export("mold_solid.stl", "mold_solid_1.stl")

preview(
    #face5,
    #Eli_face_scan_1,
    #face_merged,
    face_outset,
    model_boundary_xz,
    mold_solid,
    )