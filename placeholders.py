class Expression:
  pass
  
class Placeholder (Expression):
  def __init__(self, name):
    self.name = name
    
  def resolve (self, mappings):
    mappings.get (self.name)
  
class Operation (Expression):
  def __init__(self, operation, *args, **kwargs):
    self.operation = operation
    self.args = args
    self.kwargs = kwargs
    
class Unresolved:
  pass
  
def _resolve_impl (expression, mappings):
  if isinstance (expression, Placeholder):
    return mappings.get (expression.name, Unresolved)
  if isinstance (expression, Operation):
    args = []
    for argument in expression.args:
      resolved = resolve(argument, mappings)
      if resolved is Unresolved:
        return Unresolved
      args.append (resolved)
    kwargs = {}
    for key, value in expression.kwargs.items():
      resolved_key = resolve(key, mappings)
      if resolved_key is Unresolved:
        return Unresolved
      resolved_value = resolve (value, mappings)
      if resolved_value is Unresolved:
        return Unresolved
      kwargs [resolved_key] = resolve_value
    return expression.operation (*args,**kwargs)
  return expression
  
def resolve (expression, mappings):
  for key in mappings.keys():
    assert type (key) is str, "mapping keys must be strings (did you accidentally put a Placeholder instead?)"
  return _resolve_impl(expression, mappings)
    
# not sure exactly which operators should be included...?
reversible_binary_operator_names = ["add", "sub", "mul", "matmul", "truediv", "floordiv", "mod", "divmod", "pow", "lshift", "rshift", "and", "xor", "or"]
operator_names = reversible_binary_operator_names + ["r"+a for a in reversible_binary_operator_names] + ["neg", "pos", "abs", "invert", "round", "trunc", "floor", "ceil"]

def handle_operator (name):
  def do_operation(self, *args, **kwargs):
    return getattr(self, name)(*args, **kwargs)
  def make_operation(self, *args,**kwargs):
    return Operation (do_operation, self, *args, **kwargs)
  setattr (Expression, name, make_operation)
  
for name in operator_names:
  handle_operator ("__" + name + "__")


'''
examples:

terrible = Placeholder ("bar")
wonderful = Placeholder ("foo")
print (terrible)
print (resolve (terrible, {}))
print (resolve (terrible, {"bar": 5}))
print (resolve (terrible+5, {"bar": 5}))
print (resolve (6+terrible, {"bar": 5}))
print (resolve (terrible + wonderful + [5, 6], {"bar": [1,2], "foo":[3,4]}))
'''