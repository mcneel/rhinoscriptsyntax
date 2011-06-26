import Rhino
import utility as rhutil
import scriptcontext
import System.Drawing.Color
import System.Enum
import System.Array
import System.Windows.Forms
from view import __viewhelper


def BrowseForFolder(folder=None, message=None, title=None):
    """Displays the browse-for-folder dialog allowing the user to select a folder
    Parameters:
      folder[opt] = a default folder
      message[opt] = a prompt or message
      title[opt] = a dialog box title
    Returns:
      selected folder
      None on error
    """
    dlg = System.Windows.Forms.FolderBrowserDialog()
    if folder:
        if not isinstance(folder, str): folder = str(folder)
        dlg.SelectedPath = folder
    if message:
        if not isinstance(message, str): message = str(message)
        dlg.Description = message
    if dlg.ShowDialog()==System.Windows.Forms.DialogResult.OK:
        return dlg.SelectedPath
    return None


def CheckListBox(items, message=None, title=None):
    """Displays a list of items in a checkable-style list dialog box
    Parameters:
      items = a list of tuples containing a string and a boolean check state
      message[opt] = a prompt or message
      title[opt] = a dialog box title
    Returns:
      A list of tuples containing the input string in items along with their
      new boolean check value
      None on error      
    """
    checkstates = [item[1] for item in items]
    itemstrs = [str(item[0]) for item in items]
    newcheckstates = Rhino.UI.Dialogs.ShowCheckListBox(title, message, itemstrs, checkstates)
    if newcheckstates:
        rc = zip(itemstrs, newcheckstates)
        return rc
    return scriptcontext.errorhandler()


def ComboListBox(items, message=None, title=None):
    """Displays a list of items in a combo-style list box dialog.
    Parameters:
      items = a list of string
      message[opt] = a prompt of message
      title[opt] = a dialog box title
    Returns:
      The selected item if successful
      None if not successful or on error
    """
    return Rhino.UI.Dialogs.ShowComboListBox(title, message, items)


def EditBox(default_string=None, message=None, title=None):
    """Displays a dialog box prompting the user to enter a string value. The
    string value may span multiple lines
    """
    rc, text = Rhino.UI.Dialogs.ShowEditBox(title, message, default_string, True)
    return text


def GetBoolean(message, items, defaults):
    """Pauses for user input of one or more boolean values. Boolean values are
    displayed as click-able command line option toggles
    Parameters:
      message = a prompt
      items = list or tuple of options. Each option is a tuple of three strings
        element 1 = description of the boolean value. Must only consist of letters
          and numbers. (no characters like space, period, or dash
        element 2 = string identifying the false value
        element 3 = string identifying the true value
      defaults = list of boolean values used as default or starting values
    Returns:
      a list of values that represent the boolean values if successful
      None on error
    """
    go = Rhino.Input.Custom.GetOption()
    go.AcceptNothing(True)
    go.SetCommandPrompt( message )
    if type(defaults) is list or type(defaults) is tuple: pass
    else: defaults = [defaults]
    count = len(items)
    if count<1 or count!=len(defaults): return scriptcontext.errorhandler()
    toggles = []
    for i in range(count):
        initial = defaults[i]
        item = items[i]
        offVal = item[1]
        t = Rhino.Input.Custom.OptionToggle( initial, item[1], item[2] )
        toggles.append(t)
        go.AddOptionToggle(item[0], t)
    while True:
        getrc = go.Get()
        if getrc==Rhino.Input.GetResult.Option: continue
        if getrc!=Rhino.Input.GetResult.Nothing: return None
        break
    return [t.CurrentValue for t in toggles]


def GetBox(mode=0, base_point=None, prompt1=None, prompt2=None, prompt3=None):
    """Pauses for user input of a box
    Parameters:
      mode[opt] = The box selection mode.
         0 = All modes
         1 = Corner. The base rectangle is created by picking two corner points
         2 = 3-Point. The base rectangle is created by picking three points
         3 = Vertical. The base vertical rectangle is created by picking three points.
         4 = Center. The base rectangle is created by picking a center point and a corner point
      base_point[opt] = optional 3D base point
      prompt1, prompt2, prompt3 [opt] = optional prompts to set
    Returns:
      list of eight Point3d that define the corners of the box on success
      None is not successful, or on error
    """
    base_point = rhutil.coerce3dpoint(base_point)
    if base_point is None: base_point = Rhino.Geometry.Point3d.Unset
    rc, box = Rhino.Input.RhinoGet.GetBox(mode, base_point, prompt1, prompt2, prompt3)
    if rc==Rhino.Commands.Result.Success: return tuple(box.GetCorners())
    return None


def GetColor(color=[0,0,0]):
    """Displays the Rhino color picker dialog allowing the user to select an RGB color
    Parameters:
      color [opt] = a default RGB value. If omitted, the default color is black
    Returns:
      RGB tuple of three numbers on success
      None on error
    """
    color = rhutil.coercecolor(color)
    if color is None: color = System.Drawing.Color.Black
    rc, color = Rhino.Input.RhinoGet.GetColor("Select color", True, color)
    if rc==Rhino.Commands.Result.Success: return color.R, color.G, color.B
    return scriptcontext.errorhandler()


def GetInteger(message=None, number=None, minimum=None, maximum=None):
    """Pauses for user input of a whole number.
    Parameters:
      message [optional] = A prompt or message.
      number [optional] = A default whole number value.
      minimum [optional] = A minimum allowable value.
      maximum [optional] = A maximum allowable value.
    Returns:
       The whole number input by the user if successful.
       None if not successful, or on error
    """
    gi = Rhino.Input.Custom.GetInteger()
    if message: gi.SetCommandPrompt(message)
    if number is not None: gi.SetDefaultInteger(number)
    if minimum is not None: gi.SetLowerLimit(minimum, False)
    if maximum is not None: gi.SetUpperLimit(maximum, False)
    if gi.Get()!=Rhino.Input.GetResult.Number: return scriptcontext.errorhandler()
    rc = gi.Number()
    gi.Dispose()
    return rc


def GetLayer(title="Select Layer", layer=None, show_new_button=False, show_set_current=False):
    """Displays a dialog box prompting the user to select a layer
    Parameters:
      title[opt] = dialog box title
      layer[opt] = name of a layer to preseclt. If omitted, the current layer will be preselected
      show_new_button, show_set_current[opt] = Optional buttons to show on the dialog
    Returns:
      name of the selected layer if successful
      None on error
    """
    layer_index = scriptcontext.doc.Layers.CurrentLayerIndex
    if layer:
        index = scriptcontext.doc.Layers.Find(layer, True)
        if index!=-1: layer_index = index
    rc = Rhino.UI.Dialogs.ShowSelectLayerDialog(layer_index, title, show_new_button, show_set_current, True)
    if rc[0]!=System.Windows.Forms.DialogResult.OK: return None
    layer = scriptcontext.doc.Layers[rc[1]]
    return layer.Name


def GetPoint(message=None, base_point=None, distance=None, in_plane=False):
    """Pauses for user input of a point.
    Parameters:
      message [opt] = A prompt or message.
      base_point [opt] = list of 3 numbers or Point3d identifying a starting, or base point
      distance  [opt] = constraining distance. If distance is specified, basePoint must also
                        be sepcified.
      in_plane [opt] = constrains the point selections to the active construction plane.
    Returns:
      point on success
      None if no point picked or user canceled
    """
    gp = Rhino.Input.Custom.GetPoint()
    if message: gp.SetCommandPrompt(message)
    base_point = rhutil.coerce3dpoint(base_point)
    if base_point:
        gp.DrawLineFromPoint(base_point,True)
        gp.EnableDrawLineFromPoint(True)
        if distance: gp.ConstrainDistanceFromBasePoint(distance)
    if in_plane: gp.ConstrainToConstructionPlane(True)
    gp.Get()
    if gp.CommandResult()!=Rhino.Commands.Result.Success:
        return scriptcontext.errorhandler()
    pt = gp.Point()
    gp.Dispose()
    return pt


def GetPointOnCurve(curve_id, message=None):
    """Pauses for user input of a point constrainted to a curve object
    Parameters:
      curve_id = identifier of the curve to get a point on
      message [opt] = a prompt of message
    Returns:
      3d point if successful
      None on error
    """
    curve = rhutil.coercecurve(curve_id, -1, True)
    gp = Rhino.Input.Custom.GetPoint()
    if message: gp.SetCommandPrompt(message)
    gp.Constrain(curve, False)
    gp.Get()
    if gp.CommandResult()!=Rhino.Commands.Result.Success:
        return scriptcontext.errorhandler()
    pt = gp.Point()
    gp.Dispose()
    return pt


def GetPointOnMesh(mesh_id, message=None):
    """Pauses for user input of a point constrained to a mesh object
    Parameters:
      mesh_id = identifier of the mesh to get a point on
      message [opt] = a prompt or message
    Returns:
      3d point if successful
      None on error
    """
    mesh_id = rhutil.coerceguid(mesh_id, True)
    if not message: message = "Point"
    cmdrc, point = Rhino.Input.RhinoGet.GetPointOnMesh(mesh_id, message, False)
    if cmdrc==Rhino.Commands.Result.Success: return point
    return None


def GetPointOnSurface(surface_id, message=None):
    """Pauses for user input of a point constrained to a surface or polysurface
    object
    Parameters:
      surface_id = identifier of the surface to get a point on
      message [opt] = a prompt or message
    Returns:
      3d point if successful
      None on error
    """
    surfOrBrep = rhutil.coercesurface(surface_id)
    if not surfOrBrep:
        surfOrBrep = rhutil.coercebrep(surface_id, True)
    gp = Rhino.Input.Custom.GetPoint()
    if message: gp.SetCommandPrompt(message)
    if isinstance(surfOrBrep,Rhino.Geometry.Surface):
        gp.Constrain(surfOrBrep,False)
    else:
        gp.Constrain(surfOrBrep, -1, -1, False)
    gp.Get()
    if gp.CommandResult()!=Rhino.Commands.Result.Success:
        return scriptcontext.errorhandler()
    pt = gp.Point()
    gp.Dispose()
    return pt


def GetPoints(draw_lines=False, in_plane=False, message1=None, message2=None, max_points=None, base_point=None):
    """Pauses for user input of one or more points
    Parameters:
      draw_lines [opt] = Draw lines between points
      in_plane[opt] = Constrain point selection to the active construction plane
      message1[opt] = A prompt or message for the first point
      message2[opt] = A prompt or message for the next points
      max_points[opt] = maximum number of points to pick. If not specified, an
                        unlimited number of points can be picked.
      base_point[opt] = a starting or base point
    Returns:
      list of 3d points if successful
      None if not successful or on error
    """
    gp = Rhino.Input.Custom.GetPoint()
    if message1: gp.SetCommandPrompt(message1)
    gp.EnableDrawLineFromPoint( draw_lines )
    if in_plane: gp.ConstrainToConstructionPlane(True)
    getres = gp.Get()
    if gp.CommandResult()!=Rhino.Commands.Result.Success: return None
    prevPoint = gp.Point()
    rc = [prevPoint]
    if max_points is None or max_points>1:
        current_point = 1
        if message2: gp.SetCommandPrompt(message2)
        def GetPointDynamicDrawFunc( sender, args ):
            if len(rc)>1:
                c = Rhino.ApplicationSettings.AppearanceSettings.FeedbackColor
                args.Display.DrawPolyline(rc, c)
        if draw_lines: gp.DynamicDraw += GetPointDynamicDrawFunc
        while True:
            if max_points and current_point>=max_points: break
            if draw_lines: gp.DrawLineFromPoint(prevPoint, True)
            current_point += 1
            getres = gp.Get()
            if getres==Rhino.Input.GetResult.Cancel: break
            if gp.CommandResult()!=Rhino.Commands.Result.Success: return None
            prevPoint = gp.Point()
            rc.append(prevPoint)
    return rc


def GetReal(message="Number", number=None, minimum=None, maximum=None):
    """Pauses for user input of a number.
    Parameters:
      message [optional] = A prompt or message.
      number [optional] = A default number value.
      minimum [optional] = A minimum allowable value.
      maximum [optional] = A maximum allowable value.
    Returns:
       The number input by the user if successful.
       None if not successful, or on error
    """
    gn = Rhino.Input.Custom.GetNumber()
    if message: gn.SetCommandPrompt(message)
    if number is not None: gn.SetDefaultNumber(number)
    if minimum is not None: gn.SetLowerLimit(minimum, False)
    if maximum is not None: gn.SetUpperLimit(maximum, False)
    if gn.Get()!=Rhino.Input.GetResult.Number: return None
    rc = gn.Number()
    gn.Dispose()
    return rc


def GetRectangle(mode=0, base_point=None, prompt1=None, prompt2=None, prompt3=None):
    """Pauses for user input of a rectangle
    Parameters:
      mode[opt] = The rectangle selection mode. The modes are as follows
          0 = All modes
          1 = Corner - a rectangle is created by picking two corner points
          2 = 3Point - a rectangle is created by picking three points
          3 = Vertical - a vertical rectangle is created by picking three points
          4 = Center - a rectangle is created by picking a center point and a corner point
      base_point[opt] = a 3d base point
      prompt1, prompt2, prompt3 = optional prompts
    Returns:
      a tuple of four 3d points that define the corners of the rectangle
      None on error
    """
    mode = System.Enum.ToObject( Rhino.Input.GetBoxMode, mode )
    base_point = rhutil.coerce3dpoint(base_point)
    if( base_point==None ): base_point = Rhino.Geometry.Point3d.Unset
    prompts = ["", "", ""]
    if prompt1: prompts[0] = prompt1
    if prompt2: prompts[1] = prompt2
    if prompt3: prompts[2] = prompt3
    rc, corners = Rhino.Input.RhinoGet.GetRectangle(mode, base_point, prompts)
    if rc==Rhino.Commands.Result.Success: return corners
    return None


def GetString(message=None, defaultString=None, strings=None):
    """Pauses for user input of a string value
    Parameters:
      message [opt]: a prompt or message
      defaultString [opt]: a default value
      strings [opt]: list of strings to be displayed as a click-able command options.
        Note, strings cannot begin with a numeric character
    """
    gs = Rhino.Input.Custom.GetString()
    if message: gs.SetCommandPrompt(message)
    if defaultString: gs.SetDefaultString(defaultString)
    if strings:
        for s in strings: gs.AddOption(s)
    result = gs.Get()
    if( gs.CommandResult()==Rhino.Commands.Result.Success ):
        if( result == Rhino.Input.GetResult.Option ):
            return gs.Option().EnglishName
        return gs.StringResult()
    return None


def ListBox(items, message=None, title=None):
    """Displays a list of items in a list box dialog.
    Parameters:
      items = a list of string
      message [optional] = a prompt of message
      title [optional] = a dialog box title
    Returns:
      The selected item if successful
      None if not successful or on error
    """
    return Rhino.UI.Dialogs.ShowListBox(title, message, items)


def MessageBox(message, buttons=0, title=""):
    """Displays a message box. A message box contains a message and
    title, plus any combination of predefined icons and push buttons.
    Parameters:
      message = A prompt or message.
      buttons[opt] = buttons and icon to display. Can be a combination of the
        following flags. If omitted, an OK button and no icon is displayed
        0      Display OK button only.
        1      Display OK and Cancel buttons.
        2      Display Abort, Retry, and Ignore buttons.
        3      Display Yes, No, and Cancel buttons.
        4      Display Yes and No buttons.
        5      Display Retry and Cancel buttons.
        16     Display Critical Message icon.
        32     Display Warning Query icon.
        48     Display Warning Message icon.
        64     Display Information Message icon.
        0      First button is the default.
        256    Second button is the default.
        512    Third button is the default.
        768    Fourth button is the default.
        0      Application modal. The user must respond to the message box
               before continuing work in the current application.
        4096   System modal. The user must respond to the message box
               before continuing work in any application.
      title[opt] = the dialog box title
    Returns:
      A number indicating which button was clicked:
        1      OK button was clicked.
        2      Cancel button was clicked.
        3      Abort button was clicked.
        4      Retry button was clicked.
        5      Ignore button was clicked.
        6      Yes button was clicked.
        7      No button was clicked.
    """
    buttontype = buttons & 0x00000007 #111 in binary
    btn = System.Windows.Forms.MessageBoxButtons.OK
    if buttontype==1: btn = System.Windows.Forms.MessageBoxButtons.OKCancel
    elif buttontype==2: btn = System.Windows.Forms.MessageBoxButtons.AbortRetryIgnore
    elif buttontype==3: btn = System.Windows.Forms.MessageBoxButtons.YesNoCancel
    elif buttontype==4: btn = System.Windows.Forms.MessageBoxButtons.YesNo
    elif buttontype==5: btn = System.Windows.Forms.MessageBoxButtons.RetryCancel
    
    icontype = buttons & 0x00000070
    icon = System.Windows.Forms.MessageBoxIcon.None
    if icontype==16: icon = System.Windows.Forms.MessageBoxIcon.Exclamation
    elif icontype==32: icon = System.Windows.Forms.MessageBoxIcon.Question
    elif icontype==48: icon = System.Windows.Forms.MessageBoxIcon.Warning
    elif icontype==64: icon = System.Windows.Forms.MessageBoxIcon.Information
    
    defbtntype = buttons & 0x00000300
    defbtn = System.Windows.Forms.MessageBoxDefaultButton.Button1
    if defbtntype==256:
        defbtn = System.Windows.Forms.MessageBoxDefaultButton.Button2
    elif defbtntype==512:
        defbtn = System.Windows.Forms.MessageBoxDefaultButton.Button3
    if not isinstance(message, str): message = str(message)
    dlg_result = Rhino.UI.Dialogs.ShowMessageBox(message, title, btn, icon, defbtn)
    if dlg_result==System.Windows.Forms.DialogResult.OK:     return 1
    if dlg_result==System.Windows.Forms.DialogResult.Cancel: return 2
    if dlg_result==System.Windows.Forms.DialogResult.Abort:  return 3
    if dlg_result==System.Windows.Forms.DialogResult.Retry:  return 4
    if dlg_result==System.Windows.Forms.DialogResult.Ignore: return 5
    if dlg_result==System.Windows.Forms.DialogResult.Yes:    return 6
    if dlg_result==System.Windows.Forms.DialogResult.No:     return 7


def PropertyListBox(items, values, message=None, title=None):
    """Displays list of items and their values in a property-style list box dialog
    Parameters:
      items, values = list of string items and their corresponding values
      message [opt] = a prompt or message
      title [opt] = a dialog box title
    Returns:
      a list of new values on success
      None on error
    """
    values = [str(v) for v in values]
    rc = Rhino.UI.Dialogs.ShowPropertyListBox(title, message, items, values)
    return rc


def OpenFileName(title=None, filter=None, folder=None, filename=None, extension=None):
    """Displays file open dialog box allowing the user to enter a file name.
    Note, this function does not open the file.
    Parameters:
      title[opt] = A dialog box title.
      filter[opt] = A filter string. The filter must be in the following form:
        "Description1|Filter1|Description2|Filter2||", where "||" terminates filter string.
        If omitted, the filter (*.*) is used.
      folder[opt] = A default folder.
      filename[opt] = a default file name
      extension[opt] = a default file extension
    Returns:
      the file name is successful
      None if not successful, or on error
    """
    fd = Rhino.UI.OpenFileDialog()
    if title: fd.Title = title
    if filter: fd.Filter = filter
    if folder: fd.InitialDirectory = folder
    if filename: fd.FileName = filename
    if extension: fd.DefaultExt = extension
    if fd.ShowDialog()==System.Windows.Forms.DialogResult.OK: return fd.FileName


def PopupMenu(items, modes=None, point=None, view=None):
    """Displays a user defined, context-style popup menu. The popup menu can appear
    almost anywhere, and it can be dismissed by either clicking the left or right
    mouse buttons
    Parameters:
      items = list of strings representing the menu items. An empty string or None
        will create a separator
      modes[opt] = List of numbers identifying the display modes. If omitted, all
        modes are enabled.
          0 = menu item is enabled
          1 = menu item is disabled
          2 = menu item is checked
          3 = menu item is disabled and checked
      point[opt] = a 3D point where the menu item will appear. If omitted, the menu
        will appear at the current cursor position
      view[opt] = if point is specified, the view in which the point is computed.
        If omitted, the active view is used
    Returns:
      index of the menu item picked or -1 if no menu item was picked
    """
    screen_point = System.Windows.Forms.Cursor.Position
    if point:
        point = rhutil.coerce3dpoint(point)
        view = __viewhelper(view)
        viewport = view.ActiveViewport
        point2d = viewport.WorldToClient(point)
        screen_point = viewport.ClientToScreen(point2d)
    return Rhino.UI.Dialogs.ShowContextMenu(items, screen_point, modes);
            



def RealBox(message="", default_number=None, title=""):
    """Displays a dialog box prompting the user to enter a number
    Returns:
      number on success
      None on error
    """
    if default_number is None: default_number = Rhino.RhinoMath.UnsetValue
    rc, number = Rhino.UI.Dialogs.ShowNumberBox(title, message, default_number)
    if rc==System.Windows.Forms.DialogResult.OK: return number
    return None


def SaveFileName(title=None, filter=None, folder=None, filename=None, extension=None):
    """Displays a save dialog box allowing the user to enter a file name.
    Note, this function does not save the file.
    Parameters:
      title[opt] = A dialog box title.
      filter[opt] = A filter string. The filter must be in the following form:
        "Description1|Filter1|Description2|Filter2||", where "||" terminates filter string.
        If omitted, the filter (*.*) is used.
      folder[opt] = A default folder.
      filename[opt] = a default file name
      extension[opt] = a default file extension
    Returns:
      the file name is successful
      None if not successful, or on error
    """
    fd = Rhino.UI.SaveFileDialog()
    if title: fd.Title = title
    if filter: fd.Filter = filter
    if folder: fd.InitialDirectory = folder
    if filename: fd.FileName = filename
    if extension: fd.DefaultExt = extension
    if fd.ShowDialog()==System.Windows.Forms.DialogResult.OK: return fd.FileName
    return None


def StringBox(default_string=None, message=None, title=None):
    "Displays a dialog box prompting the user to enter a string value."
    rc, text = Rhino.UI.Dialogs.ShowEditBox(title, message, default_string, False)
    return text
