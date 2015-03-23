import rhinoscriptsyntax as rs
import System
from System.IO import Path

def CreateShortcut():
    """
    Create a shortcut to the current document
    NOTE!! This function only runs on Windows
    """
    if( not rs.IsRunningOnWindows() ):
        rs.MessageBox("CreateShortcut.py only runs on Windows", 48, "Script Error")
        return
    
    # Get the document name and path
    name = rs.DocumentName()
    path = rs.DocumentPath()

    # Get the Windows Scripting Host's Shell object
    objShell = System.Activator.CreateInstance(System.Type.GetTypeFromProgID("WScript.Shell"))
    # Get the desktop folder
    desktop = objShell.SpecialFolders("Desktop")
    # Make a new shortcut
    ShellLink = objShell.CreateShortcut(desktop + "\\" + name + ".lnk")
    ShellLink.TargetPath = Path.Combine(path, name)
    ShellLink.WindowStyle = 1
    ShellLink.IconLocation = rs.ExeFolder() + "Rhino4.exe, 0"
    ShellLink.Description = "Shortcut to " + name
    ShellLink.WorkingDirectory = path
    ShellLink.Save()

##########################################################################
# Check to see if this file is being executed as the "main" python
# script instead of being used as a module by some other python script
# This allows us to use the module which ever way we want.
if( __name__ == '__main__' ):
    #call function defined above
    CreateShortcut()
