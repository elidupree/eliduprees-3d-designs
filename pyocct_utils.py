from pyocct_system import *

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
            p + (surface.normal(closest=p)*1).projected_perpendicular (Up).normalized()*thickness
            for v,p in enumerate(row)
        ]
        for u,row in enumerate(rows)
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