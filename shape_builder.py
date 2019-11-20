import FreeCAD
import Part
import math

class FreeCAD_shape_builder:
  def __init__(self, zigzag_depth = 2, zigzag_length_limit = None):
    if zigzag_length_limit is not None:
      discriminant = zigzag_length_limit**2 - zigzag_depth**2
      if discriminant <= 0:
        raise InputError ("unreasonable zigzag requirements")
      self.zigzag_max_split_length = math.sqrt (discriminant)*2 * 0.99
    self.zigzag_depth = zigzag_depth
    self.zigzag_length_limit = zigzag_length_limit
    self.components = []
    self.current_position = None
    self.last_start_position = None
  def vector (self, coordinates):
    return FreeCAD.Vector (*coordinates, 0)
  def add_line_impl (self, endpoints):
    segment = Part.LineSegment (*endpoints)
    if self.zigzag_length_limit is not None and segment.length() > self.zigzag_length_limit:
      splits = math.ceil(segment.length()/self.zigzag_max_split_length)
      delta = endpoints [1] - endpoints [0]
      sideways = FreeCAD.Vector (delta[1], -delta[0], 0).normalized() * self.zigzag_depth
      for split in range (splits):
        start_frac = split / splits
        end_frac = (split + 1) / splits
        mid_frac = (split + 0.5) / splits
        points = [
          endpoints[1]*start_frac + endpoints[0]*(1-start_frac),
          endpoints[1]*mid_frac + endpoints[0]*(1-mid_frac) + sideways,
          endpoints[1]*end_frac + endpoints[0]*(1-end_frac),
        ]
        #print(endpoints, points)
        assert((points[1]-points[0]).Length < self.zigzag_length_limit)
        self.add_line_impl (points[0:2])
        self.add_line_impl (points[1:3])
      return
    self.components.append (segment)
  def add_line (self,*endpoints):
    self.add_line_impl([self.vector (coordinates) for coordinates in endpoints])
  def line_to (self, coordinates):
    self.add_line (self.current_position, coordinates)
    self.current_position = coordinates
  def arc_through_to (self, through, to):
    points = (self.current_position, through, to)
    self.components.append (Part.Arc (*[self.vector (coordinates) for coordinates in points]))
    self.current_position = to
  def finish(self):
    return Part.Shape (self.components)
  def build(self, components):
    for component in components:
      component.apply (self)
    return self.finish()

class horizontal_to:
  def __init__(self, coordinate):
    self.coordinate = coordinate
  def apply(self, builder):
    builder.line_to (
      (self.coordinate, builder.current_position [1])
    )

class vertical_to:
  def __init__(self, coordinate):
    self.coordinate = coordinate
  def apply(self, builder):
    builder.line_to (
      (builder.current_position [0], self.coordinate)
    )
    
class diagonal_to:
  def __init__(self, *coordinates):
    self.coordinates = coordinates
  def apply(self, builder):
    builder.line_to (self.coordinates)
    
class arc_through_to:
  def __init__(self, through, to):
    self.through = through
    self.to = to
  def apply(self, builder):
    builder.arc_through_to (self.through, self.to)

class start_at:
  def __init__(self, *coordinates):
    self.coordinates = coordinates
  def apply(self, builder):
    builder.current_position = self.coordinates
    builder.last_start_position = self.coordinates

class close:
  def apply(self, builder):
    builder.line_to (builder.last_start_position)
