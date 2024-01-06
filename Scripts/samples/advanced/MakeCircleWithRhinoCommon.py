################################################################
# Rhino Python Sample - MakeCircleWithRhinoCommon
#
# The rhinoscript package is provided as a scripting "convenience"
# Python can use all of the classes and functions defined
# in RhinoCommon and the rest of the .NET Framework!!!
#
# This sample creates a circle without using functions in the
# rhinoscript package
#
# Rhino is the base namespace of the RhinoCommon SDK
################################################################
import math
import Rhino
import scriptcontext


# Use a GetPoint to prompt the user to select a point
# If the user doesn't cancel, this function returns a new Circle
# class instance centered at the selection point with a radius of 1
def GetCircleFromUser():
  get_result = Rhino.Input.RhinoGet.GetPoint("Circle center", False)
  if( get_result[0] != Rhino.Commands.Result.Success ):
    print("error getting point")
    return None
  pt = get_result[1]
  print("Got a point at {}".format(pt))
  # return a new Circle
  return Rhino.Geometry.Circle( pt, 1 )

# Add some points to the document that are on a circle
def MakeCirclePoints( circle, count ):
  for i in range(count):
    #circles parameterized between 0 and 2Pi
    t = float(i) * 2 * math.pi / float(count)
    print(t)
    pt = circle.PointAt(t)
    scriptcontext.doc.Objects.AddPoint(pt)


######################################
# Functions have been defined above - let's execute some script
#
# Here we check to see if this file is being executed as the "main" python
# script instead of being used as a module by some other python script
# This allows us to use the module which ever way we want.
if( __name__ == '__main__' ):
  print("Python sample script to make a circle curve and plop some points on it")
  circle = GetCircleFromUser()

  if circle == None:
    print("circle is none")
  else:
    print("got a circle")
    scriptcontext.doc.Objects.AddCircle(circle)
    MakeCirclePoints( circle, 10 )
    # redraw everything so we can see what we got
    scriptcontext.doc.Views.Redraw()

  print("Script Complete")
