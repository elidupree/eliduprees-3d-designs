import math

from pyocct_system import *
from depthmap2 import load_depthmaps_from_specfile, Depthmap
from svg_utils import load_Inkscape_BSplineCurve

initialize_pyocct_system()

CPAP_head_diameter = 31
CPAP_head_length = 45
CPAP_hose_diameter = 22
CPAP_head_radius = CPAP_head_diameter/2
CPAP_hose_radius = CPAP_hose_diameter/2
halfish_sample_count = 200
sample_count = halfish_sample_count*2-1
wall_thickness = 3

depthmaps = load_depthmaps_from_specfile("face_mold_depthmaps_spec.json", ["merged", "outset_1mm"])

def front_curve_from_layout_file(id):
    # I've laid out some curves as front-views in Inkscape:
    return load_Inkscape_BSplineCurve("glasses_airspace_layout.svg", id) @ Mirror(Right) @ Rotate(Left, Degrees(90))

def front_depthmap_sample_point(depthmap, x_or_p, z = None, avoid_chin = False):
    if z is None:
        x = x_or_p[0]
        z = x_or_p[2]
    else:
        x = x_or_p
    z2 = z
    if avoid_chin:
        z2 = max(z, -80)
        dangle = z2 - z
        dangle_translation = Translate(0, dangle/7 - dangle**2/350, -dangle)
    p = Point(x, 100, z2)
    p2 = depthmap.projected_to_smoothed_surface(p, 1, default=p)
    if avoid_chin:
        p2 = p2 @ dangle_translation
    if p2[1] > 100:
        return p
    return p2

def resample_curve_front(depthmap, curve):
    points_stageright_leftwards = curve.subdivisions(amount=halfish_sample_count)
    points = [p @ Mirror(Right) for p in points_stageright_leftwards] + points_stageright_leftwards[-1::-1]
    return BSplineCurve([front_depthmap_sample_point(depthmap, p) for p in points])

@run_if_changed
def mask_top_top_curve():
    return resample_curve_front(depthmaps["merged"], front_curve_from_layout_file("helmetmask_top_top"))

@run_if_changed
def mask_top_bottom_curve():
    return resample_curve_front(depthmaps["merged"], front_curve_from_layout_file("helmetmask_top_bottom"))

@run_if_changed
def outer_x():
    return mask_top_top_curve.position(parameter=0)[0]

@run_if_changed
def putative_face_surface():
    resolution = 5
    return BSplineSurface([[front_depthmap_sample_point(depthmaps["merged"],x,z) for z in subdivisions(-142, 80, max_length=resolution)] for x in subdivisions(-80,80,max_length=resolution)])

@run_if_changed
def putative_CPAP():
    base_point = Point(-CPAP_head_radius*1.5, -5, -125)
    d = Direction(0,-0.12,1)
    return Compound(
        Face(Circle(Axes(base_point, d), CPAP_head_radius)).extrude(d*CPAP_head_length),
        Face(Circle(Axes(base_point, d), CPAP_hose_radius)).extrude(d*-50),
        )

def shell_control_points(depthmap, z, inset=0):
    x = outer_x
    p1 = front_depthmap_sample_point(depthmap, x, z, avoid_chin = True)
    p2 = front_depthmap_sample_point(depthmap, -x, z, avoid_chin = True)
    y2 = -35 + (z+85)**2/300

    return [p1 + Left*inset,
            Point(x-2-inset, y2+15+inset, z),
            Point(x/2, y2+inset, z),
            Point(-x/2, y2+inset, z),
            Point(-(x-2)+inset, y2+15+inset, z),
            p2 + Right*inset]

# @run_if_changed
# def shell_rows():
#     z0 = mask_top_bottom_curve.position(parameter=0)[2] - 3
#     return [shell_control_points(z) for z in subdivisions(z0, -140, max_length = 5)]

def shell_sample_points(depthmap, z, inset=0):
    return BSplineCurve(shell_control_points(depthmap, z, inset)).subdivisions(amount=sample_count)

@run_if_changed
def outer_surface_rows():
    rows = [
        # [front_depthmap_sample_point(depthmaps["outset_1mm"], x, z) for x in subdivisions(outer_x-0.01, -outer_x+0.01, amount=sample_count)]
        # for z in [10,8,6,4,2,0,-4,-7,-10,-14,-18]
        [front_depthmap_sample_point(depthmaps["outset_1mm"], p[0], Between(p[2], min(p[2]-1, max(mask_top_bottom_curve.position(x=p[0])[2], -18)), frac)) for p in mask_top_top_curve.subdivisions(amount=sample_count)]
        for frac in subdivisions(0,0.6, amount=20)+[0.8,1]
    ] + [shell_sample_points(depthmaps["outset_1mm"], z) for z in [-40] + subdivisions(-60, -140, amount=10)]

    return rows
            #.cut(Edge(mask_top_top_curve).extrude(Front*100, centered=True).extrude(Up*100))

@run_if_changed
def outer_surface():
    return BSplineSurface(outer_surface_rows)

@run_if_changed
def inner_surface_without_face():
    inset = wall_thickness
    rows = [
        mask_top_bottom_curve.subdivisions(start_x = outer_x-inset, end_x = -outer_x +inset, amount=sample_count)
    ] + [shell_sample_points(depthmaps["merged"], z, inset=inset) for z in [-55] + subdivisions(-65, -140, amount=10)]
    

    return BSplineSurface(rows)

@run_if_changed
def inner_surface():
    def sample(p):
        if (abs(p[0]) > outer_x - wall_thickness) or p[2] > -18:
            front_depthmap_sample_point(depthmaps["merged"], p, avoid_chin=True)
        i = inner_surface_without_face.intersections(RayIsh(p, Back*1000))
        if len(i.points) > 0:
            return i.point()
        return front_depthmap_sample_point(depthmaps["merged"], p, avoid_chin=True)
    return BSplineSurface([[sample(p) for p in row] for row in outer_surface_rows])

# @run_if_changed
# def face_surface_for_cutting():
#     resolution = 0.5
#     return BSplineSurface([[front_depthmap_sample_point(depthmaps["merged"],x,z,avoid_chin=True) for z in subdivisions(-142, 10, max_length=resolution)] for x in subdivisions(outer_x+resolution,-outer_x-resolution,max_length=resolution)])

# @run_if_changed
# def surface_joiners():
#     def select_edge(edges, cond):
#         options = [e for e in edges if cond(e)]
#         assert (len(options) == 1)
#         return options[0]
#     def select_edges(cond):
#         return select_edge(inner_surface.edges(), cond), select_edge(outer_surface.edges(), cond)
#     # def joiner_pairs(cond):
#     #     e0,e1 = select_edges(cond)
#     #     return [[a,b] for a,b in zip(e0.trimmed_curve().subdivisions(amount=sample_count), e1.trimmed_curve().subdivisions(amount=sample_count))]
#     def face_sample(p):
#         return front_depthmap_sample_point(depthmaps["merged"], p, avoid_chin=True)

#     ei,eo = select_edges(lambda e: e.bounds().max()[2] < -80)
#     # result = [Loft(Wire(ei), Wire(eo), ruled=True)]
#     # result = [Face(Wire(ei, ))]
#     result = []
#     face_conditions = [
#         lambda e: e.bounds().max()[0] < 0,
#         lambda e: e.bounds().min()[0] > 0,
#         lambda e: e.bounds().min()[2] > -80,
#     ]
#     def face_row(a,b):
#         return [face_sample(p) for p in subdivisions(a,b,amount=20)]
#     for cond in face_conditions:
#         ei, eo = select_edges(cond)
#         ci, co = ei.curve()[0], eo.curve()[0]
#         cp = co.poles()
#         preview(ci, co)
#         assert (len(cp) == len(ci.poles()))
#         face_rows = [[Between(a,b,frac) for a,b in zip(ci.poles(), cp)] for frac in subdivisions(0,1, amount=20)]
#         result.append(Face(BSplineSurface(face_rows)))
#         result.append(Face(BSplineSurface([face_rows[-1], cp], u=BSplineDimension(degree=1))))
#         # result.append(Loft(Wire(BSplineCurve(rows[-1])), Wire(eo), ruled=True))

#         # pairs = joiner_pairs(cond)
#         # face_rows = [face_row(a,b) for a,b in pairs]
#         # to_face_rows = [[b, face_sample(b)] for a,b in pairs]
#         # result.append(BSplineSurface(face_rows))
#         # result.append(BSplineSurface(to_face_rows, v = BSplineDimension(degree=1)))
#     # preview(result)
#     return result


# @run_if_changed
# def mask_solid():
#     return outer_surface.extrude(Back*50).cut(inner_surface.extrude(Back*100) @ Translate(Down*0.01)).cut(Face(face_surface_for_cutting).extrude(Back*100))

# @run_if_changed
# def mask_solid():
#     for a, b in 

preview(
    putative_face_surface,
    mask_top_top_curve,
    mask_top_bottom_curve,
    putative_CPAP,
    # [BSplineCurve(row) for row in shell_rows],
    # [BSplineSurface([mask_top_bottom_curve.poles(), BSplineCurve(shell_rows[2]).subdivisions(amount=sample_count)], u=BSplineDimension(degree=1))],
    outer_surface,

    inner_surface @ Translate(Front*300),
    outer_surface @ Translate(Front*300),
    # Compound(surface_joiners) @ Translate(Front*300),
    # (outer_surface @ Translate(Front*300)).vertices(),
    # mask_solid @ Translate(Front*300)
    )