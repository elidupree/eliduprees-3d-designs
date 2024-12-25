import math
from PIL import Image

depthmap_res = 750
depthmap_size = 250
depthmap_image = Image.open("private/Eli_face_scan_1_depthmap_3px_per_mm_color_range_-100to150y.png")

def depthmap_sample(x, z):
    x = (x + depthmap_size/2) * depthmap_res/depthmap_size
    y = (z + depthmap_size/2 - 8) * depthmap_res/depthmap_size
    x0 = math.floor(x)
    y0 = math.floor(y)
    xfrac = math.trunc(x)
    yfrac = math.trunc(y)
    interpolated = sum(
        depthmap_image.getpixel((xn,yn)) * xweight * yweight
          for (xn,xweight) in [(x0, 1-xfrac), (x0+1, xfrac)]
          for (yn,yweight) in [(y0, 1-yfrac), (y0+1, yfrac)]
    )
    return interpolated * 250 - 100