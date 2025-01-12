
from pyocct_system import *

def assert_same_length(a, b, c, d):
  l0 = (a - b).length()
  l1 = (c - d).length()
  assert abs(l0 - l1) < 0.00001

def unrolled_next_triangle_point(prev_a, prev_b, unrolled_prev_a, unrolled_prev_b, new_point):
  # calculate relative position of the new point in
  # two dimensions _relative_ to the current section,
  # these dimensions being crosswise (c) and lengthwise (l).
  # Crosswise movement is simple and reflects the 3D movement, signedly;
  # but for the l dimension, _any_ non-crosswise movement in 3D
  # becomes positive lengthwise movement in 2D.
  cdir = Direction(prev_a, prev_b)
  unrolled_cdir = Direction(unrolled_prev_a, unrolled_prev_b)
  unrolled_ldir = unrolled_cdir2 @ Rotate(Up, Turns(1/4))

  # use prev_a / unrolled_prev_a as a reference point; this would yield
  # the same result if we picked prev_b / unrolled_prev_b,
  # since they differ only in c, which cancels
  d = new_point - prev_a
  c = d.dot(cdir)
  l = d.projected_perpendicular(cdir).length()
  result = unrolled_prev_a + unrolled_cdir * c + unrolled_ldir * l

  # error if I made a mistake:
  assert_same_length(prev_a, new_point, unrolled_prev_a, result)
  assert_same_length(prev_b, new_point, unrolled_prev_b, result)
  return result


# o = original, u = unrolled
class UnrolledPoint:
  def __init__(self, o, u):
    self.o = o
    self.u = u

class TriangleCandidate:
  def __init__(self, edge, new_point, was_ccw):
    self.edge = edge
    self.new_point = new_point
    self.was_ccw = was_ccw

class UnrolledEdge:
  def __init__(self, a, b):
    assert isinstance(a, UnrolledPoint)
    assert isinstance(b, UnrolledPoint)
    assert (a.o - b.o).length() > 0.000001
    self.a = a
    self.b = b
    assert_same_length(a.o, b.o, a.u, b.u)
    self.along_edge_o = Direction(self.a.o, self.b.o)
    self.along_edge_u = Direction(self.a.u, self.b.u)
    # by convention, the interior of a curve is on the ccw side, so outside is always cw
    self.outwards_from_edge_u = self.along_edge_u @ Rotate(Up, Turns(-1/4))
  
  def relative_point(self, new_point) -> UnrolledPoint:
    # calculate relative position of the new point in
    # two dimensions _relative_ to the current section,
    # these dimensions being crosswise (c) and lengthwise (l).
    # Crosswise movement is simple and reflects the 3D movement, signedly;
    # but for the l dimension, _any_ non-crosswise movement in 3D
    # becomes positive lengthwise movement in 2D.

    # use a as a reference point; this would yield
    # the same result if we picked b,
    # since they differ only in the along_edge direction, which cancels
    d = new_point - self.a.o
    alongness = d.dot(self.along_edge_o)
    perpness = d.projected_perpendicular(self.along_edge_o).length()
    return UnrolledPoint(new_point, self.a.u
              + self.along_edge_u * alongness
              + self.outwards_from_edge_u * perpness)


class UnrolledSurface:
  def __init__(self, ao, bo):
    a = UnrolledPoint(ao, Origin)
    b = UnrolledPoint(bo, Point(0,(bo-ao).length()))
    self.edges = [
      UnrolledEdge(a, b),
      UnrolledEdge(b, a),
    ]

  def unrolled_points(self):
    return [e.a.u for e in self.edges]

  def unrolled_wire(self):
    return Wire(self.unrolled_points(), loop=True)

  def unrolled_face(self):
    return Face(self.unrolled_wire())

  def extend_edge_to_triangle(self, edge, ao):
    i = self.edges.index(edge)
    a = edge.relative_point(ao)
    new_edges = [
      UnrolledEdge(edge.a, a),
      UnrolledEdge(a, edge.b)
    ]
    self.edges[i:i+1] = new_edges
    return new_edges

  def extend_edge_to_quad(self, edge, ao, bo):
    i = self.edges.index(edge)

    # If the four points weren't coplanar, these may be the wrong distance from each other. We can guarantee correct unrolling by dividing into two triangles...
    a = edge.relative_point(ao)
    b = edge.relative_point(bo)

    a_triangulated = UnrolledEdge(edge.a, b).relative_point(ao)
    b_triangulated = UnrolledEdge(a, edge.b).relative_point(bo)

    # only the pairs (a, b_triangulated) and (b, a_triangulated) are guaranteed to be valid,
    # but for non-coplanar points, they may differ. Warn if they differ by too much:
    if (a_triangulated.u - a.u).length() > 0.01*(a.u - edge.a.u).length():
      print(f"Warning: {(a_triangulated.u - a.u).length()} arbitrariness in unrolling-choice")

    new_edges = [
      UnrolledEdge(edge.a, a_triangulated),
      UnrolledEdge(a_triangulated, b),
      UnrolledEdge(b, edge.b)
    ]
    self.edges[i:i+1] = new_edges
    return new_edges


def unroll_quad_strip(sections):
  unrolled = UnrolledSurface(*sections[0])
  latest_edge = unrolled.edges[0]
  for section in sections[1:]:
    latest_edge = unrolled.extend_edge_to_quad(latest_edge, *section)[1]
  return unrolled
