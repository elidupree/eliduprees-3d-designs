import math

from pyocct_system import *
initialize_system (globals())

def runfile(filepath):
  globals()["__file__"] = filepath
  with open(filepath, 'rb') as file:
    exec(compile(file.read(), filepath, 'exec'), globals())


runfile("full_face_mask_pyocct/setup.py")
runfile("full_face_mask_pyocct/intake.py")
runfile("full_face_mask_pyocct/frame.py")
runfile("full_face_mask_pyocct/flat_pieces.py")
runfile("full_face_mask_pyocct/assembly.py")

  