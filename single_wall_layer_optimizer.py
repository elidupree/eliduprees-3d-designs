from collections import defaultdict
from scipy.optimize import minimize
from pyocct_system import *
from gcode_stuff.gcode_utils import *

class SingleWallLayers:
  def __init__(self, surface, num_layers, num_columns):
    self.surface = surface
    self.num_layers = num_layers
    self.num_columns = num_columns
    self.periodic = self.surface.IsVPeriodic()
    self.colrange = self.num_columns if self.periodic else (self.num_columns-1)
    (self.u1, self.u2, self.v1, self.v2) = self.surface.bounds(0,0,0,0)
    self.v_values = [v for v in subdivisions(self.v1, self.v2, amount=num_layers)[1:-1] for _ in range(num_columns)]

  def column_u(self, column):
    return Between(self.u1, self.u2, column / self.colrange)
  def layer_v(self, layer, column, v_values = None):
    if v_values is None: v_values = self.v_values
    if layer == 0: return self.v1
    if layer == self.num_layers - 1: return self.v2
    return v_values[(layer-1)*self.num_columns + column]
  def parameter(self, layer, column, v_values = None):
    return (self.layer_v(layer, column, v_values), self.column_u(column))
  def position(self, layer, column, v_values = None):
    return self.surface.position(parameter=self.parameter(layer, column, v_values))
  def normal_3d(self, layer, column, v_values = None):
    return self.surface.normal(parameter=self.parameter(layer, column, v_values))
  def normal_in_layer(self, layer, column, v_values = None):
    return Direction((self.normal_3d(layer,  column, v_values)*1).projected_perpendicular(Up))
  def positions(self, v_values = None):
    if v_values is None: v_values = self.v_values
    return [[self.position(layer, column, v_values) for column in range(self.num_columns)] for layer in range(self.num_layers)]

  def loss(self, v_values=None, *, undesired_thinness, undesired_thickness, undesired_overhang, undesired_slope, do_report=False):
    result = 0
    # upos = lambda l,c: pos(v_values, l, c)
    positions = self.positions(v_values)
    report = defaultdict(float)
    def bad(name, badness):
      nonlocal result
      result += badness**2
      if do_report:
        report[name] = max(report[name], badness)
    for column in range(self.num_columns):
      for layer1,layer2 in pairs(range(self.num_layers)):
        diff = positions[layer2][column] - positions[layer1][column]
        overhang = abs(diff.dot(self.normal_in_layer(layer1, column, v_values)))
        if overhang > undesired_overhang:
          bad("overhang", (overhang - undesired_overhang))
        if diff[2] > undesired_thickness:
          bad("thinness", (diff[2] - undesired_thickness))
        if diff[2] < undesired_thinness:
          bad("thickness", (undesired_thinness - diff[2]))

    for layer1 in range(0,self.num_layers):
      for column1,column2 in pairs(range(self.num_columns), loop = self.periodic):
        if self.periodic and column2 == 0:
          layer2 = layer1 + 1
        else:
          layer2 = layer1
        diff = positions[layer2][column2] - positions[layer1][column1]
        h = diff.projected_perpendicular(Up).length()
        slope = abs(diff[2]/h)
        if slope > undesired_slope:
          bad("slope", (slope - undesired_slope))

    if do_report:
      return result, report
    return result

  def optimize(self, **kwargs):
    best_v_values = minimize(lambda v_values: self.loss(v_values, **kwargs), self.v_values).x
    self.v_values = best_v_values
    return self.loss(report = True, **kwargs)

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
          c2 = (c1 + 1)%self.num_columns
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
      
        


      