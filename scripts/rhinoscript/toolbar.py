import Rhino

def CloseToolbarCollection(name, prompt=False):
    """Closes a currently open toolbar collection
    Parameters:
      name = name of a currently open toolbar collection
      prompt[opt] = if True, user will be prompted to save the collection file
        if it has been modified prior to closing
    Returns:
      True or False indicating success or failure
    """
    tbfile = Rhino.RhinoApp.ToolbarFiles.FindByName(name, True)
    if tbfile: return tbfile.Close(prompt)
    return False


def OpenToolbarCollection(file):
    """Opens a toolbar collection file
    Parameters:
      file = full path to the collection file
    Returns:
      Rhino-assigned name of the toolbar collection if successful
      None if not successful
    """
    tbfile = Rhino.RhinoApp.ToolbarFiles.Open(file)
    if tbfile: return tbfile.Name


def SaveToolbarCollection(name):
    """Saves an open toolbar collection to disk
    Parameters:
      name = name of a currently open toolbar file
    Returns:
      True or False indicating success or failure
    """
    tbfile = Rhino.RhinoApp.ToolbarFiles.FindByName(name, True)
    if tbfile: return tbfile.Save()
    return False


def SaveToolbarCollectionAs(name, file):
    """Saves an open toolbar collection to a different disk file
    Parameters:
      name = name of a currently open toolbar file
      file = full path to file name to save to
    Returns:
      True or False indicating success or failure
    """
    tbfile = Rhino.RhinoApp.ToolbarFiles.FindByName(name, True)
    if tbfile: return tbfile.SaveAs(file)
    return False


def ToolbarCollectionCount():
    """Returns number of currently open toolbar collections"""
    return Rhino.RhinoApp.ToolbarFiles.Count


def ToolbarCollectionNames():
    """Returns names of all currently open toolbar collections"""
    return [tbfile.Name for tbfile in Rhino.RhinoApp.ToolbarFiles]


def ToolbarCollectionPath(name):
    """Returns full path to a currently open toolbar collection file
    Parameters:
      name = name of currently open toolbar collection
    Returns:
      full path on success, None on error
    """
    tbfile = Rhino.RhinoApp.ToolbarFiles.FindByName(name, True)
    if tbfile: return tbfile.Path
