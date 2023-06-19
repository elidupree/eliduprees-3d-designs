import math

from pyocct_system import *
initialize_pyocct_system()

from full_face_mask_definitions.headband import temple_block, headband_waves, temple_extender, forehead_band
from full_face_mask_definitions.intake import intake_wall, headband_to_intake_strut, intake_fins
from full_face_mask_definitions.shield import shield_infinitesimal, eye_lasers, unrolled_shield_wire, \
    spout_to_shield_contact_part

@run_if_changed
def mirrored_headband_parts():
    return Compound([
        temple_block,
        temple_extender,
    ])

save_STL("headband", Compound([
    mirrored_headband_parts,
    mirrored_headband_parts @ Reflect(Right),
    forehead_band,
    headband_waves,
]))

save_STL("intake", Compound([
    intake_wall,
    intake_fins,
    headband_to_intake_strut,
    spout_to_shield_contact_part,
]))

preview(shield_infinitesimal.wires(), eye_lasers, temple_block, headband_waves, temple_extender, forehead_band, intake_wall, unrolled_shield_wire, headband_to_intake_strut, intake_fins, spout_to_shield_contact_part)

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

  