import math

from pyocct_system import *
from full_face_mask_definitions.constants import glasses_point, TowardsFrontOfHead, putative_chin, putative_eyeball
from full_face_mask_definitions.headband_shape import headband_curve, headband_top

del Front, Back

"""
A lot of the mask geometry centers around the shape of the face shield.

Since I make the shield from a flat sheet of clear polycarbonate, it has to be a "developable surface". In particular, we are going to make it a "generalized cone": there's a single focal point, and from any point on the shield surface, the line towards the focal point is within the surface.

Conveniently, a simple BSplineSurface can express such a shape. We describe a curve, then scale it about the focal point to get other curves in the same surface, and join them linearly to express the surface.

Since my forehead is bigger than my chin, it's efficient to put the focal point below the chin instead of above.
"""

# We select a corner where the shield surface meets the headband. We call it the "temple", because that's where it is. It's named "temple_xy" to emphasize that this is a 2D position within the Z=0 plane, rather than a 3D location.
shield_back_y = -75
temple_xy = Edge(RayIsh(Point(0, shield_back_y, 0), Right)).extrude(Up*1, centered=True).surface().intersections(headband_curve).point()

# The formal top edge of the shield is the same as the formal top edge of the headband.
temple_top = temple_xy + Up * headband_top

# We assert that the direction straight down from the temple will lie within the shield, which leaves one degree of freedom at that location. To eliminate that one degree, we explicitly define the XY-plane angle that the shield surface extends from the temple.
temple_radians = (math.tau / 4) * 0.6
temple_direction = Right @ Rotate(Up, radians=temple_radians)

# We explicitly define the angle of the shield surface in the YZ plane.
shield_focal_slope = 1.8

# We have a choice of how to define the y-position of the shield: We could define it relative to the forehead, or relative to the chin. The chin-relative position is more sensitive, so we explicitly define the amount of distance in the y dimension to put between the putative chin and the shield.
chin_leeway = 10

# The above definitions uniquely determine the focal point for the generalized cone of the shield surface; we calculate that now.
shield_focal_y = temple_xy[1] - (temple_xy[0] * temple_direction[1] / temple_direction[0])
shield_chin_peak = putative_chin + TowardsFrontOfHead * chin_leeway
dy = shield_focal_y - shield_chin_peak[1]
shield_focal_point = Point(0, shield_focal_y, shield_chin_peak[2] + dy * shield_focal_slope)


# We describe a "source curve" at the top edge of the shield, which we will project towards the focal point to describe the surface.
def project_point_to_z(z, point):
    return point.projected(
        Plane(Point(0, 0, z), Up),
        by=Direction(shield_focal_point, point)
    )


shield_source_curve_points = [
    temple_top,
    project_point_to_z(headband_top, glasses_point + vector(15, 10, 0)),
    project_point_to_z(headband_top, shield_chin_peak),
]
shield_source_curve_points = shield_source_curve_points + [v @ Reflect(Right) for v in
                                                           reversed(shield_source_curve_points[:-1])]
# Arrange the source curve from left to right.
shield_source_curve_points.reverse()


# We defined the above points to be *on* the shield surface – interpolated, rather than used as control points – and we need to enforce the angle at the beginning and end. But to make a single BSplineSurface, we will need the actual control points. So we first make an interpolated curve, then examine what control points it ended up with.
@run_if_changed
def shield_source_curve():
    return Interpolate(shield_source_curve_points,
                       tangents=[
                           Vector(temple_direction) @ Reflect(Right),
                           Vector(temple_direction) @ Reflect(Origin)
                       ])


shield_source_curve_length = shield_source_curve.length()


def project_shield_source_poles_to_z(z):
    return [pole @ Scale(
        (shield_focal_point[2] - z) / (shield_focal_point[2] - headband_top),
        center=shield_focal_point
    ) for pole in shield_source_curve.poles()]


# For the actual shield_surface variable, we make the surface extend a little further beyond the top and bottom, to avoid any issues with rounding error later.
@run_if_changed
def shield_surface():
    return BSplineSurface(
        [
            project_shield_source_poles_to_z(putative_chin[2] - 80),
            project_shield_source_poles_to_z(20),
        ],
        u=BSplineDimension(degree=1),
        v=BSplineDimension(knots=shield_source_curve.knots(), multiplicities=shield_source_curve.multiplicities())
    )


print(
    f"Shield position directly in front of chin: {shield_surface.intersections(Line(putative_chin, TowardsFrontOfHead)).point()} (should be equal to {shield_chin_peak})")


# Now that we've defined the shield surface itself, we can define a system for taking samples from it, with useful extra data like the normal to the surface and such.

class ShieldSample(SerializeAsVars):
    def __init__(self, *, parameter=None, closest=None, intersecting=None, which=None):
        if intersecting is not None:
            intersections = shield_surface.intersections(intersecting)
            closest = intersections.points[which] if which is not None else intersections.point()
        if closest is not None:
            self.shield_parameter = shield_surface.parameter(closest)
        elif parameter is not None:
            self.shield_parameter = parameter
        else:
            raise RuntimeError("didn't specify how to initialize ShieldSample")

        self.position = shield_surface.value(self.shield_parameter)
        self.normal = shield_surface.normal(self.shield_parameter)


class CurveSample(ShieldSample):
    def __init__(self, curve, *, distance=None, closest=None, y=None, z=None, which=None, intersecting=None):
        if y is not None:
            intersecting = Plane(Point(0, y, 0), Front)
        if z is not None:
            intersecting = Plane(Point(0, 0, z), Up)
        if intersecting is not None:
            intersections = curve.intersections(intersecting)
            closest = intersections.points[which] if which is not None else intersections.point()

        if distance is not None:
            self.curve_distance = distance
            self.curve_parameter = curve.parameter(distance=distance)
        elif closest is not None:
            self.curve_parameter = curve.parameter(closest=closest)
            self.curve_distance = curve.length(0, self.curve_parameter)
        else:
            raise RuntimeError("didn't specify how to initialize CurveSample")

        derivatives = curve.derivatives(self.curve_parameter)
        super().__init__(closest=derivatives.position)

        self.curve_tangent = derivatives.tangent
        self.curve_normal = derivatives.normal
        self.curve_in_surface_normal = Direction(self.curve_tangent.cross(self.normal))

        if isinstance(curve, ShieldCurveInPlane):
            self.plane_normal = curve.plane.normal(
                (0, 0))  # note: the plane is actually a BSplineSurface, so we need to give the parameters
            self.normal_in_plane = Direction(-self.normal.cross(self.plane_normal).cross(self.plane_normal))

            self.normal_in_plane_unit_height_from_shield = self.normal_in_plane / self.normal_in_plane.dot(self.normal)
            self.curve_in_surface_normal_unit_height_from_plane = self.curve_in_surface_normal / abs(
                self.curve_in_surface_normal.dot(self.plane_normal))

        # selected to approximately match XYZ when looking at the +x end of the side curve
        # self.moving_frame = Transform(self.normal, self.curve_in_surface_normal, self.curve_tangent, self.position)


def curve_samples(curve, start_distance=None, end_distance=None, **kwargs):
    if start_distance is None:
        start_distance = 0
        try:
            end_distance = curve.precomputed_length
        except AttributeError:
            end_distance = curve.length()
    return (CurveSample(curve, distance=distance) for distance in subdivisions(start_distance, end_distance, **kwargs))


# There's at least one instance where we want a *planar* curve within the shield surface, to assist with making FDM-printable objects. This gets special features!

class ShieldCurveInPlane(SerializeAsVars):
    def __init__(self, plane):
        self.plane = plane
        self.curve = shield_surface.intersections(plane).curve()
        self.precomputed_length = self.curve.length()

    def __getattr__(self, name):
        return getattr(self.curve, name)


@run_if_changed
def shield_top_curve():
    return ShieldCurveInPlane(Plane(Point(0, 0, headband_top), Up))


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

            reflected_direction = direction @ Reflect(sample.normal)
            # add a laser for direct vision
            lasers.append(Wire(putative_eyeball, sample.position, sample.position + direction * 50))

            try:
                sample2 = ShieldSample(intersecting=RayIsh(sample.position + 0.1*reflected_direction, reflected_direction), which=0)
            except IndexError:
                # if it doesn't hit the shield, it wasn't a problematic reflection
                continue
            # add a laser for the problematic reflection
            lasers.append(Wire(putative_eyeball, sample.position, sample2.position, sample2.position + reflected_direction * 50))
    return Compound(lasers)
