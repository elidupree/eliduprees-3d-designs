"""

Move planner notes:

If we do this naïvely, then when you're trying to move fast, the move planner won't know your future movement, so it will conservatively limit the speed so that you would be able to decelerate to a stop by the end of the known movement.

To avoid this, we plan moves in advance. If the printer has a max acceleration of A, and the maximum speed you want to go is V, then the required pre-commit duration is V/A. Since we are fine with a max speed of 50mm/s and a max acceleration of 500mm/s/s, this allows us to use 0.1s pre-commit duration (well, slightly more to make sure the printer receives the commands in time), which is fine. This adds 0.12s of latency to the joystick inputs, which is smaller than human reaction time. As a quirk, when you *start* motion, it fills out the whole 0.12s with the first nonzero joystick input.

To make our own moves smooth given arbitrary joystick inputs, we send move commands every 0.01s.

…but also, moves might sometimes be slowed down by junction deviation limits, or other quirks of the planner that I don't know about. To deal with this, we keep track of when the moves are actually finished. The guiding assumption is that we are _approximately_ correct, and most of our moves will take approximately 0.01s as intended. So, at any given moment, we know the following:

* The current real time
* The number of precommit moves that are still in the planning buffer
* ...which give us a _predicted moment_ when those moves will run out, which will never be longer than the intended 0.12s from "now"
* The position of the joystick

So we simply apply our own movement rules as if exactly 0.01s are passing, based on the current joystick position, until the predicted run-out time exceeds 0.12s... which is the same as just filling up the buffer until there are 12 commands in it. Effectively, from our code's perspective, if a move takes longer in reality, we act as if _less time passes_.

"""
import math
import time
from dataclasses import dataclass
from threading import Thread
from typing import List
import numpy as np
import pygame

from live_printer_control.connection import Command, CommandStatus, PositionReport
from live_printer_control.scene import Scene, SceneManager


def move_code(dp, max_feedrate_mm_s):
    return f"G1 X{dp[0]:.5f} Y{dp[1]:.5f} F{max_feedrate_mm_s * 60:.5f}"

@dataclass
class PlannedMove:
    command: Command
    expected_end_position: np.array
    expected_completion_time: float

class JoystickControl(Scene):
    _max_speed: float
    _max_acceleration: float
    _step_duration: float
    _num_steps_to_plan_at_once: int
    _current_velocity: np.array
    _target_velocity: np.array
    _planned_moves: List[PlannedMove]

    def __init__(self, max_speed=50, max_acceleration=500, step_duration=0.02):
        self._max_speed = max_speed
        self._max_acceleration = max_acceleration
        self._step_duration = step_duration
        self._num_steps_to_plan_at_once = math.ceil((self._max_speed / self._max_acceleration)/step_duration) + 2
        self._current_velocity = np.zeros(2, dtype=np.float64)
        self._target_velocity = np.zeros(2, dtype=np.float64)
        self._planned_moves = []

    def enter(self, manager: SceneManager):
        manager.update_printer_settings({
            "M201": {"X": self._max_acceleration, "Y": self._max_acceleration},
            "M204": {"T": self._max_acceleration},
            "M205": {
                #"B": math.floor(self._step_duration * 1_000_000),
                "B": 0,
                "S": 0, "T": 0, "J": 0.08},
        })
        # TODO fix hack
        manager.send("G91")
        Thread(target=self._pester_printer, args=[manager], daemon=True).start()

    def _expected_printer_position(self, manager: SceneManager):
        if self._planned_moves:
            return self._planned_moves[-1].expected_end_position
        else:
            report = manager.last_position_report()
            if report is None:
                return None
            return np.array([report.x, report.y])

    def _do_next_step(self, manager: SceneManager):
        if len(self._planned_moves) >= self._num_steps_to_plan_at_once:
            # print("already planned enough")
            return False

        if not (np.any(self._current_velocity) or np.any(self._target_velocity)):
            # print("stationary")
            return False

        dv = self._target_velocity - self._current_velocity
        dv_norm = np.linalg.norm(dv)
        speedup_time = 0
        expected_completion_time = time.time() + len(self._planned_moves)*self._num_steps_to_plan_at_once
        # dp = np.zeros(2, dtype=np.float64)
        # old_velocity = self._current_velocity
        if dv_norm != 0:
            speedup_time = min(dv_norm / self._max_acceleration, self._step_duration)
            acceleration = dv / dv_norm * self._max_acceleration
            dp_while_accelerating = self._current_velocity * speedup_time + acceleration * speedup_time * speedup_time / 2
            # since feedrate is a maximum, we need to use the end-speed if we're accelerating and the start-speed if we're decelerating
            max_feedrate_mm_s = np.linalg.norm(self._current_velocity)
            self._current_velocity += acceleration * speedup_time
            max_feedrate_mm_s = max(max_feedrate_mm_s, np.linalg.norm(self._current_velocity))
            # dp += dp_while_accelerating
            self._planned_moves.append(PlannedMove(manager.send(move_code(dp_while_accelerating, max_feedrate_mm_s)), self._expected_printer_position(manager) + dp_while_accelerating, expected_completion_time))
            # print("A:", self._current_velocity, self._target_velocity, dv, acceleration, speedup_time, dp_while_accelerating)

        # if acceleration stops partway through a step,

        if speedup_time < self._step_duration:
            self._current_velocity = self._target_velocity.copy()
            if np.any(self._target_velocity):
                plateau_time = self._step_duration - speedup_time
                dp_after = plateau_time * self._target_velocity
                # dp += dp_after
                self._planned_moves.append(PlannedMove(manager.send(move_code(dp_after, np.linalg.norm(self._current_velocity))), self._expected_printer_position(manager) + dp_after, expected_completion_time))
                # print("B:", self._current_velocity, self._target_velocity, dv, speedup_time, dp_after)

        # self._planned_moves.append(manager.send(move_in_duration(dp, self._step_duration)))
        # print("added plan?", dv_norm != 0, speedup_time < self._step_duration, speedup_time)
        return True

    def _preplan_as_needed(self, manager: SceneManager):
        while self._do_next_step(manager):
            pass

    def on_update(self, manager: SceneManager):
        self._planned_moves = [p for p in self._planned_moves if p.command.status() != CommandStatus.CONSUMED]
        # print([p.command.status() for p in self._planned_moves])
        self._preplan_as_needed(manager)

    def on_position_report(self, manager: "SceneManager", position: PositionReport):
        position = np.array([position.x, position.y])
        now = time.time()
        while self._planned_moves:
            if self._planned_moves[0].expected_completion_time > now:
                return
            dist = np.linalg.norm(self._planned_moves[0].expected_end_position - position)
            if dist < 0.0001:
                self._planned_moves.pop(0)
                continue
            elif len(self._planned_moves) >= 2:
                d2 = np.linalg.norm(self._planned_moves[1].expected_end_position - position)
                if d2 < dist:
                    self._planned_moves.pop(0)
                    continue

            break

    def on_pygame_event(self, manager: "SceneManager", event: pygame.event.Event):
        if event.type == pygame.JOYAXISMOTION:
            # print(event.axis, event.value)
            if event.axis < 2:
                value = event.value
                if event.axis == 1:
                    value = -value
                deadzone = 0.1
                mag = abs(value)
                if mag < deadzone:
                    self._target_velocity[event.axis] = 0
                else:
                    self._target_velocity[event.axis] = np.sign(value)*mag*mag*self._max_speed
                self._preplan_as_needed(manager)

    def _pester_printer(self, manager):
        while True:
            time.sleep(0.1)
            manager.send("M114 R")
