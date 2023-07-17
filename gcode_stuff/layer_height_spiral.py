import math

from gcode_stuff.gcode_utils import wrap_gcode


def spiral_code(nozzle_diameter):
    z = 0
    radius = 20
    center_x = 235 / 2
    center_y = 235 / 2
    extrusion = 0
    filament_diameter = 1.75
    volume_per_extrusion_distance = filament_diameter * filament_diameter

    starting_layer_height = 0.1 * nozzle_diameter

    commands = [
        f'G0 X{center_x - radius:.5f} Y{center_y:.5f} Z{starting_layer_height:.5f} F18000'
    ]
    num_columns = 360
    column_heights = [0]*num_columns
    which_column = 0
    last_fan_speed = 0
    while z < 100:
        angle_change = math.tau / num_columns
        distance_moved = angle_change * radius
        angle = angle_change * which_column
        x = math.cos(angle) * radius
        y = math.sin(angle) * radius
        layer_height = (z / 50 + 0.1) * nozzle_diameter
        # move up by one layer each rotation:
        z += layer_height * (angle_change / math.tau)
        actual_z_increase = z - column_heights[which_column]
        column_heights[which_column] = z
        extrusion += (distance_moved * actual_z_increase * nozzle_diameter) / volume_per_extrusion_distance

        fan_frac = max(0, min(1, z / 0.84 - 0.1))
        fan_speed = round(fan_frac*255)
        if fan_speed != last_fan_speed:
            commands.append(f'M106 S{fan_speed}')
            last_fan_speed = fan_speed
        commands.append(f'G1 X{center_x - x:.5f} Y{center_y + y:.5f} Z{z:.5f} E{extrusion:.5f} F1500')

        which_column = (which_column + 1) % num_columns

    return "\n".join(commands)


print(wrap_gcode(spiral_code(0.5)))
