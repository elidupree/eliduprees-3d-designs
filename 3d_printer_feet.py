import math

from pyocct_system import *

initialize_pyocct_system()

foot_leeway = 1
foot_width = 40 + foot_leeway
foot_length = 20 + foot_leeway
foot_wall_depth = 2
wall_thickness = 1.2

spring_bottom_diameter = 16.4
spring_top_diameter = 12.9
spring_wire_thickness = 1.4

# hack - at the time of this writing, my print settings
# made a 0.34mm-deep spring slot when it should've been 1.4.
# adjusting my print setup is harder than adding a compensation:
spring_wire_extra_depth = 1
# and anyway, having the plates be more rigid could be a small benefit.

bottom_plate_depth = spring_wire_thickness + spring_wire_extra_depth + 1.2
lots = 100

@run_if_changed
def top_plate():
    slot_leeway = 0.2
    slot_thickness = 2*spring_wire_thickness + 2*slot_leeway
    plate_depth = wall_thickness*2 + slot_thickness
    chunk = (Vertex(Origin)
             .extrude(Left*(foot_width + wall_thickness*2), centered=True)
             .extrude(Back*(foot_length + wall_thickness*2), centered=True)
             .extrude(Up*(plate_depth+foot_wall_depth)))
    foot_space = (Vertex(Origin)
             .extrude(Left*(foot_width), centered=True)
             .extrude(Back*(foot_length), centered=True)
             .extrude(Up*plate_depth, Up*lots))

    # spring_space = Face(Circle(Axes(Origin, Up), spring_top_diameter/2), holes=[Circle(Axes(Origin, Up), spring_top_diameter/2 - spring_wire_thickness).reversed()]).extrude(Up*(spring_wire_thickness + spring_wire_extra_depth))
    spring_space = Compound(
        Vertex(Origin).extrude(Up*wall_thickness, Up*(wall_thickness+slot_thickness)).extrude(Left*(spring_top_diameter+2*slot_leeway), centered=True),

        Vertex(Origin + Left*(spring_top_diameter/2+slot_leeway)).extrude(Up*wall_thickness, Up*lots).extrude(Right*(spring_wire_thickness+slot_leeway*2)),
    ).extrude(Back*spring_top_diameter/2, Front*lots)

    result = chunk.cut ([foot_space, spring_space])

    save_STL("3d_printer_foot_top_plate", result)
    export("3d_printer_foot_top_plate.stl", "3d_printer_foot_top_plate_3.stl")
    preview(result)

@run_if_changed
def bottom_plate():
    chunk = Face(Circle(Axes(Origin, Up), 25)).extrude(Up*bottom_plate_depth)

    spring_space = Face(Circle(Axes(Origin, Up), spring_bottom_diameter/2), holes=[Circle(Axes(Origin, Up), spring_bottom_diameter/2 - spring_wire_thickness).reversed()]).extrude(Up*(spring_wire_thickness + spring_wire_extra_depth))

    result = chunk.cut ([spring_space])

    save_STL("3d_printer_foot_bottom_plate", result)
    # export("3d_printer_foot_bottom_plate.stl", "3d_printer_foot_bottom_plate_1.stl")
    preview(result)