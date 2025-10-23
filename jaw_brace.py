import math

import depthmap
from depthmap import Depthmap
from pyocct_system import *
import matplotlib.pyplot as plt

from svg_utils import load_Inkscape_BSplineCurve

initialize_pyocct_system()

chin_depthmap = Depthmap("private/chin_bones_mold_downward_depthmap_3px_per_mm_100mm_range.exr", pixels_per_unit = 3, px_at_zero = (750-1)/2, py_at_zero = (750-1)/2, min_depth = 100, max_depth = 0, invalid_depths = depthmap.Lt(5))

# plt.hist([c for row in chin_depthmap.pixels for cell in row for c in cell if c != 1.0], bins=50)
# plt.show()

def sample(x, y = None):
    if y is None:
        x, y = x[0],x[1]
    return chin_depthmap.depth_smoothed(x, -y, 1)
def sample_point(x, y = None):
    if y is None:
        x, y = x[0],x[1]
    z = sample(x, y)
    if z is None:
        return None
    return Point(x, y, z)

def curve_from_layout_file(id):
    # I've laid out some curves as front-views in Inkscape:
    return load_Inkscape_BSplineCurve("jaw_mold_layout.svg", id) @ Mirror(Back) @ Translate(Left*125 + Back*125)

@run_if_changed
def inner_line():
    return curve_from_layout_file("inner_line")
@run_if_changed
def outer_line():
    return curve_from_layout_file("outer_line")
@run_if_changed
def middle_line():
    return curve_from_layout_file("middle_line")


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

@run_if_changed
def strips():
    num_curved_strips = 5
    rowses = [[] for _ in range(num_curved_strips)]
    for i, inner in enumerate(inner_line.subdivisions(amount=101)):
        try:
            outer = outer_line.position(closest = inner)
        except:
            preview(outer, outer_line, inner_line)
        mid = min(middle_line.intersections(Plane(inner, Direction((outer - inner).cross(Up)))).points, key = lambda p: outer.distance(p))
        edge = max(subdivisions(mid, outer, max_length = 0.2), key = sample)
        # if mid.distance(outer) < mid.distance(inner):

        d = Direction(inner, outer)
        half_width_offset = Direction(inner, outer)*0.5
        mid_z = sample(mid)
        def cropped_sample(p):
            too_far_in = inner.distance(mid) - inner.distance(p)
            if outer.distance(p) < outer.distance(edge):
                z = 100
            elif too_far_in > 0:
                z = mid_z - too_far_in*0.3
            else:
                z = sample(p)
            try:
                return Point(p[0], p[1], z)
            except:
                preview(Compound(chunks), outer, inner, mid, p, edge, outer_line, middle_line, inner_line)
        for rows, strip_point in zip(rowses, subdivisions(inner, edge+d*1, amount = num_curved_strips)):
            offset = [-1, 0, 1, 0][i % 4]
            offset = d * offset*0.8
            a, b = strip_point - half_width_offset + offset, strip_point + half_width_offset + offset
            rows.append([cropped_sample(p) for p in [a,b]])
        z = sample(mid)
        # if z is None:
        #     preview(Compound(chunks), outer, inner, mid, outer_line, middle_line, inner_line)
        # else:
        #     z = sample()
        # try:
        # rowses[0].append([sample_point(edge), Point(inner[0], inner[1], z)])
        # except:
        #     import traceback
        #     traceback.print_exc()
        #     preview(Compound(chunks), outer, inner, mid, outer_line, middle_line, inner_line)

    cross_strips = []
    for i, rows_pair in enumerate(pairs(rowses)):
        parity = i % 2
        for (_, a), (b, _) in zip(*(rows[parity*2+1:-1:4] for rows in rows_pair)):
            d1 = Direction(a, b)
            d2 = Direction(d1.cross(Up))
            def fix(p):
                p2 = sample_point(p)
                if p2 is not None and p[2] - 5 < p2[2] < p[2]:
                    return p2
                return p
            e = Edge(BSplineCurve([fix(p) for p in subdivisions(a-d1*0.1, b+d1*0.1, amount=4)]))
            cross_strips.append(e.extrude(d2*1, centered=True).extrude(Down*20) @ Translate(Down*2))
    return Compound([Face(BSplineSurface(rows, v = BSplineDimension(degree=1))).extrude(Down*20) for rows in rowses] + cross_strips)

@run_if_changed
def export_strips():
    save_STL("jaw_mold_test", strips)
    export("jaw_mold_test.stl", "jaw_mold_test_2.stl")
    pass

preview(strips, Compound(chunks), Vertex(0, 0, 50).extrude(Left*100, centered=True).extrude(Back*100, centered=True), Vertex(0, 0, 70).extrude(Left*100, centered=True).extrude(Back*100, centered=True))
