import scriptcontext
import Rhino
import utility as rhutil
import System.Guid, System.Enum
from layer import __getlayer


def CopyObject(object_id, translation=None):
    """Copies object from one location to another, or in-place.
    Parameters:
      object_id: object to copy
      translation[opt]: translation vector to apply
    Returns:
      id for the copy if successful
      None if not able to copy
    """
    rc = CopyObjects(object_id, translation)
    if rc: return rc[0]


def CopyObjects(object_ids, translation=None):
    """Copies one or more objects from one location to another, or in-place.
    Parameters:
      object_ids: list of objects to copy
      translation [opt]: list of three numbers or Vector3d representing
                         translation vector to apply to copied set
    Returns:
      list of identifiers for the copies if successful
    """
    if translation:
        translation = rhutil.coerce3dvector(translation, True)
        translation = Rhino.Geometry.Transform.Translation(translation)
    else:
        translation = Rhino.Geometry.Transform.Identity
    rc = TransformObjects(object_ids, translation, True)
    return rc


def DeleteObject(object_id):
    """Deletes a single object from the document
    Parameters:
      object_id: identifier of object to delete
    Returns:
      True of False indicating success or failure
    """
    object_id = rhutil.coerceguid(object_id, True)
    rc = scriptcontext.doc.Objects.Delete(object_id, True)
    if rc: scriptcontext.doc.Views.Redraw()
    return rc


def DeleteObjects(object_ids):
    """Deletes one or more objects from the document
    Parameters:
      object_ids: identifiers of objects to delete
    Returns:
      Number of objects deleted
    """
    rc = 0
    id = rhutil.coerceguid(object_ids, False)
    if id: object_ids = [id]
    for id in object_ids:
        id = rhutil.coerceguid(id, True)
        if scriptcontext.doc.Objects.Delete(id, True): rc+=1
    if rc: scriptcontext.doc.Views.Redraw()
    return rc


def FlashObject(object_ids, style=True):
    """Causes the selection state of one or more objects to change momentarily
    so the object appears to flash on the screen
    Parameters:
      object_ids = identifiers of objects to flash
      style[opt] = If True, flash between object color and selection color.
        If False, flash between visible and invisible
    """
    id = rhutil.coerceguid(object_ids, False)
    if id: object_ids = [id]
    rhobjs = [rhutil.coercerhinoobject(id, True, True) for id in object_ids]
    if rhobjs: scriptcontext.doc.Views.FlashObjects(rhobjs, style)


def HideObject(object_id):
    """Hides a single object. Hidden objects are not visible, cannot be snapped
    to and cannot be selected
    Parameters:
      object_id: String or Guid representing id of object to hide
    Returns:
      True of False indicating success or failure
    """
    id = rhutil.coerceguid(object_id, True)
    rc = scriptcontext.doc.Objects.Hide(id, False)
    scriptcontext.doc.Views.Redraw()
    return rc


def HideObjects(object_ids):
    """Hides one or more objects. Hidden objects are not visible, cannot be
    snapped to and cannot be selected
    Parameters:
      object_ids: identifiers of objects to hide
    Returns:
      Number of objects hidden
    """
    id = rhutil.coerceguid(object_ids, False)
    if id: object_ids = [id]
    rc = 0
    for id in object_ids:
        id = rhutil.coerceguid(id, True)
        if scriptcontext.doc.Objects.Hide(id, False): rc += 1
    if rc: scriptcontext.doc.Views.Redraw()
    return rc


def IsLayoutObject(object_id):
    """Verifies that an object is in either page layout space or model space
    Parameters:
      object_id: String or Guid representing id of an object
    Returns:
      True if the object is in page layout space
      False if the object is in model space
    """
    rhobj = rhutil.coercerhinoobject(object_id, True, True)
    return rhobj.Attributes.Space == Rhino.DocObjects.ActiveSpace.PageSpace


def IsObject(object_id):
    """Verifies the existance of an object
    Parameters:
      object_id: The identifier of an object
    Returns:
      True if the object exists
      False if the object does not exist
    """
    return rhutil.coercerhinoobject(object_id, True, False) is not None


def IsObjectHidden(object_id):
    """Verifies that an object is hidden. Hidden objects are not visible, cannot
    be snapped to, and cannot be selected
    Parameters:
      object_id: String or Guid. The identifier of an object
    Returns:
      True if the object is hidden
      False if the object is not hidden
    """
    rhobj = rhutil.coercerhinoobject(object_id, True, True)
    return rhobj.IsHidden


def IsObjectInBox(object_id, box, test_mode=True):
    """Verifies an object's bounding box is inside of another bounding box
    Parameters:
      object_id: String or Guid. The identifier of an object
      box: bounding box to test for containment
      test_mode[opt] = If True, the object's bounding box must be contained by box
        If False, the object's bounding box must be contained by or intersect box
    Returns:
      True if object is inside box
      False is object is not inside box
    """
    rhobj = rhutil.coercerhinoobject(object_id, True, True)
    box = rhutil.coerceboundingbox(box, True)
    objbox = rhobj.Geometry.GetBoundingBox(True)
    if test_mode: return box.Contains(objbox)
    union = Rhino.Geometry.BoundingBox.Intersection(box, objbox)
    return union.IsValid


def IsObjectInGroup(object_id, group_name=None):
    """Verifies that an object is a member of a group
    Parameters:
      object_id: The identifier of an object
      group_name[opt]: The name of a group. If omitted, the function
        verifies that the object is a member of any group
    Returns:
      True if the object is a member of the specified group. If a group_name
        was not specified, the object is a member of some group.
      False if the object is not a member of the specified group. If a
        group_name was not specified, the object is not a member of any group
    """
    rhobj = rhutil.coercerhinoobject(object_id, True, True)
    count = rhobj.GroupCount
    if count<1: return False
    if not group_name: return True
    index = scriptcontext.doc.Groups.Find(group_name, True)
    if index<0: raise ValueError("%s group does not exist"%group_name)
    group_ids = rhobj.GetGroupList()
    for id in group_ids:
        if id==index: return True
    return False


def IsObjectLocked(object_id):
    """Verifies that an object is locked. Locked objects are visible, and can
    be snapped to, but cannot be selected
    Parameters:
      object_id: String or Guid. The identifier of an object
    Returns:
      True if the object is locked
      False if the object is not locked
    """
    rhobj = rhutil.coercerhinoobject(object_id, True, True)
    return rhobj.IsLocked


def IsObjectNormal(object_id):
    """Verifies that an object is normal. Normal objects are visible, can be
    snapped to, and can be selected
    Parameters:
      object_id: String or Guid. The identifier of an object
    Returns:
      True if the object is normal
      False if the object is not normal
    """
    rhobj = rhutil.coercerhinoobject(object_id, True, True)
    return rhobj.IsNormal


def IsObjectReference(object_id):
    """Verifies that an object is a reference object. Reference objects are
    objects that are not part of the current document
    Parameters:
      object_id: String or Guid. The identifier of an object
    Returns:
      True if the object is a reference object
      False if the object is not a reference object
    """
    rhobj = rhutil.coercerhinoobject(object_id, True, True)
    return rhobj.IsReference


def IsObjectSelectable(object_id):
    """Verifies that an object can be selected
    Parameters:
      object_id: String or Guid. The identifier of an object
    Returns:
      True or False
    """
    rhobj = rhutil.coercerhinoobject(object_id, True, True)
    return rhobj.IsSelectable()


def IsObjectSelected(object_id):
    """Verifies that an object is currently selected
    Parameters:
      object_id: String or Guid. The identifier of an object
    Returns:
      True if the object is selected
      False if the object is not selected
    """
    rhobj = rhutil.coercerhinoobject(object_id, True, True)
    return rhobj.IsSelected(False)


def IsObjectSolid(object_id):
    """Verifies that an object is a closed, solid object
    Parameters:
      object_id: String or Guid. The identifier of an object
    Returns:
      True if the object is solid
      False if the object is not solid
    """
    rhobj = rhutil.coercerhinoobject(object_id, True, True)
    if( isinstance(rhobj, Rhino.DocObjects.BrepObject) or isinstance(rhobj, Rhino.DocObjects.SurfaceObject) ):
        return rhobj.Geometry.IsSolid
    if( isinstance(rhobj, Rhino.DocObjects.MeshObject) ):
        return rhobj.MeshGeometry.IsClosed
    return False


def IsObjectValid(object_id):
    """Verifies that an object's geometry is valid and without error
    Parameters:
      object_id: String or Guid. The identifier of an object
    Returns:
      True if the object is valid
      False if the object is not valid
    """
    rhobj = rhutil.coercerhinoobject(object_id, True, True)
    return rhobj.IsValid

# [skipping for now] IsVisibleInView

def LockObject(object_id):
    """Locks a single object. Locked objects are visible, and they can be
    snapped to. But, they cannot be selected.
    Parameters:
      object_id: The identifier of an object
    Returns:
      True or False indicating success or failure
    """
    return LockObjects(object_id)==1


def LockObjects(object_ids):
    """Locks one or more objects. Locked objects are visible, and they can be
    snapped to. But, they cannot be selected.
    Parameters:
      object_ids: list of Strings or Guids. The identifiers of objects
    Returns:
      number of objects locked
    """
    id = rhutil.coerceguid(object_ids, False)
    if id: object_ids = [id]
    rc = 0
    for id in object_ids:
        id = rhutil.coerceguid(id, True)
        if scriptcontext.doc.Objects.Lock(id, False): rc += 1
    if rc: scriptcontext.doc.Views.Redraw()
    return rc


def MatchObjectAttributes(target_ids, source_id=None):
    """Matches, or copies the attributes of a source object to a target object
    Parameters:
      target_ids = identifiers of objects to copy attributes to
      source_id[opt] = identifier of object to copy attributes from. If None,
        then the default attributes are copied to the target_ids
    Returns:
      number of objects modified
    """
    id = rhutil.coerceguid(target_ids, False)
    if id: target_ids = [id]
    source_attr = Rhino.DocObjects.ObjectAttributes()
    if source_id:
        source = rhutil.coercerhinoobject(source_id, True, True)
        source_attr = source.Attributes
    rc = 0
    for id in target_ids:
        id = rhutil.coerceguid(id, True)
        if scriptcontext.doc.Objects.ModifyAttributes(id, source_attr, True):
            rc += 1
    if rc: scriptcontext.doc.Views.Redraw()
    return rc


def MirrorObject(object_id, start_point, end_point, copy=False):
    """Mirrors a single object
    Parameters:
      object_id: String or Guid. The identifier of an object
      start_point: start of the mirror plane
      end_point: end of the mirror plane
      copy[opt] = copy the object
    Returns:
      Identifier of the mirrored object if successful
      None on error
    """
    rc = MirrorObjects(object_id, start_point, end_point, copy)
    if rc: return rc[0]


def MirrorObjects(object_ids, start_point, end_point, copy=False):
    """Mirrors a list of objects
    Parameters:
      object_ids: identifiers of objects to mirror
      start_point: start of the mirror plane
      end_point: end of the mirror plane
      copy[opt] = copy the objects
    Returns:
      List of identifiers of the mirrored objects if successful
    """
    start_point = rhutil.coerce3dpoint(start_point, True)
    end_point = rhutil.coerce3dpoint(end_point, True)
    vec = end_point-start_point
    if vec.IsTiny(0): raise Exception("start and end points are too close to each other")
    normal = scriptcontext.doc.Views.ActiveView.ActiveViewport.ConstructionPlane().Normal
    vec = Rhino.Geometry.Vector3d.CrossProduct(vec, normal)
    vec.Unitize()
    xf = Rhino.Geometry.Transform.Mirror(start_point, vec)
    rc = TransformObjects(object_ids, xf, copy)
    return rc


def MoveObject(object_id, translation):
    """Moves a single object
    Parameters:
      object_id: String or Guid. The identifier of an object
      translation: list of 3 numbers or Vector3d
    Returns:
      Identifier of the moved object if successful
      None on error
    """
    rc = MoveObjects(object_id, translation)
    if rc: return rc[0]


def MoveObjects(object_ids, translation):
    """Moves one or more objects
    Parameters:
      object_ids: The identifiers objects to move
      translation: list of 3 numbers or Vector3d
    Returns:
      List of identifiers of the moved objects if successful
    """
    translation = rhutil.coerce3dvector(translation, True)
    xf = Rhino.Geometry.Transform.Translation(translation)
    rc = TransformObjects(object_ids, xf)
    return rc


def ObjectColor(object_ids, color=None):
    """Returns of modifies the color of an object. Object colors are represented
    as RGB colors. An RGB color specifies the relative intensity of red, green,
    and blue to cause a specific color to be displayed
    Parameters:
        object_ids = id or ids of object(s)
        color[opt] = the new color value. If omitted, then current object
            color is returned. If object_ids is a list, color is required
    Returns:
        If color value is not specified, the current color value
        If color value is specified, the previous color value
        If object_ids is a list, then the number of objects modified
    """
    id = rhutil.coerceguid(object_ids, False)
    rhino_object = None
    rhino_objects = None
    if id:
        rhino_object = rhutil.coercerhinoobject(id, True, True)
    else:
        rhino_objects = [rhutil.coercerhinoobject(id, True, True) for id in object_ids]
        if len(rhino_objects)==1:
            rhino_object = rhino_objects[0]
            rhino_objects = None
    if color is None:
        #get the color
        if rhino_objects: raise ValueError("color must be specified when a list of rhino objects is provided")
        return rhino_object.Attributes.DrawColor(scriptcontext.doc)
    color = rhutil.coercecolor(color, True)
    if rhino_objects is not None:
        for rh_obj in rhino_objects:
            attr = rh_obj.Attributes
            attr.ObjectColor = color
            attr.ColorSource = Rhino.DocObjects.ObjectColorSource.ColorFromObject
            scriptcontext.doc.Objects.ModifyAttributes( rh_obj, attr, True)
        return len(rhino_objects)
    rc = rhino_object.Attributes.DrawColor(scriptcontext.doc)
    attr = rhino_object.Attributes
    attr.ObjectColor = color
    attr.ColorSource = Rhino.DocObjects.ObjectColorSource.ColorFromObject
    scriptcontext.doc.Objects.ModifyAttributes( rhino_object, attr, True )
    scriptcontext.doc.Views.Redraw()
    return rc


def ObjectColorSource(object_ids, source=None):
    """Returns of modifies the color source of an object.
    Paramters:
      object_ids = single identifier of list of identifiers
      source[opt] = new color source
          0 = color from layer
          1 = color from object
          2 = color from material
          3 = color from parent
    Returns:
      if color source is not specified, the current color source
      is color source is specified, the previous color source
      if color_ids is a list, then the number of objects modifief
    """
    id = rhutil.coerceguid(object_ids, False)
    if id:
        rhobj = rhutil.coercerhinoobject(id, True, True)
        rc = int(rhobj.Attributes.ColorSource)
        if source is not None:
            rhobj.Attributes.ColorSource = System.Enum.ToObject(Rhino.DocObjects.ObjectColorSource, source)
            rhobj.CommitChanges()
            scriptcontext.doc.Views.Redraw()
        return rc
    else:
        rc = 0
        source = System.Enum.ToObject(Rhino.DocObjects.ObjectColorSource, source)
        for id in object_ids:
            rhobj = rhutil.coercerhinoobject(id, True, True)
            rhobj.Attributes.ColorSource = source
            rhobj.CommitChanges()
            rc += 1
        if rc: scriptcontext.doc.Views.Redraw()
        return rc


def ObjectDescription(object_id):
    """Returns a short text description of an object
    Parameters:
      object_id = identifier of an object
    """
    rhobj = rhutil.coercerhinoobject(object_id, True, True)
    return rhobj.ShortDescription(False)


def ObjectGroups(object_id):
    """Returns all of the group names that an object is assigned to
    Parameters:
      object_id = identifier of an object
    Returns:
      list of group names on success
    """
    rhino_object = rhutil.coercerhinoobject(object_id, True, True)
    if rhino_object.GroupCount<1: return []
    group_indices = rhino_object.GetGroupList()
    rc = [scriptcontext.doc.Groups.GroupName(index) for index in group_indices]
    return rc


def ObjectLayer(object_id, layer=None):
    """Returns or modifies the layer of an object
    Parameters:
      object_id = the identifier of the object(s)
      layer[opt] = name of an existing layer
    Returns:
      If a layer is not specified, the object's current layer
      If a layer is specified, the object's previous layer
      If object_id is a list or tuple, the number of objects modified
    """
    if type(object_id) is not str and hasattr(object_id, "__len__"):
        layer = __getlayer(layer, True)
        index = layer.LayerIndex
        for id in object_id:
            obj = rhutil.coercerhinoobject(object_id, True, True)
            obj.Attributes.LayerIndex = index
            obj.CommitChanges()
        scriptcontext.doc.Views.Redraw()
        return len(object_id)
    obj = rhutil.coercerhinoobject(object_id, True, True)
    if obj is None: return scriptcontext.errorhandler()
    index = obj.Attributes.LayerIndex
    rc = scriptcontext.doc.Layers[index].Name
    if layer:
        layer = __getlayer(layer, True)
        index = layer.LayerIndex
        obj.Attributes.LayerIndex = index
        obj.CommitChanges()
        scriptcontext.doc.Views.Redraw()
    return rc


def ObjectLayout(object_id, layout=None, return_name=True):
    """Returns or changes the layout or model space of an object
    Parameters:
      object_id = identifier of the object
      layout[opt] = to change, or move, an object from model space to page
        layout space, or from one page layout to another, then specify the
        title or identifier of an existing page layout view. To move an object
        from page layout space to model space, just specify None
      return_name[opt] = If True, the name, or title, of the page layout view
        is returned. If False, the identifier of the page layout view is returned
    Returns:
      if layout is not specified, the object's current page layout view
      if layout is specfied, the object's previous page layout view
      None if not successful
    """
    rhobj = rhutil.coercerhinoobject(object_id, True, True)
    rc = None
    if rhobj.Attributes.Space==Rhino.DocObjects.ActiveSpace.PageSpace:
        page_id = rhobj.Attributes.ViewportId
        pageview = scriptcontext.doc.Views.Find(page_id)
        if return_name: rc = pageview.MainViewport.Name
        else: rc = pageview.MainViewport.Id
        if layout is None: #move to model space
            rhobj.Attributes.Space = Rhino.DocObjects.ActiveSpace.ModelSpace
            rhobj.Attributes.ViewportId = System.Guid.Empty
            rhobj.CommitChanges()
            scriptcontext.doc.Views.Redraw()
    else:
        if layout:
            layout = scriptcontext.doc.Views.Find(layout, False)
            if layout is not None and isinstance(layout, Rhino.Display.RhinoPageView):
                rhobj.Attributes.ViewportId = layout.MainViewport.Id
                rhobj.Attributes.Space = Rhino.DocObjects.ActiveSpace.PageSpace
                rhobj.CommitChanges()
                scriptcontext.doc.Views.Redraw()
    return rc


def ObjectLinetype(object_ids, linetype=None):
    """Returns of modifies the linetype of an object
    Parameters:
      object_ids = identifiers of object(s)
      linetype[opt] = name of an existing linetype. If omitted, the current
        linetype is returned. If object_ids is a list of identifiers, this parameter
        is required
    Returns:
      If a linetype is not specified, the object's current linetype
      If linetype is specified, the object's previous linetype
      If object_ids is a list, the number of objects modified
    """
    id = rhutil.coerceguid(object_ids, False)
    if id:
        rhino_object = rhutil.coercerhinoobject(id, True, True)
        oldindex = scriptcontext.doc.Linetypes.LinetypeIndexForObject(rhino_object)
        if linetype:
            newindex = scriptcontext.doc.Linetypes.Find(linetype, True)
            rhino_object.Attributes.LinetypeSource = Rhino.DocObjects.ObjectLinetypeSource.LinetypeFromObject
            rhino_object.Attributes.LinetypeIndex = newindex
            rhino_object.CommitChanges()
            scriptcontext.doc.Views.Redraw()
        return scriptcontext.doc.Linetypes[oldindex].Name

    newindex = scriptcontext.doc.Linetypes.Find(linetype, True)
    if newindex<0: raise Exception("%s does not exist in LineTypes table"%linetype)
    for id in object_ids:
        rhino_object = rhutil.coercerhinoobject(id, True, True)
        rhino_object.Attributes.LinetypeSource = Rhino.DocObjects.ObjectLinetypeSource.LinetypeFromObject
        rhino_object.Attributes.LinetypeIndex = newindex
        rhino_object.CommitChanges()
    scriptcontext.doc.Views.Redraw()
    return len(object_ids)


def ObjectLinetypeSource(object_ids, source=None):
    """Returns of modifies the linetype source of an object
    Parameters:
      object_ids = identifiers of object(s)
      source[opt] = new linetype source. If omitted, the current source is returned.
        If object_ids is a list of identifiers, this parameter is required
          0 = By Layer
          1 = By Object
          3 = By Parent
    Returns:
      If a source is not specified, the object's current linetype source
      If source is specified, the object's previous linetype source
      If object_ids is a list, the number of objects modified
    """
    id = rhutil.coerceguid(object_ids, False)
    if id:
        rhino_object = rhutil.coercerhinoobject(id, True, True)
        oldsource = rhino_object.Attributes.LinetypeSource
        if source is not None:
            source = System.Enum.ToObject(Rhino.DocObjects.ObjectLinetypeSource, source)
            rhino_object.Attributes.LinetypeSource = source
            rhino_object.CommitChanges()
            scriptcontext.doc.Views.Redraw()
        return int(oldsource)
    source = System.Enum.ToObject(Rhino.DocObjects.ObjectLinetypeSource, source)
    for id in object_ids:
        rhino_object = rhutil.coercerhinoobject(id, True, True)
        rhino_object.Attributes.LinetypeSource = source
        rhino_object.CommitChanges()
    scriptcontext.doc.Views.Redraw()
    return len(object_ids)


def ObjectMaterialIndex(object_id):
    """Returns the material index of an object. Rendering materials are stored in
    Rhino's rendering material table. The table is conceptually an array. Render
    materials associated with objects and layers are specified by zero based
    indices into this array.
    Parameters:
      object_id = identifier of an object
    Returns:
      If the return value of ObjectMaterialSource is "material by object", then
      the return value of this function is the index of the object's rendering
      material. A material index of -1 indicates no material has been assigned,
      and that Rhino's internal default material has been assigned to the object.
      None on failure      
    """
    rhino_object = rhutil.coercerhinoobject(object_id, True, True)
    return rhino_object.Attributes.MaterialIndex


def ObjectMaterialSource(object_ids, source=None):
    """Returns or modifies the rendering material source of an object.
    Parameters:
      object_ids = one or more object identifiers
      source [opt] = The new rendering material source. If omitted and a single
        object is provided in object_ids, then the current material source is
        returned. This parameter is required if multiple objects are passed in
        object_ids
        0 = Material from layer
        1 = Material from object
        3 = Material from parent
    Returns:
      If source is not specified, the current rendering material source
      If source is specified, the previous rendering material source
      If object_ids refers to multiple objects, the number of objects modified
    """
    id = rhutil.coerceguid(object_ids, False)
    if id: # working with single object
        rhino_object = rhutil.coercerhinoobject(id, True, True)
        rc = int(rhino_object.Attributes.MaterialSource)
        if source is not None:
            rhino_object.Attributes.MaterialSource = System.Enum.ToObject(Rhino.DocObjects.ObjectMaterialSource, source)
            rhino_object.CommitChanges()
        return rc
    # else working with multiple objects
    if source is None: raise Exception("source is required when object_ids represents multiple objects")
    for id in object_ids:
        rhino_object = rhutil.coercerhinoobject(id, True, True)
        rhino_object.Attributes.MaterialSource = source
        rhino_object.CommitChanges()
    return len(object_ids)


def ObjectName(object_id, name=None):
    """Returns or modifies the user-definable name of an object
    Parameters:
      object_id = id or ids of object(s)
      name[opt] = the new object name. If omitted, the current object name
        is returned.
    Returns:
      If name is not specified, the current object name
      If name is specified, the previous object name
      If object_id is a list, the number of objects changed
    """
    id = rhutil.coerceguid(object_id, False)
    rhino_object = None
    rhino_objects = None
    if id:
        rhino_object = rhutil.coercerhinoobject(id, True, True)
    else:
        rhino_objects = [rhutil.coercerhinoobject(id, True, True) for id in object_id]
        if not rhino_objects: return 0
        if len(rhino_objects)==1:
            rhino_object = rhino_objects[0]
            rhino_objects = None
    if name is None:
        #get the name
        if rhino_objects: raise Exception("name required when object_id represents multiple objects")
        return rhino_object.Name
    if rhino_objects:
        for rh_obj in rhino_objects:
            attr = rh_obj.Attributes
            attr.Name = name
            scriptcontext.doc.Objects.ModifyAttributes(rh_obj, attr, True)
        return len(rhino_objects)
    rc = rhino_object.Name
    attr = rhino_object.Attributes
    attr.Name = name
    scriptcontext.doc.Objects.ModifyAttributes(rhino_object, attr, True)
    return rc


def ObjectPrintWidth(object_ids, width=None):
    """Returns or modifies the print width of an object
    Parameters:
      object_ids = identifiers of object(s)
      width[opt] = new print width value in millimeters, where width=0 means use
        the default width, and width<0 means do not print (visible for screen display,
        but does not show on print). If omitted, the current width is returned.
    Returns:
      If width is not specified, the object's current print width
      If width is specified, the object's previous print width
      If object_ids is a list or tuple, the number of objects modified
    """
    id = rhutil.coerceguid(object_ids, False)
    if id:
        rhino_object = rhutil.coercerhinoobject(id, True, True)
        rc = rhino_object.Attributes.PlotWeight
        if width is not None:
            rhino_object.Attributes.PlotWeightSource = Rhino.DocObjects.ObjectPlotWeightSource.PlotWeightFromObject
            rhino_object.Attributes.PlotWeight = width
            rhino_object.CommitChanges()
            scriptcontext.doc.Views.Redraw()
        return rc
    for id in object_ids:
        rhino_object = rhutil.coercerhinoobject(id, True, True)
        rhino_object.Attributes.PlotWeightSource = Rhino.DocObjects.ObjectPlotWeightSource.PlotWeightFromObject
        rhino_object.Attributes.PlotWeight = width
        rhino_object.CommitChanges()
    scriptcontext.doc.Views.Redraw()
    return len(object_ids)


def ObjectPrintWidthSource(object_ids, source=None):
    """Returns or modifies the print width source of an object
    Parameters:
      object_ids = identifiers of object(s)
      source[opt] = new print width source
        0 = print width by layer
        1 = print width by object
        3 = print width by parent
    Returns:
      If source is not specified, the object's current print width source
      If source is specified, the object's previous print width source
      If object_ids is a list or tuple, the number of objects modified
    """
    id = rhutil.coerceguid(object_ids, False)
    if id:
        rhino_object = rhutil.coercerhinoobject(id, True, True)
        rc = int(rhino_object.Attributes.PlotWeight)
        if source is not None:
            rhino_object.Attributes.PlotWeightSource = System.Enum.ToObject(Rhino.DocObjects.ObjectPlotWeightSource, source)
            rhino_object.CommitChanges()
            scriptcontext.doc.Views.Redraw()
        return rc
    for id in object_ids:
        rhino_object = rhutil.coercerhinoobject(id, True, True)
        rhino_object.Attributes.PlotWeightSource = System.Enum.ToObject(Rhino.DocObjects.ObjectPlotWeightSource, source)
        rhino_object.CommitChanges()
    scriptcontext.doc.Views.Redraw()
    return len(object_ids)


def ObjectType(object_id):
    """Returns the object type
    Parameters:
      object_id = identifier of an object
    Returns:
      see help for values
    """
    rhobj = rhutil.coercerhinoobject(object_id, True, True)
    geom = rhobj.Geometry
    if isinstance(geom, Rhino.Geometry.Brep) and geom.Faces.Count==1:
        return 8 #surface
    return int(geom.ObjectType)


def OrientObject(object_id, reference, target, flags=0):
    """Orients a single object based on input points
    Parameters:
        object_id = String or Guid. The identifier of an object
        reference = list of 3-D reference points
        target = list of 3-D target points
        flags[opt]: 1 = copy object
                    2 = scale object
    """
    object_id = rhutil.coerceguid(object_id, True)
    from_array = rhutil.coerce3dpointlist(reference)
    to_array = rhutil.coerce3dpointlist(target)
    if from_array is None or to_array is None:
        raise ValueError("Could not convert reference or target to point list")
    from_count = len(from_array)
    to_count = len(to_array)
    if from_count<2 or to_count<2: raise Exception("point lists must have at least 2 values")

    copy = ((flags & 1) == 1)
    scale = ((flags & 2) == 2)
    xform_final = None
    if from_count>2 and to_count>2:
        #Orient3Pt
        from_plane = Rhino.Geometry.Plane(from_array[0], from_array[1], from_array[2])
        to_plane = Rhino.Geometry.Plane(to_array[0], to_array[1], to_array[2])
        if not from_plane.IsValid or not to_plane.IsValid:
            raise Exception("unable to create valid planes from point lists")
        xform_final = Rhino.Geometry.Transform.PlaneToPlane(from_plane, to_plane)
    else:
        #Orient2Pt
        xform_move = Rhino.Geometry.Transform.Translation( to_array[0]-from_array[0] )
        xform_scale = Rhino.Geometry.Transform.Identity
        v0 = from_array[1] - from_array[0]
        v1 = to_array[1] - to_array[0]
        if scale:
            len0 = v0.Length
            len1 = v1.Length
            if len0<0.000001 or len1<0.000001: raise Exception("vector lengths too short")
            scale = len1 / len0
            if abs(1.0-scale)>=0.000001:
                plane = Rhino.Geometry.Plane(from_array[0], v0)
                xform_scale = Rhino.Geometry.Transform.Scale(plane, scale, scale, scale)
        v0.Unitize()
        v1.Unitize()
        xform_rotate = Rhino.Geometry.Transform.Rotation(v0, v1, from_array[0])
        xform_final = xform_move * xform_scale * xform_rotate
    rc = scriptcontext.doc.Objects.Transform(object_id, xform_final, not copy)
    if rc==System.Guid.Empty: return scriptcontext.errorhandler()
    scriptcontext.doc.Views.Redraw()
    return rc


def RotateObject(object_id, center_point, rotation_angle, axis=None, copy=False):
    """Rotates a single object
    Parameters:
      object_id: String or Guid. The identifier of an object
      center_point: the center of rotation
      rotation_angle: in degrees
      axis[opt] = axis of rotation, If omitted, the Z axis of the active
        construction plane is used as the rotation axis
      copy[opt] = copy the object
    Returns:
      Identifier of the rotated object if successful
      None on error
    """
    rc = RotateObjects(object_id, center_point, rotation_angle, axis, copy)
    if rc: return rc[0]
    return scriptcontext.errorhandler()


def RotateObjects( object_ids, center_point, rotation_angle, axis=None, copy=False):
    """Rotates multiple objects
    Parameters:
      object_ids: Identifiers of objects to rotate
      center_point: the center of rotation
      rotation_angle: in degrees
      axis[opt] = axis of rotation, If omitted, the Z axis of the active
        construction plane is used as the rotation axis
      copy[opt] = copy the object
    Returns:
      List of identifiers of the rotated objects if successful
    """
    center_point = rhutil.coerce3dpoint(center_point, True)
    if not axis:
        axis = scriptcontext.doc.Views.ActiveView.ActiveViewport.ConstructionPlane().Normal
    axis = rhutil.coerce3dvector(axis, True)
    rotation_angle = Rhino.RhinoMath.ToRadians(rotation_angle)
    xf = Rhino.Geometry.Transform.Rotation(rotation_angle, axis, center_point)
    rc = TransformObjects(object_ids, xf, copy)
    return rc


def ScaleObject(object_id, origin, scale, copy=False):
    """Scales a single object. Can be used to perform a uniform or non-uniform
    scale transformation. Scaling is based on the active construction plane.
    Parameters:
      object_id: The identifier of an object
      origin: the origin of the scale transformation
      scale: three numbers that identify the X, Y, and Z axis scale factors to apply
      copy[opt] = copy the object
    Returns:
      Identifier of the scaled object if successful
      None on error
    """
    rc = ScaleObjects(object_id, origin, scale, copy )
    if rc: return rc[0]
    return scriptcontext.errorhandler()


def ScaleObjects(object_ids, origin, scale, copy=False):
    """Scales one or more objects. Can be used to perform a uniform or non-
    uniform scale transformation. Scaling is based on the active construction plane.
    Parameters:
      object_ids: Identifiers of objects to scale
      origin: the origin of the scale transformation
      scale: three numbers that identify the X, Y, and Z axis scale factors to apply
      copy[opt] = copy the objects
    Returns:
      List of identifiers of the scaled objects if successful
      None on error
    """
    origin = rhutil.coerce3dpoint(origin, True)
    scale = rhutil.coerce3dpoint(scale, True)
    plane = scriptcontext.doc.Views.ActiveView.ActiveViewport.ConstructionPlane()
    plane.Origin = origin
    xf = Rhino.Geometry.Transform.Scale(plane, scale.X, scale.Y, scale.Z)
    rc = TransformObjects(object_ids, xf, copy)
    return rc


def SelectObject(object_id):
    """Selects a single object
    Parameters:
      object_id = the identifier of the object to select
    Returns:
      True on success
    """
    rhobj = rhutil.coercerhinoobject(object_id, True, True)
    rhobj.Select(True)
    scriptcontext.doc.Views.Redraw()
    return True


def SelectObjects( object_ids):
    """Selects one or more objects
    Parameters:
      object_ids = list of Guids identifying the objects to select
    Returns:
      number of selected objects
    """
    id = rhutil.coerceguid(object_ids, False)
    if id: object_ids = [id]
    rc = 0
    for id in object_ids:
        if SelectObject(id)==True: rc += 1
    return rc


def ShowObject(object_id):
    """Shows a previously hidden object. Hidden objects are not visible, cannot
    be snapped to and cannot be selected
    Parameters:
      object_id: String or Guid representing id of object to show
    Returns:
      True of False indicating success or failure
    """
    return ShowObjects(object_id)==1


def ShowObjects(object_ids):
    """Shows one or more objects. Hidden objects are not visible, cannot be
    snapped to and cannot be selected
    Parameters:
      object_ids: list of Strings or Guids representing ids of objects to show
    Returns:
      Number of objects shown
    """
    id = rhutil.coerceguid(object_ids, False)
    if id: object_ids = [id]
    rc = 0
    for id in object_ids:
        id = rhutil.coerceguid(id, True)
        if scriptcontext.doc.Objects.Show(id, False): rc += 1
    if rc: scriptcontext.doc.Views.Redraw()
    return rc


def TransformObject(object_id, matrix, copy=False):
    """Moves, scales, or rotates an object given a 4x4 transformation matrix.
    The matrix acts on the left.
    Parameters:
      object = The identifier of the object.
      matrix = The transformation matrix (4x4 array of numbers).
      copy [opt] = Copy the object.
    Returns:
      The identifier of the transformed object
      None if not successful, or on error
    """
    rc = TransformObjects(object_id, matrix, copy)
    if rc: return rc[0]
    return scriptcontext.errorhandler()

# this is also called by Copy, Scale, Mirror, Move, and Rotate functions defined above
def TransformObjects(object_ids, matrix, copy=False):
    """Moves, scales, or rotates a list of objects given a 4x4 transformation
    matrix. The matrix acts on the left.
    Parameters:
      object_ids = List of object identifiers.
      matrix = The transformation matrix (4x4 array of numbers).
      copy[opt] = Copy the objects
    Returns:
      List of ids identifying the newly transformed objects
    """
    xform = rhutil.coercexform(matrix, True)
    id = rhutil.coerceguid(object_ids, False)
    if id: object_ids = [id]
    rc = []
    for object_id in object_ids:
        object_id = rhutil.coerceguid(object_id, True)
        id = scriptcontext.doc.Objects.Transform(object_id, xform, not copy)
        if id!=System.Guid.Empty: rc.append(id)
    if rc: scriptcontext.doc.Views.Redraw()
    return rc


def UnlockObject(object_id):
    """Unlocks an object. Locked objects are visible, and can be snapped to,
    but they cannot be selected.
    Parameters:
      object_id: The identifier of an object
    Returns:
      True or False indicating success or failure
    """
    return UnlockObjects(object_id)==1


def UnlockObjects(object_ids):
    """Unlocks one or more objects. Locked objects are visible, and can be
    snapped to, but they cannot be selected.
    Parameters:
      object_ids: The identifiers of objects
    Returns:
      number of objects unlocked
    """
    id = rhutil.coerceguid(object_ids, False)
    if id: object_ids = [id]
    rc = 0
    for id in object_ids:
        id = rhutil.coerceguid(id, True)
        if scriptcontext.doc.Objects.Unlock(id, False): rc += 1
    if rc: scriptcontext.doc.Views.Redraw()
    return rc


def UnselectObject(object_id):
    """Unselects a single selected object
    Parameters:
      object_id: String or Guid representing id of object to unselect
    Returns:
      True of False indicating success or failure
    """
    return UnselectObjects(object_id)==1


def UnselectObjects(object_ids):
    """Unselects one or more selected objects.
    Parameters:
      object_ids = identifiers of the objects to unselect.
    Returns:
      The number of objects unselected
    """
    id = rhutil.coerceguid(object_ids, False)
    if id: object_ids = [id]
    count = len(object_ids)
    for id in object_ids:
        obj = rhutil.coercerhinoobject(id, True, True)
        obj.Select(False)
    if count: scriptcontext.doc.Views.Redraw()
    return count
