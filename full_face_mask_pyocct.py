import math

from pyocct_system import *
initialize_pyocct_system()

from full_face_mask_definitions.headband import temple_block_uncut, headband_waves, temple_extender, forehead_band
from full_face_mask_definitions.intake import intake_wall
from full_face_mask_definitions.shield import shield_infinitesimal, eye_lasers, unrolled_shield_wire

preview(shield_infinitesimal, eye_lasers, temple_block_uncut, headband_waves, temple_extender, forehead_band, intake_wall, unrolled_shield_wire)

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

  