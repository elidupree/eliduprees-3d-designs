import math

import depthmap
from depthmap import Depthmap
from pyocct_system import *

initialize_pyocct_system()

chin_depthmap = Depthmap("private/chin_bones_mold_downward_depthmap_3px_per_mm_100mm_range.exr", pixels_per_unit = 3, px_at_zero = (750-1)/2, py_at_zero = (750-1)/2, min_depth = 100, max_depth = 0, invalid_depths = depthmap.Lt(5))

def sample(x, y):
    return chin_depthmap.depth_smoothed(x, y, 1)

chunk_radius = 5
chunk_diameter = chunk_radius*2
chunk_hole_diameter = 7

@run_if_changed
def chunk_shadow():
    section = Vertex(Origin).extrude(Left*chunk_diameter, centered=True).extrude(Back*chunk_diameter, centered=True)
    hole = Vertex(Origin).extrude(Left*chunk_hole_diameter, centered=True).extrude(Back*chunk_hole_diameter, centered=True)
    return section.cut(hole).extrude(Up*45, Up*100)

def surface_chunk(x, y):
    rows = []
    for x2 in subdivisions(x-chunk_radius, x+chunk_radius, amount=chunk_diameter//2+1):
        row = []
        rows.append(row)
        for y2 in subdivisions(y-chunk_radius, y+chunk_radius, amount=chunk_diameter//2+1):
            z = sample(x2, y2)
            if z is None:
                return None
            row.append(Point(x2, y2, z))
    # preview(rows)
    return BSplineSurface(rows)


def chunk(x, y):
    s = surface_chunk(x, y)
    if s is None:
        return None
    return Intersection(chunk_shadow @ Translate(x, y), Face(s).extrude(Down*100))

@run_if_changed
def chunks():
    result = []
    for x in range(-50, 51, chunk_diameter):
        for y in range(-50, 101, chunk_diameter):
            c = chunk(x, y)
            if c is not None:
                result.append(c)
    return result

preview(Compound(chunks), Vertex(0, 0, 50).extrude(Left*100, centered=True).extrude(Back*100, centered=True), Vertex(0, 0, 70).extrude(Left*100, centered=True).extrude(Back*100, centered=True))
