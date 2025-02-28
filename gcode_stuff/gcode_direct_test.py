import math
import sys

import serial
import serial.tools.list_ports
import time
import threading
import pygame

pygame.init()

#initialise the joystick module
pygame.joystick.init()
joysticks = []

print("Serial ports", [p.device for p in serial.tools.list_ports.comports()])

command_queue = []
def stdio_thread_fn():
    while True:
        l = sys.stdin.readline()
        command_queue.append(l)

stdio_thread = threading.Thread(target = stdio_thread_fn)
stdio_thread.start()

ser = serial.Serial("COM4", 115200, timeout=1)
time.sleep(1)
ser.write("M155 S1\n".encode()) # auto report temperature every 1s
while True:
    if ser.in_waiting > 0:
        print(ser.read(ser.in_waiting).decode())
    for event in pygame.event.get():
        if event.type == pygame.JOYDEVICEADDED:
            joystick = pygame.joystick.Joystick(event.device_index)
            joysticks.append(joystick)
            print(f"added joystick with {joystick.get_numbuttons()} buttons and {joystick.get_numaxes()} axes")
    for i,joystick in enumerate(joysticks):
        pass
        # print([joystick.get_axis(i) for i in range(joystick.get_numaxes())])
        axes = [joystick.get_axis(i) for i in range(joystick.get_numaxes())]
        if any(abs(v) > 0.1 for v in axes[:2]):
            parts = ["G1"]
            xy = [1*v for v in axes[:2]]
            xy[1] *= -1
            dist = math.sqrt(xy[0]**2 + xy[1]**2)
            for d,v in zip("XY", xy[:2]):
                parts.append(f"{d}{v:.5f}")
            parts.append(f"F{600*dist:.5f}")
            command_queue.append("G91\n")
            command_queue.append(" ".join(parts) + "\n")
    for command in command_queue:
        print(f"sending {repr(command)}")
        ser.write(command.encode())
    command_queue = []



    time.sleep(0.1)

ser.close()