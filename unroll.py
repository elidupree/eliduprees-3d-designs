
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


def unroll(sections):
  """Takes a list of pairs of points in 3D space, describing a ruled surface
  (each pair being a 1D cross-section of the 2D surface),
  and returns a list of pairs of points in the XY plane,
  describing the 1D cross-sections of a flat surface that can be rolled
  into the 3D surface."""

  unrolled_sections = []
  previous = None
  for a3,b3 in pairs:
    if previous is None:
      unrolled_sections.append([Point(0,0), Point(0,(b3 - a3).length())])
    else:
      pa3, pb3 = previous
      pa2, pb2 = unrolled_sections[-1]

      a2 = unrolled_next_triangle_point(pa3, pb3, pa2, pb2, a3)
      b2 = unrolled_next_triangle_point(pa3, pb3, pa2, pb2, b3)

      # ...however, if the four points weren't coplanar, these may be the wrong distance from each other. We can guarantee correct unrolling by dividing into two triangles...
      a2_triangulated = unrolled_next_triangle_point(pa3, b3, pa2, b2, a3)
      b2_triangulated = unrolled_next_triangle_point(a3, pb3, a2, pb2, b3)

      # only the pairs (a2, b2_triangulated) and (b2, a2_triangulated) are guaranteed to be valid,
      # but for non-coplanar points, they may differ. Warn if they differ by too much:
      if (a2_triangulated - a2).length() > 0.01*(a2 - pa2).length():
        print("Warning: arbitrariness in unrolling-choice")
      
      # and error if I made a mistake:
      assert_same_length(pa3, a3, pa2, a2)
      assert_same_length(pa3, a3, pa2, a2_triangulated)
      assert_same_length(pb3, b3, pb2, b2)
      assert_same_length(pb3, b3, pb2, b2_triangulated)
      assert_same_length(a3, b3, a2_triangulated, b2)
      assert_same_length(a3, b3, a2, b2_triangulated)
      
      unrolled_sections.append([a2_triangulated, b2])

    previous = (a3,b3)