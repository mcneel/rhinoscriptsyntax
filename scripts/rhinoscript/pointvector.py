import utility as rhutil
import Rhino
import scriptcontext
import math

def IsVectorParallelTo(vector1, vector2):
    """Compares two vectors to see if they are parallel
    Parameters:
      vector1, vector2 = the vectors to compare
    Returns:
      -1 = the vectors are anti-parallel
      0 = the vectors are not parallel
      1 = the vectors are parallel
    """
    vector1 = rhutil.coerce3dvector(vector1, True)
    vector2 = rhutil.coerce3dvector(vector2, True)
    return vector1.IsParallelTo(vector2)


def IsVectorPerpendicularTo(vector1, vector2):
    """Compares two vectors to see if they are perpendicular
    Parameters:
      vector1, vector2 = the vectors to compare
    Returns:
      True if vectors are perpendicular, otherwise False
    """
    vector1 = rhutil.coerce3dvector(vector1, True)
    vector2 = rhutil.coerce3dvector(vector2, True)
    return vector1.IsPerpendicularTo(vector2)


def IsVectorTiny(vector):
    """Verifies that a vector is very short. The X,Y,Z elements are <= 1.0e-12
    Parameters:
      vector - the vector to check
    Returns:
      True if the vector is tiny, otherwise False
    """
    vector = rhutil.coerce3dvector(vector, True)
    return vector.IsTiny( 1.0e-12 )


def IsVectorZero(vector):
    """Verifies that a vector is zero, or tiny. The X,Y,Z elements are equal to 0.0
    Parameters:
      vector - the vector to check
    Returns:
      True if the vector is zero, otherwise False
    """
    vector = rhutil.coerce3dvector(vector, True)
    return vector.IsZero


def PointAdd(point1, point2):
    """Adds a 3D point or a 3D vector to a 3D point
    Parameters:
      point1, point2 = the points to add
    Returns:
      the resulting 3D point if successful
      None on error
    """
    point1 = rhutil.coerce3dpoint(point1, True)
    point2 = rhutil.coerce3dpoint(point2, True)
    return point1+point2


#[skipping PointArrayBoundingBox]

def PointArrayClosestPoint(points, test_point):
    """Finds the point in a list of 3D points that is closest to a test point
    Parameters:
      points = list of points
      test_point = the point to compare against
    Returns:
      index of the element in the point list that is closest to the test point
    """
    points = rhutil.coerce3dpointlist(points, True)
    test_point = rhutil.coerce3dpoint(test_point, True)
    index = Rhino.Collections.Point3dList.ClosestIndexInList(points, test_point)
    if index<0: return scriptcontext.errorhandler()
    return index


def PointArrayTransform(points, xform):
    """Transforms a list of 3D points
    Parameters:
      points = list of 3D points
      xform = transformation to apply
    Returns:
      list of transformed points on success
    """
    points = rhutil.coerce3dpointlist(points, True)
    xform = rhutil.coercexform(xform, True)
    rc = [xform*point for point in points]
    return rc


def PointClosestObject(point, object_ids):
    """Finds the object that is closest to a test point
    Parameters:
      point = point to test
      object_id = identifiers of one or more objects
    Returns:
      (closest object_id, point on object) on success
      None on failure
    """
    object_ids = rhutil.coerceguidlist(object_ids)
    point = rhutil.coerce3dpoint(point, True)
    closest = None
    for id in object_ids:
        geom = rhutil.coercegeometry(id, True)
        point_geometry = geom
        if isinstance(point_geometry, Rhino.Geometry.Point):
            distance = point.DistanceTo( point_geometry.Location )
            if closest is None or distance<closest[0]:
                closest = distance, id, point_geometry.Location
            continue
        point_cloud = geom
        if isinstance(point_cloud, Rhino.Geometry.PointCloud):
            index = point_cloud.ClosestPoint(point)
            if index>=0:
                distance = point.DistanceTo( point_cloud[index].Location )
                if closest is None or distance<closest[0]:
                    closest = distance, id, point_cloud[index].Location
            continue
        curve = geom
        if isinstance(curve, Rhino.Geometry.Curve):
            rc, t = curve.ClosestPoint(point)
            if rc:
                distance = point.DistanceTo( curve.PointAt(t) )
                if closest is None or distance<closest[0]:
                    closest = distance, id, curve.PointAt(t)
            continue
        brep = geom
        if isinstance(brep, Rhino.Geometry.Brep):
            brep_closest = brep.ClosestPoint(point)
            distance = point.DistanceTo( brep_closest )
            if closest is None or distance<closest[0]:
                closest = distance, id, brep_closest
            continue
        mesh = geom
        if isinstance(mesh, Rhino.Geometry.Mesh):
            mesh_closest = mesh.ClosestPoint(point)
            distance = point.DistanceTo( mesh_closest )
            if closest is None or distance<closest[0]:
                closest = distance, id, mesh_closest
            continue
    if not closest: return scriptcontext.errorhandler()
    return closest[1], closest[2]


def PointCompare(point1, point2, tolerance=None):
    """Compares two 3D points
    Parameters:
      point1, point2 = the points to compare
      tolerance [opt] = tolerance to use for comparison. If omitted,
        Rhino's internal zero tolerance is used
    Returns:
      True or False
    """
    point1 = rhutil.coerce3dpoint(point1, True)
    point2 = rhutil.coerce3dpoint(point2, True)
    if tolerance is None: tolerance = Rhino.RhinoMath.ZeroTolerance
    vector = point2-point1
    return vector.IsTiny(tolerance)


def PointDivide(point, divide):
    """Divides a 3D point by a value
    Parameters:
      point = the point to divide
      divide = a non-zero value to divide
    Returns:
      resulting point
    """
    point = rhutil.coerce3dpoint(point, True)
    return point/divide


def PointsAreCoplanar(points, tolerance=1.0e-12):
    """Verifies that a list of 3D points are coplanar
    Parameters:
      points = list of 3D points
      tolerance[opt] = tolerance to use when verifying
    Returns:
      True or False
    """
    points = rhutil.coerce3dpointlist(points, True)
    return Rhino.Geometry.Point3d.ArePointsCoplanar(points, tolerance)


def PointScale(point, scale):
    """Scales a 3D point by a value
    Parameters:
      point = the point to divide
      scale = scale factor to apply
    Returns:
      resulting point on success
    """
    point = rhutil.coerce3dpoint(point, True)
    return point*scale


def PointSubtract(point1, point2):
    """Subtracts a 3D point or a 3D vector from a 3D point
    Parameters:
      point1, point2 = the points to subtract
    Returns:
      the resulting 3D point if successful
    """
    point1 = rhutil.coerce3dpoint(point1, True)
    point2 = rhutil.coerce3dpoint(point2, True)
    v = point1-point2
    return Rhino.Geometry.Point3d(v)

  
def PointTransform(point, xform):
    """Transforms a 3D point
    Paramters:
      point = the point to transform
      xform = a valid 4x4 transformation matrix
    Returns:
      transformed vector on success
    """
    point = rhutil.coerce3dpoint(point, True)
    xform = rhutil.coercexform(xform, True)
    return xform*point


def ProjectPointToMesh(points, mesh_ids, direction):
    """Projects one or more points onto one or more meshes
    Parameters:
      points = one or more 3D points
      mesh_ids = identifiers of one or more meshes
      direction = direction vector to project the points
    Returns:
     list of projected points on success
    """
    pts = rhutil.coerce3dpointlist(points, False)
    if pts is None:
        pts = [rhutil.coerce3dpoint(points, True)]
    direction = rhutil.coerce3dvector(direction, True)
    id = rhutil.coerceguid(mesh_ids, False)
    if id: mesh_ids = [id]
    meshes = [rhutil.coercemesh(id, True) for id in mesh_ids]
    tolerance = scriptcontext.doc.ModelAbsoluteTolerance
    rc = Rhino.Geometry.Intersect.Intersection.ProjectPointsToMeshes(meshes, pts, direction, tolerance)
    return rc


def ProjectPointToSurface(points, surface_ids, direction):
    """Projects one or more points onto one or more surfaces or polysurfaces
    Parameters:
      points = one or more 3D points
      surface_ids = identifiers of one or more surfaces/polysurfaces
      direction = direction vector to project the points
    Returns:
     list of projected points on success
    """
    pts = rhutil.coerce3dpointlist(points)
    if pts is None:
        pts = [rhutil.coerce3dpoint(points, True)]
    direction = rhutil.coerce3dvector(direction, True)
    id = rhutil.coerceguid(surface_ids, False)
    if id: surface_ids = [id]
    breps = [rhutil.coercebrep(id, True) for id in surface_ids]
    tolerance = scriptcontext.doc.ModelAbsoluteTolerance
    rc = Rhino.Geometry.Intersect.Intersection.ProjectPointsToBreps(breps, pts, direction, tolerance)
    return rc


def PullPoints(object_id, points):
    """Pulls an array of points to a surface or mesh object. For more
    information, see the Rhino help file Pull command
    Parameters:
      object_id = the identifier of the surface or mesh object that pulls
      points = list of 3D points
    Returns:
      list of 3D points
    """
    id = rhutil.coerceguid(object_id, True)
    points = rhutil.coerce3dpointlist(points, True)
    mesh = rhutil.coercemesh(id, False)
    if mesh:
        points = mesh.PullPointsToMesh(points)
        return list(points)
    brep = rhutil.coercebrep(id, False)
    if brep and brep.Faces.Count==1:
        tolerance = scriptcontext.doc.ModelAbsoluteTolerance
        points = brep.Faces[0].PullPointsToFace(points, tolerance)
        return list(points)
    return []


def VectorAdd(vector1, vector2):
    """Adds two 3D vectors
    Parameters:
      vector1, vector2 = the vectors to add
    Returns:
      the resulting 3D vector if successful
    """
    vector1 = rhutil.coerce3dvector(vector1, True)
    vector2 = rhutil.coerce3dvector(vector2, True)
    return vector1+vector2


def VectorAngle(vector1, vector2):
    "Returns the angle, in degrees, between two 3-D vectors"
    vector1 = rhutil.coerce3dvector(vector1, True)
    vector2 = rhutil.coerce3dvector(vector2, True)
    vector1 = Rhino.Geometry.Vector3d(vector1.X, vector1.Y, vector1.Z)
    vector2 = Rhino.Geometry.Vector3d(vector2.X, vector2.Y, vector2.Z)
    if not vector1.Unitize() or not vector2.Unitize():
        raise ValueError("unable to unitize vector")
    dot = vector1 * vector2
    dot = rhutil.clamp(-1,1,dot)
    radians = math.acos(dot)
    return math.degrees(radians)


def VectorCompare(vector1, vector2):
    """Compares two 3D vectors
    Parameters:
      vector1, vector2 = the vectors to compare
    Returns:
      -1 if vector1 is less than vector2
      0 if vector1 is equal to vector2
      1 if vector1 is greater than vector2
    """
    vector1 = rhutil.coerce3dvector(vector1, True)
    vector2 = rhutil.coerce3dvector(vector2, True)
    return vector1.CompareTo(vector2)


def VectorCreate(to_point, from_point):
    """Creates a vector from two 3D points
    Parameters:
      to_point, from_point = the points defining the vector
    Returns:
      the resulting vector if successful
    """
    to_point = rhutil.coerce3dpoint(to_point, True)
    from_point = rhutil.coerce3dpoint(from_point, True)
    return to_point-from_point


def VectorCrossProduct(vector1, vector2):
    """Calculates the cross product of two 3D vectors
    Parameters:
      vector1, vector2 = the vectors to perform cross product on
    Returns:
      the resulting vector if successful
    """
    vector1 = rhutil.coerce3dvector(vector1, True)
    vector2 = rhutil.coerce3dvector(vector2, True)
    return Rhino.Geometry.Vector3d.CrossProduct( vector1, vector2 )


def VectorDivide(vector, divide):
    """Divides a 3D vector by a value
    Parameters:
      vector = the vector to divide
      divide = a non-zero value to divide
    Returns:
      resulting vector on success
    """
    vector = rhutil.coerce3dvector(vector, True)
    return vector/divide


def VectorDotProduct(vector1, vector2):
    """Calculates the dot product of two 3D vectors
    Parameters:
      vector1, vector2 = the vectors to perform the dot product on
    Returns:
      the resulting dot product if successful
    """
    vector1 = rhutil.coerce3dvector(vector1, True)
    vector2 = rhutil.coerce3dvector(vector2, True)
    return vector1*vector2


def VectorLength(vector):
    "Returns the length of a 3D vector"
    vector = rhutil.coerce3dvector(vector, True)
    return vector.Length


def VectorMultiply(vector1, vector2):
    """Multiplies two 3D vectors
    Parameters:
      vector1, vector2 = the vectors to multiply
    Returns:
      the resulting inner (dot) product if successful
    """
    return VectorDotProduct(vector1, vector2)


def VectorReverse(vector):
    """Reverses the direction of a 3D vector
    Parameters:
      vector = the vector to reverse
    Returns:
      reversed vector on success
    """
    vector = rhutil.coerce3dvector(vector, True)
    rc = Rhino.Geometry.Vector3d(vector.X, vector.Y, vector.Z)
    rc.Reverse()
    return rc


def VectorRotate(vector, angle_degrees, axis):
    """Rotates a 3D vector
    Parameters:
      vector = the vector to rotate
      angle_degrees = rotation angle
      axis = axis of rotation
    Returns:
      rotated vector on success
    """
    vector = rhutil.coerce3dvector(vector, True)
    axis = rhutil.coerce3dvector(axis, True)
    angle_radians = Rhino.RhinoMath.ToRadians(angle_degrees)
    rc = Rhino.Geometry.Vector3d(vector.X, vector.Y, vector.Z)
    if not rc.Rotate(angle_radians, axis): return scriptcontext.errorhandler()
    return rc


def VectorScale(vector, scale):
    """Scales a 3-D vector
    Parameters:
      vector = the vector to scale
      scale = scale factor to apply
    Returns:
      resulting vector on success
    """
    vector = rhutil.coerce3dvector(vector, True)
    return vector*scale


def VectorSubtract(vector1, vector2):
    """Subtracts two 3D vectors
    Parameters:
      vector1 = the vector to subtract from
      vector2 = the vector to subtract
    Returns:
      the resulting 3D vector if successful
    """
    vector1 = rhutil.coerce3dvector(vector1, True)
    vector2 = rhutil.coerce3dvector(vector2, True)
    return vector1-vector2


def VectorTransform(vector, xform):
    """Transforms a 3D vector
    Paramters:
      vector = the vector to transform
      xform = a valid 4x4 transformation matrix
    Returns:
      transformed vector on success
    """
    vector = rhutil.coerce3dvector(vector, True)
    xform = rhutil.coercexform(xform, True)
    return xform*vector


def VectorUnitize(vector):
    """Unitizes, or normalizes a 3D vector. Note, zero vectors cannot be unitized
    Parameters:
      vector = the vector to unitize
    Returns:
      unitized vector on success
      None on error
    """
    vector = rhutil.coerce3dvector(vector, True)
    rc = Rhino.Geometry.Vector3d(vector.X, vector.Y, vector.Z)
    if not rc.Unitize(): return scriptcontext.errorhandler()
    return rc
