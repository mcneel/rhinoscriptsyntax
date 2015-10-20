import scriptcontext
import utility as rhutil
import Rhino
import System.Enum
import math

def __viewhelper(view):
    if view is None: return scriptcontext.doc.Views.ActiveView
    allviews = scriptcontext.doc.Views.GetViewList(True, True)
    view_id = rhutil.coerceguid(view, False)
    for item in allviews:
        if view_id:
            if item.MainViewport.Id == view_id: return item
        elif item.MainViewport.Name == view:
            return item
    raise ValueError("unable to coerce %s into a view"%view)


def AddDetail(layout_id, corner1, corner2, title=None, projection=1):
    """Add new detail view to an existing layout view
    Parameters:
      layout_id = identifier of an existing layout
      corner1, corner2 = 2d corners of the detail in the layout's unit system
      title[opt] = title of the new detail
      projection[opt] = type of initial view projection for the detail
          1 = parallel top view
          2 = parallel bottom view
          3 = parallel left view
          4 = parallel right view
          5 = parallel front view
          6 = parallel back view
          7 = perspective view
    Returns:
      identifier of the newly created detial on success
      None on error
    """
    layout_id = rhutil.coerceguid(layout_id, True)
    corner1 = rhutil.coerce2dpoint(corner1, True)
    corner2 = rhutil.coerce2dpoint(corner2, True)
    if projection<1 or projection>7: raise ValueError("projection must be a value between 1-7")
    layout = scriptcontext.doc.Views.Find(layout_id)
    if not layout: raise ValueError("no layout found for given layout_id")
    projection = System.Enum.ToObject(Rhino.Display.DefinedViewportProjection, projection)
    detail = layout.AddDetailView(title, corner1, corner2, projection)
    if not detail: return scriptcontext.errorhandler()
    scriptcontext.doc.Views.Redraw()
    return detail.Id


def AddLayout(title=None, size=None):
    """Adds a new page layout view
    Parameters:
      title[opt] = title of new layout
      size[opt] = width and height of paper for the new layout
    Returns:
      id of new layout
    """
    page = None
    if size is None: page = scriptcontext.doc.Views.AddPageView(title)
    else: page = scriptcontext.doc.Views.AddPageView(title, size[0], size[1])
    if page: return page.MainViewport.Id


def AddNamedCPlane(cplane_name, view=None):
    """Adds new named construction plane to the document
    Parameters:
      cplane_name: the name of the new named construction plane
      view:[opt] string or Guid. Title or identifier of the view from which to save
               the construction plane. If omitted, the current active view is used.
    Returns:
      name of the newly created construction plane if successful
      None on error
    """
    view = __viewhelper(view)
    if not cplane_name: raise ValueError("cplane_name is empty")
    plane = view.MainViewport.ConstructionPlane()
    index = scriptcontext.doc.NamedConstructionPlanes.Add(cplane_name, plane)
    if index<0: return scriptcontext.errorhandler()
    return cplane_name


def AddNamedView(name, view=None):
    """Adds a new named view to the document
    Parameters:
      name: the name of the new named view
      view: [opt] the title or identifier of the view to save. If omitted, the current
            active view is saved
    Returns:
      name fo the newly created named view if successful
      None on error
    """
    view = __viewhelper(view)
    if not name: raise ValueError("name is empty")
    viewportId = view.MainViewport.Id
    index = scriptcontext.doc.NamedViews.Add(name, viewportId)
    if index<0: return scriptcontext.errorhandler()
    return name


def CurrentDetail(layout, detail=None, return_name=True):
    """Returns or changes the current detail view in a page layout view
    Parameters:
      layout = title or identifier of an existing page layout view
      detail[opt] = title or identifier the the detail view to set
      return_name[opt] = return title if True, else return identifier
    Returns:
      if detail is not specified, the title or id of the current detail view
      if detail is specified, the title or id of the previous detail view
      None on error
    """
    layout_id = rhutil.coerceguid(layout)
    page = None
    if layout_id is None: page = scriptcontext.doc.Views.Find(layout, False)
    else: page = scriptcontext.doc.Views.Find(layout_id)
    if page is None: return scriptcontext.errorhandler()
    rc = None
    active_viewport = page.ActiveViewport
    if return_name: rc = active_viewport.Name
    else: rc = active_viewport.Id
    if detail:
        id = rhutil.coerceguid(detail)
        if( (id and id==page.MainViewport.Id) or (id is None and detail==page.MainViewport.Name) ):
            page.SetPageAsActive()
        else:
            if id: page.SetActiveDetail(id)
            else: page.SetActiveDetail(detail, False)
    scriptcontext.doc.Views.Redraw()
    return rc


def CurrentView(view=None, return_name=True):
    """Returns or sets the currently active view
    Parameters:
      view:[opt] String or Guid. Title or id of the view to set current.
        If omitted, only the title or identifier of the current view is returned
      return_name:[opt] If True, then the name, or title, of the view is returned.
        If False, then the identifier of the view is returned
    Returns:
      if the title is not specified, the title or id of the current view
      if the title is specified, the title or id of the previous current view
      None on error
    """
    rc = None
    if return_name: rc = scriptcontext.doc.Views.ActiveView.MainViewport.Name
    else: rc = scriptcontext.doc.Views.ActiveView.MainViewport.Id
    if view:
        id = rhutil.coerceguid(view)
        rhview = None
        if id: rhview = scriptcontext.doc.Views.Find(id)
        else: rhview = scriptcontext.doc.Views.Find(view, False)
        if rhview is None: return scriptcontext.errorhandler()
        scriptcontext.doc.Views.ActiveView = rhview
    return rc


def DeleteNamedCPlane(name):
    """Removes a named construction plane from the document
    Parameters:
      name: name of the construction plane to remove
    Returns:
      True or False indicating success or failure
    """
    return scriptcontext.doc.NamedConstructionPlanes.Delete(name)


def DeleteNamedView(name):
    """Removes a named view from the document
    Parameters:
      name: name of the named view to remove
    Returns:
      True or False indicating success or failure
    """
    return scriptcontext.doc.NamedViews.Delete(name)


def DetailLock(detail_id, lock=None):
    """Returns or modifies the projection locked state of a detail
    Parameters:
      detail_id = identifier of a detail object
      lock[opt] = the new lock state
    Returns:
      if lock==None, the current detail projection locked state
      if lock is True or False, the previous detail projection locked state
      None on error
    """
    detail_id = rhutil.coerceguid(detail_id, True)
    detail = scriptcontext.doc.Objects.Find(detail_id)
    if not detail: return scriptcontext.errorhandler()
    rc = detail.DetailGeometry.IsProjectionLocked
    if lock is not None and lock!=rc:
        detail.DetailGeometry.IsProjectionLocked = lock
        detail.CommitChanges()
    return rc


def DetailScale(detail_id, model_length=None, page_length=None):
    """Returns or modifies the scale of a detail object
    Parameters:
      detail_id = identifier of a detail object
      model_length[opt] = a length in the current model units
      page_length[opt] = a length in the current page units
    Returns:
      current page to model scale ratio if model_length and page_length are both None
      previous page to model scale ratio if model_length and page_length are values
      None on error
    """
    detail_id = rhutil.coerceguid(detail_id, True)
    detail = scriptcontext.doc.Objects.Find(detail_id)
    if detail is None: return scriptcontext.errorhandler()
    rc = detail.DetailGeometry.PageToModelRatio
    if model_length or page_length:
        if model_length is None or page_length is None:
            return scriptcontext.errorhandler()
        model_units = scriptcontext.doc.ModelUnitSystem
        page_units = scriptcontext.doc.PageUnitSystem
        if detail.DetailGeometry.SetScale(model_length, model_units, page_length, page_units):
            detail.CommitChanges()
            scriptcontext.doc.Views.Redraw()
    return rc


def IsDetail(layout, detail):
    """Verifies that a detail view exists on a page layout view
    Parameters:
      layout: title or identifier of an existing page layout
      detail: title or identifier of an existing detail view
    Returns:
      True if detail is a detail view
      False if detail is not a detail view
      None on error
    """
    layout_id = rhutil.coerceguid(layout)
    views = scriptcontext.doc.Views.GetViewList(False, True)
    found_layout = None
    for view in views:
        if layout_id:
            if view.MainViewport.Id==layout_id:
                found_layout = view
                break
        elif view.MainViewport.Name==layout:
            found_layout = view
            break
    # if we couldn't find a layout, this is an error
    if found_layout is None: return scriptcontext.errorhandler()
    detail_id = rhutil.coerceguid(detail)
    details = view.GetDetailViews()
    if not details: return False
    for detail_view in details:
        if detail_id:
            if detail_view.Id==detail_id: return True
        else:
            if detail_view.Name==detail: return True
    return False


def IsLayout(layout):
    """Verifies that a view is a page layout view
    Parameters:
      layout: title or identifier of an existing page layout view
    Returns:
      True if layout is a page layout view
      False is layout is a standard, model view
      None on error
    """
    layout_id = rhutil.coerceguid(layout)
    alllayouts = scriptcontext.doc.Views.GetViewList(False, True)
    for layoutview in alllayouts:
        if layout_id:
            if layoutview.MainViewport.Id==layout_id: return True
        elif layoutview.MainViewport.Name==layout: return True
    allmodelviews = scriptcontext.doc.Views.GetViewList(True, False)
    for modelview in allmodelviews:
        if layout_id:
          if modelview.MainViewport.Id==layout_id: return False
        elif modelview.MainViewport.Name==layout: return False
    return scriptcontext.errorhandler()


def IsView(view):
    """Verifies that the specified view exists
    Parameters:
      view: title or identifier of the view
    Returns:
      True of False indicating success or failure
    """
    view_id = rhutil.coerceguid(view)
    if view_id is None and view is None: return False
    allviews = scriptcontext.doc.Views.GetViewList(True, True)
    for item in allviews:
        if view_id:
            if item.MainViewport.Id==view_id: return True
        elif item.MainViewport.Name==view: return True
    return False


def IsViewCurrent(view):
    """Verifies that the specified view is the current, or active view
    Parameters:
      view: title or identifier of the view
    Returns:
      True of False indicating success or failure
    """
    activeview = scriptcontext.doc.Views.ActiveView
    view_id = rhutil.coerceguid(view)
    if view_id: return view_id==activeview.MainViewport.Id
    return view==activeview.MainViewport.Name


def IsViewMaximized(view=None):
    """Verifies that the specified view is maximized (enlarged so as to fill
    the entire Rhino window)
    Parameters:
      view: [opt] title or identifier of the view. If omitted, the current
            view is used
    Returns:
      True of False
    """
    view = __viewhelper(view)
    return view.Maximized


def IsViewPerspective(view):
    """Verifies that the specified view's projection is set to perspective
    Parameters:
      view: title or identifier of the view
    Returns:
      True of False
    """
    view = __viewhelper(view)
    return view.MainViewport.IsPerspectiveProjection


def IsViewTitleVisible(view=None):
    """Verifies that the specified view's title window is visible
    Parameters:
      view: [opt] The title or identifier of the view. If omitted, the current
            active view is used
    Returns:
      True of False
    """
    view = __viewhelper(view)
    return view.MainViewport.TitleVisible


def IsWallpaper(view):
    """Verifies that the specified view contains a wallpaper image
    Parameters:
      view = view to verify
    Returns:
      True or False
    """
    view = __viewhelper(view)
    return len(view.MainViewport.WallpaperFilename)>0


def MaximizeRestoreView(view=None):
    """Toggles a view's maximized/restore window state of the specified view
    Parameters:
      view: [opt] the title or identifier of the view. If omitted, the current
            active view is used
    Returns:
      None
    """
    view = __viewhelper(view)
    view.Maximized = not view.Maximized


def NamedCPlane(name):
    """Returns the plane geometry of the specified named construction plane
    Parameters:
      name: the name of the construction plane
    Returns:
      a plane on success
      None on error
    """
    index = scriptcontext.doc.NamedConstructionPlanes.Find(name)
    if index<0: return scriptcontext.errorhandler()
    return scriptcontext.doc.NamedConstructionPlanes[index].Plane


def NamedCPlanes():
    "Returns the names of all named construction planes in the document"
    count = scriptcontext.doc.NamedConstructionPlanes.Count
    rc = [scriptcontext.doc.NamedConstructionPlanes[i].Name for i in range(count)]
    return rc


def NamedViews():
    "Returns the names of all named views in the document"
    count = scriptcontext.doc.NamedViews.Count
    return [scriptcontext.doc.NamedViews[i].Name for i in range(count)]


def RenameView(old_title, new_title):
    """Changes the title of the specified view
    Parameters:
      old_title: the title or identifier of the view to rename
      new_title: the new title of the view
    Returns:
      the view's previous title if successful
      None on error
    """
    if not old_title or not new_title: return scriptcontext.errorhandler()
    old_id = rhutil.coerceguid(old_title)
    foundview = None
    allviews = scriptcontext.doc.Views.GetViewList(True, True)
    for view in allviews:
        if old_id:
            if view.MainViewport.Id==old_id:
                foundview = view
                break
        elif view.MainViewport.Name==old_title:
            foundview = view
            break
    if foundview is None: return scriptcontext.errorhandler()
    old_title = foundview.MainViewport.Name
    foundview.MainViewport.Name = new_title
    return old_title


def RestoreNamedCPlane(cplane_name, view=None):
    """Restores a named construction plane to the specified view.
    Parameters:
      cplane_name: name of the construction plane to restore
      view: [opt] the title or identifier of the view. If omitted, the current
            active view is used
    Returns:
      name of the restored named construction plane if successful
      None on error
    """
    view = __viewhelper(view)
    index = scriptcontext.doc.NamedConstructionPlanes.Find(cplane_name)
    if index<0: return scriptcontext.errorhandler()
    cplane = scriptcontext.doc.NamedConstructionPlanes[index]
    view.MainViewport.PushConstructionPlane(cplane)
    view.Redraw()
    return cplane_name


def RestoreNamedView(named_view, view=None, restore_bitmap=False):
    """Restores a named view to the specified view
    Parameters:
      named_view: name of the named view to restore
      view:[opt] title or id of the view to restore the named view.
           If omitted, the current active view is used
      restore_bitmap: [opt] restore the named view's background bitmap
    Returns:
      name of the restored view if successful
      None on error
    """
    view = __viewhelper(view)
    index = scriptcontext.doc.NamedViews.FindByName(named_view)
    if index<0: return scriptcontext.errorhandler()
    viewinfo = scriptcontext.doc.NamedViews[index]
    if view.MainViewport.PushViewInfo(viewinfo, restore_bitmap):
        view.Redraw()
        return view.MainViewport.Name
    return scriptcontext.errorhandler()


def RotateCamera(view=None, direction=0, angle=None):
    """Rotates a perspective-projection view's camera. See the RotateCamera
    command in the Rhino help file for more details
    Parameters:
      view:[opt] title or id of the view. If omitted, current active view is used
      direction: [opt] the direction to rotate the camera where 0=right, 1=left,
            2=down, 3=up
      angle: [opt] the angle to rotate. If omitted, the angle of rotation
            is specified by the "Increment in divisions of a circle" parameter
            specified in Options command's View tab
    Returns:
      True or False indicating success or failure
    """
    view = __viewhelper(view)
    viewport = view.ActiveViewport
    if angle is None:
        angle = 2.0*math.pi/Rhino.ApplicationSettings.ViewSettings.RotateCircleIncrement
    else:
        angle = Rhino.RhinoMath.ToRadians( abs(angle) )
    target_distance = (viewport.CameraLocation-viewport.CameraTarget)*viewport.CameraZ
    axis = viewport.CameraY
    if direction==0 or direction==2: angle=-angle
    if direction==0 or direction==1:
        if Rhino.ApplicationSettings.ViewSettings.RotateToView:
            axis = viewport.CameraY
        else:
            axis = Rhino.Geometry.Vector3d.ZAxis
    elif direction==2 or direction==3:
        axis = viewport.CameraX
    else:
        return False
    if Rhino.ApplicationSettings.ViewSettings.RotateReverseKeyboard: angle=-angle
    rot = Rhino.Geometry.Transform.Rotation(angle, axis, Rhino.Geometry.Point3d.Origin)
    camUp = rot * viewport.CameraY
    camDir = -(rot * viewport.CameraZ)
    target = viewport.CameraLocation + target_distance*camDir
    viewport.SetCameraLocations(target, viewport.CameraLocation)
    viewport.CameraUp = camUp
    view.Redraw()
    return True


def RotateView(view=None, direction=0, angle=None):
    """Rotates a view. See RotateView command in Rhino help for more information
    Parameters:
      view:[opt] title or id of the view. If omitted, the current active view is used
      direction:[opt] the direction to rotate the view where
            0=right, 1=left, 2=down, 3=up
      angle:[opt] angle to rotate. If omitted, the angle of rotation is specified
            by the "Increment in divisions of a circle" parameter specified in
            Options command's View tab
    Returns:
      True or False indicating success or failure
    """
    view = __viewhelper(view)
    viewport = view.ActiveViewport
    if angle is None:
        angle = 2.0*math.pi/Rhino.ApplicationSettings.ViewSettings.RotateCircleIncrement
    else:
        angle = Rhino.RhinoMath.ToRadians( abs(angle) )
    if Rhino.ApplicationSettings.ViewSettings.RotateReverseKeyboard: angle = -angle
    if direction==0: viewport.KeyboardRotate(True, angle)
    elif direction==1: viewport.KeyboardRotate(True, -angle)
    elif direction==2: viewport.KeyboardRotate(False, -angle)
    elif direction==3: viewport.KeyboardRotate(False, angle)
    else: return False
    view.Redraw()
    return True


def ShowGrid(view=None, show=None):
    """Shows or hides a view's construction plane grid
    Parameters:
      view:[opt] title or id of the view. If omitted, the current active view is used
      show:[opt] The grid state to set. If omitted, the current grid display state is returned
    Returns:
      If show is not specified, then the grid display state if successful
      If show is specified, then the previous grid display state if successful
    """
    view = __viewhelper(view)
    viewport = view.ActiveViewport
    rc = viewport.ConstructionGridVisible
    if show is not None and rc!=show:
        viewport.ConstructionGridVisible = show
        view.Redraw()
    return rc


def ShowGridAxes(view=None, show=None):
    """Shows or hides a view's construction plane grid axes.
    Parameters:
      view:[opt] title or id of the view. If omitted, the current active view
        is used
      show:[opt] The state to set. If omitted, the current grid axes display
        state is returned
    Returns:
      If show is not specified, then the grid axes display state
      If show is specified, then the previous grid axes display state
    """
    view = __viewhelper(view)
    viewport = view.ActiveViewport
    rc = viewport.ConstructionAxesVisible
    if show is not None and rc!=show:
        viewport.ConstructionAxesVisible = show
        view.Redraw()
    return rc


def ShowViewTitle(view=None, show=True):
    """Shows or hides the title window of a view
    Parameters:
      view:[opt] title or id of the view. If omitted, the current active view is used
      show:[opt] The state to set.
    Returns:
      None
    """
    view = __viewhelper(view)
    if view is None: return scriptcontext.errorhandler()
    view.TitleVisible = show


def ShowWorldAxes(view=None, show=None):
    """Shows or hides a view's world axis icon
    Parameters:
      view: [opt] title or id of the view. If omitted, the current active view is used
      show: [opt] The state to set.
    Returns:
      If show is not specified, then the world axes display state
      If show is specified, then the previous world axes display state
    """
    view = __viewhelper(view)
    viewport = view.ActiveViewport
    rc = viewport.WorldAxesVisible
    if show is not None and rc!=show:
        viewport.WorldAxesVisible = show
        view.Redraw()
    return rc


def TiltView(view=None, direction=0, angle=None):
    """Tilts a view by rotating the camera up vector. See the TiltView command in
    the Rhino help file for more details.
    Parameters:
      view [opt] = title or id of the view. If omitted, the current active view is used
      direction [opt] = the direction to rotate the view where 0=right, 1=left
      angle [opt] = the angle to rotate. If omitted, the angle of rotation is
        specified by the "Increment in divisions of a circle" parameter specified
        in Options command's View tab
    Returns:
      True or False indicating success or failure
    """
    view = __viewhelper(view)
    viewport = view.ActiveViewport
    if angle is None:
        angle = 2.0*math.pi/Rhino.ApplicationSettings.ViewSettings.RotateCircleIncrement
    else:
        angle = Rhino.RhinoMath.ToRadians( abs(angle) )
    
    if Rhino.ApplicationSettings.ViewSettings.RotateReverseKeyboard: angle = -angle
    axis = viewport.CameraLocation - viewport.CameraTarget
    if direction==0: viewport.Rotate(angle, axis, viewport.CameraLocation)
    elif direction==1: viewport.Rotate(-angle, axis, viewport.CameraLocation)
    else: return False
    view.Redraw()
    return True


def ViewCamera(view=None, camera_location=None):
    """Returns or sets the camera location of the specified view
    Parameters:
      view:[opt] title or id of the view. If omitted, the current active view is used
      camera_location: [opt] a 3D point identifying the new camera location.
        If omitted, the current camera location is returned
    Returns:
      If camera_location is not specified, the current camera location
      If camera_location is specified, the previous camera location
      None on error    
    """
    view = __viewhelper(view)
    rc = view.ActiveViewport.CameraLocation
    if camera_location is None: return rc
    camera_location = rhutil.coerce3dpoint(camera_location)
    if camera_location is None: return scriptcontext.errorhandler()
    view.ActiveViewport.SetCameraLocation(camera_location, True)
    view.Redraw()
    return rc


def ViewCameraLens(view=None, length=None):
    """Returns or sets the 35mm camera lens length of the specified perspective
    projection view.
    Parameters:
      view:[opt] title or id of the view. If omitted, the current active view is used
      length:[opt] the new 35mm camera lens length. If omitted, the previous
        35mm camera lens length is returned
    Returns:
      If lens length is not specified, the current lens length
      If lens length is specified, the previous lens length
    """
    view = __viewhelper(view)
    rc = view.ActiveViewport.Camera35mmLensLength
    if not length: return rc
    view.ActiveViewport.Camera35mmLensLength = length
    view.Redraw()
    return rc


def ViewCameraPlane(view=None):
    """Returns the orientation of a view's camera.
    Parameters:
      view:[opt] title or id of the view. If omitted, the current active view is used
    Returns:
      the view's camera plane if successful
      None on error
    """
    view = __viewhelper(view)
    rc, frame = view.ActiveViewport.GetCameraFrame()
    if not rc: return scriptcontext.errorhandler()
    return frame


def ViewCameraTarget(view=None, camera=None, target=None):
    """Returns or sets the camera and target positions of the specified view
    Parameters:
      view:[opt] title or id of the view. If omitted, current active view is used
      camera:[opt] 3d point identifying the new camera location. If camera and
         target are not specified, current camera and target locations are returned
      target:[opt] 3d point identifying the new target location. If camera and
         target are not specified, current camera and target locations are returned
    Returns:
      if both camera and target are not specified, then the 3d points containing
        the current camera and target locations is returned
      if either camera or target are specified, then the 3d points containing the
        previous camera and target locations is returned
    """
    view = __viewhelper(view)
    rc = view.ActiveViewport.CameraLocation, view.ActiveViewport.CameraTarget
    if not camera and not target: return rc
    if camera: camera = rhutil.coerce3dpoint(camera, True)
    if target: target = rhutil.coerce3dpoint(target, True)
    if camera and target: view.ActiveViewport.SetCameraLocations(target, camera)
    elif camera is None: view.ActiveViewport.SetCameraTarget(target, True)
    else: view.ActiveViewport.SetCameraLocation(camera, True)
    view.Redraw()
    return rc


def ViewCameraUp(view=None, up_vector=None):
    """Returns or sets the camera up direction of a specified
    Parameters:
      view[opt]: title or id of the view. If omitted, the current active view is used
      up_vector[opt]: 3D vector identifying the new camera up direction
    Returns:
      if up_vector is not specified, then the current camera up direction
      if up_vector is specified, then the previous camera up direction
    """
    view = __viewhelper(view)
    rc = view.ActiveViewport.CameraUp
    if up_vector:
        view.ActiveViewport.CameraUp = rhutil.coerce3dvector(up_vector, True)
        view.Redraw()
    return rc


def ViewCPlane(view=None, plane=None):
    """Return or set a view's construction plane
    Parameters:
      view:[opt] title or id of the view. If omitted, current active view is used.
      plane:[opt] the new construction plane if setting
    Returns:
      If a construction plane is not specified, the current construction plane
      If a construction plane is specified, the previous construction plane
    """
    view = __viewhelper(view)
    cplane = view.ActiveViewport.ConstructionPlane()
    if plane:
        plane = rhutil.coerceplane(plane, True)
        view.ActiveViewport.SetConstructionPlane(plane)
        view.Redraw()
    return cplane

def ViewDisplayMode(view=None, mode=None, return_name=True):
    """Return or set a view display mode
    Parameters:
      view: [opt] Title or id of a view. If omitted, active view is used
      mode: [opt] Name or id of a display mode
      return_name: [opt] If true, return display mode name. If False, display mode id
    Returns:
      If mode is specified, the previous mode
      If mode is not specified, the current mode
    """
    view = __viewhelper(view)
    current = view.ActiveViewport.DisplayMode
    if return_name: rc = current.EnglishName
    else: rc = current.Id
    if mode:
        mode_id = rhutil.coerceguid(mode)
        if mode_id:
            desc = Rhino.Display.DisplayModeDescription.GetDisplayMode(mode_id)
        else:
            desc = Rhino.Display.DisplayModeDescription.FindByName(mode)
        if desc: view.ActiveViewport.DisplayMode = desc
        scriptcontext.doc.Views.Redraw()
    return rc


def ViewDisplayModeId(name):
    """Return id of a display mode given it's name
    Parameters:
      name = name of the display mode
    Returns:
      The id of the display mode if successful, otherwise None
    """
    desc = Rhino.Display.DisplayModeDescription.FindByName(name)
    if desc: return desc.Id


def ViewDisplayModeName(mode_id):
    """Return name of a display mode given it's id
    Parameters:
      mode_id = The identifier of the display mode obtained from the ViewDisplayModes method.
    Returns:
      The name of the display mode if successful, otherwise None
    """
    mode_id = rhutil.coerceguid(mode_id, True)
    desc = Rhino.Display.DisplayModeDescription.GetDisplayMode(mode_id)
    if desc: return desc.EnglishName


def ViewDisplayModes(return_names=True):
    """Return list of display modes
    Parameters:
      return_name [opt] = If True, return mode names. If False, return ids
    Returns:
      A list of strings identifying the display mode names or identifiers if successful
    """
    modes = Rhino.Display.DisplayModeDescription.GetDisplayModes()
    if return_names:
        return [mode.EnglishName for mode in modes]
    return [mode.Id for mode in modes]


def ViewNames(return_names=True, view_type=0):
    """Return the names, titles, or identifiers of all views in the document
    Parameters:
      return_names: [opt] if True then the names of the views are returned.
        If False, then the identifiers of the views are returned
      view_type: [opt] the type of view to return
                       0 = standard model views
                       1 = page layout views
                       2 = both standard and page layout views
    Returns:
      list of the view names or identifiers on success
      None on error
    """
    views = scriptcontext.doc.Views.GetViewList(view_type!=1, view_type>0)
    if views is None: return scriptcontext.errorhandler()
    if return_names: return [view.MainViewport.Name for view in views]
    return [view.MainViewport.Id for view in views]


def ViewNearCorners(view=None):
    """Return 3d corners of a view's near clipping plane rectangle. Useful
    in determining the "real world" size of a parallel-projected view
    Parameters:
      view:[opt] title or id of the view. If omitted, current active view is used
    Returns:
      Four Point3d that define the corners of the rectangle (counter-clockwise order)
    """
    view = __viewhelper(view)
    rc = view.ActiveViewport.GetNearRect()
    return rc[0], rc[1], rc[3], rc[2]


def ViewProjection(view=None, mode=None):
    """Return or set a view's projection mode.
    Parameters:
      view:[opt] title or id of the view. If omitted, current active view is used
      mode:[opt] the projection mode (1=parallel, 2=perspective)
    Returns:
      if mode is not specified, the current projection mode for the specified view
      if mode is specified, the previous projection mode for the specified view
    """
    view = __viewhelper(view)
    viewport = view.ActiveViewport
    rc = 2
    if viewport.IsParallelProjection: rc = 1
    if mode is None or mode==rc: return rc
    if mode==1: viewport.ChangeToParallelProjection(True)
    elif mode==2: viewport.ChangeToPerspectiveProjection(True, 50)
    else: return
    view.Redraw()
    return rc

def ViewRadius(view=None, radius=None, mode=False):
    """Returns or sets the radius of a parallel-projected view. Useful
    when you need an absolute zoom factor for a parallel-projected view
    Parameters:
      view:[opt] title or id of the view. If omitted, current active view is used
      radius:[opt] the view radius
      mode: [opt] perform a "dolly" magnification by moving the camera 
        towards/away from the target so that the amount of the screen 
        subtended by an object changes.  true = perform a "zoom" 
        magnification by adjusting the "lens" angle
    Returns:
      if radius is not specified, the current view radius for the specified view
      if radius is specified, the previous view radius for the specified view
    """
    view = __viewhelper(view)
    viewport = view.ActiveViewport
    if not viewport.IsParallelProjection: return scriptcontext.errorhandler()
    fr = viewport.GetFrustum()
    frus_right = fr[2]
    frus_top = fr[4]
    old_radius = min(frus_top, frus_right)
    if radius is None: return old_radius
    magnification_factor = radius / old_radius
    d = 1.0 / magnification_factor
    viewport.Magnify(d, mode)
    view.Redraw()
    return old_radius


def ViewSize(view=None):
    """Returns the width and height in pixels of the specified view
    Parameters:
      view:[opt] title or id of the view. If omitted, current active view is used
    Returns:
      tuple of two numbers idenfitying width and height
    """
    view = __viewhelper(view)
    cr = view.ClientRectangle
    return cr.Width, cr.Height


def ViewSpeedTest(view=None, frames=100, freeze=True, direction=0, angle_degrees=5):
    """Test's Rhino's display performance
    Parameters:
      view [opt] = The title or identifier of the view.  If omitted, the current active view is used
      frames [opt] = The number of frames, or times to regenerate the view. If omitted, the view will be regenerated 100 times.
      freeze [opt] = If True (Default), then Rhino's display list will not be updated with every frame redraw. If False, then Rhino's display list will be updated with every frame redraw.
      direction [opt] = The direction to rotate the view, where 0 = Right, 1 = Left, 2 = Down, and 3 = Up. The default direction is Right (0).
      angle_degrees [opt] = The angle to rotate. If omitted, the rotation angle of 5.0 degrees will be used.
    Returns:
      The number of seconds it took to regenerate the view frames number of times, if successful, otherwise None.
    """
    view = __viewhelper(view)
    angle_radians = math.radians(angle_degrees)
    return view.SpeedTest(frames, freeze, direction, angle_radians)


def ViewTarget(view=None, target=None):
    """Returns or sets the target location of the specified view
    Parameters:
      view:[opt] title or id of the view. If omitted, current active view is used
      target:[opt] 3d point identifying the new target location. If omitted,
        the current target location is returned
    Returns:
      is target is not specified, then the current target location
      is target is specified, then the previous target location
      None on error
    """
    view = __viewhelper(view)
    viewport = view.ActiveViewport
    old_target = viewport.CameraTarget
    if target is None: return old_target
    target = rhutil.coerce3dpoint(target)
    if target is None: return scriptcontext.errorhandler()
    viewport.SetCameraTarget(target, True)
    view.Redraw()
    return old_target


def ViewTitle(view_id):
    """Returns the name, or title, of a given view's identifier
    Parameters:
      view_id: String or Guid. The identifier of the view
    Returns:
      name or title of the view on success
      None on error
    """
    view_id = rhutil.coerceguid(view_id)
    if view_id is None: return scriptcontext.errorhandler()
    view = scriptcontext.doc.Views.Find(view_id)
    if view is None: return scriptcontext.errorhandler()
    return view.MainViewport.Name


def Wallpaper(view=None, filename=None):
    """Returns or sets the wallpaper bitmap of the specified view. To remove a
    wallpaper bitmap, pass an empty string ""
    Parameters:
      view[opt] = String or Guid. The identifier of the view. If omitted, the
        active view is used
      filename[opt] = Name of the bitmap file to set as wallpaper
    Returns:
      If filename is not specified, the current wallpaper bitmap filename
      If filename is specified, the previous wallpaper bitmap filename
    """
    view = __viewhelper(view)
    rc = view.ActiveViewport.WallpaperFilename
    if filename is not None and filename!=rc:
        view.ActiveViewport.SetWallpaper(filename, False)
        view.Redraw()
    return rc


def WallpaperGrayScale(view=None, grayscale=None):
    """Returns or sets the grayscale display option of the wallpaper bitmap in a
    specified view
    Parameters:
      view[opt] = String or Guid. The identifier of the view. If omitted, the
        active view is used
      grayscale[opt] = Display the wallpaper in gray(True) or color (False)
    Returns:
      If grayscale is not specified, the current grayscale display option
      If grayscale is specified, the previous grayscale display option
    """
    view = __viewhelper(view)
    rc = view.ActiveViewport.WallpaperGrayscale
    if grayscale is not None and grayscale!=rc:
        filename = view.ActiveViewport.WallpaperFilename
        view.ActiveViewport.SetWallpaper(filename, grayscale)
        view.Redraw()
    return rc


def WallpaperHidden(view=None, hidden=None):
    """Returns or sets the visibility of the wallpaper bitmap in a specified view
    Parameters:
      view[opt] = String or Guid. The identifier of the view. If omitted, the
        active view is used
      hidden[opt] = Show or hide the wallpaper
    Returns:
      If hidden is not specified, the current hidden state
      If hidden is specified, the previous hidden state
    """
    view = __viewhelper(view)
    rc = not view.ActiveViewport.WallpaperVisible
    if hidden is not None and hidden!=rc:
        filename = view.ActiveViewport.WallpaperFilename
        gray = view.ActiveViewport.WallpaperGrayscale
        view.ActiveViewport.SetWallpaper(filename, gray, not hidden)
        view.Redraw()
    return rc


def ZoomBoundingBox(bounding_box, view=None, all=False):
    """Zooms to the extents of a specified bounding box in the specified view
    Parameters:
      bounding_box = eight points that define the corners of a bounding box
        or a BoundingBox class instance
      view [opt] = title or id of the view. If omitted, current active view is used
      all [opt] = zoom extents in all views
    Returns:
      None
    """
    bbox = rhutil.coerceboundingbox(bounding_box)
    if bbox:
      if all:
          views = scriptcontext.doc.Views.GetViewList(True, True)
          for view in views: view.ActiveViewport.ZoomBoundingBox(bbox)
      else:
          view = __viewhelper(view)
          view.ActiveViewport.ZoomBoundingBox(bbox)
      scriptcontext.doc.Views.Redraw()


def ZoomExtents(view=None, all=False):
    """Zooms to extents of visible objects in the specified view
    Parameters:
      view [opt] = title or id of the view. If omitted, current active view is used
      all [opt] = zoom extents in all views
    Returns:
      None
    """
    if all:
        views = scriptcontext.doc.Views.GetViewList(True, True)
        for view in views: view.ActiveViewport.ZoomExtents()
    else:
        view = __viewhelper(view)
        view.ActiveViewport.ZoomExtents()
    scriptcontext.doc.Views.Redraw()


def ZoomSelected(view=None, all=False):
    """Zoom to extents of selected objects in a view
    Parameters:
      view [opt] = title or id of the view. If omitted, active view is used
      all [opt] = zoom extents in all views
    Returns:
      None
    """
    if all:
        views = scriptcontext.doc.Views.GetViewList(True, True)
        for view in views: view.ActiveViewport.ZoomExtentsSelected()
    else:
        view = __viewhelper(view)
        view.ActiveViewport.ZoomExtentsSelected()
    scriptcontext.doc.Views.Redraw()
