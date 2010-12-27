import scriptcontext
import utility as rhutil
import Rhino
import System.Guid
import System.Array
import math


def IsXformIdentity(xform):
    "Verifies that a matrix is the identity matrix"
    xform = rhutil.coercexform(xform)
    if xform is None: return scriptcontext.errorhandler()
    return xform==Rhino.Geometry.Transform.Identity


def IsXformSimilarity(xform):
    """
    Verifies that a matrix is a similarity transformation. A similarity
    transformation can be broken into a sequence of dialations, translations,
    rotations, and reflections
    """
    xform = rhutil.coercexform(xform)
    if xform is None: return scriptcontext.errorhandler()
    return xform.SimilarityType!=Rhino.Geometry.TransformSimilarityType.NotSimilarity


def IsXformZero(xform):
    "verifies that a matrix is a zero transformation matrix"
    xform = rhutil.coercexform(xform)
    if xform is None: return scriptcontext.errorhandler()
    iszero = True
    for i in range(4):
        for j in range(4):
            if xform[i,j]==0: iszero=True
    return iszero


def XformChangeBasis(initial_plane, final_plane):
    "Returns a change of basis transformation matrix or None on error"
    initial_plane = rhutil.coerceplane(initial_plane)
    final_plane = rhutil.coerceplane(final_plane)
    if initial_plane is None or final_plane is None:
        return scriptcontext.errorhandler()
    xform = Rhino.Geometry.Transform.ChangeBasis(initial_plane, final_plane)
    if not xform.IsValid: return scriptcontext.errorhandler()
    return xform


def XformChangeBasis2(x0,y0,z0,x1,y1,z1):
    """
    Returns a change of basis transformation matrix of None on error
    Parameters:
      x0,y0,z0 = initial basis
      x1,y1,z1 = final basis
    """
    x0 = rhutil.coerce3dvector(x0)
    y0 = rhutil.coerce3dvector(y0)
    z0 = rhutil.coerce3dvector(z0)
    if x0 is None or y0 is None or z0 is None:
        return scriptcontext.errorhandler()
    x1 = rhutil.coerce3dvector(x1)
    y1 = rhutil.coerce3dvector(y1)
    z1 = rhutil.coerce3dvector(z1)
    if x1 is None or y1 is None or z1 is None:
        return scriptcontext.errorhandler()
    xform = Rhino.Geometry.Transform.ChangeBasis(x0,y0,z0,x1,y1,z1)
    if not xform.IsValid: return scriptcontext.errorhandler()
    return xform


def XformCPlaneToWorld(point, plane):
    """
    Transforms a point from construction plane coordinates to world coordinates
    Parameters:
      point = A 3-D point in construction plane coordinates.
      plane = The construction plane
    Returns:
      A 3-D point in world coordinates if successful.
      None if not successful, or on error.
    """
    point = rhutil.coerce3dpoint(point)
    plane = rhutil.coerceplane(plane)
    if point is None or plane is None: return scriptcontext.errorhandler()
    return plane.Origin + point.X*plane.XAxis + point.Y*plane.YAxis + point.Z*plane.ZAxis


def XformDeterminant(xform):
    """
    Returns the determinant of a transformation matrix. If the determinant of a
    transformation matrix is 0, the matrix is said to be singular. Singular
    matrices do not have inverses.
    Returns None on error
    """
    xform = rhutil.coercexform(xform)
    if xform is None: return scriptcontext.errorhandler()
    return xform.Determinant


def XformDiagonal(diagonal_value):
    """
    Returns a diagonal transformation matrix. Diagonal matrices are 3x3 with
    the bottom row [0,0,0,1]
    """
    return Rhino.Geometry.Transform(diagonal_value)


def XformIdentity():
    "returns the identity transformation matrix"
    return Rhino.Geometry.Transform.Identity


def XformInverse(xform):
    """
    Returns the inverse of a non-singular transformation matrix
    Returns None on error
    """
    xform = rhutil.coercexform(xform)
    rc, inverse = xform.TryGetInverse()
    if not rc: return scriptcontext.errorhandler()
    return inverse


def XformMirror(mirror_plane_point, mirror_plane_normal):
    """
    Creates a mirror transformation matrix
    Parameters:
      mirror_plane_point = point on the mirror plane
      mirror_plane_normal = a 3D vector that is normal to the mirror plane
    Returns:
      mirror Transform on success
      None on error
    """
    point = rhutil.coerce3dpoint(mirror_plane_point)
    normal = rhutil.coerce3dvector(mirror_plane_normal)
    if point is None or normal is None: return scriptcontext.errorhandler()
    return Rhino.Geometry.Transform.Mirror(point, normal)


def XformMultiply(xform1, xform2):
    """
    Multiplies two transformation matrices, where result = xform1 * xform2
    Returns:
      result transformation on success
      None on error
    """
    xform1 = rhutil.coercexform(xform1)
    xform2 = rhutil.coercexform(xform2)
    if xform1 is None or xform2 is None: return scriptcontext.errorhandler()
    return xform1*xform2


def XformPlanarProjection(plane):
    """
    Returns a transformation matrix that projects to a plane.
    Parameters
      plane = The plane to project to.
    Returns:
      The 4x4 transformation matrix.
      None on error.
    """
    plane = rhutil.coerceplane(plane)
    if plane is None: return scriptcontext.errorhandler()
    return Rhino.Geometry.Transform.PlanarProjection(plane)


def XformRotation1( initial_plane, final_plane ):
    """
    Returns a rotation transformation that maps initial_plane to final_plane.
    The planes should be right hand orthonormal planes.
    Returns:
      The 4x4 transformation matrix.
      None on error.
    """
    initial_plane = rhutil.coerceplane(initial_plane)
    final_plane = rhutil.coerceplane(final_plane)
    if initial_plane is None or final_plane is None:
        return scriptcontext.errorhandler()
    xform = Rhino.Geometry.Transform.PlaneToPlane(initial_plane, final_plane)
    if not xform.IsValid: return scriptcontext.errorhandler()
    return xform


def XformRotation2( angle_degrees, rotation_axis, center_point ):
    """
    Returns a rotation transformation
    Returns:
      The 4x4 transformation matrix.
      None on error.
    """
    axis = rhutil.coerce3dvector(rotation_axis)
    center = rhutil.coerce3dpoint(center_point)
    if axis is None or center is None: return scriptcontext.errorhandler()
    angle_rad = math.radians(angle_degrees)
    xform = Rhino.Geometry.Transform.Rotation(angle_rad, axis, center)
    if not xform.IsValid: return scriptcontext.errorhandler()
    return xform


def XformRotation3( start_direction, end_direction, center_point ):
    """
    Calculate the minimal transformation that rotates start_direction to
    end_direction while fixing center_point
    Parameters:
      start_direction, end_direction = 3d vectors
      center_point = the rotation center
    Returns:
      The 4x4 transformation matrix.
      None on error.
    """
    start = rhutil.coerce3dvector(start_direction)
    end = rhutil.coerce3dvector(end_direction)
    center = rhutil.coerce3dpoint(center_point)
    if start is None or end is None or center is None:
        return scriptcontext.errorhandler()
    xform = Rhino.Geometry.Transform.Rotation(start, end, center)
    if not xform.IsValid: return scriptcontext.errorhandler()
    return xform


def XformRotation4(x0, y0, z0, x1, y1, z1):
    """
    Returns a rotation transformation.
    Paramters:
      x0,y0,z0 = Vectors defining the initial orthonormal frame
      x1,y1,z1 = Vectors defining the final orthonormal frame
    Returns:
      The 4x4 transformation matrix.
      None on error.
    """
    x0 = rhutil.coerce3dveector(x0)
    y0 = rhutil.coerce3dveector(y0)
    z0 = rhutil.coerce3dveector(z0)
    x1 = rhutil.coerce3dveector(x1)
    y1 = rhutil.coerce3dveector(y1)
    z1 = rhutil.coerce3dveector(z1)
    if x0 is None or y0 is None or z0 is None: return scriptcontext.errorhandler()
    if x1 is None or y1 is None or z1 is None: return scriptcontext.errorhandler()
    xform = Rhino.Geometry.Transform.Rotation(x0,y0,z0,x1,y1,z1)
    if not xform.IsValid: return scriptcontext.errorhandler()
    return xform


def XformScale( scale, point=None ):
    """
    Creates a scale transformation
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
    point = rhutil.coerce3dpoint(point)
    if point is None: point = Rhino.Geometry.Point3d.Origin
    plane = Rhino.Geometry.Plane(point, Rhino.Geometry.Vector3d.ZAxis);
    xf = Rhino.Geometry.Transform.Scale(plane, factor[0], factor[1], factor[2])
    return xf


def XformTranslation(vector):
    "Creates a translation transformation matrix"
    vector = rhutil.coerce3dvector(vector)
    if vector is None: return scriptcontext.errorhandler()
    return Rhino.Geometry.Transform.Translation(vector)


def XformWorldtoCplane(point, plane):
    """
    Transforms a point from world coordinates to construction plane coordinates.
    Parameters:
      point = A 3-D point in world coordinates.
      plane = The construction plane
    Returns:
      A 3-D point in construction plane coordinates if successful.
      None if not successful, or on error.
    """
    point = rhutil.coerce3dpoint(point)
    plane = rhutil.coerceplane(plane)
    if point is None or plane is None: return scriptcontext.errorhandler()
    v = point - plane.Origin;
    return Rhino.Geometry.Point3d(v*plane.XAxis, v*plane.YAxis, v*plane.ZAxis)


def XformZero():
    "Returns a zero transformation matrix"
    return Rhino.Geometry.Transform()