import math

from pyocct_system import *

initialize_pyocct_system()

inch = 25.4
sq2 = math.sqrt(2)

main_radius = 3*inch
led_strip_width = 10
height_reserved_for_vision = 21.75
flat_width = height_reserved_for_vision + led_strip_width
outer_radius = main_radius + flat_width
paper_leeway = 0.3
led_application_leeway =8
led_application_grip_depth = 2
led_strip_thickness_reserved = 2
form_thickness = 3
taping_leeway = 0.6*inch



@run_if_changed
def led_application_form():
    section = Wire([
        Point (main_radius- paper_leeway,- paper_leeway),
        Point(main_radius +flat_width + paper_leeway, - paper_leeway),
        Point(main_radius +flat_width + paper_leeway, paper_leeway),
        Point(main_radius +led_application_leeway, paper_leeway),
        Point(main_radius +led_application_leeway+ form_thickness, paper_leeway+ form_thickness),
        Point(main_radius +flat_width + paper_leeway + form_thickness, paper_leeway+ form_thickness),
        Point(main_radius +flat_width + paper_leeway + form_thickness, -(paper_leeway+ form_thickness)),
        Point(main_radius - paper_leeway - form_thickness, -(paper_leeway+ form_thickness)),
        Point(main_radius - paper_leeway - form_thickness, paper_leeway+ form_thickness + led_strip_width),
        Point(main_radius + paper_leeway + led_application_grip_depth , paper_leeway+ form_thickness + led_strip_width),
        Point(main_radius + paper_leeway + led_application_grip_depth, paper_leeway + led_strip_width),
        Point(main_radius - paper_leeway, paper_leeway + led_strip_width),
    ], loop=True)
    # preview (section)
    led_application_form = Face(section).revolve(Front, Degrees( 45))

    save_STL("led_application_form", led_application_form)
    export("led_application_form.stl", "led_application_form_1.stl")
    return led_application_form


@run_if_changed
def slant_taping_form():
    # fdgf f
    section = Wire([
        # Point (main_radius - paper_leeway, paper_leeway),
        Point (outer_radius - paper_leeway*(1+sq2) , paper_leeway),
        Point(main_radius - paper_leeway*sq2, flat_width),
        Point(main_radius, flat_width + paper_leeway*sq2),
        Point(outer_radius - taping_leeway/sq2 + paper_leeway/sq2, taping_leeway/sq2 + paper_leeway/sq2),
        Point(outer_radius - taping_leeway/sq2 + (paper_leeway+form_thickness)/sq2, taping_leeway/sq2 + (paper_leeway+form_thickness)/sq2),
        Point(main_radius, flat_width + (paper_leeway+form_thickness)*sq2),
        Point(main_radius - (paper_leeway+form_thickness)*sq2, flat_width),
        Point (main_radius - (paper_leeway+form_thickness), led_strip_width),
        Point (main_radius - (paper_leeway+form_thickness), - (paper_leeway+form_thickness)),

        Point(outer_radius - taping_leeway, -(paper_leeway+form_thickness)),
        Point(outer_radius - taping_leeway, -paper_leeway),
        Point (main_radius - paper_leeway, -paper_leeway),
        Point (main_radius - paper_leeway, led_strip_width+paper_leeway),
        Point (main_radius + led_strip_thickness_reserved, led_strip_width+paper_leeway),
        Point (main_radius + led_strip_thickness_reserved, paper_leeway),
    ], loop=True)
    # preview (section)
    slant_taping_form = Face(section).revolve(Front, Degrees(35))

    save_STL("slant_taping_form", slant_taping_form)
    export("slant_taping_form.stl", "slant_taping_form.stl")
    return slant_taping_form


preview(slant_taping_form)