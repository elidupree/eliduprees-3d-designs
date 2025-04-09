import math

from pyocct_system import *
from gears import InvoluteGear

initialize_pyocct_system()

def example(g, t):
    return Compound(g, g @ Rotate(Up, Turns(t)) @ Translate(Right*40))

weird = InvoluteGear(num_teeth=40, pitch_radius=20, pressure_angle=Degrees(10), skip_teeth=2).shape
weird = Compound(weird.extrude(Up*5), weird.extrude(Up*5, Up*10) @ Rotate(Up, Turns(1/40)))

gears = [
    example(InvoluteGear(num_teeth=20, pitch_radius=20).shape.extrude(Up*10), 1/40),
    # InvoluteGear(num_teeth=20, pitch_radius=20, pressure_angle=Degrees(1)).shape,
    example(weird, 1/40),
]
preview([g @ Translate(Back*50*i) for i, g in enumerate(gears)])
