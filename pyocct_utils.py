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
            for v in surface.VKnots()
        ]
        for u in surface.UKnots()
    ]

    # preview(surface,
    #         # [BSplineCurve(row, BSplineDimension (periodic = loop)) for row in rows],
    #         [BSplineCurve(row, BSplineDimension (periodic = loop)) for row in other_rows])
    other_surface = BSplineSurface(
        other_rows,
        v = BSplineDimension (periodic = loop)
    )
    # preview(surface, other_surface,
    #         # [BSplineCurve(row, BSplineDimension (periodic = loop)) for row in rows],
    #         [BSplineCurve(row, BSplineDimension (periodic = loop)) for row in other_rows], other_rows)
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


def sorted_points_from_edges(edges):
    result = [v.point() for v in edges[0].vertices()]
    rest = edges[1:]
    while rest:
        new_rest = []
        for edge in rest:
            points = [v.point() for v in edge.vertices()]
            epsilon=0.00001
            if points[0].distance(result[-1]) < epsilon:
                result.append (points [1])
            elif points[1].distance(result[-1]) < epsilon:
                result.append (points [0])
            else:
                new_rest.append(edge)
        if len(new_rest) == len(rest):
            break
        rest = new_rest
    return result

def stitch_unordered_edges_to_wire(edges):
    result = [edges[0]]
    next = edges[0].vertices()[1].point()
    rest = edges[1:]
    while rest:
        new_rest = []
        for edge in rest:
            points = [v.point() for v in edge.vertices()]
            epsilon=0.00001
            if points[0].distance(next) < epsilon:
                result.append(edge)
                next = points[1]
            elif points[1].distance(next) < epsilon:
                result.append(edge)
                next = points[0]
            else:
                new_rest.append(edge)
        if len(new_rest) == len(rest):
            break
        rest = new_rest
    return Wire(result)



def flat_ended_tube_BSplineSurface_to_solid(surface):
    if surface.IsVPeriodic():
        faces = [Face(surface)] + [Face(Wire(surface.UIso(surface.UKnot(i)))) for i in [surface.FirstUKnotIndex(), surface.LastUKnotIndex()]]
    if surface.IsUPeriodic():
        faces = [Face(surface)] + [Face(Wire(surface.VIso(surface.VKnot(i)))) for i in [surface.FirstVKnotIndex(), surface.LastVKnotIndex()]]

    return Solid(Shell(faces))



def two_BSplineSurfaces_to_solid(a, b):
    ar = a.copy()
    ar.UReverse()
    param_bounds = [[[getattr(s, f"{d}Knot")(getattr(s,param_idx_fn.format(d))()) for d in ["U", "V"]] for param_idx_fn in ["First{}KnotIndex", "Last{}KnotIndex"]] for s in [a,b]]
    pointing_inwards = a.normal(param_bounds[0][0]).dot(Direction(a.position(param_bounds[0][0]), b.position(param_bounds[1][0]))) < 0
    if pointing_inwards:
        ar.UReverse()
    faces = [Face(ar), Face(b)]
    assert a.IsUPeriodic() == b.IsUPeriodic()
    assert a.IsVPeriodic() == b.IsVPeriodic()
    if not a.IsUPeriodic():
        faces.extend([
            f
            for fn in ["FirstUKnotIndex", "LastUKnotIndex"]
            for f in Loft([Wire(s.UIso(s.UKnot(getattr(s, fn)()))) for s in [a,b]], ruled=True).faces()
        ])
    if not a.IsVPeriodic():
        faces.extend([
            f
            for fn in ["FirstVKnotIndex", "LastVKnotIndex"]
            for f in Loft([Wire(s.VIso(s.VKnot(getattr(s, fn)()))) for s in [a,b]], ruled=True).faces()
        ])
    return Solid(Shell(faces))


def turn_subdivisions(amount):
    return [Turns(t) for t in subdivisions(0, 1, amount=amount)[::-1]]

def circleish_rect_points(*, length, width, amount, center = Point(0,0,0), start_angle = Turns(0), corner_copies = 1):
    a = atan2(length, width)
    turnses = [a.turns, -a.turns, 0.5-a.turns, 0.5+a.turns]*corner_copies + subdivisions(0, 1, amount=amount-(corner_copies*4) + 1)[:-1]
    turnses = sorted((t - start_angle.turns) % 1 for t in turnses)
    # print(len(turnses), amount)
    assert(len(turnses) == amount)
    def v(t):
        if t <= a.turns or t >= 1-a.turns:
            return Vector(width/2, Turns(t).tan()*width/2)
        elif 0.5-a.turns <= t <= 0.5+a.turns:
            return Vector(-width/2, Turns(t-0.5).tan()*-width/2)
        elif t < 0.5:
            return Vector(Turns(t-0.25).tan()*-length/2, length/2)
        else:
            return Vector(Turns(t-0.75).tan()*length/2, -length/2)

    return [center + v(t) for t in turnses]
