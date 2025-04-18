import math
import re
from collections import deque
import xml.etree.ElementTree as ElementTree

from pyocct_system import *

def SVG_path_wire (text):
    things = deque(re.split("[,\s]", text))

    edges = []

    current_handler = None
    current_position = Origin
    first_position = None

    def next_number():
        return float(things.popleft())

    def next_absolute():
        return Point(next_number(), next_number(), 0)
    def next_relative():
        return current_position + Vector(next_number(), next_number(), 0)

    def M():
        nonlocal current_position
        nonlocal first_position
        a,current_position = current_position,next_point()
        if first_position is None:
            first_position = current_position
        else:
            edges.append (Edge (a,current_position))


    def H():
        nonlocal current_position
        if next_point is next_absolute:
            new = next_number()
        else:
            new = current_position[0] + next_number()

        a, current_position = current_position, Point(new, current_position [1], 0)
        edges.append(Edge (a,current_position))

    def L():
        nonlocal current_position
        a,b = current_position, next_point()
        edges.append (Edge (a,b))
        current_position = b

    def C():
        nonlocal current_position
        a,b,c,d = current_position, next_point(), next_point(), next_point()
        edges.append (Edge (BezierCurve([a,b,c,d])))
        current_position = d

    def Z():
        nonlocal current_position
        a,current_position = current_position,first_position
        edges.append(Edge (a,current_position))

    handlers = {
        "m": M,
        "h": H,
        "l": L,
        "c": C,
        "z": Z,
    }

    while things:
        if things[0].lower() in handlers:
            h = things.popleft()
            if h.isupper():
                next_point = next_absolute
            else:
                next_point = next_relative
            current_handler = handlers[h.lower()]
        else:
            current_handler()

    return Wire (edges)

def Inkscape_BSplineCurve(text):
    things = deque(re.split("[,\s]", text))
    assert(things.popleft() == "m")
    periodic = things[-1] == "z"
    if periodic:
        things.pop()
    position = Point(float(things.popleft()), float(things.popleft()), 0)
    assert(things.popleft() == "c")
    control_points = []
    # while things:
    #     print(things)
    #     position = position + vector(float(things.popleft()), float(things.popleft()))
    #     control_points.append (position)
    control_points.append (position)
    for i in range(4, len(things), 6):
        position = position + vector(float(things[i]), float(things[i+1]))
        control_points.append (position)
    if periodic and (control_points[0] - control_points[-1]).length() <= 0.001:
        control_points.pop()
    return BSplineCurve(control_points, BSplineDimension(periodic = periodic))

def load_Inkscape_BSplineCurve(filename, id):
    register_file_read(filename)
    tree = ElementTree.parse(filename)
    elem = tree.getroot().find(f".//*[@id='{id}']")
    return Inkscape_BSplineCurve(elem.attrib["{http://www.inkscape.org/namespaces/inkscape}original-d"])


