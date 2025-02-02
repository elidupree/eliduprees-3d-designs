import math
from pyocct_system import *

inch = 25.4

def wallify(rows, thickness, *, loop):
    """
    Take rows, which define a BSplineSurface, where each row should be flat (compared with the build plate),
    and extrude that surface by `thickness` in the direction that is normal to the surface within the parallel-to-build-plate plane (note: the caller must be careful about positive versus negative)
    """
    surface = BSplineSurface(
        rows,
        v = BSplineDimension (periodic = loop)
    )
    other_rows = [
        [
            surface.position(parameter=(u,v)) + (surface.normal(parameter=(u,v))*1).projected_perpendicular (Up).normalized()*thickness
            for u in surface.UKnots()
        ]
        for v in surface.VKnots()
    ]

    other_surface = BSplineSurface(
        other_rows,
        v = BSplineDimension (periodic = loop)
    )
    if loop:
        joiner = [
            Face(BSplineSurface([rows[0], other_rows[0]], BSplineDimension(degree=1), BSplineDimension (periodic = loop))),
            Face(BSplineSurface([rows[-1], other_rows[-1]], BSplineDimension(degree=1), BSplineDimension (periodic = loop))),
        ]
    else:
        joiner = Loft(Face(surface).outer_wire(), Face(other_surface).outer_wire()).faces()
    #preview(surface, other_surface, joiner)
    wall = Solid(Shell(Face(surface).complemented(), Face(other_surface), joiner))
    return wall


def pointy_hexagon(*, short_radius = None, long_radius = None):
    # if short_radius is None:
    #     short_radius = long_radius * math.cos(math.tau / 12)
    if long_radius is None:
        long_radius = short_radius / math.cos(math.tau / 12)

    return Compound(
        Face(Wire([
            Point(long_radius, 0, 0) @ Rotate(Up, degrees=i * 60)
            for i in range(6)
        ], loop=True)),
        # make it a little spiky, to compensate for print irregularities
        Face(Wire([
            p
            for i in range(6)
            for p in [Point(long_radius*0.5, 0, 0) @ Rotate(Up, degrees=i * 60 - 30),
                      Point(long_radius*1.28, 0, 0) @ Rotate(Up, degrees=i * 60),]
        ], loop=True)),
    )
