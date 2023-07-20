import math

from pyocct_system import *

initialize_pyocct_system()

wall_thickness = 0.8
post_diameter = 35.15
post_bulge_thickness = 6.36
post_bulge_radius = post_diameter/2 + post_bulge_thickness
post_bulge_height = 49.73
camera_foot_max_width = 44.16
camera_foot_max_thickness = 11.3
camera_foot_length = 56
camera_neck_raise = 17
shelf_length = 33
contact_leeway = 0.3
flare = 15

shelf_z = 0 - camera_neck_raise
post_bulge_radius = post_diameter/2 + post_bulge_thickness
post_center = Origin+Back*post_bulge_radius

@run_if_changed
def post_bulge():
    return Face(Circle(Axes(post_center, Up), post_bulge_radius)).extrude(Up*post_bulge_height, centered=True)

@run_if_changed
def post_bulge_exclusion():
    radius = post_diameter/2 + post_bulge_thickness
    cross_section = Face (Wire([
        Point(0,0,-post_bulge_height/2 - contact_leeway),
        Point(0,0,post_bulge_height/2 + contact_leeway),
        Point(0,post_bulge_thickness, post_bulge_height/2 + contact_leeway + post_bulge_thickness),
        Point(0,radius, post_bulge_height/2 + contact_leeway + post_bulge_thickness),
        Point(0,radius, -post_bulge_height/2 - contact_leeway),
    ], loop = True))
    return cross_section.revolve(Axis(post_center, Up))

@run_if_changed
def post():
    radius = post_diameter/2
    return Face(Circle(Axes(post_center, Up), radius + contact_leeway)).extrude(Up*300, centered=True)

@run_if_changed
def post_exclusion():
    return Compound(post_bulge_exclusion, post)

funnel_shadow = None
@run_if_changed
def camera_foot_funnel():
    global funnel_shadow
    def column(base, out):
        return [
            base + Down*40,
            base + Down*30,
            base + Down*20,
            base + Down*10,
            base + out * flare,
        ]

    column_specs = [
        (Point(-camera_foot_max_width/2 - contact_leeway, -wall_thickness, shelf_z), Left*1, Left*1+Back*1),
        (Point(-camera_foot_max_width/2 - contact_leeway, -wall_thickness -(camera_foot_max_thickness + contact_leeway*2), shelf_z), Left*1+Front*1, Left*1+Front*1),
        (Point(camera_foot_max_width/2 + contact_leeway, -wall_thickness -(camera_foot_max_thickness + contact_leeway*2), shelf_z), Right*1+Front*1, Right*1+Front*1),
        (Point(camera_foot_max_width/2 + contact_leeway, -wall_thickness, shelf_z), Right*1, Right*1+Back*1),
    ]

    def solid(wall_offset):
        columns = [column(base + wallout*wall_offset, out) for base, out, wallout in column_specs]
        faces = [Face(BSplineSurface(rows, BSplineDimension(degree =1))) for rows in pairs(columns, loop=True)] + [
            Face(Wire([c[0] for c in columns], loop=True)),
            Face(Wire([c[-1] for c in columns], loop=True)),
        ]
        #preview(faces)
        return Solid(Shell(faces))

    funnel_shadow = Compound(
        Face(BSplineSurface([column(base + wallout*wall_thickness, out) for base, out, wallout in [column_specs[0], column_specs[-1]]], BSplineDimension(degree =1))).extrude(Back*100),
        Vertex(0, -wall_thickness, shelf_z).extrude(Right*(camera_foot_max_width + 2*contact_leeway + 2*wall_thickness + 2*flare), centered=True).extrude(Up*100).extrude(Back*100)
    )
    # def column(z, thickness):
    #     return Vertex(Origin + Up*z).extrude(Left*(camera_foot_max_width + contact_leeway*2), centered=True).extrude(Front*(wall_thickness), Front*(wall_thickness + contact_leeway + thickness + contact_leeway)).outer_wire()
    #
    # hoops = [
    #     hoop(shelf_z-camera_foot_length, camera_foot_max_thickness),
    #     hoop(shelf_z-15, camera_foot_max_thickness),
    #     hoop(shelf_z, camera_foot_max_thickness + 15),
    #     ]
    # preview(Loft(hoops, ruled=True))
    # return Loft(hoops, ruled=True, solid=True)
    result = solid(wall_thickness).cut(solid(0))
    #preview(result)
    return result

@run_if_changed
def main_block():
    b = post_bulge_thickness + 6
    b = -(post_bulge_radius - math.sqrt(post_bulge_radius**2 + (33/2)**2))
    print(b)
    top_block = Loft([
        Vertex(0, -wall_thickness, shelf_z).extrude(Right*(camera_foot_max_width + 2*contact_leeway + 2*wall_thickness + 2*flare), centered=True).extrude(Back*(b + wall_thickness)).outer_wire(),
        Vertex(0, -wall_thickness, post_bulge_height/2 + post_bulge_thickness + 10).extrude(Right*(30), centered=True).extrude(Back*(b + wall_thickness)).outer_wire(),
    ], solid = True, ruled = True)
    #top_block = Vertex(Origin).extrude(Up*-post_bulge_height/2, Up*(post_bulge_height/2 + post_bulge_thickness)).extrude(Back*(b), Front*wall_thickness).extrude(Left*100, centered=True)

    bottom_block = Vertex(Origin).extrude(Up*shelf_z, Up*(shelf_z - 40)).extrude(Back*(b), Front*(wall_thickness + camera_foot_max_thickness + wall_thickness)).extrude(Left*100, centered=True)
    bottomer_block = Vertex(Origin).extrude(Down*(post_bulge_height/2 + contact_leeway), Up*(shelf_z - 40)).extrude(Back*(30), Front*(wall_thickness + camera_foot_max_thickness + wall_thickness)).extrude(Left*post_diameter*0.7, centered=True)
    
    block = Compound(top_block, bottom_block, bottomer_block)
    block = block.cut(post_exclusion).intersection(funnel_shadow)
    return block

@run_if_changed
def pole_grabber():
    ring = Face(
        Circle(Axes(post_center, Up), post_diameter/2 + contact_leeway + 1.2),
        holes = [Wire(Circle(Axes(post_center, Up), post_diameter/2 + contact_leeway)).reversed()]
    ).extrude (Down*(post_bulge_height/2 + contact_leeway), Up*(shelf_z - 40))

    cut = Vertex (post_center).extrude (Right *3, centered = True).extrude (Up*1000, centered = True).extrude (Back * 100)
    return ring.cut (cut)

@run_if_changed
def camera_bracket():
    a = post_center + Front*(post_bulge_radius + wall_thickness) + Up*(post_bulge_height/2 + post_bulge_thickness + 5)
    notch = Face(Wire(
        [a + Down*2 + vector(0, -30, -30), a + Down*2, a + Up*2, a + Up*2 + vector(0, -30, 30),],
        loop = True
    )).revolve(Axis(post_center, Up))

    result = Compound(main_block.cut(notch), camera_foot_funnel, pole_grabber)
    save_STL("camera_bracket", result)
    return result


preview (camera_bracket)