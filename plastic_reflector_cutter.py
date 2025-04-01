import math

from pyocct_system import *
from svg_utils import load_Inkscape_BSplineCurve

initialize_pyocct_system()

blade_full_length = 42.7
blade_width = 22

blade_center = Point(blade_full_length/2, blade_width/2, 0)

@run_if_changed
def blade_cutout():
    quarter = load_Inkscape_BSplineCurve("razor_blade.svg", "quarter_of_cutout")
    ghh = Compound(Edge(quarter @ Mirror(Axes(blade_center, Right))), Edge(quarter.reversed()))
    poles = quarter.poles()
    # oops_blade_center = Point(poles[-1][0], poles[0][1], 0)
    # print([v.point() for e in ghh.edges() for v in e.vertices()])
    # print(oops_blade_center)
    # def qt(t):
    #     return BSplineCurve([p @ t for p in poles])
    # preview([quarter @ Mirror(Axes(oops_blade_center, Right)), quarter.reversed(), quarter @ Mirror(Axes(oops_blade_center, Back)), quarter.reversed() @ Rotate(Axis(oops_blade_center, Up), Degrees(180))])
    # wire = Wire([qt(Mirror(Axes(oops_blade_center, Right))), quarter.reversed(), qt(Mirror(Axes(oops_blade_center, Back))), qt(Rotate(Axis(oops_blade_center, Up), Degrees(180))).reversed()], loop=True)
    def qt(t):
        return [p @ t for p in poles]
    wire = Wire(BSplineCurve(qt(Mirror(Axes(blade_center, Right))) + poles[::-1] + qt(Mirror(Axes(blade_center, Back))) + qt(Rotate(Axis(blade_center, Up), Degrees(180)))[::-1], BSplineDimension(periodic=True)))
    preview(wire)
    return Face(wire)

# preview(blade_cutout, Vertex(Origin).extrude(Back*blade_width).extrude(Right*blade_full_length))

@run_if_changed
def blade_holder():
    total_blades_thickness = 10
    extra_rod_length = 3
    left_wall_thickness = 3
    offset_unit_vector = Vector(0,1,1)
    amount_gripped = 11.5
    left_extension = 10
    handle_grip_extension = 15
    rod = blade_cutout.intersection(HalfSpace(Point(amount_gripped,0,0), Left)).extrude(offset_unit_vector * (total_blades_thickness + extra_rod_length))
    bottom_plate = Vertex(Origin).extrude(Back*(blade_width)).extrude(Left*left_extension, Right*amount_gripped).extrude(offset_unit_vector*-3)
    top_plate = Vertex(Origin + offset_unit_vector*total_blades_thickness).extrude(Back*(blade_width)).extrude(Left*left_extension, Right*amount_gripped).extrude(offset_unit_vector*3).cut(rod)
    left_wall = Vertex(Origin).extrude(Back*(blade_width)).extrude(Left*(left_extension + handle_grip_extension), Left*(left_extension - left_wall_thickness)).extrude(offset_unit_vector*-3, offset_unit_vector*(total_blades_thickness + 3))
    left_wall_mortise = Vertex(Origin + Back*blade_width/2).extrude(Back*10, centered=True).extrude(Left*(left_extension-1), Left*(left_extension-left_wall_thickness)).extrude(offset_unit_vector*-2)

    screw_radius = 1.5
    screw_hole = Face(Circle(Axes(Point(-2, blade_width/2 + total_blades_thickness/2*offset_unit_vector[1], 0), Up), screw_radius)).extrude(Up*100, centered=True)

    bottom_plate = bottom_plate.cut([screw_hole, left_wall_mortise])
    top_plate = top_plate.cut(screw_hole)
    left_wall = left_wall.cut(bottom_plate)

    virtual_blade = Vertex(Origin).extrude(Right*blade_full_length).extrude(Back*blade_width).outer_wire()
    virtual_blades = [virtual_blade @ Translate(offset_unit_vector*(i+0.5)*0.2) for i in range(50)]

    handle = Face(Circle(Axes(Origin, Left), 9.5/2)).extrude(Left*100) @ Rotate(Up, Degrees(30)) @ Translate(Back*blade_width*0.7 + offset_unit_vector*total_blades_thickness/2 + Left*left_extension)
    left_wall = left_wall.cut(handle)

    bottom_part = Compound(rod, bottom_plate)
    top_part = Compound(top_plate, left_wall, left_wall_mortise)
    # save_STL("blade_holder_bottom_part", bottom_part)
    # export("blade_holder_bottom_part.stl", "blade_holder_bottom_part_1.stl")
    save_STL("blade_holder_top_part", top_part)
    export("blade_holder_top_part.stl", "blade_holder_top_part_1.stl")

    return Compound(bottom_part, Compound(top_part, handle.wires()) @ Translate(offset_unit_vector*5), virtual_blades, )

preview(blade_holder)