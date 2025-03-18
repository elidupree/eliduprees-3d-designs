import math
import OpenEXR
from pyocct_system import *


def normal_of_depthmap_sampler(sampler, x, y, epsilon=0.001):
    d = sampler(x, y)
    if d is None: return None
    dxe, dye = sampler(x+epsilon, y), sampler(x, y+epsilon)
    if dxe is None or dye is None: return None
    dddx,dddy = dxe - d, dye - d
    return -Direction(Vector(epsilon, 0, dddx).cross(Vector(0, epsilon, dddy)))

class Depthmap:
    def __init__(self, file_path, *, pixels_per_unit, px_at_zero, py_at_zero, min_depth, max_depth, invalid_depths = None):
        self.file_path = file_path
        register_file_read(file_path)
        self.file = OpenEXR.File(file_path)
        self.pixels = self.file.channels()["RGB"].pixels
        self.px_at_zero = px_at_zero
        self.py_at_zero = py_at_zero
        self.pixels_per_unit = pixels_per_unit
        self.min_depth = min_depth
        self.depth_range = max_depth - min_depth
        self.invalid_depths = invalid_depths

    def __repr__(self):
        v = vars(self).copy()
        del v["file"]
        del v["pixels"]
        del v["invalid_depths"]
        return f"Depthmap({repr(v)})"

    def pixel_depth(self, px, py):
        result = self.pixels[py,px][0]
        result = self.min_depth + result * self.depth_range
        if self.invalid_depths is not None and self.invalid_depths(result):
            return None
        return result

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
                try:
                    depth = self.pixel_depth(px2, py2)
                except IndexError:
                    continue
                if depth is None:
                    continue
                total = total + depth*weight
                total_used_weight += weight

        if total_used_weight/total_weight <= 0.75:
            return None
        return total / total_used_weight
    
    def x_to_px(self, x):
        return self.px_at_zero + self.pixels_per_unit*x

    def y_to_py(self, y):
        return self.py_at_zero + self.pixels_per_unit*y

    def depth_smoothed(self, x, y, radius):
        return self.pixel_depth_smoothed(self.x_to_px(x), self.y_to_py(y), radius*self.pixels_per_unit)

