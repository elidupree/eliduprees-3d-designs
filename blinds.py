import math

from pyocct_system import *
from pyocct_utils import turn_subdivisions, inch

initialize_pyocct_system()

cordlock_radius = 6.5
cord_radius = 2.5
assumed_slat_thickness_min = 4
assumed_slat_thickness_max = 8
grabber_length = 10

# staple_width = 12.68
# staple_thickness = 0.45

# @run_if_changed
def blinds_hinge():
    solid_thickness = 1.5
    springy_thickness = 1
    min_wall_thickness = 0.5

    grabber_total_thickness = assumed_slat_thickness_max + springy_thickness + min_wall_thickness
    grabber_corner = Point(cord_radius, cord_radius*2 + grabber_total_thickness + solid_thickness)
    total_height = solid_thickness*2 + cord_radius*2

    main_profile = Compound([
        Face(Circle(Axes(Origin, Up), cordlock_radius+solid_thickness)),
        Face(Wire([
            Origin + Right*cord_radius,
            grabber_corner + Vector(0, 0),
            # grabber_corner + Vector(0, grabber_length),
            # grabber_corner + Vector(springy_thickness, grabber_length),
            # grabber_corner + Vector(springy_thickness, 0),
            # grabber_corner + Vector(grabber_total_thickness-springy_thickness, 0),
            # grabber_corner + Vector(grabber_total_thickness-springy_thickness, grabber_length),
            # grabber_corner + Vector(grabber_total_thickness, grabber_length),
            grabber_corner + Vector(grabber_total_thickness, 0),
            Point(cordlock_radius+solid_thickness, 0, 0)], loop=True)),
    ]).cut(Face(Circle(Axes(Origin, Up), cordlock_radius)))

    jaws_base = Compound([
        Vertex(Origin).extrude(Up*total_height).extrude(Left*springy_thickness),
        Wire([Point(assumed_slat_thickness_max, 0, 0), Point(assumed_slat_thickness_min, 0, total_height/2), Point(assumed_slat_thickness_max, 0, total_height)]).extrude(Right*min_wall_thickness),
    ]).extrude(Back*grabber_length)

    tooth_length = 3
    tooth = Vertex(Origin).extrude(Front*2).extrude(Up*2).extrude(Right*tooth_length)
    tooth_point = Point(tooth_length, -1, 1)
    dx = 0.6
    tooth = tooth.cut([
        HalfSpace(tooth_point, d)
        for d in [Direction(dx,1,0), Direction(dx,-1,0)]
    ])
    tooth = tooth.cut([
        HalfSpace(tooth_point, d)
        for d in [Direction(dx,0,1), Direction(dx,0,-1)]
    ])

    jaws = Compound(jaws_base, [tooth @ Translate(Back*grabber_length*f) for f in [0.4,1.0]]) @ Translate(Right*springy_thickness)

    cord_shadow = Vertex(0,0,total_height/2).extrude(Right*cord_radius, Left*100).extrude(Up*cord_radius*2, centered=True).extrude(Back*100, centered=True)

    a = Point(cordlock_radius, 0, total_height)
    rough_surface_avoidance_catch = Wire(BSplineCurve([
        a,
        a + Vector(-1, 0, 1),
        a + Vector(-1, 0, 2),
        a + Vector(0, 0, 3),
    ])).extrude(Back*3, centered=True).extrude(Right*springy_thickness)

    result = main_profile.extrude(Up*total_height)
    result = result.cut([cord_shadow, cord_shadow @ Rotate(Up, Degrees(135))])
    result = Compound(result, [rough_surface_avoidance_catch @ Rotate(Up, Degrees(d)) for d in [0, 120, 240]])

    result = Compound(result, jaws @ Translate(grabber_corner - Origin))
    save_STL("blinds_hinge", result)
    export("blinds_hinge.stl", "blinds_hinge_2.stl")

    preview(result)

@run_if_changed
def blinds_hinge_2():
    # note for future Eli: this function is currently messy because I built and discarded several different ideas in it
    base_thickness = 2.4
    ring_thickness = 1.5

    ring_or = cordlock_radius+ring_thickness
    ring_cut = Face(Circle(Axes(Origin, Up), cordlock_radius))
    ring_uncut = Face(Circle(Axes(Origin, Up), ring_or))

    flute_distance = 4.08
    slat_thickness = 4

    pillar_radius = 3/2
    cord_space = 3.5

    pillar_stop_top = base_thickness+cord_space+base_thickness
    pillar = Face(Wire([BSplineCurve([
        Point(pillar_radius, 0, 0),
        Point(pillar_radius, 0, pillar_stop_top-1),
        Point(pillar_radius+1, 0, pillar_stop_top-1),
        Point(pillar_radius+1, 0, pillar_stop_top),
        Point(pillar_radius, 0, pillar_stop_top),
        Point(pillar_radius, 0, pillar_stop_top+6),
        Point(pillar_radius+0.5, 0, pillar_stop_top+6),
        Point(pillar_radius+0.5, 0, pillar_stop_top+7),
        Point(pillar_radius, 0, pillar_stop_top+7),
        Point(pillar_radius, 0, pillar_stop_top+10),
        Point(0, 0, pillar_stop_top+10),
    ]), Origin], loop=True)).revolve(Up)


    def pillar_offset(num_flutes):
        return Vector(flute_distance*num_flutes, cordlock_radius + slat_thickness*0.6, 0)


    a = pillar_offset(3)
    b = pillar_offset(6)
    cantilever_base_connector=Face(Wire([
        Point(0, pillar_radius, 0) @ Translate(v) for v in [a,b]
    ] + [
        Point(0, -pillar_radius, 0) @ Translate(b),
        Origin + (Direction(b)@Rotate(Up, Degrees(-90))) * ring_or,
        Point(0, ring_or),
    ], loop=True))
    cantilever_base = Compound(ring_uncut, cantilever_base_connector).cut(ring_cut).extrude(Up*base_thickness)

    cantilever_part = Compound(cantilever_base, [pillar @ Translate(v) for v in [a,b]])

    a = pillar_offset(-1)
    b = pillar_offset(1)
    direct_base_connector=Face(Wire(
        [
            Point(0, pillar_radius, 0) @ Translate(v) for v in [a,b]
        ] + [
            Point(0, -cordlock_radius, 0) @ Translate(v) for v in [b,a]
        ], loop=True))
    direct_base = Compound(ring_uncut, direct_base_connector).cut(ring_cut).extrude(Up*base_thickness)

    # retainer_guide_wall_1 = Vertex(Origin).extrude(Back*1.0, centered=True).extrude(Left*(ring_or+2)*2, centered=True).cut(ring_cut).extrude(Up*(base_thickness+2.5))
    # retainer_guide_wall_1 = Chamfer(retainer_guide_wall_1, [(e, 0.2) for e in retainer_guide_wall_1.edges()])
    # retainer_guide_wall_2 = (retainer_guide_wall_1 @ Rotate(Up, Degrees(40))).cut(HalfSpace(Origin+Back*cordlock_radius, Back))

    retainer_guide_extra_height = 4.5
    retainer_grip_profile_inner_points = [
        Point(ring_or - ring_thickness*0.7, 0, 0),
        Point(ring_or - ring_thickness*0.7, 0, base_thickness + cord_space - 1),
        Point(ring_or - ring_thickness*0.7, 0, base_thickness + cord_space - 1),
        Point(ring_or - ring_thickness*0.7, 0, base_thickness + cord_space),
        Point(ring_or, 0, base_thickness + cord_space),
        Point(ring_or+0.3, 0, base_thickness + cord_space),
        Point(ring_or+0.3, 0, base_thickness + cord_space + base_thickness-0.3),
        Point(ring_or, 0, base_thickness + cord_space + base_thickness),
        Point(ring_or - ring_thickness*0.7, 0, base_thickness + cord_space + base_thickness+0.9),
        Point(ring_or - ring_thickness*0.7, 0, base_thickness + cord_space + base_thickness + 1.3),
        Point(ring_or - ring_thickness*0.7, 0, base_thickness + cord_space + base_thickness + retainer_guide_extra_height/2),
        Point(ring_or+1, 0, base_thickness + cord_space + base_thickness + retainer_guide_extra_height),
        Point(ring_or+2, 0, base_thickness + cord_space + base_thickness + retainer_guide_extra_height),]
    # retainer_grip_cut_section = Edge(BSplineCurve(retainer_grip_profile_inner_points)).extrude(Left*0.3,Right*10) @ Translate(Down*(base_thickness + cord_space))
    # retainer_grip_cut = (retainer_grip_cut_section @ Rotate(Up, Degrees(14))).revolve(Up, Degrees(32))
    # retainer_guide_ring = Face(Circle(Axes(Origin, Up), ring_or+2)).extrude(Up*(base_thickness + 2.5)).cut(retainer_grip_cut)
    retainer_guide_wall_section = Face(Wire([
        Point(cordlock_radius,0,0),
        Point(ring_or-0.1,0,0),
        Point(ring_or-0.1+base_thickness,0,base_thickness),
        # Point(ring_or+2,0,base_thickness+retainer_guide_extra_height-1),
        # Point(ring_or+1,0,base_thickness+retainer_guide_extra_height),
        # Point(cordlock_radius+1,0,base_thickness+retainer_guide_extra_height),
        # Point(cordlock_radius,0,base_thickness+retainer_guide_extra_height/2),
        Point(cordlock_radius,0,base_thickness),
    ], loop=True))

    retainer_guide_wall_cord_pass_degrees = 34
    retainer_prong_degrees = 16

    retainer_guide_wall_back_start_degrees = retainer_guide_wall_cord_pass_degrees/2+retainer_prong_degrees+1
    retainer_guide_wall_back = retainer_guide_wall_section.revolve(Up, Degrees(9)) @ Rotate(Up, Degrees(retainer_guide_wall_back_start_degrees))

    retainer_guide_walls = Compound(
        retainer_guide_wall_section.revolve(Up, Degrees(retainer_guide_wall_cord_pass_degrees)) @ Rotate(Up, Degrees(-retainer_guide_wall_cord_pass_degrees/2)),
        retainer_guide_wall_back.cut(HalfSpace(Origin+Back*cordlock_radius, Back)),
        retainer_guide_wall_back @ Mirror(Front)
    )

    direct_part = Compound(direct_base,
                           retainer_guide_walls,
                           retainer_guide_walls @ Mirror(Left),
                           # retainer_guide_wall_1, retainer_guide_wall_2, retainer_guide_wall_2 @ Mirror(Right),
                           [(pillar @ Translate(v + Down*(cord_space + base_thickness))).cut(HalfSpace(Origin, Down)) for v in [a,b]])
    retainer_grip_profile = BSplineCurve(retainer_grip_profile_inner_points + [
        Point(ring_or+2.1, 0, base_thickness + cord_space + base_thickness + 1.3),
        Point(ring_or+2.1, 0, base_thickness + cord_space + base_thickness),
        Point(ring_or+2.1, 0, base_thickness + cord_space),
        Point(ring_or, 0, 0),
    ])
    retainer_grip = Face(Wire(retainer_grip_profile, loop=True)).revolve(Up, Degrees(retainer_prong_degrees))
    retainer_base = Face(Circle(Axes(Origin, Up), ring_or+0.5)).cut(ring_cut).extrude(Up*base_thickness, Down*1.2)
    retainer_grip_part = Compound([retainer_base, retainer_grip, retainer_grip @ Rotate(Up, Turns(0.5))])


    retainer_staple_contact_leeway = 0.3
    # retainer_staple_noncontact_leeway = 0.5
    retainer_staple_avoid_cordlock = cordlock_radius #+0.5  # (can afford to do exactly cordlock_radius because in-fact the printing imprecisions force a higher distance)
    retainer_staple_avoid_cordlock_harder = cordlock_radius+2
    retainer_staple_width = 2.4
    retainer_staple_point_length = 2
    retainer_staple_point_z = -11.7
    curve1_half = [
        Point(0, 0, retainer_staple_point_z),
        Point(3, 0, retainer_staple_point_z - retainer_staple_point_length),
        Point(5, 0, retainer_staple_point_z - retainer_staple_point_length),
        # Point(retainer_staple_avoid_cordlock_harder-3, 0, retainer_staple_point_z - retainer_staple_point_length),
        Point(retainer_staple_avoid_cordlock_harder, 0, retainer_staple_point_z - retainer_staple_point_length),
        Point(retainer_staple_avoid_cordlock_harder, 0, retainer_staple_point_z - retainer_staple_point_length + 3),
        Point(retainer_staple_avoid_cordlock_harder, 0, -retainer_staple_contact_leeway - 1.5),
        Point(retainer_staple_avoid_cordlock, 0, -retainer_staple_contact_leeway - 1),
        Point(retainer_staple_avoid_cordlock, 0, -retainer_staple_contact_leeway - 0.5),
        Point(retainer_staple_avoid_cordlock, 0, -retainer_staple_contact_leeway),
    ]
    curve2_half = [
        Point(retainer_staple_avoid_cordlock, 0, base_thickness + retainer_staple_contact_leeway),
        Point(retainer_staple_avoid_cordlock, 0, base_thickness + retainer_staple_contact_leeway + 0.5),
        Point(retainer_staple_avoid_cordlock, 0, base_thickness + retainer_staple_contact_leeway + 1),
        Point(retainer_staple_avoid_cordlock_harder + retainer_staple_width - 2, 0, base_thickness + retainer_staple_contact_leeway + 1),
        Point(retainer_staple_avoid_cordlock_harder + retainer_staple_width, 0, base_thickness + retainer_staple_contact_leeway + 1),
        Point(retainer_staple_avoid_cordlock_harder + retainer_staple_width, 0, base_thickness + retainer_staple_contact_leeway + 1 - 3),
        Point(retainer_staple_avoid_cordlock_harder + retainer_staple_width, 0, retainer_staple_point_z - retainer_staple_point_length - retainer_staple_width + 6),
        Point(retainer_staple_avoid_cordlock_harder + retainer_staple_width, 0, retainer_staple_point_z - retainer_staple_point_length - retainer_staple_width + 2),
        Point(retainer_staple_avoid_cordlock_harder + retainer_staple_width - 2, 0, retainer_staple_point_z - retainer_staple_point_length - retainer_staple_width),
        Point(cordlock_radius/2, 0, retainer_staple_point_z - retainer_staple_point_length - retainer_staple_width),
        Point(0, 0, retainer_staple_point_z - retainer_staple_point_length - retainer_staple_width),
    ]
    retainer_staple_half_edges = [
        BSplineCurve(curve1_half),

        Point(ring_or, 0, -retainer_staple_contact_leeway),
        Point(ring_or, 0, base_thickness + retainer_staple_contact_leeway),

        BSplineCurve(curve2_half),
    ]
    def reversed(obj):
        if hasattr(obj, "reversed"):
            return obj.reversed()
        return obj
    # retainer_staple_half_wire = Wire(retainer_staple_half_edges)
    # preview(Wire(retainer_staple_half_edges, [reversed(a) @ Mirror(Right) for a in retainer_staple_half_edges[::-1]]))
    # preview(Wire(retainer_staple_points[::-1] + [a @ Mirror(Right) for a in retainer_staple_points[1:]], loop=True))
    retainer_staple_thickness = 1.8
    retainer_staple = Face(Wire(retainer_staple_half_edges, [reversed(a) @ Mirror(Right) for a in retainer_staple_half_edges[::-1]])).extrude(Back*retainer_staple_thickness, centered=True)
    point_sharpener = Vertex(0, 0, retainer_staple_point_z).extrude(Left*5, centered=True).extrude(Up*5).extrude(Vector(0, -10, -10), centered=True)
    retainer_staple = retainer_staple.cut([point_sharpener, point_sharpener @ Mirror(Back)])
    # preview(retainer_staple_points)

    save_STL("blinds_hinge_cantilever_part", cantilever_part)
    export("blinds_hinge_cantilever_part.stl", "blinds_hinge_cantilever_part.stl")
    save_STL("blinds_hinge_direct_part", direct_part)
    export("blinds_hinge_direct_part.stl", "blinds_hinge_direct_part.stl")
    save_STL("blinds_hinge_retainer_grip_part", retainer_grip_part)
    export("blinds_hinge_retainer_grip_part.stl", "blinds_hinge_retainer_grip_part.stl")
    save_STL("blinds_hinge_retainer_staple", retainer_staple @ Rotate(Left, Degrees(90)))
    export("blinds_hinge_retainer_staple.stl", "blinds_hinge_retainer_staple.stl")
    preview(
        direct_part, # @ Translate(Up*(cord_space + base_thickness)),
        #retainer_grip_part @ Rotate(Up, Degrees(retainer_guide_wall_cord_pass_degrees/2 + 1)),
        retainer_staple @ Rotate(Up, Degrees(retainer_guide_wall_cord_pass_degrees/2 + retainer_prong_degrees/2)),
        # retainer_grip_cut
        #cantilever_part
            )

@run_if_changed
def blinds_hinge_3():
    spear_thickness = 1.8
    prong_max_halfwidth = 2.5
    prong_mid_halfwidth = 1.8
    crossguard_width = 1.1
    crossguard_length = 8
    face_cuts = [HalfSpace(Origin + d*spear_thickness/2, d) for d in [Up, Down]]
    prong_uncut = Face(Wire([BSplineCurve([
        Point(-crossguard_width/2, prong_mid_halfwidth-0.5),
        Point(0, prong_mid_halfwidth-0.5),
        Point(3, prong_max_halfwidth-0.5),
        Point(6, prong_max_halfwidth-0.5),
        Point(6, prong_max_halfwidth),
        Point(7, prong_max_halfwidth),
        Point(7, prong_max_halfwidth-0.5),
        # Point(10, 1.2),
        # Point(11, 1.2),
        Point(14, prong_max_halfwidth-0.5),
        Point(14, prong_max_halfwidth),
        Point(15, prong_max_halfwidth),
        Point(15, prong_max_halfwidth-0.5),
        Point(20, prong_mid_halfwidth-0.5),
        Point(20, prong_mid_halfwidth),
        Point(21, prong_mid_halfwidth),
        Point(21, prong_mid_halfwidth-0.5),
        Point(25, 1),
        Point(26, 0),
    ]), Point(-crossguard_width/2,0,0)], loop=True)).revolve(Right)

    prong_edge_thickness = 1.1
    prong_cut = Intersection(prong_uncut @ Translate(Back*prong_edge_thickness), prong_uncut @ Translate(Front*prong_edge_thickness))
    # preview(prong_uncut.cut(face_cuts).cut(prong_cut))
    axle_radius = (spear_thickness/2)*math.sqrt(2) + 0.3
    axle_length = 6
    axle_snapin_dist = 4
    axle_snapin_x = -crossguard_width - axle_snapin_dist
    axle_end_x = -crossguard_width - axle_length
    axle_profile = Circle(Axes(Origin,Left), axle_radius)
    axle_uncut = Face(axle_profile).extrude(Left*crossguard_width/2, Left*(axle_length + crossguard_width))

    axle_snapin_length = 1
    axle_snapin_point_length = 0.9
    axle_edge_profile = Wire(axle_profile).cut(face_cuts).cut(HalfSpace(Origin, Back))
    pointy_surface = Edge(Origin, Origin + Direction(1,1,0) * 3).revolve(Front) @ Translate(Front*(axle_radius + axle_snapin_point_length) + Back*0.01)
    axle_snapin_other_surface = axle_edge_profile.extrude(Left*(axle_length - axle_snapin_dist), Right*(axle_snapin_dist+crossguard_width/2)) #.cut(pointy_surface.extrude(Back*10))
    pointy_surface = pointy_surface.cut(face_cuts).cut(axle_uncut @ Translate(Right*axle_length/2))
    # axle_snapin = axle_snapin_profile.extrude(Front*0.5, Left*(axle_snapin_length/2))
    # axle_snapin = Compound(axle_snapin, axle_snapin @ Mirror(Left))
    # preview(pointy_surface, axle_snapin_other_surface, axle_uncut)
    # axle_snapin = Compound(pointy_surface.extrude(Back*1.2), axle_snapin_other_surface.extrude(Back*1.1))
    axle_snapin = Compound(pointy_surface.extrude(Back*1.2).cut(axle_snapin_other_surface.extrude(Back*1.0,Back*5)), axle_snapin_other_surface.extrude(Back*1.0).cut(pointy_surface.extrude(Back*1.2, Back*5)))
    axle = Compound(axle_snapin, axle_snapin @ Mirror(Back)) @ Translate(Vector(axle_snapin_x, 0, 0))

    crossguard = Vertex(Origin).extrude(Left*crossguard_width).extrude(Front*crossguard_length, centered=True).extrude(Up*spear_thickness, centered=True)
    crossguard = Chamfer(crossguard, [(e, 0.3) for e in crossguard.edges()])

    prong = prong_uncut.cut(face_cuts).cut(prong_cut)
    # prong = prong.cut([HalfSpace(Point(-1.5,-1.5*d,0), Direction(-1,-1*d,0)) for d in [-1,1]])
    # axle = axle_uncut.cut(face_cuts)
    # cut_for_snapin = Vertex(Origin).extrude(Left*axle_snapin_spring_length, centered=True).extrude(Up*10, centered=True).extrude(Back*10, centered=True)
    # axle = axle.cut(cut_for_snapin)
    # preview(axle)
    # axle = Compound(axle, axle_snapin @ Translate(Left*(crossguard_width + axle_length/2)))
    
    spear = Compound(axle, crossguard, prong,
                    # prong @ Translate(Front*prong_span)
                    )

    jam_hole_radius = axle_radius + 0.4
    jam_hole_flare = 1.5
    jam_hole_profile_1 = [
        Point(-axle_length-0.4, jam_hole_radius, 0),
        Point(-axle_snapin_dist - axle_snapin_point_length, jam_hole_radius, 0),
        Point(-axle_snapin_dist, jam_hole_radius + axle_snapin_point_length, 0),
        Point(-axle_snapin_dist + axle_snapin_point_length, jam_hole_radius, 0),
        Point(-2, jam_hole_radius, 0),
        Point(0, jam_hole_radius+jam_hole_flare, 0),
    ]
    jam_hole_sections = [Wire([
        Point(0, 0, p[1]*math.sqrt(2)),
        TrimmedCurve(Circle(Axes(Origin, Right, Up), p[1]), math.tau/8, math.tau*7/8)
    ], loop=True) @ Translate(Right*p[0]) for p in jam_hole_profile_1]
    # preview(jam_hole_sections)
    jam_hole = Loft(jam_hole_sections, solid=True, ruled=True)
    # preview(jam_hole)

    # jam_hole_profile_2 = Face(Wire([jam_hole_profile_1, Point(-1, 0, 0), Point(-axle_length, 0, 0),], loop=True))
    # # preview(spear, jam_hole_profile)
    # jam_hole_fdm_accommodation_pieces = [Edge(jam_hole_profile_1).extrude(Front*10).extrude(Up*10, centered=True).cut(HalfSpace(Origin, Front)) @ Rotate(Right, Degrees(90+45*d)) for d in [-1,1]]
    # preview(jam_hole_fdm_accommodation_pieces)
    # jam_hole_fdm_accommodation = Intersection(
    #     *jam_hole_fdm_accommodation_pieces) @ Translate(Down*0.01)
    # preview(jam_hole_fdm_accommodation)
    # # preview(jam_hole_profile_2, jam_hole_fdm_accommodation)
    # preview(Union([jam_hole_profile_2.revolve(Right), jam_hole_fdm_accommodation]))
    #
    jam_socket_radius = jam_hole_radius+jam_hole_flare+0.5
    jam_socket_profile = Wire([
        Point(0, 0, -jam_socket_radius*math.sqrt(2)),
        TrimmedCurve(Circle(Axes(Origin, Right, Down), jam_socket_radius), math.tau/8, math.tau*7/8)
    ], loop=True)
    jam_socket = Face(jam_socket_profile).extrude(Left*(0.4+0.3), Left*(axle_length+1.4)).cut(HalfSpace(Origin + Down*jam_socket_radius, Down))
    # jam_socket = jam_socket.cut([jam_hole_profile_2.revolve(Right), jam_hole_fdm_accommodation])
    jam_socket = jam_socket.cut(jam_hole)
    # jam_hole_profile_2 =
    # jam =

    jam_v_tight = 3/2
    jam_v_leeway = 1
    jam_v_loose = jam_v_tight + jam_v_leeway
    jam_v_profile_1 = BSplineCurve([point + Up*v_z for v_z in [d*(jam_socket_radius-jam_v_leeway) for d in [-1,1]] for point in [
        # Point(jam_v_loose, 0, -jam_v_leeway*2),
        Point(jam_v_loose, 0, -jam_v_leeway),
        Point(jam_v_tight, 0, 0),
        Point(jam_v_tight, 0, 0),
        Point(jam_v_tight, 0, 0),
        Point(jam_v_loose, 0, jam_v_leeway),
        # Point(jam_v_loose, 0, jam_v_leeway*2),
    ]])
    jam_v_profile_2 = jam_v_profile_1.cartesian_product(BSplineCurve([
        Point(-0.5, 0, 0),
        Point(0, 1, 0),
        Point(0, 2, 0),
        Point(-0.5, 3.5, 0),
        Point(-1.3, 4.5, 0),
        Point(1, 7, 0),
        Point(2, 8, 0),
    ]))
    # preview(jam_v_profile_2)
    jam_v_thickness = 1.1
    jam_v_side = Face(jam_v_profile_2).extrude(Right*jam_v_thickness) @ Translate(Back*(jam_socket_radius))
    jam_v_outer = Wire(jam_v_profile_1) @ Translate(Right*(jam_v_thickness - 0.5))
    jam_axle_positioning = Translate(Left*axle_snapin_dist)
    jam_vs = Compound(
        jam_v_side,
        jam_v_side @ Mirror(Right),
        # Face(jam_v_profile_1.extrude(Right*0.6) @ Translate(Left*0.5)).revolve(Down, Turns(0.5)) @ Translate(Back*jam_v_loose)
    ) @ jam_axle_positioning
    jam_connector = (Loft([jam_v_outer, jam_v_outer @ Mirror(Right)], ruled=True).extrude(Back*(jam_socket_radius)) @ jam_axle_positioning).cut(jam_hole)
    jam = Compound(jam_socket, jam_vs, jam_connector)

    many_parts = Compound(
        [spear @ Translate(Vector(j*40, -(crossguard_length+0.5)*(i + 1.5))) for i in range(12) for j in range(1)] +
        [jam @ Translate(Vector(i*15,j*20,0)) for i in range(3) for j in range(4)]
    )

    save_STL("blinds_hinge_spear", spear)
    export("blinds_hinge_spear.stl", "blinds_hinge_spear.stl")
    save_STL("blinds_hinge_jam", jam)
    export("blinds_hinge_jam.stl", "blinds_hinge_jam.stl")
    # save_STL("blinds_hinge_many", many_parts)
    # export("blinds_hinge_many.stl", "blinds_hinge_many.stl")
    preview(many_parts)
    preview(spear, jam @ Translate(Left*crossguard_width))


# @run_if_changed
def vacuum_pleat_roller():
    length = 20
    axle_radius = 3
    wall_thickness = 0.5
    vacuum_chamber_ir = 16
    vacuum_chamber_or = vacuum_chamber_ir + wall_thickness
    groove_depth = 2
    roller_or = vacuum_chamber_or + groove_depth
    roller_oc = math.tau*roller_or
    groove_approx_period = 4
    num_grooves = round(roller_oc / groove_approx_period)

    slice = Edge(
        Point(vacuum_chamber_ir, 0, 0),
        Point(roller_or, 0, 0),
    ).revolve(Up, Turns(1/num_grooves/2)).extrude(Up*length)

    slices = Compound([slice @ Rotate(Up, a) for a in turn_subdivisions(amount=num_grooves)])

    preview(slices)

# @run_if_changed
def pleat_rollers():
    length = 10
    wall_thickness = 0.5
    groove_depth = 4
    groove_approx_period = 4
    body_radius = 10
    knobs_outer_radius = body_radius + groove_depth
    roller_oc = math.tau*knobs_outer_radius
    num_grooves = round(roller_oc / groove_approx_period)
    straights_extra_length = 0.5
    straights_outer_radius = knobs_outer_radius + straights_extra_length

    def version(prong):
        return Compound([
           prong @ Rotate(Up, a) for a in turn_subdivisions(amount=num_grooves)
        ] + [
            Face(Circle(Axes(Origin, Up), body_radius)).cut(Face(Circle(Axes(Origin, Up), body_radius - wall_thickness*2)))
        ]).extrude(Up*length)

    straight_prong = Vertex(body_radius, 0, 0).extrude(Left*wall_thickness/2, Right*(groove_depth+straights_extra_length)).extrude(Back*wall_thickness, centered=True)

    knob_radius = (groove_approx_period - wall_thickness - 1.0)/2
    knob_prong = Compound(
        Vertex(body_radius, 0, 0).extrude(Left*wall_thickness/2, Right*(groove_depth-wall_thickness/2)).extrude(Back*wall_thickness, centered=True),
        Face(Circle(Axes(Origin + Right*(knobs_outer_radius-knob_radius), Up), knob_radius))
    )

    straight_roller = version(straight_prong)
    knobbed_roller = version(knob_prong)
    knobbed_roller_test = knobbed_roller.cut(HalfSpace(Point(6,0,0), Left))

    save_STL("knobbed_roller_test", knobbed_roller_test)
    export("knobbed_roller_test.stl", "knobbed_roller_test.stl")

    preview(knobbed_roller_test, straight_roller, knobbed_roller @ Rotate(Up, Turns(0.5 + 0.5/num_grooves)) @ Translate(Right*(body_radius+straights_outer_radius)))

