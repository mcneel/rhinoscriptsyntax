import rhinoscriptsyntax as rs

def ExportControlPoints():
    "Export curve's control points to a text file"
    #pick a curve object
    object_id = rs.GetObject("Select curve", rs.filter.curve)
    
    #get the curve's control points
    points = rs.CurvePoints(object_id)
    if not points: return
    
    #prompt the user to specify a file name
    filter = "Text File (*.txt)|*.txt|All files (*.*)|*.*||"
    filename = rs.SaveFileName("Save Control Points As", filter)
    if not filename: return

    file = open( filename, "w" )
    for pt in points:
        file.write( str(pt.X) )
        file.write( ", " )
        file.write( str(pt.Y) )
        file.write( ", " )
        file.write( str(pt.Z) )
        file.write( "\n" )
    file.close()


##########################################################################
# Check to see if this file is being executed as the "main" python
# script instead of being used as a module by some other python script
# This allows us to use the module which ever way we want.
if( __name__ == "__main__" ):
    ExportControlPoints()