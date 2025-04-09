import math
from pyocct_system import *

class InvoluteGear(SerializeAsVars):
    def __init__(self, num_teeth, pitch_radius= None, base_radius = None, base_pitch = None, pressure_angle= Degrees(20), skip_teeth = 1):
        def get_unfilled():
            return [a is None for a in [pitch_radius, base_radius, pressure_angle, base_pitch]]
        unfilled = get_unfilled()
        while any(unfilled):
            if pitch_radius is None and base_radius is not None and pressure_angle is not None:
                pitch_radius = base_radius / pressure_angle.cos()
            if pitch_radius is not None and base_radius is None and pressure_angle is not None:
                base_radius = pitch_radius * pressure_angle.cos()
            if pitch_radius is not None and base_radius is not None and pressure_angle is None:
                pressure_angle = acos(base_radius/pitch_radius)
            if base_radius is None and base_pitch is not None:
                base_radius = base_pitch * num_teeth / math.tau
            if base_radius is not None and base_pitch is None:
                base_pitch = base_radius * math.tau / num_teeth
            if get_unfilled() == unfilled:
                raise RuntimeError("InvoluteGear under-constrained")
            unfilled = get_unfilled()

        self.num_teeth = num_teeth
        self.skip_teeth = skip_teeth
        self.base_pitch = base_pitch
        self.base_radius = base_radius
        self.pitch_radius = pitch_radius
        self.pressure_angle = pressure_angle
        self.diametral_pitch = num_teeth / (pitch_radius*2)
        self.addendum = 1 / self.diametral_pitch
        self.dedendum = self.addendum * 1.2
        self.outside_radius = self.pitch_radius + self.addendum
        self.root_radius = self.pitch_radius - self.dedendum

        points = [
            Point(self.root_radius, 0, 0)
        ]
        unroll_distance = 0
        pitch_point = None
        while True:
            a = unroll_distance / base_radius
            bp = Point(base_radius, 0, 0) @ Rotate(Up, Radians(a))
            v = Vector(0, -unroll_distance, 0) @ Rotate(Up, Radians(a))
            p = bp + v
            a2 = math.atan2(p[1], p[0])
            if a2/math.tau > (1/(self.num_teeth / skip_teeth)) / 4:
                break
            # i = Segment(points[-1], p).intersections(Circle(Axes(Origin, Up), self.pitch_radius))
            # if i.points():
            #     pitch_point = i.points()[0]
            if Origin.distance(p) < self.pitch_radius:
                pitch_point = p
            if points[-1].distance(p) > 0.1:
                points.append(p)
            unroll_distance += 0.1
            
        pitch_point_radians = math.atan2(pitch_point[1], pitch_point[0])
        radian_span = math.tau / (self.num_teeth / skip_teeth) / 2
        print(pitch_point_radians, radian_span)
        points = [p @ Rotate(Up, Radians(-radian_span/2 - pitch_point_radians)) for p in points]

        tooth_points = points + [p @ Mirror(Back) for p in points[::-1]]
        self.curve =  BSplineCurve(
            [p @ Rotate(Up, Turns(i / (num_teeth / skip_teeth)))
             for i in range(num_teeth // skip_teeth) for p in tooth_points],
            BSplineDimension(periodic=True, degree=2))
        shape = Face(Wire(self.curve))
        shape = shape.intersection(Face(Circle(Axes(Origin, Up), self.outside_radius)))
        self.shape = shape
        # preview(gear, Circle(Axes(Origin, Up), base_radius), Circle(Axes(Origin, Up), pitch_radius))

