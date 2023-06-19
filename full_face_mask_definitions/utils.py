import math
from pyocct_system import *
del Front, Back


def edges_with_reversed(wire):
    edges = wire.edges()
    if len(edges) <= 1:
        for e in edges:
            yield e, False
    else:
        def same(a, b):
            return a[0] == b[0] and a[1] == b[1] and a[2] == b[2]

        a1, a2 = edges[0].vertices()
        b1, b2 = edges[1].vertices()
        if same(a2, b1) or same(a2, b2):
            yield edges[0], False
            last_end = a2
        else:
            yield edges[0], True
            last_end = a1
        for e in edges[1:]:
            e1, e2 = e.vertices()
            if same(e1, last_end):
                yield e, False
                last_end = e2
            else:
                yield e, True
                last_end = e1


def oriented_edge_curves(wire):
    for edge, reversed in edges_with_reversed(wire):
        c, a, b = edge.curve()
        if reversed:
            a, b = b, a
        yield c, a, b