
import math

from face_depthmap_loader import front_depthmap_sample_point
from pyocct_system import *

initialize_pyocct_system()

@run_if_changed
def approx_face_surface():
    """A version of the face that's an actual BSplineSurface, for display"""
    return BSplineSurface([[front_depthmap_sample_point(x,z) for z in range(-42, 31, 2)] for x in range(-64,65,2)])



"""

Modeling strategy:

We make a single, main curve of point+direction of how the shield falls away from the approximate glasses frame. This induces the surface that's infinite in one dimension and periodic in the other. Offsets of this surface are also well-defined.
"""
@run_if_changed
def