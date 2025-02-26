import math

from pyocct_system import *
initialize_pyocct_system()

@run_if_changed
def print_on_object_test():
    guide = Vertex(Origin).extrude(Left*20, centered=True).extrude(Back*17, centered=True).extrude(Up*0.3).cut([
        Vertex(Origin).extrude(Left*20, centered=True).extrude(Back*16, centered=True).extrude(Up*0.3)
    ])

    thingy = Vertex(-9, 0, 0.4).extrude(Right*2).extrude(Back*10, centered=True).extrude(Up*5)

    test = Compound(guide, thingy)
    save_STL("print_on_object_guide", guide)
    export("print_on_object_guide.stl", "print_on_object_guide_1.stl")
    save_STL("print_on_object_thingy", thingy)
    export("print_on_object_thingy.stl", "print_on_object_thingy_1.stl")
    save_STL("print_on_object_test", test)
    export("print_on_object_test.stl", "print_on_object_test_1.stl")

    preview(guide, thingy)