import scriptcontext
import Rhino
import Rhino.ApplicationSettings.ModelAidSettings as modelaid
import Rhino.Commands.Command as rhcommand
import System.TimeSpan, System.Enum, System.Environment
import System.Windows.Forms.Screen
import datetime
import utility as rhutil


def AddAlias(alias, macro):
    """Add new command alias to Rhino. Command aliases can be added manually by
    using Rhino's Options command and modifying the contents of the Aliases tab.
    Parameters:
      alias = name of new command alias. Cannot match command names or existing
              aliases.
      macro = The macro to run when the alias is executed.
    Returns:
      True or False indicating success or failure.
    Example:
      import rhinoscriptsyntax as  rs
      rs.AddAlias("OriginLine",  "!_Line 0,0,0")
    See Also:
      AliasCount
      AliasMacro
      AliasNames
      DeleteAlias
      IsAlias
    """
    return Rhino.ApplicationSettings.CommandAliasList.Add(alias, macro)


def AddSearchPath(folder, index=-1):
    """Add new path to Rhino's search path list. Search paths can be added by
    using Rhino's Options command and modifying the contents of the files tab.
    Parameters:
      folder = A valid folder, or path, to add.
      index [opt] = Zero-based position in the search path list to insert.
                    If omitted, path will be appended to the end of the
                    search path list.
    Returns:
      The index where the item was inserted if success.
      -1 on failure.
    Example:
      import rhinoscriptsyntax as rs
      rs.AddSearchPath("C:\\My Python Scripts")
    See Also:
      DeleteSearchPath
      SearchPathCount
      SearchPathList
    """
    return Rhino.ApplicationSettings.FileSettings.AddSearchPath(folder, index)


def AliasCount():
    """Returns number of command aliases in Rhino.
    Parameters:
      None
    Returns:
      the number of command aliases in Rhino.
    Example:
      import rhinoscriptsyntax as rs
      print "alias count = ", rs.AliasCount()
    See Also:
      AddAlias
      AliasMacro
      AliasNames
      DeleteAlias
      IsAlias
    """
    return Rhino.ApplicationSettings.CommandAliasList.Count


def AliasMacro(alias, macro=None):
    """Returns or modifies the macro of a command alias.
    Parameters:
      alias = The name of an existing command alias.
      macro [opt] = The new macro to run when the alias is executed.
    Returns:
      If a new macro is not specified, the existing macro if successful.
      If a new macro is specified, the previous macro if successful.
      None on error
    Example:
      import rhinoscriptsyntax as rs
      aliases = rs.AliasNames()
      for alias in aliases:
      print alias, " -> ", rs.AliasMacro(alias)
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


def AliasNames():
    """Returns a list of command alias names.
    Parameters:
      None
    Returns:
      a list of command alias names.
    Example:
      import rhinoscriptsyntax as rs
      aliases = rs.AliasNames()
      for alias in aliases: print alias
    See Also:
      AddAlias
      AliasCount
      AliasMacro
      DeleteAlias
      IsAlias
    """
    return Rhino.ApplicationSettings.CommandAliasList.GetNames()


def AppearanceColor(item, color=None):
    """Returns or modifies an application interface item's color.
    Parameters:
      item = Item number to either query or modify
             0  = View background
             1  = Major grid line
             2  = Minor grid line
             3  = X-Axis line
             4  = Y-Axis line
             5  = Selected Objects
             6  = Locked Objects
             7  = New layers
             8  = Feedback
             9  = Tracking
             10 = Crosshair
             11 = Text
             12 = Text Background
             13 = Text hover
      color[opt] = The new color value
    Returns:
      if color is not specified, the current item color
      if color is specified, the previous item color
    Example:
      import rhinoscriptsyntax as rs
      oldColor = rs.AppearanceColor(0)
      newColor = rs.GetColor(oldColor)
      if newColor is not None:
      rs.AppearanceColor(0, newColor)
      rs.Redraw()
    See Also:
      GetColor
    """
    rc = None
    color = rhutil.coercecolor(color)
    appearance = Rhino.ApplicationSettings.AppearanceSettings
    if item==0:
        rc = appearance.ViewportBackgroundColor
        if color: appearance.ViewportBackgroundColor = color
    elif item==1:
        rc = appearance.GridThickLineColor
        if color: appearance.GridThickLineColor = color
    elif item==2:
        rc = appearance.GridThinLineColor
        if color: appearance.GridThinLineColor = color
    elif item==3:
        rc = appearance.GridXAxisLineColor
        if color: appearance.GridXAxisLineColor = color
    elif item==4:
        rc = appearance.GridYAxisLineColor
        if color: appearance.GridYAxisLineColor = color
    elif item==5:
        rc = appearance.SelectedObjectColor
        if color: appearance.SelectedObjectColor = color
    elif item==6:
        rc = appearance.LockedObjectColor
        if color: appearance.LockedObjectColor = color
    elif item==7:
        rc = appearance.DefaultLayerColor
        if color: appearance.DefaultLayerColor = color
    elif item==8:
        rc = appearance.FeedbackColor
        if color: appearance.FeedbackColor = color
    elif item==9:
        rc = appearance.TrackingColor
        if color: appearance.TrackingColor = color
    elif item==10:
        rc = appearance.CrosshairColor
        if color: appearance.CrosshairColor = color
    elif item==11:
        rc = appearance.CommandPromptTextColor
        if color: appearance.CommandPromptTextColor = color
    elif item==12:
        rc = appearance.CommandPromptBackgroundColor
        if color: appearance.CommandPromptBackgroundColor = color
    elif item==13:
        rc = appearance.CommandPromptHypertextColor
        if color: appearance.CommandPromptHypertextColor = color
    if rc is None: raise ValueError("item is out of range")
    scriptcontext.doc.Views.Redraw()
    return rc


def AutosaveFile(filename=None):
    """Returns or changes the file name used by Rhino's automatic file saving
    Parameters:
      filename [opt] = name of the new autosave file
    Returns:
      if filename is not specified, the name of the current autosave file
      if filename is specified, the name of the previous autosave file
    Example:
      import rhinoscriptsyntax as rs
      file = rs.AutosaveFile()
      print "The current autosave file is", file
    See Also:
      AutosaveInterval
      EnableAutosave
    """
    rc = Rhino.ApplicationSettings.FileSettings.AutosaveFile
    if filename: Rhino.ApplicationSettings.FileSettings.AutosaveFile = filename
    return rc


def AutosaveInterval(minutes=None):
    """Returns or changes how often the document will be saved when Rhino's
    automatic file saving mechanism is enabled
    Parameters:
      minutes [opt] = the number of minutes between saves
    Returns:
      if minutes is not specified, the current interval in minutes
      if minutes is specified, the previous interval in minutes
    Example:
      import rhinoscriptsyntax as rs
      minutes = rs.AutosaveInterval()
      if minutes>20: rs.AutosaveInterval(20)
    See Also:
      AutosaveFile
      EnableAutosave
    """
    rc = Rhino.ApplicationSettings.FileSettings.AutosaveInterval.TotalMinutes
    if minutes:
        timespan = System.TimeSpan.FromMinutes(minutes)
        Rhino.ApplicationSettings.FileSettings.AutosaveInterval = timespan
    return rc


def BuildDate():
    """Returns the build date of Rhino
    Parameters:
      None
    Returns:
      the build date of Rhino
    Example:
      import rhinoscriptsyntax as rs
      build = rs.BuildDate()
      print "Rhino Build:", build
    See Also:
      
    """
    build = Rhino.RhinoApp.BuildDate
    return datetime.date(build.Year, build.Month, build.Day)


def ClearCommandHistory():
    """Clears contents of Rhino's command history window. You can view the
    command history window by using the CommandHistory command in Rhino.
    Parameters:
      None
    Returns:
      None
    Example:
      import rhinoscriptsyntax as rs
      rs.ClearCommandHistory()
    See Also:
      CommandHistory
    """
    Rhino.RhinoApp.ClearCommandHistoryWindow()


__command_serial_numbers = None

def Command(commandString, echo=True):
    """Runs a Rhino command script. All Rhino commands can be used in command
    scripts. The command can be a built-in Rhino command or one provided by a
    3rd party plug-in.
    Parameters:
      commandString = a Rhino command including any arguments
      echo[opt] = the command echo mode
    Returns:
      True or False indicating success or failure

    Write command scripts just as you would type the command sequence at the
    command line. A space or a new line acts like pressing <Enter> at the
    command line. For more information, see "Scripting" in Rhino help.

    Note, this function is designed to run one command and one command only.
    Do not combine multiple Rhino commands into a single call to this method.
      WRONG:
        rs.Command("_Line _SelLast _Invert")
      CORRECT:
        rs.Command("_Line")
        rs.Command("_SelLast")
        rs.Command("_Invert")

    Also, the exclamation point and space character ( ! ) combination used by
    button macros and batch-driven scripts to cancel the previous command is
    not valid.
      WRONG:
        rs.Command("! _Line _Pause _Pause")
      CORRECT:
        rs.Command("_Line _Pause _Pause")
    After the command script has run, you can obtain the identifiers of most
    recently created or changed object by calling LastCreatedObjects.
    Example:
      import rhinoscriptsyntax as rs
      rs.Command("_Line 0,0,0 2,2,2")
      rs.Command("_Line _Pause _Pause")
    See Also:
      IsCommand
      LastCommandName
      LastCommandResult
      LastCreatedObjects
      Prompt
    """
    start = Rhino.DocObjects.RhinoObject.NextRuntimeSerialNumber
    rc = Rhino.RhinoApp.RunScript(commandString, echo)
    end = Rhino.DocObjects.RhinoObject.NextRuntimeSerialNumber
    global __command_serial_numbers
    __command_serial_numbers = None
    if start!=end: __command_serial_numbers = (start,end)
    return rc


def CommandHistory():
    """Returns the contents of Rhino's command history window
    Parameters:
      None
    Returns:
      the contents of Rhino's command history window
    Example:
      import rhinoscriptsyntax as rs
      print rs.CommandHistory()
    See Also:
      ClearCommandHistory
    """
    return Rhino.RhinoApp.CommandHistoryWindowText


def DefaultRenderer(renderer=None):
    """Returns or changes the default render plug-in
    Parameters:
      renderer [opt] = the name of the renderer to set as default renderer
    Returns:
      uuid of default renderer
    Example:
      import rhinoscriptsyntax as rs
      rs.DefaultRenderer("MyRenderPlugIn")
    See Also:
      PlugIns
    """
    id = Rhino.Render.Utilities.DefaultRenderPlugInId
    plugins = Rhino.PlugIns.PlugIn.GetInstalledPlugIns()
    rc = plugins[id]
    if renderer:
        id = Rhino.PlugIns.PlugIn.IdFromName(renderer)
        Rhino.Render.Utilities.SetDefaultRenderPlugIn(id)
    return rc


def DeleteAlias(alias):
    """Delete an existing alias from Rhino.
    Parameters:
      alias = the name of an existing alias
    Returns:
      True or False indicating success
    Example:
      import rhinoscriptsyntax as rs
      print rs.DeleteAlias("Hello")
    See Also:
      AddAlias
      AliasCount
      AliasMacro
      AliasNames
      IsAlias
    """
    return Rhino.ApplicationSettings.CommandAliasList.Delete(alias)


def DeleteSearchPath(folder):
    """Removes existing path from Rhino's search path list. Search path items
    can be removed manually by using Rhino's options command and modifying the
    contents of the files tab
    Parameters:
      folder = a folder to remove
    Returns:
      True or False indicating success
    Example:
      import rhinoscriptsyntax as rs
      rs.DeleteSearchPath("C:\\My RhinoScripts")
    See Also:
      AddSearchPath
      SearchPathCount
      SearchPathList
    """
    return Rhino.ApplicationSettings.FileSettings.DeleteSearchPath(folder)


def DisplayOleAlerts( enable ):
    """Enables/disables OLE Server Busy/Not Responding dialog boxes
    Parameters:
      enable = whether alerts should be visible (True or False)
    Returns:
      None
    Example:
      import System
      import rhinoscriptsyntax as rs
      rs.DisplayOleAlerts( False )
      t = System.Type.GetTypeFromProgID("Excel.Application")
      objExcel = System.Activator.CreateObject(t)
      ...
    See Also:
      
    """
    Rhino.Runtime.HostUtils.DisplayOleAlerts( enable )


def EdgeAnalysisColor(color=None):
    """Returns or modifies edge analysis color displayed by the ShowEdges command
    Parameters:
      color [opt] = the new color
    Returns:
      if color is not specified, the current edge analysis color
      if color is specified, the previous edge analysis color
    Example:
      import rhinoscriptsyntax as rs
      oldcolor = rs.EdgeAnalysisColor()
      newcolor = rs.GetColor(oldcolor)
      if newcolor is not None:
      rs.EdgeAnalysisColor(newcolor)
    See Also:
      EdgeAnalysisMode
    """
    rc = Rhino.ApplicationSettings.EdgeAnalysisSettings.ShowEdgeColor
    if color:
        color = rhutil.coercecolor(color, True)
        Rhino.ApplicationSettings.EdgeAnalysisSettings.ShowEdgeColor = color
    return rc


def EdgeAnalysisMode(mode=None):
    """Returns or modifies edge analysis mode displayed by the ShowEdges command
    Parameters:
      mode [opt] = the new display mode. The available modes are
                   0 - display all edges
                   1 - display naked edges
    Returns:
      if mode is not specified, the current edge analysis mode
      if mode is specified, the previous edge analysis mode
    Example:
      import rhinoscriptsyntax as rs
      previous_mode = rs.EdgeAnalysisMode(1)
    See Also:
      EdgeAnalysisColor
    """
    rc = Rhino.ApplicationSettings.EdgeAnalysisSettings.ShowEdges
    if mode==1 or mode==2:
        Rhino.ApplicationSettings.EdgeAnalysisSettings.ShowEdges = mode
    return rc


def EnableAutosave(enable=True):
    """Enables or disables Rhino's automatic file saving mechanism
    Parameters:
      enable = the autosave state
    Returns:
      the previous autosave state
    Example:
      import rhinoscriptsyntax as rs
      prevstate = rs.EnableAutosave()
    See Also:
      AutosaveFile
      AutosaveInterval
    """
    rc = Rhino.ApplicationSettings.FileSettings.AutoSaveEnabled
    if rc!=enable: Rhino.ApplicationSettings.FileSettings.AutoSaveEnabled = enable
    return rc


def EnablePlugIn(plugin, enable=None):
    """Enables or disables a Rhino plug-in
      Parameters:
        plugin = id of the plugin
        enable [opt] = load silently if True
      Returns:
        True if set to load silently otherwise False
      Example:
        import rhinoscriptsyntax as rs
        print rs.EnablePlugIn("RhinoCrasher", False)
      See Also:
        IsPlugIn
        PlugInId
        PlugIns
    """
    id = rhutil.coerceguid(plugin)
    if not id: id = Rhino.PlugIns.PlugIn.IdFromName(plugin)
    rc, loadSilent = Rhino.PlugIns.PlugIn.GetLoadProtection(id)
    if enable is not None:
        Rhino.PlugIns.PlugIn.SetLoadProtection(id, enable)
    return loadSilent


def ExeFolder():
    """Returns the full path to Rhino's executable folder.
    Parameters:
      None
    Returns:
      the full path to Rhino's executable folder.
    Example:
      import rhinoscriptsyntax as rs
      folder = rs.ExeFolder()
      print folder
    See Also:
      InstallFolder
    """
    return Rhino.ApplicationSettings.FileSettings.ExecutableFolder


def ExePlatform():
    """Returns the platform of the Rhino executable
    Parameters:
      None
    Returns:
      the platform of the Rhino executable
    Example:
      import rhinoscriptsyntax as rs
      if rs.ExePlatform() == 1:
      print "You are using a 64-bit version of Rhino."
      else:
      print "You are using a 32-bit version of Rhino."
    See Also:
      BuildDate
      ExeVersion
      SdkVersion
    """
    if System.Environment.Is64BitProcess: return 1
    return 0


def ExeServiceRelease():
    """Returns the service release number of the Rhino executable
    Parameters:
      None
    Returns:
      the service release number of the Rhino executable
    Example:
      import rhinoscriptsyntax as rs
      print "Build date:", rs.BuildDate()
      print "SDK Version:", rs.SdkVersion()
      print "SDK Service Release:", rs.SdkServiceRelease()
      print "Executable Version:", rs.ExeVersion()
      print "Executable Service Release:", rs.ExeServiceRelease()
      print "Serial Number:", rs.SerialNumber()
      print "Node Type:", rs.NodeType()
      print "Install Type:", rs.InstallType()
    See Also:
      BuildDate
      ExeVersion
      SdkVersion
    """
    return Rhino.RhinoApp.ExeServiceRelease


def ExeVersion():
    """Returns the major version number of the Rhino executable
    Parameters:
      None
    Returns:
      the major version number of the Rhino executable
    Example:
      import rhinoscriptsyntax as rs
      print "Build date:", rs.BuildDate()
      print "SDK Version:", rs.SdkVersion()
      print "SDK Service Release:", rs.SdkServiceRelease()
      print "Executable Version:", rs.ExeVersion()
      print "Executable Service Release:", rs.ExeServiceRelease()
      print "Serial Number:", rs.SerialNumber()
      print "Node Type:", rs.NodeType()
      print "Install Type:", rs.InstallType()
    See Also:
      BuildDate
      ExeServiceRelease
      SdkVersion
    """
    return Rhino.RhinoApp.ExeVersion


def Exit():
    """Closes the rhino application
    Parameters:
      None
    Returns:
      None
    Example:
      import rhinoscriptsyntax as rs
      rs.Exit()
    See Also:
      
    """
    Rhino.RhinoApp.Exit()


def FindFile(filename):
    """Searches for a file using Rhino's search path. Rhino will look for a
    file in the following locations:
      1. The current document's folder.
      2. Folder's specified in Options dialog, File tab.
      3. Rhino's System folders
    Parameters:
      filename = short file name to search for
    Returns:
      full path on success
    Example:
      import rhinoscriptsyntax as rs
      path = rs.FindFile("Rhino.exe")
      print path
    See Also:
      
    """
    return Rhino.ApplicationSettings.FileSettings.FindFile(filename)


def GetPlugInObject(plug_in):
    """Returns a scriptable object from a specified plug-in. Not all plug-ins
    contain scriptable objects. Check with the manufacturer of your plug-in
    to see if they support this capability.
    Parameters:
      plug_in = name or Id of a registered plug-in that supports scripting.
                If the plug-in is registered but not loaded, it will be loaded
    Returns:
      scriptable object if successful
      None on error
    Example:
      import rhinoscriptsyntax as rs
      objPlugIn = rs.GetPlugInObject("SomePlugIn")
      if objPlugIn is not None:
      print objPlugIn.About()
    See Also:
      
    """
    return Rhino.RhinoApp.GetPlugInObject(plug_in)


def InCommand(ignore_runners=True):
    """Determines if Rhino is currently running a command. Because Rhino allows
    for transparent commands (commands run from inside of other commands), this
    method returns the total number of active commands.
    Parameters:
      ignore_runners [opt] = If true, script running commands, such as
          LoadScript, RunScript, and ReadCommandFile will not counted.
    Returns:
      the number of active commands
    Example:
      import rhinoscriptsyntax as rs
      commands = rs.InCommand()
      if commands > 0:
      print "Rhino is running", commands, "command(s)."
      else:
      print "Rhino is not running any command(s)."
    See Also:
      Command
      IsCommand
    """
    ids = rhcommand.GetCommandStack()
    return len(ids)


def InstallFolder():
    """The full path to Rhino's installation folder
    Parameters:
      None
    Returns:
      the full path to Rhino's installation folder
    Example:
      import rhinoscriptsyntax as rs
      print rs.InstallFolder()
    See Also:
      ExeFolder
    """
    return Rhino.ApplicationSettings.FileSettings.InstallFolder


def IsAlias(alias):
    """Verifies that a command alias exists in Rhino
    Parameters:
      alias = the name of an existing command alias
    Returns:
      True or False
    Example:
      import rhinoscriptsyntax as rs
      print rs.IsAlias("Hello")
    See Also:
      AddAlias
      AliasCount
      AliasMacro
      AliasNames
      DeleteAlias
    """
    return Rhino.ApplicationSettings.CommandAliasList.IsAlias(alias)


def IsCommand(command_name):
    """Verifies that a command exists in Rhino. Useful when scripting commands
    found in 3rd party plug-ins.
    Parameters:
      command_name = the command name to test
    Returns:
      True of False
    Example:
      import rhinoscriptsyntax as rs
      GetString("Command name to test")
      if cmdname is not None:
      iscmd = rs.IsCommand(cmdname)
      if iscmd:
      print "The", cmdname, "command exists."
      else:
      print "The", cmdname, "command does not exist."
    See Also:
      Command
      InCommand
    """
    return rhcommand.IsCommand(command_name)


def IsPlugIn(plugin):
    """Verifies that a plug-in is registered
    Parameters:
      plugin = id of the plug-in
    Returns:
      True or False
    Example:
      import rhinoscriptsyntax as rs
      plugin = rs.GetString("Plug-in name")
    See Also:
      EnablePlugIn
      PlugInId
      PlugIns
    """
    id = rhutil.coerceguid(plugin)
    if not id: id = Rhino.PlugIns.PlugIn.IdFromName(plugin)
    if id:
        rc, loaded, loadprot = Rhino.PlugIns.PlugIn.PlugInExists(id)
        return rc


def IsRunningOnWindows():
    """Returns True if this script is being executed on a Windows platform
    Parameters:
      None
    Returns:
      True or False
    Example:
      import rhinoscriptsyntax as rs
      if rs.IsRunngingOnWindows():
      print "Running on Windows"
      else:
      print "Running on Mac"
    See Also:
      
    """
    return Rhino.Runtime.HostUtils.RunningOnWindows


def LastCommandName():
    """Returns the name of the last executed command
    Parameters:
      None
    Returns:
      the name of the last executed command
    Example:
      import rhinoscriptsyntax as rs
      rs.Command( "Line" )
      print "The last command was the", rs.LastCommandName(), "command."
    See Also:
      Command
      IsCommand
      LastCommandResult
    """
    id = rhcommand.LastCommandId
    return rhcommand.LookupCommandName(id, True)


def LastCommandResult():
    """Returns the result code for the last executed command
    0 = success (command successfully completed)
    1 = cancel (command was cancelled by the user)
    2 = nothing (command did nothing, but was not cancelled)
    3 = failure (command failed due to bad input, computational problem...)
    4 = unknown command (the command was not found)
    Parameters:
      None
    Returns:
      the result code for the last executed command
    Example:
      import rhinoscriptsyntax as rs
      rs.Command( "Line" )
      result = rs.LastCommandResult()
      if result==0:
      print "The command completed."
      else:
      print "The command did not complete."
    See Also:
      Command
      IsCommand
      LastCommandName
    """
    return int(rhcommand.LastCommandResult)


def LocaleID():
    """Returns the current language used for the Rhino interface.  The current
    language is returned as a locale ID, or LCID, value.
      1029  Czech
      1031  German-Germany
      1033  English-United States
      1034  Spanish-Spain
      1036  French-France
      1040  Italian-Italy
      1041  Japanese
      1042  Korean
      1045  Polish
    Parameters:
      None
    Returns:
      the current language used fro the Rhino interface as a locale ID, or LCID.
    Example:
      import rhinoscriptsyntax as rs
      lcid = rs.LocaleID()
      if lcid==1029:
      print "message in Czech"
      elif lcid==1031:
      print "message in German"
      elif lcid==1033:
      print "message in English"
      elif lcid==1034:
      print "message in Spanish"
      elif lcid==1036:
      print "message in Italian"
      elif lcid==1040:
      print "message in Japanese"
      elif lcid==1042:
      print "message in Korean"
      elif lcid==1045:
      print "message in Polish"
    See Also:
      
    """
    return Rhino.ApplicationSettings.AppearanceSettings.LanguageIdentifier


def Ortho(enable=None):
    """Enables or disables Rhino's ortho modeling aid.
    Parameters:
      enable [opt] = the new enabled status (True or False)
    Returns:
      if enable is not specified, then the current ortho status
      if enable is secified, then the previous ortho status
    Example:
      import rhinoscriptsyntax as rs
      if not rs.Ortho(): rs.Ortho(True)
    See Also:
      Osnap
      Planar
      Snap
    """
    rc = modelaid.Ortho
    if enable!=None: modelaid.Ortho = enable
    return rc


def Osnap(enable=None):
    """Enables or disables Rhino's object snap modeling aid.
    Object snaps are tools for specifying points on existing objects.
    Parameters:
      enable [opt] = the new enabled status (True or False)
    Returns:
      if enable is not specified, then the current osnap status
      if enable is secified, then the previous osnap status
    Example:
      import rhinoscriptsyntax as rs
      if not rs.Osnap(): rs.Osnap(True)
    See Also:
      Ortho
      OsnapMode
      Planar
      Snap
    """
    rc = modelaid.Osnap
    if enable!=None: modelaid.Osnap = enable
    return rc


def OsnapDialog(visible=None):
    """Shows or hides Rhino's dockable object snap bar
    Parameters:
      visible [opt] = the new visibility state (True or False)
    Returns:
      if visible is not specified, then the current visible state
      if visible is secified, then the previous visible state
    Example:
      import rhinoscriptsyntax as rs
      if not rs.OsnapDialog(): rs.OsnapDialog(True)
    See Also:
      Osnap
      OsnapMode
      ProjectOsnaps
    """
    rc = modelaid.UseHorizontalDialog
    if visible is not None: modelaid.UseHorizontalDialog = visible
    return rc


def OsnapMode(mode=None):
    """Returns or sets the object snap mode. Object snaps are tools for
    specifying points on existing objects
    Parameters:
      mode [opt] = The object snap mode or modes to set. Object snap modes
                   can be added together to set multiple modes
                   0     None
                   1     Near
                   2     Focus
                   4     Center
                   8     Knot
                   16    Quadrant
                   32    Midpoint
                   64    Intersection
                   128   End
                   256   Perpendicular
                   512   Tangent
                   1024  Point
                   2048  Vertex
    Returns:
      if mode is not specified, then the current object snap mode(s)
      if mode is specified, then the previous object snap mode(s)
    Example:
      import rhinoscriptsyntax as rs
      rhOsnapModeEnd = 128
      mode = rs.OsnapMode()
      if not (mode & rhOSnapModeEnd):
      mode = mode + rhOsnapModeEnd
      rs.OsnapMode(mode)
    See Also:
      Osnap
      OsnapDialog
      ProjectOsnaps
    """
    rc = int(modelaid.OsnapModes)
    m = [(0,0), (1,2), (2,8), (4,0x20), (8,0x80), (16,0x200), (32,0x800), (64,0x2000),
          (128,0x20000), (256,0x80000), (512,0x200000), (1024,0x8000000), (2048, 0x40)]
    rc = sum([x[0] for x in m if x[1] & rc])
    if mode is not None:
        mode = sum([x[1] for x in m if x[0] & int(mode)])
        modelaid.OsnapModes = System.Enum.ToObject(Rhino.ApplicationSettings.OsnapModes, mode)
    return rc

def Planar(enable=None):
    """Enables or disables Rhino's planar modeling aid
    Parameters:
      enable = the new enable status (True or False)
    Returns:
      if enable is not specified, then the current planar status
      if enable is secified, then the previous planar status
    Example:
      import rhinoscriptsyntax as rs
      if not rs.Planar(): rs.Planar(True)
    See Also:
      Ortho
      Osnap
      Snap
    """
    rc = modelaid.Planar
    if enable is not None: modelaid.Planar = enable
    return rc


def PlugInId(plugin):
    """Returns the identifier of a plug-in given the plug-in name
    Parameters:
      plugin = name of the plug-in
    Returns:
      the id of the plug-in or None if the plug-in isn't valid
    Example:
      import rhinoscriptsyntax as rs
      plugins = rs.PlugIns(0, 1)
      if plugins:
    See Also:
      EnablePlugIn
      IsPlugIn
      PlugIns
    """
    id = Rhino.PlugIns.PlugIn.IdFromName(plugin)
    if id!=System.Guid.Empty: return id


def PlugIns(types=0, status=0):
    """Returns a list of registered Rhino plug-ins
    Parameters:
      types [opt] = type of plug-ins to return. 0=all, 1=render, 2=file export,
        4=file import, 8=digitizer, 16=utility
      status [opt] = 0=both loaded and unloaded, 1=loaded, 2=unloaded
    Returns:
      list of registered Rhino plug-ins
    Example:
      import rhinoscriptsyntax as rs
      plugins = rs.PlugIns(0, 1)
    See Also:
      
    """
    filter = Rhino.PlugIns.PlugInType.None
    if types&1: filter |= Rhino.PlugIns.PlugInType.Render
    if types&2: filter |= Rhino.PlugIns.PlugInType.FileExport
    if types&4: filter |= Rhino.PlugIns.PlugInType.FileImport
    if types&8: filter |= Rhino.PlugIns.PlugInType.Digitiger
    if types&16: filter |= Rhino.PlugIns.PlugInType.Utility
    if types==0: filter = Rhino.PlugIns.PlugInType.Any
    loaded = (status==0 or status==1)
    unloaded = (status==0 or status==2)
    names = Rhino.PlugIns.PlugIn.GetInstalledPlugInNames(filter, loaded, unloaded)
    return list(names)


def ProjectOsnaps(enable=None):
    """Enables or disables object snap projection
    Parameters:
      enable [opt] = the new enabled status (True or False)
    Returns:
      if enable is not specified, the current object snap projection status
      if enable is specified, the previous object snap projection status
    Example:
      import rhinoscriptsyntax as rs
      if not rs.ProjectOsnaps(): rs.ProjectOsnaps(True)
    See Also:
      Osnap
      OsnapDialog
      OsnapMode
    """
    rc = modelaid.ProjectSnapToCPlane
    if enable is not None: modelaid.ProjectSnapToCPlane = enable
    return rc


def Prompt(message=None):
    """Change Rhino's command window prompt
    Parameters:
      message [opt] = the new prompt
    Returns:
      None
    Example:
      import rhinoscriptsyntax as rs
      rs.Prompt("Hello Rhino!")
    See Also:
      Command
    """
    if message and type(message) is not str:
        strList = [str(item) for item in message]
        message = "".join(strList)
    Rhino.RhinoApp.SetCommandPrompt(message)


def ScreenSize():
    """Returns current width and height, of the screen of the primary monitor.
    Parameters:
      None
    Returns:
      Tuple containing two numbers identifying the width and height
    Example:
      import rhinoscriptsyntax as rs
      size = rs.ScreenSize()
      print "Screen Width:", size[0], "pixels"
      print "Screen Height:", size[1], "pixels"
    See Also:
      
    """
    sz = System.Windows.Forms.Screen.PrimaryScreen.Bounds
    return sz.Width, sz.Height


def SdkVersion():
    """Returns version of the Rhino SDK supported by the executing Rhino.
    Rhino SDK versions are 9 digit numbers in the form of YYYYMMDDn.
    Parameters:
      None
    Returns:
      the version of the Rhino SDK supported by the executing Rhino
    Example:
      import rhinoscriptsyntax as rs
      print "Required SDK Version:", rs.SdkVersion()
    See Also:
      
    """
    return Rhino.RhinoApp.SdkVersion


def SearchPathCount():
    """Returns the number of path items in Rhino's search path list.
    See "Options Files settings" in the Rhino help file for more details.
    Parameters:
      None
    Returns:
      the number of path items in Rhino's search path list
    Example:
      import rhinoscriptsyntax as rs
      count = rs.SearchPathCount()
      if count>0:
      paths = rs.SearchPathList()
    See Also:
      AddSearchPath
      DeleteSearchPath
      SearchPathList
    """
    return Rhino.ApplicationSettings.FileSettings.SearchPathCount


def SearchPathList():
    """Returns all of the path items in Rhino's search path list.
    See "Options Files settings" in the Rhino help file for more details.
    Parameters:
      None
    Returns:
      list of search paths
    Example:
      import rhinoscriptsyntax as rs
      count = rs.SearchPathCount()
      if count>0:
      paths = rs.SearchPathList()
    See Also:
      AddSearchPath
      DeleteSearchPath
      SearchPathCount
    """
    return Rhino.ApplicationSettings.FileSettings.GetSearchPaths()


def SendKeystrokes(keys=None, add_return=True):
    """Sends a string of printable characters to Rhino's command line
    Parameters:
      keys [opt] = A string of characters to send to the command line.
      add_returns [opt] = Append a return character to the end of the string.
    Returns:
      None
    Example:
      import rhinoscriptsyntax as rs
      rs.SendKeystroke( "Hello Rhino!" )
      rs.SendKeystrokes( 25/4 )
    See Also:
      Command
    """
    Rhino.RhinoApp.SendKeystrokes(keys, add_return)


def Snap(enable=None):
    """Enables or disables Rhino's grid snap modeling aid
    Parameters:
      enable [opt] = the new enabled status (True or False)
    Returns:
      if enable is not specified, the current grid snap status
      if enable is specified, the previous grid snap status
    Example:
      import rhinoscriptsyntax as rs
      if not rs.Snap(): rs.Snap(True)
    See Also:
      Ortho
      Osnap
      Planar
    """
    rc = modelaid.GridSnap
    if enable is not None and enable <> rc:
        modelaid.GridSnap = enable
    return rc


def StatusBarDistance(distance=0):
    """Sets Rhino's status bar distance pane
    Parameters:
      distance [opt] = distance to set the status bar
    Returns:
      None
    Example:
      import rhinoscriptsyntax as rs
      rs.StatusBarDistance(3.14159)
    See Also:
      StatusBarMessage
      StatusBarPoint
    """
    Rhino.UI.StatusBar.SetDistancePane(distance)


def StatusBarMessage(message=None):
    """Sets Rhino's status bar message pane
      Parameters:
        message [opt] = message value
      Returns:
        None
      Example:
        import rhinoscriptsyntax as rs
        rs.StatusBarMessage("Hello Rhino!")
      See Also:
        StatusBarDistance
        StatusBarPoint
    """
    Rhino.UI.StatusBar.SetMessagePane(message)


def StatusBarPoint(point=None):
    """Sets Rhino's status bar point coordinate pane
    Parameters:
      point [opt] = point value
    Returns:
      None
    Example:
      import rhinoscriptsyntax as rs
      pt = (1.1, 2.2, 3.3)
      rs.StatusBarPoint(pt)
    See Also:
      StatusBarDistance
      StatusBarMessage
    """
    point = rhutil.coerce3dpoint(point)
    if not point: point = Rhino.Geometry.Point3d(0,0,0)
    Rhino.UI.StatusBar.SetPointPane(point)


def StatusBarProgressMeterShow(label, lower, upper, embed_label=True, show_percent=True):
    """Start the Rhino status bar progress meter
    Parameters:
      label = short description of the progesss
      lower = lower limit of the progress meter's range
      upper = upper limit of the progress meter's range
      embed_label[opt] = if True, the label will show inside the meter.
        If false, the label will show to the left of the meter
      show_percent[opt] = show the percent complete
    Returns:
      True or False indicating success or failure
    Example:
    See Also:
    """
    rc = Rhino.UI.StatusBar.ShowProgressMeter(lower, upper, label, embed_label, show_percent)
    return rc==1


def StatusBarProgressMeterUpdate(position, absolute=True):
    """Set the current position of the progress meter
    Parameters:
      position = new position in the progress meter
      absolute[opt] = position is an absolute or relative
    Returns:
      previous position setting
    Example:
    See Also:
    """
    return Rhino.UI.StatusBar.UpdateProgressMeter(position, absolute)


def StatusBarProgressMeterHide():
    """Hide the progress meter
    Parameters:
      None
    Returns:
      None
    Example:
    See Also:
    """
    Rhino.UI.StatusBar.HideProgressMeter()


def TemplateFile(filename=None):
    """Returns or sets Rhino's default template file. This is the file used
    when Rhino starts.
    Parameters:
      filename[opt] = The name of the new default template file (must exist)
    Returns:
      if filename is not specified, then the current default template file
      if filename is specified, then the previous default template file
    Example:
      import rhinoscriptsyntax as rs
      folder = rs.TemplateFolder()
      filename = folder + "\\Millimeters.3dm"
      rs.TemplateFile(filename)
    See Also:
      TemplateFolder
    """
    rc = Rhino.ApplicationSettings.FileSettings.TemplateFile
    if filename: Rhino.ApplicationSettings.FileSettings.TemplateFile = filename
    return rc


def TemplateFolder(folder=None):
    """Returns or sets the location of Rhino's template folder
    Parameters:
      The location of Rhino's template files. Note, the location must exist
    Returns:
      if folder is not specified, then the current template file folder
      if folder is specified, then the previous template file folder
    Example:
      import rhinoscriptsyntax as rs
      folder = rs.TemplateFolder()
      filename = folder + "\\Millimeters.3dm"
      rs.TemplateFile(filename)
    See Also:
      TemplateFile
    """
    rc = Rhino.ApplicationSettings.FileSettings.TemplateFolder
    if folder is not None: Rhino.ApplicationSettings.FileSettings.TemplateFolder = folder
    return rc


def WindowHandle():
    """Returns the windows handle of Rhino's main window
    Parameters:
      None
    Returns:
      the windows handle of Rhino's main window
    Example:
      import rhinoscriptsyntax as rs
      handle = rs.WindowHandle()
      print handle
    See Also:
      
    """
    return Rhino.RhinoApp.MainWindowHandle()


def WorkingFolder(folder=None):
    """Returns or sets Rhino's working folder (directory).
    The working folder is the default folder for all file operations.
    Parameters:
      folder[opt] = the new working folder
    Returns:
      if folder is not specified, then the current working folder
      if folder is specified, then the previous working folder
    Example:
      import rhinoscriptsyntax as  rs
      folder = rs.WorkingFolder()
      folder = rs.BrowseForFolder(folder,  "Directory", "Select Directory")
      if folder is not None:
      rs.WorkingFolder(folder)
    See Also:
      BrowseForFolder
    """
    rc = Rhino.ApplicationSettings.FileSettings.WorkingFolder
    if folder is not None: Rhino.ApplicationSettings.FileSettings.WorkingFolder = folder
    return rc