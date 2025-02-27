import math
import numpy as np
from gcode_stuff.gcode_utils import *
from spiral_printing import make_spiral
from pyocct_system import *
initialize_pyocct_system()

# def chunk_commands(*, center, start_z, stop_z, z_to_radius, layer_height, outwards_dir, line_width, transit_z):
#     result = [set_extrusion_reference(0)]
#     layers = (stop_z-start_z)/layer_height
#     steps = math.ceil(layers*360)
#     steps_per_layer = steps/layers
#
#     for i in range(steps):
#         angle = Degrees(i/steps_per_layer)
#         z = Between(start_z, stop_z, i/steps)
#         radius = z_to_radius(angle) - outwards_dir*line_width/2
#         stroke_thickness = layer_height
#
#         layers_from_end = (min(i, (steps-1)-i) / steps_per_layer)
#         if layers_from_end < 1:
#             endness = 1-layers_from_end
#             radius -= outwards_dir*endness*line_width
#             stroke_thickness *= layers_from_end
#
#         x = center[0] + radius*angle.cos()
#         y = center[1] + radius*angle.sin()
#         if i==0:
#                 result.extend(square_jump(x, y, z))
#             else:
#                 result.append(fastmove(x=x,y=y,z=z))
#         else:
#             result.append(g1(x=radius*angle.cos(), y=radius*angle.sin(), z=z, eplus=line_width*stroke_thickness*radius*angle.radians))
#
#     return result

def careful_circle_commands(*, center, top_z, height, radius, outwards_dir, line_width, start_degrees=0, sweep_degrees, min_transit_z, f):
    result = [zero_extrusion_reference()]

    insweep_start = 360-sweep_degrees
    insweep_return_start = insweep_start+360-sweep_degrees
    outsweep_start = insweep_return_start+sweep_degrees
    outfill_start = outsweep_start+sweep_degrees
    total_degrees = outfill_start+sweep_degrees
    for i in range(0,total_degrees):
        stroke_radius = radius - outwards_dir*line_width/2
        stroke_thickness = height

        insweep_progress = smootherstep(i, insweep_start, insweep_start+sweep_degrees)
        insweep_return_progress = smootherstep(i, insweep_return_start, insweep_return_start+sweep_degrees)
        outsweep_progress = smootherstep(i, outsweep_start, outsweep_start+sweep_degrees)
        outfill_progress = smootherstep(i, outfill_start, outfill_start+sweep_degrees)

        insetness = max(1-insweep_progress, outsweep_progress)
        stroke_radius -= outwards_dir*insetness*line_width

        if 0 < outsweep_progress < 1:
            stroke_thickness = 0
        if outfill_progress == 0:
            angle = Degrees(start_degrees+i)
            stroke_thickness *= (1-insweep_return_progress)
        else:
            angle = Degrees(start_degrees+outfill_start - (i-outfill_start))
            stroke_thickness *= (1-outfill_progress)

        x = center[0] + stroke_radius*angle.cos()
        y = center[1] + stroke_radius*angle.sin()

        if i==0:
            # result.extend(square_jump(x, y, top_z, min_transit_z))
            result.append(g1(x=x, y=y, z=top_z, f=1500))
        else:
            result.append(g1(x=x, y=y, z=top_z, eplus_mm3=line_width*stroke_thickness*radius*(math.tau/360), f=f))


    return result


def bearing_commands(*, bearing_height, inner_radius, roller_min_radius, roller_max_radius, num_rollers, line_width, max_layer_height, leeway):
    layers = math.ceil(bearing_height/max_layer_height)
    layer_height = bearing_height/layers
    roller_min_surface_offset = inner_radius + line_width*4 + leeway
    roller_center_offset = roller_min_surface_offset+roller_max_radius
    roller_centers = [Point(roller_center_offset,0,0)@Rotate(Up, Turns(t+1/num_rollers)) for t in subdivisions(0, 1, amount=num_rollers+1)[1:]]
    commands = [fastmove(x=roller_center_offset+roller_min_radius+leeway +1,y=0,z=layer_height)]
    current_degrees = 0
    for l in range(layers):
        top_z = layer_height*(l+1)
        mid_z = top_z-layer_height*0.5
        topness = mid_z / bearing_height
        edgeness = abs((topness*2)-1)
        middleness = (1-edgeness)
        roller_radius = Between(roller_min_radius, roller_max_radius, middleness)
        inface_radius = roller_center_offset-roller_radius-leeway
        outface_radius = roller_center_offset+roller_radius+leeway

        insweep_progress = linear_step(l, 0, 2)
        startness = 1-insweep_progress
        inface_radius -= startness*0.4
        outface_radius += startness*0.4

        shared_args = {"top_z":top_z, "height":layer_height + (0.1 if l==0 else 0), "line_width":line_width,"min_transit_z":layer_height/2}

        commands.extend(careful_circle_commands(center=Origin, radius=outface_radius, outwards_dir=-1, start_degrees=current_degrees, sweep_degrees=40, f=900, **shared_args))
        current_degrees -= 40

        for roller_center in roller_centers:
            commands.extend(careful_circle_commands(center=roller_center @ Rotate(Up, Degrees(current_degrees)), radius=roller_radius, outwards_dir=1, sweep_degrees=90, f=500, **shared_args))
        current_degrees -= 360/num_rollers

        commands.extend(careful_circle_commands(center=Origin, radius=inner_radius, outwards_dir=-1, start_degrees=current_degrees, sweep_degrees=40, f=900, **shared_args))
        current_degrees -= 40
        commands.extend(careful_circle_commands(center=Origin, radius=inface_radius, outwards_dir=1, start_degrees=current_degrees, sweep_degrees=40, f=900, **shared_args))
        current_degrees -= 40

    return commands

@run_if_changed
def bearing():
    commands = [
        'M106 S255 ; Fan 100%',
    ] + bearing_commands(
        bearing_height=5,
        inner_radius=19/2,
        roller_min_radius=1.5,
        roller_max_radius=2.5,
        num_rollers=18,
        line_width=0.5,
        max_layer_height=0.2,
        leeway=0.2)

    gcode = wrap_gcode("\n".join(commands))

    export_string(gcode, "bearing_1.gcode")



"""
def spiral(*, parameter01_to_cross_section_curve, nozzle_width, line_width, starting_downfill, max_layer_height, min_transit_z, f):
    def try_loop(curve_steps, fixed_control_points):
        '''
Assume that the "layer-position to v" function is a quadratic B-spline, so it can be smooth.

Assume that we've already committed to a segment of that B-spline, which means committing to 4 control points. We are now trying to commit to the next segment, i.e. one more control point.

We don't actually want to maximize that new control point, because we want to leave room for the later control points to grow. That control point will influence another 3 segments after the one we are now committing to.

Our choice of next control point has no effect on the starting position OR velocity of the segment we're about to commit to – what it does is apply a constant jump to the starting acceleration.

A control point can never be lower than the previous ones, so at the very least, if we are setting the new control point to x, then it must be permissible to continue having the upcoming points be x until you reach a constant-x function. This means we have to look at the next 2 segments after the one we are committing to, which incorporate 2 more control points. (The next segment after them could be constant-x.)

Additionally, we don't want to accelerate so hard that we would have to brake to a constant.


Naïvely, perhaps we would only want to accelerate hard enough that we could then continue at a fixed speed for the next 2 segments. If the input actually forces us to slow down, then this makes us go unnecessarily slow preemptively. That really doesn't seem like a problem, and the general optimization problem doesn't have a clear best answer.

If we required the next 2 segments to be able to continue linearly, then clearly that would be stricter than requiring them to have all the control points be x, so that's okay.

The only real "problem scenario" I can think of is that if you are approaching a point where you have to slow down a lot (a sudden large overhang? no, a speed issue in the input parameterization…), this would constrain you to exponentially decaying towards it instead. Maybe that's just a case of "bad input".

… Actually, arguably, the whole point here is to correct for bad input. "reparameterize the input into a permissible-layers form". Smoothness in "layer to v" doesn't actually seem right (what if v wasn't smooth? Enforcing smoothness means we enforced the input-nonsmoothness to be visible in the output!)

A slicing approach would divide v into layers, and then there would just happen to be a particular layer transition that includes the input discontinuity-of-derivative. Here though, the transition may happen in the middle of a layer, so we should use an approach where the layer-to-v may have a sudden jump ANYWHERE in the derivative. The only smoothness we care about is smoothness of physical distances …

So if the constraints are…
* Never reduce v
* try to be smooth in ... z? Not exactly z if you're tilted. Smooth in "distance to the layer you're fusing to" perhaps? Even that wobbles around a layer when there is a tilt, but that part's inevitable.

The main thing we care about is: don't go backwards in v, and don't make any fuse-points too far apart from each other. Within that, we would prefer to make the fuse-point-distance smooth as you move up the layers on any particular side…

Consider this: use, for reference, a pair of constant-v cross-sections. At each point, find its closest neighbor in EACH of those cross-sections and position it proportionally between them. If it is proportionally too far from either…        '''


def try_loop(curve_steps, prev_loop_start_param, start_param, stop_param):
        # prev = previous_curve.derivatives(parameter=previous_curve.LastParameter())
        prev = None
        points = []
        too_coarse = 0
        too_steep = 0
        for step in range(1,curve_steps+1):
            rise_parameter = Between(rise_parameter_start, rise_parameter_stop, step/curve_steps)
            curve = parameter01_to_cross_section_curve(rise_parameter)
            d = curve.derivatives(distance=curve.length() * step/curve_steps)
            point = d.position
            # ref = previous_curve.position(closest=point)
            ref = parameter01_to_cross_section_curve(max(0, rise_parameter + rise_parameter_start - rise_parameter_stop)).position(closest=point)

            if prev is not None:
                movement = (point - prev.position)
                offsetness = movement.projected_perpendicular(prev.tangent).length() / 0.002
                curvedness = (d.tangent - prev.tangent).length() * 360 / math.tau
                too_coarse = max(too_coarse, offsetness, curvedness)

            riseness = (point - ref)[2] / max_layer_height
            assert (riseness >= 0)
            overhangness = (point - ref).projected_perpendicular(Up).length() / (nozzle_width*0.6)
            # if overhangness > 1:
            #     print(point, ref)
            #     preview(point, ref, previous_curve)
            too_steep = max(too_steep, riseness, overhangness)

            points.append((point, (ref - point).length()))

            prev = d

        return points, too_coarse, too_steep

    def points_to_curve(points):
        return BSplineCurve([p for p,d in points], BSplineDimension(degree=1))

    def try_2_loops(curve_steps, rise_parameter_start, rise_parameter_stop, previous_curve):
        rise_middle = Between(rise_parameter_start, rise_parameter_stop)
        p1, c1, s1 = try_loop(curve_steps, rise_parameter_start, rise_middle,)
        p2, c2, s2 = try_loop(curve_steps, rise_middle, rise_parameter_stop)
        return p1, p2, max(c1, c2), max(s1, s2)

    commands = [zero_extrusion_reference()]
    all_points = []

    current_parameter = 0
    # established_curve = parameter01_to_cross_section_curve(0)
    # printed_curves = []

    started = False
    def add_curve(ps):
        # nonlocal established_curve
        # established_curve = points_to_curve(ps)
        # printed_curves.append(established_curve)
        for p,d in ps:
            all_points.append(p)
            if started:
                commands.append(g1(coords=p, eplus_cross_sectional_mm2=line_width*d, f=f))
            else:
                started = True
                commands.extend(square_jump(coords=p, min_transit_z=min_transit_z))

    while True:
        next_parameter = 1
        steps = 10
        while True:
            if current_parameter == 1:
                p1, too_coarse, _ = try_loop(steps, current_parameter, next_parameter, established_curve)
                too_steep = 0
                p2 = []
            else:
                p1, p2, too_coarse, too_steep = try_2_loops(steps, current_parameter, next_parameter, established_curve)

            if too_steep > 1:
                print(f"too steep: {current_parameter}, {next_parameter}, {too_steep}")
                next_parameter = Between(current_parameter, next_parameter, np.clip(1/too_steep, 0.6, 0.96))
                if next_parameter - current_parameter < 0.01:
                    preview(established_curve, Compound(Vertex(p) for p,d in p1+p2))
            elif too_coarse > 1:
                print(f"too coarse: {current_parameter}, {next_parameter}, {steps}, {too_coarse}")
                steps = math.ceil(steps*np.clip(too_coarse, 1.05, 2))
                if steps > 2000:
                    preview(established_curve, Compound(Vertex(p) for p,d in p1+p2))

            else: # if too_steep <= 1 and too_coarse <= 1:
                print(f"added curve to {next_parameter} with {steps} steps")
                curves_to_add = [p1]
                if next_parameter == 1 and current_parameter < 1:
                    curves_to_add.append(p2)
                    current_parameter = 1
                else:
                    current_parameter = Between(current_parameter, next_parameter)
                for ps in curves_to_add:
                    add_curve(ps)

                break
        if current_parameter == 1:
            break

    # preview(printed_curves)
    return all_points, commands
"""

# @run_if_changed
def spiral_test():
    def curvefn(v):
        return Circle(Axes(Point(0,0,v*10), Direction(v*0.2,0,1), Back), 5+5*v*v)
    # preview(curvefn(v) for v in subdivisions(0,1,amount=20))
    spiral_start, spiral_points, spiral_commands = make_spiral(
        v_to_cross_section_curve=curvefn,
        max_overhang=0.24,
        line_width=0.5,
        max_layer_height=0.2,
        starting_downfill=0.2,
        f=900,
    )
    commands = ([
                   'M106 S255 ; Fan 100%',
               ] +
               square_jump(coords=spiral_start, min_transit_z=0.2) +
               spiral_commands)
    gcode = wrap_gcode("\n".join(commands))

    export_string(gcode, "spiral_test_4.gcode")

    preview(BSplineCurve(spiral_points, BSplineDimension(degree=1)))


ball_diameter = 3.5
ball_radius = ball_diameter/2
sq2 = math.sqrt(2)
races_base = 0.5
races_inner_radius = 19/2+0.5
ball_center_offset = races_inner_radius + 0.5 + ball_radius

# @run_if_changed
def inner_race():
    def inner_race_fn(v):
        z = v*(ball_diameter/sq2 + races_base)
        offs = max(0, z - races_base) - (ball_radius/sq2)

        r = ball_center_offset - math.sqrt(ball_radius**2 - offs**2) - 0.25
        return Circle(Axes(Point(0,0,z), Up), r)
    inner_race_start, inner_race_points, inner_race_commands = make_spiral(
        v_to_cross_section_curve=inner_race_fn,
        max_overhang=0.24,
        line_width=0.5,
        max_layer_height=0.2,
        starting_downfill=0.2,
        f=900,
    )
    commands = ([
                    'M106 S255 ; Fan 100%',
                ] +
                square_jump(coords=inner_race_start, min_transit_z=0.2) +
                inner_race_commands)
    gcode = wrap_gcode("\n".join(commands))

    export_string(gcode, "inner_race_2.gcode")

    return BSplineCurve(inner_race_points, BSplineDimension(degree=1))

# @run_if_changed
def outer_race_half():
    def outer_race_fn(v):
        z = v*(ball_radius/sq2 + races_base)
        offs = max(0, z - races_base) - (ball_radius/sq2)

        r = ball_center_offset + math.sqrt(ball_radius**2 - offs**2) + 0.25
        return Circle(Axes(Point(0,0,z), Up), r)
    outer_race_start, outer_race_points, outer_race_commands = make_spiral(
        v_to_cross_section_curve=outer_race_fn,
        max_overhang=0.24,
        line_width=0.5,
        max_layer_height=0.2,
        starting_downfill=0.2,
        f=900,
    )
    commands = ([
                    'M106 S255 ; Fan 100%',
                ] +
                square_jump(coords=outer_race_start, min_transit_z=0.2) +
                outer_race_commands)
    gcode = wrap_gcode("\n".join(commands))

    export_string(gcode, "outer_race_2.gcode")

    return BSplineCurve(outer_race_points, BSplineDimension(degree=1))

CPAP_inner_radius=19/2
CPAP_min_wall_thickness=0.8
CPAP_ball_leeway=0.03
CPAP_ball_space_radius= ball_radius
CPAP_bearing_ball_center_offset = CPAP_inner_radius + CPAP_min_wall_thickness + CPAP_ball_space_radius
CPAP_bearing_outermost_radius = CPAP_bearing_ball_center_offset + CPAP_ball_leeway + CPAP_min_wall_thickness*2
CPAP_most_walls_thickness = CPAP_min_wall_thickness + (1-1/sq2)*CPAP_ball_space_radius
# large enough to be just-over-flush with the balls:
CPAP_inner_race_base = ball_radius*(1-1/sq2)+0.1

CPAP_retainer_bite_thickness = 1
CPAP_retainer_bite_depth = CPAP_most_walls_thickness - CPAP_min_wall_thickness
CPAP_joint_overshoot_for_sanding=1

@run_if_changed
def curved_tube_with_builtin_inner_race():
    def ball_facing_radius(z):
        offs = min((CPAP_ball_space_radius/sq2), abs(z - CPAP_inner_race_base - (CPAP_ball_space_radius/sq2)))
        return CPAP_bearing_ball_center_offset - math.sqrt(CPAP_ball_space_radius**2 - offs**2)

    bearing_top_z = (CPAP_ball_space_radius*sq2 + CPAP_inner_race_base)

    torus_rows = []
    tube_radius = CPAP_inner_radius+CPAP_most_walls_thickness/2
    revolution_radius = CPAP_bearing_outermost_radius
    revolution_center = Point(revolution_radius, 0, 0)
    revolution_axis = Axis(revolution_center, Back)
    retainer_face_start_center = Origin @ Rotate(revolution_axis, Degrees(30))
    retainer_face_along = Up @ Rotate(revolution_axis, Degrees(30))
    for i in range(360):
        tube_angle = Degrees(i)
        curve_start = Point(tube_radius,0,0) @ Rotate(Up, tube_angle)
        curve_end = (curve_start @ Rotate (revolution_axis, Degrees(30)))
        tube_outwards = Right @ Rotate(Up, tube_angle)
        retainer_face_outwards = tube_outwards @ Rotate(revolution_axis, Degrees(30))
        retainer_bite_surface = BSplineCurve([
            curve_end,
            curve_end+retainer_face_along*CPAP_retainer_bite_thickness/2 - retainer_face_outwards*CPAP_retainer_bite_depth/2,
            curve_end+retainer_face_along*CPAP_retainer_bite_thickness,
            curve_end+retainer_face_along*(CPAP_retainer_bite_thickness + CPAP_joint_overshoot_for_sanding),
        ])
        for j in range(1000):
            zplus = j*0.1
            plane = Plane(Point(0,0,zplus), Up)
            ratio = zplus/(revolution_center-curve_start)[0]
            if ratio < 1:
                angle = asin(ratio)
                position = curve_start @ Rotate (revolution_axis, angle)
                # print(start, zplus, position[2], angle.degrees, position.distance(revolution_center), start.distance(revolution_center))
            if ratio >= 1 or angle.degrees > 30:
                ps = plane.intersections(retainer_bite_surface)
                if ps.points:
                    position = ps.point()
                else:
                    break

            if len (torus_rows) <= j:
                torus_rows.append ([])
            torus_rows [j].append (position + Up*bearing_top_z)
    retainer_face_start_center = retainer_face_start_center + Up*bearing_top_z
    revolution_center = revolution_center + Up*bearing_top_z
    complete_torus_rows = [r for r in torus_rows if len(r) == 360]
    incomplete_torus_rows = torus_rows[len(complete_torus_rows):]

    complete_torus_surface = BSplineSurface(complete_torus_rows, v=BSplineDimension(periodic = True))
    # print([r[1] for r in complete_torus_rows])
    # print(list(complete_torus_surface.UMultiplicities()))
    # print(list(complete_torus_surface.UKnots()))
    # # print(complete_torus_surface.VKnots(0).position(distance=5))
    # print(complete_torus_surface.UIso(1.5).position(distance=5))
    knots = list(complete_torus_surface.UKnots())
    cts_a, cts_b = knots[0], knots[-1]

    def curvefn(v):
        circle_axis = Up
        if v < 0.5:
            center = Point(0,0,(v/0.5)*bearing_top_z)
        else:
            # rotation = Rotate(Axis(Point(CPAP_bearing_outermost_radius,0,bearing_top_z), Back), Degrees(((v-0.5)/0.5)*20))
            # center = Point(0,0,bearing_top_z) @ rotation
            # circle_axis = circle_axis @ rotation
            return complete_torus_surface.UIso(Between(cts_a, cts_b, (v-0.5)/0.5))

        a,b = CPAP_inner_radius, ball_facing_radius(center[2])
        r = Between(a,b)
        return Circle(Axes(center, circle_axis), r)
    # preview((curvefn(v) for v in subdivisions(0,1,amount=20)), complete_torus_surface, Compound(Edge(BSplineCurve(r)) for r in incomplete_torus_rows[1::2]))
    def thickness_fn(p):
        retainerness = (p - retainer_face_start_center).dot(retainer_face_along)
        if retainerness > 1:
            ref = retainer_face_start_center + retainer_face_along*retainerness
        elif p[2] < bearing_top_z:
            ref = Point(0,0,p[2])
        else:
            d = Direction((p-revolution_center).projected_perpendicular(Back))
            ref = revolution_center+d*revolution_radius

        dist = p.distance(ref)
        return (dist - CPAP_inner_radius)*2 #/(((p-ref)/dist).projected_perpendicular(Up)).length()
        # if 0 < retainerness < 1:
        #     return CPAP_most_walls_thickness - CPAP_retainer_bite_depth*(1-abs(retainerness*2-1))
        # return ball_facing_radius(p[2]) - CPAP_inner_radius
    f = 900
    start, points, commands = make_spiral(
        v_to_cross_section_curve=curvefn,
        max_overhang=0.5,
        line_width=thickness_fn,
        max_layer_height=0.2,
        starting_downfill=0.1,
        f=f,
    )
    commands = ([
                    'M106 S255 ; Fan 100%',
                ] +
                square_jump(coords=start, min_transit_z=0.2) +
                commands)

    parity = 1
    for row in incomplete_torus_rows[1::2]:
        row = row[::parity]
        parity = -parity
        points.extend(row)
        commands.append(g1(coords=row[0], f=f))
        for p in row[1:]:
            commands.append(g1(coords=p, eplus_cross_sectional_mm2=thickness_fn(p)*0.2, f=f))

    gcode = wrap_gcode("\n".join(commands))

    export_string(gcode, "curved_tube_with_builtin_inner_race_5.gcode")

    return BSplineCurve(points, BSplineDimension(degree=1))


CPAP_outer_race_base = 0.5
@run_if_changed
def CPAP_outer_race_half():
    def outer_race_fn(v):
        z = v*(ball_radius/sq2 + CPAP_outer_race_base)
        z_above_base = z - CPAP_outer_race_base
        offs = max(0, z - CPAP_outer_race_base) - (ball_radius/sq2)

        r = CPAP_bearing_ball_center_offset + math.sqrt(ball_radius**2 - offs**2) + CPAP_min_wall_thickness + CPAP_ball_leeway
        if z_above_base < 0:
            r += z_above_base
        return Circle(Axes(Point(0,0,z), Up), r)
    outer_race_start, outer_race_points, outer_race_commands = make_spiral(
        v_to_cross_section_curve=outer_race_fn,
        max_overhang=0.5,
        line_width=CPAP_min_wall_thickness,
        max_layer_height=0.2,
        starting_downfill=0.1,
        f=900,
    )
    commands = ([
                    'M106 S255 ; Fan 100%',
                ] +
                square_jump(coords=outer_race_start, min_transit_z=0.2) +
                outer_race_commands)
    gcode = wrap_gcode("\n".join(commands))

    export_string(gcode, "CPAP_outer_race_3.gcode")

    return BSplineCurve(outer_race_points, BSplineDimension(degree=1))


@run_if_changed
def CPAP_bearings_retainer_ring():
    flat_bottom = Plane(Point(0,0,0), Up)
    flat_top = Plane(Point(0,0,CPAP_retainer_bite_thickness), Up)
    ball_center = Point(CPAP_bearing_ball_center_offset + CPAP_ball_leeway, 0, CPAP_retainer_bite_thickness + ball_radius+0.1)
    a = ball_center + Direction(1,0,-1)*(ball_radius+CPAP_min_wall_thickness)
    b = a + Direction(1,0,-1)*CPAP_min_wall_thickness
    arc = Edge(a,b).revolve(Axis(ball_center, Back), Degrees(-90))

    rest = Face(Wire([
        b.projected(flat_bottom, by=Direction(-1,0,-1)),
        b,
        a,
        a.projected(flat_top, by=Direction(-1,0,-1)),
        Point(CPAP_inner_radius + CPAP_most_walls_thickness, 0, CPAP_retainer_bite_thickness),
        Point(CPAP_inner_radius + CPAP_min_wall_thickness, 0, CPAP_retainer_bite_thickness/2),
        Point(CPAP_inner_radius + CPAP_most_walls_thickness, 0, 0),
    ], loop=True))
    whole_thing = Compound(arc, rest).revolve(Up)

    slit_thickness=1

    tabs = Compound(
        Vertex(b).revolve(Axis(ball_center, Back), Degrees(-90)),
        Edge(b, b.projected(flat_bottom, by=Direction(-1,0,-1))),
    ).extrude(Left*0.2,Right*5).extrude(Back*(CPAP_min_wall_thickness*2+slit_thickness), centered=True)
    slit = Vertex(Origin).extrude(Back*slit_thickness, centered=True).extrude(Right*100).extrude(Up*100)
    # preview(whole_thing, tabs, slit)
    tab_holes = Face(Circle(Axes(b+Right*3+Up*ball_center[2],Back),1)).extrude(Back*10, centered=True)
    
    result = Compound(
        whole_thing,
        tabs.cut(tab_holes),
    ).cut(slit)

    save_STL("CPAP_bearings_retainer_ring", result)
    export("CPAP_bearings_retainer_ring.stl", "CPAP_bearings_retainer_ring_2.stl")
    preview(result)
    return result



preview(curved_tube_with_builtin_inner_race, CPAP_outer_race_half, CPAP_bearings_retainer_ring @ Translate(Down*(CPAP_retainer_bite_thickness+0.1)))