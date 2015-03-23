# Displays information about the currently loaded Rhino document.
import rhinoscriptsyntax as rs
from System.IO import Path, File, FileInfo, FileAttributes

# some helper functions for CurrentModelInfo
def __FileAttributes(fullpath):
    "Returns a string describing a file's attributes."
    attr = File.GetAttributes(fullpath)
    if( attr == FileAttributes.Normal ):
        return "Normal"
    rc = ""
    if( attr & FileAttributes.Directory ): rc += "Directory "
    if( attr & FileAttributes.ReadOnly ): rc += "Read Only "
    if( attr & FileAttributes.Hidden ): rc += "Hidden "
    if( attr & FileAttributes.System ): rc += "System "
    if( attr & FileAttributes.Archive ): rc += "Archive "
    if( attr & FileAttributes.Compressed ): rc += "Compressed "
    return rc


def __PrintFileInformation( fullpath ):
    "Displays a file's information."
    fi = FileInfo(fullpath)
    info  = "Full Path:  " + fullpath +"\n"
    info += "File Name:  " + Path.GetFileName(fullpath) + "\n"
    info += "File Attributes:  " + __FileAttributes(fullpath) + "\n"
    info += "Date Created:  " + File.GetCreationTime(fullpath).ToString() + "\n"
    info += "Last Date Accessed:  " + File.GetLastAccessTime(fullpath).ToString() + "\n"
    info += "Last Date Modified:  " + File.GetLastWriteTime(fullpath).ToString() + "\n"
    info += "File Size (Bytes):  " + fi.Length.ToString() + "\n"
    rs.MessageBox( info, 0, "Current Model Information" )


def CurrentModelInfo():
    "Get the current document name and path"
    name = rs.DocumentName()
    path = rs.DocumentPath()
    fileexists = False
    if( path and name ):
        filespec = Path.Combine(path, name)
        fileexists = File.Exists(filespec)
    
    if fileexists:
        __PrintFileInformation(filespec)
    else:
        print "Current model not found. Make sure the model has been saved to disk."


##########################################################################
# Check to see if this file is being executed as the "main" python
# script instead of being used as a module by some other python script
# This allows us to use the module which ever way we want.
if( __name__ == "__main__" ):
  #call function defined above
  CurrentModelInfo()