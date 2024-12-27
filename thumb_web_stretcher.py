import math

from pyocct_system import *

initialize_pyocct_system()

# mc = metacarpal, assume of the thumb
mc_thickness = 26
mc_width_on_build_plane = 25
pinchers_pinch_flesh_to_thickness = 6
pinchers_pinch_flesh_fallaway_slope = 0.7
pincher_stretch_flesh_to_distance = 36
dont_pinch_2d_web_thinner_than = 22
@run_if_changed
def index_pinch_angle():
    return Degrees(60)
@run_if_changed
def thumb_pinch_angle():
    return Degrees(90)
@run_if_changed
def thumb_support_angle():
    return Degrees(78)
pincher_radius = 2
strut_thickness = 10

def cross_section_poles(z):
    plane = Plane(Origin+Up*z, Up)
    p1 = ((Origin + Left*(pincher_stretch_flesh_to_distance - (pincher_radius*2)))
          .projected(onto=plane, by=(Right*1)@Rotate(Front, index_pinch_angle)))
    p2 = (Origin+Right*5).projected(onto=plane, by=(Right*1)@Rotate(Front, thumb_pinch_angle))
    end_of_thumb = ((Origin+Right*mc_width_on_build_plane)
                    .projected(onto=plane, by=(Right*1)@Rotate(Front, thumb_support_angle)))
    flesh_thickness = pinchers_pinch_flesh_to_thickness + pinchers_pinch_flesh_fallaway_slope*z
    def pincher_points(center):
        return [center + Front*(flesh_thickness/2 + pincher_radius) + (Right*pincher_radius)@Rotate(Up, Degrees(d)) for d in subdivisions(0, 180, amount=7)]
    pp1_center = p1 + Right*pincher_radius
    pp2_center = p2 + Left*pincher_radius
    pp1 = pincher_points(pp1_center)
    pp2 = pincher_points(pp2_center)
    one_side = ([]
            + [end_of_thumb + Front*x for x in subdivisions(0, mc_thickness/2, amount=3)[:-1]]
            + [p + Front*mc_thickness/2 for p in subdivisions(end_of_thumb, p2, amount=5)]
            + pp2
            + [p + Front*dont_pinch_2d_web_thinner_than/2 for p in subdivisions(pp2_center + Left*pincher_radius, pp1_center + Right*pincher_radius, amount=7)]
            + pp1
            + [p + Front*(max(mc_thickness/2, dont_pinch_2d_web_thinner_than/2) + strut_thickness) for p in subdivisions(pp1_center + Left*pincher_radius, end_of_thumb + Right*strut_thickness, amount=7)]
            + [end_of_thumb + Right*strut_thickness + Front*x for x in subdivisions(mc_thickness/2 + strut_thickness, 0, amount=3)[1:]]
    )
    return one_side + [p @ Mirror(Back) for p in one_side[1:-1][::-1]]


@run_if_changed
def thumb_web_stretcher():
    c0 = cross_section_poles(0)
    c1 = cross_section_poles(20)
    cu0 = BSplineCurve(c0, periodic=True)
    cu1 = BSplineCurve(c1, periodic=True)
    # preview(cu0, cu1)
    shell = Shell([Face(f) for f in[
                   cu0, cu1,
                   BSplineSurface([c0,c1], BSplineDimension(degree=1), BSplineDimension(periodic=True)),
                   ]])

    save_STL("thumb_web_stretcher", shell)
    # export("thumb_web_stretcher.stl", "thumb_web_stretcher_3.stl")
    preview(shell)