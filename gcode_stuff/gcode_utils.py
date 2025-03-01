import math

filament_diameter = 1.75
mm3_per_extrusion_distance = filament_diameter * filament_diameter
ender3_size_y = 235
ender3_center_x = 235/2
ender3_center_y = ender3_size_y/2

def start_gcode(min_temp = 240, good_temp = 255):
    return f'''
G90     ; Use absolute positioning
G92 E0  ; Set extruder reference point
M107    ; Fan off to start

; start heating while we move
M104 S{good_temp}

G28     ; Home all axes

; need to reach min temp to make sure we don't try to shove cold filament into the build plate, but keep heating up while we do it
; (relying on EliDupree custom behavior for M109+M104)
M109 S{min_temp}
M104 S{good_temp}
  
G1 X0.1 Y10 Z0 F2000.0 ; enter the bed on Z=zero, to scrape off any current ooze
  
; get closer to target temp before initial wipe, but keep heating up while we do it
; (relying on EliDupree custom behavior for M109+M104)
M109 S{max(min_temp, good_temp - 10)}
M104 S{good_temp} ; ...

; start initial wipe, modified from Cura's:
; G1 Z2.0 F3000 ; Move Z Axis up little to prevent scratching of Heat Bed
G1 X0.1 Y20 Z0.3 F5000.0 ; Move to start position
G1 X0.1 Y200.0 Z0.3 F1500.0 E15 ; Draw the first line
G1 X1.3 Y200.0 Z0.3 F5000.0 ; Move to side a little

; Get near max temp before we finish the initial wipe
; (was relying on EliDupree custom behavior for M109+M104, but actually we probably better get to the target for real, to make it steady for the real print)
; M109 S{max(min_temp, good_temp-5)}
; M104 S{good_temp}
M109 S{good_temp}

; rest of initial wipe, modified from Cura's:
G1 X1.3 Y20 Z0.3 F1500.0 E30 ; Draw the second line
G1 X5 Y20 Z0.1 F5000.0 ; Move over and get lower, to make sure not to drag the filament with us
G92 E0 ; Reset Extruder

'''

def finish_gcode():
    machine_depth = ender3_size_y
    return f'''
; borrowed from Cura, just tweaked order (we can turn heat off before leaving):
M104 S0 ;Turn-off hotend
M140 S0 ;Turn-off bed
G91 ;Relative positioning
G1 E-2 F2700 ;Retract a bit
G1 E-2 Z0.2 F2400 ;Retract and raise Z
G1 X5 Y5 F3000 ;Wipe out
G1 Z10 E-10 ;Raise Z more, retract more
G90 ;Absolute positioning

G1 X0 Y{machine_depth} ;Present print
M106 S0 ;Turn-off fan
; G1 Z2 ;Go to bed to help suppress oozing. note that the back 17mm of Y are "safe" from smacking the X rail into the print (the nozzle can't print that far back). (I ended up not using this because I don't want to risk descending into a print if it got stuck to the hotend)
; M106 S0 ;Turn-off fan
; G1 X10 Z0.2 F5000 ;wipe off any current ooze, first quickly...
; G91 ;Relative positioning
; G1 Y-10 Z-0.2 F5000 ; then down to bed to block harder
; G90 ;Absolute positioning
; G1 X0 F10 ; ...then very slowly

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

# Hack: update the globals that say where we are
def assume_at(**kwargs):
    fastmove(**kwargs)

def square_jump(x=None, y=None, z=None, coords=None, *, min_transit_z):
    if coords is not None:
        x,y,z = coords
    if (x,y) == (last_position["x"],last_position["y"]):
        if z == last_position["z"]:
            return []
        return [fastmove(z=z)]
    result = []
    if last_position["z"] < min_transit_z:
        result.append(fastmove(z=min_transit_z))
    if z < min_transit_z:
        result.append(fastmove(x=x,y=y,z=min_transit_z))
        result.append(fastmove(z=z))
    else:
        result.append(fastmove(x=x,y=y,z=z))
    return result

last_position = {"x":0,"y":0,"z":0,"e_filament":0}

def zero_extrusion_reference():
    return set_extrusion_reference(e_filament=0)
def set_extrusion_reference(*, e_filament):
    last_position["e_filament"] = e_filament
    return f'G92 E{e_filament:.5f}'

def g1(x=None, y=None, z=None, e_filament=None, e_mm3=None, f=None, coords=None, eplus_mm3=None, eplus_cross_sectional_mm2=None):
    result = ["G1"]
    if coords is not None:
        x,y,z = coords
    if x is None:
        x = last_position["x"]
    if y is None:
        y = last_position["y"]
    if z is None:
        z = last_position["z"]

    if eplus_cross_sectional_mm2 is not None:
        dist = math.sqrt((x-last_position["x"])**2 + (y-last_position["y"])**2 + (z-last_position["z"])**2)
        eplus_mm3 = eplus_cross_sectional_mm2*dist
    if eplus_mm3 is not None:
        e_mm3 = last_position["e_filament"]*mm3_per_extrusion_distance + eplus_mm3
    if e_mm3 is not None:
        e_filament = e_mm3 / mm3_per_extrusion_distance
    if e_filament is None:
        e_filament = last_position["e_filament"]

    if x != last_position["x"]:
        last_position["x"] = x
        result.append(f'X{ender3_center_x + x:.5f}')
    if y != last_position["y"]:
        last_position["y"] = y
        result.append(f'Y{ender3_center_y + y:.5f}')
    if z != last_position["z"]:
        last_position["z"] = z
        result.append(f'Z{z:.5f}')
    if e_filament != last_position["e_filament"]:
        last_position["e_filament"] = e_filament
        result.append(f'E{e_filament:.5f}')

    if f is not None:
        result.append(f'F{f}')
    
    return " ".join(result)