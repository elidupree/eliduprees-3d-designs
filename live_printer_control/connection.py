import functools
import re
import time
from collections import deque
from enum import Enum
from threading import Thread

import serial
from serial import SerialTimeoutException

ok_regex = re.compile(rb"^ok P(\d+) B(\d+)")
temperature_regex = re.compile(rb"^(?:ok P\d+ B\d+|) T:([\d\.]+) /([\d\.]+) B:([\d\.]+) /([\d\.]+) @:0 B@:0$")

class CommandStatus(Enum):
    INVENTED = 0
    QUEUED = 1
    SENT = 2
    PLANNING = 3
    DONE = 4

class Command:
    def __init__(self, code, status=CommandStatus.INVENTED):
        self._code = code
        self._status = status

    def code(self):
        return self._code

    def status(self):
        return self._status

class PrinterConnection:
    """
    A connection to a 3D printer.

    Keeps track of sending queued commands only when the printer is ready for them.

    If I could protect the motion planner cleanly and reliably, this would also interact with motion stuff. But I currently can't, so since I don't want this file to have a sprawling scope, it doesn't attempt that.
    """
    def __init__(self, port = None, /, baud = 115200, timeout = 1, on_):
        if port is None:
            ports = [p.device for p in serial.tools.list_ports.comports()]
            port = ports[0]
        self._port = port
        self._baud = baud
        self._timeout = timeout
        self._receive_thread = None
        self._next_line_number = 0
        self._printer_move_planner_buffer_capacity = 15
        self._printer_unprocessed_buffer_capacity = 3
        self._hotend_temperature, self._hotend_target_temperature, self._bed_temperature, self._bed_target_temperature = [0]*4
        self._in_progress_commands = deque()

    def __enter__(self):
        self._serial = serial.Serial(self._port, self._baud, timeout=1)
        self._receive_thread = Thread(target=self._receive_loop, daemon=True)
        time.sleep(1)
        # self.send_immediate("M110") # reset line number?? Cura claims this is sometimes needed, but the documentation says this command would only report the last line number, not set it
        self.send("M155 S1") # report temperature every 1 second

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._serial.close()
        self._serial = None

    def _send_immediate(self, command: Command):
        """Send a command immediately, bypassing the queue. Caller's responsibility to not send so many commands to overload the printer's own command queue."""
        assert ("\n" not in command.code())
        assert (self._printer_unprocessed_buffer_availability > 0)

        # Marlin implements, but does not document in its documentation, some kind of checksum approach. This is only available when you also give a line number, so I just give every line a sequential number.
        line_number = self._next_line_number
        self._next_line_number += 1

        # In lieu of documentation, I have copied this checksum code from Cura.
        checksum = functools.reduce(lambda x, y: x ^ y, map(ord, "N%d%s" % (line_number, command.code())))
        code = "N%d%s*%d\n" % (line_number, command, checksum)

        self._serial.write(code.encode())
        self._printer_unprocessed_buffer_availability -= 1

    def send(self, command: str | Command) -> SentCommand:
        if type(command) is str:
            command = Command(command)
        if self._printer_unprocessed_buffer_availability > 0:
            self._send_immediate(command)
            status = SentCommandStatus.SENT
        else:
            self._command_queue.put(command)
            status = SentCommandStatus.QUEUED
        sent_command = SentCommand(command, status)
        self._in_progress_commands.append(sent_command)
        return sent_command

    def unprocessed_buffer_availability(self):
        return self._printer_unprocessed_buffer_availability
    def planning_buffer_availability(self):
        return self._printer_move_planner_buffer_availability
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
            try:
                line = self._serial.readline()
            except SerialTimeoutException:
                continue

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
                planner_buffer, unprocessed_buffer = [int(s) for s in ok_match.groups()]
                unprocessed_change = self._printer_unprocessed_buffer_availability - unprocessed_buffer
                planner_change = self._printer_move_planner_buffer_availability - planner_buffer
                self._printer_move_planner_buffer_availability, self._printer_unprocessed_buffer_availability = planner_buffer, unprocessed_buffer

                unprocessed = [p for p in self._in_progress_commands if p.status() == SentCommandStatus.SENT]
                for now_processed in unprocessed[:unprocessed_change]:
                    if now_processed.command().split(" ", 1)[0] in ["G0", "G1"]:
                        now_processed._status = SentCommandStatus.PLANNING
                    else:
                        now_processed._status = SentCommandStatus.DONE

                planned = [p for p in self._in_progress_commands if p.status() == SentCommandStatus.PLANNING]
                for now_finished in planned[:planner_change]:
                    now_finished._status = SentCommandStatus.DONE

                unsent = [p for p in self._in_progress_commands if p.status() == SentCommandStatus.QUEUED]
                for now_sending in unsent[:self._printer_unprocessed_buffer_availability]
                while self._printer_unprocessed_buffer_availability > 0 and not self._command_queue.empty():
                    self._send_immediate(self._command_queue.get())

            temperature_match = temperature_regex.match(line)
            if temperature_match:
                line_understood = True
                self._hotend_temperature, self._hotend_target_temperature, self._bed_temperature, self._bed_target_temperature = [float(s) for s in temperature_regex.groups()]

            if not line_understood:
                print(f"received line from printer that we didn't understand: {line}")









