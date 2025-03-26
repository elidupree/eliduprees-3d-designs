import time

from connection import PrinterConnection

with PrinterConnection() as connection:
    connection.send("G91")
    connection.send("G28")
    connection.send("M109 S255")
    connection.send("G92 E0")
    connection.send("G1 X20 Y20")
    while True:
        parts = input().split(",")
        if parts[0] == "q":
            break

        for part in parts:
            connection.send(part.strip())
        # e, z, f = parts
        # connection.send(f"G1 Z0.3 F18000")
        # connection.send(f"G1 Y200 E{e}")
        # connection.send(f"G1 X2")
        # connection.send(f"G1 Y-200 F{f}")
        # connection.send(f"G1 X2")
        '''
        G1 Z0.3 F18000, G1 Y200 E20 F18000, G1 X2 F18000, G1 Y-200 F600, G1 X2 F18000
        G1 Y200 E20 F1200, G1 X2 F18000, G1 Y-200 F300, G1 X2 F18000
        G1 Y200 E20 F600, G1 X2 F18000, G1 Y-10 F600, G1 Y-190 F100, G1 X2 F18000
        G1 Y200 E20 F1200, G1 X2 F18000, G1 Y-5 F800, G1 Y-5 F600, G1 Y-5 F400, G1 Y-5 F200, G1 Y-180 F100, G1 X2 F18000
        G1 Y200 E20 F800, G1 X2 F18000, G1 Y-5 F800, G1 Y-5 F600, G1 Y-5 F400, G1 Y-5 F200, G1 Y-5 Z-0.2 F100, G1 Y-175 F100, G1 X2 Z0.2 F18000,
        G1 Z0.1
        G1 Y200 E20 F400, G1 X2 F18000, G1 Y-5 F800, G1 Y-5 F600, G1 Y-5 F400, G1 Y-5 F200, G1 Y-5 Z-0.2 F100, G1 Y-175 F100, G1 X2 Z0.2 F18000,
        G1 Z1, G1 Y200 E20 F500, G1 Z-1 X2 F18000, G1 Y-10 F2000, G1 Y-10 F1500, G1 Y-10 F1000, G1 Y-10 F500, G1 Y-10 F100, G1 Y-10 F20, G1 Y-175 F300, G1 X2 F18000,
        G1 Z0.3
        G1 Y20
        G1 Z0.5, G1 Y200 E20 F600, G1 Z-0.5 X2 F18000, G1 Y-10 F1000, G1 Y-10 F750, G1 Y-10 F500, G1 Y-10 F250, G1 Y-10 F100, G1 Y-10 F20, G1 Y-140 F300, G1 X2 F18000,
        G1 Z0.5, G1 Y200 E20 F800, G1 Z-0.5 X2 F18000, G1 Y-10 F500, G1 Y-10 F375, G1 Y-10 F250, G1 Y-10 F125, G1 Y-10 F80, G1 Y-10 F40, G1 Y-140 F300, G1 X2 F18000,
        G1 Z0.5, G1 Y200 E20 F1000, G1 Z-0.5 X2 F18000, G1 Y-10 F350, G1 Y-10 F300, G1 Y-10 F250, G1 Y-10 F200, G1 Y-10 F150, G1 Y-10 F100, G1 Y-10 F75, G1 Y-10 F50, G1 Y-120 F300, G1 X2 F18000,
        G1 Z0.3, G1 Y200 E20 F1200, G1 Z-0.3 X2 F18000, G1 Y-200 F250,
        G1 X2 F18000,
        G1 Z0.3, G1 Y200 E20 F2400, G1 Z-0.3 X2 F18000, G1 Y-200 F250, G1 X2 F18000, G1 Y200 F250, G1 X2 F18000, G1 Y200 F250, G1 X2 F18000
        G1 Y-15 F250
        G1 Y-200 F250
        G1 Z0.3, G1 Y200 E20 F4800, G1 Z-0.3 X2 F18000, G1 Y-20 F150, G1 Y-120 F250, G1 Y-60 F125, G1 X4 F18000
        G1 Z0.3, G1 Y200 E30 F4800, G1 Z-0.3 X2 F18000, G1 Y-2 F1000, G1 Y-8 F500, G1 Y-10 F150, G1 Y-100 F250, G1 Y-80 F125, G1 X3 F18000
        G1 Z0.3, G1 Y200 E23 F4800, G1 Z-0.3 X2 F18000, G1 Y-2 F2000, G1 Y-8 F800, G1 Y-5 F500, G1 Y-5 F150, G1 Y-100 F250, G1 Y-80 F125, G1 X3 F18000
        G1 Z0.3, G1 Y200 E20 F7500, G1 Z-0.2 X2 F18000, G1 Y-2 F2000, G1 Y-8 F800, G1 Y-5 Z-0.1 F500, G1 Y-5 F150, G1 Y-80 F250, G1 Y-30 F125, G1 Y-70 F80, G1 X3 F18000
        '''

    connection.send("M104 0")


