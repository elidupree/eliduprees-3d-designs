import math

from pyocct_system import *
from gears import InvoluteGear

initialize_pyocct_system()

inch = 25.4

shank_short_radius = inch / 8
shank_long_radius = shank_short_radius / math.cos(math.tau / 12)
lego_shaft_diameter = 4.75

def hex_shank(length, indent = True):

    shank = Face(Wire([
        Point(shank_long_radius, 0, 0) @ Rotate(Up, degrees=i * 60)
        for i in range(6)
    ], loop=True)).extrude(Up * length)

    if indent:
        indentation_result_radius = inch * 3 / 32
        indentation_cut_halfwidth = inch * 3 / 32
        knob_length = inch * 5 / 16
        # algebra:
        # indentation_cut_center_x - indentation_result_radius = sqrt((indentation_cut_width/2)**2 + (indentation_cut_center_x - shank_short_radius)**2)
        # solve for indentation_cut_center_x:
        indentation_cut_center_x = (
                                               indentation_result_radius ** 2 - shank_short_radius ** 2 - indentation_cut_halfwidth ** 2) / (
                                       2*(indentation_result_radius - shank_short_radius))
        indentation_cut_radius = indentation_cut_center_x - indentation_result_radius
        indentation = Face(
            Circle(Axes(Point(indentation_cut_center_x, 0, length - knob_length - indentation_cut_halfwidth), Back),
                   indentation_cut_radius)).revolve(Up)

        shank = shank.cut(indentation)
    shank = Chamfer(shank, [(e, 1.5) for e in shank.edges() if e.bounds().min()[2] > length - 0.01])

    #preview (shank)
    return shank


def stirrer(head_radius, fin_height = shank_long_radius):
    length = 4 * inch


    shield_size = 10

    shield = Vertex(shield_size,0,length-24).extrude(Right*0.8).extrude(Vector(-50, 0, -50)).intersection(HalfSpace(Origin, Right)).revolve(Up)

    fin_thickness = 0.8
    fin = Vertex(0, -shank_long_radius/2, 0).extrude(Vector(0, shank_long_radius-fin_thickness, fin_height)).extrude(Back*fin_thickness).extrude(Right*head_radius)

    return Compound(hex_shank(length), shield, [fin @ Rotate(Up, degrees=i * 60 + 30)
                                                for i in range(6)])


@run_if_changed
def stirrer_1():
    result = stirrer(13)
    save_STL("stirrer_1", result)
    return result

@run_if_changed
def stirrer_2():
    result = stirrer(25, 10)
    save_STL("stirrer_2", result)
    return result


def lego_shaft_hole(length, end_closed):
    contact_leeway = 0.1
    chamfer = 1.5
    def hoop(expand, z):
        return Vertex(Origin + Up*z).extrude(Left*(1.9 + 2*expand), centered=True).extrude(Back*(lego_shaft_diameter + 2*expand), centered=True).outer_wire()
    hoops = [hoop(chamfer + contact_leeway, 0), hoop(contact_leeway, chamfer)]
    if end_closed:
        hoops += [hoop(contact_leeway, length - 4), hoop(contact_leeway - 0.15, length)]
    else:
        hoops += [hoop(contact_leeway, length - chamfer), hoop(chamfer + contact_leeway, length)]

    cut = Loft(hoops, ruled=True, solid=True)
    return Compound(cut, cut @ Rotate(Up, degrees=90))


@run_if_changed
def drill_to_lego_shaft():
    result = hex_shank(inch)
    sheath = Face(Circle(Axes(Origin, Up), 6)).extrude(Up*9)
    sheath = Loft([
        Wire(Circle(Axes(Origin, Up), 8)),
        Wire(Circle(Axes(Origin + Up*1, Up), 8)),
        Wire(Circle(Axes(Origin + Up*3, Up), 6)),
        Wire(Circle(Axes(Origin + Up*9, Up), 6)),
    ], ruled=True, solid=True)
    cut = lego_shaft_hole(length = 9, end_closed = True)
    result = Compound(result, sheath).cut(cut)
    save_STL("drill_to_lego_shaft", result)
    return result


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

@run_if_changed
def cardboard_roller_stuff():
    crusher_diameter = 25.9
    crush_to_width = 1.0
    shaft_distance = crusher_diameter + crush_to_width

    #gear = read_brep("involute_gear_12teeth_1pitchrad_fixed.brep")
    # gear = read_brep("involute_gear_12teeth_1pitchrad.brep")
    # gear = Wire(sorted_points_from_edges(gear.edges()))
    # gear.write_brep("involute_gear_12teeth_1pitchrad_fixed.brep")
    gear = InvoluteGear(12, pitch_radius=shaft_distance/2).shape

    #gear = gear @ Scale((crusher_diameter + crush_to_width)/2)
    #preview(gear, gear.offset2D(-0.2))
    #gear = gear.offset2D(-0.2)
    #chamfer = 1.2
    thickness = 6
    # hoops = [
    #     gear.offset2D(-0.2 - chamfer),
    #     gear.offset2D(-0.2) @ Translate(Up*chamfer),
    #     gear.offset2D(-0.2) @ Translate(Up*(thickness-chamfer)),
    #     gear.offset2D(-0.2 - chamfer) @ Translate(Up*thickness),
    # ]
    # preview(hoops)
    # gear = Loft(hoops[:2], ruled=True, solid=True)
    gear = gear.extrude(Up*thickness)
    #gear = Chamfer(gear, [(e, chamfer) for e in gear.edges()])
    gear = gear.cut(lego_shaft_hole(length = thickness, end_closed = False))
    save_STL("cardboard_roller_drive_gear", gear)

    r1 = lego_shaft_diameter/2 + 0.1
    r2 = r1 + 3.0
    bar = Vertex(Origin).extrude(Right*shaft_distance).extrude (Back * r2*2, centered = True).extrude (Up * 3)
    centers = [Origin, Origin + Right*shaft_distance]
    bar = Compound(bar, [Face(Circle(Axes(p, Up), r2)).extrude (Up * 3) for p in centers])
    bar = bar.cut([Face(Circle(Axes(p, Up), r1)).extrude (Up * 3) for p in centers])
    #bar = bar.extrude (Up * 3)
    save_STL("cardboard_roller_bar", bar)

    preview(bar)

def screw_threads(*, pitch, radius1, radius2, turns):
    profile = Wire([
        Point (radius1, 0, 0),
        Point (radius2, 0, pitch / 2),
        Point (radius2, 0, - pitch / 2),
    ], loop=True)
    def hoop(position):
        return profile @ Rotate(Up, Turns (position)) @ Translate(Up*position * pitch)
    hoops = [
        hoop(d)
        for d in subdivisions (-0.5, turns +0.5, max_length = 1/360)
    ]
    result = Loft(hoops, solid=True)
    #preview(result)
    return result

def hex_drive_hole_face(short_radius):
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

@run_if_changed
def bending_brake_knob():
    knob_diameter = 36
    rod_outer_diameter = 11.8
    rod_inner_diameter = 10.4
    thread_length = 13
    drive_hole_short_radius = 5
    drive_hole_long_radius = drive_hole_short_radius / math.cos(math.tau / 12)
    drive_hole_depth = 20
    a = Point(rod_outer_diameter/2 + 3, 0, 0)
    g = Point(0, 0, knob_diameter)
    f = g + Right*(drive_hole_long_radius + 2)
    h = g + Right*drive_hole_short_radius
    section = Face(Wire([
        Edge(Origin, a),
        BSplineCurve([
            a,
            a + Direction(1,0,1) * 9,
            Point(knob_diameter/2, 0, knob_diameter/2 - 2),
            Point(knob_diameter/2, 0, knob_diameter/2 + 8),
            f + Right*5 + Down*1,
            f,
            g + Right*drive_hole_short_radius + Down*1,
            g + Down*15
        ]),
        #i,
    ], loop = True))
    result = section.revolve(Up)
    result = result.cut (Face(Circle(Axes(Origin, Up), rod_outer_diameter/2-0.2)).extrude (Up * thread_length))
    result = result.cut (hex_drive_hole_face(drive_hole_long_radius).extrude (Down * drive_hole_depth) @ Translate(Up*knob_diameter))

    thread_pitch = 9.9/6
    threads = screw_threads(pitch=thread_pitch, radius1=rod_inner_diameter/2, radius2=rod_outer_diameter/2, turns = thread_length/thread_pitch)
    threads = threads.cut(HalfSpace(Origin, Down))
    result = Compound(result, threads)

    save_STL("bending_brake_knob", result)
    preview(result)

@run_if_changed
def hook_driver():
    hook_diameter = 37
    hook_thickness = 5.5
    wall_thickness = 6
    base_thickness = 10
    tool_thickness = hook_thickness + wall_thickness* 2
    tool_height = base_thickness + 12
    result = Vertex (Origin).extrude (Up*tool_height).extrude (Back *tool_thickness, centered = True).extrude (Left * hook_diameter, centered = True)
    result = result.cut (Face(Circle(Axes(Point(2.5, 0, hook_diameter/2 + base_thickness), Back), hook_diameter/2)).extrude (Back * hook_thickness, centered = True))
    result = Chamfer(result, [(e, 1.5) for e in result.edges()])

    result = result.cut (hex_drive_hole_face(short_radius=5).extrude (Up * (base_thickness-2)))

    save_STL("hook_driver", result)
    preview(result)


@run_if_changed
def nozzle_driver():
    nozzle_grip_diameter = 12.6
    nozzle_grip_radius = nozzle_grip_diameter/2
    nozzle_grip_depth = 5
    nozzle_point_leeway = 2.5
    hex_socket_short_radius = 4/2

    nozzle_grip = Face (Circle(Axes(Origin,Up), nozzle_grip_radius)).extrude(Up*nozzle_grip_depth)

    arm_thickness = 1.5

    grabber = Face(Edge(BSplineCurve([
        Point(1.5, 0, -10),
        Point(nozzle_grip_radius, 0, -3),
        Point(nozzle_grip_radius+arm_thickness/2-0.3 + 1, 0, -2),
        Point(nozzle_grip_radius+arm_thickness/2-0.3 + 0.5, 0, 0),
        Point(nozzle_grip_radius+arm_thickness/2-0.3, 0, +0.5),
        Point(nozzle_grip_radius+arm_thickness/2-0.3, 0, nozzle_grip_depth/2),
        Point(nozzle_grip_radius+arm_thickness/2-0.3, 0, nozzle_grip_depth-0.5),
        Point(nozzle_grip_radius + 1, 0, nozzle_grip_depth + 0.5),
    ])).offset2D(arm_thickness/2)).extrude(Back*5, centered=True).cut(HalfSpace(Origin+Down*(nozzle_point_leeway + hex_socket_short_radius*2 + 0.5), Down))
    #preview(grabber, nozzle_grip)
    
    result = Face (Circle(Axes(Origin+Down*nozzle_point_leeway,Up), 6)).extrude(Down*(hex_socket_short_radius*2 + 0.5))
    result = Compound(result, [grabber @ Rotate(Up, Turns(i/5)) for i in range(5)])

    # result = Vertex (Origin).extrude (Up*tool_height).extrude (Back *tool_thickness, centered = True).extrude (Left * hook_diameter, centered = True)
    # result = result.cut (Face(Circle(Axes(Point(2.5, 0, hook_diameter/2 + base_thickness), Back), hook_diameter/2)).extrude (Back * hook_thickness, centered = True))
    # result = Chamfer(result, [(e, 1.5) for e in result.edges()])
    #
    result = result.cut ((hex_drive_hole_face(short_radius=hex_socket_short_radius) @ Translate(Down*(nozzle_point_leeway+0.5))).extrude (Down * (50)))
    #
    save_STL("nozzle_driver", result)

    ring_plate_thickness = 1.6
    ring_thickness = 1.2
    ring = Face (Circle(Axes(Origin,Up), nozzle_grip_radius + arm_thickness + ring_thickness), holes = [Wire(Circle(Axes(Origin,Up), nozzle_grip_radius + arm_thickness)).reversed()])
    ring_plate = Vertex(Point(nozzle_grip_radius + arm_thickness - 0.1, 0)).extrude(Right*(ring_thickness + 6)).extrude (Back*ring_plate_thickness,centered=True)
    ring = ring.cut(Vertex(Origin).extrude(Right*100).extrude (Back*2,centered=True))
    ring = Compound(ring, [ring_plate @ Translate (Back*direction * (ring_plate_thickness/2+1)) for direction in [- 1, 1]])
    ring = ring.extrude (Up*(nozzle_grip_depth-1), centered=True)
    ring = ring.cut(Face(Circle(Axes(Origin + Right*(nozzle_grip_radius + arm_thickness + ring_thickness + 3),Back),(3-0.2)/2)).extrude(Back*100, centered=True))

    ring = ring@ Translate(Up*nozzle_grip_depth/2)
    save_STL("nozzle_driver_ring", ring)

    preview(result, nozzle_grip.wires(), ring)


def spiral_spring_winder(*, start_radius, wire_radius, wire_spacing, pitch, length):
    def hoop(turns, z, inner_radius):
        a = Point(inner_radius, 0, z)
        b = a + vector(0, 0, wire_radius)
        c = a + vector(0, 0, -wire_radius)
        d = b + vector(2, 0, 2)
        e = c + vector(2, 0, -2)
        y = min((d[0] - 1.1)/2, length + wire_radius + 2.1 - d[2])
        f = d + vector(-y*2, 0, y)
        x = min(e[0] - 1.1, e[2] + wire_radius + 2.1)
        g = e + vector(-x, 0, -x)
        h = Point(1, 0, f[2])
        i = Point(1, 0, g[2])
        #preview(a,b,c,d,e,f,g)
        profile = Wire([
            i,g,e,c,b,d,f,h
        ], loop=True)
        
        return profile @ Rotate(Up, Turns (turns))
    
    z = 0
    turns = 0
    turn_increment = 1/24
    inner_radius = start_radius
    hoops = []
    while z < length:
        hoops.append(hoop(turns, z, inner_radius))
        turns += turn_increment
        if turns > 0.5:
            z += turn_increment * pitch
            inner_radius -= wire_spacing * turn_increment
    z = length

    stop = turns + 0.5
    while turns < stop:
        hoops.append(hoop(turns, z, inner_radius))
        turns += turn_increment
    #preview(Compound(hoops))
    #preview(Compound([Face(f) for f in hoops]))
    result = Union([Loft(p, solid=True, ruled=True) for p in pairs(hoops)])
    result = (result @ Translate(Up*(wire_radius + 2.1)))
    #preview(result)
    return result

@run_if_changed
def printer_spring_winder():
    result = spiral_spring_winder(start_radius = 25, wire_radius = 1, wire_spacing = 2.5, pitch = 10, length = 40)
    #preview(result)
    result = result.cut(hex_drive_hole_face(short_radius=5).extrude (Down*10, Up * (150)))
    save_STL("printer_spring_winder", result)
    preview(result)


preview(stirrer_2)