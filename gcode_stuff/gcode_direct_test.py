import math
import sys
from queue import Queue

import serial
import serial.tools.list_ports
import time
import threading
import pygame
import numpy as np

pygame.init()

#initialise the joystick module
pygame.joystick.init()
joysticks = []

print("Serial ports", [p.device for p in serial.tools.list_ports.comports()])

command_queue = Queue()
def queue_command(command):
    command_queue.put(command)
printer_busy = False
def send_command(command):
    # print(f"sending {repr(command)}")
    ser.write((command+"\n").encode())

def stdio_thread_fn():
    while True:
        l = sys.stdin.readline()
        command_queue.append(l)

stdio_thread = threading.Thread(target = stdio_thread_fn)
stdio_thread.start()

ser = serial.Serial("COM3", 115200, timeout=1)
time.sleep(1)
send_command("M155 S1") # auto report temperature every 1s
joystick_induced_velocity = np.zeros(2)
joystick_target_velocity = np.zeros(2)
assumed_max_mm_ss = 400
max_mm_s = 25
lookahead_duration = max_mm_s/assumed_max_mm_ss + 0.02
joystick_movement_planned_through = time.time()

def plan_joystick_movement():
    now = time.time()
    global joystick_movement_planned_through, joystick_induced_velocity, joystick_target_velocity
    joystick_movement_planned_through = max(joystick_movement_planned_through, now)
    time_to_plan = now + lookahead_duration - joystick_movement_planned_through
    if time_to_plan > 0 and (np.any(joystick_induced_velocity) or np.any(joystick_target_velocity)):
        dv = joystick_target_velocity - joystick_induced_velocity
        norm = np.linalg.norm(dv, np.inf)
        speedup_time = min(norm / assumed_max_mm_ss, time_to_plan)
        if norm != 0:
            acceleration = dv/norm
        else:
            acceleration = 0
        dp_while_accelerating = joystick_induced_velocity * speedup_time + acceleration*speedup_time/2
        dp_after = (time_to_plan - speedup_time) * joystick_target_velocity
        dp = dp_while_accelerating + dp_after
        feedrate_mm_s = np.linalg.norm(dp, np.inf)/time_to_plan
        joystick_movement_planned_through += time_to_plan
        joystick_induced_velocity += acceleration*speedup_time
        if speedup_time == time_to_plan:
            joystick_induced_velocity = joystick_target_velocity
        queue_command("G91")
        queue_command(f"G1 X{dp[0]:.5f} Y{dp[1]:.5f} F{feedrate_mm_s*60:.5f}")



latest_serial_responses = ""
def handle_line_from_printer(line):
    if line.startswith("ok"):
        printer_busy = False
    elif line.startswith("echo:busy:"):
        printer_busy = True
    else:
        print("unhandled input from printer:", line)

while True:
    if ser.in_waiting > 0:
        data = ser.read(ser.in_waiting).decode()
        latest_serial_responses += data
        split = latest_serial_responses.split("\n", 1)
        if len(split) > 1:
            latest_serial_responses = split[1]
            handle_line_from_printer(split[0])

    for event in pygame.event.get():
        if event.type == pygame.JOYDEVICEADDED:
            joystick = pygame.joystick.Joystick(event.device_index)
            joysticks.append(joystick)
            print(f"added joystick with {joystick.get_numbuttons()} buttons and {joystick.get_numaxes()} axes")
    plan_joystick_movement()
    for i,joystick in enumerate(joysticks):
        # print([joystick.get_axis(i) for i in range(joystick.get_numaxes())])
        axes = [joystick.get_axis(i) for i in range(joystick.get_numaxes())]
        # if any(abs(v) > 0.1 for v in axes[:2]):
        #     parts = ["G1"]
        #     xy = [1*v for v in axes[:2]]
        #     xy[1] *= -1
        #     dist = math.sqrt(xy[0]**2 + xy[1]**2)
        #     for d,v in zip("XY", xy[:2]):
        #         parts.append(f"{d}{v:.5f}")
        #     parts.append(f"F{600*dist:.5f}")
        #     queue_command("G91")
        #     queue_command(" ".join(parts))
        joystick_target_velocity = np.array([np.sign(v) * max(0, abs(v) - 0.1) * max_mm_s for v in axes[:2]])
    if not printer_busy:
        for _ in range(5):
            if command_queue.empty():
                break
            send_command(command_queue.get())

    time.sleep(0.01)

ser.close()