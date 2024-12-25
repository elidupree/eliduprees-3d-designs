import math
from PIL import Image

depthmap_res = 750
depthmap_size = 250
depthmap_image = Image.open("private/Eli_face_scan_1_depthmap_3px_per_mm_color_range_-100to150y.png")

def depthmap_sample(x, z):
    x = (x + depthmap_size/2) * depthmap_res/depthmap_size
    y = (depthmap_size/2 + 8 - z) * depthmap_res/depthmap_size
    x0 = math.floor(x)
    y0 = math.floor(y)
    xfrac = x - x0
    yfrac = y - y0
    sample_points = [(xs, ys)
        for xs in [(x0, 1-xfrac), (x0+1, xfrac)]
        for ys in [(y0, 1-yfrac), (y0+1, yfrac)]]
    samples = [depthmap_image.getpixel((xn,yn))[0] for ((xn,_),(yn,_)) in sample_points]
    if any(s == 255 for s in samples): return None
    interpolated = sum(
        s * xweight * yweight for s, ((xn,xweight),(yn,yweight)) in zip(samples,sample_points)
    )
    # print(x0, xfrac, interpolated)
    return (interpolated / 255) * 250 - 100

depthmap_sample(0,0)