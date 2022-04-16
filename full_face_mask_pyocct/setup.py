########################################################################
########  Constants  #######
########################################################################
  
min_wall_thickness = 0.8
stiffer_wall_thickness = 1.1
shield_glue_face_width = 6
elastic_holder_depth = 10
CPAP_outer_radius = 21.5/2
CPAP_inner_radius = CPAP_outer_radius - min_wall_thickness
CPAP_hose_helix_outer_radius = 22/2
shield_thickness = 0.5
headband_thickness = min_wall_thickness
headband_width = 8
overhead_strap_width = headband_width
headband_cut_radius = 25
cloth_with_elastic_space = 3
forehead_point = Origin
headphones_front = forehead_point[1]-75
#side_plate_width = max(min_wall_thickness + shield_glue_face_width, elastic_holder_depth)
#shield_back = headphones_front + side_plate_width - shield_glue_face_width
shield_back = headphones_front #+ min_wall_thickness
back_edge = forehead_point[1] - 96
putative_chin = forehead_point + vector (0, -13, -125)

# The amount of distance in the y dimension to put between the putative chin and the shield
chin_leeway = 10

# The bottom edge of the shield. Ideally, this should be further down than the invisible point – far enough down that even after cloth is put over it, the cloth is also invisible.
rim_bottom_z = putative_chin[2] - 36 

# The putative corner of where glasses might be, experimentally determined from someone with large glasses.
glasses_point = forehead_point + vector (66, 0, -10)

# The putative source of sight, used for determining where reflections will be visible.
putative_eyeball = forehead_point + vector (35, -15, -35)

# The location the air should be directed towards, intended to be just under the nose.
air_target = putative_chin + vector(0, 10, 40)

# Contact leeway mainly reflects the amount of error in the 3D printing process.
# My home Ender-3 makes holes smaller than they should be. Also, we are generally gluing
# stuff into the holes, so we want a little space for glue.
# For a more precise system (e.g. Shapeways) I would set it to more like 0.1
contact_leeway = 0.4

# The corner where the shield surface meets the headband. This is not guaranteed to be placed exactly on the headband curve.
temple = Point (77, shield_back, 0)

# The angle (in the XY plane) that the shield surface extends from the temple.
temple_radians = (math.tau/4) * 0.6
temple_direction = Right@Rotate (Up, radians = temple_radians)

# The angle of the shield surface in the YZ plane.
shield_focal_slope = 1.8

# The thickness of the flat-ish part of the air passage at its thickest point (this may not be exact because we make it conform to the shield a bit)
intake_flat_air_thickness_base = 12

# The length, approximately along the side curve, of the exterior of the intake wall (The actual width from the perspective of the moving air will be somewhat shorter than this, because the opening is angled)
intake_flat_width = 56

# The width of the opening of the triangular corner the elastic should nestle into
elastic_corner_opening_width = 4

# The width of the concave point (avoid leaving an air gap by either making it too pointy, so the cloth doesn't go all the way to the point, or too loose, so the cloth doesn't fill it)
elastic_corner_point_width = 2

# the thickness of the intake support in the direction normal to the shield
intake_support_thickness = 4

intake_middle_y = -50
intake_middle_z = -100


lots = 500

# Estimated minimum and maximum sizes of real people's heads (currently unused, I think)
min_head_circumference = 500
max_head_circumference = 650

# add significant leeway to accommodate larger necks, reduce the chance of yanking it off the rim
neck_offset = 20
neck_y = shield_back - neck_offset


headband_top = shield_glue_face_width + min_wall_thickness
headband_bottom= headband_top - headband_width

########################################################################
########  Generalized cone definitions  #######
########################################################################


# The above constants uniquely determine a focal point for
# the generalized cone of the shield surface; we calculate that now
shield_focal_y = temple[1] - (temple[0] * temple_direction[1] / temple_direction[0])

shield_chin_peak = putative_chin + Back*chin_leeway
shield_focal_point = Point (0, shield_focal_y, shield_chin_peak[2] + (shield_focal_y - shield_chin_peak[1]) * shield_focal_slope)


# For historical reasons, the top edge of the shield
# does not have z-coordinate 0, but headband_top.
# We describe a "source curve" at the top edge of the shield,
# which is projected towards the focal point to describe the surface.
above_temple = temple + vector (0, 0, headband_top)
def projected_to_top (point):
  return point.projected (
    Plane (above_temple, Up),
    by = Direction (shield_focal_point, point)
  )

shield_source_curve_points = [
  above_temple,
  projected_to_top (glasses_point + vector (15, 10, 0)),
  projected_to_top (shield_chin_peak),
]

shield_source_curve_points = shield_source_curve_points + [v@Reflect (Right) for v in reversed (shield_source_curve_points[:-1])]
shield_source_curve_points.reverse()
save ("shield_source_curve", Interpolate (shield_source_curve_points, tangents = [Vector (temple_direction)@Reflect (Right), Vector (temple_direction)@Reflect (Origin)]))


shield_source_curve_length = shield_source_curve.length()




def scaled_shield_source_curve(z):
  return [pole@Scale (
    (shield_focal_point [2]-z)/shield_focal_point [2],
    center = shield_focal_point
  ) for pole in shield_source_curve.poles()]

save ("shield_surface", BSplineSurface (
  [
    scaled_shield_source_curve (rim_bottom_z - 5),
    scaled_shield_source_curve (20),
  ],
  u = BSplineDimension (degree = 1),
  v = BSplineDimension (knots = shield_source_curve.knots(), multiplicities = shield_source_curve.multiplicities())
))
    
save ("shield_source_points", Compound ([Vertex (point) for point in shield_source_curve_points]))

print (f"Shield position directly in front of chin: {shield_surface.intersections (Line(putative_chin, Back)).point()} (should be equal to {shield_chin_peak})")

# Now that we've defined the shield surface itself, we can define a system for taking samples from it, with useful extra date of like the normal to the surface and such

class ShieldSample(SerializeAsVars):
  def __init__(self, *, parameter = None, closest = None, intersecting = None, which = None):
    if intersecting is not None:
      intersections = shield_surface.intersections (intersecting)
      closest = intersections.points [which] if which is not None else intersections.point()
    if closest is not None:
      self.shield_parameter = shield_surface.parameter(closest)
    elif parameter is not None:
      self.shield_parameter = parameter
    else:
      raise RuntimeError ("didn't specify how to initialize ShieldSample")
    
    self.position = shield_surface.value(self.shield_parameter)
    self.normal = shield_surface.normal(self.shield_parameter)


class CurveSample (ShieldSample):
  def __init__(self, curve, *, distance = None, closest = None, y = None, z = None, which = None, intersecting = None):
    if y is not None:
      intersecting = Plane (Point(0,y,0), Front)
    if z is not None:
      intersecting = Plane (Point(0,0,z), Up)
    if intersecting is not None:
      intersections = curve.intersections (intersecting)
      closest = intersections.points [which] if which is not None else intersections.point()
    
    if distance is not None:
      self.curve_distance = distance
      self.curve_parameter = curve.parameter(distance = distance)
    elif closest is not None:
      self.curve_parameter = curve.parameter(closest = closest)
      self.curve_distance = curve.length(0, self.curve_parameter)
    else:
      raise RuntimeError ("didn't specify how to initialize CurveSample")
    
    derivatives = curve.derivatives(self.curve_parameter)
    super().__init__(closest = derivatives.position)
    
    self.curve_tangent = derivatives.tangent
    self.curve_normal = derivatives.normal
    self.curve_in_surface_normal = Direction (self.curve_tangent.cross (self.normal))
    
    if isinstance(curve, ShieldCurveInPlane):
      self.plane_normal = curve.plane.normal((0,0)) # note: the plane is actually a BSplineSurface, so we need to give the parameters
      self.normal_in_plane = Direction (-self.normal.cross(self.plane_normal).cross(self.plane_normal))
      
      self.normal_in_plane_unit_height_from_shield = self.normal_in_plane/self.normal_in_plane.dot(self.normal)
      self.curve_in_surface_normal_unit_height_from_plane = self.curve_in_surface_normal/abs (self.curve_in_surface_normal.dot(self.plane_normal))
    
    # selected to approximately match XYZ when looking at the +x end of the side curve
    # self.moving_frame = Transform(self.normal, self.curve_in_surface_normal, self.curve_tangent, self.position)


def curve_samples(curve, start_distance = None, end_distance = None, **kwargs):
  if start_distance is None:
    start_distance = 0
    try:
      end_distance = curve.precomputed_length
    except AttributeError:
      end_distance = curve.length()
  return (CurveSample(curve, distance=distance) for distance in subdivisions(start_distance, end_distance, **kwargs))



shield_bottom_peak = ShieldSample(intersecting = Line(Point(0,0,rim_bottom_z), Back))


# There's at least one instance where we want a *planar* curve within the shield surface, to assist with making FDM-printable objects. This gets special features!

class ShieldCurveInPlane(SerializeAsVars):
  def __init__(self, plane):
    self.plane = plane
    self.curve = shield_surface.intersections (plane).curve()
    self.precomputed_length = self.curve.length()
    
  def __getattr__(self, name):
    return getattr(self.curve, name)



@run_if_changed
def make_shield_top_curve():
  save ("shield_top_curve", ShieldCurveInPlane(Plane(Point (0, 0, headband_top), Up)))
  
@run_if_changed
def make_shield_cross_sections():
  shield_top_full_wire = Wire (Edge (shield_top_curve.curve), Edge (shield_top_curve.EndPoint(), shield_top_curve.StartPoint()))
  shield_region = HalfSpace (Point (0, shield_back, 0), Back)
  shield_cross_section = Face (shield_top_full_wire)
  shield_cross_sections = []
  for offset_distance in (20.0*x for x in range(10)):
    offset_fraction = offset_distance / -shield_focal_point[2]
    full_section = shield_cross_section@Scale (1.0 - offset_fraction)@Translate (Vector(Origin,shield_focal_point)*offset_fraction)
    shield_cross_sections.append(Intersection(full_section, shield_region))
    
  save ("shield_cross_sections", Compound (shield_cross_sections))

  
  

save ("glasses_vertex", Vertex (glasses_point))
diff = Direction (glasses_point - shield_focal_point)
save ("glasses_edge", Edge (glasses_point + diff*180, glasses_point - diff*180))


########################################################################
########  Eye lasers  #######
########################################################################


def eye_laser(direction):
  try: 
    sample = ShieldSample(intersecting = TrimmedCurve(Line (putative_eyeball, direction), 0, lots), which = 0)
    further_direction = direction@Reflect (sample.normal)
    return Wire (putative_eyeball, sample.position, sample.position + further_direction*200)
  except IndexError:
    return Wire (putative_eyeball, putative_eyeball + direction*200)
    
@run_if_changed
def make_eye_lasers():
  save ("eye_lasers", Compound ([
    eye_laser(Direction (x, 1, z))
    for x in subdivisions (-2, 2, amount = 10)
    for z in subdivisions (-2, 2, amount = 10)
  ]))
  
  