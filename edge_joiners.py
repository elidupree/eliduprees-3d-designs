import math
from pyocct_system import *

wall_thickness = 0.8
channel_thickness = 0.8
channel_wraparound_length = 1.2
injection_hole_radius = 2

class AbuttingSheet:
    def __init__(self, joiner, index):
        self.further_into_sheet = joiner.edge_directions[index]
        self.sideways_towards_this = joiner.along_edge.cross(joiner.inwards)
        if self.sideways_towards_this.dot(self.further_into_sheet) < 0:
            self.sideways_towards_this = -self.sideways_towards_this
        self.outwards = self.further_into_sheet.cross(joiner.along_edge)
        if self.outwards.dot(joiner.inwards) > 0:
            self.outwards = -self.outwards

        self.inside_corner = joiner.inside_corners[0] + self.further_into_sheet*(wall_thickness/2 + channel_thickness)/self.further_into_sheet.dot(self.sideways_towards_this)
        self.outside_corner = self.inside_corner + self.outwards * joiner.sheet_thickness

        self.sheet_face = Vertex(self.inside_corner).extrude(self.outside_corner - self.inside_corner).extrude(self.further_into_sheet * 10)
        self.extended_sheet_face = Vertex(self.inside_corner).extrude(self.outside_corner - self.inside_corner).extrude(self.further_into_sheet * 30, centered=True)
        self.block_face = Vertex(self.inside_corner + self.further_into_sheet * (channel_wraparound_length + wall_thickness)).extrude(self.outwards * -(channel_thickness + wall_thickness), self.outwards * (joiner.sheet_thickness + channel_thickness + wall_thickness)).extrude(self.further_into_sheet * -10)
        self.wide_channels_face = Vertex(self.inside_corner + self.further_into_sheet * channel_wraparound_length).extrude(self.outwards * -channel_thickness, self.outwards * (joiner.sheet_thickness + channel_thickness)).extrude(self.further_into_sheet * -10)

        self.this_side = HalfSpace(joiner.inside_corners[0], self.sideways_towards_this)
        self.narrow_channeled_face = self.block_face.cut(self.extended_sheet_face).intersection(self.this_side)
        self.wide_channeled_face = self.narrow_channeled_face.cut(self.wide_channels_face)
        #preview (self.block_face, self.extended_sheet_face, self.wide_channels_face, self.wide_channeled_face.edges())



class EdgeJoiner:
    def __init__(self, inside_corners, edge_directions, sheet_thickness):
        self.inside_corners = inside_corners
        self.edge_directions = edge_directions
        self.sheet_thickness = sheet_thickness
        a, b = inside_corners
        d1, d2 = edge_directions
        v = b - a
        self.inwards = Direction(d1 + d2)
        print(self.inwards)
        self.along_edge = Direction (b - a)

        self.sheets = [AbuttingSheet(self, i) for i in range(2)]
        self.above_build_surface = HalfSpace(self.sheets[0].outside_corner - self.inwards * (channel_thickness + wall_thickness), self.inwards)
        self.above_floor = HalfSpace(self.sheets[0].outside_corner - self.inwards * channel_thickness, self.inwards)

        self.floor_face = Vertex (self.sheets[0].outside_corner - self.inwards * channel_thickness).extrude (wall_thickness * - self.inwards).extrude (self.sheets[0].sideways_towards_this * 30, centered = True)
        self.floor_face = Intersection (*[s.block_face for s in self.sheets]).intersection (self.floor_face)

        self.central_support_face = Vertex (inside_corners[0]).extrude (self.sheets[0].sideways_towards_this * wall_thickness, centered = True).extrude (self.inwards * 30, centered = True)
        self.central_support_face = Intersection (*[s.block_face for s in self.sheets]).intersection (self.above_build_surface).intersection (self.central_support_face)

        injection_hole = Face (Circle (Axes(inside_corners[0],self.inwards), injection_hole_radius)).extrude (-self.inwards*30)

        self.length = self.inside_corners[0].distance (self.inside_corners[1])
        self.injection_hole_positions = [self.length/2]
        self.injection_holes = [injection_hole @ Translate(self.along_edge * d) for d in self.injection_hole_positions]

        self.ridges = Compound ([Vertex (inside_corners[0] + self.along_edge * d).extrude(self.along_edge * wall_thickness).extrude (self.sheets[0].sideways_towards_this * 30, centered = True).extrude (self.inwards * 30, centered = True) for d in subdivisions (0, self.length -wall_thickness,max_length =5) if all(abs(l - (d + wall_thickness*0.5)) > (injection_hole_radius+ wall_thickness*0.5) for l in self.injection_hole_positions)])

        self.solid = Compound (
            [s.wide_channeled_face.extrude(v).intersection (self.above_build_surface).cut (self.injection_holes) for s in self.sheets],
            [s.narrow_channeled_face.extrude(v).intersection (self.above_build_surface).intersection (self.ridges) for s in self.sheets],
            self.floor_face.extrude(v).cut (self.injection_holes),
            self.central_support_face.extrude(v).cut (self.injection_holes),
        )

        self.build_solid = self.solid @ Transform(self.sheets[0].sideways_towards_this, self.along_edge, self.inwards).inverse()

