################################################################
#Creates an array of points on a surface
################################################################
import rhinoscriptsyntax as rs

def ArrayPointsOnSurface():
  # Get the surface object
  objectId = rs.GetObject("Select surface", rs.filter.surface)
  if( objectId == None ):
    return

  # Get the number of rows
  nRows = rs.GetInteger("Number of rows", 2, 2)
  if( nRows == None ):
    return

  # Get the number of columns
  nColumns = rs.GetInteger("Number of columns", 2, 2)
  if( nColumns == None ):
    return

  # Get the domain of the surface
  U = rs.SurfaceDomain(objectId, 0)
  V = rs.SurfaceDomain(objectId, 1)
  
  if( U==None or V==None ):
    return

  # Add the points
  for i in xrange(0,nRows):
    param0 = U[0] + (((U[1] - U[0]) / (nRows-1)) * i)
    for j in xrange(0,nColumns):
      param1 = V[0] + (((V[1] - V[0]) / (nColumns-1)) * j)
      point = rs.EvaluateSurface(objectId, param0, param1)
      if( point != None ):
        rs.AddPoint(point)


##########################################################################
# Here we check to see if this file is being executed as the "main" python
# script instead of being used as a module by some other python script
# This allows us to use the module which ever way we want.
if( __name__ == '__main__' ):
  # call the function defined above
  ArrayPointsOnSurface()