import scriptcontext
import utility as rhutil
import Rhino
import System.Guid, System.Array, System.Drawing.Color


def AddMesh(vertices, face_vertices, vertex_normals=None, texture_coordinates=None, vertex_colors=None):
    """Adds a mesh object to the document
    Parameters:
      vertices = list of 3D points defining the vertices of the mesh
      face_vertices = list containing lists of 3 or 4 numbers that define the
        vertex indices for each face of the mesh. If the third a fourth vertex
        indices of a face are identical, a triangular face will be created.
      vertex_normals[opt] = list of 3D vectors defining the vertex normals of
        the mesh. Note, for every vertex, there must be a corresponding vertex
        normal
      texture_coordinates[opt] = list of 2D texture coordinates. Note, for
        every vertex, there must be a corresponding texture coordinate
      vertex_colors[opt] = a list of color values. Note, for every vertex,
        there must be a corresponding vertex color
    Returns:
      Identifier of the new object if successful
      None on error
    """
    mesh = Rhino.Geometry.Mesh()
    for a, b, c in vertices: mesh.Vertices.Add(a, b, c)
    for face in face_vertices:
        if len(face)<4:
            mesh.Faces.AddFace(face[0], face[1], face[2])
        else:
            mesh.Faces.AddFace(face[0], face[1], face[2], face[3])
    if vertex_normals:
        count = len(vertex_normals)
        normals = System.Array.CreateInstance(Rhino.Geometry.Vector3f, count)
        for i, normal in enumerate(vertex_normals):
            normals[i] = Rhino.Geometry.Vector3f(normal[0], normal[1], normal[2])
        mesh.Normals.SetNormals(normals)
    if texture_coordinates:
        count = len(texture_coordinates)
        tcs = System.Array.CreateInstance(Rhino.Geometry.Point2f, count)
        for i, tc in enumerate(texture_coordinates):
            tcs[i] = Rhino.Geometry.Point2f(tc[0], tc[1], tc[2])
        mesh.TextureCoordinates.SetTextureCoordinates(tcs)
    if vertex_colors:
        count = len(vertex_colors)
        colors = System.Array.CreateInstance(System.Drawing.Color, count)
        for i, color in enumerate(vertex_colors):
            colors[i] = System.Drawing.Color.FromArgb(color[0], color[1], color[2])
        mesh.VertexColors.SetColors(colors)
    rc = scriptcontext.doc.Objects.AddMesh(mesh)
    if rc==System.Guid.Empty: raise Exception("unable to add mesh to document")
    scriptcontext.doc.Views.Redraw()
    return rc


def AddPlanarMesh(object_id, delete_input=False):
    """Creates a planar mesh from a closed, planar curve
    Parameters:
      object_id = identifier of a closed, planar curve
      delete_input[opt] = if True, delete the input curve defined by object_id
    Returns:
      id of the new mesh on success
      None on error
    """
    curve = rhutil.coercecurve(object_id, -1, True)
    mesh = Rhino.Geometry.Mesh.CreateFromPlanarBoundary(curve, Rhino.Geometry.MeshingParameters.Default)
    if not mesh: return scriptcontext.errorhandler()
    rc = scriptcontext.doc.Objects.AddMesh(mesh)
    if rc==System.Guid.Empty: raise Exception("unable to add mesh to document")
    scriptcontext.doc.Views.Redraw()
    return rc


def CurveMeshIntersection(curve_id, mesh_id, return_faces=False):
    """Calculates the intersection of a curve object and a mesh object
    Parameters:
      curve_id = identifier of a curve object
      mesh_id = identifier or a mesh object
      return_faces[opt] = return both intersection points and face indices.
        If False, then just the intersection points are returned
    Returns:
      if return_false is omitted or False, then a list of intersection points
      if return_false is True, the a one-dimensional list containing information
        about each intersection. Each element contains the following two elements
        (point of intersection, mesh face index where intersection lies)
      None on error
    """
    curve = rhutil.coercecurve(curve_id, -1, True)
    mesh = rhutil.coercemesh(mesh_id, True)
    tolerance = scriptcontext.doc.ModelAbsoluteTolerance
    polylinecurve = curve.ToPolyline(0,0,0,0,0.0,tolerance,0.0,0.0,True)
    pts, faceids = Rhino.Geometry.Intersect.Intersection.MeshPolyline(mesh, polylinecurve)
    if not pts: return scriptcontext.errorhandler()
    pts = list(pts)
    if return_faces:
        faceids = list(faceids)
        return zip(pts, faceids)
    return pts


def DisjointMeshCount(object_id):
    """Returns number of meshes that could be created by calling SplitDisjointMesh
    Parameters:
      object_id = identifier of a mesh object
    Returns:
      The number of meshes that could be created
    """
    mesh = rhutil.coercemesh(object_id, True)
    return mesh.DisjointMeshCount


def DuplicateMeshBorder(mesh_id):
    """Creates curves that duplicates a mesh border
    Parameters:
      mesh_id = identifier of a mesh object
    Returns:
      list of curve ids on success
      None on error
    """
    mesh = rhutil.coercemesh(mesh_id, True)
    polylines = mesh.GetNakedEdges()
    rc = []
    if polylines:
        for polyline in polylines:
            id = scriptcontext.doc.Objects.AddPolyline(polyline)
            if id!=System.Guid.Empty: rc.append(id)
    if rc: scriptcontext.doc.Views.Redraw()
    return rc


def ExplodeMeshes(mesh_ids, delete=False):
    """Explodes a mesh object, or mesh objects int submeshes. A submesh is a
    collection of mesh faces that are contained within a closed loop of
    unwelded mesh edges. Unwelded mesh edges are where the mesh faces that
    share the edge have unique mesh vertices (not mesh topology vertices)
    at both ends of the edge
    Parameters:
      mesh_ids = list of mesh identifiers
      delete[opt] = delete the input meshes
    Returns:
      List of identifiers
    """
    id = rhutil.coerceguid(mesh_ids)
    if id: mesh_ids = [mesh_ids]
    rc = []
    for mesh_id in mesh_ids:
        mesh = rhutil.coercemesh(mesh_id, True)
        if mesh:
            submeshes = mesh.ExplodeAtUnweldedEdges()
            if submeshes:
                for submesh in submeshes:
                    id = scriptcontext.doc.Objects.AddMesh(submesh)
                    if id!=System.Guid.Empty: rc.append(id)
    if rc: scriptcontext.doc.Views.Redraw()
    return rc


def IsMesh(object_id):
    "Verifies if an object is a mesh"
    mesh = rhutil.coercemesh(object_id)
    return mesh is not None


def IsMeshClosed(object_id):
    """Verifies a mesh object is closed
    Parameters:
      object_id = identifier of a mesh object
    """
    mesh = rhutil.coercemesh(object_id, True)
    return mesh.IsClosed


def IsMeshManifold(object_id):
    """Verifies a mesh object is manifold. A mesh for which every edge is shared
    by at most two faces is called manifold. If a mesh has at least one edge
    that is shared by more than two faces, then that mesh is called non-manifold
    Parameters:
      object_id = identifier of a mesh object
    """
    mesh = rhutil.coercemesh(object_id, True)
    rc = mesh.IsManifold(True)
    return rc[0]


def IsPointOnMesh(object_id, point):
    """Verifies that a point is on a mesh
    Parameters:
      object_id = identifier of a mesh object
      point = test point
    """
    mesh = rhutil.coercemesh(object_id, True)
    point = rhutil.coerce3dpoint(point, True)
    max_distance = Rhino.RhinoMath.SqrtEpsilon
    face, pt = mesh.ClosestPoint(point, max_distance)
    return face>=0


def MeshArea(object_ids):
    """Returns the approximate area of one or more mesh objects
    Parameters:
      object_ids = identifiers of one or more mesh objects
    Returns:
      a list containing 3 numbers if successful where
        element[0] = number of meshes used in calculation
        element[1] = total area of all meshes
        element[2] = the error estimate
      None if not successful
    """
    id = rhutil.coerceguid(object_ids)
    if id: object_ids = [object_ids]
    meshes_used = 0
    total_area = 0.0
    error_estimate = 0.0
    for id in object_ids:
        mesh = rhutil.coercemesh(id, True)
        if mesh:
            mp = Rhino.Geometry.AreaMassProperties.Compute(mesh)
            if mp:
                meshes_used += 1
                total_area += mp.Area
                error_estimate += mp.AreaError
    if meshes_used==0: return scriptcontext.errorhandler()
    return meshes_used, total_area, error_estimate


def MeshAreaCentroid(object_id):
    """Calculates the area centroid of a mesh object
    Parameters:
      object_id = identifier of a mesh object
    Returns:
      Point3d representing the area centroid if successful
      None on error  
    """
    mesh = rhutil.coercemesh(object_id, True)
    mp = Rhino.Geometry.AreaMassProperties.Compute(mesh)
    if mp is None: return scriptcontext.errorhandler()
    return mp.Centroid


def MeshBooleanDifference(input0, input1, delete_input=True):
    """Performs a boolean difference operation on two sets of input meshes
    Parameters:
      input0, input1 = identifiers of meshes
      delete_input[opt] = delete the input meshes
    Returns:
      list of identifiers of new meshes
    """
    id = rhutil.coerceguid(input0)
    if id: input0 = [id]
    id = rhutil.coerceguid(input1)
    if id: input1 = [id]
    meshes0 = [rhutil.coercemesh(id, True) for id in input0]
    meshes1 = [rhutil.coercemesh(id, True) for id in input1]
    if not meshes0 or not meshes1: raise ValueError("no meshes to work with")
    newmeshes = Rhino.Geometry.Mesh.CreateBooleanDifference(meshes0, meshes1)
    rc = []
    for mesh in newmeshes:
        id = scriptcontext.doc.Objects.AddMesh(mesh)
        if id!=System.Guid.Empty: rc.append(id)
    if rc and delete_input:
        input = input0 + input1
        for id in input:
            id = rhutil.coerceguid(id, True)
            scriptcontext.doc.Objects.Delete(id, True)
    scriptcontext.doc.Views.Redraw()
    return rc


def MeshBooleanIntersection(input0, input1, delete_input=True):
    """Performs a boolean intersection operation on two sets of input meshes
    Parameters:
      input0, input1 = identifiers of meshes
      delete_input[opt] = delete the input meshes
    Returns:
      list of identifiers of new meshes on success
    """
    id = rhutil.coerceguid(input0)
    if id: input0 = [id]
    id = rhutil.coerceguid(input1)
    if id: input1 = [id]
    meshes0 = [rhutil.coercemesh(id, True) for id in input0]
    meshes1 = [rhutil.coercemesh(id, True) for id in input1]
    if not meshes0 or not meshes1: raise ValueError("no meshes to work with")
    newmeshes = Rhino.Geometry.Mesh.CreateBooleanIntersection(meshes0, meshes1)
    rc = []
    for mesh in newmeshes:
        id = scriptcontext.doc.Objects.AddMesh(mesh)
        if id!=System.Guid.Empty: rc.append(id)
    if rc and delete_input:
        input = input0 + input1
        for id in input:
            id = rhutil.coerceguid(id, True)
            scriptcontext.doc.Objects.Delete(id, True)
    scriptcontext.doc.Views.Redraw()
    return rc

def MeshBooleanSplit(input0, input1, delete_input=True):
    """Performs a boolean split operation on two sets of input meshes
    Parameters:
      input0, input1 = identifiers of meshes
      delete_input[opt] = delete the input meshes
    Returns:
      list of identifiers of new meshes on success
      None on error
    """
    id = rhutil.coerceguid(input0)
    if id: input0 = [id]
    id = rhutil.coerceguid(input1)
    if id: input1 = [id]
    meshes0 = [rhutil.coercemesh(id, True) for id in input0]
    meshes1 = [rhutil.coercemesh(id, True) for id in input1]
    if not meshes0 or not meshes1: raise ValueError("no meshes to work with")
    newmeshes = Rhino.Geometry.Mesh.CreateBooleanSplit(meshes0, meshes1)
    rc = []
    for mesh in newmeshes:
        id = scriptcontext.doc.Objects.AddMesh(mesh)
        if id!=System.Guid.Empty: rc.append(id)
    if rc and delete_input:
        input = input0 + input1
        for id in input:
            id = rhutil.coerceguid(id, True)
            scriptcontext.doc.Objects.Delete(id, True)
    scriptcontext.doc.Views.Redraw()
    return rc


def MeshBooleanUnion(mesh_ids, delete_input=True):
    """Performs a boolean union operation on a set of input meshes
    Parameters:
      mesh_ids = identifiers of meshes
      delete_input[opt] = delete the input meshes
    Returns:
      list of identifiers of new meshes
    """
    if len(mesh_ids)<2: raise ValueError("mesh_ids must contain at least 2 meshes")
    meshes = [rhutil.coercemesh(id, True) for id in mesh_ids]
    newmeshes = Rhino.Geometry.Mesh.CreateBooleanUnion(meshes)
    rc = []
    for mesh in newmeshes:
        id = scriptcontext.doc.Objects.AddMesh(mesh)
        if id!=System.Guid.Empty: rc.append(id)
    if rc and delete_input:
        for id in mesh_ids:
            id = rhutil.coerceguid(id, True)
            scriptcontext.doc.Objects.Delete(id, True)
    scriptcontext.doc.Views.Redraw()
    return rc


def MeshClosestPoint(object_id, point, maximum_distance=None):
    """Returns the point on a mesh that is closest to a test point
    Parameters:
      object_id = identifier of a mesh object
      point = point to test
      maximum_distance[opt] = upper bound used for closest point calculation.
        If you are only interested in finding a point Q on the mesh when
        point.DistanceTo(Q) < maximum_distance, then set maximum_distance to
        that value
    Returns:
      Tuple containing the results of the calculation where
        element[0] = the 3-D point on the mesh
        element[1] = the index of the mesh face on which the 3-D point lies
      None on error
    """
    mesh = rhutil.coercemesh(object_id, True)
    point = rhutil.coerce3dpoint(point, True)
    tolerance=maximum_distance if maximum_distance else 0.0
    face, closest_point = mesh.ClosestPoint(point, tolerance)
    if face<0: return scriptcontext.errorhandler()
    return closest_point, face


# [skipping for now] MeshContourPoints

def MeshFaceCenters(mesh_id):
    """Returns the center of each face of the mesh object
    Parameters:
      mesh_id = identifier of a mesh object
    Returns:
      list of 3d points defining the center of each face
    """
    mesh = rhutil.coercemesh(mesh_id, True)
    count = mesh.Faces.Count
    rc = [mesh.Faces.GetFaceCenter(i) for i in range(count)]
    return rc


def MeshFaceCount(object_id):
    """Returns the total face count of a mesh object
    Parameters:
      object_id = identifier of a mesh object
    """
    mesh = rhutil.coercemesh(object_id, True)
    return mesh.Faces.Count


def MeshFaceNormals(mesh_id):
    """Returns the face unit normal for each face of a mesh object
    Paramters:
      mesh_id = identifier of a mesh object
    Returns:
      A list of 3D vectors that define the face unit normals of the mesh
      None on error    
    """
    mesh = rhutil.coercemesh(mesh_id, True)
    if mesh.FaceNormals.Count != mesh.Faces.Count:
        mesh.FaceNormals.ComputeFaceNormals()
    rc = []
    for i in xrange(mesh.FaceNormals.Count):
        normal = mesh.FaceNormals[i]
        rc.append(Rhino.Geometry.Vector3d(normal))
    return rc


def MeshFaces(object_id, face_type=True):
    """Returns the face vertices of a mesh
    Parameters:
      object_id = identifier of a mesh object
      face_type[opt] = The face type to be returned. True = both triangles
        and quads. False = only triangles
    Returns:
      a list of 3D points that define the face vertices of the mesh. If
      face_type is True, then faces are returned as both quads and triangles
      (4 3D points). For triangles, the third and fourth vertex will be
      identical. If face_type is False, then faces are returned as only
      triangles(3 3D points). Quads will be converted to triangles.
    """
    mesh = rhutil.coercemesh(object_id, True)
    rc = []
    for i in xrange(mesh.Faces.Count):
        getrc, p0, p1, p2, p3 = mesh.Faces.GetFaceVertices(i)
        p0 = Rhino.Geometry.Point3d(p0)
        p1 = Rhino.Geometry.Point3d(p1)
        p2 = Rhino.Geometry.Point3d(p2)
        p3 = Rhino.Geometry.Point3d(p3)
        rc.append( p0 )
        rc.append( p1 )
        rc.append( p2 )
        if face_type:
            rc.append(p3)
        else:
            if p2!=p3:
                rc.append( p2 )
                rc.append( p3 )
                rc.append( p0 )
    return rc


def MeshFaceVertices(object_id):
    """Returns the vertex indices of all faces of a mesh object
    Paramters:
      object_id = identifier of a mesh object
    Returns:
      A list containing tuples of 4 numbers that define the vertex indices for
      each face of the mesh. Both quad and triangle faces are returned. If the
      third and fourth vertex indices are identical, the face is a triangle.
    """
    mesh = rhutil.coercemesh(object_id, True)
    rc = []
    for i in xrange(mesh.Faces.Count):
        face = mesh.Faces.GetFace(i)
        rc.append( (face.A, face.B, face.C, face.D) )
    return rc


def MeshHasFaceNormals(object_id):
    """Verifies a mesh object has face normals
    Parameters:
      object_id = identifier of a mesh object
    """
    mesh = rhutil.coercemesh(object_id, True)
    return mesh.FaceNormals.Count>0


def MeshHasTextureCoordinates(object_id):
    """Verifies a mesh object has texture coordinates
    Parameters:
      object_id = identifier of a mesh object
    """
    mesh = rhutil.coercemesh(object_id, True)
    return mesh.TextureCoordinates.Count>0


def MeshHasVertexColors(object_id):
    """Verifies a mesh object has vertex colors
    Parameters:
      object_id = identifier of a mesh object
    """
    mesh = rhutil.coercemesh(object_id, True)
    return mesh.VertexColors.Count>0


def MeshHasVertexNormals(object_id):
    """Verifies a mesh object has vertex normals
    Parameters:
      object_id = identifier of a mesh object
    """
    mesh = rhutil.coercemesh(object_id, True)
    return mesh.Normals.Count>0


def MeshMeshIntersection(mesh1, mesh2, tolerance=None):
    """Calculates the intersections of a mesh object with another mesh object
    Parameters:
      mesh1, mesh2 = identifiers of meshes
      tolerance[opt] = the intersection tolerance
    Returns:
      List of 3d point arrays that define the vertices of the intersection curves
    """
    mesh1 = rhutil.coercemesh(mesh1, True)
    mesh2 = rhutil.coercemesh(mesh2, True)
    if tolerance is None: tolerance = Rhino.RhinoMath.ZeroTolerance
    polylines = Rhino.Geometry.Intersect.Intersection.MeshMeshAccurate(mesh1, mesh2, tolerance)
    if polylines: return list(polylines)
    return []


def MeshNakedEdgePoints(object_id):
    """Identifies the naked edge points of a mesh object. This function shows
    where mesh vertices are not completely surrounded by faces. Joined
    meshes, such as are made by MeshBox, have naked mesh edge points where
    the sub-meshes are joined
    Parameters:
      object_id = identifier of a mesh object
    Returns:
      List of boolean values that represent whether or not a mesh vertex is
      naked or not. The number of elements in the list will be equal to
      the value returned by MeshVertexCount. In which case, the list will
      identify the naked status for each vertex returned by MeshVertices
      None on error
    """
    mesh = rhutil.coercemesh(object_id, True)
    rc = mesh.GetNakedEdgePointStatus()
    return rc


def MeshOffset(mesh_id, distance):
    """Makes a new mesh with vertices offset at a distance in the opposite
    direction of the existing vertex normals
    Parameters:
      mesh_id = identifier of a mesh object
      distance = the distance to offset
    Returns:
      id of the new mesh object if successful
      None on error
    """
    mesh = rhutil.coercemesh(mesh_id, True)
    offsetmesh = mesh.Offset(distance)
    if offsetmesh is None: return scriptcontext.errorhandler()
    rc = scriptcontext.doc.Objects.AddMesh(offsetmesh)
    if rc==System.Guid.Empty: raise Exception("unable to add mesh to document")
    scriptcontext.doc.Views.Redraw()
    return rc


def MeshQuadCount(object_id):
    """Returns the number of quad faces of a mesh object
    Parameters:
      object_id = identifier of a mesh object
    """
    mesh = rhutil.coercemesh(object_id, True)
    return mesh.Faces.QuadCount


def MeshQuadsToTriangles(object_id):
    """Converts a mesh object's quad faces to triangles
    Parameters:
      object_id = identifier of a mesh object
    Returns:
      True or False indicating success or failure
    """
    mesh = rhutil.coercemesh(object_id, True)
    rc = True
    if mesh.Faces.QuadCount>0:
        rc = mesh.Faces.ConvertQuadsToTriangles()
        if rc:
            id = rhutil.coerceguid(object_id, True)
            scriptcontext.doc.Objects.Replace(id, mesh)
            scriptcontext.doc.Views.Redraw()
    return rc

# [skipping for now] MeshTextureCoordinates

def MeshTriangleCount(object_id):
    """Returns the number of triangular faces of a mesh object
    Parameters:
      object_id = identifier of a mesh object
    """
    mesh = rhutil.coercemesh(object_id, True)
    return mesh.Faces.TriangleCount


def MeshVertexColors(mesh_id, colors=0):
    """Returns of modifies the vertex colors of a mesh object
    Parameters:
      mesh_id = identifier of a mesh object
      colors[opt] = A list of color values. Note, for each vertex, there must
        be a corresponding vertex color. If the value is None, then any
        existing vertex colors will be removed from the mesh
    Returns:
      if colors is not specified, the current vertex colors
      if colors is specified, the previous vertex colors
    """
    mesh = rhutil.coercemesh(mesh_id, True)
    rc = [mesh.VertexColors[i] for i in range(mesh.VertexColors.Count)]
    if colors==0: return rc
    if colors is None:
        mesh.VertexColors.Clear()
    else:
        color_count = len(colors)
        if color_count!=mesh.Vertices.Count:
            raise ValueError("length of colors must match vertex count")
        colors = [rhutil.coercecolor(c) for c in colors]
        mesh.VertexColors.Clear()
        for c in colors: mesh.VertexColors.Add(c)
        id = rhutil.coerceguid(mesh_id, True)
        scriptcontext.doc.Objects.Replace(id, mesh)
    scriptcontext.doc.Views.Redraw()
    return rc


def MeshVertexCount(object_id):
    """Returns the vertex count of a mesh object
    Parameters:
      object_id = identifier of a mesh object
    """
    mesh = rhutil.coercemesh(object_id, True)
    return mesh.Vertices.Count


def MeshVertexFaces(mesh_id, vertex_index):
    """Returns the mesh faces that share a specified mesh vertex
    Parameters:
      mesh_id = identifier of a mesh object
      vertex_index = index of the mesh vertex to find faces for
    Returns:
      list of face indices on success
      None on error
    """
    mesh = rhutil.coercemesh(mesh_id, True)
    return mesh.Vertices.GetVertexFaces(vertex_index)


def MeshVertexNormals(mesh_id):
    """Returns the vertex unit normal for each vertex of a mesh object
    Parameters:
      mesh_id = identifier of a mesh object
    Returns:
      list of vertex normals, (empty list if no normals exist)
    """
    mesh = rhutil.coercemesh(mesh_id, True)
    count = mesh.Normals.Count
    if count<1: return []
    return [Rhino.Geometry.Vector3d(mesh.Normals[i]) for i in xrange(count)]


def MeshVertices(object_id):
    """Returns the vertices of a mesh object
    Parameters:
      object_id = identifier of a mesh object
    Returns:
      list of 3D points
    """
    mesh = rhutil.coercemesh(object_id, True)
    count = mesh.Vertices.Count
    rc = []
    for i in xrange(count):
        vertex = mesh.Vertices[i]
        rc.append(Rhino.Geometry.Point3d(vertex))
    return rc


def MeshVolume(object_ids, True):
    """
    Returns the approximate volume of one or more closed mesh objects
    Parameters:
      object_ids = identifiers of one or more mesh objects
    Returns:
      a tuple containing 3 numbers if successful where
        element[0] = number of meshes used in volume calculation
        element[1] = total volume of all meshes
        element[2] = the error estimate
      None if not successful
    """
    id = rhutil.coerceguid(object_ids)
    if id: object_ids = [id]
    meshes_used = 0
    total_volume = 0.0
    error_estimate = 0.0
    for id in object_ids:
        mesh = rhutil.coercemesh(id, True)
        mp = Rhino.Geometry.VolumeMassProperties.Compute(mesh)
        if mp:
            meshes_used += 1
            total_volume += mp.Volume
            error_estimate += mp.VolumeError
    if meshes_used==0: return scriptcontext.errorhandler()
    return meshes_used, total_volume, error_estimate


def MeshVolumeCentroid(object_id):
    """Calculates the volume centroid of a mesh object
    Parameters:
      object_id = identifier of a mesh object
    Returns:
      Point3d representing the volume centroid
      None on error
    """
    mesh = rhutil.coercemesh(object_id, True)
    mp = Rhino.Geometry.VolumeMassProperties.Compute(mesh)
    if mp: return mp.Centroid
    return scriptcontext.errorhandler()


def PullCurveToMesh(mesh_id, curve_id):
    """Pulls a curve object to a mesh object. The function makes a polyline
    approximation of the input curve and get the closest point on the mesh
    for each point on the polyline. Then it "connects the points" so that
    you have a polyline on the mesh
    Paramters:
      mesh_id = identifier of mesh object that pulls
      curve_id = identifier of curve object to pull
    Returns:
      Guid of new curve on success
      None on error
    """
    mesh = rhutil.coercemesh(mesh_id, True)
    curve = rhutil.coercecurve(curve_id, True)
    tol = scriptcontext.doc.ModelAbsoluteTolerance
    polyline = curve.PullToMesh(mesh, tol)
    if not polyline: return scriptcontext.errorhandler()
    rc = scriptcontext.doc.Objects.AddCurve(polyline)
    if rc==System.Guid.Empty: raise Exception("unable to add polyline to document")
    scriptcontext.doc.Views.Redraw()
    return rc


def SplitDisjointMesh(object_id, delete_input=False):
    """Splits up a mesh object into its unconnected pieces
    Parameters:
      object_id = identifier of a mesh object
      delete_input [opt] = delete the input object
    Returns:
      list of Guids for the new meshes
    """
    mesh = rhutil.coercemesh(object_id, True)
    pieces = mesh.SplitDisjointPieces()
    rc = [scriptcontext.doc.Objects.AddMesh(piece) for piece in pieces]
    if rc and delete_input:
        id = rhutil.coerceguid(object_id, True)
        scriptcontext.doc.Objects.Delete(id)
    scriptcontext.doc.Views.Redraw()
    return rc


def UnifyMeshNormals(object_id):
    """Fixes inconsistencies in the directions of faces of a mesh
    Parameters:
      object_id = identifier of a mesh object
    Returns:
      number of faces that were modified
    """
    mesh = rhutil.coercemesh(object_id, True)
    rc = mesh.UnifyNormals()
    if rc>0:
        id = rhutil.coerceguid(object_id, True)
        scriptcontext.doc.Objects.Replace(id, mesh)
        scriptcontext.doc.Views.Redraw()
    return rc
