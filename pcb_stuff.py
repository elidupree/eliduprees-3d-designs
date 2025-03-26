import math

from pyocct_system import *
from gcode_stuff.gcode_utils import *
from pyocct_utils import wallify

initialize_pyocct_system()

@run_if_changed
def led_strip_prototype():
    led_width = 2.75
    led_length = 3.5
    led_thickness = 0.9
    resistor_width = 1.4
    resistor_length = 2.2
    resistor_thickness = 0.6
    wire_thickness = 0.6
    wall_thickness = 1.0

    def component_cut(width, length, thickness):
        return Vertex(Origin).extrude(Right*width).extrude(Back*length).extrude(Up*0.1, Down*thickness)

    led_cut = component_cut(led_width, led_length, led_thickness)
    resistor_cut = component_cut(resistor_width, resistor_length, resistor_thickness)
    resistor_corner = Point(led_width + wall_thickness, 0, 0)

    component_cuts = [led_cut @ Translate(Back*(led_length+wall_thickness)*i) for i in range(3)]+[
        resistor_cut @ Translate(resistor_corner - Origin)
    ]
    wires = [Vertex(Origin).extrude(Back*2, centered=True) @ Translate(led_width/2, (led_length + wall_thickness)*(i + 1)) for i in range(3)]+[
        Edge(Point(led_width/2, 0.6, 0), resistor_corner+Vector(resistor_width/2, 0.2, 0)),
        Edge(resistor_corner+Vector(resistor_width/2, resistor_length-0.2, 0), resistor_corner+Vector(resistor_width/2, led_length*4)),
    ]
    wire_cuts = [e.extrude((Direction(e.vertices()[1].point() - e.vertices()[0].point())*wire_thickness) @ Rotate(Up, Degrees(90)), centered=True).extrude(Up*wire_thickness) for e in wires]

    block = Vertex(Origin).extrude(Down*(led_thickness+0.2), Up*(wire_thickness+0.2)).extrude(Left*wall_thickness, Right*(led_width+resistor_width+2)).extrude(Front*wall_thickness, Back*(led_length*3 + wall_thickness*4))

    # preview(wire_cuts, component_cuts)
    over_wires = HalfSpace(Origin+Up*wire_thickness, Up)
    bottom_part = block.cut([component_cuts, wire_cuts, over_wires])
    top_part = Compound(block.intersection(wire_cuts), block.intersection(over_wires))

    middle_part = bottom_part.intersection(HalfSpace(Origin+Up*0.1, Up))

    save_STL("led_strip_prototype_bottom", bottom_part)
    export("led_strip_prototype_bottom.stl", "led_strip_prototype_bottom_1.stl")
    save_STL("led_strip_prototype_middle", middle_part)
    export("led_strip_prototype_middle.stl", "led_strip_prototype_middle_1.stl")
    save_STL("led_strip_prototype_top", top_part)
    export("led_strip_prototype_top.stl", "led_strip_prototype_top_1.stl")

    preview(bottom_part.cut(HalfSpace(Origin+Up*0.1, Up)) @ Translate(Left*8), middle_part, top_part @ Translate(Right*8))


@run_if_changed
def wall_thickness_test():
    commands = [zero_extrusion_reference(), fastmove(-50,-50, 0.1)]
    z = 0
    for i in range(50):
        layer_height = 0.1 + i*0.2/50
        z += layer_height
        commands.append(g1(z=z, f_mm_s=1000))
        for k in range(4):
            y = -50 + k * 3
            line_width = 0.3 + k*0.1
            commands.append(g1(y=y, f_mm_s=1000))
            js = range(100)
            if k % 2 == 1:
                js = reversed(js)
            for j in js:
                x = j - 50
                speed = (math.floor(j / 5) + 1)*2.5
                # speed = j+1
                commands.append(g1(x=x, f_mm_s=speed, eplus_cross_sectional_mm2=layer_height*line_width))

    export_string(wrap_gcode("\n".join(commands)), "wall_thickness_test_1.gcode")


@run_if_changed
def constant_extrusion_rate_test():
    commands = [zero_extrusion_reference(), fastmove(-50,-50, 0.1)]
    #extrusion_rate = 0.5 # mm^3/s
    z = 0
    for i in range(50):
        layer_height = 0.1 + i*0.2/50
        z += layer_height
        commands.append(g1(z=z, f_mm_s=1000))
        extrusion_rate = 0.5+i*18/50
        # fan_speed = math.floor(i/10)*math.floor(255/4)
        # if fan_speed == 0:
        #     commands.append("M107")
        # else:
        #     commands.append(f"M106 F{fan_speed}")
        for k in range(2):
            y = -50 + k * 3
            line_width = 0.4 + k*0.2
            commands.append(g1(y=y, f_mm_s=1000))
            js = range(100)
            if k % 2 == 1:
                js = reversed(js)
            for j in js:
                # layer_height = 0.1 + j*0.2/100
                x = j - 50
                z = layer_height*(i+1)
                cross_section_area = layer_height*line_width
                commands.append(g1(x=x, z=z, f_mm_s=extrusion_rate/cross_section_area, eplus_cross_sectional_mm2=cross_section_area))

    export_string(wrap_gcode("\n".join(commands)), "constant_extrusion_rate_test_3.gcode")


class ConstantExtrusionRoute:
    def __init__(self, extrusion_rate, starting_position, /, max_acceleration=500, layer_height=0.3, nozzle_width = 0.4):
        self.position = starting_position
        self.extrusion_rate = extrusion_rate
        self.max_acceleration = max_acceleration
        self.layer_height = layer_height
        self.solid_printing_speed = extrusion_rate/(nozzle_width*layer_height)
        self.commands = [zero_extrusion_reference(), f"M201 X{max_acceleration} Y{max_acceleration}", f"M204 P{max_acceleration}"]

        # # positions and velocities if you turn as hard as you can starting from self.solid_printing_speed
        # self.hard_turn_points = [(Point(0,0,0), Vector(self.solid_printing_speed,0,0))]
        # while True:
        #     p,v = self.hard_turn_points[-1]
        #     if v[1] < 0:
        #         break
        #     s = v.length()
        #     # this formula means: do not let the *slower edge* of the stroke get slower than self.solid_printing_speed
        #     max_centripetal_acceleration = min(self.max_acceleration, (s - self.solid_printing_speed)*s/0.2)
        #     forwards_acceleration = math.sqrt(self.max_acceleration**2 - max_centripetal_acceleration**2)
        #     # "don't go more than 0.01mm or turn more than 1 degree before recalculating"
        #     degrees_per_second = (max_centripetal_acceleration/s)*(360/math.tau)
        #     step_size = 0.01/s
        #     if degrees_per_second > 0:
        #         step_size = min(step_size, 1/degrees_per_second)
        #     forwards = Direction(v)
        #     radial = forwards @ Rotate(Up, Degrees(90))
        #     a = radial*max_centripetal_acceleration + forwards*forwards_acceleration
        #     v2 = v + a*step_size
        #     p2 = p + Between(v, v2)*step_size
        #     self.hard_turn_points.append((p2, v2))
        #     if max_centripetal_acceleration > 0:
        #         print(max_centripetal_acceleration/self.max_acceleration, s*s/max_centripetal_acceleration, (p - Origin).length(), s, p)


    def move(self, destination, cross_section_mm2):
        self.commands.append(g1(coords=destination, eplus_cross_sectional_mm2=self.extrusion_rate/cross_section_mm2))


@run_if_changed
def constant_extrusion_led_strip_prototype():
    route = ConstantExtrusionRoute(1, Origin)
    # preview(BSplineCurve([p for p,v in route.hard_turn_points]),
    #         #Compound([Vertex(p) for p,v in route.hard_turn_points])
    #         )


@run_if_changed
def springy_led_strip_prototype():

    led_width = 2.75
    led_length = 3.5
    led_thickness = 0.9
    resistor_width = 1.4
    resistor_length = 2.2
    resistor_thickness = 0.6

    wire_width = 0.6
    wall_thickness = 0.5
    main_corner_outset = wall_thickness/2
    component_vertical_leeway = 0.1
    component_lip_thickness = 0.2
    component_chamfer = 0.3
    chamfer_corner_outset = main_corner_outset/3

    def component_holder(width, length, thickness, max_component_thickness):
        def row_points(z, outset, corner_outset):
            def corner_points(dx, dy):
                l = length + outset*2
                w = width + outset*2
                c = Point(l/2*dx,w/2*dy,z)
                points = [
                    c + Left*dx*length/4,
                    c + Left*dx*length/6,
                    c + Back*dy*corner_outset,
                    c + Back*dy*corner_outset + Right*dx*corner_outset,
                    c + Right*dx*corner_outset,
                    c + Front*dy*width/6,
                    c + Front*dy*width/4,
                ]
                if dx*dy > 0:
                    return points[::-1]
                else:
                    return points

            return [
                p
                for dx, dy in [(-1,-1),(1,-1),(1,1),(-1,1)]
                for p in corner_points(dx, dy)
            ]
        # wall = Wire(BSplineCurve(row_points(0, 0), BSplineDimension (periodic = True))).offset2d(wall_thickness, fill = True).extrude (Up*component_vertical_leeway, Down*thickness)
        frames = [Wire(BSplineCurve(points, BSplineDimension (periodic = True))) for points in [row_points(component_vertical_leeway, component_chamfer, chamfer_corner_outset), row_points(component_vertical_leeway-component_chamfer, 0, main_corner_outset), row_points(-thickness, 0, main_corner_outset)]]
        # preview(frames)
        outer_frames = [f.offset2d(wall_thickness) for f in frames]
        wall = Solid(Shell([f for l in [Loft(frames, ruled=True),Loft(outer_frames, ruled=True),Loft([frames[0],outer_frames[0]], ruled=True),Loft([frames[-1],outer_frames[-1]], ruled=True)] for f in l.faces()]))
        # wall = wallify([row_points(component_lip_thickness, component_chamfer), row_points(-thickness/4, 0), row_points(-thickness/2, 0), row_points(-thickness, 0)], wall_thickness, loop=True)
        lip = Wire(BSplineCurve(row_points(-thickness, -wall_thickness/2, main_corner_outset+wall_thickness/4), BSplineDimension (periodic = True))).offset2d(wall_thickness, fill = True).extrude (Down*(max_component_thickness-thickness + component_lip_thickness))

        return Compound(wall,lip)

    led_holder = component_holder(led_width, led_length, led_thickness, led_thickness)
        # led_cut = component_cut(led_width, led_length, led_thickness)
    resistor_holder = component_holder(resistor_width, resistor_length, resistor_thickness, led_thickness)

    component_housing_space = wall_thickness+component_chamfer+chamfer_corner_outset+0.15
    led_offset = led_length + component_housing_space*2
    resistor_center = Point(0, led_width/2 + component_housing_space*2 + resistor_width/2, 0)
    component_holders = [led_holder @ Translate(Right*led_offset*i) for i in range(3)]+[
        resistor_holder @ Translate(resistor_center - Origin)
    ]
    save_STL("springy_led_strip_prototype", Compound(component_holders))
    export("springy_led_strip_prototype.stl", "springy_led_strip_prototype_1.stl")
    preview(component_holders)