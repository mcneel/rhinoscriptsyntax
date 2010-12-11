################################################################
#Annotate the endpoints of curve objects
################################################################
import rhinoscriptsyntax as rs

def AnnotateCurveEndPoints():
  """
  Purpose: Annotates the endpoints of curve objects. If the curve is closed
           then only the starting point is annotated.
  """
  # get the curve object
  objectId = rs.GetObject("Select curve", rs.filter.curve)
  if( objectId == None ):
    return

  # Add the first annotation
  point = rs.CurveStartPoint(objectId)
  rs.AddPoint(point)
  rs.AddTextDot( str(point), point )

  # Add the second annotation
  if( not rs.IsCurveClosed(objectId) ):
    point = rs.CurveEndPoint(objectId)
    rs.AddPoint(point)
    rs.AddTextDot( str(point), point )


##########################################################################
# Here we check to see if this file is being executed as the "main" python
# script instead of being used as a module by some other python script
# This allows us to use the module which ever way we want.
if( __name__ == '__main__' ):
  # Call the function defined above
  AnnotateCurveEndPoints()