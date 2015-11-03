import scriptcontext
import Rhino
import utility as rhutil
import application as rhapp
from layer import __getlayer
from view import __viewhelper


class filter:
    allobjects = 0
    point = 1
    pointcloud = 2
    curve = 4
    surface = 8
    polysurface = 16
    mesh = 32
    light = 256
    annotation = 512
    instance = 4096
    textdot = 8192
    grip = 16384
    detail = 32768
    hatch = 65536
    morph = 13072
    cage = 134217728
    phantom = 268435456
    clippingplane = 536870912
    extrusion = 1073741824


def AllObjects(select=False, include_lights=False, include_grips=False, include_references=False):
    """Returns identifiers of all objects in the document.
    Parameters:
      select[opt] = Select the objects
      include_lights[opt] = Include light objects
      include_grips[opt] = Include grips objects
    Returns:
      List of Guids identifying the objects
    Example:
      import rhinoscriptsyntax as rs
      objs = rs.AllObjects()
      for obj in objs: print "Object identifier: ", obj
    See Also:
      HiddenObjects
      LockedObjects
      NormalObjects
    """
    it = Rhino.DocObjects.ObjectEnumeratorSettings()
    it.IncludeLights = include_lights
    it.IncludeGrips = include_grips
    it.NormalObjects = True
    it.LockedObjects = True
    it.HiddenObjects = True
    it.ReferenceObjects = include_references
    e = scriptcontext.doc.Objects.GetObjectList(it)
    object_ids = []
    for object in e:
        if select: object.Select(True)
        object_ids.append(object.Id)
    if object_ids and select: scriptcontext.doc.Views.Redraw()
    return object_ids


def FirstObject(select=False, include_lights=False, include_grips=False):
    """Returns identifier of the first object in the document. The first
    object is the last object created by the user.
    Parameters:
      select [opt] = Select the object.  If omitted (False), the object is not selected.
      include_lights [opt] = Include light objects.  If omitted (False), light objects are not returned.
      include_gripts [opt] = Include grips objects.  If omitted (False), grips objects are not returned.
    Returns:
      The identifier of the object if successful.
    Example:
      import rhinoscriptsyntax as rs
      rs.AddLine( (0,0,0), (5,5,0) )
      rs.AddLine( (0,0,0), (5,0,0) )
      rs.AddLine( (0,0,0), (0,5,0) )
      objectId = rs.FirstObject()
      print "Object identifier: ", objectId
      rs.SelectObject(objectId)
    See Also:
      LastObject
      NextObject
    """
    it = Rhino.DocObjects.ObjectEnumeratorSettings()
    it.IncludeLights = include_lights
    it.IncludeGrips = include_grips
    e = scriptcontext.doc.Objects.GetObjectList(it).GetEnumerator()
    if not e.MoveNext(): return None
    object = e.Current
    if object:
        if select: object.Select(True)
        return object.Id


def __FilterHelper(filter):
    geometry_filter = Rhino.DocObjects.ObjectType.None
    if filter & 1:
        geometry_filter |= Rhino.DocObjects.ObjectType.Point
    if filter & 16384:
        geometry_filter |= Rhino.DocObjects.ObjectType.Grip
    if filter & 2:
        geometry_filter |= Rhino.DocObjects.ObjectType.PointSet
    if filter & 4:
        geometry_filter |= Rhino.DocObjects.ObjectType.Curve
    if filter & 8:
        geometry_filter |= Rhino.DocObjects.ObjectType.Surface
    if filter & 16:
        geometry_filter |= Rhino.DocObjects.ObjectType.Brep
    if filter & 32:
        geometry_filter |= Rhino.DocObjects.ObjectType.Mesh
    if filter & 512:
        geometry_filter |= Rhino.DocObjects.ObjectType.Annotation
    if filter & 256:
        geometry_filter |= Rhino.DocObjects.ObjectType.Light
    if filter & 4096:
        geometry_filter |= Rhino.DocObjects.ObjectType.InstanceReference
    if filter & 134217728:
        geometry_filter |= Rhino.DocObjects.ObjectType.Cage
    if filter & 65536:
        geometry_filter |= Rhino.DocObjects.ObjectType.Hatch
    if filter & 131072:
        geometry_filter |= Rhino.DocObjects.ObjectType.MorphControl
    if filter & 2097152:
        geometry_filter |= Rhino.DocObjects.ObjectType.PolysrfFilter
    if filter & 268435456:
        geometry_filter |= Rhino.DocObjects.ObjectType.Phantom
    if filter & 8192:
        geometry_filter |= Rhino.DocObjects.ObjectType.TextDot
    if filter & 32768:
        geometry_filter |= Rhino.DocObjects.ObjectType.Detail
    if filter & 536870912:
        geometry_filter |= Rhino.DocObjects.ObjectType.ClipPlane
    if filter & 1073741824:
        geometry_filter |= Rhino.DocObjects.ObjectType.Extrusion
    return geometry_filter


def GetCurveObject(message=None, preselect=False, select=False):
    """Prompts user to pick or select a single curve object
    Parameters:
      message[opt] = a prompt or message.
      preselect[opt] = Allow for the selection of pre-selected objects.
      select[opt] = Select the picked objects. If False, objects that
        are picked are not selected.
    Returns:
      Tuple containing the following information
        element 0 = identifier of the curve object
        element 1 = True if the curve was preselected, otherwise False
        element 2 = selection method (see help)
        element 3 = selection point
        element 4 = the curve parameter of the selection point
        element 5 = name of the view selection was made
      None if no object picked
    Example:
      import rhinoscriptsyntax as rs
      select_result = rs.GetCurveObject("Select curve")
      if select_result:
      print "Curve identifier: ", select_result[0]
    See Also:
      GetObject
      GetObjects
      GetSurfaceObject
    """
    if not preselect:
        scriptcontext.doc.Objects.UnselectAll()
        scriptcontext.doc.Views.Redraw()
    go = Rhino.Input.Custom.GetObject()
    if message: go.SetCommandPrompt(message)
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Curve
    go.SubObjectSelect = False
    go.GroupSelect = False
    go.AcceptNothing(True)
    if go.Get()!=Rhino.Input.GetResult.Object: return None
 
    objref = go.Object(0)
    id = objref.ObjectId
    presel = go.ObjectsWerePreselected
    selmethod = 0
    sm = objref.SelectionMethod()
    if Rhino.DocObjects.SelectionMethod.MousePick==sm: selmethod = 1
    elif Rhino.DocObjects.SelectionMethod.WindowBox==sm: selmethod = 2
    elif Rhino.DocObjects.SelectionMethod.CrossingBox==sm: selmethod = 3
    point = objref.SelectionPoint()
    crv, curve_parameter = objref.CurveParameter()
    viewname = go.View().ActiveViewport.Name
    obj = go.Object(0).Object()
    go.Dispose()
    if not select:
        scriptcontext.doc.Objects.UnselectAll()
        scriptcontext.doc.Views.Redraw()
    obj.Select(select)
    return id, presel, selmethod, point, curve_parameter, viewname


def GetObject(message=None, filter=0, preselect=False, select=False, custom_filter=None, subobjects=False):
    """Prompts user to pick, or select, a single object.
    Parameters:
      message[opt] = a prompt or message.
      filter[opt] = The type(s) of geometry (points, curves, surfaces, meshes,...)
          that can be selected. Object types can be added together to filter
          several different kinds of geometry. use the filter class to get values
      preselect[opt] =  Allow for the selection of pre-selected objects.
      select[opt] = Select the picked objects.  If False, the objects that are
          picked are not selected.
      subobjects[opt] = If True, subobjects can be selected. When this is the
          case, an ObjRef is returned instead of a Guid to allow for tracking
          of the subobject when passed into other functions
    Returns:
      Identifier of the picked object
      None if user did not pick an object
    Example:
      import rhinoscriptsyntax as rs
      objectId = rs.GetObject("Pick any object")
      if objectId:
      
      objectId = rs.GetObject("Pick a curve or surface", rs.filter.curve | rs.filter.surface)
      if objectId:
    See Also:
      GetCurveObject
      GetObjectEx
      GetObjects
      GetSurfaceObject
    """
    if not preselect:
        scriptcontext.doc.Objects.UnselectAll()
        scriptcontext.doc.Views.Redraw()
    
    class CustomGetObject(Rhino.Input.Custom.GetObject):
        def __init__(self, filter_function):
            self.m_filter_function = filter_function
        def CustomGeometryFilter( self, rhino_object, geometry, component_index ):
            rc = True
            if self.m_filter_function is not None:
                try:
                    rc = self.m_filter_function(rhino_object, geometry, component_index)
                except:
                    rc = True
            return rc
    go = CustomGetObject(custom_filter)
    if message: go.SetCommandPrompt(message)
    geometry_filter = __FilterHelper(filter)
    if filter>0: go.GeometryFilter = geometry_filter
    go.SubObjectSelect = subobjects
    go.GroupSelect = False
    go.AcceptNothing(True)      
    if go.Get()!=Rhino.Input.GetResult.Object: return None
    objref = go.Object(0)
    obj = objref.Object()
    go.Dispose()
    if not select:
        scriptcontext.doc.Objects.UnselectAll()
        scriptcontext.doc.Views.Redraw()
    if subobjects: return objref
    obj.Select(select)
    return obj.Id


class __CustomGetObjectEx(Rhino.Input.Custom.GetObject):
    def __init__(self, allowable_geometry):
        self.m_allowable = allowable_geometry
    def CustomGeometryFilter(self, rhino_object, geometry, component_index):
        for id in self.m_allowable:
            if id==rhino_object.Id: return True
        return False

def GetObjectEx(message=None, filter=0, preselect=False, select=False, objects=None):
    """Prompts user to pick, or select a single object
    Parameters:
      message[opt] = a prompt or message.
      filter[opt] = The type(s) of geometry (points, curves, surfaces, meshes,...)
          that can be selected. Object types can be added together to filter
          several different kinds of geometry. use the filter class to get values
      preselect[opt] =  Allow for the selection of pre-selected objects.
      select[opt] = Select the picked objects.  If False, the objects that are
          picked are not selected.
      objects[opt] = list of object identifiers specifying objects that are
          allowed to be selected
    Returns:
      Tuple of information containing the following information
        element 0 = identifier of the object
        element 1 = True if the object was preselected, otherwise False
        element 2 = selection method (see help)
        element 3 = selection point
        element 4 = name of the view selection was made
      None if no object selected
    Example:
      import rhinoscriptsyntax as rs
      obj = rs.GetObjectEx("Select object", 0, True)
      if obj:
      print "Object id = ", obj[0]
      print "Object was preselected = ", obj[1]
      if obj[2]==0:
      elif obj[2]==1:
      print "Selection method = 1 (mouse)"
      print "Pick point = ", obj[3]
      elif obj[2]==2:
      print "Selection method = 2 (window)"
      elif obj[2]==3:
      print "Selection method = 3 (crossing)"
      print "Active view = ", obj[4]
    See Also:
      GetCurveObject
      GetObject
      GetObjects
      GetObjectsEx
      GetSurfaceObject
    """
    if not preselect:
        scriptcontext.doc.Objects.UnselectAll()
        scriptcontext.doc.Views.Redraw()
    go = None
    if objects:
        ids = [rhutil.coerceguid(id, True) for id in objects]
        if ids: go = __CustomGetObjectEx(ids)
    if not go: go = Rhino.Input.Custom.GetObject()
    if message: go.SetCommandPrompt(message)
    geometry_filter = __FilterHelper(filter)
    if filter>0: go.GeometryFilter = geometry_filter
    go.SubObjectSelect = False
    go.GroupSelect = False
    go.AcceptNothing(True)      
    if go.Get()!=Rhino.Input.GetResult.Object: return None
    objref = go.Object(0)
    id = objref.ObjectId
    presel = go.ObjectsWerePreselected
    selmethod = 0
    sm = objref.SelectionMethod()
    if Rhino.DocObjects.SelectionMethod.MousePick==sm: selmethod = 1
    elif Rhino.DocObjects.SelectionMethod.WindowBox==sm: selmethod = 2
    elif Rhino.DocObjects.SelectionMethod.CrossingBox==sm: selmethod = 3
    point = objref.SelectionPoint()
    viewname = go.View().ActiveViewport.Name
    obj = go.Object(0).Object()
    go.Dispose()
    if not select:
        scriptcontext.doc.Objects.UnselectAll()
        scriptcontext.doc.Views.Redraw()
    obj.Select(select)
    return id, presel, selmethod, point, viewname


def GetObjects(message=None, filter=0, group=True, preselect=False, select=False, objects=None, minimum_count=1, maximum_count=0, custom_filter=None):
    """Prompts user to pick or select one or more objects.
    Parameters:
      message[opt] = a prompt or message.
      filter[opt] = The type(s) of geometry (points, curves, surfaces, meshes,...)
          that can be selected. Object types can be added together to filter
          several different kinds of geometry. use the filter class to get values
      group[opt] = Honor object grouping.  If omitted and the user picks a group,
          the entire group will be picked (True). Note, if filter is set to a
          value other than 0 (All objects), then group selection will be disabled.
      preselect[opt] =  Allow for the selection of pre-selected objects.
      select[opt] = Select the picked objects.  If False, the objects that are
          picked are not selected.
      objects[opt] = list of objects that are allowed to be selected
      mimimum_count, maximum_count[out] = limits on number of objects allowed to be selected
    Returns:
      list of Guids identifying the picked objects
    Example:
      import rhinoscriptsyntax as rs
      objectIds = rs.GetObjects("Pick some curves", rs.filter.curve)
      for id in objectIds: print "Object identifier:", id
    See Also:
      GetCurveObject
      GetObject
      GetSurfaceObject
    """
    if not preselect:
        scriptcontext.doc.Objects.UnselectAll()
        scriptcontext.doc.Views.Redraw()

    objects = rhutil.coerceguidlist(objects)
    class CustomGetObject(Rhino.Input.Custom.GetObject):
        def __init__(self, filter_function):
            self.m_filter_function = filter_function
        def CustomGeometryFilter( self, rhino_object, geometry, component_index ):
            if objects and not rhino_object.Id in objects: return False
            rc = True
            if self.m_filter_function is not None:
                try:
                    rc = self.m_filter_function(rhino_object, geometry, component_index)
                except:
                    rc = True
            return rc
    go = CustomGetObject(custom_filter)
    go.SetCommandPrompt(message or "Select objects")
    geometry_filter = __FilterHelper(filter)
    if filter>0: go.GeometryFilter = geometry_filter
    go.SubObjectSelect = False
    go.GroupSelect = group
    go.AcceptNothing(True)
    if go.GetMultiple(minimum_count,maximum_count)!=Rhino.Input.GetResult.Object: return None
    if not select:
        scriptcontext.doc.Objects.UnselectAll()
        scriptcontext.doc.Views.Redraw()
    rc = []
    count = go.ObjectCount
    for i in xrange(count):
        objref = go.Object(i)
        rc.append(objref.ObjectId)
        obj = objref.Object()
        if select and obj is not None: obj.Select(select)
    go.Dispose()
    return rc


def GetObjectsEx(message=None, filter=0, group=True, preselect=False, select=False, objects=None):
    """Prompts user to pick, or select one or more objects
    Parameters:
      message[opt] = a prompt or message.
      filter[opt] = The type(s) of geometry (points, curves, surfaces, meshes,...)
          that can be selected. Object types can be added together to filter
          several different kinds of geometry. use the filter class to get values
      group[opt] = Honor object grouping.  If omitted and the user picks a group,
          the entire group will be picked (True). Note, if filter is set to a
          value other than 0 (All objects), then group selection will be disabled.
      preselect[opt] =  Allow for the selection of pre-selected objects.
      select[opt] = Select the picked objects. If False, the objects that are
          picked are not selected.
      objects[opt] = list of object identifiers specifying objects that are
          allowed to be selected
    Returns:
      A list of tuples containing the following information
        element 0 = identifier of the object
        element 1 = True if the object was preselected, otherwise False
        element 2 = selection method (see help)
        element 3 = selection point
        element 4 = name of the view selection was made
    Example:
      import rhinoscriptsyntax as rs
      objects = rs.GetObjectsEx("Select objects", 0, True)
      for obj in objects:
      print "Object id = ", obj[0]
      print "Object was preselected = ", obj[1]
      if obj[2]==0:
      print "Selection method = 0 (non-mouse)"
      elif obj[2]==1:
      print "Selection method = 1 (mouse)"
      print "Pick point = ", obj[3]
      elif obj[2]==2:
      print "Selection method = 2 (window)"
      elif obj[2]==3:
      print "Selection method = 3 (crossing)"
      print "Active view = ", obj[4]
    See Also:
      GetCurveObject
      GetObject
      GetObjectEx
      GetObjects
      GetSurfaceObject
    """
    if not preselect:
        scriptcontext.doc.Objects.UnselectAll()
        scriptcontext.doc.Views.Redraw()
    go = None
    if objects:
        ids = [rhutil.coerceguid(id) for id in objects]
        if ids: go = __CustomGetObjectEx(ids)
    if not go: go = Rhino.Input.Custom.GetObject()
    go.SetCommandPrompt(message or "Select objects")
    geometry_filter = __FilterHelper(filter)
    if filter>0: go.GeometryFilter = geometry_filter
    go.SubObjectSelect = False
    go.GroupSelect = False
    go.AcceptNothing(True)      
    if go.GetMultiple(1,0)!=Rhino.Input.GetResult.Object: return []
    if not select:
        scriptcontext.doc.Objects.UnselectAll()
        scriptcontext.doc.Views.Redraw()
    rc = []
    count = go.ObjectCount
    for i in xrange(count):
        objref = go.Object(i)
        id = objref.ObjectId
        presel = go.ObjectsWerePreselected
        selmethod = 0
        sm = objref.SelectionMethod()
        if Rhino.DocObjects.SelectionMethod.MousePick==sm: selmethod = 1
        elif Rhino.DocObjects.SelectionMethod.WindowBox==sm: selmethod = 2
        elif Rhino.DocObjects.SelectionMethod.CrossingBox==sm: selmethod = 3
        point = objref.SelectionPoint()
        viewname = go.View().ActiveViewport.Name
        rc.append( (id, presel, selmethod, point, viewname) )
        obj = objref.Object()
        if select and obj is not None: obj.Select(select)
    go.Dispose()
    return rc


def GetPointCoordinates(message="select points", preselect=False):
    """Prompts the user to select one or more point objects.
    Parameters:
      message [opt] = a prompt message.
      preselect [opt] = Allow for the selection of pre-selected objects.  If omitted (False), pre-selected objects are not accepted.
    Returns:
      list of 3d coordinates on success
    Example:
      import rhinoscriptsyntax as rs
      points = rs.GetPointCoordinates()
      for point in points: print point
    See Also:
      GetObject
      GetObjects
      GetPoint
      GetPoints
      PointCoordinates
    """
    ids = GetObjects(message, filter.point, preselect=preselect)
    rc = []
    for id in ids:
        rhobj = scriptcontext.doc.Objects.Find(id)
        rc.append(rhobj.Geometry.Location)
    return rc


def GetSurfaceObject(message="select surface", preselect=False, select=False):
    """Prompts the user to select a single surface
    Parameters:
      message[opt] = prompt displayed
      preselect[opt] = allow for preselected objects
      select[opt] = select the picked object
    Returns:
      tuple of information on success
        element 0 = identifier of the surface
        element 1 = True if the surface was preselected, otherwise False
        element 2 = selection method ( see help )
        element 3 = selection point
        element 4 = u,v surface parameter of the selection point
        element 5 = name of the view in which the selection was made
      None on error
    Example:
      import rhinoscriptsyntax as rs
      select = rs.GetSurfaceObject("Select surface")
      if select:
      print "Surface identifier: ", select[0]
    See Also:
      GetCurveObject
      GetObject
      GetObjects
    """
    if not preselect:
        scriptcontext.doc.Objects.UnselectAll()
        scriptcontext.doc.Views.Redraw()
    go = Rhino.Input.Custom.GetObject()
    go.SetCommandPrompt(message)
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Surface
    go.SubObjectSelect = False
    go.GroupSelect = False
    go.AcceptNothing(True)
    if go.Get()!=Rhino.Input.GetResult.Object:
        return scriptcontext.errorhandler()
    objref = go.Object(0)
    rhobj = objref.Object()
    rhobj.Select(select)
    scriptcontext.doc.Views.Redraw()

    id = rhobj.Id
    prepicked = go.ObjectsWerePreselected
    selmethod = objref.SelectionMethod()
    point = objref.SelectionPoint()
    surf, u, v = objref.SurfaceParameter()
    uv = (u,v)
    if not point.IsValid:
        point = None
        uv = None
    view = go.View()
    name = view.ActiveViewport.Name
    go.Dispose()
    return id, prepicked, selmethod, point, uv, name


def LockedObjects(include_lights=False, include_grips=False, include_references=False):
    """Returns identifiers of all locked objects in the document. Locked objects
    cannot be snapped to, and cannot be selected
    Parameters:
      include_lights[opt] = include light objects
      include_grips[opt] = include grip objects
    Returns:
      A list of Guids identifying the objects if successful.
    Example:
      import rhinoscriptsyntax as  rs
      objs = rs.LockedObjects()
      for obj in objs: print "Object  identifier:", obj
    See Also:
      AllObjects
      HiddenObjects
      NormalObjects
    """
    settings = Rhino.DocObjects.ObjectEnumeratorSettings()
    settings.ActiveObjects = True
    settings.NormalObjects = True
    settings.LockedObjects = True
    settings.HiddenObjects = True
    settings.IncludeLights = include_lights
    settings.IncludeGrips = include_grips
    settings.ReferenceObjects = include_references
    return [i.Id for i in scriptcontext.doc.Objects.GetObjectList(settings)
        if i.IsLocked or (scriptcontext.doc.Layers[i.Attributes.LayerIndex]).IsLocked]

def HiddenObjects(include_lights=False, include_grips=False, include_references=False):
    """Returns identifiers of all hidden objects in the document. Hidden objects
    are not visible, cannot be snapped to, and cannot be selected
    Parameters:
      include_lights[opt] = include light objects
      include_grips[opt] = include grip objects
    Returns:
      A list of Guids identifying the objects if successful.
    Example:
      import rhinoscriptsyntax as rs
      hidden = rs.HiddenObjects()
      for obj in hidden: print "Object identifier", obj
    See Also:
      AllObjects
      LockedObjects
      NormalObjects
    """
    settings = Rhino.DocObjects.ObjectEnumeratorSettings()
    settings.ActiveObjects = True
    settings.NormalObjects = True
    settings.LockedObjects = True
    settings.HiddenObjects = True
    settings.IncludeLights = include_lights
    settings.IncludeGrips = include_grips
    settings.ReferenceObjects = include_references
    return [i.Id for i in scriptcontext.doc.Objects.GetObjectList(settings)
        if i.IsHidden or not (scriptcontext.doc.Layers[i.Attributes.LayerIndex]).IsVisible]


def InvertSelectedObjects(include_lights=False, include_grips=False, include_references=False):
    """Inverts the current object selection. The identifiers of the newly
    selected objects are returned
    Parameters:
      include_lights [opt] = Include light objects.  If omitted (False), light objects are not returned.
      include_gripts [opt] = Include grips objects.  If omitted (False), grips objects are not returned.
      include_references [opt] = Include reference objects.  If omitted (False), reference objects are not returned.
    Returns:
      A list of Guids identifying the newly selected objects if successful.
    Example:
      import rhinoscriptsyntax as rs
      rs.GetObjects("Select some objects", select=True)
      objs = rs.InvertSelectedObjects()
      for id in objs: print "Object identifier:", id
    See Also:
      SelectedObjects
      UnselectAllObjects
    """
    settings = Rhino.DocObjects.ObjectEnumeratorSettings()
    settings.IncludeLights = include_lights
    settings.IncludeGrips = include_grips
    settings.IncludePhantoms = True
    settings.ReferenceObjects = include_references
    rhobjs = scriptcontext.doc.Objects.GetObjectList(settings)
    rc = []
    for obj in rhobjs:
        if not obj.IsSelected(False) and obj.IsSelectable():
            rc.append(obj.Id)
            obj.Select(True)
        else:
            obj.Select(False)
    scriptcontext.doc.Views.Redraw()
    return rc


def LastCreatedObjects(select=False):
    """Returns identifiers of the objects that were most recently created or changed
    by scripting a Rhino command using the Command function. It is important to
    call this function immediately after calling the Command function as only the
    most recently created or changed object identifiers will be returned
    Parameters:
      select [opt] = Select the object.  If omitted (False), the object is not selected.
    Returns:
      A list of Guids identifying the most recently created or changed objects if successful.
    Example:
      import rhinoscriptsyntax as rs
      rs.Command( "_-Circle 0,0,0 10" )
      rs.Command( "_-Circle 10,0,0 10" )
      rs.Command( "_-Circle 20,0,0 10" )
      objs = rs.LastCreatedObjects()
      if objs:
      # Only the last circle will be selected
      rs.SelectObjects( objs )
    See Also:
      Command
    """
    serial_numbers = rhapp.__command_serial_numbers
    if serial_numbers is None: return scriptcontext.errorhandler()
    serial_number = serial_numbers[0]
    end = serial_numbers[1]
    rc = []
    while serial_number<end:
        obj = scriptcontext.doc.Objects.Find(serial_number)
        if obj and not obj.IsDeleted:
            rc.append(obj.Id)
            if select: obj.Select(True)
        serial_number += 1
    if select==True and rc: scriptcontext.doc.Views.Redraw()
    return rc


def LastObject(select=False, include_lights=False, include_grips=False):
    """Returns the identifier of the last object in the document. The last object
    in the document is the first object created by the user
    Parameters:
      select[opt] = select the object
      include_lights[opt] = include lights in the potential set
      include_grips[opt] = include grips in the potential set
    Returns:
      identifier of the object on success
    Example:
      import rhinoscriptsyntax as rs
      rs.AddLine((0,0,0), (5,5,0))
      rs.AddCircle((0,0,0), 5)
      print "Object identifier: ", rs.LastObject()
    See Also:
      FirstObject
      NextObject
    """
    settings = Rhino.DocObjects.ObjectEnumeratorSettings()
    settings.IncludeLights = include_lights
    settings.IncludeGrips = include_grips
    settings.DeletedObjects = False
    rhobjs = scriptcontext.doc.Objects.GetObjectList(settings)
    firstobj = None
    for obj in rhobjs: firstobj = obj
    if firstobj is None: return scriptcontext.errorhandler()
    rc = firstobj.Id
    if select:
        firstobj.Select(True)
        scriptcontext.doc.Views.Redraw()
    return rc


def NextObject(object_id, select=False, include_lights=False, include_grips=False):
    """Returns the identifier of the next object in the document
    Parameters:
      object_id = the identifier of the object from which to get the next object
      select[opt] = select the object
      include_lights[opt] = include lights in the potential set
      include_grips[opt] = include grips in the potential set
    Returns:
      identifier of the object on success
    Example:
      import rhinoscriptsyntax as rs
      obj = rs.FirstObject()
      while obj:
      print "Object identifier:", obj
      obj = rs.NextObject(obj)
    See Also:
      FirstObject
      LastObject
    """
    current_obj = rhutil.coercerhinoobject(object_id, True)
    settings = Rhino.DocObjects.ObjectEnumeratorSettings()
    settings.IncludeLights = include_lights
    settings.IncludeGrips = include_grips
    settings.DeletedObjects = False
    rhobjs = scriptcontext.doc.Objects.GetObjectList(settings)
    found = False
    for obj in rhobjs:
        if found and obj: return obj.Id
        if obj.Id == current_obj.Id: found = True


def NormalObjects(include_lights=False, include_grips=False):
    """Returns identifiers of all normal objects in the document. Normal objects
    are visible, can be snapped to, and are independent of selection state
    Parameters:
      include_lights [opt] = Include light objects.  If omitted (False), light objects are not returned.
      include_gripts [opt] = Include grips objects.  If omitted (False), grips objects are not returned.
    Returns:
      A list of Guids identifying the objects if successful.
    Example:
      import rhinoscriptsyntax as rs
      objs = rs.NormalObjects()
      for obj in objs: print "Object identifier:", obj
    See Also:
      AllObjects
      HiddenObjects
      LockedObjects
    """
    iter = Rhino.DocObjects.ObjectEnumeratorSettings()
    iter.NormalObjects = True
    iter.LockedObjects = False
    iter.IncludeLights = include_lights
    iter.IncludeGrips = include_grips
    return [obj.Id for obj in scriptcontext.doc.Objects.GetObjectList(iter)]


def ObjectsByColor(color, select=False, include_lights=False):
    """Returns identifiers of all objects based on color
    Parameters:
      color = color to get objects by
      select[opt] = select the objects
      include_lights[opt] = include lights in the set
    Returns:
      list of identifiers
    Example:
      import rhinoscriptsyntax as rs
      obj = rs.GetObject("Pick any object")
      if obj:
      color = rs.ObjectColor(obj)
      rs.ObjectsByColor(color, True)
    See Also:
      
    """
    color = rhutil.coercecolor(color, True)
    rhino_objects = scriptcontext.doc.Objects.FindByDrawColor(color, include_lights)
    if select:
        for obj in rhino_objects: obj.Select(True)
        scriptcontext.doc.Views.Redraw()
    return [obj.Id for obj in rhino_objects]


def ObjectsByGroup(group_name, select=False):
    """Returns identifiers of all objects based on the objects' group name
    Parameters:
      group_name = name of the group
      select [opt] = select the objects
    Returns:
      list of identifiers on success
    Example:
      import rhinoscriptsyntax as rs
      group = rs.GetString("Group to select")
      if group: rs.ObjectsByGroup( group, True )
    See Also:
      
    """
    group_index = scriptcontext.doc.Groups.Find(group_name, True)
    if group_index<0: raise ValueError("%s does not exist in GroupTable"%group_name)
    rhino_objects = scriptcontext.doc.Groups.GroupMembers(group_index)
    if not rhino_objects: return []
    if select:
        for obj in rhino_objects: obj.Select(True)
        scriptcontext.doc.Views.Redraw()
    return [obj.Id for obj in rhino_objects]


def ObjectsByLayer(layer_name, select=False):
    """Returns identifiers of all objects based on the objects' layer name
    Parameters:
      layer_name = name of the layer
      select [opt] = select the objects
    Returns:
      list of identifiers
    Example:
      import rhinoscriptsyntax as rs
      obj = rs.GetObject("Pick any object")
      if obj:
      layer = rs.ObjectLayer(obj)
      rs.ObjectsByLayer(layer, True)
    See Also:
      
    """
    layer = __getlayer(layer_name, True)
    rhino_objects = scriptcontext.doc.Objects.FindByLayer(layer)
    if not rhino_objects: return []
    if select:
        for rhobj in rhino_objects: rhobj.Select(True)
        scriptcontext.doc.Views.Redraw()
    return [rhobj.Id for rhobj in rhino_objects]


def ObjectsByName(name, select=False, include_lights=False, include_references=False):
    """Returns identifiers of all objects based on user-assigned name
    Parameters:
      name = name of the object or objects
      select[opt] = select the objects
      include_lights[opt] = include light objects
    Returns:
      list of identifiers
    Example:
      import rhinoscriptsyntax as rs
      name = rs.GetString("Name to select")
      if name: rs.ObjectsByName(name,True)
    See Also:
      
    """
    settings = Rhino.DocObjects.ObjectEnumeratorSettings()
    settings.HiddenObjects = True
    settings.DeletedObjects = False
    settings.IncludeGrips = False
    settings.IncludePhantoms = True
    settings.IncludeLights = include_lights
    settings.NameFilter = name
    settings.ReferenceObjects = include_references
    objects = scriptcontext.doc.Objects.GetObjectList(settings)
    ids = [rhobj.Id for rhobj in objects]
    if ids and select:
        objects = scriptcontext.doc.Objects.GetObjectList(settings)
        for rhobj in objects: rhobj.Select(True)
        scriptcontext.doc.Views.Redraw()
    return ids
   

def ObjectsByType(geometry_type, select=False, state=0):
    """Returns identifiers of all objects based on the objects' geometry type.
    Parameters:
      geometry_type = The type(s) of geometry objects (points, curves, surfaces,
             meshes, etc.) that can be selected. Object types can be
             added together to filter several different kinds of geometry.
              Value        Description
               0           All objects
               1           Point
               2           Point cloud
               4           Curve
               8           Surface or single-face brep
               16          Polysurface or multiple-face
               32          Mesh
               256         Light
               512         Annotation
               4096        Instance or block reference
               8192        Text dot object
               16384       Grip object
               32768       Detail
               65536       Hatch
               131072      Morph control
               134217728   Cage
               268435456   Phantom
               536870912   Clipping plane
      select[opt] = Select the objects
      state[opt] = Object state. See help
    Returns:
      A list of Guids identifying the objects.
    Example:
      import rhinoscriptsyntax as  rs
      objs = rs.ObjectsByType(4 |  8, True)
    See Also:
      
    """
    if not state: state = 7
    bSurface = False
    bPolySurface = False
    bLights = False
    bGrips = False
    bPhantoms = False
    geometry_filter = __FilterHelper(geometry_type)
    if type(geometry_type) is int and geometry_type==0:
        geometry_filter = Rhino.DocObjects.ObjectType.AnyObject
    if geometry_filter & Rhino.DocObjects.ObjectType.Surface: bSurface = True
    if geometry_filter & Rhino.DocObjects.ObjectType.Brep: bPolySurface = True
    if geometry_filter & Rhino.DocObjects.ObjectType.Light: bLights = True
    if geometry_filter & Rhino.DocObjects.ObjectType.Grip: bGrips = True
    if geometry_filter & Rhino.DocObjects.ObjectType.Phantom: bPhantoms = True

    it = Rhino.DocObjects.ObjectEnumeratorSettings()
    it.DeletedObjects = False
    it.ActiveObjects = True
    it.ReferenceObjects = True
    it.IncludeLights = bLights
    it.IncludeGrips = bGrips
    it.IncludePhantoms = bPhantoms

    it.NormalObjects = True
    it.LockedObjects = True
    it.HiddenObjects = True

    object_ids = []
    e = scriptcontext.doc.Objects.GetObjectList(it)
    for object in e:
      if state & 1 and object.IsNormal or state & 2 and object.IsLocked or state & 4 and object.IsHidden:
        bFound = False
        object_type = object.ObjectType
        if object_type==Rhino.DocObjects.ObjectType.Brep and (bSurface or bPolySurface):
            brep = rhutil.coercebrep(object.Id)
            if brep:
                if brep.Faces.Count==1:
                    if bSurface: bFound = True
                else:
                    if bPolySurface: bFound = True
        elif object_type==Rhino.DocObjects.ObjectType.Extrusion and (bSurface or bPolySurface):
            extrusion = object.Geometry
            profile_count = extrusion.ProfileCount
            cap_count = extrusion.CapCount
            if profile_count==1 and cap_count==0 and bSurface:
                bFound = True
            elif profile_count>0 and cap_count>0 and bPolySurface:
                bFound = True
        elif object_type & geometry_filter:
            bFound = True

        if bFound:
            if select: object.Select(True)
            object_ids.append(object.Id)

    if object_ids and select: scriptcontext.doc.Views.Redraw()
    return object_ids
  

def SelectedObjects(include_lights=False, include_grips=False):
    """Returns the identifiers of all objects that are currently selected
    Parameters:
      include_lights [opt] = include light objects
      include_grips [opt] = include grip objects
    Returns:
      list of Guids identifying the objects
    Example:
      import rhinoscriptsyntax as rs
      objects = rs.SelectedObjects()
      for obj in objects: print "Object identifier: ", obj
    See Also:
      InvertSelectedObjects
      UnselectAllObjects
    """
    selobjects = scriptcontext.doc.Objects.GetSelectedObjects(include_lights, include_grips)
    return [obj.Id for obj in selobjects]


def UnselectAllObjects():
    """Unselects all objects in the document
    Parameters:
      None
    Returns:
      the number of objects that were unselected
    Example:
      import rhinoscriptsyntax as rs
      count = rs.UnselectAllObjects()
      print count, " objects were unselected"
    See Also:
      InvertSelectedObjects
      SelectedObjects
    """
    rc = scriptcontext.doc.Objects.UnselectAll()
    if rc>0: scriptcontext.doc.Views.Redraw()
    return rc


def VisibleObjects(view=None, select=False, include_lights=False, include_grips=False):
    """Return identifiers of all objects that are visible in a specified view
    Parameters:
      view [opt] = the view to use. If omitted, the current active view is used
      select [opt] = Select the objects
      include_lights [opt] = include light objects
      include_grips [opt] = include grip objects
    Returns:
      list of Guids identifying the objects
    Example:
      import rhinoscriptsyntax as rs
      object_ids = rs.VisibleObjects("Top")
      if object_ids:
      for id in object_ids: print "Object identifier:", id
    See Also:
      IsView
      IsVisibleInView
    """
    it = Rhino.DocObjects.ObjectEnumeratorSettings()
    it.DeletedObjects = False
    it.ActiveObjects = True
    it.ReferenceObjects = True
    it.IncludeLights = include_lights
    it.IncludeGrips = include_grips
    it.VisibleFilter = True
    viewport = __viewhelper(view).MainViewport
    it.ViewportFilter = viewport

    object_ids = []
    e = scriptcontext.doc.Objects.GetObjectList(it)
    for object in e:
        bbox = object.Geometry.GetBoundingBox(True)
        if viewport.IsVisible(bbox):
            if select: object.Select(True)
            object_ids.append(object.Id)

    if object_ids and select: scriptcontext.doc.Views.Redraw()
    return object_ids


def WindowPick(corner1, corner2, view=None, select=False, in_window=True):
    """Picks objects using either a window or crossing selection
    Parameters:
      corner1, corner2 = corners of selection window
      view[opt] = view to perform the selection in
      select[opt] = select picked objects
      in_window[opt] = if False, then a crossing window selection is performed
    Returns:
      list of object ids on success
    Example:
      import rhinoscriptsyntax as  rs
      rs.WindowPick((0,0,0), (0,0,0),  None, True)
    See Also:
      
    """
    viewport = __viewhelper(view).MainViewport
    screen1 = Rhino.Geometry.Point2d(rhutil.coerce3dpoint(corner1, True))
    screen2 = Rhino.Geometry.Point2d(rhutil.coerce3dpoint(corner2, True))
    xf = viewport.GetTransform(Rhino.DocObjects.CoordinateSystem.World, Rhino.DocObjects.CoordinateSystem.Screen)
    screen1.Transform(xf)
    screen2.Transform(xf)
    objects = None
    filter = Rhino.DocObjects.ObjectType.AnyObject
    if in_window:
        objects = scriptcontext.doc.Objects.FindByWindowRegion(viewport, screen1, screen2, True, filter)
    else:
        objects = scriptcontext.doc.Objects.FindByCrossingWindowRegion(viewport, screen1, screen2, True, filter)
    if objects:
        rc = []
        for rhobj in objects:
            rc.append(rhobj.Id)
            if select: rhobj.Select(True)
        if select: scriptcontext.doc.Views.Redraw()
        return rc