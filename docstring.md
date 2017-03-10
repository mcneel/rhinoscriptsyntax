Docstring Style Guide
===================
The RhinoScriptSyntax Python library includes [Docstrings](https://www.python.org/dev/peps/pep-0257/) that are used for generating the context help in the editor and the API documentation on the [RhinoScriptSyntax API Reference](http://developer.rhino3d.com/api/RhinoScriptSyntax/win)

Docstring source
----------------
Here are some of the influential sources for this style guide:
* [PEP 257 -- Docstring Conventions](https://www.python.org/dev/peps/pep-0257/)
* [PEP 216 -- Docstring Format Goals](https://www.python.org/dev/peps/pep-0216/#docstring-format-goals)
* [Google Style Docstrings](http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html#example-google)
* [RhinoScript API Documentation](http://4.rhino3d.com/5/rhinoscript/index.html)

Docstring example
-----------------
Here is a example function with a docstring example:

```python
def AliasMacro(alias, macro=None):
    """Returns or modifies the macro of a command alias.
    Parameters:
      alias (str): The name of an existing command alias.
      macro (str, optional): The new macro to run when the alias is executed. If omitted, the current alias macro is returned.
    Returns:
      str:  If a new macro is not specified, the existing macro if successful.
      str:  If a new macro is specified, the previous macro if successful.
      null:  None on error
    Example:
      import rhinoscriptsyntax as rs
      aliases = rs.AliasNames()
      for alias in aliases:
      print alias, " -> ", rs.AliasMacro(alias)(guid
    See Also:
      AddAlias
      AliasCount
      AliasNames
      DeleteAlias
      IsAlias
    """
    rc = Rhino.ApplicationSettings.CommandAliasList.GetMacro(alias)
    if macro:
        Rhino.ApplicationSettings.CommandAliasList.SetMacro(alias, macro)
    if rc is None: return scriptcontext.errorhandler()
    return rc
```

Sections of Dev docs:
- Description
- Parameters
- Returns
- Example
- See Also

Variable types descriptions can be abbreviated
http://pythonvisually.com/ybuild/html/primitive-data-types.html


Authors
-------
Steve Baer - https://github.com/sbaer steve@mcneel.com
Scott Davidson - https://github.com/scotttd scottd@mcneel.com
