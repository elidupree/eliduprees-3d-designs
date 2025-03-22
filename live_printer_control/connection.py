import functools
import os
import re
import sys
import time
from collections import deque
from dataclasses import dataclass
from enum import Enum
from threading import Thread, Event, RLock
from typing import Callable, Optional, List, Dict

import serial
import serial.tools.list_ports
from serial import SerialTimeoutException

ok_regex = re.compile(rb"^ok N(\d+) P(\d+) B(\d+)")
temperature_regex = re.compile(rb"^(?:ok P\d+ B\d+|) ?T:([\d\.]+) /([\d\.]+) B:([\d\.]+) /([\d\.]+) @:0 B@:0$")
m114_regex = re.compile(rb"^X:([\-\d\.]+) Y:([\-\d\.]+) Z:([\-\d\.]+) E:([\-\d\.]+) Count X:([\-\d]+) Y:([\-\d]+) Z:([\-\d]+)$")


class CommandStatus(Enum):
    INVENTED = 0
    QUEUED = 1
    SENT = 2
    PLANNING = 3
    CONSUMED = 4


class Command:
    def __init__(self, code, status=CommandStatus.INVENTED):
        assert ("\n" not in code)
        self._code = code
        self._status = status
        self._line_number = None

    def code(self):
        return self._code

    def status(self):
        return self._status

    def line_number(self):
        return self._line_number


@dataclass(frozen=True)
class PositionReport:
    x: float
    y: float
    z: float
    e: float
    x_count: int
    y_count: int
    z_count: int

@dataclass(frozen=True)
class TemperatureReport:
    hotend: float
    hotend_target: float
    bed: float
    bed_target: float


managed_settings = {
    "M201": "XYZE",
    "M204": "PRT",
    "M205": "BESTJ",
}

KnownSingleCommandSettings = Dict[str, float]
KnownMultipleCommandSettings = Dict[str, Dict[str, float]]


class PrinterConnection:
    """
    A connection to a 3D printer.

    Keeps track of sending queued commands only when the printer is ready for them.

    If I could protect the motion planner cleanly and reliably, this would also interact with motion stuff. But I currently can't, so since I don't want this file to have a sprawling scope, it doesn't attempt that.
    """
    _port: str
    _baud: int = 115200
    _timeout: float = 1
    _on_update: Callable[[], None] = lambda: None
    _on_position_report: Callable[[PositionReport], None] = lambda p: None
    _printer_move_planner_buffer_capacity: int = 63
    _printer_unprocessed_buffer_capacity: int = 3

    _receive_thread: Optional[Thread] = None
    _lock: RLock

    _known_settings_values: KnownMultipleCommandSettings

    _next_line_number: int
    _last_okayed_line_number: Optional[int] = None
    _printer_move_planner_buffer_availability: int
    _printer_unprocessed_buffer_availability: int
    _in_process_commands: List[Command]
    _last_temperature_report: Optional[TemperatureReport] = None
    _last_position_report: Optional[TemperatureReport] = None
    _outstanding_settings_request: Optional[Command] = None
    _closing: bool = False
    _settings_known_event: Event
    _debug: bool

    def __init__(self, port: str = None, /, baud: int = 115200, timeout: float = 1, on_update: Callable[[], None] = lambda: None, on_position_report: Callable[[PositionReport], None] = lambda p: None, debug: bool = False):
        if port is None:
            ports = [p.device for p in serial.tools.list_ports.comports()]
            port = ports[0]
        self._port = port
        self._baud = baud
        self._timeout = timeout
        self._on_update = on_update
        self._on_position_report = on_position_report
        self._debug = debug

        self._lock = RLock()

        self._next_line_number = 0
        self._printer_move_planner_buffer_availability = self._printer_move_planner_buffer_capacity
        self._printer_unprocessed_buffer_availability = self._printer_unprocessed_buffer_capacity
        self._in_progress_commands = []
        self._known_settings_values = {id:{} for id in managed_settings.keys()}
        self._settings_known_event = Event()

    def __enter__(self):
        if "ED3D_IS_AUTORUN" in os.environ:
            print("Aborting because we don't allow autoruns that directly command the printer")
            sys.exit(0)
        with self._lock:
            self._serial = serial.Serial(self._port, self._baud, timeout=self._timeout)
            self._receive_thread = Thread(target=self._receive_loop, daemon=True)
            self._receive_thread.start()
            time.sleep(1)
            self.send("M110") # reset line number
            self._outstanding_settings_request = self.send("M503") # report settings
            self.send("M155 S1") # report temperature every 1 second
        self._settings_known_event.wait()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._closing = True
        while self._serial is not None:
            time.sleep(0.1)

    def _send_immediate(self, command: Command):
        """Send a command immediately, bypassing the queue. Caller's responsibility to not send so many commands to overload the printer's own command queue."""
        assert (self._printer_unprocessed_buffer_availability > 0)

        with self._lock:
            # Marlin implements, but does not document in its documentation, some kind of checksum approach. This is only available when you also give a line number, so I just give every line a sequential number.
            command._line_number = self._next_line_number
            self._next_line_number += 1

            # In lieu of documentation, I have copied this checksum code from Cura.
            checksum = functools.reduce(lambda x, y: x ^ y, map(ord, "N%d%s" % (command.line_number(), command.code())))
            code = "N%d%s*%d\n" % (command.line_number(), command.code(), checksum)

            if self._debug:
              print(f"Sending to printer: {repr(code)}")
            self._serial.write(code.encode())
            command._status = CommandStatus.SENT
            self._printer_unprocessed_buffer_availability -= 1

    def send(self, command: str | Command) -> Command:
        if type(command) is str:
            command = Command(command)
        with self._lock:
            self._in_progress_commands.append(command)
            if self._printer_unprocessed_buffer_availability > 0:
                self._send_immediate(command)
            else:
                command._status = CommandStatus.QUEUED
        return command

    def printer_settings(self):
        assert (self._settings_known_event.is_set()), "caller's responsibility to wait for printer settings to be known before messing with them (waiting here would risk deadlocks). we normally always wait on __enter__"
        with self._lock:
            return self._known_settings_values.copy()

    def update_printer_settings(self, values: KnownMultipleCommandSettings):
        with self._lock:
            for cmd, values2 in values.items():
                self.update_printer_setting(cmd, values2)

    def update_printer_setting(self, cmd: str, values: KnownSingleCommandSettings):
        assert (self._settings_known_event.is_set()), "caller's responsibility to wait for printer settings to be known before messing with them (waiting here would risk deadlocks). we normally always wait on __enter__"
        with self._lock:
            known = self._known_settings_values[cmd]
            changed = []
            for param, value in values.items():
                if param not in known:
                    raise RuntimeError(f"Tried to update setting `{cmd} {param}`, which isn't known (known settings are {self._known_settings_values})")
                # the settings we're managing are at a resolution of 0.01, so there's no point changing them at finer increments, but we do want to be working with regular floats in the code, soooo
                old = f"{known[param]:.2f}"
                new = f"{value:.2f}"
                if new != old:
                    changed.append(f"{param}{new}")
                    known[param] = value

            if changed:
                self.send(" ".join([cmd] + changed))

    def unprocessed_buffer_availability(self):
        return self._printer_unprocessed_buffer_availability
    def planning_buffer_availability(self):
        return self._printer_move_planner_buffer_availability
    def unprocessed_buffer_count(self):
        return self._printer_unprocessed_buffer_capacity - self._printer_unprocessed_buffer_availability
    def planning_buffer_count(self):
        return self._printer_move_planner_buffer_capacity - self._printer_move_planner_buffer_availability

    def last_temperature_report(self) -> TemperatureReport:
        return self._last_temperature_report
    def last_position_report(self) -> PositionReport:
        return self._last_position_report


    # def set_on_update(self, on_update: Callable[[], None]):
    #     self._on_update = on_update
    #
    # def set_on_position_report(self, on_position_report: Callable[[PositionReport], None]):
    #     self._on_position_report = on_position_report

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
            if self._debug:
                print(f"received line from printer: {line}")
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
                with self._lock:
                    self._last_okayed_line_number, p, b = [int(s) for s in ok_match.groups()]

                    # self._printer_move_planner_buffer_availability = , self._printer_unprocessed_buffer_availability

                    for command in self._in_progress_commands:
                        if command.status() == CommandStatus.SENT and command.line_number() < self._last_okayed_line_number:
                            if command.code().split(" ", 1)[0] in ["G0", "G1"]:
                                command._status = CommandStatus.PLANNING
                            else:
                                command._status = CommandStatus.CONSUMED

                    sent_but_unacknowledged = [p for p in self._in_progress_commands if p.status() == CommandStatus.SENT]
                    # Sending can race with okaying, so we don't know whether the free slots listed in `b` are slated to be consumed by what we've sent since then. Conservatively assume that they all are (well, as many as could possibly be).
                    self._printer_unprocessed_buffer_availability = max(0, b - len(sent_but_unacknowledged))

                    # putting things in and out of planning is all the printer's job, so this part won't race with *us*.
                    self._printer_move_planner_buffer_availability = p
                    planned = [p for p in self._in_progress_commands if p.status() == CommandStatus.PLANNING]
                    for now_finished in planned[:len(planned)-self.planning_buffer_count()]:
                        now_finished._status = CommandStatus.CONSUMED

                    self._in_progress_commands = [c for c in self._in_progress_commands if c.status() != CommandStatus.CONSUMED]
                    if self._outstanding_settings_request is not None and self._last_okayed_line_number > self._outstanding_settings_request.line_number():
                        self._outstanding_settings_request = None
                        print("Done receiving settings from printer")
                        self._settings_known_event.set()

                    unsent = [p for p in self._in_progress_commands if p.status() == CommandStatus.QUEUED]
                    # The -1 is so that auto-sending queued commands never fills the last slot in case someone wanted to bypass the queue really urgently. Not that I have any situation where I'm particularly thinking of doing this, but if I *do* find one, I don't want something to break because it was relying on using the entire unprocessed buffer for queued commands.
                    if self._printer_unprocessed_buffer_availability > 0:
                        for now_sending in unsent[:self._printer_unprocessed_buffer_availability-1]:
                            self._send_immediate(now_sending)

            temperature_match = temperature_regex.match(line)
            if temperature_match:
                line_understood = True
                with self._lock:
                    self._last_temperature_report = TemperatureReport(*[float(s) for s in temperature_match.groups()])

            m114_match = m114_regex.match(line)
            if m114_match:
                line_understood = True
                groups = m114_match.groups()
                with self._lock:
                    self._last_position_report = PositionReport(*[float(s) for s in groups[0:4]] + [int(s) for s in groups[4:7]])
                    self._on_position_report(self._last_position_report)

            # when the printer has OK'd the previous command, it's about to send the data for the next command
            with self._lock:
                if self._outstanding_settings_request is not None and self._last_okayed_line_number is not None and self._outstanding_settings_request.line_number() == self._last_okayed_line_number + 1:
                    # explicitly ignore un-handled settings reports
                    line_understood = True
                    data_prefix = b"echo:  "
                    if line.startswith(data_prefix):
                        parts = line[len(data_prefix):].decode().split(" ")
                        cmd = parts[0]
                        if cmd in managed_settings:
                            params = managed_settings[cmd]
                            for part in parts[1:]:
                                param = part[0]
                                assert(param in params)
                                self._known_settings_values[cmd][param] = float(part[1:])

            if not line_understood:
                print(f"received line from printer that we didn't understand: {line}")

            self._on_update()









