import functools
import os
import re
import sys
import time
from collections import deque
from dataclasses import dataclass
from enum import Enum
from threading import Thread

import serial
import serial.tools.list_ports
from serial import SerialTimeoutException

ok_regex = re.compile(rb"^ok N(\d+) P(\d+) B(\d+)")
temperature_regex = re.compile(rb"^(?:ok P\d+ B\d+|) T:([\d\.]+) /([\d\.]+) B:([\d\.]+) /([\d\.]+) @:0 B@:0$")
m114_regex = re.compile(rb"^X:([\-\d\.]+) Y:([\-\d\.]+) Z:([\-\d\.]+) E:([\-\d\.]+) Count X:([\-\d]+) Y:([\-\d]+) Z:([\-\d]+)$")

class CommandStatus(Enum):
    INVENTED = 0
    QUEUED = 1
    SENT = 2
    PLANNING = 3
    DONE = 4

class Command:
    def __init__(self, code, status=CommandStatus.INVENTED):
        assert ("\n" not in code)
        self._code = code
        self._status = status

    def code(self):
        return self._code

    def status(self):
        return self._status

@dataclass
class ReportedPosition:
    x: float
    y: float
    z: float
    e: float
    x_count: int
    y_count: int
    z_count: int

class PrinterConnection:
    """
    A connection to a 3D printer.

    Keeps track of sending queued commands only when the printer is ready for them.

    If I could protect the motion planner cleanly and reliably, this would also interact with motion stuff. But I currently can't, so since I don't want this file to have a sprawling scope, it doesn't attempt that.
    """
    def __init__(self, port = None, /, baud = 115200, timeout = 1, on_update = lambda: None, on_position_report = lambda p: None):
        if port is None:
            ports = [p.device for p in serial.tools.list_ports.comports()]
            port = ports[0]
        self._port = port
        self._baud = baud
        self._timeout = timeout
        self._on_update = on_update
        self._on_position_report = on_position_report

        self._receive_thread = None
        self._next_line_number = 0
        self._printer_move_planner_buffer_capacity = 63
        self._printer_unprocessed_buffer_capacity = 3
        self._printer_move_planner_buffer_availability = self._printer_move_planner_buffer_capacity
        self._printer_unprocessed_buffer_availability = self._printer_unprocessed_buffer_capacity
        self._hotend_temperature, self._hotend_target_temperature, self._bed_temperature, self._bed_target_temperature = [0]*4
        self._in_progress_commands = deque()
        self._last_position_report = None
        self._closing = False

    def __enter__(self):
        if "ED3D_IS_AUTORUN" in os.environ:
            print("Aborting because we don't allow autoruns that directly command the printer")
            sys.exit(0)
        self._serial = serial.Serial(self._port, self._baud, timeout=self._timeout)
        self._receive_thread = Thread(target=self._receive_loop, daemon=True)
        self._receive_thread.start()
        time.sleep(1)
        self.send("M110") # reset line number
        self.send("M155 S1") # report temperature every 1 second
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._closing = True
        while self._serial is not None:
            time.sleep(0.1)

    def _send_immediate(self, command: Command):
        """Send a command immediately, bypassing the queue. Caller's responsibility to not send so many commands to overload the printer's own command queue."""
        assert (self._printer_unprocessed_buffer_availability > 0)

        # Marlin implements, but does not document in its documentation, some kind of checksum approach. This is only available when you also give a line number, so I just give every line a sequential number.
        line_number = self._next_line_number
        self._next_line_number += 1

        # In lieu of documentation, I have copied this checksum code from Cura.
        checksum = functools.reduce(lambda x, y: x ^ y, map(ord, "N%d%s" % (line_number, command.code())))
        code = "N%d%s*%d\n" % (line_number, command.code(), checksum)

        # print(f"Sending to printer: {repr(code)}")
        self._serial.write(code.encode())
        command._status = CommandStatus.SENT
        self._printer_unprocessed_buffer_availability -= 1

    def send(self, command: str | Command) -> Command:
        if type(command) is str:
            command = Command(command)
        self._in_progress_commands.append(command)
        if self._printer_unprocessed_buffer_availability > 0:
            self._send_immediate(command)
        else:
            command._status = CommandStatus.QUEUED
        return command

    def unprocessed_buffer_availability(self):
        return self._printer_unprocessed_buffer_availability
    def planning_buffer_availability(self):
        return self._printer_move_planner_buffer_availability
    def unprocessed_buffer_count(self):
        return self._printer_unprocessed_buffer_capacity - self._printer_unprocessed_buffer_availability
    def planning_buffer_count(self):
        return self._printer_move_planner_buffer_capacity - self._printer_move_planner_buffer_availability
    def hotend_temperature(self):
        return self._hotend_temperature
    def hotend_target_temperature(self):
        return self._hotend_target_temperature
    def bed_temperature(self):
        return self._bed_temperature
    def bed_target_temperature(self):
        return self._bed_target_temperature

    def _receive_loop(self):
        while self._serial is not None:
            # try:
            line = self._serial.read_until(b"\n")
            if not line.endswith(b"\n"):
                # timed out
                if self._closing:
                    self._serial.close()
                    self._serial = None
                continue
            line = line[:-1]
            # except SerialTimeoutException:
            #     if self._closing:
            #         self._serial.close()
            #         self._serial = None
            #     continue

            line_understood = False

            # if line.startswith(b"echo:busy:"):
            #     self._printer_ready_for_more_commands = False

            # empty line means the printer is idle, according to Cura code
            if line == b"":
                line_understood = True

            ok_match = ok_regex.match(line)
            if ok_match:
                if ok_match[0] == line:
                    line_understood = True
                _, self._printer_move_planner_buffer_availability, self._printer_unprocessed_buffer_availability = [int(s) for s in ok_match.groups()]

                unprocessed = [p for p in self._in_progress_commands if p.status() == CommandStatus.SENT]
                for now_processed in unprocessed[:len(unprocessed)-self.unprocessed_buffer_count()]:
                    if now_processed.code().split(" ", 1)[0] in ["G0", "G1"]:
                        now_processed._status = CommandStatus.PLANNING
                    else:
                        now_processed._status = CommandStatus.DONE

                planned = [p for p in self._in_progress_commands if p.status() == CommandStatus.PLANNING]
                for now_finished in planned[:len(planned)-self.planning_buffer_count()]:
                    now_finished._status = CommandStatus.DONE

                unsent = [p for p in self._in_progress_commands if p.status() == CommandStatus.QUEUED]
                # The -1 is so that auto-sending queued commands never fills the last slot in case someone wanted to bypass the queue really urgently. Not that I have any situation where I'm particularly thinking of doing this, but if I *do* find one, I don't want something to break because it was relying on using the entire unprocessed buffer for queued commands.
                for now_sending in unsent[:self._printer_unprocessed_buffer_availability-1]:
                    self._send_immediate(now_sending)

            temperature_match = temperature_regex.match(line)
            if temperature_match:
                line_understood = True
                self._hotend_temperature, self._hotend_target_temperature, self._bed_temperature, self._bed_target_temperature = [float(s) for s in temperature_match.groups()]

            m114_match = m114_regex.match(line)
            if m114_match:
                line_understood = True
                groups = m114_match.groups()
                self._last_position_report = ReportedPosition(*[float(s) for s in groups[0:4]]+[int(s) for s in groups[4:7]])
                (self._on_position_report)(self._last_position_report)

            if not line_understood:
                print(f"received line from printer that we didn't understand: {line}")
            # print(f"received line from printer: {line}")

            self._on_update()









