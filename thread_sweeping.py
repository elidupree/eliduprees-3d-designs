from typing import Callable, Optional

from pyocct_system import *

class ScrewThreadSurface:
    def __init__(self, *, pitch: float, length: Optional[float] = None, turns: Optional[float] = None, radius_fn: Callable[[float], float], left_handed = False):
        """Generate a surface by revolving a thread profile.

        The profile is given as radius_fn, a function from ThreadPosition to "radius at that point".

        Always centered at the origin, goes up to z=length, and the crest reference point starts on the x-axis."""
        if length is None:
            length = pitch*turns
        if turns is None:
            turns = length/pitch
        self.length = length
        self.turns = turns
        self.pitch = pitch
        self.radius_fn = radius_fn
        self.left_handed = left_handed

    def generate(self, angle_samples = 120, z_max_sample_distance: Optional[float] = None):
        if z_max_sample_distance is None:
            z_max_sample_distance = self.pitch / 10
        angles = [Turns(turns) for turns in subdivisions(0,1,amount=angle_samples+1)[:-1]]
        return BSplineSurface([[Point(self.radius_fn(ThreadPosition(self, z, angle)), 0, z) @ Rotate(Up, angle) for z in subdivisions(0, self.length, max_length=z_max_sample_distance)] for angle in angles], u=BSplineDimension(periodic=True))

class ThreadPosition:
    z: float
    angle: Angle
    angle_direction: Direction
    threads_so_far: float
    threads_offset_from_last_crest: float
    threads_offset_from_nearest_crest: float
    frac_from_crest_to_trough: float
    z_offset_from_last_crest: float
    z_offset_from_nearest_crest: float
    frac_along_length: float
    # frac_from_nearest_end: float
    # z_distance_from_nearest_end: float

    def __init__(self, surface: ScrewThreadSurface, z: float, angle: Angle):
        self.z = z
        self.angle = angle
        self.angle_direction = Right @ Rotate(Up, angle)
        self.threads_so_far = z / surface.pitch
        handed_turns = angle.turns
        if surface.left_handed:
            handed_turns *= -1
        self.threads_offset_from_last_crest = (self.threads_so_far - handed_turns + 1) % 1
        self.threads_offset_from_nearest_crest = self.threads_offset_from_last_crest
        if self.threads_offset_from_last_crest > 0.5:
            self.threads_offset_from_nearest_crest -= 1
        self.frac_from_crest_to_trough = self.threads_offset_from_nearest_crest*2
        self.z_offset_from_last_crest = self.threads_offset_from_last_crest * surface.pitch
        self.z_offset_from_nearest_crest = self.threads_offset_from_nearest_crest * surface.pitch
        self.frac_along_length = self.z/surface.length
        # self.frac_from_nearest_end = min(self.frac_along_length, 1-self.frac_along_length)
        # self.z_distance_from_nearest_end = min(self.z, surface.length - self.z)

