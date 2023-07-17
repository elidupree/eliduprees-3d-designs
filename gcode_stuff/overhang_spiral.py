import math

from gcode_stuff.gcode_utils import *

def spiral_code(nozzle_diameter, layer_height, center_x, center_y,):
    z = 0
    radius = 10
    extrusion = 0

    commands = [
        'G92 E0  ; Set extruder reference point',
        'M107    ; Fan off to start',
        f'G0 X{center_x - radius:.5f} Y{center_y:.5f} Z0 F18000',
    ]
    num_columns = 360
    column_heights = [0]*num_columns
    which_column = 0
    last_fan_speed = 0
    while z < 20:
        angle_change = math.tau / num_columns
        distance_moved = angle_change * radius
        angle = angle_change * which_column
        x = math.cos(angle) * radius
        y = math.sin(angle) * radius

        line_width = nozzle_diameter * (2 + math.cos(angle))

        slope = z / 5
        layer_offset = slope * layer_height
        # move up by one layer each rotation:
        z += layer_height * (angle_change / math.tau)
        # move out by layer_offset each rotation:
        radius += layer_offset * (angle_change / math.tau)

        actual_z_increase = z - column_heights[which_column]
        column_heights[which_column] = z
        extrusion += (distance_moved * actual_z_increase * line_width) / mm3_per_extrusion_distance

        fan_frac = max(0, min(1, z / 0.2 - 0.1))
        fan_speed = round(fan_frac*255)
        if fan_speed != last_fan_speed:
            commands.append(f'M106 S{fan_speed}')
            last_fan_speed = fan_speed
        commands.append(f'G1 X{center_x - x:.5f} Y{center_y + y:.5f} Z{z:.5f} E{extrusion:.5f} F1500')

        which_column = (which_column + 1) % num_columns

    return "\n".join(commands)


print(wrap_gcode(spiral_code(nozzle_diameter=0.4, layer_height=0.3, center_x = 235/2, center_y = 235/2)))
