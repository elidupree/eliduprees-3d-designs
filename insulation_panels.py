import math

from pyocct_system import *

initialize_pyocct_system()


@run_if_changed
def hoop_prototype():
    result = Face(Circle(Axes(Origin, Up), 130/2)).cut(Face(Circle(Axes(Origin, Up), 130/2 - 4))).extrude(Up * 3)
    save_STL("hoop_prototype", result)
    preview(result)
