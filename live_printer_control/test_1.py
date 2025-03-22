import functools
import math
import sys
from collections import deque
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
commands_sent = deque()
def queue_command(command):
    command_queue.put(command)
printer_busy = False
def send_command(command):
    assert ("\n" not in command)
    print(f"sending {repr(command)}")
    ser.write((command+"\n").encode())
    commands_sent.append(command)
    if len(commands_sent) > 5:
        commands_sent.popleft()

def stdio_thread_fn():
    while True:
        l = sys.stdin.readline()
        command_queue.append(l)

stdio_thread = threading.Thread(target = stdio_thread_fn)
stdio_thread.start()

ser = serial.Serial("COM3", 115200, timeout=1, xonxoff=False)
time.sleep(1)
send_command("M155 S1") # auto report temperature every 1s
queue_command("G91")
joystick_induced_velocity = np.zeros(2, dtype=np.float64)
joystick_target_velocity = np.zeros(2, dtype=np.float64)
assumed_max_mm_ss = 450
max_mm_s = 25
min_lookahead_duration = max_mm_s/assumed_max_mm_ss + 0.02 + 0.5
max_lookahead_duration = min_lookahead_duration #+ 0.02
joystick_movement_planned_through = time.time()

def move_in_duration(dp, t):
    if np.linalg.norm(dp) < 0.01:
        return
    feedrate_mm_s = np.linalg.norm(dp)/t
    queue_command(f"G0 X{dp[0]:.5f} Y{dp[1]:.5f} F{feedrate_mm_s*60:.5f}")


def plan_joystick_movement():
    now = time.time()
    global joystick_movement_planned_through, joystick_induced_velocity, joystick_target_velocity
    joystick_movement_planned_through = max(joystick_movement_planned_through, now)
    current_lookahead = joystick_movement_planned_through - now
    if current_lookahead < min_lookahead_duration and (np.any(joystick_induced_velocity) or np.any(joystick_target_velocity)):
        time_to_plan = max_lookahead_duration - current_lookahead
        joystick_movement_planned_through += time_to_plan
        dv = joystick_target_velocity - joystick_induced_velocity
        norm = np.linalg.norm(dv)
        acceleration = 0
        speedup_time = 0
        if norm != 0:
            speedup_time = min(norm / assumed_max_mm_ss, time_to_plan)
            acceleration = dv/norm * assumed_max_mm_ss
            joystick_induced_velocity += acceleration*speedup_time
            dp_while_accelerating = joystick_induced_velocity * speedup_time + acceleration*speedup_time*speedup_time/2
            move_in_duration(dp_while_accelerating, speedup_time)
        print (speedup_time, time_to_plan, joystick_target_velocity, joystick_induced_velocity, acceleration)
        if speedup_time < time_to_plan:
            joystick_induced_velocity = joystick_target_velocity
            if np.any(joystick_target_velocity):
                plateau_time = time_to_plan - speedup_time
                dp_after = plateau_time * joystick_target_velocity
                move_in_duration(dp_after, plateau_time)



latest_serial_responses = ""
def handle_line_from_printer(line):
    if line.startswith("ok"):
        print(line)
        printer_busy = False
    elif line.startswith("echo:busy:"):
        printer_busy = True
    else:
        print("unhandled input from printer:", line)
        if line.startswith("echo:Unknown command:"):
            print(commands_sent)

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
        def ax_fn(ax):
            deadzone = 0.1
            mag = (abs(ax) - deadzone) / (1.0 - deadzone)
            if mag < 0.0:
                return 0
            return np.sign(ax)*mag*mag*max_mm_s
        joystick_target_velocity = np.array([ax_fn(axes[0]), ax_fn(-axes[1])], dtype=np.float64)
    if not printer_busy:
        for _ in range(5):
            if command_queue.empty():
                break
            send_command(command_queue.get())

    time.sleep(0.01)

ser.close()