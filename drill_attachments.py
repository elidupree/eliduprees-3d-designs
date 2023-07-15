import math

from pyocct_system import *

initialize_pyocct_system()

inch = 25.4

shank_short_radius = inch / 8
shank_long_radius = shank_short_radius / math.cos(math.tau / 12)

def keyless_chuck_shank(length):

    shank = Face(Wire([
        Point(shank_long_radius, 0, 0) @ Rotate(Up, degrees=i * 60)
        for i in range(6)
    ], loop=True)).extrude(Up * length)

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

    #preview (shank)
    return shank


def stirrer(head_radius):
    length = 4 * inch


    shield_size = 10

    shield = Vertex(shield_size,0,length-24).extrude(Right*0.8).extrude(Vector(-50, 0, -50)).intersection(HalfSpace(Origin, Right)).revolve(Up)

    fin_thickness = 0.8
    fin = Vertex(0, -shank_long_radius/2, 0).extrude(Vector(0, shank_long_radius-fin_thickness, shank_long_radius)).extrude(Back*fin_thickness).extrude(Right*head_radius)

    return Compound(keyless_chuck_shank(length), shield, [fin @ Rotate(Up, degrees=i * 60 + 30)
                                                          for i in range(6)])


@run_if_changed
def stirrer_1():
    result = stirrer(13)
    save_STL("stirrer_1", result)
    return result

preview(stirrer_1)