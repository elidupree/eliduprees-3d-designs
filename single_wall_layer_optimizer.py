from scipy.optimize import minimize
from pyocct_system import *
from gcode_stuff.gcode_utils import *

class SingleWallLayers:
  def __init__(self, surface, num_layers, num_columns):
    self.surface = surface
    self.num_layers = num_layers
    self.num_columns = num_columns
    self.periodic = self.surface.IsVPeriodic()
    self.colrange = self.num_columns if periodic else (self.num_columns-1)
    (self.u1, self.u2, self.v1, self.v2) = self.surface.bounds()
    self.u_values = [u for u in subdivisions(self.u1, self.u2, amount=num_layers)[1:-1] for _ in range(num_columns)]

  def column_v(self, column):
    return Between(self.v1, self.v2, column / colrange)
  def layer_u(layer, u_values = None):
    if u_values is None: u_values = self.u_values
    if layer == 0: return self.u1
    if layer == self.num_layers - 1: return self.u2
    return u_values[(layer-1)*self.num_columns + column]
  def position(layer, column, u_values = None):
    if u_values is None: u_values = self.u_values
    return self.surface.position(parameter=(self.layer_u(layer, u_values), self.column_v(column)))
  def positions(u_values = None):
    if u_values is None: u_values = self.u_values
    return [[self.position(layer, column, u_values) for column in range(self.num_columns)] for layer in range(self.num_layers)]

  def optimize(self, *, undesired_thinness, undesired_thickness, undesired_overhang, undesired_slope):
    def loss(u_values):
      result = 0
      # upos = lambda l,c: pos(u_values, l, c)
      positions = self.positions(u_values)
      for column in range(self.num_columns):
        for layer1,layer2 in pairs(range(self.num_layers)):
          diff = positions[layer2][column] - positions[layer1][column]
          overhang = diff.projected_perpendicular(Up).length()
          if overhang > undesired_overhang:
            result += (overhang - undesired_overhang)**2
          if diff[2] > undesired_thickness:
            result += (diff[2] - undesired_thickness)**2
          if diff[2] < undesired_thinness:
            result += (undesired_thinness - diff[2])**2
      
      for layer1 in range(0,self.num_layers):
        for column1,column2 in pairs(range(), loop = self.periodic):
          if self.periodic and column2 == 0:
            layer2 = layer1 + 1
          else:
            layer2 = layer1
          diff = positions[layer2][column2] - positions[layer1][column1]
          h = diff.projected_perpendicular(Up).length()
          slope = abs(diff[2]/h)
          if slope > undesired_slope:
            result += (slope - undesired_slope)**2
      
      return result

    best_u_values = minimize(loss, self.u_values).x
    self.u_values = best_u_values

  def gcode_commands(self, *, line_width, extrusion_start = 0, speed=1500):
    extrusion = extrusion_start
    commands = []
    positions = self.positions()
    def step(l1, c1, l2, c2):
      nonlocal commands, extrusion
      p1 = positions[l1][c1]
      p2 = positions[l2][c2]
      p1_depth = p1[2] - positions[l1-1][c1][2]
      p2_depth = p2[2] - positions[l2-1][c2][2]
      extrusion += (p2 - p1).length() * Between(p1_depth, p2_depth) * line_width
      commands.append(g1(*p2,extrusion,f=speed))

    if self.periodic:
      commands.append(fastmove(*positions[1][0]))
      for l1 in range(1, self.num_layers):
        for c1 in range(0, self.num_columns):
          c2 = (c + 1)%self.num_columns
          l2 = l1+1 if c2 == 0 else l1
          step(l1, c1, l2, c2)

    else: # not self.periodic
      for l in range(1, self.num_layers):
        cols = list(range(self))
        if l % 2 == 0:
          cols.reverse()
        commands.append(fastmove(*positions(l,cols[0])))
        for c1, c2 in pairs(cols):
          step(l, c1, l, c2)
    
    return commands
      
        


      