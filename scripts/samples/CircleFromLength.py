################################################################
#Create a circle from a center point and a circumference.
#
# if you want to match old RhinoScript as close as possible,
# import the support libraries with the following line
import rhinoscriptsyntax as rs
import math

def CreateCircle(circumference=None):
  center = rs.GetPoint("Center point of circle")
  if( center!=None ):
    plane = rs.MovePlane(rs.ViewCPlane(), center)
    length = circumference
    if( length==None ):
      length = rs.GetReal("Circle circumference")
    if( length!=None and length > 0.0 ):
      radius = length / (2 * math.pi)
      objectId = rs.AddCircle(plane, radius)
      rs.SelectObject(objectId)
      return length
  return None

# call function defined above
# Here we check to see if this file is being executed as the "Main" python
# script instead of being used as a module by some other python script
# This allows us to use the module which ever way we want.
if( __name__ == '__main__' ):
  CreateCircle()
  
# See UseModule.py sample for using this script as a module