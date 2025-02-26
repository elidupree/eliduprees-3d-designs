import math
from gcode_stuff.gcode_utils import *
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
    result = [set_extrusion_reference(0)]

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
            result.append(g1(x=x, y=y, z=top_z, eplus=line_width*stroke_thickness*radius*(math.tau/360), f=f))


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

        shared_args = {"top_z":top_z, "height":layer_height, "line_width":line_width,"min_transit_z":layer_height/2}

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
        max_layer_height=0.15,
        leeway=0.9)

    gcode = wrap_gcode("\n".join(commands))

    export_string(gcode, "bearing_1.gcode")




