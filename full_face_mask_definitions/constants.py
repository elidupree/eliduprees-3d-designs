import math
from pyocct_system import *
del Front, Back

min_wall_thickness = 0.8

# The amount of to leave between parts that are supposed to touch each other. This mainly reflects the amount of error in the 3D printing process. (My home Ender-3 makes holes smaller than they should be; for a more precise system (e.g. Shapeways) I would set it to more like 0.1.)
contact_leeway = 0.4

CPAP_outer_radius = 21.5/2
CPAP_inner_radius = CPAP_outer_radius - min_wall_thickness

# We need a few reference locations. The choice of where to put "0" is completely arbitrary in the front-back and up-down dimensions (for left-right, the natural 0 is the center of the face). Since there is no obvious reason to prefer one over the other, we yield to historical reasons, where the origin is a particular point on the forehead.

# The names "Front" and "Back" are confusing, because typically the "front of the model" means the side you are looking at, but here, if your head is oriented as it is in the mask model, you would be looking at the back of your head. So we define these instead:
TowardsFrontOfHead = Direction(0, 1, 0)
TowardsBackOfHead = Direction(0, -1, 0)

putative_chin = Point(0, -13, -125)

# The putative corner of where glasses might be, experimentally determined from someone with large glasses.
glasses_point = Point(66, 0, -10)

# The putative source of sight, used for determining where reflections will be visible.
putative_eyeball = Point(35, -15, -35)

# The location the air should be directed towards, intended to be between the nose and mouth, maybe favoring the mouth a bit.
air_target = putative_chin + vector(0, 10, 33)

neck_leeway = 20
