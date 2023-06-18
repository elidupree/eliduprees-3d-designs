import math
from pyocct_system import *
del Front, Back

# To shape the headband part of the mask, I need a curve that is representative of my head, at forehead height. For this, I use a BSplineCurve, with control points determined by experiment. The front part reflects my head pretty accurately; the back is decently close, and doesn't matter so much, especially since the current version doesn't even extend the headband all the way around.

headband_curve_points = [Origin + vector (a,b,0) for a,b in [
    (0, 0),
    (15, -0.01),
    (25, -2.5),
    (35, -7),
    (45, -14),
    (55, -27),
    (62, -37),
    (71, -53),
    (79, -90),
    (81, -107),
    (81, -130),
    (60, -180),
    (15, -195),
    (0, -195),
]]
headband_curve_points = [a@Mirror (Right) for a in reversed(headband_curve_points[1:-1])] + headband_curve_points

@run_if_changed
def headband_curve():
    return BSplineCurve(
        headband_curve_points,
        BSplineDimension (periodic = True),
    )
print(f"Headband circumference: {headband_curve.length()}")

# The above curve lies in the Z=0 plane, but that is an arbitrary reference point that doesn't really align with any of the real locations. We now define the z coordinates:
headband_width = 8
headband_top = 6.8 # for historical reasons
headband_bottom = headband_top - headband_width
forehead_center_distance_on_headband_curve = headband_curve.distance(closest = Origin)

def extrude_flat_shape_to_headband(shape):
    """
    Extrude a 2D shape (assumed to be within the Z=0 plane) to have the Z range of the headband.

    :param shape: The source shape.
    :return: A new shape with 1 more dimension.
    """
    return (shape @ Translate(Up*headband_top)).extrude(Down*headband_width)