import math
from pyocct_system import *
from depthmap import Depthmap

front_depthmap = Depthmap("private/Eli_face_scan_1_depthmap_3px_per_mm_color_range_-100to150y.exr", pixels_per_unit = 3, px_at_zero = (750-1)/2, py_at_zero = (750-1)/2, min_depth = -100, max_depth = 150, invalid_depths = lambda d: d > 149)
left_depthmap = Depthmap("private/Eli_face_scan_1_depthmap_3px_per_mm_color_range_-100to150x.exr", pixels_per_unit = 3, px_at_zero = (750-1)/2, py_at_zero = (750-1)/2, min_depth = -100, max_depth = 150, invalid_depths = lambda d: d > 5)
right_depthmap = Depthmap("private/Eli_face_scan_1_depthmap_3px_per_mm_color_range_100to-150x.exr", pixels_per_unit = 3, px_at_zero = (750-1)/2, py_at_zero = (750-1)/2, min_depth = 100, max_depth = -150, invalid_depths = lambda d: d > 5)


def front_depthmap_sample_y(x, z=None, radius = 2):
    """Pick a standardized interpretation of the depth map.

    It might theoretically be beneficial to use the recorded asymmetries of my face,
    rather than erasing them, but intuitively I would rather have the device be symmetric,
    and also it's possible that the recorded asymmetries are error (which could be canceled out)
    rather than a true signal. So just average the two sides.

    "average of depthmap" isn't necessarily the optimal way to enforce symmetries
    (it has directional biases) but I don't care enough to perfect it.
    """
    if z is None: x,z = x[0],x[2]
    l = front_depthmap.depth_smoothed(-x, -z, radius)
    r = front_depthmap.depth_smoothed(x, -z, radius)
    if l is None:
        return r
    if r is None:
        return l
    return Between(l, r)


def front_depthmap_sample_point(x, z=None, radius = 2):
    if z is None: x,z = x[0],x[2]
    y = front_depthmap_sample_y(x, z, radius)
    if y is None: return None
    return Point(x, y, z)


def side_depthmap_sample_x(y, z=None, radius = 2):
    if z is None: y,z = y[1],y[2]
    l = left_depthmap.depth_smoothed(-y, -z, radius)
    r = right_depthmap.depth_smoothed(y, -z, radius)
    if r is None:
        return l
    if l is None:
        return -r
    return Between(l, -r)


def side_depthmap_sample_point(y, z=None, radius = 2):
    if z is None: y,z = y[1],y[2]
    x = side_depthmap_sample_x(y, z, radius)
    if x is None: return None
    return Point(x, y, z)