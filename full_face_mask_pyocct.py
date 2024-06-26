import math

from pyocct_system import *

initialize_pyocct_system()

from full_face_mask_definitions.headband import temple_block, headband_waves, temple_extender, forehead_band, \
    top_cloth_lip, temple_knob, temple_block_uncut
from full_face_mask_definitions.intake import intake_wall, headband_to_intake_strut, intake_fins
from full_face_mask_definitions.shield import shield_infinitesimal, eye_lasers, unrolled_shield_wire, \
    spout_to_shield_contact_part
from full_face_mask_definitions.top_cloth import top_cloth
from full_face_mask_definitions.chin_cloth import chin_cloth_3d, chin_cloth_flat


@run_if_changed
def mirrored_headband_parts():
    return Compound([
        temple_extender,
        temple_knob,
    ])


save_STL("headband", Compound([
    mirrored_headband_parts,
    mirrored_headband_parts @ Reflect(Right),
    temple_block,
    temple_block_uncut @ Reflect(Right),
    forehead_band,
    headband_waves,
    top_cloth_lip,
]))

save_STL("intake", Compound([
    intake_wall,
    intake_fins,
    headband_to_intake_strut,
    spout_to_shield_contact_part,
]))

preview(shield_infinitesimal.wires(), eye_lasers, temple_block, headband_waves, temple_extender, forehead_band,
        intake_wall, unrolled_shield_wire, headband_to_intake_strut, intake_fins, spout_to_shield_contact_part,
        top_cloth, chin_cloth_3d, chin_cloth_flat,
        top_cloth_lip, temple_knob)

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
