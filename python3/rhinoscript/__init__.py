"""A collection of RhinoScript-like functions that can be called from Python"""

__all__ = [
    "application",
    "block",
    "curve",
    "dimension",
    "document",
    "geometry",
    "grips",
    "group",
    "hatch",
    "layer",
    "line",
    "linetype",
    "light",
    "mesh",
    "object",
    "plane",
    "pointvector",
    "selection",
    "surface",
    "toolbar",
    "transformation",
    "userdata",
    "userinterface",
    "utility",
    "view",
]


from . import application
from . import block
from . import curve
from . import dimension
from . import document
from . import geometry
from . import grips
from . import group
from . import hatch
from . import layer
from . import line
from . import linetype
from . import light
from . import mesh

# FIXME: bad object name
from . import object  # pylint: disable=redefined-builtin
from . import plane
from . import pointvector
from . import selection
from . import surface
from . import toolbar
from . import transformation
from . import userdata
from . import userinterface
from . import utility
from . import view
