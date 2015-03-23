# scriptcontext module
import RhinoPython.Host as __host

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


'''A dictionary of values that can be reused between execution of scripts
'''
sticky = dict()

def escape_test( throw_exception=True, reset=False ):
    "Tests to see if the user has pressed the escape key"
    rc = __host.EscapePressed(reset)
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
