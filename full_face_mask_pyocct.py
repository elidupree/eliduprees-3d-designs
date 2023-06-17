import math

from pyocct_system import *
initialize_pyocct_system()

from full_face_mask_definitions.shield_shape import eye_lasers, shield_surface

preview(shield_surface, eye_lasers)

# def runfile(filepath):
#   globals()["__file__"] = filepath
#   with open(filepath, 'rb') as file:
#     exec(compile(file.read(), filepath, 'exec'), globals())
#
#
# runfile("full_face_mask_pyocct_old/setup.py")
# runfile("full_face_mask_pyocct_old/intake.py")
# runfile("full_face_mask_pyocct_old/frame.py")
# runfile("full_face_mask_pyocct_old/flat_pieces.py")
# runfile("full_face_mask_pyocct_old/assembly.py")

  