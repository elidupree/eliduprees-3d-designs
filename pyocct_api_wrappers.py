import re

import OCCT.Exchange
import OCCT.TopoDS
import OCCT.gp

def setup(wrap, export, override_attribute):
  _ExchangeBasic = wrap(OCCT.Exchange.ExchangeBasic)
  _GP = wrap(OCCT.gp)
  def vector(*arguments):
    if len (arguments) == 3:
      return _GP.gp_Vec(*(float (value) for value in arguments))
    if len (arguments) == 0:
      return _GP.gp_Vec()
  
  def vec_str(self):
    return f"Vec({self.X()}, {self.Y()}, {self.Z()})"
  def vec_index(self, index):
    if index == 0:
      return self.X()
    if index == 1:
      return self.Y()
    if index == 2:
      return self.Z()
    raise IndexError("vector can only be indexed with 0-2")
  
  override_attribute(OCCT.gp.gp_Vec, "__str__", lambda original: vec_str)
  override_attribute(OCCT.gp.gp_Vec, "__index__", lambda original: vec_index)
  
  for name in re.findall(r"[\w_]+", "vector"):
    export(name, locals()[name])
