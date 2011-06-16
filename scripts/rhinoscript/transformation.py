import scriptcontext
import utility as rhutil
import Rhino
import System.Guid, System.Array
import math
import view as rhview


def IsXformIdentity(xform):
    "Verifies a matrix is the identity matrix"
    xform = rhutil.coercexform(xform, True)
    return xform==Rhino.Geometry.Transform.Identity


def IsXformSimilarity(xform):
    """Verifies a matrix is a similarity transformation. A similarity
    transformation can be broken into a sequence of dialations, translations,
    rotations, and reflections
    """
    xform = rhutil.coercexform(xform, True)
    return xform.SimilarityType!=Rhino.Geometry.TransformSimilarityType.NotSimilarity


def IsXformZero(xform):
    "verifies that a matrix is a zero transformation matrix"
    xform = rhutil.coercexform(xform, True)
    for i in range(4):
        for j in range(4):
            if xform[i,j]!=0: return False
    return True


def XformChangeBasis(initial_plane, final_plane):
    "Returns a change of basis transformation matrix or None on error"
    initial_plane = rhutil.coerceplane(initial_plane, True)
    final_plane = rhutil.coerceplane(final_plane, True)
    xform = Rhino.Geometry.Transform.ChangeBasis(initial_plane, final_plane)
    if not xform.IsValid: return scriptcontext.errorhandler()
    return xform


def XformChangeBasis2(x0,y0,z0,x1,y1,z1):
    """Returns a change of basis transformation matrix of None on error
    Parameters:
      x0,y0,z0 = initial basis
      x1,y1,z1 = final basis
    """
    x0 = rhutil.coerce3dvector(x0, True)
    y0 = rhutil.coerce3dvector(y0, True)
    z0 = rhutil.coerce3dvector(z0, True)
    x1 = rhutil.coerce3dvector(x1, True)
    y1 = rhutil.coerce3dvector(y1, True)
    z1 = rhutil.coerce3dvector(z1, True)
    xform = Rhino.Geometry.Transform.ChangeBasis(x0,y0,z0,x1,y1,z1)
    if not xform.IsValid: return scriptcontext.errorhandler()
    return xform


def XformCompare(xform1, xform2):
    """Compares two transformation matrices
    Parameters:
      xform1, xform2 = matrices to compare
    Returns:
      -1 if xform1<xform2
       1 if xform1>xform2
       0 if xform1=xform2
    """
    xform1 = rhutil.coercexform(xform1, True)
    xform2 = rhutil.coercexform(xform2, True)
    return xform1.CompareTo(xform2)


def XformCPlaneToWorld(point, plane):
    """Transform point from construction plane coordinates to world coordinates
    Parameters:
      point = A 3D point in construction plane coordinates.
      plane = The construction plane
    Returns:
      A 3D point in world coordinates
    """
    point = rhutil.coerce3dpoint(point, True)
    plane = rhutil.coerceplane(plane, True)
    return plane.Origin + point.X*plane.XAxis + point.Y*plane.YAxis + point.Z*plane.ZAxis


def XformDeterminant(xform):
    """Returns the determinant of a transformation matrix. If the determinant
    of a transformation matrix is 0, the matrix is said to be singular. Singular
    matrices do not have inverses.
    """
    xform = rhutil.coercexform(xform, True)
    return xform.Determinant


def XformDiagonal(diagonal_value):
    """Returns a diagonal transformation matrix. Diagonal matrices are 3x3 with
    the bottom row [0,0,0,1]
    """
    return Rhino.Geometry.Transform(diagonal_value)


def XformIdentity():
    "returns the identity transformation matrix"
    return Rhino.Geometry.Transform.Identity


def XformInverse(xform):
    """Returns the inverse of a non-singular transformation matrix
    Returns None on error
    """
    xform = rhutil.coercexform(xform, True)
    rc, inverse = xform.TryGetInverse()
    if not rc: return scriptcontext.errorhandler()
    return inverse


def XformMirror(mirror_plane_point, mirror_plane_normal):
    """Creates a mirror transformation matrix
    Parameters:
      mirror_plane_point = point on the mirror plane
      mirror_plane_normal = a 3D vector that is normal to the mirror plane
    Returns:
      mirror Transform
    """
    point = rhutil.coerce3dpoint(mirror_plane_point, True)
    normal = rhutil.coerce3dvector(mirror_plane_normal, True)
    return Rhino.Geometry.Transform.Mirror(point, normal)


def XformMultiply(xform1, xform2):
    """Multiplies two transformation matrices, where result = xform1 * xform2
    Returns:
      result transformation on success
    """
    xform1 = rhutil.coercexform(xform1, True)
    xform2 = rhutil.coercexform(xform2, True)
    return xform1*xform2


def XformPlanarProjection(plane):
    """Returns a transformation matrix that projects to a plane.
    Parameters
      plane = The plane to project to.
    Returns:
      The 4x4 transformation matrix.
    """
    plane = rhutil.coerceplane(plane, True)
    return Rhino.Geometry.Transform.PlanarProjection(plane)


def XformRotation1(initial_plane, final_plane):
    """Returns a rotation transformation that maps initial_plane to final_plane.
    The planes should be right hand orthonormal planes.
    Returns:
      The 4x4 transformation matrix.
      None on error.
    """
    initial_plane = rhutil.coerceplane(initial_plane, True)
    final_plane = rhutil.coerceplane(final_plane, True)
    xform = Rhino.Geometry.Transform.PlaneToPlane(initial_plane, final_plane)
    if not xform.IsValid: return scriptcontext.errorhandler()
    return xform


def XformRotation2(angle_degrees, rotation_axis, center_point):
    """Returns a rotation transformation
    Returns:
      The 4x4 transformation matrix.
      None on error.
    """
    axis = rhutil.coerce3dvector(rotation_axis, True)
    center = rhutil.coerce3dpoint(center_point, True)
    angle_rad = math.radians(angle_degrees)
    xform = Rhino.Geometry.Transform.Rotation(angle_rad, axis, center)
    if not xform.IsValid: return scriptcontext.errorhandler()
    return xform


def XformRotation3( start_direction, end_direction, center_point ):
    """Calculate the minimal transformation that rotates start_direction to
    end_direction while fixing center_point
    Parameters:
      start_direction, end_direction = 3d vectors
      center_point = the rotation center
    Returns:
      The 4x4 transformation matrix.
      None on error.
    """
    start = rhutil.coerce3dvector(start_direction, True)
    end = rhutil.coerce3dvector(end_direction, True)
    center = rhutil.coerce3dpoint(center_point, True)
    xform = Rhino.Geometry.Transform.Rotation(start, end, center)
    if not xform.IsValid: return scriptcontext.errorhandler()
    return xform


def XformRotation4(x0, y0, z0, x1, y1, z1):
    """Returns a rotation transformation.
    Paramters:
      x0,y0,z0 = Vectors defining the initial orthonormal frame
      x1,y1,z1 = Vectors defining the final orthonormal frame
    Returns:
      The 4x4 transformation matrix.
      None on error.
    """
    x0 = rhutil.coerce3dveector(x0, True)
    y0 = rhutil.coerce3dveector(y0, True)
    z0 = rhutil.coerce3dveector(z0, True)
    x1 = rhutil.coerce3dveector(x1, True)
    y1 = rhutil.coerce3dveector(y1, True)
    z1 = rhutil.coerce3dveector(z1, True)
    xform = Rhino.Geometry.Transform.Rotation(x0,y0,z0,x1,y1,z1)
    if not xform.IsValid: return scriptcontext.errorhandler()
    return xform


def XformScale(scale, point=None):
    """Creates a scale transformation
    Parameters:
      scale = single number, list of 3 numbers, Point3d, or Vector3d
      point[opt] = center of scale. If omitted, world origin is used
    Returns:
      The 4x4 transformation matrix on success
      None on error
    """
    factor = rhutil.coerce3dpoint(scale)
    if factor is None:
        if type(scale) is int or type(scale) is float:
            factor = (scale,scale,scale)
        if factor is None: return scriptcontext.errorhandler()
    if point: point = rhutil.coerce3dpoint(point, True)
    else: point = Rhino.Geometry.Point3d.Origin
    plane = Rhino.Geometry.Plane(point, Rhino.Geometry.Vector3d.ZAxis);
    xf = Rhino.Geometry.Transform.Scale(plane, factor[0], factor[1], factor[2])
    return xf


def XformScreenToWorld(point, view=None, screen_coordinates=False):
    """Transforms a point from either client-area coordinates of the specified view
    or screen coordinates to world coordinates. The resulting coordinates are represented
    as a 3-D point
    Parameters:
      point = 2D point
      view[opt] = title or identifier of a view. If omitted, the active view is used
      screen_coordinates[opt] = if False, point is in client-area coordinates. If True,
      point is in screen-area coordinates
    Returns:
      3D point on success
      None on error
    """
    point = rhutil.coerce2dpoint(point, True)
    view = rhview.__viewhelper(view)
    viewport = view.MainViewport
    xform = viewport.GetTransform(Rhino.DocObjects.CoordinateSystem.Screen, Rhino.DocObjects.CoordinateSystem.World)
    point3d = Rhino.Geometry.Point3d(point.X, point.Y, 0)
    if screen_coordinates:
        screen = view.ScreenRectangle
        point3d.X = point.X - screen.Left
        point3d.Y = point.Y - screen.Top
    point3d = xform * point3d
    return point3d


def XformShear(plane, x, y, z):
    """Returns a shear transformation matrix
    Parameters:
      plane = plane[0] is the fixed point
      x,y,z = each axis scale factor
    Returns:
      The 4x4 transformation matrix on success
    """
    plane = rhutil.coerceplane(plane, True)
    x = rhutil.coerce3dvector(x, True)
    y = rhutil.coerce3dvector(y, True)
    z = rhutil.coerce3dvector(z, True)
    return Rhino.Geometry.Transform.Shear(plane,x,y,z)


def XformTranslation(vector):
    "Creates a translation transformation matrix"
    vector = rhutil.coerce3dvector(vector, True)
    return Rhino.Geometry.Transform.Translation(vector)


def XformWorldtoCplane(point, plane):
    """Transforms a point from world coordinates to construction plane coordinates.
    Parameters:
      point = A 3D point in world coordinates.
      plane = The construction plane
    Returns:
      A 3D point in construction plane coordinates
    """
    point = rhutil.coerce3dpoint(point, True)
    plane = rhutil.coerceplane(plane, True)
    v = point - plane.Origin;
    return Rhino.Geometry.Point3d(v*plane.XAxis, v*plane.YAxis, v*plane.ZAxis)


def XformWorldToScreen(point, view=None, screen_coordinates=False):
    """Transforms a point from world coordinates to either client-area coordinates of
    the specified view or screen coordinates. The resulting coordinates are represented
    as a 2D point
    Parameters:
      point = 3D point in world coordinates
      view[opt] = title or identifier of a view. If omitted, the active view is used
      screen_coordinates[opt] = if False, the function returns the results as
        client-area coordinates. If True, the result is in screen-area coordinates
    Returns:
      2D point on success
      None on error
    """
    point = rhutil.coerce3dpoint(point, True)
    view = rhview.__viewhelper(view)
    viewport = view.MainViewport
    xform = viewport.GetTransform(Rhino.DocObjects.CoordinateSystem.World, Rhino.DocObjects.CoordinateSystem.Screen)
    point = xform * point
    point = Rhino.Geometry.Point2d(point.X, point.Y)
    if screen_coordinates:
        screen = view.ScreenRectangle
        point.X = point.X + screen.Left
        point.Y = point.Y + screen.Top
    return point


def XformZero():
    "Returns a zero transformation matrix"
    return Rhino.Geometry.Transform()