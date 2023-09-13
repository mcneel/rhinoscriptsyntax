# scriptcontext module
import rhinocompat as compat

'''The Active Rhino document (Rhino.RhinoDoc in RhinoCommon) while a script
is executing. This variable is set by Rhino before the exection of every script.
'''
doc = None


'''Identifies how the script is currently executing
1 = running as standard python script
2 = running inside grasshopper component
3... potential other locations where script could be running
'''
id = 1


class __Py2StickyWrapper(dict):
    '''A dictionary of values that can be reused between execution of scripts
    '''
    def items(self):
        return list(super().items())

    def keys(self):
        return list(super().keys())

    def values(self):
        return list(super().values())

    def has_key(self, key):
        return key in super().keys()

    def viewitems(self):
        return super().items()

    def viewkeys(self):
        return super().keys()

    def viewvalues(self):
        return super().values()

    def iteritems(self):
        return super().items()

    def iterkeys(self):
        return super().keys()

    def itervalues(self):
        return super().values()


'''A dictionary of values that can be reused between execution of scripts
'''
sticky = dict()
if compat.PY3:
    sticky = __Py2StickyWrapper()


def escape_test( throw_exception=True, reset=False ):
    "Tests to see if the user has pressed the escape key"
    rc = compat.GET_HOST().EscapePressed(reset)
    if rc and throw_exception:
        raise Exception('escape key pressed')
    return rc
    

def errorhandler():
    '''
    The default error handler called by functions in the rhinoscript package.
    If you want to have your own predefined function called instead of errorhandler,
    replace the scriptcontext.errorhandler value
    '''
    return None


__executing_command = None
def localize(s):
    import Rhino
    if __executing_command is None:
        return Rhino.UI.LocalizeStringPair(s,s)
    assembly = __executing_command.PlugIn.Assembly
    l = Rhino.UI.Localization.LocalizeString(s, assembly, -1)
    return Rhino.UI.LocalizeStringPair(s,l)
