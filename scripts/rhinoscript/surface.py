import scriptcontext
import math
import Rhino
import System.Guid
import utility as rhutil
import object as rhobject

def AddBox(corners):
    """Adds a new box shaped polysurface to the document
    Parameters:
      corners = 8 3D points that define the corners of the box. Points need to
        be in counter-clockwise order starting with the bottom rectangle of the box
    Returns:
      identifier of the new object on success
    """
    box = rhutil.coerce3dpointlist(corners, True)
    brep = Rhino.Geometry.Brep.CreateFromBox(box)
    if brep is None: raise ValueError("unable to create brep from box")
    rc = scriptcontext.doc.Objects.AddBrep(brep)
    if rc==System.Guid.Empty: raise Exception("unable to add brep to document")
    scriptcontext.doc.Views.Redraw()
    return rc


def AddCone(base, height, radius, cap=True):
    """Adds a cone shaped polysurface to the document
    Parameters:
      base = 3D origin point of the cone or a plane with an apex at the origin
          and normal along the plane's z-axis
      height = 3D height point of the cone if base is a 3D point. The height
          point defines the height and direction of the cone. If base is a
          plane, height is a numeric value
      radius = the radius at the base of the cone
      cap [opt] = cap base of the cone
    Returns:
      identifier of the new object on success
    """
    plane = None
    height_point = rhutil.coerce3dpoint(height)
    if height_point is None:
        plane = rhutil.coerceplane(base, True)
    else:
        base_point = rhutil.coerce3dpoint(base, True)
        normal = base_point - height_point
        height = normal.Length
        plane = Rhino.Geometry.Plane(height_point, normal)
    cone = Rhino.Geometry.Cone(plane, height, radius)
    brep = Rhino.Geometry.Brep.CreateFromCone(cone, cap)
    rc = scriptcontext.doc.Objects.AddBrep(brep)
    scriptcontext.doc.Views.Redraw()
    return rc


def AddCutPlane(object_ids, start_point, end_point, normal=None):
    """Adds a planar surface through objects at a designated location. For more
    information, see the Rhino help file for the CutPlane command
    Parameters:
      objects_ids = identifiers of objects that the cutting plane will
          pass through
      start_point, end_point = line that defines the cutting plane
      normal[opt] = vector that will be contained in the returned planar
          surface. In the case of Rhino's CutPlane command, this is the
          normal to, or Z axis of, the active view's construction plane.
          If omitted, the world Z axis is used
    Returns:
      identifier of new object on success
      None on error
    """
    objects = []
    bbox = Rhino.Geometry.BoundingBox.Unset
    for id in object_ids:
        rhobj = rhutil.coercerhinoobject(id, True, True)
        geometry = rhobj.Geometry
        bbox.Union( geometry.GetBoundingBox(True) )
    start_point = rhutil.coerce3dpoint(start_point, True)
    end_point = rhutil.coerce3dpoint(end_point, True)
    if not bbox.IsValid: return scriptcontext.errorhandler()
    line = Rhino.Geometry.Line(start_point, end_point)
    if normal: normal = rhutil.coerce3dvector(normal, True)
    else: normal = scriptcontext.doc.Views.ActiveView.ActiveViewport.ConstructionPlane().Normal
    surface = Rhino.Geometry.PlaneSurface.CreateThroughBox(line, normal, bbox)
    if surface is None: return scriptcontext.errorhandler()
    id = scriptcontext.doc.Objects.AddSurface(surface)
    if id==System.Guid.Empty: return scriptcontext.errorhandler()
    scriptcontext.doc.Views.Redraw()
    return id


def AddCylinder(base, height, radius, cap=True):
    """Adds a cylinder-shaped polysurface to the document
    Parameters:
      base = The 3D base point of the cylinder or the base plane of the cylinder
      height = if base is a point, then height is a 3D height point of the
        cylinder. The height point defines the height and direction of the
        cylinder. If base is a plane, then height is the numeric height value
        of the cylinder
      radius = radius of the cylinder
      cap[opt] = cap the cylinder
    Returns:
      identifier of new object if successful
      None on error
    """
    cylinder=None
    height_point = rhutil.coerce3dpoint(height)
    if height_point:
        #base must be a point
        base = rhutil.coerce3dpoint(base, True)
        normal = height_point-base
        plane = Rhino.Geometry.Plane(base, normal)
        height = normal.Length
        circle = Rhino.Geometry.Circle(plane, radius)
        cylinder = Rhino.Geometry.Cylinder(circle, height)
    else:
        #base must be a plane
        if type(base) is Rhino.Geometry.Point3d: base = [base.X, base.Y, base.Z]
        base = rhutil.coerceplane(base, True)
        circle = Rhino.Geometry.Circle(base, radius)
        cylinder = Rhino.Geometry.Cylinder(circle, height)
    brep = cylinder.ToBrep(cap, cap)
    id = scriptcontext.doc.Objects.AddBrep(brep)
    if id==System.Guid.Empty: return scriptcontext.errorhandler()
    scriptcontext.doc.Views.Redraw()
    return id


def AddEdgeSrf(curve_ids):
    """Creates a surface from 2, 3, or 4 edge curves
    Parameters:
      curve_ids = list or tuple of curves
    Returns:
      identifier of new object if successful
      None on error
    """
    curves = [rhutil.coercecurve(id, -1, True) for id in curve_ids]
    brep = Rhino.Geometry.Brep.CreateEdgeSurface(curves)
    if brep is None: return scriptcontext.errorhandler()
    id = scriptcontext.doc.Objects.AddBrep(brep)
    if id==System.Guid.Empty: return scriptcontext.errorhandler()
    scriptcontext.doc.Views.Redraw()
    return id


def AddNurbsSurface(point_count, points, knots_u, knots_v, degree, weights=None):
    """Adds a NURBS surface object to the document
    Parameters:
      point_count = number of control points in the u and v direction
      points = list of 3D points
      knots_u = knot values for the surface in the u direction.
                Must contain point_count[0]+degree[0]-1 elements
      knots_v = knot values for the surface in the v direction.
                Must contain point_count[1]+degree[1]-1 elements
      degree = degree of the surface in the u and v directions.
      weights[opt] = weight values for the surface. The number of elements in
        weights must equal the number of elements in points. Values must be
        greater than zero.
    Returns:
      identifier of new object if successful
      None on error
    """
    if len(points)<(point_count[0]*point_count[1]):
        return scriptcontext.errorhandler()
    ns = Rhino.Geometry.NurbsSurface.Create(3, weights!=None, degree[0]+1, degree[1]+1, point_count[0], point_count[1])
    #add the points and weights
    controlpoints = ns.Points
    index = 0
    for i in range(point_count[0]):
        for j in range(point_count[1]):
            if weights:
                cp = Rhino.Geometry.ControlPoint(points[index], weights[index])
                controlpoints.SetControlPoint(i,j,cp)
            else:
                cp = Rhino.Geometry.ControlPoint(points[index])
                controlpoints.SetControlPoint(i,j,cp)
            index += 1
    #add the knots
    for i in range(ns.KnotsU.Count): ns.KnotsU[i] = knots_u[i]
    for i in range(ns.KnotsV.Count): ns.KnotsV[i] = knots_v[i]
    if not ns.IsValid: return scriptcontext.errorhandler()
    id = scriptcontext.doc.Objects.AddSurface(ns)
    if id==System.Guid.Empty: return scriptcontext.errorhandler()
    scriptcontext.doc.Views.Redraw()
    return id


def AddPlanarSrf(object_ids):
    """Creates one or more surfaces from planar curves
    Parameters:
      object_ids = identifiers of curves to use for creating planar surfaces
    Returns:
      list of surfaces created on success
      None on error
    """
    id = rhutil.coerceguid(object_ids, False)
    if id: object_ids = [id]
    curves = [rhutil.coercecurve(id,-1,True) for id in object_ids]
    breps = Rhino.Geometry.Brep.CreatePlanarBreps(curves)
    rc = [scriptcontext.doc.Objects.AddBrep(brep) for brep in breps]
    scriptcontext.doc.Views.Redraw()
    return rc


def AddPlaneSurface(plane, u_dir, v_dir):
    """Creates a plane surface and adds it to the document.
    Parameters:
      plane = The plane.
      u_dir = The magnitude in the U direction.
      v_dir = The magnitude in the V direction.
    Returns:
      The identifier of the new object if successful.
      None if not successful, or on error.
    """
    plane = rhutil.coerceplane(plane, True)
    u_interval = Rhino.Geometry.Interval(0, u_dir)
    v_interval = Rhino.Geometry.Interval(0, v_dir)
    plane_surface = Rhino.Geometry.PlaneSurface(plane, u_interval, v_interval) 
    if plane_surface is None: return scriptcontext.errorhandler()
    rc = scriptcontext.doc.Objects.AddSurface(plane_surface)
    if rc==System.Guid.Empty: return scriptcontext.errorhandler()
    scriptcontext.doc.Views.Redraw()
    return rc


def AddLoftSrf(object_ids, start=None, end=None, loft_type=0, simplify_method=0, value=0, closed=False):
    """Adds a surface created by lofting curves to the document.
    - no curve sorting performed. pass in curves in the order you want them sorted
    - directions of open curves not adjusted. Use CurveDirectionsMatch and
      ReverseCurve to adjust the directions of open curves
    - seams of closed curves are not adjusted. Use CurveSeam to adjust the seam
      of closed curves
    Parameters:
      object_ids = ordered list of object identifiers for the curves to loft through
      start [opt] = starting point of the loft
      end [opt] = ending point of the loft
      loft_type [opt] = type of loft. Possible options are:
        0 = Normal. Uses chord-length parameterization in the loft direction
        1 = Loose. The surface is allowed to move away from the original curves
            to make a smoother surface. The surface control points are created
            at the same locations as the control points of the loft input curves.
        2 = Straight. The sections between the curves are straight. This is
            also known as a ruled surface.
        3 = Tight. The surface sticks closely to the original curves. Uses square
            root of chord-length parameterization in the loft direction
        4 = Developable. Creates a separate developable surface or polysurface
            from each pair of curves.
      simplify_method [opt] = Possible options are:
        0 = None. Does not simplify.
        1 = Rebuild. Rebuilds the shape curves before lofting.
        2 = Refit. Refits the shape curves to a specified tolerance
      value [opt] = A value based on the specified style.
        style=1 (Rebuild), then value is the number of control point used to rebuild
        style=1 is specified and this argument is omitted, then curves will be
        rebuilt using 10 control points.
        style=2 (Refit), then value is the tolerance used to rebuild.
        style=2 is specified and this argument is omitted, then the document's
        absolute tolerance us used for refitting.
    Returns:
      An array containing the identifiers of the new surface objects if successful
      None on error
    """
    if loft_type<0 or loft_type>5: raise ValueError("loft_type must be 0-4")
    if simplify_method<0 or simplify_method>2: raise ValueError("simplify_method must be 0-2")

    # get set of curves from object_ids
    curves = [rhutil.coercecurve(id,-1,True) for id in object_ids]
    if len(curves)<2: return scriptcontext.errorhandler()
    if start is None: start = Rhino.Geometry.Point3d.Unset
    if end is None: end = Rhino.Geometry.Point3d.Unset
    start = rhutil.coerce3dpoint(start, True)
    end = rhutil.coerce3dpoint(end, True)
    
    lt = Rhino.Geometry.LoftType.Normal
    if loft_type==1: lt = Rhino.Geometry.LoftType.Loose
    elif loft_type==2: lt = Rhino.Geometry.LoftType.Straight
    elif loft_type==3: lt = Rhino.Geometry.LoftType.Tight
    elif loft_type==4: lt = Rhino.Geometry.LoftType.Developable

    breps = None
    if simplify_method==0:
        breps = Rhino.Geometry.Brep.CreateFromLoft(curves, start, end, lt, closed)
    elif simplify_method==1:
        value = abs(value)
        rebuild_count = int(value)
        breps = Rhino.Geometry.Brep.CreateFromLoftRebuild(curves, start, end, lt, closed, rebuild_count)
    elif simplify_method==2:
        refit = abs(value)
        if refit==0: refit = scriptcontext.doc.ModelAbsoluteTolerance
        breps = Rhino.Geometry.Brep.CreateFromLoftRefit(curves, start, end, lt, closed, refit)
    if not breps: return scriptcontext.errorhandler()

    idlist = []
    for brep in breps:
        id = scriptcontext.doc.Objects.AddBrep(brep)
        if id!=System.Guid.Empty: idlist.append(id)
    if idlist: scriptcontext.doc.Views.Redraw()
    return idlist


def AddRevSrf(curve_id, axis, start_angle=0.0, end_angle=360.0):
    """Creates a surface by revolving a curve around an axis
    Parameters:
      curve_id = identifier of profile curve
      axis = line for the rail revolve axis
      start_angle[opt], end_angle[opt] = start and end angles of revolve
    Returns:
      identifier of new object if successful
      None on error
    """
    curve = rhutil.coercecurve(curve_id, -1, True)
    axis = rhutil.coerceline(axis, True)
    start_angle = math.radians(start_angle)
    end_angle = math.radians(end_angle)
    srf = Rhino.Geometry.RevSurface.Create(curve, axis, start_angle, end_angle)
    if not srf: return scriptcontext.errorhandler()
    rc = scriptcontext.doc.Objects.AddSurface(srf)
    scriptcontext.doc.Views.Redraw()
    return rc


def AddSphere(center_or_plane, radius):
    """Adds a spherical surface to the document
    Parameters:
      center_or_plane = center point of the sphere. If a plane is input,
        the origin of the plane will be the center of the sphere
      radius = radius of the sphere in the current model units
    Returns:
      intentifier of the new object on success
      None on error
    """
    center = rhutil.coerce3dpoint(center_or_plane)
    if center is None:
        plane = rhutil.coerceplane(center_or_plane, True)
        center = plane.Origin
    sphere = Rhino.Geometry.Sphere(center, radius)
    rc = scriptcontext.doc.Objects.AddSphere(sphere)
    if rc==System.Guid.Empty: return scriptcontext.errorhandler()
    scriptcontext.doc.Views.Redraw()
    return rc


def AddSrfContourCrvs(object_id, points_or_plane, interval=None):
    """Adds a spaced series of planar curves resulting from the intersection of
    defined cutting planes through a surface or polysurface. For more
    information, see Rhino help for details on the Contour command
    Parameters:
      object_id = object identifier
      points_or_plane = either a list/tuple of two points or a plane
        if two points, they define the start and end points of a center line
        if a plane, the plane defines the cutting plane
      interval[opt] = distance beween contour curves.
    Returns:
      ids of new curves on success
      None on error
    """
    brep = rhutil.coercebrep(object_id)
    plane = rhutil.coerceplane(points_or_plane)
    curves = None
    if plane:
        curves = Rhino.Geometry.Brep.CreateContourCurves(brep, plane)
    else:
        start = rhutil.coerce3dpoint(points_or_plane[0], True)
        end = rhutil.coerce3dpoint(points_or_plane[1], True)
        if not interval:
            bbox = brep.GetBoundingBox(True)
            v = bbox.Max - bbox.Min
            interval = v.Length / 50.0
        curves = Rhino.Geometry.Brep.CreateContourCurves(brep, start, end, interval)
    rc = []
    for crv in curves:
        id = scriptcontext.doc.Objects.AddCurve(crv)
        if id!=System.Guid.Empty: rc.append(id)
    scriptcontext.doc.Views.Redraw()
    return rc


def AddSrfControlPtGrid(count, points, degree=(3,3)):
    """Creates a surface from a grid of points
    Parameters:
      count = tuple of two numbers defining number of points in the u,v directions
      points = list of 3D points
      degree[opt] = two numbers defining degree of the surface in the u,v directions
    Returns:
      The identifier of the new object if successful.
      None if not successful, or on error.
    """
    points = rhutil.coerce3dpointlist(points, True)
    surf = Rhino.Geometry.NurbsSurface.CreateFromPoints(points, count[0], count[1], degree[0], degree[1])
    if surf is None: return scritpcontext.errorhandler()
    id = scriptcontext.doc.Objects.AddSurface(surf)
    if id!=System.Guid.Empty:
        scriptcontext.doc.Views.Redraw()
        return id
    return scriptcontext.errorhandler()


def AddSrfPt(points):
    """Creates a new surface from either 3 or 4 control points.
    Parameters:
      points = list of either 3 or 4 control points
    Returns
      The identifier of the new object if successful.
      None if not successful, or on error.
    """
    points = rhutil.coerce3dpointlist(points, True)
    surface=None
    if len(points)==3:
        surface = Rhino.Geometry.NurbsSurface.CreateFromCorners(points[0], points[1], points[2])
    elif len(points)==4:
        surface = Rhino.Geometry.NurbsSurface.CreateFromCorners(points[0], points[1], points[2], points[3])
    if surface is None: return scriptcontext.errorhandler()
    rc = scriptcontext.doc.Objects.AddSurface(surface)
    if rc==System.Guid.Empty: return scriptcontext.errorhandler()
    scriptcontext.doc.Views.Redraw()
    return rc


def AddTorus(base, major_radius, minor_radius, direction=None):
    """Adds a torus shaped revolved surface to the document
    Parameters:
      base = 3D origin point of the torus or the base plane of the torus
      major_radius, minor_radius = the two radii of the torus
      directions[opt] = A point that defines the direction of the torus when base is a point.
        If omitted, a torus that is parallel to the world XY plane is created
    Returns:
      The identifier of the new object if successful.
      None if not successful, or on error.
    """
    baseplane = None
    basepoint = rhutil.coerce3dpoint(base)
    if basepoint is None:
        baseplane = rhutil.coerceplane(base, True)
        if direction!=None: return scriptcontext.errorhandler()
    if baseplane is None:
        direction = rhutil.coerce3dpoint(direction, True)
        if direction: direction = direction-basepoint
        else: direction = Rhino.Geometry.Vector3d.ZAxis
        baseplane = Rhino.Geometry.Plane(basepoint, direction)
    torus = Rhino.Geometry.Torus(baseplane, major_radius, minor_radius)
    revsurf = torus.ToRevSurface()
    rc = scriptcontext.doc.Objects.AddSurface(revsurf)
    scriptcontext.doc.Views.Redraw()
    return rc


def BooleanDifference(input0, input1, delete_input=True):
    """Performs a boolean difference operation on two sets of input surfaces
    and polysurfaces. For more details, see the BooleanDifference command in
    the Rhino help file
    Parameters:
        input0 = list of surfaces to subtract from
        input1 = list of surfaces to be subtracted
        delete_input[opt] = delete all input objects
    Returns:
        list of identifiers of newly created objects on success
        None on error
    """
    if type(input0) is list or type(input0) is tuple: pass
    else: input0 = [input0]
    
    if type(input1) is list or type(input1) is tuple: pass
    else: input1 = [input1]

    breps0 = [rhutil.coercebrep(id, True) for id in input0]
    breps1 = [rhutil.coercebrep(id, True) for id in input1]
    tolerance = scriptcontext.doc.ModelAbsoluteTolerance
    newbreps = Rhino.Geometry.Brep.CreateBooleanDifference(breps0, breps1, tolerance)
    if newbreps is None: return scriptcontext.errorhandler()
    
    rc = [scriptcontext.doc.Objects.AddBrep(brep) for brep in newbreps]
    if delete_input:
        for id in input0: scriptcontext.doc.Objects.Delete(id, True)
        for id in input1: scriptcontext.doc.Objects.Delete(id, True)
    scriptcontext.doc.Views.Redraw()
    return rc


def BooleanIntersection(input0, input1, delete_input=True):
    """Performs a boolean intersection operation on two sets of input surfaces
    and polysurfaces. For more details, see the BooleanIntersection command in
    the Rhino help file
    Parameters:
        input0 = list of surfaces
        input1 = list of surfaces
        delete_input[opt] = delete all input objects
    Returns:
        list of identifiers of newly created objects on success
        None on error
    """
    if type(input0) is list or type(input0) is tuple: pass
    else: input0 = [input0]
    
    if type(input1) is list or type(input1) is tuple: pass
    else: input1 = [input1]

    breps0 = [rhutil.coercebrep(id, True) for id in input0]
    breps1 = [rhutil.coercebrep(id, True) for id in input1]
    tolerance = scriptcontext.doc.ModelAbsoluteTolerance
    newbreps = Rhino.Geometry.Brep.CreateBooleanIntersection(breps0, breps1, tolerance)
    if newbreps is None: return scriptcontext.errorhandler()
    rc = [scriptcontext.doc.Objects.AddBrep(brep) for brep in newbreps]
    if delete_input:
        for id in input0: scriptcontext.doc.Objects.Delete(id, True)
        for id in input1: scriptcontext.doc.Objects.Delete(id, True)
    scriptcontext.doc.Views.Redraw()
    return rc


def BooleanUnion(input, delete_input=True):
    """Performs a boolean union operation on a set of input surfaces and
    polysurfaces. For more details, see the BooleanUnion command in the
    Rhino help file
    Parameters:
        input = list of surfaces to union
        delete_input[opt] = delete all input objects
    Returns:
        list of identifiers of newly created objects on success
        None on error
    """
    if len(input)<2: return scriptcontext.errorhandler()
    breps = [rhutil.coercebrep(id, True) for id in input]
    tolerance = scriptcontext.doc.ModelAbsoluteTolerance
    newbreps = Rhino.Geometry.Brep.CreateBooleanUnion(breps, tolerance)
    if newbreps is None: return scriptcontext.errorhandler()
    
    rc = [scriptcontext.doc.Objects.AddBrep(brep) for brep in newbreps]
    if delete_input:
        for id in input: scriptcontext.doc.Objects.Delete(id, True)
    scriptcontext.doc.Views.Redraw()
    return rc


def BrepClosestPoint(object_id, point):
    """Returns the point on a surface or polysurface that is closest to a test
    point. This function works on both untrimmed and trimmed surfaces.
    Parameters:
      object_id = The object's identifier.
      point = The test, or sampling point.
    Returns:
      A tuple of closest point information if successful. The list will
      contain the following information:
      Element     Type             Description
         0        Point3d          The 3-D point at the parameter value of the 
                                   closest point.
         1        (U, V)           Parameter values of closest point. Note, V 
                                   is 0 if the component index type is brep_edge
                                   or brep_vertex. 
         2        (type, index)    The type and index of the brep component that
                                   contains the closest point. Possible types are
                                   brep_face, brep_edge or brep_vertex.
         3        Vector3d         The normal to the brep_face, or the tangent
                                   to the brep_edge.  
      None if not successful, or on error.
    """
    brep = rhutil.coercebrep(object_id, True)
    point = rhutil.coerce3dpoint(point, True)
    rc = brep.ClosestPoint(point, 0.0)
    if rc[0]:
        type = int(rc[2].ComponentIndexType)
        index = rc[2].Index
        return rc[1], (rc[3], rc[4]), (type, index), rc[5]


def CapPlanarHoles(surface_id):
    """Caps planar holes in a surface or polysurface
    Returns:
      True or False indicating success or failure
    """
    brep = rhutil.coercebrep(surface_id, True)
    tolerance = scriptcontext.doc.ModelAbsoluteTolerance
    newbrep = brep.CapPlanarHoles(tolerance)
    if newbrep:
        surface_id = rhutil.coerceguid(surface_id)
        if surface_id and scriptcontext.doc.Objects.Replace(surface_id, newbrep):
            scriptcontext.doc.Views.Redraw()
            return True
    return False


def DuplicateEdgeCurves(object_id, select=False):
    """Duplicates the edge curves of a surface or polysurface. For more
    information, see the Rhino help file for information on the DupEdge
    command.
    Parameters:
      object_id = The identifier of the surface or polysurface object.
      select [opt] = Select the duplicated edge curves. The default is not
      to select (False).
    Returns:
      A list of Guids identifying the newly created curve objects if successful.
      None if not successful, or on error.
    """
    brep = rhutil.coercebrep(object_id, True)
    out_curves = brep.DuplicateEdgeCurves()
    curves = []
    for curve in out_curves:
        if curve.IsValid:
            rc = scriptcontext.doc.Objects.AddCurve(curve)
            curve.Dispose()
            if rc==System.Guid.Empty: return None
            curves.append(rc)
            if select: rhobject.SelectObject(rc)
    if curves: scriptcontext.doc.Views.Redraw()
    return curves


def DuplicateSurfaceBorder(surface_id):
    """Creates a curve that duplicates a surface or polysurface border
    Parameters:
      surface_id = identifier of a surface
    Returns:
      list of curve ids on success
      None on error
    """
    brep = rhutil.coercebrep(surface_id, True)
    curves = brep.DuplicateEdgeCurves(True)
    if curves is None: return scriptcontext.errorhandler()
    tolerance = scriptcontext.doc.ModelAbsoluteTolerance * 2.1
    curves = Rhino.Geometry.Curve.JoinCurves(curves, tolerance)
    if curves is None: return scriptcontext.errorhandler()
    rc = [scriptcontext.doc.Objects.AddCurve(c) for c in curves]
    scriptcontext.doc.Views.Redraw()
    return rc


def EvaluateSurface(surface_id, u, v):
    "Evaluates a surface at a U,V parameter"
    surface = rhutil.coercesurface(surface_id, True)
    rc = surface.PointAt(u,v)
    if rc.IsValid: return rc
    return scriptcontext.errorhandler()


def ExtendSurface(surface_id, parameter, length, smooth=True):
    """Lengthens an untrimmed surface object
    Parameters:
      surface_id = identifier of a surface
      parameter = tuple of two values definfing the U,V parameter to evaluate.
        The surface edge closest to the U,V parameter will be the edge that is
        extended
      length = amount to extend to surface
      smooth[opt] = If True, the surface is extended smoothly curving from the
        edge. If False, the surface is extended in a straight line from the edge
    Returns:
      True or False indicating success or failure
    """
    surface = rhutil.coercesurface(surface_id, True)
    edge = surface.ClosestSide(parameter[0], parameter[1])
    newsrf = surface.Extend(edge, length, smooth)
    if newsrf:
        surface_id = rhutil.coerceguid(surface_id)
        if surface_id: scriptcontext.doc.Objects.Replace(surface_id, newsrf)
        scriptcontext.doc.Views.Redraw()
    return newsrf is not None


def ExplodePolysurfaces(object_ids, delete_input=False):
    """Explodes, or unjoins, one or more polysurface objects. Polysurfaces
    will be exploded into separate surfaces
    Parameters:
      object_ids = identifiers of polysurfaces to explode
      delete_input[opt] = delete input objects after exploding
    Returns:
      List of identifiers of exploded pieces on success
    """
    id = rhutil.coerceguid(object_ids, False)
    if id: object_ids = [id]
    ids = []
    for id in object_ids:
        brep = rhutil.coercebrep(id, True)
        if brep.Faces.Count>1:
            for i in range(brep.Faces.Count):
                copyface = brep.Faces[i].DuplicateFace(False)
                face_id = scriptcontext.doc.Objects.AddBrep(copyface)
                if face_id!=System.Guid.Empty: ids.append(face_id)
            if delete_input: scriptcontext.doc.Objects.Delete(id, True)
    scriptcontext.doc.Views.Redraw()
    return ids


def ExtractIsoCurve(surface_id, parameter, direction):
    """Extracts isoparametric curves from a surface
    Parameters:
      surface_id = identifier of a surface
      parameter = u,v parameter of the surface to evaluate
      direction
        0 = u, 1 = v, 2 = both
    Returns:
      list of curve ids on success
      None on error
    """
    surface = rhutil.coercesurface(surface_id, True)
    ids = []
    if direction==0 or direction==2:
        curves = None
        if type(surface) is Rhino.Geometry.BrepFace:
            curves = surface.TrimAwareIsoCurve(0, parameter[1])
        else:
            curves = [surface.IsoCurve(0,parameter[1])]
        if curves:
            for curve in curves:
                id = scriptcontext.doc.Objects.AddCurve(curve)
                if id!=System.Guid.Empty: ids.append(id)
    if direction==1 or direction==2:
        curves = None
        if type(surface) is Rhino.Geometry.BrepFace:
            curves = surface.TrimAwareIsoCurve(1, parameter[0])
        else:
            curves = [surface.IsoCurve(1,parameter[0])]
        if curves:
            for curve in curves:
                id = scriptcontext.doc.Objects.AddCurve(curve)
                if id!=System.Guid.Empty: ids.append(id)
    scriptcontext.doc.Views.Redraw()
    return ids


def ExtractSurface(object_id, face_indices, copy=False):
    """Separates or copies a surface or a copy of a surface from a polysurface
    Paramters:
      object_id: polysurface identifier
      face_indices: one or more numbers representing faces
      copy[opt]: If True the faces are copied. If False, the faces are extracted
    Returns:
      identifiers of extracted surface objects on success
    """
    brep = rhutil.coercebrep(object_id, True)
    if hasattr(face_indices, "__getitem__"): pass
    else: face_indices = [face_indices]
    rc = []
    face_indices = sorted(face_indices, reverse=True)
    for index in face_indices:
        face = brep.Faces[index]
        newbrep = face.DuplicateFace(True)
        id = scriptcontext.doc.Objects.AddBrep(newbrep)
        rc.append(id)
    if not copy:
        for index in face_indices: brep.Faces.RemoveAt(index)
        id = rhutil.coerceguid(object_id)
        scriptcontext.doc.Objects.Replace(id, brep)
    scriptcontext.doc.Views.Redraw()
    return rc


def ExtrudeCurve(curve_id, path_id):
    """Creates a surface by extruding a curve along a path
    Parameters:
      curve_id = identifier of the curve to extrude
      path_id = identifier of the path curve
    Returns:
      identifier of new surface on success
      None on error
    """
    curve1 = rhutil.coercecurve(curve_id, True)
    curve2 = rhutil.coercecurve(path_id, True)
    srf = Rhino.Geometry.SumSurface.Create(curve1, curve2)
    rc = scriptcontext.doc.Objects.AddSurface(srf)
    if rc==System.Guid.Empty: return scriptcontext.errorhandler()
    scriptcontext.doc.Views.Redraw()
    return rc


def ExtrudeCurvePoint(curve_id, point):
    """Creates a surface by extruding a curve to a point
    Parameters:
      curve_id = identifier of the curve to extrude
      point = 3D point
    Returns:
      identifier of new surface on success
      None on error
    """
    curve = rhutil.coercecurve(curve_id, True)
    point = rhutil.coerce3dpoint(point, True)
    srf = Rhino.Geometry.Surface.CreateExtrusionToPoint(curve, point)
    rc = scriptcontext.doc.Objects.AddSurface(srf)
    if rc==System.Guid.Empty: return scriptcontext.errorhandler()
    scriptcontext.doc.Views.Redraw()
    return rc


def ExtrudeCurveStraight(curve_id, start_point, end_point):
    """Creates a surface by extruding a curve along two points that define a line
    Parameters:
      curve_id = identifier of the curve to extrude
      start_point, end_point = 3D points
    Returns:
      identifier of new surface on success
      None on error
    """
    curve = rhutil.coercecurve(curve_id, -1, True)
    start_point = rhutil.coerce3dpoint(start_point, True)
    end_point = rhutil.coerce3dpoint(end_point, True)
    vec = end_point - start_point
    srf = Rhino.Geometry.Surface.CreateExtrusion(curve, vec)
    rc = scriptcontext.doc.Objects.AddSurface(srf)
    if rc==System.Guid.Empty: return scriptcontext.errorhandler()
    scriptcontext.doc.Views.Redraw()
    return rc


def FilletSurfaces(surface0, surface1, radius, uvparam0=None, uvparam1=None):
    """Create constant radius rolling ball fillets between two surfaces. Note,
    this function does not trim the original surfaces of the fillets
    Parameters:
      surface0, surface1 = identifiers of first and second surface
      radius = a positive fillet radius
      uvparam0[opt] = a u,v surface parameter of surface0 near where the fillet
        is expected to hit the surface
      uvparam1[opt] = same as uvparam0, but for surface1
    Returns:
      ids of surfaces created on success
      None on error
    """
    surface0 = rhutil.coercesurface(surface0, True)
    surface1 = rhutil.coercesurface(surface1, True)
    uvparam0 = rhutil.coerce2dpoint(uvparam0, True)
    uvparam1 = rhutil.coerce2dpoint(uvparam1, True)
    surfaces = None
    tol = scriptcontext.doc.ModelAbsoluteTolerance
    if uvparam0 and uvparam1:
        surfaces = Rhino.Geometry.Surface.CreateRollingBallFillet(surface0, uvparam0, surface1, uvparam1, radius, tol)
    else:
        surfaces = Rhino.Geometry.Surface.CreateRollingBallFillet(surface0, surface1, radius, tol)
    if not surfaces: return scriptcontext.errorhandler()
    rc = []
    for surf in surfaces:
        rc.append( scriptcontext.doc.Objects.AddSurface(surf) )
    scriptcontext.doc.Views.Redraw()
    return rc


def FlipSurface(surface_id, flip=None):
    """Returns or changes the normal direction of a surface. This feature can
    also be found in Rhino's Dir command
    Parameters:
      surface_id = identifier of a surface object
      flip[opt] = new normal orientation, either flipped(True) or not flipped (False).
    Returns:
      if flipped is not specified, the current normal orientation
      if flipped is specified, the previous normal orientation
      None on error
    """
    brep = rhutil.coercebrep(surface_id, True)
    if brep.Faces.Count>1: return scriptcontext.errorhandler()
    face = brep.Faces[0]
    old_reverse = face.OrientationIsReversed
    if flip!=None and brep.IsSolid==False and old_reverse!=flip:
        brep.Flip()
        surface_id = rhutil.coerceguid(surface_id)
        if surface_id: scriptcontext.doc.Objects.Replace(surface_id, brep)
        scriptcontext.doc.Views.Redraw()
    return old_reverse


def IntersectBreps(brep1, brep2, tolerance=None):
    """Intersects a brep object with another brep object. Note, unlike the
    SurfaceSurfaceIntersection function this function works on trimmed surfaces.
    Parameters:
      brep1 = The first brep object's identifier.
      brep2 = The second  brep object's identifier.
      tolerance = The distance tolerance at segment midpoints. If omitted,
                  the current absolute tolerance is used.
    Returns:
      A list of Guids identifying the newly created intersection curve and
      point objects if successful.
      None if not successful, or on error.
    """
    brep1 = rhutil.coercebrep(brep1, True)
    brep2 = rhutil.coercebrep(brep2, True)
    if tolerance is None or tolerance < 0.0:
        tolerance = scriptcontext.doc.ModelAbsoluteTolerance
    rc = Rhino.Geometry.Intersect.Intersection.BrepBrep(brep1, brep2, tolerance)
    if not rc[0]: return None
    out_curves = rc[1]
    out_points = rc[2]
    merged_curves = Rhino.Geometry.Curve.JoinCurves(out_curves, 2.1 * tolerance)
    
    ids = []
    if merged_curves:
        for curve in merged_curves:
            if curve.IsValid:
                rc = scriptcontext.doc.Objects.AddCurve(curve)
                curve.Dispose()
                if rc==System.Guid.Empty: return scriptcontext.errorhandler()
                ids.append(rc)
    else:
        for curve in out_curves:
            if curve.IsValid:
                rc = scriptcontext.doc.Objects.AddCurve(curve)
                curve.Dispose()
                if rc==System.Guid.Empty: return scriptcontext.errorhandler()
                ids.append(rc)
    for point in out_points:
        rc = scriptcontext.doc.Objects.AddPoint(point)
        if rc==System.Guid.Empty: return scriptcontext.errorhandler()
        ids.append(rc)
    if ids: scriptcontext.doc.Views.Redraw()
    return ids


def IntersectSpheres(sphere_plane0, sphere_radius0, sphere_plane1, sphere_radius1):
    """Calculates intersections of two spheres
    Parameters:
      sphere_plane0 = an equatorial plane of the first sphere. The origin of the
        plane will be the center point of the sphere
      sphere_radius0 = radius of the first sphere
      sphere_plane1 = plane for second sphere
      sphere_radius1 = radius for second sphere
    Returns:
      List of intersection results
        element 0 = type of intersection (0=point, 1=circle, 2=spheres are identical)
        element 1 = Point of intersection or plane of circle intersection
        element 2 = radius of circle if circle intersection
      None on error
    """
    plane0 = rhutil.coerceplane(sphere_plane0, True)
    plane1 = rhutil.coerceplane(sphere_plane1, True)
    sphere0 = Rhino.Geometry.Sphere(plane0, sphere_radius0)
    sphere1 = Rhino.Geometry.Sphere(plane1, sphere_radius1)
    rc, circle = Rhino.Geometry.Intersect.Intersection.SphereSphere(sphere0, sphere1)
    if rc==Rhino.Geometry.Intersect.SphereSphereIntersection.Point:
        return [0, circle.Center]
    if rc==Rhino.Geometry.Intersect.SphereSphereIntersection.Circle:
        return [1, circle.Plane, circle.Radius]
    if rc==Rhino.Geometry.Intersect.SphereSphereIntersection.Overlap:
        return [2]
    return scriptcontext.errorhandler()


def IsBrep(object_id):
    """Verifies an object is a Brep, or a boundary representation model, object.
    Parameters:
      object_id = The object's identifier.
    Returns:
      True if successful, otherwise False.
      None on error.
    """
    return rhutil.coercebrep(object_id)!=None


def IsCone(object_id):
    "Determines if a surface is a portion of a cone"
    surface = rhutil.coercesurface(object_id, True)
    return surface.IsCone()


def IsCylinder(object_id):
    "Determines if a surface is a portion of a cone"
    surface = rhutil.coercesurface(object_id, True)
    return surface.IsCylinder()


def IsPlaneSurface(object_id):
    """Verifies an object is a plane surface. Plane surfaces can be created by
    the Plane command. Note, a plane surface is not a planar NURBS surface
    """
    face = rhutil.coercesurface(object_id, True)
    if type(face) is Rhino.Geometry.BrepFace and face.IsSurface:
        return type(face.UnderlyingSurface()) is Rhino.Geometry.PlaneSurface
    return False
    

def IsPointInSurface(object_id, point):
    """Verifies that a point is inside a closed surface or polysurface
    Parameters:
      object_id: the object's identifier
      point: list of three numbers or Point3d. The test, or sampling point
    Returns:
      True if successful, otherwise False
    """
    object_id = rhutil.coerceguid(object_id, True)
    point = rhutil.coerce3dpoint(point, True)
    if object_id==None or point==None: return scriptcontext.errorhandler()
    obj = scriptcontext.doc.Objects.Find(object_id)
    if type(obj)!=Rhino.DocObjects.BrepObject:
        return scriptcontext.errorhandler()
    tolerance = Rhino.RhinoMath.SqrtEpsilon
    return obj.BrepGeometry.IsPointInside(point, tolerance, False)


def IsPointOnSurface(object_id, point):
    """Verifies that a point lies on a surface
    Parameters:
      object_id: the object's identifier
      point: list of three numbers or Point3d. The test, or sampling point
    Returns:
      True if successful, otherwise False
    """
    surf = rhutil.coercesurface(object_id, True)
    point = rhutil.coerce3dpoint(point, True)
    rc, u, v = surf.ClosestPoint(point)
    if rc:
        srf_pt = surf.PointAt(u,v)
        if srf_pt.DistanceTo(point)>Rhino.RhinoMath.SqrtEpsilon:
            rc = False
        else:
            rc = surf.IsPointOnFace(u,v) != Rhino.Geometry.PointFaceRelation.Exterior
    return rc


def IsPolysurface(object_id):
    """Verifies an object is a polysurface. Polysurfaces consist of two or more
    surfaces joined together. If the polysurface fully encloses a volume, it is
    considered a solid.
    Parameters:
      object_id: the object's identifier
    Returns:
      True is successful, otherwise False
    """
    brep = rhutil.coercebrep(object_id)
    if brep is None: return False
    return brep.Faces.Count>1


def IsPolysurfaceClosed(object_id):
    """Verifies a polysurface object is closed. If the polysurface fully encloses
    a volume, it is considered a solid.
    Parameters:
      object_id: the object's identifier
    Returns:
      True is successful, otherwise False
    """
    brep = rhutil.coercebrep(object_id, True)
    return brep.IsSolid


def IsSphere(object_id):
    "Determines if a surface is a portion of a sphere"
    surface = rhutil.coercesurface(object_id, True)
    return surface.IsSphere()


def IsSurface(object_id):
    """Verifies an object is a surface. Brep objects with only one face are
    also considered surfaces.
    Parameters:
      object_id = the object's identifier.
    Returns:
      True if successful, otherwise False.
    """
    brep = rhutil.coercebrep(object_id)
    if brep and brep.Faces.Count==1: return True
    surface = rhutil.coercesurface(object_id)
    return (surface!=None)


def IsSurfaceClosed( surface_id, direction ):
    """Verifies a surface object is closed in the specified direction.  If the
    surface fully encloses a volume, it is considered a solid
    Parameters:
      surface_id = identifier of a surface
      direction = 0=U, 1=V
    Returns:
      True or False
    """
    surface = rhutil.coercesurface(surface_id, True)
    return surface.IsClosed(direction)


def IsSurfacePeriodic(surface_id, direction):
    """Verifies a surface object is periodic in the specified direction.
    Parameters:
      surface_id = identifier of a surface
      direction = 0=U, 1=V
    Returns:
      True or False
    """
    surface = rhutil.coercesurface(surface_id, True)
    return surface.IsPeriodic(direction)


def IsSurfacePlanar(surface_id, tolerance=None):
    """Verifies a surface object is planar
    Parameters:
      surface_id = identifier of a surface
      tolerance[opt] = tolerance used when checked. If omitted, the current absolute
        tolerance is used
    Returns:
      True or False
    """
    surface = rhutil.coercesurface(surface_id, True)
    if tolerance is None:
        tolerance = scriptcontext.doc.ModelAbsoluteTolerance
    return surface.IsPlanar(tolerance)


def IsSurfaceRational(surface_id):
    """Verifies a surface object is rational
    Parameters:
      surface_id = the surface's identifier
    """
    surface = rhutil.coercesurface(surface_id, True)
    ns = surface.ToNurbsSurface()
    if ns is None: return False
    return ns.IsRational


def IsSurfaceSingular(surface_id, direction):
    """Verifies a surface object is singular in the specified direction.
    Surfaces are considered singular if a side collapses to a point.
    Parameters:
      surface_id = the surface's identifier
      direction: 0=south, 1=east, 2=north, 3=west
    Returns:
      True or False
    """
    surface = rhutil.coercesurface(surface_id, True)
    return surface.IsSingular(direction)


def IsSurfaceTrimmed(surface_id):
    """Verifies a surface object has been trimmed
    Parameters:
      surface_id = the surface's identifier
    Returns:
      True or False
    """
    brep = rhutil.coercebrep(surface_id, True)
    return not brep.IsSurface


def IsTorus(surface_id):
    "Determines if a surface is a portion of a torus"
    surface = rhutil.coercesurface(surface_id, True)
    return surface.IsTorus()


def JoinSurfaces(object_ids, delete_input=False):
    """Joins two or more surface or polysurface objects together to form one
    polysurface object
    Parameters:
      object_ids = list of object identifiers
    Returns:
      identifier of newly created object on success
      None on failure
    """
    breps = [rhutil.coercebrep(id, True) for id in object_ids]
    if len(breps)<2: return scriptcontext.errorhandler()
    tol = scriptcontext.doc.ModelAbsoluteTolerance * 2.1
    joinedbreps = Rhino.Geometry.Brep.JoinBreps(breps, tol)
    if joinedbreps is None or len(joinedbreps)!=1:
        return scriptcontext.errorhandler()
    rc = scriptcontext.doc.Objects.AddBrep(joinedbreps[0])
    if rc==System.Guid.Empty: return scriptcontext.errorhandler()
    if delete_input:
        for id in object_ids:
            id = rhutil.coerceguid(id)
            scriptcontext.doc.Objects.Delete(id, True)
    scriptcontext.doc.Views.Redraw()
    return rc


def MakeSurfacePeriodic(surface_id, direction, delete_input=False):
    """Makes an existing surface a periodic NURBS surface
    Paramters:
      surface_id = the surface's identifier
      direction = The direction to make periodic, either 0=U or 1=V
      delete_input[opt] = delete the input surface
    Returns:
      if delete_input is False, identifier of the new surface
      if delete_input is True, identifer of the modifier surface
      None on error
    """
    surface = rhutil.coercesurface(surface_id, True)
    newsurf = Rhino.Geometry.Surface.CreatePeriodicSurface(surface, direction)
    if newsurf is None: return scriptcontext.errorhandler()
    id = rhutil.coerceguid(surface_id)
    if delete_input:
        scriptcontext.doc.Objects.Replace(id, newsurf)
    else:
        id = scriptcontext.doc.Objects.AddSurface(newsurf)
    scriptcontext.doc.Views.Redraw()
    return id


def OffsetSurface(surface_id, distance, tolerance=None):
    """Offsets a trimmed or untrimmed surface by a distance. The offset surface
    will be added to Rhino.
    Parameters:
      surface_id = the surface's identifier
      distance = the distance to offset
      tolerance [opt] = The offset tolerance. Use 0.0 to make a loose offset. Otherwise, the
        document's absolute tolerance is usually sufficient.
    Returns:
      identifier of the new object if successful
      None on error
    """
    brep = rhutil.coercebrep(surface_id, True)
    face = None
    if brep.IsSurface: face = brep.Faces[0]
    if face is None: return scriptcontext.errorhandler()
    if tolerance is None: tolerance = scriptcontext.doc.ModelAbsoluteTolerance
    newbrep = Rhino.Geometry.Brep.CreateFromOffsetFace(face, distance, tolerance, False, False)
    if newbrep is None: return scriptcontext.errorhandler()
    rc = scriptcontext.doc.Objects.AddBrep(newbrep)
    if rc==System.Guid.Empty: return scriptcontext.errorhandler()
    scriptcontext.doc.Views.Redraw()
    return rc


def RebuildSurface(object_id, degree=(3,3), pointcount=(10,10)):
    """Rebuilds a surface to a given degree and control point count. For more
    information see the Rhino help file for the Rebuild command
    Parameters:
      object_id = the surface's identifier
      degree[opt] = two numbers that identify surface degree in both U and V directions
      pointcount[opt] = two numbers that identify the surface point count in both the U and V directions
    Returns:
      True of False indicating success or failure
    """
    surface = rhutil.coercesurface(object_id, True)
    newsurf = surface.Rebuild( degree[0], degree[1], pointcount[0], pointcount[1] )
    if newsurf is None: return False
    object_id = rhutil.coerceguid(object_id)
    rc = scriptcontext.doc.Objects.Replace(object_id, newsurf)
    if rc: scriptcontext.doc.Views.Redraw()
    return rc


def ShootRay(surface_ids, start_point, direction, reflections=10):
    """Shoots a ray at a collection of surfaces
    Parameters:
      surface_ids = one of more surface identifiers
      start_point = starting point of the ray
      direction = vector identifying the direction of the ray
      reflections[opt] = the maximum number of times the ray will be reflected
    Returns:
      list of reflection points on success
      None on error
    """
    start_point = rhutil.coerce3dpoint(start_point, True)
    direction = rhutil.coerce3dvector(direction, True)
    id = rhutil.coerceguid(surface_ids, False)
    if id: surface_ids = [id]
    ray = Rhino.Geometry.Ray3d(start_point, direction)
    breps = []
    for id in surface_ids:
        brep = rhutil.coercebrep(id)
        if brep: breps.append(brep)
        else:
            surface = rhutil.coercesurface(id, True)
            breps.append(surface)
    if not breps: return scriptcontext.errorhandler()
    points = Rhino.Geometry.Intersect.Intersection.RayShoot(ray, breps, reflections)
    if points:
        rc = []
        rc.append(start_point)
        rc = rc + list(points)
        return rc
    return scriptcontext.errorhandler()


def ShortPath(surface_id, start_point, end_point):
    """Creates the shortest possible curve(geodesic) between two points on a
    surface. For more details, see the ShortPath command in Rhino help
    Parameters:
      surface_id = identifier of a surface
      start_point, end_point = start/end points of the short curve
    Returns:
      identifier of the new surface on success
      None on error
    """
    surface = rhutil.coercesurface(surface_id, True)
    start = rhutil.coerce3dpoint(start_point, True)
    end = rhutil.coerce3dpoint(end_point, True)
    rc_start, u_start, v_start = surface.ClosestPoint(start)
    rc_end, u_end, v_end = surface.ClosestPoint(end)
    if not rc_start or not rc_end: return scriptcontext.errorhandler()
    start = Rhino.Geometry.Point2d(u_start, v_start)
    end = Rhino.Geometry.Point2d(u_end, v_end)
    tolerance = scriptcontext.doc.ModelAbsoluteTolerance
    curve = surface.ShortPath(start, end, tolerance)
    if curve is None: return scriptcontext.errorhandler()
    id = scriptcontext.doc.Objects.AddCurve(curve)
    if id==System.Guid.Empty: return scriptcontext.errorhandler()
    scriptcontext.doc.Views.Redraw()
    return id


def ShrinkTrimmedSurface(object_id, create_copy=False):
    """Shrinks the underlying untrimmed surfaces near to the trimming
    boundaries. See the ShrinkTrimmedSrf command in the Rhino help.
    Parameters:
      object_id = the surface's identifier
      create_copy[opt] = If True, the original surface is not deleted
    Returns:
      If create_copy is False, True or False indifating success or failure
      If create_copy is True, the identifier of the new surface
      None on error
    """
    brep = rhutil.coercebrep(object_id, True)
    if not brep.Faces.ShrinkFaces(): return scriptcontext.errorhandler()
    rc = None
    object_id = rhutil.coerceguid(object_id)
    if create_copy:
        oldobj = scriptcontext.doc.Objects.Find(object_id)
        attr = oldobj.Attributes
        rc = scriptcontext.doc.Objects.AddBrep(brep, attr)
    else:
        rc = scriptcontext.doc.Objects.Replace(object_id, brep)
    scriptcontext.doc.Views.Redraw()
    return rc


def __GetMassProperties(object_id, area):
    surface = rhutil.coercebrep(object_id)
    if surface is None:
        surface = rhutil.coercesurface(object_id)
        if surface is None: return None
    if area==True: return Rhino.Geometry.AreaMassProperties.Compute(surface)
    if not surface.IsSolid: return None
    return Rhino.Geometry.VolumeMassProperties.Compute(surface)


def SplitBrep(brep_id, cutter_id, delete_input=False):
    """Splits a brep
    Parameters:
      brep = identifier of the brep to split
      cutter = identifier of the brep to split with
    Returns:
      identifiers of split pieces on success
      None on error
    """
    brep = rhutil.coercebrep(brep_id, True)
    cutter = rhutil.coercebrep(cutter_id, True)
    tol = scriptcontext.doc.ModelAbsoluteTolerance
    pieces = brep.Split(cutter, tol)
    if not pieces: return scriptcontext.errorhandler()
    if delete_input:
        brep_id = rhutil.coerceguid(brep_id)
        scriptcontext.doc.Objects.Delete(brep_id, True)
    rc = [scriptcontext.doc.Objects.AddBrep(piece) for piece in pieces]
    scriptcontext.doc.Views.Redraw()
    return rc


def SurfaceArea(object_id):
    """Calculates the area of a surface or polysurface object. The results are
    based on the current drawing units
    Parameters:
      object_id = the surface's identifier
    Returns:
      list of area inforation on success (area, absolute error bound)
      None on error
    """
    amp = __GetMassProperties(object_id, True)
    if amp is None: return scriptcontext.errorhandler()
    return amp.Area, amp.AreaError


def SurfaceAreaCentroid(object_id):
    """Calculates the area centroid of a surface or polysurface
    Parameters:
      object_id = the surface's identifier
    Returns:
      (Area Centriod, Error bound) on success
      None on error
    """
    amp = __GetMassProperties(object_id, True)
    if amp is None: return scriptcontext.errorhandler()
    return amp.Centroid, amp.CentroidError


def __AreaMomentsHelper(surface_id, area):
    mp = __GetMassProperties(surface_id, area)
    if mp is None: return scriptcontext.errorhandler()
    a = (mp.WorldCoordinatesFirstMoments.X, mp.WorldCoordinatesFirstMoments.Y, mp.WorldCoordinatesFirstMoments.Z)
    b = (mp.WorldCoordinatesFirstMomentsError.X, mp.WorldCoordinatesFirstMomentsError.Y, mp.WorldCoordinatesFirstMomentsError.Z)
    c = (mp.WorldCoordinatesSecondMoments.X, mp.WorldCoordinatesSecondMoments.Y, mp.WorldCoordinatesSecondMoments.Z)
    d = (mp.WorldCoordinatesSecondMomentsError.X, mp.WorldCoordinatesSecondMomentsError.Y, mp.WorldCoordinatesSecondMomentsError.Z)
    e = (mp.WorldCoordinatesProductMoments.X, mp.WorldCoordinatesProductMoments.Y, mp.WorldCoordinatesProductMoments.Z)
    f = (mp.WorldCoordinatesProductMomentsError.X, mp.WorldCoordinatesProductMomentsError.Y, mp.WorldCoordinatesProductMomentsError.Z)
    g = (mp.WorldCoordinatesMomentsOfInertia.X, mp.WorldCoordinatesMomentsOfInertia.Y, mp.WorldCoordinatesMomentsOfInertia.Z)
    h = (mp.WorldCoordinatesMomentsOfInertiaError.X, mp.WorldCoordinatesMomentsOfInertiaError.Y, mp.WorldCoordinatesMomentsOfInertiaError.Z)
    i = (mp.WorldCoordinatesRadiiOfGyration.X, mp.WorldCoordinatesRadiiOfGyration.Y, mp.WorldCoordinatesRadiiOfGyration.Z)
    j = (0,0,0) # need to add error calc to RhinoCommon
    k = (mp.CentroidCoordinatesMomentsOfInertia.X, mp.CentroidCoordinatesMomentsOfInertia.Y, mp.CentroidCoordinatesMomentsOfInertia.Z)
    l = (mp.CentroidCoordinatesMomentsOfInertiaError.X, mp.CentroidCoordinatesMomentsOfInertiaError.Y, mp.CentroidCoordinatesMomentsOfInertiaError.Z)
    m = (mp.CentroidCoordinatesRadiiOfGyration.X, mp.CentroidCoordinatesRadiiOfGyration.Y, mp.CentroidCoordinatesRadiiOfGyration.Z)
    n = (0,0,0) #need to add error calc to RhinoCommon
    return (a,b,c,d,e,f,g,h,i,j,k,l,m,n)


def SurfaceAreaMoments(surface_id):
    """Calculates area moments of inertia of a surface or polysurface object.
    See the Rhino help for "Mass Properties calculation details"
    Parameters:
      surface_id = the surface's identifier
    Returns:
      list of moments and error bounds - see help topic
      None on error
    """
    return __AreaMomentsHelper(surface_id, True)


def SurfaceClosestPoint(surface_id, test_point):
    """Returns U,V parameters of point on a surface that is closest to a test point
    Parameters:
      surface_id = identifier of a surface object
      test_point = sampling point
    Returns:
      The U,V parameters of the closest point on the surface if successful.
      None on error.
    """
    surface = rhutil.coercesurface(surface_id, True)
    point = rhutil.coerce3dpoint(test_point, True)
    rc, u, v = surface.ClosestPoint(point)
    if not rc: return None
    return u,v


def SurfaceCone(surface_id):
    """Returns the definition of a surface cone
    Parameters:
      surface_id = the surface's identifier
    Returns:
      tuple containing the definition of the cone if successful
        element 0 = the plane of the cone. The apex of the cone is at the
            plane's origin and the axis of the cone is the plane's z-axis
        element 1 = the height of the cone
        element 2 = the radius of the cone
      None on error
    """
    surface = rhutil.coercesurface(surface_id, True)
    rc, cone = surface.TryGetCone()
    if not rc: return scriptcontext.errorhandler()
    return cone.Plane, cone.Height, cone.Radius


def SurfaceCurvature(surface_id, parameter):
    """Returns the curvature of a surface at a U,V parameter. See Rhino help
    for details of surface curvature
    Parameters:
      surface_id = the surface's identifier
      parameter = u,v parameter
    Returns:
      tuple of curvature information
        element 0 = point at specified U,V parameter
        element 1 = normal direction
        element 2 = maximum principal curvature
        element 3 = maximum principal curvature direction
        element 4 = minimum principal curvature
        element 5 = minimum principal curvature direction
        element 6 = gaussian curvature
        element 7 = mean curvature
      None if not successful, or on error
    """
    surface = rhutil.coercesurface(surface_id, True)
    if len(parameter)<2: return scriptcontext.errorhandler()
    c = surface.CurvatureAt(parameter[0], parameter[1])
    if c is None: return scriptcontext.errorhandler()
    return c.Point, c.Normal, c.Kappa(0), c.Direction(0), c.Kappa(1), c.Direction(1), c.Gaussian, c.Mean


def SurfaceDegree(surface_id, direction=2):
    """Returns the degree of a surface object in the specified direction
    Parameters:
      surface_id = the surface's identifier
      direction[opt]
        0 = U, 1 = v, 2 = both
    Returns:
      Tuple of two values if direction = 2
      Single number if direction = 0 or 1
      None on error
    """
    surface = rhutil.coercesurface(surface_id, True)
    if direction==0 or direction==1: return surface.Degree(direction)
    if direction==2: return surface.Degree(0), surface.Degree(1)
    return scriptcontext.errorhandler()


def SurfaceDomain(surface_id, direction):
    """Returns the domain of a surface object in the specified direction.
    Parameters:
      surface_id = the surface's identifier
      direction = either 0 = U, or 1 = V
    Returns:
      list containing the domain interval in the specified direction
      None if not successful, or on error
    """
    if direction!=0 and direction!=1: return scriptcontext.errorhandler()
    surface = rhutil.coercesurface(surface_id, True)
    domain = surface.Domain(direction)
    return domain.T0, domain.T1


def SurfaceEditPoints(surface_id, return_parameters=False, return_all=True):
    """Returns the edit, or Greville points of a surface object. For each
    surface control point, there is a corresponding edit point
    Parameters:
      surface_id = the surface's identifier
      return_parameters[opt] = If False, edit points are returned as a list of
        3D points. If True, edit points are returned as a list of U,V surface
        parameters
      return_all[opt] = If True, all surface edit points are returned. If False,
        the function will return surface edit points based on whether or not the
        surface is closed or periodic
    Returns:
      if return_parameters is False, a list of 3D points
      if return_parameters is True, a list of U,V parameters
      None on error
    """
    surface = rhutil.coercesurface(surface_id, True)
    nurb = surface.ToNurbsSurface()
    if not nurb: return scriptcontext.errorhandler()
    ufirst = 0
    ulast = nurb.Points.CountU
    vfirst = 0
    vlast = nurb.Points.CountV
    if not return_all:
        if nurb.IsClosed(0): ulast = nurb.Points.CountU-1
        if nurbs.IsPeriodic(0):
            degree = nurb.Degree(0)
            ufirst = degree/2
            ulast = nurb.Points.CountU-degree+ufirst
        if nurb.IsClosed(1): vlast = nurb.Points.CountV-1
        if nurbs.IsPeriodic(1):
            degree = nurb.Degree(1)
            vfirst = degree/2
            vlast = nurb.Points.CountV-degree+vfirst
    rc = []
    for u in range(ufirst, ulast):
        for v in range(vfirst, vlast):
            pt = nurb.Points.GetGrevillePoint(u,v)
            if not return_parameters: pt = nurb.PointAt(pt.X, pt.Y)
            rc.append(pt)
    return rc


def SurfaceEvaluate(surface_id, parameter, derivative):
    """A general purpose surface evaluator
    Parameters:
      surface_id = the surface's identifier
      parameter = u,v parameter to evaluate
      derivative = number of derivatives to evaluate
    Returns:
      list of derivatives on success
      None on error
    """
    surface = rhutil.coercesurface(surface_id, True)
    success, point, der = surface.Evaluate(parameter[0], parameter[1], derivative)
    if not success: return scriptcontext.errorhandler()
    rc = [point]
    for d in der: rc.append(d)
    return rc


def SurfaceFrame(surface_id, uv_parameter):
    """Returns a plane based on the normal, u, and v directions at a surface
    U,V parameter
    Parameters:
      surface_id = the surface's identifier
      uv_parameter = u,v parameter to evaluate
    Returns:
      plane on success
      None on error
    """
    surface = rhutil.coercesurface(surface_id, True)
    rc, frame = surface.FrameAt(uv_parameter[0], uv_parameter[1])
    if rc: return frame


def SurfaceIsocurveDensity(surface_id, density=None):
    """Returns or sets the isocurve density of a surface or polysurface object.
    An isoparametric curve is a curve of constant U or V value on a surface.
    Rhino uses isocurves and surface edge curves to visualize the shape of a
    NURBS surface
    Parameters:
      surface_id = the surface's identifier
      density[opt] = the isocurve wireframe density. The possible values are
          -1: Hides the surface isocurves
           0: Display boundary and knot wires
           1: Display boundary and knot wires and one interior wire if there
              are no interior knots
         >=2: Display boundary and knot wires and (N+1) interior wires
    Returns:
      If density is not specified, then the current isocurve density if successful
      If density is specified, the the previous isocurve density if successful
      None on error
    """
    rhino_object = rhutil.coercerhinoobject(surface_id, True, True)
    if not isinstance(rhino_object, Rhino.DocObjects.BrepObject):
        return scriptcontext.errorhandler()
    rc = rhino_object.Attributes.WireDensity
    if density is not None:
        if density<0: density = -1
        rhino_object.Attributes.WireDensity = density
        rhino_object.CommitChanges()
        scriptcontext.doc.Views.Redraw()
    return rc


def SurfaceKnotCount(surface_id):
    """Returns the control point count of a surface
      surface_id = the surface's identifier
    Returns:
      (U count, V count) on success
      None on error
    """
    surface = rhutil.coercesurface(surface_id, True)
    ns = surface.ToNurbsSurface()
    if ns is None: return scriptcontext.errorhandler()
    return ns.KnotsU.Count, ns.KnotsV.Count


def SurfaceKnots(surface_id):
    """Returns the knots, or knot vector, of a surface object.
    Parameters:
      surface_id = the surface's identifier
    Returns:
      The list of knot values of the surface if successful. The list will
      contain the following information:
      Element     Description
        0         Knot vector in U direction
        1         Knot vector in V direction
      None if not successful, or on error.
    """
    surface = rhutil.coercesurface(surface_id, True)
    nurb_surf = surface.ToNurbsSurface()
    if nurb_surf is None: return scriptcontext.errorhandler()
    s_knots = [knot for knot in nurb_surf.KnotsU]
    t_knots = [knot for knot in nurb_surf.KnotsV]
    if not s_knots or not t_knots: return scriptcontext.errorhandler()
    return s_knots, t_knots


def SurfaceNormal(surface_id, uv_parameter):
    """Returns 3D vector that is the normal to a surface at a parameter
    Parameters:
      surface_id = the surface's identifier
      uv_parameter = the uv parameter to evaluate
    Returns:
      Normal vector on success
      None on error
    """
    surface = rhutil.coercesurface(surface_id, True)
    normal = surface.NormalAt(uv_parameter[0], uv_parameter[1])
    return normal


def SurfaceNormalizedParameter(surface_id, parameter):
    """Converts surface parameter to a normalized surface parameter; one that
    ranges between 0.0 and 1.0 in both the U and V directions
    Parameters:
      surface_id = the surface's identifier
      parameter = the surface parameter to convert
    Returns:
      normalized surface parameter if successful
      None on error
    """
    surface = rhutil.coercesurface(surface_id, True)
    u_domain = surface.Domain(0)
    v_domain = surface.Domain(1)
    if parameter[0]<u_domain.Min or parameter[0]>u_domain.Max:
        return scriptcontext.errorhandler()
    if parameter[1]<v_domain.Min or parameter[1]>v_domain.Max:
        return scriptcontext.errorhandler()
    u = u_domain.NormalizedParameterAt(parameter[0])
    v = v_domain.NormalizedParameterAt(parameter[1])
    return u,v


def SurfaceParameter(surface_id, parameter):
    """Converts normalized surface parameter to a surface parameter; or
    within the surface's domain
    Parameters:
      surface_id = the surface's identifier
      parameter = the normalized parameter to convert
    Returns:
      surface parameter as tuple on success
      None on error
    """
    surface = rhutil.coercesurface(surface_id, True)
    x = surface.Domain(0).ParameterAt(parameter[0])
    y = surface.Domain(1).ParameterAt(parameter[1])
    return x, y


def SurfacePointCount(surface_id):
    """Returns the control point count of a surface
      surface_id = the surface's identifier
    Returns:
      (U count, V count) on success
      None on error
    """
    surface = rhutil.coercesurface(surface_id, True)
    ns = surface.ToNurbsSurface()
    if ns is None: return scriptcontext.errorhandler()
    return ns.Points.CountU, ns.Points.CountV


def SurfacePoints(surface_id, return_all=True):
    """Returns the control points, or control vertices, of a surface object
    Parameters:
      surface_id = the surface's identifier
      return_all[opt] = If True all surface edit points are returned. If False,
        the function will return surface edit points based on whether or not
        the surface is closed or periodic
    Returns:
      the control points if successful
      None on error
    """
    surface = rhutil.coercesurface(surface_id, True)
    ns = surface.ToNurbsSurface()
    if ns is None: return scriptcontext.errorhandler()
    ucount = ns.Points.CountU
    vcount = ns.Points.CountV
    rc = []
    for u in range(ucount):
        for v in range(vcount):
            pt = ns.Points.GetControlPoint(u,v)
            rc.append(pt.Location)
    return rc


def SurfaceTorus(surface_id):
    """Returns the definition of a surface torus
    Parameters:
      surface_id = the surface's identifier
    Returns:
      tuple containing the definition of the torus if successful
        element 0 = the base plane of the torus
        element 1 = the major radius of the torus
        element 2 = the minor radius of the torus
      None on error
    """
    surface = rhutil.coercesurface(surface_id, True)
    rc, torus = surface.TryGetTorus()
    if not rc: return scriptcontext.errorhandler()
    return torus.Plane, torus.MajorRadius, torus.MinorRadius


def SurfaceVolume(object_id):
    """Calculates the volume of a closed surface or polysurface
    Parameters:
      object_id = the surface's identifier
    Returns:
      (Volume, Error bound) on success
      None on error
    """
    vmp = __GetMassProperties(object_id, False)
    if vmp is None: return scriptcontext.errorhandler()
    return vmp.Volume, vmp.VolumeError


def SurfaceVolumeCentroid(object_id):
    """Calculates the volume centroid of a closed surface or polysurface
    Parameters:
      object_id = the surface's identifier
    Returns:
      (Volume Centriod, Error bound) on success
      None on error
    """
    vmp = __GetMassProperties(object_id, False)
    if vmp is None: return scriptcontext.errorhandler()
    return vmp.Centroid, vmp.CentroidError


def SurfaceVolumeMoments(surface_id):
    """Calculates the volume moments of inertia of a surface or polysurface object.
    For more information, see Rhino help for "Mass Properties calculation details"
    Parameters:
      surface_id = the surface's identifier
    Returns:
      list of moments and error bounds - see help topic
      None on error
    """
    return __AreaMomentsHelper(surface_id, False)


def SurfaceWeights(object_id):
    """Returns list of weight values that are assigned to the control points of
    a surface. The number of weights returned will be equal to the number of
    control points in the U and V directions.
    Parameters:
      object_id = the surface's identifier
    Returns:
      list of weights
      None on error
    """
    surface = rhutil.coercesurface(object_id, True)
    ns = surface.ToNurbsSurface()
    if ns is None: return scriptcontext.errorhandler()
    ucount = ns.Points.CountU
    vcount = ns.Points.CountV
    rc = []
    for u in range(ucount):
        for v in range(vcount):
            pt = ns.Points.GetControlPoint(u,v)
            rc.append(pt.Weight)
    return rc
