import utility as rhutil
import Rhino
import scriptcontext
import math

def IsVectorParallelTo( vector1, vector2 ):
    """
    Compares two vectors to see if they are parallel
    Parameters:
      vector1, vector2 = the vectors to compare
    Returns:
      -1 = the vectors are anti-parallel
      0 = the vectors are not parallel
      1 = the vectors are parallel
      None on error   
    """
    vector1 = rhutil.coerce3dvector(vector1)
    vector2 = rhutil.coerce3dvector(vector2)
    if vector1 is None or vector2 is None: return scriptcontext.errorhandler()
    return vector1.IsParallelTo(vector2)


def IsVectorPerpendicularTo( vector1, vector2 ):
    """
    Compares two vectors to see if they are perpendicular
    Parameters:
      vector1, vector2 = the vectors to compare
    Returns:
      True if vectors are perpendicular, otherwise False
      None on error   
    """
    vector1 = rhutil.coerce3dvector(vector1)
    vector2 = rhutil.coerce3dvector(vector2)
    if vector1 is None or vector2 is None: return scriptcontext.errorhandler()
    return vector1.IsPerpendicularTo(vector2)


def IsVectorTiny(vector):
    """
    Verifies that a vector is very short. The X,Y,Z elements are <= 1.0e-12
    Parameters:
      vector - the vector to check
    Returns:
      True if the vector is tiny, otherwise False
      None on error
    """
    vector = rhutil.coerce3dvector(vector)
    if vector is None: return scriptcontext.errorhandler()
    return vector.IsTiny( 1.0e-12 )


def IsVectorZero(vector):
    """
    Verifies that a vector is zero, or tiny. The X,Y,Z elements are equal to 0.0
    Parameters:
      vector - the vector to check
    Returns:
      True if the vector is zero, otherwise False
      None on error
    """
    vector = rhutil.coerce3dvector(vector)
    if vector is None: return scriptcontext.errorhandler()
    return vector.IsZero


def PointAdd(point1, point2):
    """
    Adds a 3-D point or a 3-D vector to a 3-D point
    Parameters:
      point1, point2 = the points to add
    Returns:
      the resulting 3D point if successful
      None on error
    """
    point1 = rhutil.coerce3dpoint(point1)
    point2 = rhutil.coerce3dpoint(point2)
    if point1 is None or point2 is None: return scriptcontext.errorhandler()
    return point1+point2


#[skipping PointArrayBoundingBox]

def PointArrayClosestPoint(points, test_point):
    """
    Finds the point in a list of 3D points that is closest to a test point
    Parameters:
      points = list of points
      test_point = the point to compare against
    Returns:
      index of the element in the point list that is closest to the test point
      None on error
    """
    points = rhutil.coerce3dpointlist(points)
    test_point = rhutil.coerce3dpoint(test_point)
    if points is None or test_point is None: return scriptcontext.errorhandler()
    index = Rhino.Collections.Point3dList.ClosestIndexInList(points, test_point)
    if index<0: return scriptcontext.errorhandler()
    return index


def PointArrayTransform(points, xform):
    """
    Transforms a list of 3-D points
    Parameters:
      points = list of 3-D points
      xform = transformation to apply
    Returns:
      list of transformed points on success
      None on error
    """
    points = rhutil.coerce3dpointlist(points)
    xform = rhutil.coercexform(xform)
    if points is None or xform is None: return scriptcontext.errorhandler()
    rc = [xform*point for point in points]
    return rc


def PointCompare(point1, point2, tolerance=None):
    """
    Compares two 3-D points
    Parameters:
      point1, point2 = the points to compare
      tolerance [opt] = tolerance to use for comparison. If omitted,
        Rhino's internal zero tolerance is used
    Returns:
      True or False
      None on error
    """
    point1 = rhutil.coerce3dpoint(point1)
    point2 = rhutil.coerce3dpoint(point2)
    if point1 is None or point2 is None: return scriptcontext.errorhandler()
    if tolerance is None: tolerance = Rhino.RhinoMath.ZeroTolerance
    vector = point2-point1
    return vector.IsTiny(tolerance)


def PointDivide( point, divide ):
    """
    Divides a 3-D point by a value
    Parameters:
      point = the point to divide
      divide = a non-zero value to divide
    Returns:
      resulting point on success
      None on error
    """
    point = rhutil.coerce3dpoint(point)
    if divide==0.0 or point is None: return scriptcontext.errorhandler()
    return point/divide


def PointsAreCoplanar(points, tolerance=1.0e-12):
    """
    Verifies that a list of 3D points are coplanar
    Parameters:
      points = list of 3D points
      tolerance[opt] = tolerance to use when verifying
    Returns:
      True or False
      None on error
    """
    points = rhutil.coerce3dpointlist(points)
    if points is None: return scriptcontext.errorhandler()
    return Rhino.Geometry.Point3d.ArePointsCoplanar(points, tolerance)


def PointScale(point, scale):
    """
    Scales a 3-D point by a value
    Parameters:
      point = the point to divide
      scale = scale factor to apply
    Returns:
      resulting point on success
      None on error
    """
    point = rhutil.coerce3dpoint(point)
    if point is None: return scriptcontext.errorhandler()
    return point*scale


def PointSubtract(point1, point2):
    """
    Subtracts a 3-D point or a 3-D vector from a 3-D point
    Parameters:
      point1, point2 = the points to subtract
    Returns:
      the resulting 3D point if successful
      None on error
    """
    point1 = rhutil.coerce3dpoint(point1)
    point2 = rhutil.coerce3dpoint(point2)
    if point1 is None or point2 is None: return scriptcontext.errorhandler()
    v = point1-point2
    return Rhino.Geometry.Point3d(v)

  
def PointTransform(point, xform):
    """
    Transforms a 3-D point
    Paramters:
      point = the point to transform
      xform = a valid 4x4 transformation matrix
    Returns:
      transformed vector on success
      None on error
    """
    point = rhutil.coerce3dpoint(point)
    xform = rhutil.coercexform(xform)
    if point is None or xform is None: return scriptcontext.errorhandler()
    return xform*point


def ProjectPointToMesh(points, mesh_ids, direction):
    """
    Projects one or more points onto one or more meshes
    Parameters:
      points = one or more 3D points
      mesh_ids = identifiers of one or more meshes
      direction = direction vector to project the points
    Returns:
     list of projected points on success
     None on error
    """
    points = rhutil.coerce3dpointlist(points)
    direction = rhutil.coerce3dvector(direction)
    if points is None or direction is None: return scriptcontext.errorhandler()
    if rhutil.coerceguid(mesh_ids): mesh_ids = [mesh_ids]
    meshes = []
    for id in mesh_ids:
        id = rhutil.coerceguid(id)
        if id is None: return scriptcontext.errorhandler()
        objref = Rhino.DocObjects.ObjRef(id)
        mesh = objref.Mesh()
        objref.Dispose()
        if mesh is None: return scriptcontext.errorhandler()
        meshes.append(mesh)
    tolerance = scriptcontext.doc.ModelAbsoluteTolerance
    rc = Rhino.Geometry.Intersect.Intersection.ProjectPointsToMeshes(meshes, points, direction, tolerance)
    return rc


def ProjectPointToSurface(points, surface_ids, direction):
    """
    Projects one or more points onto one or more surfaces or polysurfaces
    Parameters:
      points = one or more 3D points
      surface_ids = identifiers of one or more surfaces/polysurfaces
      direction = direction vector to project the points
    Returns:
     list of projected points on success
     None on error
    """
    points = rhutil.coerce3dpointlist(points)
    if points is None:
        point = rhutil.coerce3dpoint(points)
        if point is not None: points = [point]
    direction = rhutil.coerce3dvector(direction)
    if points is None or direction is None: return scriptcontext.errorhandler()
    if rhutil.coerceguid(surface_ids): surface_ids = [surface_ids]
    breps = []
    for id in surface_ids:
        id = rhutil.coerceguid(id)
        if id is None: return scriptcontext.errorhandler()
        objref = Rhino.DocObjects.ObjRef(id)
        brep = objref.Brep()
        objref.Dispose()
        if brep is None: return scriptcontext.errorhandler()
        breps.append(brep)
    tolerance = scriptcontext.doc.ModelAbsoluteTolerance
    rc = Rhino.Geometry.Intersect.Intersection.ProjectPointsToBreps(breps, points, direction, tolerance)
    return rc


def PullPoints(object_id, points):
    """
    Pulls an array of points to a surface or mesh object. For more information, see the Rhino help
    file for information on the Pull command
    Parameters:
      object_id = the identifier of the surface or mesh object that pulls
      points = list of 3d points
    Returns:
      list of 3d points
      None on error
    """
    id = rhutil.coerceguid(object_id)
    points = rhutil.coerce3dpointlist(points)
    if id is None or points is None: return scriptcontext.errorhandler()
    mesh = rhutil.coercemesh(id)
    if mesh is not None:
        points = mesh.PullPointsToMesh(points)
        if points is None: return scriptcontext.errorhandler()
        return list(points)
    brep = rhutil.coercebrep(id)
    if brep is not None and brep.Faces.Count==1:
        tolerance = scriptcontext.doc.ModelAbsoluteTolerance
        points = brep.Faces[0].PullPointsToFace(points, tolerance)
        if points is None: return scriptcontext.errorhandler()
        return list(points)
    return scriptcontext.errorhandler()        


def VectorAdd(vector1, vector2):
    """
    Adds two 3-D vectors
    Parameters:
      vector1, vector2 = the vectors to add
    Returns:
      the resulting 3D vector if successful
      None on error
    """
    vector1 = rhutil.coerce3dvector(vector1)
    vector2 = rhutil.coerce3dvector(vector2)
    if vector1 is None or vector2 is None: return scriptcontext.errorhandler()
    return vector1+vector2


def VectorAngle(vector1, vector2):
    "Returns the angle, in degrees, between two 3-D vectors"
    vector1 = rhutil.coerce3dvector(vector1)
    vector2 = rhutil.coerce3dvector(vector2)
    if vector1 is None or vector2 is None: return scriptcontext.errorhandler()
    vector1 = Rhino.Geometry.Vector3d(vector1.X, vector1.Y, vector1.Z)
    vector2 = Rhino.Geometry.Vector3d(vector2.X, vector2.Y, vector2.Z)
    if not vector1.Unitize() or not vector2.Unitize():
        return scriptcontext.errorhandler()
    dot = vector1 * vector2
    dot = rhutil.clamp(-1,1,dot)
    radians = math.acos(dot)
    return math.degrees(radians)


def VectorCompare(vector1, vector2):
    """
    Compares two 3-D vectors
    Parameters:
      vector1, vector2 = the vectors to compare
    Returns:
      -1 if vector1 is less than vector2
      0 if vector1 is equal to vector2
      1 if vector1 is greater than vector2
      None on error
    """
    vector1 = rhutil.coerce3dvector(vector1)
    vector2 = rhutil.coerce3dvector(vector2)
    if vector1 is None or vector2 is None: return scriptcontext.errorhandler()
    return vector1.CompareTo(vector2)


def VectorCreate(to_point, from_point):
    """
    Creates a vector from two 3-D points
    Parameters:
      to_point, from_point = the points defining the vector
    Returns:
      the resulting vector if successful
      None on error
    """
    to_point = rhutil.coerce3dpoint(to_point)
    from_point = rhutil.coerce3dpoint(from_point)
    if to_point is None or from_point is None:
        return scriptcontext.errorhandler()
    return to_point-from_point


def VectorCrossProduct( vector1, vector2 ):
    """
    Calculates the cross product of two 3D vectors
    Parameters:
      vector1, vector2 = the vectors to perform cross product on
    Returns:
      the resulting vector if successful
      None on error
    """
    vector1 = rhutil.coerce3dvector(vector1)
    vector2 = rhutil.coerce3dvector(vector2)
    if vector1 is None or vector2 is None: return scriptcontext.errorhandler()
    return Rhino.Geometry.Vector3d.CrossProduct( vector1, vector2 )


def VectorDivide( vector, divide ):
    """
    Divides a 3-D vector by a value
    Parameters:
      vector = the vector to divide
      divide = a non-zero value to divide
    Returns:
      resulting vector on success
      None on error
    """
    vector = rhutil.coerce3dvector(vector)
    if divide==0.0 or vector is None: return scriptcontext.errorhandler()
    return vector/divide


def VectorDotProduct( vector1, vector2 ):
    """
    Calculates the dot product of two 3-D vectors
    Parameters:
      vector1, vector2 = the vectors to perform the dot product on
    Returns:
      the resulting dot product if successful
      None on error
    """
    vector1 = rhutil.coerce3dvector(vector1)
    vector2 = rhutil.coerce3dvector(vector2)
    if vector1 is None or vector2 is None: return scriptcontext.errorhandler()
    return vector1*vector2


def VectorLength( vector ):
    "Returns the length of a 3-D vector"
    vector = rhutil.coerce3dvector(vector)
    if vector is None: return scriptcontext.errorhandler()
    return vector.Length


def VectorMultiply( vector1, vector2 ):
    """
    Multiplies two 3-D vectors
    Parameters:
      vector1, vector2 = the vectors to multiply
    Returns:
      the resulting inner (dot) product if successful
      None on error
    """
    return VectorDotProduct(vector1, vector2)


def VectorReverse( vector ):
    """
    Reverses the direction of a 3-D vector
    Parameters:
      vector = the vector to reverse
    Returns:
      reversed vector on success
      None on error
    """
    vector = rhutil.coerce3dvector(vector)
    if vector is None: return scriptcontext.errorhandler()
    rc = Rhino.Geometry.Vector3d(vector.X, vector.Y, vector.Z)
    rc.Reverse()
    return rc


def VectorRotate( vector, angle_degrees, axis ):
    """
    Rotates a 3-D vector
    Parameters:
      vector = the vector to rotate
      angle_degrees = rotation angle
      axis = axis of rotation
    Returns:
      rotated vector on success
      None on error
    """
    vector = rhutil.coerce3dvector(vector)
    axis = rhutil.coerce3dvector(axis)
    if vector is None or axis is None: return scriptcontext.errorhandler()
    angle_radians = Rhino.RhinoMath.ToRadians(angle_degrees)
    rc = Rhino.Geometry.Vector3d(vector.X, vector.Y, vector.Z)
    if not rc.Rotate(angle_radians, axis): return scriptcontext.errorhandler()
    return rc


def VectorScale(vector, scale):
    """
    Scales a 3-D vector
    Parameters:
      vector = the vector to scale
      scale = scale factor to apply
    Returns:
      resulting vector on success
      None on error
    """
    vector = rhutil.coerce3dvector(vector)
    if vector is None: return scriptcontext.errorhandler()
    return vector*scale


def VectorSubtract(vector1, vector2):
    """
    Subtracts two 3-D vectors
    Parameters:
      vector1 = the vector to subtract from
      vector2 = the vector to subtract
    Returns:
      the resulting 3D vector if successful
      None on error
    """
    vector1 = rhutil.coerce3dvector(vector1)
    vector2 = rhutil.coerce3dvector(vector2)
    if vector1 is None or vector2 is None: return scriptcontext.errorhandler()
    return vector1-vector2


def VectorTransform(vector, xform):
    """
    Transforms a 3-D vector
    Paramters:
      vector = the vector to transform
      xform = a valid 4x4 transformation matrix
    Returns:
      transformed vector on success
      None on error
    """
    vector = rhutil.coerce3dvector(vector)
    xform = rhutil.coercexform(xform)
    if vector is None or xform is None: return scriptcontext.errorhandler()
    return xform*vector


def VectorUnitize(vector):
    """
    Unitizes, or normalizes a 3-D vector. Note, zero vectors cannot be unitized
    Parameters:
      vector = the vector to unitize
    Returns:
      unitized vector on success
      None on error
    """
    vector = rhutil.coerce3dvector(vector)
    if vector is None: return scriptcontext.errorhandler()
    rc = Rhino.Geometry.Vector3d(vector.X, vector.Y, vector.Z)
    if not rc.Unitize(): return scriptcontext.errorhandler()
    return rc
