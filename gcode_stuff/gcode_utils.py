
filament_diameter = 1.75
mm3_per_extrusion_distance = filament_diameter * filament_diameter

def start_gcode(min_temp = 200, good_temp = 250):
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
