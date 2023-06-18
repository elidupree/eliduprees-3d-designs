import math

from full_face_mask_definitions.constants import putative_chin, TowardsFrontOfHead, putative_eyeball, TowardsBackOfHead
from full_face_mask_definitions.headband_geometry import headband_top
from full_face_mask_definitions.intake import intake_outer_solids
from full_face_mask_definitions.shield_geometry import shield_back_y, shield_surface, ShieldSample, temple_top
from pyocct_system import *

# The bottom point of the shield. Ideally, this should be further down than the invisible point – far enough down that even after cloth is put over it, the cloth is also invisible. In practice, the very center is invisible because of my nose, but the parts beside it are just barely visible as a compromise with "not bumping the bottom edge into my chest".
shield_bottom_z = putative_chin[2] - 50


@run_if_changed
def shield_bottom_peak():
    return ShieldSample(intersecting=Line(Point(0, 0, shield_bottom_z), TowardsFrontOfHead))


@run_if_changed
def shield_back_face():
    c = BSplineCurve([
        temple_top,
        temple_top + Down*60,
        temple_top + Down*125,
        shield_bottom_peak.position,
    ], BSplineDimension(degree=2))
    return Edge(c).extrude(Right*500, centered=True)


@run_if_changed
def shield_infinitesimal():
    result = Face(shield_surface)
    #result = result.intersection(HalfSpace(Point(0, shield_back_y, 0), TowardsFrontOfHead))
    #result = result.intersection(HalfSpace(Point(0, 0, headband_top), Down))
    #result = result.intersection(HalfSpace(shield_bottom_peak.position, Direction(0, 1.6, 1)))
    result = result.intersection(shield_back_face.extrude(TowardsFrontOfHead*200))
    for solid in intake_outer_solids:
        result = result.cut(solid)
    return result

# To help analyze the reflection properties of the surface, we draw sight lines – provocatively called "eye lasers" – to see the locations from which light could unpleasantly reflect off the shield into the eye.
@run_if_changed
def eye_lasers():
    lasers = []
    for x in subdivisions(-2, 2, amount=10):
        for z in subdivisions(-2, 2, amount=10):
            direction = Direction (x, 1, z)
            try:
                sample = ShieldSample(intersecting=RayIsh(putative_eyeball, direction), which=0)
            except IndexError:
                # if it doesn't hit the shield, you couldn't see in that direction anyway
                continue
            # hack - also exclude points that aren't in the cropped shield
            # maybe this should explicitly use shield_infinitesimal
            if sample.position[2] > headband_top:
                continue

            reflected_direction = direction @ Reflect(sample.normal)
            # add a laser for direct vision
            lasers.append(Wire(putative_eyeball, sample.position, sample.position + direction * 50))

            try:
                sample2 = ShieldSample(intersecting=RayIsh(sample.position + 0.1*reflected_direction, reflected_direction), which=0)
            except IndexError:
                # if it doesn't hit the shield, it wasn't a problematic reflection
                continue
            # hack - also exclude points that aren't in the cropped shield
            # maybe this should explicitly use shield_infinitesimal
            if not RayIsh(sample2.position, TowardsBackOfHead).intersections(shield_back_face.surface()).points:
                continue
            # add a laser for the problematic reflection
            lasers.append(Wire(putative_eyeball, sample.position, sample2.position, sample2.position + reflected_direction * 50))
    return Compound(lasers)