import FreeCAD
import Part

class FreeCAD_shape_builder:
  def __init__(self, transform = lambda vector: vector):
    self.components = []
    self.current_position = None
    self.last_start_position = None
    self.transform = transform
  def vector (self, coordinates):
    return self.transform (FreeCAD.Vector (*coordinates, 0))
  def add_line (self,*endpoints):
    self.components.append (Part.LineSegment (*[self.vector (coordinates) for coordinates in endpoints]))
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
