import math
import numpy as np
from gcode_stuff.gcode_utils import *
from pyocct_system import *

def make_spiral(*, v_to_cross_section_curve, nozzle_width, line_width, starting_downfill, max_layer_height, f, go_to_start = fastmove):
    """
    Calculate the route for a FDM nozzle to move in a spiral to render the provided surface, so it can form a single-wall with absolutely no printing artifacts like stringing or z-seams.

Input is given as a function from parameter that ranges from 0 to 1 (call it v) to an arbitrary curve, which is assumed to be closed. This function is expected to be continuous, but need not be smooth. This function will take care of making the layers thinner wherever it is needed for overhangs; we even support 90° overhangs, at least if they are convex. This function will always proceed upwards in v; it even supports having the constant-v cross-sections become tilted, making the printer print on a diagonal surface instead of a horizontal one (the user is responsible for making sure their printer can handle the tilts they specify).

Design-wise, our approach is this: iterate from bottom to top, splitting the surface into layers, with a search for permissible layer heights. With in each layer, we actually need to proceed in a spiral; so we pick 2 constant-v cross-sections of the input, and proceed around them by equal proportions of arc length, placing the spiral-points in between the layers.
    :param v_to_cross_section_curve: The input surface
    :param nozzle_width: Determines the permissible overhang
    :param line_width: The assumed line width to generate (I usually use slightly higher than the nozzle width)
    :param starting_downfill: make the first layer have this much extra stroke thickness, for bed adhesion
    :param max_layer_height: layers will not be made further apart than this in z
    :param f: speed of print (mm/min; TODO maybe support lower speeds for tighter turns? and/or enforcing thinner layer heights for that?)
    :return: tuple of
        1. the starting position (which the user must move to manually)
        2. all points (mainly for preview purposes)
        3. the gcode commands (as a list of strings)
    """


    def try_next_section(curve_steps, vs):
        curves = [v_to_cross_section_curve(v) for v in vs]
        lengths = [c.length() for c in curves]
        recent = [curves[1].position(distance=0)]
        points_and_depths = []
        coarseness = 0
        steepness = 0
        for step in range(1, curve_steps+1):
            frac = step/curve_steps
            derivatives = [c.derivatives(distance = l * frac) for c, l in zip (curves, lengths)]
            below, current = [Between (d0.position, d1.position, frac) for d0,d1 in [derivatives[0:2], derivatives[1:3]]]

            if len(recent) > 2:
                a,b,c = recent[-3:]
                pointiness = (b-a).projected_perpendicular(Direction(a,c)).length()

                coarseness = max(coarseness, pointiness/0.05, pointiness/(c-a).length()*360)

            layer_to_layer = derivatives[-1].position - derivatives[-2].position
            riseness = layer_to_layer[2] / max_layer_height
            if riseness < 0:
                raise RuntimeError("spiral moved downwards")
                preview (curves, current, below)
            overhangness = layer_to_layer.projected_perpendicular(Up).length() / (nozzle_width*0.6)

            steepness = max(steepness, riseness, overhangness)

            points_and_depths.append((current, (current - below).length()))

            recent.append(current)

        return points_and_depths, coarseness, steepness


    commands = [set_extrusion_reference(0)]
    all_points = []
    started = False
    start_position = None

    cross_sections_achieved = [0,0]
    while cross_sections_achieved[-2] < 1:
        next = 1
        steps = 10
        min_swing_size = 0.05
        while True:
            points_and_depths, coarseness, steepness = try_next_section(steps,cross_sections_achieved[-2:]+[next])
            if steepness > 1:
                print(f"too steep: {cross_sections_achieved[-2:]}, {next}, {steepness}")
                next = Between(cross_sections_achieved[-1], next, np.clip(1/steepness, 0.5, 1-min_swing_size))
            elif steepness < 0.98 and next != 1:
                print(f"not steep enough: {cross_sections_achieved[-2:]}, {next}, {steepness}")
                next = Between(cross_sections_achieved[-1], next, np.clip(1/steepness, 1+min_swing_size, 2))
                min_swing_size *= 0.6
            elif coarseness > 1:
                print(f"too coarse: {cross_sections_achieved[-2:]}, {next}, {steps}, {coarseness}")
                steps = math.ceil(steps*np.clip(coarseness, 1.05, 2))

            else: # if too_steep <= 1 and coarseness <= 1:
                print(f"added curve to {next} with {steps} steps")
                extra_depth = 0 if started else starting_downfill
                for p,d in points_and_depths:
                    all_points.append(p)
                    if started:
                        commands.append(g1(coords=p, eplus_cross_sectional_area=line_width*(d+extra_depth), f=f))
                    else:
                        started = True
                        start_position = p
                cross_sections_achieved.append(next)
                break

    return start_position, all_points, commands

