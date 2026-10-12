

import json
import math
from pathlib import Path
import subprocess
import numpy as np
from pyocct_system import *


def load_depthmaps_from_specfile(specfile_path, names):
    # see eliduprees_3d_designs_lib/src/depthmap.rs
    register_file_read(specfile_path)
    with open(specfile_path) as specfile:
        maps_spec = json.load(specfile)

    export_path = Path(maps_spec["export_path"])
    # up_to_date = False
    # try:
    #     with open(export_path/"spec_as_last_rendered.json") as rendered_specfile:
    #         rendered_spec = json.load(rendered_specfile)
    #         if json.dumps(maps_spec) == json.dumps(rendered_spec):
    #             up_to_date = True
    #         else:
    #             print(f"Found out-of-date depthmap specfile for: {specfile_path}")
    # except IOError as e:
    #     print(f"IOError loading depthmap specfile: {specfile_path}, {e}")
    #     pass

    # if up_to_date:
    #     print(f"Depthmap specfile up-to-date: {specfile_path}")
    # else:
        # print(f"Updating depthmap specfile: {specfile_path}")
    subprocess.run(["cargo", "run", "--bin", "render_depthmaps", "--", specfile_path])
        # print(f"Done updating depthmap specfile: {specfile_path}")

    result = {}
    
    for map_spec in maps_spec["maps"]:
        if map_spec["name"] in names:
            result[map_spec["name"]] = Depthmap(export_path/(map_spec["name"]+".npy"), maps_spec["frame_of_reference"])

    return result
            
class Depthmap:
    def __init__(self, file_path, frame_of_reference):
        self.file_path = str(file_path)
        register_file_read(file_path)
        self.pixels = np.load(file_path)
        self.origin = Point(*frame_of_reference["origin"])
        self.x_pixel_offset = Vector(*frame_of_reference["x_pixel_offset"])
        self.y_pixel_offset = Vector(*frame_of_reference["y_pixel_offset"])
        self.depth_unit_offset = Vector(*frame_of_reference["depth_unit_offset"])

    def __repr__(self):
        v = vars(self).copy()
        del v["pixels"]
        return f"Depthmap({repr(v)})"

    def px_py_relative_to_center(self, p):
        from_center = (p - self.origin)
        px_offs = from_center.dot(self.x_pixel_offset) / self.x_pixel_offset.dot(self.x_pixel_offset)
        py_offs = from_center.dot(self.y_pixel_offset) / self.y_pixel_offset.dot(self.y_pixel_offset)
        return px_offs, py_offs

    def px_py(self, p):
        px_offs, py_offs = self.px_py_relative_to_center(p)
        return (
            ((self.pixels.shape[1] -1) /2) + px_offs,
            ((self.pixels.shape[0] -1) /2) + py_offs,
        )

    def projected_to_smoothed_surface(self, p, pradius, default = None):
        px_offs, py_offs = self.px_py_relative_to_center(p)
        px, py = self.px_py(p)
        # print(px_offs, py_offs, px, py)
        depth = self.pixel_depth_smoothed(px,py,pradius)
        if depth is None:
            return default
        return (self.origin
                + self.x_pixel_offset * px_offs
                + self.y_pixel_offset * py_offs
                + self.depth_unit_offset * depth
        )

    def pixel_depth(self, px, py):
        if px < 0 or py < 0:
            return None
        try:
            return self.pixels[py,px]
        except IndexError:
            return None

    def pixel_depth_smoothed(self, px, py, pradius):
        sr = pradius**2
        total = 0
        total_used_weight = 0
        total_weight = 0
        for px2 in range(math.floor(px-pradius+1), math.ceil(px+pradius)):
            for py2 in range(math.floor(py-pradius+1), math.ceil(py+pradius)):
                weight = 1 - ((px-px2)**2+(py-py2)**2)/sr
                if weight <= 0: continue
                total_weight += weight
                depth = self.pixel_depth(px2, py2)
                if depth is None or math.isinf(depth):
                    continue
                total = total + depth*weight
                total_used_weight += weight

        if total_used_weight/total_weight <= 0.75:
            return None
        return total / total_used_weight

    
    
