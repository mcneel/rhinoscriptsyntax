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


def HideToolbar(name, toolbar_group):
    """Hides a previously visible toolbar group in an open toolbar collection
    Parameters:
      name = name of a currently open toolbar file
      toolbar_group = name of a toolbar group to hide
    Returns:
      True or False indicating success or failure
    """
    tbfile = Rhino.RhinoApp.ToolbarFiles.FindByName(name, True)
    if tbfile:
        group = tbfile.GetGroup(toolbar_group)
        if group:
            group.Visible = False
            return True
    return False


def IsToolbar(name, toolbar, group=False):
    """Verifies a toolbar (or toolbar group) exists in an open collection file
    Parameters:
      name = name of a currently open toolbar file
      toolbar = name of a toolbar group
      group[opt] = if toolbar parameter is refering to a toolbar group
    Returns:
      True or False indicating success or failure
    """
    tbfile = Rhino.RhinoApp.ToolbarFiles.FindByName(name, True)
    if tbfile:
        if group: return tbfile.GetGroup(toolbar) != None
        return tbfile.GetToolbar(toolbar) != None
    return False


def IsToolbarCollection(file):
    """Verifies that a toolbar collection is open
    Parameters:
      file = full path to a toolbar collection file
    Returns:
      Rhino-assigned name of the toolbar collection if successful
      None if not successful
    """
    tbfile = Rhino.RhinoApp.ToolbarFiles.FindByPath(file)
    if tbfile: return tbfile.Name


def IsToolbarDocked(name, toolbar_group):
    """Verifies that a toolbar group in an open toolbar collection is visible
    Parameters:
      name = name of a currently open toolbar file
      toolbar_group = name of a toolbar group
    Returns:
      True or False indicating success or failure
      None on error
    """
    tbfile = Rhino.RhinoApp.ToolbarFiles.FindByName(name, True)
    if tbfile:
        group = tbfile.GetGroup(toolbar_group)
        if group: return group.IsDocked


def IsToolbarVisible(name, toolbar_group):
    """Verifies that a toolbar group in an open toolbar collection is visible
    Parameters:
      name = name of a currently open toolbar file
      toolbar_group = name of a toolbar group
    Returns:
      True or False indicating success or failure
      None on error
    """
    tbfile = Rhino.RhinoApp.ToolbarFiles.FindByName(name, True)
    if tbfile:
        group = tbfile.GetGroup(toolbar_group)
        if group: return group.Visible


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


def ShowToolbar(name, toolbar_group):
    """Shows a previously hidden toolbar group in an open toolbar collection
    Parameters:
      name = name of a currently open toolbar file
      toolbar_group = name of a toolbar group to show
    Returns:
      True or False indicating success or failure
    """
    tbfile = Rhino.RhinoApp.ToolbarFiles.FindByName(name, True)
    if tbfile:
        group = tbfile.GetGroup(toolbar_group)
        if group:
            group.Visible = True
            return True
    return False


def ToolbarCollectionCount():
    """Returns number of currently open toolbar collections
    Parameters:
      None
    Returns:
      the number of currently open toolbar collections
    """
    return Rhino.RhinoApp.ToolbarFiles.Count


def ToolbarCollectionNames():
    """Returns names of all currently open toolbar collections
    Parameters:
      None
    Returns:
      the names of all currently open toolbar collections
    """
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


def ToolbarCount(name, groups=False):
    """Returns the number of toolbars or groups in a currently open toolbar file
    Parameters:
      name = name of currently open toolbar collection
      groups[opt] = If true, return the number of toolbar groups in the file
    Returns:
      number of toolbars on success, None on error
    """
    tbfile = Rhino.RhinoApp.ToolbarFiles.FindByName(name, True)
    if tbfile:
        if groups: return tbfile.GroupCount
        return tbfile.ToolbarCount


def ToolbarNames(name, groups=False):
    """Returns the names of all toolbars (or toolbar groups) found in a
    currently open toolbar file
    Parameters:
      name = name of currently open toolbar collection
      groups[opt] = If true, return the names of toolbar groups in the file
    Returns:
      names of all toolbars (or toolbar groups) on success, None on error
    """
    tbfile = Rhino.RhinoApp.ToolbarFiles.FindByName(name, True)
    if tbfile:
        rc = []
        if groups:
            for i in range(tbfile.GroupCount): rc.append(tbfile.GetGroup(i).Name)
        else:
            for i in range(tbfile.ToolbarCount): rc.append(tbfile.GetToolbar(i).Name)
        return rc;
