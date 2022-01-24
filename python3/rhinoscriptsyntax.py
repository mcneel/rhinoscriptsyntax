# this is not the best python scripting practice, but if you want everything in one big list
from rhinoscript.application import *
from rhinoscript.curve import *
from rhinoscript.document import *
from rhinoscript.geometry import *
from rhinoscript.layer import *
from rhinoscript.object import *
from rhinoscript.plane import *
from rhinoscript.selection import *
from rhinoscript.surface import *
from rhinoscript.userinterface import *
from rhinoscript.view import *
from rhinoscript.utility import *
from rhinoscript.block import *
from rhinoscript.group import *
from rhinoscript.mesh import *
from rhinoscript.line import *
from rhinoscript.transformation import *
from rhinoscript.grips import *
from rhinoscript.pointvector import *
from rhinoscript.userdata import *
from rhinoscript.material import *
from rhinoscript.dimension import *
from rhinoscript.light import *
from rhinoscript.hatch import *
from rhinoscript.linetype import *
from rhinoscript.toolbar import *

def __reverse_module_search(func_name):
    if func_name is None: return None
    if not isinstance(func_name, str): return None
    g_lower = dict((k.lower(),(k,v)) for k,v in list(globals().items()))
    f_lower = func_name.lower()
    if f_lower in g_lower:
        f_data = g_lower[f_lower]
        if f_data[1]:
            try:
                full_module_name = f_data[1].__module__
                if full_module_name: return (f_data[0],full_module_name)
            except:
                return None
