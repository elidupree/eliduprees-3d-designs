import math

from pyocct_system import *

initialize_pyocct_system()
pegboard_thickness = 3.87
pegboard_hole_diameter = 6.75
pegboard_hole_radius = pegboard_hole_diameter / 2

peg_height = pegboard_hole_diameter / math.sqrt(2)
peg_deflection = peg_height / 4
catch_length = 4

contact_leeway_one_sided = 0.2

inch = 25.4

stiff_wall_thickness = 1.2


def peg(other_board_thickness):
    total_thickness = pegboard_thickness + other_board_thickness + contact_leeway_one_sided*2
    cap = Face(Circle(Axes(Origin, Right), pegboard_hole_radius + peg_deflection)).extrude(Left * catch_length)
    shaft = Face(Circle(Axes(Origin, Right), pegboard_hole_radius - contact_leeway_one_sided)).extrude(Right * (total_thickness + catch_length))
    slit = Vertex(Origin).extrude(Up*100, centered = True).extrude(Right*100).extrude (Back *peg_deflection * 2.5, centered = True)
    shaft = shaft.cut (slit)
    tips = [f for f in shaft.faces() if f.bounds().min()[0] > total_thickness + catch_length - 0.1]
    def catch(tip):
        if tip.bounds().min()[1] > 0:
            direction = Back
        else:
            direction = Front

        corner = Point(tip.vertices()[0][0], tip.vertices()[0][1])
        fill = Face (Wire ([corner, corner + Left*catch_length, corner + Left*catch_length + direction*peg_deflection], loop = True)).extrude(Up*peg_height, centered = True)
        
        return Compound(
            tip.extrude(Left*catch_length + direction*peg_deflection),
            fill
        )
    result = Compound (cap, shaft, [catch(tip) for tip in tips])
    result = result.intersection(Vertex(Origin).extrude(Up*peg_height, centered = True).extrude(Right*100, centered = True).extrude (Back *100, centered = True))
    preview(result)
    return result

@run_if_changed
def standard_peg():
    result = peg(stiff_wall_thickness)
    save_STL("standard_peg", result)
    return result


peg_attachment_plate_holes_radius = inch / math.sqrt(2)
peg_attachment_plate_radius = peg_attachment_plate_holes_radius + 4 + stiff_wall_thickness
peg_attachment_plate_width = peg_attachment_plate_radius*2

@run_if_changed
def peg_attachment_plate():
    #flare = 15
    # plate = Wire ([
    #     Point(0,0,0),
    #     Point(0,0,plate_radius),
    #     Point(flare,0,plate_radius+flare)
    # ]).extrude (Right*stiff_wall_thickness).revolve(Right)


    # flare = 32
    #r = Rotate(Back, radians = mount_radians)
    # plate = Compound(
    #     Vertex(Origin).extrude(Up*plate_radius*2, centered = True).extrude(Right*stiff_wall_thickness).extrude (Back *plate_radius*2, centered = True),
    #     Vertex(0, -plate_radius, 0).extrude(Up*plate_radius*2, centered = True).extrude(Right*flare).extrude (Back *stiff_wall_thickness),
    #     Vertex(0, plate_radius, 0).extrude(Up*plate_radius*2, centered = True).extrude(Right*flare).extrude (Front *stiff_wall_thickness),
    #     Vertex(0, 0, plate_radius).extrude(Vector(flare,0,flare*1.5) @ r).extrude(Direction(1.5, 0, -1)*stiff_wall_thickness @ r).extrude (Front*plate_radius*2, centered = True),
    #     Vertex(0, 0, -plate_radius).extrude(Vector(flare,0,0) @ r).extrude(Direction(0, 0, 1)*stiff_wall_thickness @ r).extrude (Front*plate_radius*2, centered = True),
    # )

    # plate = Face(Wire([
    #     Point(0, 0, -plate_radius) + Vector(flare,0,0) @ r,
    #     Point(0, 0, -plate_radius),
    #     Point(0, 0, plate_radius),
    #     Point(0, 0, plate_radius) + Vector(flare,0,0),
    # ], loop = True)).extrude(Back*plate_radius*2, centered = True)

    hole_radius = 2
    plate = Vertex (Origin).extrude (Left * peg_attachment_plate_width, centered = True).extrude (Back* peg_attachment_plate_width,centered = True).extrude (Up*stiff_wall_thickness)

    plate = plate.cut(Face(Circle(Axes(Origin, Up), peg_attachment_plate_holes_radius- 5)).extrude(Up*stiff_wall_thickness))

    hole_center = Point(peg_attachment_plate_holes_radius,0,0)
    num_holes = next(i for i in range(4,100, 4) if hole_center.distance(hole_center @ Rotate(Up, radians = math.tau / (i+1))) < hole_radius*2 + contact_leeway_one_sided*2 + stiff_wall_thickness)
    # hole = Face(Circle(Axes(Point(0,0,holes_radius), Right), hole_radius + contact_leeway_one_sided)).extrude(Right*(100), centered = True)
    hole = Face(Circle(Axes(hole_center, Up), hole_radius + contact_leeway_one_sided)).extrude(Up*stiff_wall_thickness)
      #  Face(Circle(Axes(hole_center + Up*stiff_wall_thickness, Right), hole_radius + peg_deflection + 1 + contact_leeway_one_sided)).extrude(Right*(catch_length + 1 + contact_leeway_one_sided*2))
    holes = [hole @ Rotate(Up, radians=(math.tau/8) + i*math.tau/num_holes) for i in range(num_holes)] + []

    rail_height = 14
    rail = Face(BSplineSurface([
        [Point(0,y,0), Point(-3 if abs(abs(y) - peg_attachment_plate_radius) > 0.01 else 0,y,4)] for y in subdivisions(-peg_attachment_plate_radius, peg_attachment_plate_radius, amount=7)
    ], v = BSplineDimension(degree=1))).extrude(Right*peg_attachment_plate_holes_radius)
    wall = Vertex (Origin).extrude (Right * peg_attachment_plate_holes_radius).extrude (Back * peg_attachment_plate_width,centered = True).extrude (Up*rail_height)
    wall = Compound(wall, rail@Translate(Up*rail_height))
    wall = wall @Translate(Left*peg_attachment_plate_radius)

    walls = Compound(
        wall,
        wall @Rotate(Up, degrees=90),
        wall @Rotate(Up, degrees=180),
        wall @Rotate(Up, degrees=270),
    )
    walls = walls.cut(Face(Circle(Axes(Origin, Up), peg_attachment_plate_radius - 1.0)).extrude(Up*100))

    # wall2 = Vertex (Origin).extrude (Back * stiff_wall_thickness).extrude (Left * peg_attachment_plate_width,centered = True).extrude (Up*(rail_height+4))

    result = Compound(
        plate.cut(holes),
        walls,
        # wall2 @Translate(Front*peg_attachment_plate_radius),
        # wall2 @Translate(Front*peg_attachment_plate_radius) @Mirror(Back),
    )
    save_STL("pegboard_rotatable_plate", result)
    preview (result)
    return result #@ Translate(0, 0, peg_attachment_plate_radius) #@ r.inverse()


# separate the plates by the appropriate distance,
# but slightly less so it pressure-fits
rail_slots_gap_radius = peg_attachment_plate_radius + 2*contact_leeway_one_sided - 0.15
rail_slots_full_radius = rail_slots_gap_radius + 6

@run_if_changed
def rail_slots():
    # s0 = 0.2
    # s1 = 1.0
    h = peg_attachment_plate_width
    # splay = (s1 - s0) * (h/2)
    #
    # lbx = 0
    # rbx = lbx + splay + 4 + stiff_wall_thickness*2
    # ltx = rbx + s0*h
    # rtx = lbx + s1*h
    # mx = lbx + stiff_wall_thickness + s1*h/2
    # block = Face(Wire([
    #     Point(lbx, 0, 0),
    #     Point(rbx, 0, 0),
    #     Point(rtx, 0, h),
    #     Point(ltx, 0, h),
    # ], loop=True)).extrude(Back*3, Front*3)

    cc = Face(Circle(Axes(Origin,Front),h/2)).cut(Face(Circle(Axes(Origin,Front),h/2 - 1.2))).extrude(Front*16, centered=True).cut(HalfSpace(Origin, Down))
    c = Vertex(-2, 0, 0).extrude(Vector(4,3,0)).extrude(Front*4).extrude(Up*100, centered = True).cut(cc)
    w = Compound(
        Vertex(0, 0, 0).extrude(Right*100).extrude(Back*6).extrude(Down*h),
        Face(Circle(Axes(Origin,Front),h/2)).extrude(Back*6).cut(HalfSpace(Point(-2, 0, 0), Left))
    )
    def cut(angle):
        return c @ Rotate(Front, radians=angle)
    def wall(angle):
        return w @ Rotate(Front, radians=angle)

    filter = Vertex(4 + stiff_wall_thickness, 0, 0).extrude(Left*100, centered=True).extrude(Front*100, centered=True).extrude(Up*h, centered=True)
    topwall = Vertex(0, 0, 0).extrude(Right*100).extrude(Back*6).extrude(Up*h)

    angles = [math.tau / 8.5, math.tau / 12, math.tau / 24]

    #q = cut(angles[0]).intersection(filter)
    #preview(q)
    left_bottom = min((v[2], v[0]) for v in cut(angles[-1]).intersection(filter).vertices())[1]
    right_edge = max(v[0] for v in cut(angles[0]).intersection(filter).vertices())
    filter = filter.cut(HalfSpace(Point(right_edge, 0, 0), Right))
    wall_cross_section = Compound(
        Face(Circle(Axes(Origin,Front),h/2)).intersection(
            Compound(
                HalfSpace(Point(-2, 0, 0), Right)@ Rotate(Front, radians=angles[0]),
                HalfSpace(Point(-2, 0, 0), Right)@ Rotate(Front, radians=angles[-1]),
                )
        ),
        Wire([
            Point(0,0,h/2),
            Point(5,0,0),
            Point(left_bottom,0,-h/2),
        ]).extrude(Right*100),
    ).intersection(filter)


    wall = wall_cross_section.extrude(Back*6).cut([cut(a) for a in angles]) @ Translate(Back*rail_slots_gap_radius)

    behind = wall_cross_section.extrude(Back*rail_slots_gap_radius*2, centered = True).cut (
        HalfSpace(Point(2, 0, 0), Left)@ Rotate(Front, radians=angles[0])).cut(
           HalfSpace(Point(2, 0, 0), Left)@ Rotate(Front, radians=angles[-1]),
        )

    #preview(behind)

    result = Compound(
        wall,
        wall @ Mirror(Front),
        behind
    ) @ Translate(Vector(
        -right_edge,
        0,
        h/2,
    ))
    preview(result)
    return result


def simple_funnel(height, bottom_diameter, top_diameter, flare):
    wall_thickness = 1.0
    bottom_inner_radius = bottom_diameter/2 + contact_leeway_one_sided
    bottom_outer_radius = bottom_inner_radius + wall_thickness
    a = [
        Point(bottom_diameter/2, 0, 0),
        Point(top_diameter/2, 0, height                                             wall_thickness ),
        Point(top_diameter/2+flare, 0, height+flare),
    ]
    b = a + [
        Point(0, 0, height+flare),
        Point(0, 0, 0),
    ]
    wall = Wire(a).extrude(Right*wall_thickness).revolve(Up)
    inside = Face(Wire(b, loop=True)).revolve(Up)
    #plate = peg_attachment_plate(mount_radians = math.tau / 16) @ Translate(Left*(bottom_diameter/2 + stiff_wall_thickness*2 + catch_length + contact_leeway_one_sided*2))
    rs = Compound(
        rail_slots @ Translate(Left*bottom_outer_radius),
        Face(Wire([
            Point(0, -bottom_outer_radius, 0),
            Point(0, bottom_outer_radius, 0),
            Point(-bottom_outer_radius, rail_slots_full_radius, 0),
            Point(-bottom_outer_radius, -rail_slots_full_radius, 0),
        ], loop = True)).extrude (Up*peg_attachment_plate_width)
    )
    return Compound(wall, rs.cut(inside))

@run_if_changed
def blower_holder():
    result = simple_funnel(bottom_diameter=54.1, top_diameter=56.4, height=43, flare=3.5)
    save_STL("blower_holder", result)
    return result


def hole_shrinking_washer(new_hole_radius):
    washer_thickness = 1.2
    washer = Face(Circle(Axes(Origin, Up), pegboard_hole_radius + 5 - contact_leeway_one_sided)).extrude(Up * washer_thickness)
    plug = Face(Circle(Axes(Origin, Up), pegboard_hole_radius - contact_leeway_one_sided)).extrude(Up * (washer_thickness + pegboard_thickness))
    new_hole = Face(Circle(Axes(Origin, Up), new_hole_radius + contact_leeway_one_sided)).extrude(Up*(washer_thickness+pegboard_thickness))
    return Compound(washer,plug).cut(new_hole)

@run_if_changed
def hole_shrinking_washer_m4():
    result = hole_shrinking_washer(2)
    save_STL("hole_shrinking_washer_m4", result)
    return result

#preview(hole_shrinking_washer_m4)
preview (blower_holder)