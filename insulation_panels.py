import math

from pyocct_system import *

initialize_pyocct_system()


@run_if_changed
def hoop_prototype():
    result = Face(Circle(Axes(Origin, Up), 130/2)).cut(Face(Circle(Axes(Origin, Up), 130/2 - 4))).extrude(Up * 3)
    save_STL("hoop_prototype", result)
    return result



@run_if_changed
def test_panel_1():
    outer_radius = 130/2
    wall_width = 4
    thickness = 3
    inner_radius = outer_radius - wall_width
    offsets = [0, wall_width]
    def rectish(d):
        a = Point(0, outer_radius)
        b = Point(-outer_radius, outer_radius)
        c1p = [
            a,
            a+Left*20,
            a+Left*outer_radius/2 + Front*10,
            b+Right*20,
            b,
            ]
        c1 = Edge(BSplineCurve(c1p))
        c2 = Edge(BSplineCurve([
            b+Front*10,
            #b+Front*40,
            Point(-outer_radius+20, 50),
            Point(-outer_radius, 30),
            Point(-outer_radius, -30),
            Point(-outer_radius+20, -50),
            #((b+Front*40) @ Reflect(Back)),
            ((b+Front*10) @ Reflect(Back)),
        ]))
        c3 = Edge(BSplineCurve([p @ Reflect(Back) for p in c1p[::-1]]))
        #preview(c1, c2)
        w2 = w = Wire([c1, b+Front*10, c2, b @ Reflect(Back), c3, Edge(a @ Reflect(Back), a)])
        if d != 0:
            w2 = w.offset2D(-d)
            #preview(w, w2)
        return Face(w2)
    rectangles = [
        #Vertex(Origin).extrude(Back*r*2, centered = True).extrude(Left*r).cut(Face(Circle(Axes(Origin + Left*outer_radius * 2, Up), -r + outer_radius*2.3)))
        rectish(d)
    for d in offsets]
    circles = [Face(Circle(Axes(Origin, Up), outer_radius - d)).intersection(HalfSpace(Origin + Left*20, Right)) for d in offsets]
    #preview(rectangles[0])

    inlet_ir = 1
    inlet_length = 8
    inlet_shapes = [
        Vertex(Origin).extrude(Back*thickness, centered = True).extrude(Up*thickness, centered = True),
        Face(Circle(Axes(Origin, Left), inlet_ir)),
    ]
    inlet_shapes = [[s.extrude(Left*(wall_width + inlet_length)) @ Translate(Left*inner_radius + Back*(outer_radius - wall_width - inlet_ir)*dir) for s in inlet_shapes] for dir in [-1, 1]]

    frame = Compound(rectangles[0], circles[0]).cut([rectangles[1], circles[1]]).extrude(Up * thickness, centered = True)
    #preview(frame)
    result = Compound(frame, [c[0] for c in inlet_shapes]).cut([c[1] for c in inlet_shapes])

    panels_period = 8
    num_panels = 4

    channel_wall_thickness = 1.0
    channel_id = thickness + 2.4
    channel_od = channel_id + channel_wall_thickness*2
    channel_ds = [channel_od, channel_id]
    inlet_cover_shapes = [
        Vertex(Origin).extrude(Back*d, centered = True).extrude(Up*d, centered = True).extrude(Left*(inlet_length + channel_wall_thickness)) for d in channel_ds
    ]
    inlet_cover_shapes = [
        [s @ Translate(Back*x) for s in inlet_cover_shapes]
        for x in subdivisions (-panels_period*num_panels/2, panels_period*num_panels/2, amount = num_panels)
    ]
    main_channel_shapes = [
        Vertex(Origin + Left*(inlet_length + channel_od/2)).extrude(Left*d, centered = True).extrude(Up*d, centered = True).extrude(Back*(panels_period*num_panels + d), centered = True) for d in channel_ds
    ]
    nozzle_widest = 15
    nozzle_narrow = 9
    nozzle_shapes = [
        Loft([
            Vertex(Origin).extrude(Back*(channel_od - inset*2), centered = True).extrude(Up*(channel_od - inset*2), centered = True).outer_wire(),
        ]+[
            Wire(Circle(Axes(Origin + Left*d, Left), nozzle_widest/2 - inset)) for d in [5, 15]
        ]+[
            Wire(Circle(Axes(Origin + Left*d, Left), nozzle_narrow/2 - inset)) for d in [18, 22]
        ], solid = True, ruled=True) @ Translate(Left*(inlet_length + channel_od/2 + channel_id/2))
        for inset in [0, channel_wall_thickness]
    ]
    distributor_shapes = inlet_cover_shapes + [main_channel_shapes, nozzle_shapes]
    distributor = Compound ([s[0] for s in distributor_shapes]).cut([s[1] for s in distributor_shapes])
    split = HalfSpace(Origin, Up)
    distributor = distributor.intersection(split)
    # preview(distributor.cut(split), distributor.intersection(split) @ Translate(Left*80))
    # preview (inlet_cover_shapes, main_channel_shapes)


    single_nozzle_shapes = [
        Loft([
                 Vertex(Point(0,0,d)).extrude(Back*(thickness + 1.3 + 0.8 + (channel_wall_thickness - inset)*2), centered = True).extrude(Left*(thickness + 0.8 + (channel_wall_thickness - inset)*2), centered = True).outer_wire()
                for d in [-inlet_length, 0]
             ]+[
                 Wire(Circle(Axes(Origin + Up*d, Up), nozzle_widest/2 - inset)) for d in [10, 20]
             ]+[
                 Wire(Circle(Axes(Origin + Up*d, Up), nozzle_narrow/2 - inset)) for d in [30, 35]
             ], solid = True, ruled=True)
        for inset in [0, channel_wall_thickness]
    ]

    single_nozzle = single_nozzle_shapes[0].cut (single_nozzle_shapes[1])

    #preview (single_nozzle)



    save_STL("test_panel_1", result)
    save_STL("single_nozzle", single_nozzle)
    save_STL("test_panel_1_distributor", distributor)
    #preview(distributor)

    return result




preview(test_panel_1)