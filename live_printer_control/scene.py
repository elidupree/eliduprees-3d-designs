from abc import ABC, abstractmethod
from dataclasses import dataclass
import threading
from threading import Thread
from typing import List, Optional
import pygame
from pygame.joystick import Joystick

from live_printer_control.connection import PositionReport, PrinterConnection, KnownMultipleCommandSettings


class Scene(ABC):
    def enter(self, manager: "SceneManager"):
        pass

    def exit(self, manager: "SceneManager"):
        pass

    def on_update(self, manager: "SceneManager"):
        pass

    def on_position_report(self, manager: "SceneManager", position: PositionReport):
        pass

    def on_pygame_event(self, manager: "SceneManager", event: pygame.event.Event):
        pass

    def needs_pygame_events(self):
        return type(self).on_pygame_event != Scene.on_pygame_event

    def run(self, *args, **kwargs):
        SceneManager(self, *args, **kwargs).run()


@dataclass
class ManagedScene:
    scene: Scene
    outer_settings: KnownMultipleCommandSettings
    running: bool


class SceneManager(PrinterConnection):
    _scene_stack: List[ManagedScene]
    _pygame_event_loop_thread: Optional[Thread] = None
    _joysticks: List[Joystick]

    def __init__(self, initial_scene: Scene, *args, **kwargs):
        super().__init__(*args, on_update=self._on_update, on_position_report=self._on_position_report, **kwargs)
        self._scene_stack = []
        self._exit_event = threading.Event()
        self._pygame_needed_event = threading.Event()
        self._initial_scene = initial_scene
        self._joysticks = []

    def _on_update(self):
        with self._lock:
            if self._scene_stack:
                self._scene_stack[-1].scene.on_update(self)

    def _on_position_report(self, position: PositionReport):
        with self._lock:
            if self._scene_stack:
                self._scene_stack[-1].scene.on_position_report(self, position)

    def __enter__(self):
        super().__enter__()
        with self._lock:
            self.push_scene(self._initial_scene)

    def push_scene(self, scene: Scene):
        with self._lock:
            old_settings = self.printer_settings()
            if scene.needs_pygame_events():
                self._needs_pygame()
            else:
                self._pygame_needed_event.clear()
            managed_scene = ManagedScene(scene, old_settings, False)
            self._scene_stack.append(managed_scene)
            scene.enter(self)
            managed_scene.running = True

    def pop_scene(self):
        with self._lock:
            popped = self._scene_stack.pop()
            popped.running = False
            popped.scene.exit(self)
            self.update_printer_settings(popped.outer_settings)
            if self._scene_stack:
                if self._scene_stack[-1].scene.needs_pygame_events():
                    self._pygame_needed_event.set()
                else:
                    self._pygame_needed_event.clear()
            else:
                self._pygame_needed_event.clear()
                self.exit_event.set()

    def wait_until_done(self):
        self._exit_event.wait()

    def run(self):
        with self:
            self.wait_until_done()

    def _needs_pygame(self):
        with self._lock:
            if self._pygame_event_loop_thread is None:
                self._pygame_event_loop_thread = Thread(target=self._pygame_event_loop, daemon=True)
                self._pygame_event_loop_thread.start()
            self._pygame_needed_event.set()

    def _pygame_event_loop(self):
        pygame.init()
        pygame.joystick.init()
        while not self._exit_event.is_set():
            self._pygame_needed_event.wait()
            event = pygame.event.wait()
            with self._lock:
                if event.type == pygame.JOYDEVICEADDED:
                    joystick = pygame.joystick.Joystick(event.device_index)
                    self._joysticks.append(joystick)
                    print(f"added joystick with {joystick.get_numbuttons()} buttons and {joystick.get_numaxes()} axes")
                # print(event)
                if self._scene_stack:
                    top = self._scene_stack[-1]
                    if top.running:
                        top.scene.on_pygame_event(self, event)
