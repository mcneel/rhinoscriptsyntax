"""Rhino script context wrapper"""

import Rhino  # pylint: disable=import-error

doc = __rhinodoc__  # pylint: disable=undefined-variable
"""Rhino.RhinoDoc: The Active Rhino document (Rhino.RhinoDoc in RhinoCommon)
while a script is executing. This variable is set by Rhino before
the exection of every script.
"""

# FIXME: bad object name
id = 1  # pylint: disable=redefined-builtin,invalid-name
"""Identifies how the script is currently executing
1 = running as standard python script
2 = running inside grasshopper component
3... potential other locations where script could be running
"""


sticky = dict()
"""A dictionary of values that can be reused between execution of scripts"""


# FIXME: deprecate function
def escape_test(throw_exception=True, reset=False):  # pylint: disable=unused-argument
    "DEPRECATE: Tests to see if the user has pressed the escape key"
    return False


def errorhandler():
    """The default error handler called by functions in the rhinoscript package.
    If you want to have your own predefined function called instead
    of errorhandler, replace the scriptcontext.errorhandler value
    """
    return None


__executing_command__ = None


# FIXME: bad argument name
def localize(s):  # pylint: disable=invalid-name
    """Localize given string"""
    if __executing_command__ is None:
        return Rhino.UI.LocalizeStringPair(s, s)
    assembly = __executing_command__.PlugIn.Assembly
    lstr = Rhino.UI.Localization.LocalizeString(s, assembly, -1)
    return Rhino.UI.LocalizeStringPair(s, lstr)
