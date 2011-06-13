import utility as rhutil
import Rhino.Geometry
import scriptcontext
import math

def DistanceToPlane(plane, point):
    "Returns the distance from a 3D point to a plane"
    plane = rhutil.coerceplane(plane, True)
    point = rhutil.coerce3dpoint(point, True)
    return plane.DistanceTo(point)


def EvaluatePlane(plane, parameter):
    """Evaluates a plane at a U,V parameter
    Parameters:
      plane = the plane to evaluate
      parameter = list of two numbers defining the U,V parameter to evaluate
    Returns:
      Point3d on success
    """
    plane = rhutil.coerceplane(plane, True)
    return plane.PointAt(parameter[0], parameter[1])


def IntersectPlanes(plane1, plane2, plane3):
    """Calculates the intersection of three planes
    Returns:
      Point3d on success
      None on error
    """
    plane1 = rhutil.coerceplane(plane1, True)
    plane2 = rhutil.coerceplane(plane2, True)
    plane3 = rhutil.coerceplane(plane3, True)
    rc, point = Rhino.Geometry.Intersect.Intersection.PlanePlanePlane(plane1, plane2, plane3)
    if rc: return point
    return scriptcontext.errorhandler()


def MovePlane(plane, origin):
    """Moves the origin of a plane
    Parameters:
      plane = Plane or ConstructionPlane
      origin = Point3d or list of three numbers
    Returns:
      moved plane
    """
    plane = rhutil.coerceplane(plane, True)
    origin = rhutil.coerce3dpoint(origin, True)
    rc = Rhino.Geometry.Plane(plane)
    rc.Origin = origin
    return rc


def PlaneClosestPoint(plane, point, return_point=True):
    """Returns the point on a plane that is closest to a test point.
    Parameters:
      plane = The plane
      point = The 3-D point to test.
      return_point [opt] = If omitted or True, then the point on the plane
         that is closest to the test point is returned. If False, then the
         parameter of the point on the plane that is closest to the test
         point is returned.
    Returns:
      If return_point is omitted or True, then the 3-D point
      If return_point is False, then an array containing the U,V parameters
      of the point
      None if not successful, or on error.
    """
    plane = rhutil.coerceplane(plane, True)
    point = rhutil.coerce3dpoint(point, True)
    if return_point:
        return plane.ClosestPoint(point)
        if rc.IsValid: return rc
    else:
        rc, s, t = plane.ClosestParameter(point)
        if rc: return s, t
    return scriptcontext.errorhandler()


def PlaneEquation(plane):
    """Returns the equation of a plane as a tuple of four numbers. The standard
    equation of a plane with a non-zero vector is Ax+By+Cz+D=0
    """
    plane = rhutil.coerceplane(plane, True)
    rc = plane.GetPlaneEquation()
    return rc[0], rc[1], rc[2], rc[3]


def PlaneFitFromPoints(points):
    """Returns a plane that was fit through an array of 3D points.
    Parameters:
    points = An array of 3D points.
    Returns: 
      The plane if successful
      None if not successful
    """
    points = rhutil.coerce3dpointlist(points, True)
    rc, plane = Rhino.Geometry.Plane.FitPlaneToPoints(points)
    if rc==Rhino.Geometry.PlaneFitResult.Success: return plane
    return scriptcontext.errorhandler()


def PlaneFromFrame(origin, x_axis, y_axis):
    """Construct a plane from a point, and two vectors in the plane.
    Parameters:
      origin = A 3D point identifying the origin of the plane.
      x_axis = A non-zero 3D vector in the plane that determines the X axis
               direction.
      y_axis = A non-zero 3D vector not parallel to x_axis that is used
               to determine the Y axis direction. Note, y_axis does not
               have to be perpendicular to x_axis.
    Returns:
      The plane if successful. 
      None if not successful
    """
    origin = rhutil.coerce3dpoint(origin, True)
    x_axis = rhutil.coerce3dvector(x_axis, True)
    y_axis = rhutil.coerce3dvector(y_axis, True)
    return Rhino.Geometry.Plane(origin, x_axis, y_axis)


def PlaneFromNormal(origin, normal, xaxis=None):
    """Creates a plane from an origin point and a normal direction vector.
    Parameters:
      origin = A 3D point identifying the origin of the plane.
      normal = A 3D vector identifying the normal direction of the plane.
      xaxis[opt] = optional vector defining the plane's x-axis
    Returns:
      The plane if successful.
      None if not successful, or on error.  
    """
    origin = rhutil.coerce3dpoint(origin, True)
    normal = rhutil.coerce3dvector(normal, True)
    rc = Rhino.Geometry.Plane(origin, normal)
    if xaxis:
        xaxis = rhutil.coerce3dpoint(xaxis, True)
        projected_start = rc.ClosestPoint(Rhino.Geometry.Point3d(0,0,0))
        projected_end = rc.ClosestPoint(xaxis)
        xaxis = projected_end - projected_start
        if xaxis.IsValid and not xaxis.IsParallelTo(rc.YAxis):
            rc = Rhino.Geometry.Plane(origin, xaxis, rc.YAxis)
    return rc


def PlaneFromPoints(origin, x, y):
    """Creates a plane from three non-colinear points
    Parameters:
      origin = origin point of the plane
      x, y = points on the plane's x and y axes
    """
    origin = rhutil.coerce3dpoint(origin, True)
    x = rhutil.coerce3dpoint(x, True)
    y = rhutil.coerce3dpoint(y, True)
    plane = Rhino.Geometry.Plane(origin, x, y)
    if plane.IsValid: return plane
    return scriptcontext.errorhandler()


def PlanePlaneIntersection(plane1, plane2):
    """Calculates the intersection of two planes
    Paramters:
      plane1, plane2 = two planes
    Returns:
      two 3d points identifying the starting/ending points of the intersection
      None on error
    """
    plane1 = rhutil.coerceplane(plane1, True)
    plane2 = rhutil.coerceplane(plane2, True)
    rc, line = Rhino.Geometry.Intersect.Intersection.PlanePlane(plane1, plane2)
    if rc: return line.From, line.To
    return scriptcontext.errorhandler()


def PlaneSphereIntersection(plane, sphere_plane, sphere_radius):
    """Calculates the intersection of a plane and a sphere
    Parameters:
      plane = the plane to intersect
      sphere_plane = equitorial plane of the sphere. origin of the plane is
        the center of the sphere
      sphere_radius = radius of the sphere
    Returns:
      list of intersection results - see help
      None on error
    """
    plane = rhutil.coerceplane(plane, True)
    sphere_plane = rhutil.coerceplane(sphere_plane, True)
    sphere = Rhino.Geometry.Sphere(sphere_plane, sphere_radius)
    rc, circle = Rhino.Geometry.Intersect.Intersection.PlaneSphere(plane, sphere)
    if rc==Rhino.Geometry.Intersect.PlaneSphereIntersection.Point:
        return 0, circle.Center
    if rc==Rhino.Geometry.Intersect.PlaneSphereIntersection.Circle:
        return 1, circle.Plane, circle.Radius
    return scriptcontext.errorhandler()


def PlaneTransform(plane, xform):
    """Transforms a plane
    Parameters:
      plane = OnPlane or On3dmConstructionPlane
      xform = 
    """
    plane = rhutil.coerceplane(plane, True)
    xform = rhutil.coercexform(xform, True)
    rc = Rhino.Geometry.Plane(plane)
    if rc.Transform(xform): return rc
    return scriptcontext.errorhandler()


def RotatePlane(plane, angle_degrees, axis):
    """Rotates a plane
    Parameters:
      plane = OnPlane or On3dmConstructionPlane
      angle_degrees = rotation angle in degrees
      axis = On3dVector or list of three numbers
    Returns:
      rotated plane on success
      None on error
    """
    plane = rhutil.coerceplane(plane, True)
    axis = rhutil.coerce3dvector(axis, True)
    angle_radians = math.radians(angle_degrees)
    rc = Rhino.Geometry.Plane(plane)
    if rc.Rotate(angle_radians, axis): return rc
    return scriptcontext.errorhandler()


def WorldXYPlane():
    "Returns Rhino's world XY plane"
    return Rhino.Geometry.Plane.WorldXY


def WorldYZPlane():
    "Returns Rhino's world YZ plane"
    return Rhino.Geometry.Plane.WorldYZ


def WorldZXPlane():
    "Returns Rhino's world ZX plane"
    return Rhino.Geometry.Plane.WorldZX
