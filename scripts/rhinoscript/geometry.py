import scriptcontext
import utility as rhutil
import Rhino
import System.Guid
import System.Array

def AddClippingPlane(plane, u_magnitude, v_magnitude, views=None):
    """
    Creates a clipping plane. A clipping plane is a plane for visibly
    clipping away geometry in a specific view. Note, clipping planes
    are infinite
    Parameters:
      plane = the plane
      u_magnitude, v_magnitude = size of the plane
      views [opt] = string, Guid, list of strings or list of Guids. The
        titles or ids the the view(s) to clip. If omitted, the active
        view is used.
    Returns:
      object identifier on success
      None on failure  
    """
    viewlist = []
    if views is None:
        viewlist.append(scriptcontext.doc.Views.ActiveView.ActiveViewportID)
    else:
        if( type(views) is System.Guid ):
            viewlist.append(views)
        elif( type(views) is str ):
            modelviews = scriptcontext.doc.Views.GetViewList(True, False)
            rc = None
            for item in modelviews:
                if item.Name == views:
                    id = item.ActiveViewportID
                    rc = AddClippingPlane(plane, u_magnitude, v_magnitude, id)
                    break
            return rc
        elif views:
            if( type(views[0]) is System.Guid ):
                viewlist = views
            elif( type(views[0]) is str ):
                modelviews = scriptcontext.doc.Views.GetViewList(True,False)
                for viewname in views:
                    for item in modelviews:
                        if item.Name==viewname:
                            viewlist.append(item.ActiveViewportID)
                            break
    if not viewlist: return scriptcontext.errorhandler()
    rc = scriptcontext.doc.Objects.AddClippingPlane(plane, u_magnitude, v_magnitude, viewlist)
    if rc==System.Guid.Empty: return scriptcontext.errorhandler()
    scriptcontext.doc.Views.Redraw()
    return rc

def AddPoint(point):
    """
    Adds a point object to the document
    Parameters:
      point = x,y,z location of point to add
    Returns:
      Guid for the object that was added to the doc on success
      None on failure
    """
    point = rhutil.coerce3dpoint(point)
    if point is None: return scriptcontext.errorhandler()
    rc = scriptcontext.doc.Objects.AddPoint(point)
    if rc==System.Guid.Empty: return scriptcontext.errorhandler()
    scriptcontext.doc.Views.Redraw()
    return rc


def AddPointCloud(points):
    """
    Adds a point cloud object to the document
    Parameters:
      points = list of values where every multiple of three represents a point
    Returns:
      identifier of point cloud on success
      None on failure
    """
    points = rhutil.coerce3dpointlist(points)
    if( points==None ): return scriptcontext.errorhandler()
    rc = scriptcontext.doc.Objects.AddPointCloud(points)
    if( rc==System.Guid.Empty ): return scriptcontext.errorhandler()
    scriptcontext.doc.Views.Redraw()
    return rc


def AddPoints(points):
    """
    Adds one or more point objects to the document
    Parameters:
      points = list of points
    Returns:
      list of Guid identifiers of the new objects on success
      None on error
    """
    points = rhutil.coerce3dpointlist(points)
    if points is None: return scriptcontext.errorhandler()
    rc = [scriptcontext.doc.Objects.AddPoint(point) for point in points]
    scriptcontext.doc.Views.Redraw()
    return rc


def AddText( text, point_or_plane, height=1.0, font="Arial", font_style=0 ):
    """
    Adds a text string to the document
    Parameters:
      text = the text to display
      point_or_plane = a 3-D point or the plane on which the text will lie.
          The origin of the plane will be the origin point of the text
      height [opt] = the text height
      font [opt] = the text font
      font_style = any of the following flags
         0 = normal
         1 = bold
         2 = italic
         3 = bold and italic
    Returns:
      Guid for the object that was added to the doc on success
      None on failure
    """
    if text is None: return scriptcontext.errorhandler()
    point = rhutil.coerce3dpoint(point_or_plane)
    plane = rhutil.coerceplane(point_or_plane)
    if point is None and plane is None: return scriptcontext.errorhandler()
    if plane is None:
        plane = scriptcontext.doc.Views.ActiveView.ActiveViewport.ConstructionPlane()
        plane.Origin = point
    bold = (1==font_style or 3==font_style)
    italic = (2==font_style or 3==font_style)
    id = scriptcontext.doc.Objects.AddText(text, plane, height, font, bold, italic)
    if id==System.Guid.Empty: return scriptcontext.errorhandler()
    scriptcontext.doc.Views.Redraw()
    return id


def AddTextDot( text, point ):
    """
    Adds an annotation text dot to the document.
    Parameters:
      text = string in dot
      point = A 3-D point identifying the origin point.
    Returns:
      The identifier of the new object if successful
      None if not successful, or on error
    """
    point = rhutil.coerce3dpoint(point)
    if point is None: return scriptcontext.errorhandler()
    rc = scriptcontext.doc.Objects.AddTextDot(str(text), point)
    if rc==System.Guid.Empty: return scriptcontext.errorhandler()
    scriptcontext.doc.Views.Redraw()
    return rc


def Area( object_id ):
    "Compute the area of a closed curve, hatch, surface, polysurface, or mesh"
    id = rhutil.coerceguid(object_id)
    if id is None: return scriptcontext.errorhandler()
    rhobj = scriptcontext.doc.Objects.Find(id)
    if rhobj is None: return scriptcontext.errorhandler()
    mp = Rhino.Geometry.AreaMassProperties.Compute(rhobj.Geometry)
    if mp is None: return scriptcontext.errorhandler()
    return mp.Area

def __GetObjRef(id):
    id = rhutil.coerceguid(id)
    if( id==None ): return None
    objref = Rhino.DocObjects.ObjRef(id)
    return objref

def BoundingBox( objects, view_or_plane=None, in_world_coords=True ):
    """
    Returns either a world axis-aligned or a construction plane axis-aligned
    bounding box of an object or of several objects
    Parameters:
      objects = The identifiers of the objects
      view_or_plane[opt] = The title or id of the view that contains the
          construction plane to which the bounding box should be aligned -or-
          user defined plane. If omitted, a world axis-aligned bounding box
          will be calculated
      in_world_coords[opt] = whether or not to return the bounding box as
          world coordinates or construction plane coordinates. Note, this
          option does not apply to world axis-aligned bounding boxes.
    Returns:
      A list of eight 3-D points that define the bounding box if successful. Points are returned
      in counter-clockwise order starting with the bottom rectangle of the box.
      None if not successful, or on error
    """
    def __objectbbox(object, xform):
        objref = __GetObjRef(object)
        if objref is None: return None
        geom = objref.Geometry()
        if geom is None: return None
        if xform: return geom.GetBoundingBox(xform)
        return geom.GetBoundingBox(True)

    if objects is None: return scriptcontext.errorhandler()
    xform = None
    plane = rhutil.coerceplane(view_or_plane)
    if plane is None and view_or_plane is not None:
        view = view_or_plane
        modelviews = scriptcontext.doc.Views.GetStandardRhinoViews()
        for item in modelviews:
            viewport = item.MainViewport
            if( type(view) is str and viewport.Name==view ):
                plane = viewport.ConstructionPlane()
                break
            elif( type(view) is System.Guid and viewport.Id==view ):
                plane = viewport.ConstructionPlane()
                break
        if plane is None: return scriptcontext.errorhandler()
        xform = Rhino.Geometry.Transform.ChangeBasis(Rhino.Geometry.Plane.WorldXY, plane)
    bbox = Rhino.Geometry.BoundingBox.Empty
    if( type(objects) is list or type(objects) is tuple ):
        for object in objects:
            objectbbox = __objectbbox(object, xform)
            if objectbbox: bbox = Rhino.Geometry.BoundingBox.Union(bbox,objectbbox)
    else:
        objectbbox = __objectbbox(objects, xform)
        if objectbbox: bbox = Rhino.Geometry.BoundingBox.Union(bbox,objectbbox)
    if not bbox.IsValid: return scriptcontext.errorhandler()

    corners = bbox.GetCorners()
    if in_world_coords and plane is not None:
        plane_to_world = Rhino.Geometry.Transform.ChangeBasis(plane, Rhino.Geometry.Plane.WorldXY)
        return [pt.Transform(plane_to_world) for pt in corners]
    return corners


def IsClippingPlane( object_id ):
    """
    Verifies that an object is a clipping plane object
    Parameters:
      object_id: the object's identifier
    Returns:
      True if the object with a given id is a clipping plane
    """
    objref = __GetObjRef(object_id)
    return objref and objref.ClippingPlaneSurface()


def IsPoint( object_id ):
    """
    Verifies an object is a point object.
    Parameters:
      object_id: the object's identifier
    Returns:
      True if the object with a given id is a point
    """
    objref = __GetObjRef(object_id)
    return objref and objref.Point()


def IsPointCloud( object_id ):
    """
    Verifies an object is a point cloud object.
    Parameters:
      object_id: the object's identifier
    Returns:
      True if the object with a given id is a point cloud
    """
    objref = __GetObjRef(object_id)
    return objref and objref.PointCloud()


def IsText( object_id ):
    """
    Verifies an object is a text object.
    Parameters:
      object_id: the object's identifier
    Returns:
      True if the object with a given id is a text object
    """
    objref = __GetObjRef(object_id)
    return objref and objref.TextEntity()


def IsTextDot( object_id ):
    """
    Verifies an object is a text dot object.
    Parameters:
      object_id: the object's identifier
    Returns:
      True if the object with a given id is a text dot object
    """
    objref = __GetObjRef(object_id)
    return objref and objref.TextDot()


def PointCloudCount( object_id ):
    """
    Returns the point count of a point cloud object
    Parameters:
      object_id: the point cloud object's identifier
    Returns:
      number of points if successful
      None on error (object_id does not represent a point cloud)
    """
    objref = __GetObjRef( object_id )
    if objref is None: return scriptcontext.errorhandler()
    cloud = objref.PointCloud()
    if cloud is None: return scriptcontext.errorhandler()
    return cloud.PointCount


def PointCloudPoints(object_id):
    """
    Returns the points of a point cloud object
    Parameters:
      object_id: the point cloud object's identifier
    Returns:
      list of points if successful
      None on error (object_id does not represent a point cloud)
    """
    objref = __GetObjRef( object_id )
    if objref is None: return scriptcontext.errorhandler()
    cloud = objref.PointCloud()
    if cloud is None: return scriptcontext.errorhandler()
    return cloud.GetPoints()


def PointCoordinates(object_id, point=None):
    """
    Returns or modifies the X, Y, and Z coordinates of a point object
    Parameters:
      object_id = The identifier of a point object
      point [opt] = A new 3-D point location.
    Returns:
      If point is not specified, the current 3-D point location
      If point is specified, the previous 3-D point location
      None if not successful, or on error
    """
    objref = __GetObjRef( object_id )
    if objref is None: return scriptcontext.errorhandler()
    pointgeom = objref.Point()
    if pointgeom is None: return scriptcontext.errorhandler()
    rc = pointgeom.Location
    point = rhutil.coerce3dpoint(point)
    if point is not None:
        scriptcontext.doc.Objects.Replace(objref, point)
        scriptcontext.doc.Views.Redraw()
    return rc


def TextDotPoint(object_id, point=None):
    """
    Returns or modifies the location, or insertion point, on a text dot object
    Parameters:
      object_id = The identifier of a text dot object
      point [opt] = list of 3 numbers or a Point3d. A new 3-D point location.
    Returns:
      If point is not specified, the current 3-D text dot location
      If point is specified, the previous 3-D text dot location
      None if not successful, or on error
    """
    objref = __GetObjRef( object_id )
    textdot = objref.TextDot() if objref else None
    if textdot is None: return scriptcontext.errorhandler()
    rc = textdot.Point
    point = rhutil.coerce3dpoint(point)
    if point is not None:
        textdot.Point = point
        scriptcontext.doc.Objects.Replace(objref, textdot)
        scriptcontext.doc.Views.Redraw()
    return rc


def TextDotText(object_id, text=None):
    """
    Returns or modifies the text on a text dot object
    Parameters:
      object_id =tThe identifier of a text dot object
      text [opt] = a new string for the dot
    Returns:
      If text is not specified, the current text dot text
      If text is specified, the previous text dot text
      None if not successful, or on error
    """
    objref = __GetObjRef( object_id )
    textdot = objref.TextDot() if objref else None
    if textdot is None: return scriptcontext.errorhandler()
    rc = textdot.Text
    if text is not None:
        textdot.Text = str(text)
        scriptcontext.doc.Objects.Replace(objref, textdot)
        scriptcontext.doc.Views.Redraw()
    return rc


def TextObjectFont(object_id, font=None):
    """
    Returns of modifies the font used by a text object
    Parameters:
      object_id = the identifier of a text object
      font [opt] = the new font face name
    Returns:
      if a font is not specified, the current font face name
      if a font is specified, the previous font face name
      None if not successful, or on error
    """
    objref = __GetObjRef( object_id )
    annotation = objref.TextEntity() if objref else None
    if annotation is None: return scriptcontext.errorhandler()
    fontdata = scriptcontext.doc.Fonts[annotation.FontIndex]
    if fontdata is None: return scriptcontext.errorhandler()
    rc = fontdata.FaceName
    if font:
        index = scriptcontext.doc.Fonts.FindOrCreate( font, fontdata.Bold, fontdata.Italic )
        annotation.FontIndex = index
        scriptcontext.doc.Objects.Replace(objref, annotation)
        scriptcontext.doc.Views.Redraw()
    return rc


def TextObjectHeight(object_id, height=None):
    """
    Returns or modifies the height of a text object
    Parameters:
      object_id = the identifier of a text object
      height [opt] = the new text height.
    Returns:
      if height is not specified, the current text height
      if height is specified, the previous text height
      None if not successful, or on error
    """
    objref = __GetObjRef( object_id )
    annotation = objref.TextEntity() if objref else None
    if annotation is None: return scriptcontext.errorhandler()
    rc = annotation.TextHeight
    if height:
        annotation.TextHeight = height
        scriptcontext.doc.Objects.Replace(objref, annotation)
        scriptcontext.doc.Views.Redraw()
    return rc


def TextObjectPlane(object_id, plane=None):
    """
    Returns or modifies the plane used by a text object
    Parameters:
      object_id = the identifier of a text object
      plane [opt] = the new text object plane
    Returns:
      if a plane is not specified, the current plane if successful
      if a plane is specified, the previous plane if successful
      None if not successful, or on Error
    """
    objref = __GetObjRef( object_id )
    annotation = objref.TextEntity() if objref else None
    if annotation is None: return scriptcontext.errorhandler()
    rc = annotation.Plane
    plane = rhutil.coerceplane(plane)
    if plane is not None:
        annotation.Plane = plane
        scriptcontext.doc.Objects.Replace(objref, annotation)
        scriptcontext.doc.Views.Redraw()
    return rc


def TextObjectPoint(object_id, point=None):
    """
    Returns or modifies the location of a text object
    Parameters:
      object_id = the identifier of a text object
      point [opt] = the new text object location
    Returns:
      if point is not specified, the 3D point identifying the current location
      if point is specified, the 3D point identifying the previous location
      None if not successful, or on Error
    """
    objref = __GetObjRef( object_id )
    text = objref.TextEntity() if objref else None
    if text is None: return scriptcontext.errorhandler()
    plane = text.Plane
    rc = plane.Origin
    point = rhutil.coerce3dpoint(point)
    if point is not None:
        plane.Origin = point
        text.Plane = plane
        scriptcontext.doc.Objects.Replace(objref, text)
        scriptcontext.doc.Views.Redraw()
    return rc


def TextObjectStyle(object_id, style=None):
    """
    Returns or modifies the font style of a text object
    Parameters:
      object_id = the identifier of a text object
      style [opt] = the font style. Can be any of the following flags
         0 = Normal
         1 = Bold
         2 = Italic
    Returns:
      if style is not specified, the current font style
      if style is specified, the previous font style
      None if not successful, or on Error
    """
    objref = __GetObjRef( object_id )
    annotation = objref.TextEntity() if objref else None
    if annotation is None: return scriptcontext.errorhandler()
    fontdata = scriptcontext.doc.Fonts[annotation.FontIndex]
    if fontdata is None: return scriptcontext.errorhandler()
    rc = 0
    if fontdata.Bold: rc += 1
    if fontdata.Italic: rc += 2
    if style is not None and style!=rc:
        index = scriptcontext.doc.Fonts.FindOrCreate( fontdata.FaceName, (style&1)==1, (style&2)==2 )
        annotation.FontIndex = index
        scriptcontext.doc.Objects.Replace(objref, annotation)
        scriptcontext.doc.Views.Redraw()
    return rc


def TextObjectText(object_id, text=None):
    """
    Returns or modifies the text string of a text object.
    Parameters:
      object_id = the identifier of a text object
      text [opt] = a new text string
    Returns:
      if text is not specified, the current string value if successful
      if text is specified, the previous string value if successful
      None if not successful, or on error
    """
    objref = __GetObjRef( object_id )
    annotation = objref.TextEntity() if objref else None
    if annotation is None: return scriptcontext.errorhandler()
    rc = annotation.Text
    if text is not None:
        annotation.Text = text
        scriptcontext.doc.Objects.Replace(objref, annotation)
        scriptcontext.doc.Views.Redraw()
    return rc
