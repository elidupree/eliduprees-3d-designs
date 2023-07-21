import math

from pyocct_system import *

initialize_pyocct_system()
pegboard_thickness = 3.87
hole_diameter = 6.75
hole_radius = hole_diameter/2

peg_height = hole_diameter / math.sqrt(2)
peg_deflection = peg_height / 4
catch_length = 4

contact_leeway_one_sided = 0.2

inch = 25.4

stiff_wall_thickness = 1.2


def peg(other_board_thickness):
    total_thickness = pegboard_thickness + other_board_thickness + contact_leeway_one_sided*2
    cap = Face(Circle(Axes(Origin, Right), hole_radius + peg_deflection)).extrude(Left*catch_length)
    shaft = Face(Circle(Axes(Origin, Right), hole_radius - contact_leeway_one_sided)).extrude(Right*(total_thickness + catch_length))
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


def peg_attachment_plate(mount_radians):
    holes_radius = inch / math.sqrt(2)
    plate_radius = holes_radius + hole_diameter

    #flare = 15
    # plate = Wire ([
    #     Point(0,0,0),
    #     Point(0,0,plate_radius),
    #     Point(flare,0,plate_radius+flare)
    # ]).extrude (Right*stiff_wall_thickness).revolve(Right)


    flare = 32
    r = Rotate(Back, radians = mount_radians)
    # plate = Compound(
    #     Vertex(Origin).extrude(Up*plate_radius*2, centered = True).extrude(Right*stiff_wall_thickness).extrude (Back *plate_radius*2, centered = True),
    #     Vertex(0, -plate_radius, 0).extrude(Up*plate_radius*2, centered = True).extrude(Right*flare).extrude (Back *stiff_wall_thickness),
    #     Vertex(0, plate_radius, 0).extrude(Up*plate_radius*2, centered = True).extrude(Right*flare).extrude (Front *stiff_wall_thickness),
    #     Vertex(0, 0, plate_radius).extrude(Vector(flare,0,flare*1.5) @ r).extrude(Direction(1.5, 0, -1)*stiff_wall_thickness @ r).extrude (Front*plate_radius*2, centered = True),
    #     Vertex(0, 0, -plate_radius).extrude(Vector(flare,0,0) @ r).extrude(Direction(0, 0, 1)*stiff_wall_thickness @ r).extrude (Front*plate_radius*2, centered = True),
    # )

    plate = Face(Wire([
        Point(0, 0, -plate_radius) + Vector(flare,0,0) @ r,
        Point(0, 0, -plate_radius),
        Point(0, 0, plate_radius),
        Point(0, 0, plate_radius) + Vector(flare,0,0),
    ], loop = True)).extrude(Back*plate_radius*2, centered = True)

    num_holes = 4*3
    # hole = Face(Circle(Axes(Point(0,0,holes_radius), Right), hole_radius + contact_leeway_one_sided)).extrude(Right*(100), centered = True)
    hole = Compound(
        Face(Circle(Axes(Point(0,0,holes_radius), Right), hole_radius + contact_leeway_one_sided)).extrude(Right*stiff_wall_thickness),
        Face(Circle(Axes(Point(stiff_wall_thickness,0,holes_radius), Right), hole_radius + peg_deflection + 1 + contact_leeway_one_sided)).extrude(Right*(catch_length + 1 + contact_leeway_one_sided*2)),
    )
    holes = [hole @ Rotate(Right, radians=i*math.tau/num_holes) for i in range(num_holes)]

    return plate.cut(holes) @ Translate(0, 0, plate_radius) @ r.inverse()


def simple_funnel(bottom_diameter, top_diameter, height):
    a = [
        Point(bottom_diameter/2, 0, 0),
        Point(top_diameter/2, 0, height),
        Point(top_diameter/2+15, 0, height+15),
    ]
    b = a + [
        Point(0, 0, height+15),
        Point(0, 0, 0),
    ]
    wall = Wire(a).extrude(Right*stiff_wall_thickness).revolve(Up)
    inside = Face(Wire(b, loop=True)).revolve(Up)
    plate = peg_attachment_plate(mount_radians = math.tau / 16) @ Translate(Left*(bottom_diameter/2 + stiff_wall_thickness*2 + catch_length + contact_leeway_one_sided*2))
    return Compound(wall, plate.cut(inside))

@run_if_changed
def blower_holder():
    result = simple_funnel(53, 54.5, 43)
    save_STL("blower_holder", result)
    return result


def hole_shrinking_washer(new_hole_radius):
    washer_thickness = 1.2
    washer = Face(Circle(Axes(Origin, Up), hole_radius + 5 - contact_leeway_one_sided)).extrude(Up*washer_thickness)
    plug = Face(Circle(Axes(Origin, Up), hole_radius - contact_leeway_one_sided)).extrude(Up*(washer_thickness+pegboard_thickness))
    new_hole = Face(Circle(Axes(Origin, Up), new_hole_radius + contact_leeway_one_sided)).extrude(Up*(washer_thickness+pegboard_thickness))
    return Compound(washer,plug).cut(new_hole)

@run_if_changed
def hole_shrinking_washer_m4():
    result = hole_shrinking_washer(2)
    save_STL("hole_shrinking_washer_m4", result)
    return result

preview(hole_shrinking_washer_m4)
preview (peg_attachment_plate(mount_radians = math.tau / 12))