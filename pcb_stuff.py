import math

from pyocct_system import *
from gcode_stuff.gcode_utils import *

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