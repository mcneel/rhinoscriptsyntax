"""Utility to convert py2 rhino-python files to py3 format"""
import os
import os.path as op
import shutil
from lib2to3.main import main  # this is what 2to3 cli utility uses


# read sources
SOURCE_DIR = r"../Scripts/"
DEST_DIR = r"../python3/"

ITEMS = [
    r"rhinoscript/",
    r"rhinoscriptsyntax.py",
    r"scriptcontext.py",
]


THIS_DIR = op.dirname(__file__)
ROOT_DIR = op.dirname(THIS_DIR)
print(f"{THIS_DIR=}")
print(f"{ROOT_DIR=}")


class SourceFile:
    """Context manager for a python source file"""

    def __init__(self, filename) -> None:
        self.filename = filename
        self.source = ""

    def __enter__(self):
        with open(self.filename, "r") as rf:
            self.source = rf.read()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        with open(self.filename, "w") as wf:
            wf.write(self.source)

    def replace(self, *args, **kwargs):
        """Replace string in source"""
        self.source = self.source.replace(*args, **kwargs)


def prep_dest(source, dest):
    """Prepare a new copy of source files"""
    if op.exists(dest):
        print(f"Deleting: {dest}")
        if op.isdir(dest):
            shutil.rmtree(dest)
        else:
            os.remove(dest)

    print(f"Updating: {dest}")
    if op.isdir(source):
        shutil.copytree(source, dest)
    else:
        shutil.copy(source, dest)


def convert_dest(dest):
    """Convert files to python3-compatible"""
    print(f"Converting: {dest}")
    main("lib2to3.fixes", args=["--write", "--nobackups", "--no-diffs", dest])


def apply_dest_fixes(dest):
    """Apply misc fixes to files"""

    def apply_fixes(item):
        item_name = op.splitext(op.basename(item))[0]
        fixer_func_name = f"{item_name}_fixes"
        if fixer_func := globals().get(fixer_func_name, None):
            fixer_func(item)

    print(f"Applying Fixes: {dest}")
    if op.isdir(dest):
        for dest_item in os.listdir(dest):
            apply_fixes(op.join(dest, dest_item))
    else:
        apply_fixes(dest)


# Fixers ======================================================================
# function naming format is <file_name>_fixes
# e.g. scriptcontext_fixes applies fixes to scriptcontext.py
# -----------------------------------------------------------------------------


def scriptcontext_fixes(item):
    """Fix misc items in scriptcontext.py"""
    with SourceFile(item) as sf:
        sf.replace(
            "import RhinoPython.Host as __host", "import Rhino"
        )
        sf.replace("doc = None", "doc = Rhino.RhinoDoc.ActiveDoc")
        sf.replace(
            "rc = __host.EscapePressed(reset)",
            "rc = None # __host.EscapePressed(reset)",
        )


def application_fixes(item):
    """Fix misc items in rhinoscript/application.py"""
    with SourceFile(item) as sf:
        sf.replace(
            """
import scriptcontext
import Rhino
import Rhino.ApplicationSettings.ModelAidSettings as modelaid
import Rhino.Commands.Command as rhcommand
import System.TimeSpan, System.Enum, System.Environment
import System.Windows.Forms.Screen
import datetime
from . import utility as rhutil
""".strip(),
            """
import datetime
import scriptcontext
from . import utility as rhutil

import System
from Rhino.ApplicationSettings import ModelAidSettings as modelaid
from Rhino.Commands import Command as rhcommand
from System import TimeSpan, Enum, Environment
from System.Windows.Forms import Screen
""".strip(),
        )
        sf.replace(
            "Rhino.PlugIns.PlugInType.None", "getattr(Rhino.PlugIns.PlugInType, 'NONE')"
        )
        sf.replace("filter =", "search_filter =")
        sf.replace("filter |=", "search_filter |=")
        sf.replace(
            "GetInstalledPlugInNames(filter,", "GetInstalledPlugInNames(search_filter,"
        )


def block_fixes(item):
    """Fix misc items in rhinoscript/block.py"""
    with SourceFile(item) as sf:
        sf.replace(
            """
import Rhino
import scriptcontext
from . import utility as rhutil
import math
import System.Guid
""".strip(),
            """
import math
import scriptcontext
from . import utility as rhutil

import System
import Rhino
from System import Guid
""".strip(),
        )


def curve_fixes(item):
    """Fix misc items in rhinoscript/curve.py"""
    with SourceFile(item) as sf:
        sf.replace(
            """
import scriptcontext
from . import utility as rhutil
import Rhino
import math
import System.Guid, System.Array, System.Enum
""".strip(),
            """
import math
import scriptcontext
from . import utility as rhutil

import System
import Rhino
from System import Guid, Array, Enum
""".strip(),
        )
        sf.replace(
            "Rhino.DocObjects.ObjectDecoration.None",
            "getattr(Rhino.DocObjects.ObjectDecoration, 'NONE')",
        )
        sf.replace("ValueException(", "ValueError(")


def dimension_fixes(item):
    """Fix misc items in rhinoscript/dimension.py"""
    with SourceFile(item) as sf:
        sf.replace(
            """
import scriptcontext
from . import utility as rhutil
import Rhino
import System.Guid
from .view import __viewhelper, ViewCPlane
""".strip(),
            """
import scriptcontext
from . import utility as rhutil
from .view import __viewhelper, ViewCPlane

import System
import Rhino
from System import Guid
""".strip(),
        )


def document_fixes(item):
    """Fix misc items in rhinoscript/document.py"""
    with SourceFile(item) as sf:
        sf.replace(
            """
import scriptcontext
import Rhino
import System.Enum, System.Drawing.Size
import System.IO
from . import utility as rhutil
import math
""".strip(),
            """
import math
import scriptcontext
from . import utility as rhutil

import System
import Rhino
from System import IO
from System import Enum
from System.Drawing import Size
""".strip(),
        )


def geometry_fixes(item):
    """Fix misc items in rhinoscript/geometry.py"""
    with SourceFile(item) as sf:
        sf.replace(
            """
import scriptcontext
from . import utility as rhutil
import Rhino
import System.Guid, System.Array
""".strip(),
            """
import scriptcontext
from . import utility as rhutil

import System
import Rhino
from System import Guid, Array
""".strip(),
        )


def hatch_fixes(item):
    """Fix misc items in rhinoscript/hatch.py"""
    with SourceFile(item) as sf:
        sf.replace(
            """
import scriptcontext
from . import utility as rhutil
import Rhino
import System.Guid
""".strip(),
            """
import scriptcontext
from . import utility as rhutil

import System
import Rhino
from System import Guid
""".strip(),
        )


def layer_fixes(item):
    """Fix misc items in rhinoscript/layer.py"""
    with SourceFile(item) as sf:
        sf.replace(
            """
import Rhino.DocObjects.Layer
import scriptcontext
from . import utility as rhutil
import System.Guid
from Rhino.RhinoMath import UnsetIntIndex
""".strip(),
            """
import scriptcontext
from . import utility as rhutil

import System
import Rhino
from System import Guid

UnsetIntIndex = Rhino.RhinoMath.UnsetIntIndex
Layer = Rhino.DocObjects.Layer
""".strip(),
        )
        sf.replace("if idx is 0:", "if idx == 0:")


def light_fixes(item):
    """Fix misc items in rhinoscript/light.py"""
    with SourceFile(item) as sf:
        sf.replace("Rhino.UnitSystem.None", "getattr(Rhino.UnitSystem, 'NONE')")


def line_fixes(item):
    """Fix misc items in rhinoscript/line.py"""
    with SourceFile(item) as sf:
        sf.replace(
            "Rhino.Geometry.Intersect.LineCylinderIntersection.None",
            "getattr(Rhino.Geometry.Intersect.LineCylinderIntersection, 'NONE')",
        )
        sf.replace(
            "Rhino.Geometry.Intersect.LineSphereIntersection.None",
            "getattr(Rhino.Geometry.Intersect.LineSphereIntersection, 'NONE')",
        )
        sf.replace("Execption(", "Exception(")


def mesh_fixes(item):
    """Fix misc items in rhinoscript/mesh.py"""
    with SourceFile(item) as sf:
        sf.replace(
            """
import scriptcontext
from . import utility as rhutil
import Rhino
import System.Guid, System.Array, System.Drawing.Color
from .view import __viewhelper
""".strip(),
            """
import scriptcontext
from . import utility as rhutil
from .view import __viewhelper

import System
import Rhino
from System import Guid, Array
from System.Drawing import Color
""".strip(),
        )


def object_fixes(item):
    """Fix misc items in rhinoscript/object.py"""
    with SourceFile(item) as sf:
        sf.replace(
            """
import scriptcontext
import Rhino
from . import utility as rhutil
import System.Guid, System.Enum
from .layer import __getlayer
from .view import __viewhelper
import math
""".strip(),
            """
import math
import scriptcontext
from . import utility as rhutil
from .layer import __getlayer
from .view import __viewhelper

import System
import Rhino
from System import Guid, Enum
""".strip(),
        )


def selection_fixes(item):
    """Fix misc items in rhinoscript/selection.py"""
    with SourceFile(item) as sf:
        sf.replace(
            "Rhino.DocObjects.ObjectType.None",
            "getattr(Rhino.DocObjects.ObjectType, 'NONE')",
        )
        sf.replace("def __FilterHelper(filter):", "def __FilterHelper(input_filter):")
        sf.replace("if filter &", "if input_filter &")


def surface_fixes(item):
    """Fix misc items in rhinoscript/surface.py"""
    with SourceFile(item) as sf:
        sf.replace(
            """
import scriptcontext
import math
import Rhino
import System.Guid
from . import utility as rhutil
from . import object as rhobject
from System.Collections.Generic import List
""".strip(),
            """
import math
import scriptcontext
from . import utility as rhutil
from . import object as rhobject

import System
import Rhino
from System import Guid
from System.Collections.Generic import List
""".strip(),
        )


def transformation_fixes(item):
    """Fix misc items in rhinoscript/transformation.py"""
    with SourceFile(item) as sf:
        sf.replace(
            """
import scriptcontext
from . import utility as rhutil
import Rhino
import System.Guid, System.Array
import math
from . import view as rhview
""".strip(),
            """
import math
import scriptcontext
from . import utility as rhutil
from . import view as rhview

import System
import Rhino
from System import Guid, Array
""".strip(),
        )


def userinterface_fixes(item):
    """Fix misc items in rhinoscript/userinterface.py"""
    with SourceFile(item) as sf:
        sf.replace(
            """
import Rhino
import Rhino.UI
from . import utility as rhutil
import scriptcontext
import System.Drawing.Color
import System.Enum
import System.Array
import Eto.Forms
import System.Windows.Forms
import math
from .view import __viewhelper
""".strip(),
            """
import math
import scriptcontext
from . import utility as rhutil
from .view import __viewhelper

import System
import Rhino
import Rhino.UI
import Eto.Forms
import System.Windows.Forms
from System import Enum, Array
from System.Drawing import Color
""".strip(),
        )
        sf.replace(
            "Rhino.UI.ShowMessageIcon.None",
            "getattr(Rhino.UI.ShowMessageIcon, 'NONE')",
        )


def utility_fixes(item):
    """Fix misc items in rhinoscript/utility.py"""
    with SourceFile(item) as sf:
        sf.replace(
            """
import Rhino
import System.Drawing.Color, System.Array, System.Guid
import time
import System.Windows.Forms.Clipboard
import scriptcontext
import math
import string
import numbers
import RhinoPython.Host as __host
""".strip(),
            """
import time
import math
import string
import numbers
import scriptcontext

import System
import Rhino
from System import Array, Guid
from System.Drawing import Color
from System.Windows.Forms import Clipboard
# import RhinoPython.Host as __host
""".strip(),
        )
        sf.replace(
            "=  __host.Coerce3dPointFromEnumerables(point)",
            "=  None # __host.Coerce3dPointFromEnumerables(point)",
        )


def view_fixes(item):
    """Fix misc items in rhinoscript/view.py"""
    with SourceFile(item) as sf:
        sf.replace(
            """
import scriptcontext
from . import utility as rhutil
import Rhino
import System.Enum
import math
""".strip(),
            """
import math
import scriptcontext
from . import utility as rhutil

import System
import Rhino
from System import Enum
""".strip(),
        )


# =============================================================================

if __name__ == "__main__":
    for item in ITEMS:
        source = op.normpath(op.join(THIS_DIR, SOURCE_DIR, item))
        dest = op.normpath(op.join(THIS_DIR, DEST_DIR, item))

        prep_dest(source, dest)
        convert_dest(dest)
        apply_dest_fixes(dest)
