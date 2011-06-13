import scriptcontext
import utility as rhutil
import Rhino


def LineClosestPoint(line, testpoint):
    "Finds the point on an infinite line that is closest to a test point"
    line = rhutil.coerceline(line, True)
    testpoint = rhutil.coerce3dpoint(testpoint, True)
    return line.ClosestPoint(testpoint, True)


def LineCylinderIntersection(line, cylinder_plane, cylinder_height, cylinder_radius):
    """Calculates the intersection of a line and a cylinder
    Parameters:
      line = the line to intersect
      cylinder_plane = base plane of the cylinder
      cylinder_height = height of the cylinder
      cylinder_radius = radius of the cylinder
    Returns:
      list of intersection points (0, 1, or 2 points)
    """
    line = rhutil.coerceline(line, True)
    cylinder_plane = rhutil.coerceplane(cylinder_plane, True)
    circle = Rhino.Geometry.Circle( cylinder_plane, cylinder_radius )
    if not circle.IsValid: raise ValueError("unable to create valid circle with given plane and radius")
    cyl = Rhino.Geometry.Cylinder( circle, cylinder_height )
    if not cyl.IsValid: raise ValueError("unable to create valid cylinder with given circle and height")
    rc, pt1, pt2 = Rhino.Geometry.Intersect.Intersection.LineCylinder(line, cyl)
    if rc==Rhino.Geometry.Intersect.LineCylinderIntersection.None:
        return []
    if rc==Rhino.Geometry.Intersect.LineCylinderIntersection.Single:
        return [pt1]
    return [pt1, pt2]


def LineIsFartherThan(line, distance, point_or_line):
    """Determines if the shortest distance from a line to a point or another
    line is greater than a specified distance
    Returns:
      True if the shortest distance from the line to the other project is
      greater than distance, False otherwise
    """
    line = rhutil.coerceline(line, True)
    test = rhutil.coerceline(point_or_line)
    if not test: test = rhutil.coerce3dpoint(point_or_line, True)
    minDist = line.MinimumDistanceTo(test)
    return minDist>distance


def LineLineIntersection(lineA, lineB):
    """Calculates the intersection of two non-parallel lines. Note, the two
    lines do not have to intersect for an intersection to be found. (see help)
    Parameters:
      lineA, lineB = lines to intersect
    Returns:
      a tuple containing a point on the first line and a point on the second line if successful
      None on error
    """
    lineA = rhutil.coerceline(lineA, True)
    lineB = rhutil.coerceline(lineB, True)
    rc, a, b = Rhino.Geometry.Intersect.Intersection.LineLine(lineA, lineB)
    if not rc: return None
    return lineA.PointAt(a), lineB.PointAt(b)


def LineMaxDistanceTo(line, point_or_line):
    """Finds the longest distance between a line as a finite chord, and a point
    or another line
    """
    line = rhutil.coerceline(line, True)
    test = rhutil.coerceline(point_or_line)
    if test is None: test = rhutil.coerce3dpoint(point_or_line, True)
    return line.MaximumDistanceTo(test)


def LineMinDistanceTo(line, point_or_line):
    """Finds the shortest distance between a line as a finite chord, and a point
    or another line
    """
    line = rhutil.coerceline(line, True)
    test = rhutil.coerceline(point_or_line)
    if test is None: test = rhutil.coerce3dpoint(point_or_line, True)
    return line.MinimumDistanceTo(test)


def LinePlane(line):
    """Returns a plane that contains the line. The origin of the plane is at the start of
    the line. If possible, a plane parallel to the world XY, YZ, or ZX plane is returned
    """
    line = rhutil.coerceline(line, True)
    rc, plane = line.TryGetPlane()
    if not rc: return scriptcontext.errorhandler()
    return plane


def LinePlaneIntersection(line, plane):
    """Calculates the intersection of a line and a plane.
    Parameters:
      line = Two 3D points identifying the starting and ending points of the line to intersect.
      plane = The plane to intersect.
    Returns:
      The 3D point of intersection is successful.
      None if not successful, or on error.
    """
    plane = rhutil.coerceplane(plane, True)
    line_points = rhutil.coerce3dpointlist(line, True)
    line = Rhino.Geometry.Line(line_points[0], line_points[1])
    rc, t = Rhino.Geometry.Intersect.Intersection.LinePlane(line, plane) 
    if  not rc: return scriptcontext.errorhandler()
    return line.PointAt(t)


def LineSphereIntersection(line, sphere_center, sphere_radius):
    """Calculates the intersection of a line and a sphere
    Returns:
      list of intersection points if successful
    """
    line = rhutil.coerceline(line, True)
    sphere_plane = rhutil.coerceplane(sphere_plane, True)
    sphere = Rhino.Geometry.Sphere(sphere_center, sphere_radius)
    rc, pt1, pt2 = Rhino.Geometry.Intersect.Intersection.LineSphere(line, sphere)
    if rc==Rhino.Geometry.Intersect.LineSphereIntersection.None: return []
    if rc==Rhino.Geometry.Intersect.LineSphereIntersection.Single: return [pt1]
    return [pt1, pt2]


def LineTransform(line, xform):
    """Transforms a line
    Parameters:
      line = the line to transform
      xform = the transformation to apply
    Returns:
      transformed line
    """
    line = rhutil.coerceline(line, True)
    xform = rhutil.coercexform(xform, True)
    success = line.Transform(xform)
    if not success: raise Execption("unable to transform line")
    return line