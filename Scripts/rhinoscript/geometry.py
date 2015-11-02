import scriptcontext
import utility as rhutil
import Rhino
import System.Guid, System.Array


def AddClippingPlane(plane, u_magnitude, v_magnitude, views=None):
    """Create a clipping plane for visibly clipping away geometry in a specific
    view. Note, clipping planes are infinite
    Parameters:
      plane = the plane
      u_magnitude, v_magnitude = size of the plane
      views[opt]= Titles or ids the the view(s) to clip. If omitted, the active
        view is used.
    Returns:
      object identifier on success
      None on failure  
    Example:
      import rhinoscriptsyntax as rs
      rs.AddClippingPlane( rs.WorldXYPlane(), 5.0, 3.0 )
    See Also:
      IsClippingPlane
    """
    viewlist = []
    if views:
        if type(views) is System.Guid:
            viewlist.append(views)
        elif type(views) is str:
            modelviews = scriptcontext.doc.Views.GetViewList(True, False)
            rc = None
            for item in modelviews:
                if item.ActiveViewport.Name == views:
                    id = item.ActiveViewportID
                    rc = AddClippingPlane(plane, u_magnitude, v_magnitude, id)
                    break
            return rc
        else:
            if type(views[0]) is System.Guid:
                viewlist = views
            elif( type(views[0]) is str ):
                modelviews = scriptcontext.doc.Views.GetViewList(True,False)
                for viewname in views:
                    for item in modelviews:
                        if item.ActiveViewport.Name==viewname:
                            viewlist.append(item.ActiveViewportID)
                            break
    else:
        viewlist.append(scriptcontext.doc.Views.ActiveView.ActiveViewportID)
    if not viewlist: return scriptcontext.errorhandler()
    rc = scriptcontext.doc.Objects.AddClippingPlane(plane, u_magnitude, v_magnitude, viewlist)
    if rc==System.Guid.Empty: raise Exception("unable to add clipping plane to document")
    scriptcontext.doc.Views.Redraw()
    return rc

def AddPictureFrame(plane, filename, width=0.0, height=0.0, self_illumination=True, embed=False, use_alpha=False, make_mesh=False):
  """Creates a picture frame and adds it to the document.
  Parameters:
    plane = The plane in which the PictureFrame will be created.  The bottom-left corner of picture will be at plane's origin. The width will be in the plane's X axis direction, and the height will be in the plane's Y axis direction.
    filename = The path to a bitmap or image file.
    width = If both dblWidth and dblHeight = 0, then the width and height of the PictureFrame will be the width and height of the image. If dblWidth = 0 and dblHeight is > 0, or if dblWidth > 0 and dblHeight = 0, then the non-zero value is assumed to be an aspect ratio of the image's width or height, which ever one is = 0. If both dblWidth and dblHeight are > 0, then these are assumed to be the width and height of in the current unit system.
    height =  If both dblWidth and dblHeight = 0, then the width and height of the PictureFrame will be the width and height of the image. If dblWidth = 0 and dblHeight is > 0, or if dblWidth > 0 and dblHeight = 0, then the non-zero value is assumed to be an aspect ratio of the image's width or height, which ever one is = 0. If both dblWidth and dblHeight are > 0, then these are assumed to be the width and height of in the current unit system.
    self_illumination =  If True, then the image mapped to the picture frame plane always displays at full intensity and is not affected by light or shadow.
    embed = If True, then the function adds the image to Rhino's internal bitmap table, thus making the document self-contained.
    use_alpha = If False, the picture frame is created without any transparency texture.  If True, a transparency texture is created with a "mask texture" set to alpha, and an instance of the diffuse texture in the source texture slot.
    make_mesh = If True, the function will make a PictureFrame object from a mesh rather than a plane surface.
  Returns:
    object identifier on success
    None on failure
  Example:
    
  See Also:
    
  """
  plane = rhutil.coerceplane(plane, True)
  if type(filename) is not System.String or not System.IO.File.Exists(filename): raise Exception('\"{0}\" does not exist or is not a file name'.format(filename))
  rc = scriptcontext.doc.Objects.AddPictureFrame(plane, filename, make_mesh, width, height, self_illumination, embed) 
  if rc==System.Guid.Empty: raise Exception("unable to add picture frame to document")
  scriptcontext.doc.Views.Redraw()
  return rc

def AddPoint(point, y=None, z=None):
    """Adds point object to the document
    Parameters:
      point = x,y,z location of point to add
    Returns:
      Guid for the object that was added to the doc
    Example:
      import rhinoscriptsyntax as rs
      rs.AddPoint( (1,2,3) )
    See Also:
      IsPoint
      PointCoordinates
    """
    if y is not None and z is not None: point = Rhino.Geometry.Point3d(point,y,z)
    point = rhutil.coerce3dpoint(point, True)
    rc = scriptcontext.doc.Objects.AddPoint(point)
    if rc==System.Guid.Empty: raise Exception("unable to add point to document")
    scriptcontext.doc.Views.Redraw()
    return rc


def AddPointCloud(points, colors=None):
    """Adds point cloud object to the document
    Parameters:
      points = list of values where every multiple of three represents a point
      colors[opt] = list of colors to apply to each point
    Returns:
      identifier of point cloud on success
    Example:
      import rhinoscriptsyntax as rs
      points = (0,0,0), (1,1,1), (2,2,2), (3,3,3)
      rs.AddPointCloud(points)
    See Also:
      IsPointCloud
      PointCloudCount
      PointCloudPoints
    """
    points = rhutil.coerce3dpointlist(points, True)
    if colors and len(colors)==len(points):
        pc = Rhino.Geometry.PointCloud()
        for i in range(len(points)):
            color = rhutil.coercecolor(colors[i],True)
            pc.Add(points[i],color)
        points = pc
    rc = scriptcontext.doc.Objects.AddPointCloud(points)
    if rc==System.Guid.Empty: raise Exception("unable to add point cloud to document")
    scriptcontext.doc.Views.Redraw()
    return rc


def AddPoints(points):
    """Adds one or more point objects to the document
    Parameters:
      points = list of points
    Returns:
      list of Guid identifiers of the new objects on success
    Example:
      import rhinoscriptsyntax as rs
      points = rs.GetPoints(True, True, "Select points")
      if points: rs.AddPoints(points)
    See Also:
      AddPoint
      AddPointCloud
    """
    points = rhutil.coerce3dpointlist(points, True)
    rc = [scriptcontext.doc.Objects.AddPoint(point) for point in points]
    scriptcontext.doc.Views.Redraw()
    return rc


def AddText(text, point_or_plane, height=1.0, font="Arial", font_style=0, justification=None):
    """Adds a text string to the document
    Parameters:
      text = the text to display
      point_or_plane = a 3-D point or the plane on which the text will lie.
          The origin of the plane will be the origin point of the text
      height [opt] = the text height
      font [opt] = the text font
      font_style[opt] = any of the following flags
         0 = normal
         1 = bold
         2 = italic
         3 = bold and italic
      justification[opt] = text justification (see help for values)
    Returns:
      Guid for the object that was added to the doc on success
      None on failure
    Example:
      import rhinoscriptsyntax as rs
      point = rs.GetPoint("Pick point")
      if point: rs.AddText("Hello Rhino!", point)
    See Also:
      IsText
    """
    if not text: raise ValueError("text invalid")
    if not isinstance(text, str): text = str(text)
    point = rhutil.coerce3dpoint(point_or_plane)
    plane = None
    if not point: plane = rhutil.coerceplane(point_or_plane, True)
    if not plane:
        plane = scriptcontext.doc.Views.ActiveView.ActiveViewport.ConstructionPlane()
        plane.Origin = point
    bold = (1==font_style or 3==font_style)
    italic = (2==font_style or 3==font_style)
    id = None
    if justification is None:
        id = scriptcontext.doc.Objects.AddText(text, plane, height, font, bold, italic)
    else:
        just = System.Enum.ToObject(Rhino.Geometry.TextJustification, justification)
        id = scriptcontext.doc.Objects.AddText(text, plane, height, font, bold, italic, just)
    if id==System.Guid.Empty: raise ValueError("unable to add text to document")
    scriptcontext.doc.Views.Redraw()
    return id


def AddTextDot(text, point):
    """Add a text dot to the document.
    Parameters:
      text = string in dot
      point = A 3D point identifying the origin point.
    Returns:
      The identifier of the new object if successful
    Example:
      import rhinoscriptsyntax as rs
      rs.AddTextDot("howdy",(1,2,3))
    See Also:
      IsTextDot
    """
    point = rhutil.coerce3dpoint(point, True)
    if not isinstance(text, str): text = str(text)
    rc = scriptcontext.doc.Objects.AddTextDot(text, point)
    if rc==System.Guid.Empty: raise ValueError("unable to add text dot to document")
    scriptcontext.doc.Views.Redraw()
    return rc


def Area(object_id):
    """Compute the area of a closed curve, hatch, surface, polysurface, or mesh
    Parameters:
      object_id = the object's identifier
    Returns:
      area if successful
      None on error
    Example:
      import rhinoscriptsyntax as  rs
      a = rs.Area('a9e34aa8-226c-4e17-9e11-b74bf2cf581b')
    See Also:
      IsPoint
      PointCoordinates
    """
    rhobj = rhutil.coercerhinoobject(object_id, True, True)
    mp = Rhino.Geometry.AreaMassProperties.Compute(rhobj.Geometry)
    if mp is None: raise Exception("unable to compute area mass properties")
    return mp.Area


def BoundingBox(objects, view_or_plane=None, in_world_coords=True):
    """Returns either world axis-aligned or a construction plane axis-aligned
    bounding box of an object or of several objects
    Parameters:
      objects = The identifiers of the objects
      view_or_plane[opt] = Title or id of the view that contains the
          construction plane to which the bounding box should be aligned -or-
          user defined plane. If omitted, a world axis-aligned bounding box
          will be calculated
      in_world_coords[opt] = return the bounding box as world coordinates or
          construction plane coordinates. Note, this option does not apply to
          world axis-aligned bounding boxes.
    Returns:
      Eight 3D points that define the bounding box. Points returned in counter-
      clockwise order starting with the bottom rectangle of the box.
      None on error
    Example:
      import rhinoscriptsyntax as rs
      object = rs.GetObject("Select object")
      if object:
      box = rs.BoundingBox(object)
      if box:
      for i, point in enumerate(box):
      rs.AddTextDot( i, point )
    See Also:
      
    """
    def __objectbbox(object, xform):
        geom = rhutil.coercegeometry(object, False)
        if not geom:
            pt = rhutil.coerce3dpoint(object, True)
            return Rhino.Geometry.BoundingBox(pt,pt)
        if xform: return geom.GetBoundingBox(xform)
        return geom.GetBoundingBox(True)

    xform = None
    plane = rhutil.coerceplane(view_or_plane)
    if plane is None and view_or_plane:
        view = view_or_plane
        modelviews = scriptcontext.doc.Views.GetStandardRhinoViews()
        for item in modelviews:
            viewport = item.MainViewport
            if type(view) is str and viewport.Name==view:
                plane = viewport.ConstructionPlane()
                break
            elif type(view) is System.Guid and viewport.Id==view:
                plane = viewport.ConstructionPlane()
                break
        if plane is None: return scriptcontext.errorhandler()
    if plane:
        xform = Rhino.Geometry.Transform.ChangeBasis(Rhino.Geometry.Plane.WorldXY, plane)
    bbox = Rhino.Geometry.BoundingBox.Empty
    if type(objects) is list or type(objects) is tuple:
        for object in objects:
            objectbbox = __objectbbox(object, xform)
            bbox = Rhino.Geometry.BoundingBox.Union(bbox,objectbbox)
    else:
        objectbbox = __objectbbox(objects, xform)
        bbox = Rhino.Geometry.BoundingBox.Union(bbox,objectbbox)
    if not bbox.IsValid: return scriptcontext.errorhandler()

    corners = list(bbox.GetCorners())
    if in_world_coords and plane is not None:
        plane_to_world = Rhino.Geometry.Transform.ChangeBasis(plane, Rhino.Geometry.Plane.WorldXY)
        for pt in corners: pt.Transform(plane_to_world)
    return corners


def ExplodeText(text_id, delete=False):
    """Creates outline curves for a given text entity
    Parameters:
      text_id: identifier of Text object to explode
      delete[opt]: delete the text object after the curves have been created
    Returns:
      list of outline curves
    Example:
      import rhinoscriptsyntax as rs
      text = rs.AddText("abcd", rs.WorldXYPlane())
      rs.ExplodeText(text, True)
    See Also:
      IsHatch
      HatchPattern
      HatchRotation
      HatchScale
    """
    rhobj = rhutil.coercerhinoobject(text_id, True, True)
    curves = rhobj.Geometry.Explode()
    attr = rhobj.Attributes
    rc = [scriptcontext.doc.Objects.AddCurve(curve,attr) for curve in curves]
    if delete: scriptcontext.doc.Objects.Delete(rhobj,True)
    scriptcontext.doc.Views.Redraw()
    return rc


def IsClippingPlane(object_id):
    """Verifies that an object is a clipping plane object
    Parameters:
      object_id: the object's identifier
    Returns:
      True if the object with a given id is a clipping plane
    Example:
      import rhinoscriptsyntax as rs
      id = rs.GetObject("Select a clipping plane")
      if rs.IsClippingPlane(id):
      print "The object is a clipping plane."
      else:
      print "The object is not a clipping plane."
    See Also:
      AddClippingPlane
    """
    cp = rhutil.coercegeometry(object_id)
    return isinstance(cp, Rhino.Geometry.ClippingPlaneSurface)


def IsPoint(object_id):
    """Verifies an object is a point object.
    Parameters:
      object_id: the object's identifier
    Returns:
      True if the object with a given id is a point
    Example:
      import rhinoscriptsyntax as rs
      id = rs.GetObject("Select a point")
      if rs.IsPoint(id):
      print "The object is a point."
      else:
      print "The object is not a point."
    See Also:
      AddPoint
      PointCoordinates
    """
    p = rhutil.coercegeometry(object_id)
    return isinstance(p, Rhino.Geometry.Point)


def IsPointCloud(object_id):
    """Verifies an object is a point cloud object.
    Parameters:
      object_id: the object's identifier
    Returns:
      True if the object with a given id is a point cloud
    Example:
      import rhinoscriptsyntax as rs
      id = rs.GetObject("Select a point cloud")
      if rs.IsPointCloud(id):
      print "The object is a point cloud."
      else:
      print "The object is not a point cloud."
    See Also:
      AddPointCloud
      PointCloudCount
      PointCloudPoints
    """
    pc = rhutil.coercegeometry(object_id)
    return isinstance(pc, Rhino.Geometry.PointCloud)


def IsText(object_id):
    """Verifies an object is a text object.
    Parameters:
      object_id: the object's identifier
    Returns:
      True if the object with a given id is a text object
    Example:
      import rhinoscriptsyntax as rs
      id = rs.GetObject("Select a text object")
      if rs.IsText(id):
      print "The object is a text object."
      else:
      print "The object is not a text object."
    See Also:
      AddText
    """
    text = rhutil.coercegeometry(object_id)
    return isinstance(text, Rhino.Geometry.TextEntity)


def IsTextDot(object_id):
    """Verifies an object is a text dot object.
    Parameters:
      object_id: the object's identifier
    Returns:
      True if the object with a given id is a text dot object
    Example:
      import rhinoscriptsyntax as rs
      id = rs.GetObject("Select a text dot object")
      if rs.IsTextDot(id):
      print "The object is a text dot object."
      else:
      print "The object is not a text dot object."
    See Also:
      AddTextDot
    """
    td = rhutil.coercegeometry(object_id)
    return isinstance(td, Rhino.Geometry.TextDot)


def PointCloudCount(object_id):
    """Returns the point count of a point cloud object
    Parameters:
      object_id: the point cloud object's identifier
    Returns:
      number of points if successful
    Example:
      import rhinoscriptsyntax as rs
      id = rs.GetObject("Select point cloud", rs.filter.pointcloud)
      print "Point count:", rs.PointCloudCount(id)
    See Also:
      AddPointCloud
      IsPointCloud
      PointCloudPoints
    """
    pc = rhutil.coercegeometry(object_id, True)
    if isinstance(pc, Rhino.Geometry.PointCloud): return pc.Count


def PointCloudHasHiddenPoints(object_id):
    """Verifies that a point cloud has hidden points
    Parameters:
      object_id: the point cloud object's identifier
    Returns:
      True if cloud has hidden points, otherwise False
    Example:
      import rhinoscriptsyntax as rs
      obj = rs.GetObject("Select a point cloud", rs.filter.pointcloud)
      if rs.PointCloudHasHiddenPoints(obj):
      print "The point cloud has hidden points."
      else:
      print "The point cloud has no hidden points."
    See Also:
      PointCloudHasPointColors
      PointCloudHidePoints
      PointCloudPointColors
    """
    pc = rhutil.coercegeometry(object_id, True)
    if isinstance(pc, Rhino.Geometry.PointCloud): return pc.HiddenPointCount>0


def PointCloudHasPointColors(object_id):
    """Verifies that a point cloud has point colors
    Parameters:
      object_id: the point cloud object's identifier
    Returns:
      True if cloud has point colors, otherwise False
    Example:
      import rhinoscriptsyntax as rs
      obj = rs.GetObject("Select a point cloud", rs.filter.pointcloud)
      if rs.PointCloudHasPointColors(obj):
      print "The point cloud has point colors."
      else:
      print "The point cloud has no point colors."
    See Also:
      PointCloudHasPointColors
      PointCloudHidePoints
      PointCloudPointColors
    """
    pc = rhutil.coercegeometry(object_id, True)
    if isinstance(pc, Rhino.Geometry.PointCloud): return pc.ContainsColors


def PointCloudHidePoints(object_id, hidden=[]):
    """Returns or modifies the hidden points of a point cloud object
    Parameters:
      object_id: the point cloud object's identifier
      hidden: list of hidden values if you want to hide certain points
    Returns:
      List of point cloud hidden states
    Example:
      import rhinoscriptsyntax as rs
      if obj:
      hidden = [True] * rs.PointCloudCount(obj)
      for i in range(len(hidden)):
      hidden[i] = (i%2==0)
      rs.PointCloudHidePoints(obj, hidden)
    See Also:
      PointCloudHasPointColors
      PointCloudPointColors
    """
    rhobj = rhutil.coercerhinoobject(object_id)
    if rhobj: pc = rhobj.Geometry
    else: pc = rhutil.coercegeometry(object_id, True)
    if isinstance(pc, Rhino.Geometry.PointCloud):
        rc = None
        if pc.ContainsHiddenFlags: rc = [item.Hidden for item in pc]
        if hidden is None:
            pc.ClearHiddenFlags()
        elif len(hidden)==pc.Count:
            for i in range(pc.Count): pc[i].Hidden = hidden[i]
        if rhobj:
            rhobj.CommitChanges()
            scriptcontext.doc.Views.Redraw()
        return rc


def PointCloudPointColors(object_id, colors=[]):
    """Returns or modifies the point colors of a point cloud object
    Parameters:
      object_id: the point cloud object's identifier
      colors: list of color values if you want to adjust colors
    Returns:
      List of point cloud colors
    Example:
      import rhinoscriptsyntax as rs
      import random
      
      def RandomColor():
      red = random.randint(0,255)
      green = random.randint(0,255)
      blue = random.randint(0,255)
      return rs.coercecolor((red,green,blue))
      
      obj = rs.GetObject("Select point cloud", rs.filter.pointcloud)
      if obj:
      colors = [RandomColor() for i in range(rs.PointCloudCount(obj))]
      rs.PointCloudColors(obj, colors)
    See Also:
      PointCloudHasHiddenPoints
      PointCloudHasPointColors
      PointCloudHidePoints
    """
    rhobj = rhutil.coercerhinoobject(object_id)
    if rhobj: pc = rhobj.Geometry
    else: pc = rhutil.coercegeometry(object_id, True)
    if isinstance(pc, Rhino.Geometry.PointCloud):
        rc = None
        if pc.ContainsColors: rc = [item.Color for item in pc]
        if colors is None:
            pc.ClearColors()
        elif len(colors)==pc.Count:
            for i in range(pc.Count): pc[i].Color = rhutil.coercecolor(colors[i])
        if rhobj:
            rhobj.CommitChanges()
            scriptcontext.doc.Views.Redraw()
        return rc


def PointCloudPoints(object_id):
    """Returns the points of a point cloud object
    Parameters:
      object_id: the point cloud object's identifier
    Returns:
      list of points if successful
    Example:
      import rhinoscriptsyntax as rs
      id = rs.GetObject("Select point cloud", rs.filter.pointcloud)
      points = rs.PointCloudPoints(id)
      if points: for point in points: print point
    See Also:
      AddPointCloud
      IsPointCloud
      PointCloudCount
    """
    pc = rhutil.coercegeometry(object_id, True)
    if isinstance(pc, Rhino.Geometry.PointCloud): return pc.GetPoints()


def PointCoordinates(object_id, point=None):
    """Returns or modifies the X, Y, and Z coordinates of a point object
    Parameters:
      object_id = The identifier of a point object
      point[opt] = A new 3D point location.
    Returns:
      If point is not specified, the current 3-D point location
      If point is specified, the previous 3-D point location
    Example:
      import rhinoscriptsyntax as rs
      id = rs.GetObject("Select point", rs.filter.point)
      point = rs.PointCoordinates(id)
    See Also:
      AddPoint
      IsPoint
    """
    point_geometry = rhutil.coercegeometry(object_id, True)
    if isinstance(point_geometry, Rhino.Geometry.Point):
        rc = point_geometry.Location
        if point:
            point = rhutil.coerce3dpoint(point, True)
            id = rhutil.coerceguid(object_id, True)
            scriptcontext.doc.Objects.Replace(id, point)
            scriptcontext.doc.Views.Redraw()
        return rc


def TextDotFont(object_id, fontface=None):
    """Returns or modified the font of a text dot
    Parameters:
      object_id = identifier of a text dot object
      fontface[opt] = new font face name
    Returns:
      If font is not specified, the current text dot font
      If font is specified, the previous text dot font
      None on error
    Example:
      import rhinoscriptsyntax as rs
      obj = rs.GetObject("Select text dot")
    See Also:
      AddTextDot
      IsTextDot
      TextDotHeight
      TextDotPoint
      TextDotText
    """
    textdot = rhutil.coercegeometry(object_id, True)
    if isinstance(textdot, Rhino.Geometry.TextDot):
        rc = textdot.FontFace
        if fontface:
            textdot.FontFace = fontface
            id = rhutil.coerceguid(object_id, True)
            scriptcontext.doc.Objects.Replace(id, textdot)
            scriptcontext.doc.Views.Redraw()
        return rc


def TextDotHeight(object_id, height=None):
    """Returns or modified the font height of a text dot
    Parameters:
      object_id = identifier of a text dot object
      height[opt] = new font height
    Returns:
      If height is not specified, the current text dot height
      If height is specified, the previous text dot height
      None on error
    Example:
      import rhinoscriptsyntax as rs
      obj = rs.GetObject("Select text dot")
      if rs.IsTextDot(obj): rs.TextDotHeight(obj, 10.0)
    See Also:
      AddTextDot
      IsTextDot
      TextDotFont
      TextDotPoint
      TextDotText
    """
    textdot = rhutil.coercegeometry(object_id, True)
    if isinstance(textdot, Rhino.Geometry.TextDot):
        rc = textdot.FontHeight
        if height and height>0:
            textdot.FontHeight = height
            id = rhutil.coerceguid(object_id, True)
            scriptcontext.doc.Objects.Replace(id, textdot)
            scriptcontext.doc.Views.Redraw()
        return rc


def TextDotPoint(object_id, point=None):
    """Returns or modifies the location, or insertion point, on a text dot object
    Parameters:
      object_id = identifier of a text dot object
      point[opt] = A new 3D point location.
    Returns:
      If point is not specified, the current 3-D text dot location
      If point is specified, the previous 3-D text dot location
      None if not successful, or on error
    Example:
      import rhinoscriptsyntax as rs
      id = rs.GetObject("Select text dot")
      if rs.IsTextDot(id):
      point = rs.TestDotPoint(id)
      rs.AddPoint( point )
      rs.TextDotPoint(id, [0,0,0])
    See Also:
      AddTextDot
      IsTextDot
      TextDotText
    """
    textdot = rhutil.coercegeometry(object_id, True)
    if isinstance(textdot, Rhino.Geometry.TextDot):
        rc = textdot.Point
        if point:
            textdot.Point = rhutil.coerce3dpoint(point, True)
            id = rhutil.coerceguid(object_id, True)
            scriptcontext.doc.Objects.Replace(id, textdot)
            scriptcontext.doc.Views.Redraw()
        return rc


def TextDotText(object_id, text=None):
    """Returns or modifies the text on a text dot object
    Parameters:
      object_id =tThe identifier of a text dot object
      text [opt] = a new string for the dot
    Returns:
      If text is not specified, the current text dot text
      If text is specified, the previous text dot text
      None if not successful, or on error
    Example:
      import rhinoscriptsyntax as rs
      id = rs.GetObject("Select text dot")
      if rs.IsTextDot(id):
      rs.TextDotText( id, "Rhino")
    See Also:
      AddTextDot
      IsTextDot
      TextDotPoint
    """
    textdot = rhutil.coercegeometry(object_id, True)
    if isinstance(textdot, Rhino.Geometry.TextDot):
        rc = textdot.Text
        if text is not None:
            if not isinstance(text, str): text = str(text)
            textdot.Text = text
            id = rhutil.coerceguid(object_id, True)
            scriptcontext.doc.Objects.Replace(id, textdot)
            scriptcontext.doc.Views.Redraw()
        return rc


def TextObjectFont(object_id, font=None):
    """Returns of modifies the font used by a text object
    Parameters:
      object_id = the identifier of a text object
      font [opt] = the new font face name
    Returns:
      if a font is not specified, the current font face name
      if a font is specified, the previous font face name
      None if not successful, or on error
    Example:
      import rhinoscriptsyntax as rs
      obj = rs.GetObject("Select text")
      if rs.IsText(obj): rs.TextObjectFont(obj, "Arial")
    See Also:
      AddText
      IsText
      TextObjectHeight
      TextObjectPlane
      TextObjectPoint
      TextObjectStyle
      TextObjectText
    """
    annotation = rhutil.coercegeometry(object_id, True)
    if not isinstance(annotation, Rhino.Geometry.TextEntity):
        return scriptcontext.errorhandler()
    fontdata = scriptcontext.doc.Fonts[annotation.FontIndex]
    if fontdata is None: return scriptcontext.errorhandler()
    rc = fontdata.FaceName
    if font:
        index = scriptcontext.doc.Fonts.FindOrCreate( font, fontdata.Bold, fontdata.Italic )
        annotation.FontIndex = index
        id = rhutil.coerceguid(object_id, True)
        scriptcontext.doc.Objects.Replace(id, annotation)
        scriptcontext.doc.Views.Redraw()
    return rc


def TextObjectHeight(object_id, height=None):
    """Returns or modifies the height of a text object
    Parameters:
      object_id = the identifier of a text object
      height[opt] = the new text height.
    Returns:
      if height is not specified, the current text height
      if height is specified, the previous text height
      None if not successful, or on error
    Example:
      import rhinoscriptsyntax as rs
      obj = rs.GetObject("Select text")
      if rs.IsText(obj):
      rs.TextObjectHeight( obj, 1.0 )
    See Also:
      AddText
      IsText
      TextObjectFont
      TextObjectPlane
      TextObjectPoint
      TextObjectStyle
      TextObjectText
    """
    annotation = rhutil.coercegeometry(object_id, True)
    if not isinstance(annotation, Rhino.Geometry.TextEntity):
        return scriptcontext.errorhandler()
    rc = annotation.TextHeight
    if height:
        annotation.TextHeight = height
        id = rhutil.coerceguid(object_id, True)
        scriptcontext.doc.Objects.Replace(id, annotation)
        scriptcontext.doc.Views.Redraw()
    return rc


def TextObjectPlane(object_id, plane=None):
    """Returns or modifies the plane used by a text object
    Parameters:
      object_id = the identifier of a text object
      plane[opt] = the new text object plane
    Returns:
      if a plane is not specified, the current plane if successful
      if a plane is specified, the previous plane if successful
      None if not successful, or on Error
    Example:
      import rhinoscriptsyntax as rs
      obj = rs.GetObject("Select text")
      if rs.IsText(obj):
      plane = rs.ViewCPlane("Top")
      rs.TextObjectPlane( obj, plane )
    See Also:
      AddText
      IsText
      TextObjectFont
      TextObjectHeight
      TextObjectPoint
      TextObjectStyle
      TextObjectText
    """
    annotation = rhutil.coercegeometry(object_id, True)
    if not isinstance(annotation, Rhino.Geometry.TextEntity):
        return scriptcontext.errorhandler()
    rc = annotation.Plane
    if plane:
        annotation.Plane = rhutil.coerceplane(plane, True)
        id = rhutil.coerceguid(object_id, True)
        scriptcontext.doc.Objects.Replace(id, annotation)
        scriptcontext.doc.Views.Redraw()
    return rc


def TextObjectPoint(object_id, point=None):
    """Returns or modifies the location of a text object
    Parameters:
      object_id = the identifier of a text object
      point[opt] = the new text object location
    Returns:
      if point is not specified, the 3D point identifying the current location
      if point is specified, the 3D point identifying the previous location
      None if not successful, or on Error
    Example:
      import rhinoscriptsyntax as rs
      obj = rs.GetObject("Select text")
      if rs.IsText(obj):
      rs.TextObjectPoint( obj, [0,0,0] )
    See Also:
      AddText
      IsText
      TextObjectFont
      TextObjectHeight
      TextObjectPlane
      TextObjectStyle
      TextObjectText
    """
    text = rhutil.coercegeometry(object_id, True)
    if not isinstance(text, Rhino.Geometry.TextEntity):
        return scriptcontext.errorhandler()
    plane = text.Plane
    rc = plane.Origin
    if point:
        plane.Origin = rhutil.coerce3dpoint(point, True)
        text.Plane = plane
        id = rhutil.coerceguid(object_id, True)
        scriptcontext.doc.Objects.Replace(id, text)
        scriptcontext.doc.Views.Redraw()
    return rc


def TextObjectStyle(object_id, style=None):
    """Returns or modifies the font style of a text object
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
    Example:
      import rhinoscriptsyntax as rs
      obj = rs.GetObject("Select text")
      if rs.IsText(obj):
      rs.TextObjectStyle( obj, 3 )
    See Also:
      AddText
      IsText
      TextObjectFont
      TextObjectHeight
      TextObjectPlane
      TextObjectPoint
      TextObjectText
    """
    annotation = rhutil.coercegeometry(object_id, True)
    if not isinstance(annotation, Rhino.Geometry.TextEntity):
        return scriptcontext.errorhandler()
    fontdata = scriptcontext.doc.Fonts[annotation.FontIndex]
    if fontdata is None: return scriptcontext.errorhandler()
    rc = 0
    if fontdata.Bold: rc += 1
    if fontdata.Italic: rc += 2
    if style is not None and style!=rc:
        index = scriptcontext.doc.Fonts.FindOrCreate( fontdata.FaceName, (style&1)==1, (style&2)==2 )
        annotation.FontIndex = index
        id = rhutil.coerceguid(object_id, True)
        scriptcontext.doc.Objects.Replace(id, annotation)
        scriptcontext.doc.Views.Redraw()
    return rc


def TextObjectText(object_id, text=None):
    """Returns or modifies the text string of a text object.
    Parameters:
      object_id = the identifier of a text object
      text [opt] = a new text string
    Returns:
      if text is not specified, the current string value if successful
      if text is specified, the previous string value if successful
      None if not successful, or on error
    Example:
      import rhinoscriptsyntax as rs
      obj = rs.GetObject("Select text")
      if rs.IsText(obj): rs.TextObjectText(obj, "Rhino")
    See Also:
      AddText
      IsText
      TextObjectFont
      TextObjectHeight
      TextObjectPlane
      TextObjectPoint
      TextObjectStyle
    """
    annotation = rhutil.coercegeometry(object_id, True)
    if not isinstance(annotation, Rhino.Geometry.TextEntity):
        return scriptcontext.errorhandler()
    rc = annotation.Text
    if text:
        if not isinstance(text, str): text = str(text)
        annotation.Text = text
        id = rhutil.coerceguid(object_id, True)
        scriptcontext.doc.Objects.Replace(id, annotation)
        scriptcontext.doc.Views.Redraw()
    return rc