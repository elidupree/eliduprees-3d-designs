import math

from pyocct_system import *
from depthmap2 import load_depthmaps_from_specfile, Depthmap

initialize_pyocct_system()

depthmaps = load_depthmaps_from_specfile("face_mold_depthmaps_spec.json", ["Eli_face_scan_1", "face5", "merged", "outset"])

def depthmap_to_surface(depthmap: Depthmap):
    def sample(x,z):
        p = Point(x, 100, z)
        p2 = depthmap.projected_to_smoothed_surface(p, 1, default=p)
        if p2[1] > 100:
            return p
        return p2
    return BSplineSurface([[sample(x,z) for z in range(-132, 121, 2)] for x in range(-102,103,2)])

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
def face_outset():
    return depthmap_to_surface(depthmaps["outset"]) 

preview(
    #face5,
    #Eli_face_scan_1,
    #face_merged,
    face_outset,
    )