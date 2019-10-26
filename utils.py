import numpy
import json

def normalize (vector):
  return vector/numpy.linalg.norm(vector)
  
def linear_step(left, right, x):
  f = (x - left) / (right - left)
  if f <= 0: return 0
  if f >= 1: return 1
  return f
    
def smootherstep(left, right, x):
  f = (x - left) / (right - left)
  if f <= 0: return 0
  if f >= 1: return 1
  return f*f*f*(f*(f*6 - 15) + 10 );


def offset_measurement_points (source_coordinates, epsilon = 0.00001):
  return [
    source_coordinates,
    source_coordinates + [0, epsilon],
    source_coordinates + [epsilon, -epsilon],
    source_coordinates + [-epsilon, -epsilon],
  ]

def offset_from_measurement_points (space_points, offset):
  normal = normalize (numpy.cross(
    space_points [3]-space_points [1],
    space_points [2]-space_points [1]
  ))
  return space_points [0] - normal*offset


# A "surface" is a function that takes x,y coords and returns a 3d vector,
# assumed to be locally Euclidean
def offset_from_surface (surface, source_coordinates, offset, epsilon = 0.00001):
  measurement_points = offset_measurement_points (source_coordinates, epsilon)
  return offset_from_measurement_points ([surface (v) for v in measurement_points], offset)


def scad_variables(variables):
  def fix(v):
    if type(v) is list:
      v = [fix(x) for x in v]
    if type(v) is numpy.ndarray:
      v = v.tolist()
    return v
  def line(k,v):
    return f"{k} = {json.dumps (fix(v))};"
  return "\n".join(line(k,v) for k,v in variables.items())
