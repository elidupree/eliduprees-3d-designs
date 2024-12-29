import math
from PIL import Image
from pyocct_system import *

depthmap_res = 750
depthmap_size = 250
depthmap_image = Image.open("private/Eli_face_scan_1_depthmap_3px_per_mm_color_range_-100to150y.png")

def depthmap_sample_pixel(px, py):
    result = depthmap_image.getpixel((px, py))[0]
    if result == 255:
        return None
    return (result / 255) * 250 - 100

def depthmap_sample_pixel_interpolated(px, py):
    px0 = math.floor(px)
    py0 = math.floor(py)
    xfrac = px - px0
    yfrac = py - py0
    sample_points = [(xs, ys)
                     for xs in [(px0, 1-xfrac), (px0+1, xfrac)]
                     for ys in [(py0, 1-yfrac), (py0+1, yfrac)]]
    samples = [depthmap_sample_pixel(pxn,pyn) for ((pxn,_),(pyn,_)) in sample_points]
    if any(s is None for s in samples): return None
    return sum(
        s * xweight * yweight for s, ((xn,xweight),(yn,yweight)) in zip(samples,sample_points)
    )

def z_to_py(z):
    return (depthmap_size/2 - z) * depthmap_res/depthmap_size
def py_to_z(py):
    return (depthmap_size/2) - (py * depthmap_size/depthmap_res)

def x_to_px(x):
    return (depthmap_size/2 + x) * depthmap_res/depthmap_size
def px_to_x(px):
    return (-depthmap_size/2) + (px * depthmap_size/depthmap_res)

def depthmap_sample(x, z):
    return depthmap_sample_pixel_interpolated(x_to_px(x), z_to_py(z))

def depthmap_pixel_to_point(px, py):
    y = depthmap_sample_pixel(px, py)
    if y is None: return None
    return Point(px_to_x(px), y, py_to_z(py))

depthmap_points = [
    [
        (depthmap_pixel_to_point(px, py))
        for py in range(depthmap_res)
    ]
    for px in range(depthmap_res)
]

def depthmap_sample_smoothed(px, py, pradius):
    cr = math.ceil(pradius)
    sr = pradius**2
    total = Vector()
    total_used_weight = 0
    total_weight = 0
    for x in range(px-cr+1, px+cr):
        for y in range(py-cr+1, py+cr):
            weight = 1 - (x**2+y**2)/sr
            total_weight += weight
            try:
                p = depthmap_points[x][y]
            except IndexError:
                continue
            if p is None:
                continue
            total = total + (p - Origin)*weight
            total_used_weight += weight

    if total_used_weight/total_weight <= 0.75:
        return None
    return Origin + (total / total_used_weight)

def depthmap_samples_smoothed(max_radius):
    pradius = math.floor(max_radius * depthmap_res/depthmap_size)
    return [
        [
            (depthmap_sample_smoothed(px, py, pradius))
            for py in range(0,depthmap_res,pradius)
        ]
        for px in range(0,depthmap_res,pradius)
    ]

depthmap_sample(0,0)