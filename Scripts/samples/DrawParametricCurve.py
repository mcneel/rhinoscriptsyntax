import rhinoscriptsyntax as rs
import math

# Something really interesting about this script is
# that we are passing a function as a parameter
def DrawParametricCurve(parametric_equation):
    "Create a interpolated curve based on a parametric equation."
    # Get the minimum parameter
    t0 = rs.GetReal("Minimum t value", 0.0)
    if( t0==None ): return
    
    # Get the maximum parameter
    t1 = rs.GetReal("Maximum t value", 1.0)
    if( t1==None ): return

    # Get the number of sampling points to interpolate through
    count = rs.GetInteger("Number of points", 50, 2)
    if count<1: return

    arrPoints = list()
    #Get the first point
    point = parametric_equation(t0)
    arrPoints.append(point)

    #Get the rest of the points
    for x in range(1,count-2):
        t = (1.0-(x/count))*t0 + (x/count)*t1
        point = parametric_equation(t)
        arrPoints.append(point)
  
    #Get the last point
    point = parametric_equation(t1)
    arrPoints.append(point)
    
    #Add the curve
    rs.AddInterpCurve(arrPoints)


#Customizable function that solves a parametric equation
def __CalculatePoint(t):
    x = (4*(1-t)+1*t ) * math.sin(3*6.2832*t)
    y = (4*(1-t)+1*t ) * math.cos(3*6.2832*t)
    z = 5*t
    return x,y,z

##########################################################################
# Check to see if this file is being executed as the "main" python
# script instead of being used as a module by some other python script
# This allows us to use the module which ever way we want.
if( __name__ == "__main__" ):
    #Call the function passing another function as a parameter
    DrawParametricCurve(__CalculatePoint)
