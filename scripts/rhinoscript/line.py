import scriptcontext
import utility as rhutil
import Rhino


def LineClosestPoint( line, testpoint ):
    """
    Finds the point on an infinite line that is closest to a test point
    Returns:
      point if successful
      None on error
    """
    line = rhutil.coerceline(line)
    testpoint = rhutil.coerce3dpoint(testpoint)
    if line is None or testpoint is None: return scriptcontext.errorhandler()
    return line.ClosestPoint(testpoint, True)


def LineCylinderIntersection(line, cylinder_plane, cylinder_height, cylinder_radius):
    """
    Calculates the intersection of a line and a cylinder
    Parameters:
      line = the line to intersect
      cylinder_plane = base plane of the cylinder
      cylinder_height = height of the cylinder
      cylinder_radius = radius of the cylinder
    Returns:
      list of one or two points of intersection if successful
      None on error
    """
    line = rhutil.coerceline(line)
    cylinder_plane = rhutil.coerceplane(cylinder_plane)
    if not line or not cylinder_plane: return scriptcontext.errorhandler()
    circle = Rhino.Geometry.Circle( cylinder_plane, cylinder_radius )
    if not circle.IsValid: return scriptcontext.errorhandler()
    cyl = Rhino.Geometry.Cylinder( circle, cylinder_height )
    if not cyl.IsValid: return scriptcontext.errorhandler()
    rc, pt1, pt2 = Rhino.Geometry.Intersect.Intersection.LineCylinder(line, cyl)
    if rc==Rhino.Geometry.Intersect.LineCylinderIntersection.None:
        return None
    if rc==Rhino.Geometry.Intersect.LineCylinderIntersection.Single:
        return [pt1]
    return [pt1,pt2]


def LineIsFartherThan(line, distance, point_or_line):
    """
    Determines if the shortest distance from a line to a point or another
    line is greater than a specified distance
    Returns:
      True if the shortest distance from the line to the other project is
      greater than distance, False otherwise
      None on error 
    """
    line = rhutil.coerceline(line)
    test = rhutil.coerceline(point_or_line)
    if not test: test = rhutil.coerce3dpoint(point_or_line)
    if line is None or test is None: return scriptcontext.errorhandler()
    minDist = line.MinimumDistanceTo(test)
    return minDist>distance


def LineLineIntersection(lineA, lineB):
    """
    Calculates the intersection of two non-parallel lines. Note, the two
    lines do not have to intersect for an intersection to be found. (see help)
    Parameters:
      lineA, lineB = lines to intersect
    Returns:
      a tuple containing a point on the first line and a point on the second line if successful
      None on error
    """
    lineA = rhutil.coerceline(lineA)
    lineB = rhutil.coerceline(lineB)
    if lineA is None or lineB is None: return scriptcontext.errorhandler()
    rc, a, b = Rhino.Geometry.Intersect.Intersection.LineLine(lineA, lineB)
    if not rc: return None
    return lineA.PointAt(a), lineB.PointAt(b)


def LineMaxDistanceTo(line, point_or_line):
    """
    Finds the longest distance between a line as a finite chord, and a point
    or another line
    """
    line = rhutil.coerceline(line)
    test = rhutil.coerceline(point_or_line)
    if test is None: test = rhutil.coerce3dpoint(point_or_line)
    if line is None or test is None: return scriptcontext.errorhandler()
    return line.MaximumDistanceTo(test)


def LineMinDistanceTo(line, point_or_line):
    """
    Finds the shortest distance between a line as a finite chord, and a point
    or another line
    """
    line = rhutil.coerceline(line)
    test = rhutil.coerceline(point_or_line)
    if test is None: test = rhutil.coerce3dpoint(point_or_line)
    if line is None or test is None: return scriptcontext.errorhandler()
    return line.MinimumDistanceTo(test)


def LinePlane(line):
    """
    Returns a plane that contains the line. The origin of the plane is at the start of
    the line. If possible, a plane parallel to the world XY, YZ, or ZX plane is returned
    """
    line = rhutil.coerceline(line)
    if line is None: return scriptcontext.errorhandler()
    rc, plane = line.TryGetPlane()
    if not rc: return scriptcontext.errorhandler()
    return plane


def LinePlaneIntersection(line, plane):
    """
    Calculates the intersection of a line and a plane.
    Parameters:
      line = Two 3-D points identifying the starting and ending points of the line to intersect.
      plane = The plane to intersect.
    Returns:
      The 3-D point of intersection is successful.
      None if not successful, or on error.
    """
    plane = rhutil.coerceplane(plane)
    line_points = rhutil.coerce3dpointlist(line)
    if plane is None or line_points is None: return scriptcontext.errorhandler()
    line = Rhino.Geometry.Line(line_points[0], line_points[1])
    rc, t = Rhino.Geometry.Intersect.Intersection.LinePlane(line, plane) 
    if  not rc: return scriptcontext.errorhandler()
    return line.PointAt(t)


def LineSphereIntersection(line, sphere_center, sphere_radius):
    """
    Calculates the intersection of a line and a sphere
    Returns:
      list of intersection points if successful
      None on error
    """
    line = rhutil.coerceline(line)
    sphere_plane = rhutil.coerceplane(sphere_plane)
    if line is None or sphere_plane is None: return scriptcontext.errorhandler()
    sphere = Rhino.Geometry.Sphere(sphere_center, sphere_radius)
    rc, pt1, pt2 = Rhino.Geometry.Intersect.Intersection.LineSphere(line, sphere)
    if rc==Rhino.Geometry.Intersect.LineSphereIntersection.None:
      return scriptcontext.errorhandler()
    if rc==Rhino.Geometry.Intersect.LineSphereIntersection.Single:
      return [pt1]
    return [pt1, pt2]


def LineTransform( line, xform ):
    """
    Transforms a line
    Parameters:
      line = the line to transform
      xform = the transformation to apply
    Returns:
      transformed line on success
      None on error
    """
    line = rhutil.coerceline(line)
    xform = rhutil.coercexform(xform)
    if line is None or xform is None: return scriptcontext.errorhandler()
    success = line.Transform(xform)
    if not success: return scriptcontext.errorhander()
    return line