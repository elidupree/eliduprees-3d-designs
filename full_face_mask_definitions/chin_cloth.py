import math

from full_face_mask_definitions.constants import neck_leeway, TowardsBackOfHead
from full_face_mask_definitions.headband_geometry import headband_bottom
from full_face_mask_definitions.intake import intake_outer_solids, intake_middle, intake_outer_surfaces_extended
from full_face_mask_definitions.shield import shield_infinitesimal_without_cuts
from full_face_mask_definitions.shield_geometry import temple_top
from full_face_mask_definitions.top_cloth import top_cloth_leeway
from full_face_mask_definitions.utils import oriented_edge_curves
from pyocct_system import *

del Front, Back


# The edge of the cloth is identical to the edge of the shield, with the one exception where it has to go around the intake on the other side.
@run_if_changed
def chin_cloth_shield_points():
    shield_edges = shield_infinitesimal_without_cuts.wire().intersection(
        HalfSpace(Point(0, 0, headband_bottom - 0.001), Down))
    for solid in intake_outer_solids:
        shield_edges = shield_edges.cut(solid)
    edges = shield_edges.edges()

    # Hack - this is hard coding the exact division into edges, so it might break if I change other geometry
    before_intake_edges = edges[0:2]
    after_intake_edge = edges[2]

    points = []
    for c, a, b in oriented_edge_curves(Wire(before_intake_edges)):
        ad = c.length(0, a)
        bd = c.length(0, b)
        for d in subdivisions(ad, bd, max_length=5):
            points.append(c.value(distance=d))

    before_intake_point = points[-1]
    after_intake_point = after_intake_edge.vertices()[0].point()
    # For curling around the intake, a fairly arbitrary approximation, but a fully realistic calculation would be way more effort than it'd be worth
    taut_direction = intake_middle.normal
    for p in subdivisions(before_intake_point, after_intake_point, max_length=3):
        base = p - taut_direction * 30

        ray = RayIsh(base, taut_direction)
        intersections = flatten([s.intersections(ray).points for s in intake_outer_surfaces_extended])
        if intersections:
            points.append(min(intersections, key=lambda p: p.distance(base)))

    c, a, b = after_intake_edge.curve()
    ad = c.length(0, a)
    bd = c.length(0, b)
    for d in subdivisions(ad, bd, max_length=5):
        points.append(c.value(distance=d))

    return points


# Previously, we used a bunch of complicated math for this, but it ended up being about the same as "perpendicularly project the cloth lip onto a plane". So now we just do that.
@run_if_changed
def chin_cloth_neck_points():
    neck_normal = Direction(0, -1, 0.3)
    neck_plane = Plane(temple_top + TowardsBackOfHead*neck_leeway, neck_normal)
    result = []
    for p in chin_cloth_shield_points:
        result.append(p.projected(neck_plane))
    return result

@run_if_changed
def chin_cloth_3d():
    return BSplineSurface([chin_cloth_shield_points, chin_cloth_neck_points], BSplineDimension(degree =1))


# It's now trivial to unroll the 3D shape, which is a generalized cone with a planar edge, and add a small leeway around all edges for practicalities of sewing.
chin_cloth_leeway = top_cloth_leeway
@run_if_changed
def chin_cloth_flat():
    flat_shield_points = [Point(0,chin_cloth_shield_points[0].distance (chin_cloth_neck_points[0]))]
    for (s1,s2), (n1,n2) in zip(pairs (chin_cloth_shield_points),pairs (chin_cloth_neck_points)):
        x = flat_shield_points[-1][0] + n1.distance(n2)
        y = s2.distance(n2)
        flat_shield_points.append (Point(x,y,0))
    exact_wire = Wire([
        Edge(BSplineCurve(flat_shield_points)),
        Point(flat_shield_points[-1][0], 0, 0),
        Point(0, 0, 0),
    ], loop = True)
    result = exact_wire.offset2D(chin_cloth_leeway)

    save_inkscape_svg("chin_cloth", result)
    return result

