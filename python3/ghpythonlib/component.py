#pylint: disable=import-error,invalid-name,broad-except,superfluous-parens
"""Support functionality for active python component"""
from Grasshopper.Kernel import GH_RuntimeMessageLevel as RML
from GhPython.DocReplacement import GrasshopperDocument
from GhPython.Component import ZuiPythonComponent

import scriptcontext


def _get_active_component():
    """Return component currently being executed by Gh runtime

    Returns:
        GhPython.Component.ZuiPythonComponent:
            active python component or None if not found
    """
    if isinstance(scriptcontext.doc, GrasshopperDocument) \
            and isinstance(scriptcontext.doc.Component, ZuiPythonComponent):
        return scriptcontext.doc.Component


def _add_msg(rml, msg):
    """Show message with given rml, in Grasshopper component bubble

    Args:
        msg (str): warning message
        rml (Grasshopper.Kernel.GH_RuntimeMessageLevel): runtime message level
    """
    ghcomp = _get_active_component()
    if ghcomp:
        ghcomp.AddRuntimeMessage(rml, msg)


def add_warning(msg):
    """Show warning message in Grasshopper component bubble

    Args:
        msg (str): warning message

    Example:
        >>> import ghpythonlib as ghlib
        >>> ghlib.component.add_warning("warning message")
        ...
    """
    _add_msg(RML.Warning, msg)


def add_error(msg):
    """Show error message in Grasshopper component bubble

    Args:
        msg (str): error message

    Example:
        >>> import ghpythonlib as ghlib
        >>> ghlib.component.add_error("error message")
        ...
    """
    _add_msg(RML.Error, msg)


def add_remark(msg):
    """Show remark message in Grasshopper component bubble

    Args:
        msg (str): remark message

    Example:
        >>> import ghpythonlib as ghlib
        >>> ghlib.component.add_remark("remark message")
        ...
    """
    _add_msg(RML.Remark, msg)
