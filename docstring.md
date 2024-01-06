
Docstring Style Guide
===================
The RhinoScriptSyntax Python library includes [Docstrings](https://www.python.org/dev/peps/pep-0257/) that are used for generating the context help in the editor and the API documentation on the [RhinoScriptSyntax API Reference](http://developer.rhino3d.com/api/RhinoScriptSyntax/win)


###Docstring source
Here are some of the influential sources for this style guide:
* [PEP 257 -- Docstring Conventions](https://www.python.org/dev/peps/pep-0257/)
* [PEP 216 -- Docstring Format Goals](https://www.python.org/dev/peps/pep-0216/#docstring-format-goals)
* [Google Style Docstrings](http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html#example-google)
* [RhinoScript API Documentation](http://4.rhino3d.com/5/rhinoscript/index.html)

###Docstring Format Goals

These are the goals for the docstring format:

1. It must be easy to type with any standard text editor.
2. It must be readable to the casual observer.
3. It must not contain information which can be deduced from parsing the module.
4. It must contain sufficient information so it can be converted to any reasonable markup format.
5. It must be possible to write a module's entire documentation in docstrings, without feeling hampered by the markup language.

Format goals section found from: [PEP 216 -- Docstring Format Goals](https://www.python.org/dev/peps/pep-0216/#docstring-format-goals)




Docstring examples
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
      print("{} -> {}".format(alias, rs.AliasMacro(alias)))
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
Sections of Dev docstrings:
- Delimiters
- Description
- Parameters
- Returns
- Example
- See Also

### Delimeters

After the function name, the delimiter `"""` is used to denote the start of a doc string. The end of the docstring section is also denoted by a `"""`.

### Description

A short description of the function and any notes that might make it unusual.  For a multi-line description, the second line and below need to be indented with two spaces.

### Parameters

Starts with a line `Parameters:`

If there are no parameters to pass to the function, the section should be removed completely.

A parameter line consists of:

1. The variable name
2. Variable type in parenthesis ().
3. Description of variable and conditions.

A simple example:

```
     alias (str): The name of an existing command alias.
```

How variable are described is as follows:

```python
#A simple string:
alias (str): The name of an existing command alias.

#A list of values of the same type and unlimited number:
alias ([str, ...]): The name of an existing command alias.

#A list of values of different types:
alias ([str, number, bool]): list of an existing command alias.

#Nested lists in a param may look like this:
alias ([str, [number, number], bool]): list of values for command alias.
    
#Use the pipe to denote differnet types "|", meaning "or"
alias (str|guid): The name or guid identifier of an existing command alias.
    
#Add ", optional" for optional parameters.
alias (str, optional): The name of an existing command alias. If omitted, None is returned.
```

For optional params, it is helpful to put a "if omitted ..." phrase that explains the default value.

###Returns

The next section starts with `Returns:` 

Unlike Parameters, functions that return `None` still need to be listed as follows:

```python
Returns:
    None
```

A normal return line will contain:

1. Return Data Type
2. Description

```python
#A simple string:
str: The name of an existing command alias.

#list of values of the same type and unlimited number:
list(str, ...): A list of alias.

#A list of values of different types:
list(str, number, bool): Various information about command alias.
    
#For different return values use multiple lines:
str: The name of an existing command alias.
number: If no argument, returns number of aliases.
None: If not successful
    
# If a number is returned that refers to a code
1 = counter clockwise
0 = stationary
-1 = clockwise

# For index numbers returned
[0] point for origin
[1] area of surface
[2] point of center
```

Use the `None` keyword if that is returned on an error.

### Example

Start the section with `Example:` .  The following lines should be indented two spaces.

The goal with the Examples is to make them self-contained and functional with a simple copy and paste into an empty script.  This allows the sample to be run.  To that end, most Examples will require the rhinoscriptsyntax import line: 

```python
import rhinoscriptsyntax as rs
```

The rest of the sample will contain the input functions to and the example function name.

If optional arguments can be used, that is best.

A example should no need a separate 3DM file or another support file to run.

### Variable Name Abbreviation

Variable types descriptions can be abbreviated according to this chart:
http://pythonvisually.com/ybuild/html/primitive-data-types.html

Specifically for RhinoScript Sytnax use these:

| Abbreviation | Types                   |
| ------------ | ----------------------- |
| number       | float, integer, long    |
| str          | string                  |
| bool         | boolean                 |
| list         | list                    |
| tuple        | tuple                   |
| guid         | uuid, object identifier |
| point        | rhino.geometry.point3d  |
| plane        | rhino.geometry.plane3d  |
| line         | rhino.geometry.line     |
| color        | system.drawing.color    |




Authors
-------
Steve Baer - https://github.com/sbaer steve@mcneel.com
Scott Davidson - https://github.com/scotttd scottd@mcneel.com
