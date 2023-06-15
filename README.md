# Eli Dupree's 3D Designs

## What is this?

It's the code I use to generate 3D models, mostly for 3D-printed DIY projects. It's not designed to be usable by anyone but Eli Dupree, but this README is a modest attempt to document it, so that "someone who knows how to mess around in Python" may be able to use it.


## How to use it?

First, you need [pyOCCT](https://anaconda.org/trelau/pyocct) installed.

Most of the files here describe individual projects. You can recognize these files by how they start with:

```python
import math

from pyocct_system import *
initialize_pyocct_system()
```

To use `some_file.py`, you run the command

```
python ./some_file.py --cache-directory /path/to/some/directory/
```

This will:
* Generate one or more 3D models.
* Display some of them in a preview window, where you can use the mouse to look around, and press `c` to close the window and continue the script.
* Save some of those models into the specified cache directory, as either OpenCASCADE BRep files, STL files, or SVG files, depending on the particular project.

The system is designed for the following workflow: I edit a script while auto-rerunning it to see the changed output, rather than ever treating the script as a finished product.

A few of the oldest files were made using other systems (OpenSCAD and FreeCAD scripts). I don't remember those systems too well. If I wanted to use those models, I would rewrite them to use my newer systems, rather than using them as-is.


## How does it work?

OpenCASCADE is a powerful tool for generating 3D models, but it's buggy, often slow, and its UI is a mess. pyOCCT is mostly machine-generated bindings for OpenCASCADE, so it inherits most of these problems. To improve on that, I've used a mess of Python metaprogramming, in `pyocct_system.py` and `pyocct_api_wrappers.py`, to implement two important systems.

### 1. Wrappers

Instead of using pyOCCT objects directly, I use custom wrappers around them. These wrappers forward all of the pyOCCT methods, but:
* Some methods are overridden, to add additional features or work around bugs.
* Wrappers also have a bunch of extra convenience methods of my own.
* For any pyOCCT method that returns another pyOCCT object, the wrapper returns another wrapped object instead.

I haven't really written documentation for specific wrapper methods. The best documentation is looking at how I've used them, or looking at the source code in `pyocct_api_wrappers.py`.

### 2. Caching

Since my process is "change the code and rerun it repeatedly", I can't accept multiple seconds of rerunning algorithms each time. To deal with this, I cache intermediate results. Any expensive operations should be put inside a function using the `@run_if_changed` decorator:

```python
@run_if_changed
def complex_model():
  some_model = expensive_operations()
  return some_model
```

`@run_if_changed` is a tricky little decorator that literally just runs the function being decorated – but only if it hasn't changed since the last time it was run, according to the caches that are stored in the `cache-directory`. After it returns, the return value is serialized into the cache, and the global variable `complex_model` holds the return value rather than the function. (If the function didn't run that time, it uses the stored version.)

`@run_if_changed` even decompiles the function, so that it can rerun the function if you changed any of the global variables referenced within the function. However, it can get confused if you _mutate_ global variables, and it treats a whole module as a single unit (if you change anything in a module, it reruns any function that referenced that module by name, even if it only used a different item from that module). To work around this, you can use `from module import item` instead, so only the item is referenced by name, not the module.

Only certain types can be serialized:
* the standard Python primitives `str`, `int`, `float`, `None`
* the OpenCASCADE shape types, `Vertex`, `Edge`, `Wire`, `Face`, `Shell`, `Solid`
* the OpenCASCADE `Geom` types, `Point`, `Vector`, `Direction`, `Curve`, `Surface`, and their 2D equivalents
* subclasses of `SerializeAsVars`
* lists, tuples, and dictionaries of serializable types


## License?

If you're an individual hobbyist, feel free to mess around with this code however you want!

If you're a corporation, or even a Free Software organization with a bit more formality (you know, the kind where you have 20-page-long forum debates about what exact licenses of code you should be using) – what are you doing using this code? It's a flaky pile of personal projects. Get outta here, lol.
