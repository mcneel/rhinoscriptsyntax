import rhinoscriptsyntax as rs

def CurveLength():
    "Calculate the length of one or more curves"
    # Get the curve objects
    arrObjects = rs.GetObjects("Select Objects", rs.filter.curve, True, True)
    if( arrObjects==None ): return
    rs.UnselectObjects(arrObjects)

    length = 0.0
    count  = 0
    for object in arrObjects:
        if rs.IsCurve(object):
            #Get the curve length
            length += rs.CurveLength(object)
            count += 1
    
    if (count>0):
        print "Curves selected:", count, " Total Length:", length
    
# Check to see if this file is being executed as the "main" python
# script instead of being used as a module by some other python script
# This allows us to use the module which ever way we want.
if( __name__ == "__main__" ):
    CurveLength()
