import math
import numpy as np
import numbers
from gcode_stuff.gcode_utils import *
from pyocct_system import *

def make_spiral(*, v_to_cross_section_curve, max_overhang, line_width, starting_downfill, max_layer_height, f):
    """
    Calculate the route for a FDM nozzle to move in a spiral to render the provided surface, so it can form a single-wall with absolutely no printing artifacts like stringing or z-seams.

Input is given as a function from parameter that ranges from 0 to 1 (call it v) to an arbitrary curve, which is assumed to be closed. This function is expected to be continuous, but need not be smooth. This function will take care of making the layers thinner wherever it is needed for overhangs; we even support 90° overhangs, at least if they are convex. This function will always proceed upwards in v; it even supports having the constant-v cross-sections become tilted, making the printer print on a diagonal surface instead of a horizontal one (the user is responsible for making sure their printer can handle the tilts they specify).

Design-wise, our approach is this: iterate from bottom to top, splitting the surface into layers, with a search for permissible layer heights. With in each layer, we actually need to proceed in a spiral; so we pick 2 constant-v cross-sections of the input, and proceed around them by equal proportions of arc length, placing the spiral-points in between the layers.
    :param v_to_cross_section_curve: The input surface
    :param max_overhang: Determines the permissible overhang
    :param line_width: The assumed line width to generate (I usually use slightly higher than the nozzle width). Can be a number or a function from location to number.
    :param starting_downfill: make the first layer have this much extra stroke thickness, for bed adhesion
    :param max_layer_height: layers will not be made further apart than this in z
    :param f: speed of print (mm/min; TODO maybe support lower speeds for tighter turns? and/or enforcing thinner layer heights for that?)
    :return: tuple of
        1. the starting position (which the user must move to manually)
        2. all points (mainly for preview purposes)
        3. the gcode commands (as a list of strings)
    """

    if isinstance(line_width, numbers.Number):
        line_width_number = line_width
        line_width = lambda p: line_width_number

    def try_next_section(curve_steps, vs):
        curves = [v_to_cross_section_curve(v) for v in vs]
        lengths = [c.length() for c in curves]
        recent = [curves[1].position(distance=0)]
        recent_fracs = [0]
        points_and_depths = []
        extra_steps = []
        steepness = 0
        for frac in curve_steps:
            derivatives = [c.derivatives(distance = l * frac) for c, l in zip (curves, lengths)]
            below, current = [Between (d0.position, d1.position, frac) for d0,d1 in [derivatives[0:2], derivatives[1:3]]]

            recent.append(current)
            recent_fracs.append(frac)
            if len(recent) > 2:
                a,b,c = recent[-3:]
                af,bf,cf = recent_fracs[-3:]
                pointiness = (b-a).projected_perpendicular(Direction(a,c)).length()

                coarseness = pointiness/0.05
                l = (c-a).length()
                if l > 0.01:
                    coarseness = max(coarseness, pointiness/(c-a).length()*360)
                if coarseness > 1:
                    extra_steps.append(Between(af,bf))
                    extra_steps.append(Between(bf,cf))

            # not all points will perfectly align, and misalignment isn't depth, so ignore difference-components in the derivatives[1].tangent direction
            layer_to_layer = (derivatives[-1].position - derivatives[-2].position).projected_perpendicular(derivatives[1].tangent)
            riseness = layer_to_layer[2] / max_layer_height
            if riseness < 0:
                raise RuntimeError("spiral moved downwards")
                preview (curves, current, below)
            overhangness = layer_to_layer.projected_perpendicular(Up).length() / (max_overhang)

            steepness = max(steepness, riseness, overhangness)

            points_and_depths.append((current, (current - below).projected_perpendicular(derivatives[1].tangent).length()))

        refined_steps = steps
        if extra_steps:
            refined_steps = sorted(set(refined_steps + extra_steps))
        return points_and_depths, refined_steps, steepness


    commands = [zero_extrusion_reference()]
    all_points = []
    started = False
    start_position = None

    cross_sections_achieved = [0,0]
    while cross_sections_achieved[-2] < 1:
        next = 1
        steps = subdivisions(0,1,amount=11)[1:]
        min_swing_size = 0.05
        max_swing_size = 2
        while True:
            points_and_depths, refined_steps, steepness = try_next_section(steps,cross_sections_achieved[-2:]+[next])
            if steepness > 1:
                print(f"too steep: {cross_sections_achieved[-2:]}, {next}, {steepness}")
                next = Between(cross_sections_achieved[-1], next, np.clip(1/steepness, 1/max_swing_size, 1-min_swing_size))
            elif steepness < 0.95 and next != 1:
                print(f"not steep enough: {cross_sections_achieved[-2:]}, {next}, {steepness}")
                next = Between(cross_sections_achieved[-1], next, np.clip(1/steepness, 1+min_swing_size, max_swing_size))
                min_swing_size *= 0.6
                max_swing_size = max_swing_size**0.6
            elif len(refined_steps) > len(steps):
                print(f"too coarse: {cross_sections_achieved[-2:]}, {next}, {len(steps)}, {len(refined_steps)}")
                steps = refined_steps #math.ceil(steps*np.clip(coarseness, 1.05, 2))

            else: # if too_steep <= 1 and coarseness <= 1:
                print(f"added curve to {next} with {len(steps)} steps")
                extra_depth = 0 if started else starting_downfill
                for p,d in points_and_depths:
                    all_points.append(p)
                    if started:
                        commands.append(g1(coords=p, eplus_cross_sectional_mm2=line_width(p)*(d+extra_depth), f=f))
                    else:
                        started = True
                        start_position = p
                        assume_at(coords=p)
                cross_sections_achieved.append(next)
                break

    return start_position, all_points, commands

