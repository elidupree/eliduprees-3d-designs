import math

filament_diameter = 1.75
mm3_per_extrusion_distance = filament_diameter * filament_diameter
ender3_center_x = 235/2
ender3_center_y = 235/2

def start_gcode(min_temp = 200, good_temp = 255):
    return f'''
G90     ; Use absolute positioning
G92 E0  ; Set extruder reference point
M107    ; Fan off to start

; start heating while we move
M104 S{min_temp}

G28     ; Home all axes

; need to reach min temp before initial wipe:
; M109 S{min_temp}
; ...but keep heating up while we do it:
; M104 S{good_temp}
M109 S{good_temp}

; start initial wipe, borrowed from Cura:
G1 Z2.0 F3000 ; Move Z Axis up little to prevent scratching of Heat Bed
G1 X0.1 Y20 Z0.3 F5000.0 ; Move to start position
G1 X0.1 Y200.0 Z0.3 F1500.0 E15 ; Draw the first line
G1 X0.4 Y200.0 Z0.3 F5000.0 ; Move to side a little

; ...want to reach max temp before we finish the initial wipe:
; M109 S{good_temp}

; rest of initial wipe, borrowed from Cura:
G1 X0.4 Y20 Z0.3 F1500.0 E30 ; Draw the second line
G92 E0 ; Reset Extruder
G1 Z2.0 F3000 ; Move Z Axis up little to prevent scratching of Heat Bed
G1 X5 Y20 Z0.3 F5000.0 ; Move over to prevent blob squish

'''

def finish_gcode():
    machine_depth = 235
    return f'''
; borrowed from Cura, just tweaked order (we can turn heat off before leaving):
M104 S0 ;Turn-off hotend
M140 S0 ;Turn-off bed
G91 ;Relative positioning
G1 E-2 F2700 ;Retract a bit
G1 E-2 Z0.2 F2400 ;Retract and raise Z
G1 X5 Y5 F3000 ;Wipe out
M106 S0 ;Turn-off fan
G1 Z10 ;Raise Z more
G90 ;Absolute positioning

G1 X0 Y{machine_depth} ;Present print

M84 X Y E ;Disable all steppers but Z
    '''

def wrap_gcode(gcode, **kwargs):
    return start_gcode(**kwargs) + gcode + finish_gcode(**kwargs)

def fastmove(x=None, y=None, z=None, coords=None):
    if coords is not None:
        x,y,z = coords
    result = ["G0"]
    if x is not None:
        last_position["x"] = x
        result.append(f'X{ender3_center_x + x:.5f}')
    if y is not None:
        last_position["y"] = y
        result.append(f'Y{ender3_center_y + y:.5f}')
    if z is not None:
        last_position["z"] = z
        result.append(f'Z{z:.5f}')

    result.append('F18000')
    return " ".join(result)

def square_jump(x=None, y=None, z=None, coords=None, *, min_transit_z):
    if coords is not None:
        x,y,z = coords
    result = []
    if last_position["z"] < min_transit_z:
        result.append(fastmove(z=min_transit_z))
    if z < min_transit_z:
        result.append(fastmove(x=x,y=y,z=min_transit_z))
        result.append(fastmove(z=z))
    else:
        result.append(fastmove(x=x,y=y,z=z))
    return result

last_position = {"x":0,"y":0,"z":0,"e":0}
def set_extrusion_reference(e):
    last_position["e"] = e
    return f'G92 E{e:.5f}'

def g1(x=None, y=None, z=None, e=None, f=None, coords=None, eplus=None, eplus_cross_sectional_area=None):
    result = ["G1"]
    if coords is not None:
        x,y,z = coords
    if x is None:
        x = last_position["x"]
    if y is None:
        y = last_position["y"]
    if z is None:
        z = last_position["z"]

    if eplus_cross_sectional_area is not None:
        dist = math.sqrt((x-last_position["x"])**2 + (y-last_position["y"])**2 + (z-last_position["z"])**2)
        eplus = eplus_cross_sectional_area*dist
    if eplus is not None:
        e = last_position["e"] + eplus
    if e is None:
        e = last_position["e"]

    if x != last_position["x"]:
        last_position["x"] = x
        result.append(f'X{ender3_center_x + x:.5f}')
    if y != last_position["y"]:
        last_position["y"] = y
        result.append(f'Y{ender3_center_y + y:.5f}')
    if z != last_position["z"]:
        last_position["z"] = z
        result.append(f'Z{z:.5f}')
    if e != last_position["e"]:
        last_position["e"] = e
        result.append(f'E{e:.5f}')

    if f is not None:
        result.append(f'F{f}')
    
    return " ".join(result)