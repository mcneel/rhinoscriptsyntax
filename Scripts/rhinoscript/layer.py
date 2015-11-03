import Rhino.DocObjects.Layer
import scriptcontext
import utility as rhutil
import System.Guid


def __getlayer(name_or_id, raise_if_missing):
    if not name_or_id: raise TypeError("Parameter must be a string or Guid")
    id = rhutil.coerceguid(name_or_id)
    if id: name_or_id = id
    else:
        layer = scriptcontext.doc.Layers.FindByFullPath(name_or_id, True)
        if layer>=0: return scriptcontext.doc.Layers[layer]
    layer = scriptcontext.doc.Layers.Find(name_or_id, True)
    if layer>=0: return scriptcontext.doc.Layers[layer]
    if raise_if_missing: raise ValueError("%s does not exist in LayerTable" % name_or_id)


def AddLayer(name=None, color=None, visible=True, locked=False, parent=None):
    """Add a new layer to the document
    Parameters:
      name[opt]: The name of the new layer. If omitted, Rhino automatically
          generates the layer name.
      color[opt]: A Red-Green-Blue color value or System.Drawing.Color. If
          omitted, the color Black is assigned.
      visible[opt]: layer's visibility
      locked[opt]: layer's locked state
      parent[opt]: name of the new layer's parent layer. If omitted, the new
          layer will not have a parent layer.
    Returns:
      The full name of the new layer if successful.
    Example:
      import rhinoscriptsyntax as rs
      from System.Drawing import Color
      print "New layer:", rs.AddLayer()
      print "New layer:", rs.AddLayer("MyLayer1")
      print "New layer:", rs.AddLayer("MyLayer2", Color.DarkSeaGreen)
      print "New layer:", rs.AddLayer("MyLayer3", Color.Cornsilk)
      print "New layer:", rs.AddLayer("MyLayer4",parent="MyLayer3")
    See Also:
      CurrentLayer
      DeleteLayer
      RenameLayer
    """
    names = ['']
    if name:
      if not isinstance(name, str): name = str(name)
      names = [n for n in name.split("::") if name]
      
    last_parent_index = -1
    last_parent = None
    for idx, name in enumerate(names):
      layer = Rhino.DocObjects.Layer.GetDefaultLayerProperties()

      if idx is 0:
        if parent:
          last_parent = __getlayer(parent, True)
      else:
        if last_parent_index <> -1:
          last_parent = scriptcontext.doc.Layers[last_parent_index]

      if last_parent:
        layer.ParentLayerId = last_parent.Id
      if name:
        layer.Name = name
        
      color = rhutil.coercecolor(color)
      if color: layer.Color = color
      layer.IsVisible = visible
      layer.IsLocked = locked
    
      last_parent_index = scriptcontext.doc.Layers.Add(layer)
      if last_parent_index == -1:
        full_path = layer.Name
        if last_parent:
            full_path = last_parent.FullPath + "::" + full_path
        last_parent_index = scriptcontext.doc.Layers.FindByFullPath(full_path, True)
    return scriptcontext.doc.Layers[last_parent_index].FullPath

def CurrentLayer(layer=None):
    """Returns or changes the current layer
    Parameters:
      layer[opt] = the name or Guid of an existing layer to make current
    Returns:
      If a layer name is not specified, the full name of the current layer
      If a layer name is specified, the full name of the previous current layer
    Example:
      import rhinoscriptsyntax as rs
      rs.AddLayer("MyLayer")
      rs.CurrentLayer("MyLayer")
    See Also:
      AddLayer
      DeleteLayer
      RenameLayer
    """
    rc = scriptcontext.doc.Layers.CurrentLayer.FullPath
    if layer:
        layer = __getlayer(layer, True)
        scriptcontext.doc.Layers.SetCurrentLayerIndex(layer.LayerIndex, True)
    return rc


def DeleteLayer(layer):
    """Removes an existing layer from the document. The layer to be removed
    cannot be the current layer. Unlike the PurgeLayer method, the layer must
    be empty, or contain no objects, before it can be removed. Any layers that
    are children of the specified layer will also be removed if they are also
    empty.
    Parameters:
      layer = the name or id of an existing empty layer
    Returns:
      True or False indicating success or failure
    Example:
      import rhinoscriptsyntax as rs
      layer = rs.GetString("Layer to remove")
      if layer: rs.DeleteLayer(layer)
    See Also:
      AddLayer
      CurrentLayer
      PurgeLayer
      RenameLayer
    """
    layer = __getlayer(layer, True)
    return scriptcontext.doc.Layers.Delete( layer.LayerIndex, True)


def ExpandLayer( layer, expand ):
    """Expands a layer. Expanded layers can be viewed in Rhino's layer dialog
    Parameters:
      layer = name of the layer to expand
      expand = True to expand, False to collapse
    Returns:
      True or False indicating success or failure
    Example:
      import rhinoscriptsyntax as rs
      if rs.IsLayerExpanded("Default"):
      rs.ExpandLayer( "Default", False )
    See Also:
      IsLayerExpanded
    """
    layer = __getlayer(layer, True)
    if layer.IsExpanded==expand: return True
    layer.IsExpanded = expand
    return scriptcontext.doc.Layers.Modify(layer, layer.LayerIndex, True)


def IsLayer(layer):
    """Verifies the existance of a layer in the document
    Parameters:
      layer = the name or id of a layer to search for
    Returns:
      True on success otherwise False
    Example:
      import rhinoscriptsyntax as rs
      layer = rs.GetString("Layer name")
      if rs.IsLayer(layer):
      print "The layer exists."
      else:
      print "The layer does not exist."
    See Also:
      IsLayerChangeable
      IsLayerEmpty
      IsLayerLocked
      IsLayerOn
      IsLayerReference
      IsLayerSelectable
      IsLayerVisible
    """
    layer = __getlayer(layer, False)
    return layer is not None


def IsLayerChangeable(layer):
    """Verifies that the objects on a layer can be changed (normal)
    Parameters:
      layer = the name or id of an existing layer
    Returns:
      True on success otherwise False
    Example:
      import rhinoscriptsyntax as rs
      layer = rs.GetString("Layer name")
      if rs.IsLayer(layer):
      if rs.IsLayerChangeable(layer): print "The layer is changeable."
      else:print "The layer is not changeable."
      else:
      print "The layer does not exist."
    See Also:
      IsLayer
      IsLayerEmpty
      IsLayerLocked
      IsLayerOn
      IsLayerReference
      IsLayerSelectable
      IsLayerVisible
    """
    layer = __getlayer(layer, True)
    rc = layer.IsVisible and not layer.IsLocked
    return rc


def IsLayerChildOf(layer, test):
    """Verifies that a layer is a child of another layer
    Parameters:
      layer = the name or id of the layer to test against
      test = the name or id to the layer to test
    Returns:
      True on success otherwise False
    Example:
      import rhinoscriptsyntax as rs
      rs.AddLayer("MyLayer1")
      rs.AddLayer("MyLayer2", parent="MyLayer1")
      rs.AddLayer("MyLayer3", parent="MyLayer2")
      rs.MessageBox( rs.IsLayerChildOf("MyLayer1", "MyLayer3") )
    See Also:
      IsLayerParentOf
    """
    layer = __getlayer(layer, True)
    test = __getlayer(test, True)
    return test.IsChildOf(layer)


def IsLayerCurrent(layer):
    """Verifies that a layer is the current layer
    Parameters:
      layer the name or id of an existing layer
    Returns:
      True on success otherwise False
    Example:
      import rhinoscriptsyntax as rs
      layer = rs.GetString("Layer name")
      if rs.IsLayer(layer):
      if rs.IsLayerCurrent(layer):print "The layer is current."
      else: print "The layer is not current."
      else:
      print "The layer does not exist."
    See Also:
      IsLayer
      IsLayerEmpty
      IsLayerLocked
      IsLayerOn
      IsLayerReference
      IsLayerSelectable
      IsLayerVisible
    """
    layer = __getlayer(layer, True)
    return layer.LayerIndex == scriptcontext.doc.Layers.CurrentLayerIndex


def IsLayerEmpty(layer):
    """Verifies that an existing layer is empty, or contains no objects
    Parameters:
      layer the name or id of an existing layer
    Returns:
      True on success otherwise False
    Example:
      import rhinoscriptsyntax as rs
      layer = rs.GetString("Layer name")
      if rs.IsLayer(layer):
      if rs.IsLayerEmpty(layer):print "The layer is empty."
      else: print "The layer is not empty."
      else:
      print "The layer does not exist."
    See Also:
      IsLayerChangeable
      IsLayerLocked
      IsLayerOn
      IsLayerReference
      IsLayerSelectable
      IsLayerVisible
    """
    layer = __getlayer(layer, True)
    rhobjs = scriptcontext.doc.Objects.FindByLayer(layer)
    if not rhobjs: return True
    return False


def IsLayerExpanded(layer):
    """Verifies that a layer is expanded. Expanded layers can be viewed in
    Rhino's layer dialog
    Parameters:
      layer the name or id of an existing layer
    Returns:
      True on success otherwise False
    Example:
      import rhinoscriptsyntax as rs
      if rs.IsLayerExpanded("Default"):
      rs.ExpandLayer( "Default", False )
    See Also:
      ExpandLayer
    """
    layer = __getlayer(layer, True)
    return layer.IsExpanded   


def IsLayerLocked(layer):
    """Verifies that a layer is locked.
    Parameters:
      layer the name or id of an existing layer
    Returns:
      True on success otherwise False
    Example:
      import rhinoscriptsyntax as rs
      layer = rs.GetString("Layer name")
      if rs.IsLayer(layer):
      if rs.IsLayerLocked(layer): print "The layer is locked."
      else: print "The layer is not locked."
      else:
      print "The layer does not exist."
    See Also:
      IsLayer
      IsLayerChangeable
      IsLayerEmpty
      IsLayerOn
      IsLayerReference
      IsLayerSelectable
      IsLayerVisible
    """
    layer = __getlayer(layer, True)
    return layer.IsLocked


def IsLayerOn(layer):
    """Verifies that a layer is on.
    Parameters:
      layer the name or id of an existing layer
    Returns:
      True on success otherwise False
    Example:
      import rhinoscriptsyntax as rs
      layer = rs.GetString("Layer name")
      if rs.IsLayer(layer):
      if rs.IsLayerOn(layer): print "The layer is on."
      else: print "The layer is not on."
      else:
      print "The layer does not exist."
    See Also:
      IsLayer
      IsLayerChangeable
      IsLayerEmpty
      IsLayerLocked
      IsLayerReference
      IsLayerSelectable
      IsLayerVisible
    """
    layer = __getlayer(layer, True)
    return layer.IsVisible


def IsLayerSelectable(layer):
    """Verifies that an existing layer is selectable (normal and reference)
    Parameters:
      layer the name or id of an existing layer
    Returns:
      True on success otherwise False
    Example:
      import rhinoscriptsyntax as rs
      layer = rs.GetString("Layer name")
      if rs.IsLayer(layer):
      if rs.IsLayerSelectable(layer): print "The layer is selectable."
      else: print "The layer is not selectable."
      else:
      print "The layer does not exist."
    See Also:
      IsLayer
      IsLayerChangeable
      IsLayerEmpty
      IsLayerLocked
      IsLayerOn
      IsLayerReference
      IsLayerVisible
    """
    layer = __getlayer(layer, True)
    return layer.IsVisible and not layer.IsLocked


def IsLayerParentOf(layer, test):
    """Verifies that a layer is a parent of another layer
    Parameters:
      layer = the name or id of the layer to test against
      test = the name or id to the layer to test
    Returns:
      True on success otherwise False
    Example:
      import rhinoscriptsyntax as rs
      rs.AddLayer("MyLayer1")
      rs.AddLayer("MyLayer2", parent="MyLayer1")
      rs.AddLayer("MyLayer3", parent="MyLayer2")
      rs.MessageBox( rs.IsLayerParentOf("MyLayer3", "MyLayer1") )
    See Also:
      IsLayerChildOf
    """
    layer = __getlayer(layer, True)
    test = __getlayer(test, True)
    return test.IsParentOf(layer)


def IsLayerReference(layer):
    """Verifies that a layer is from a reference file.
    Parameters:
      layer the name or id of an existing layer
    Returns:
      True on success otherwise False
    Example:
      import rhinoscriptsyntax as rs
      layer = rs.GetString("Layer name")
      if rs.IsLayer(layer):
      if rs.IsLayerReference(layer):print "The layer is a reference layer."
      else:print "The layer is not a reference layer."
      else:
      print "The layer does not exist."
    See Also:
      IsLayer
      IsLayerChangeable
      IsLayerEmpty
      IsLayerLocked
      IsLayerOn
      IsLayerSelectable
      IsLayerVisible
    """
    layer = __getlayer(layer, True)
    return layer.IsReference


def IsLayerVisible(layer):
    """Verifies that a layer is visible (normal, locked, and reference)
    Parameters:
      layer the name or id of an existing layer
    Returns:
      True on success otherwise False
    Example:
      import rhinoscriptsyntax as rs
      layer = rs.GetString("Layer name")
      if rs.IsLayer(layer):
      if rs.IsLayerVisible(layer): print "The layer is visible"
      else: print "The layer is not visible"
      else:
      print "The layer does not exist."
    See Also:
      IsLayer
      IsLayerChangeable
      IsLayerEmpty
      IsLayerLocked
      IsLayerOn
      IsLayerReference
      IsLayerSelectable
    """
    layer = __getlayer(layer, True)
    return layer.IsVisible


def LayerChildCount(layer):
    """Returns the number of immediate child layers of a layer
    Parameters:
      layer the name or id of an existing layer
    Returns:
      the number of immediate child layers if successful
    Example:
      import rhinoscriptsyntax as rs
      children = rs.LayerChildCount("Default")
      if children: rs.ExpandLayer("Default", True)
    See Also:
      LayerChildren
    """
    layer = __getlayer(layer, True)
    children = layer.GetChildren()
    if children: return len(children)
    return 0


def LayerChildren(layer):
    """Returns the immediate child layers of a layer
    Parameters:
      layer = the name or id of an existing layer
    Returns:
      List of children
    Example:
      import rhinoscriptsyntax as rs
      children = rs.LayerChildren("Default")
      if children:
      for child in children: print child
    See Also:
      LayerChildCount
      ParentLayer
    """
    layer = __getlayer(layer, True)
    children = layer.GetChildren()
    if children: return [child.FullPath for child in children]
    return [] #empty list


def LayerColor(layer, color=None):
    """Returns or changes the color of a layer.
    Parameters:
      layer = name or id of an existing layer
      color [opt] = the new color value. If omitted, the current layer color is returned.
    Returns:
      If a color value is not specified, the current color value on success
      If a color value is specified, the previous color value on success
    Example:
      import rhinoscriptsyntax as rs
      import random
      from System.Drawing import Color
      
      def randomcolor():
      red = int(255*random.random())
      green = int(255*random.random())
      blue = int(255*random.random())
      return Color.FromArgb(red,green,blue)
      
      layerNames = rs.LayerNames()
      if layerNames:
      for name in layerNames: rs.LayerColor(name, randomcolor())
    See Also:
      
    """
    layer = __getlayer(layer, True)
    rc = layer.Color
    if color:
        color = rhutil.coercecolor(color)
        layer.Color = color
        if scriptcontext.doc.Layers.Modify(layer, layer.LayerIndex, False):
            scriptcontext.doc.Views.Redraw()
    return rc


def LayerCount():
    """Returns the number of layers in the document
    Parameters:
      None
    Returns:
      the number of layers in the document
    Example:
      import rhinoscriptsyntax as rs
      count = rs.LayerCount()
      print "There are", count, "layers."
    See Also:
      LayerNames
    """
    return scriptcontext.doc.Layers.ActiveCount


def LayerIds():
    """Return identifiers of all layers in the document
    Parameters:
      None
    Returns:
      the identifiers of all layers in the document
    Example:
      import rhinoscriptsyntax as rs
      layers = rs.LayerIds()
      for layer in layers: print layer
    See Also:
      LayerCount
      LayerNames
    """
    return [layer.Id for layer in scriptcontext.doc.Layers]


def LayerLinetype(layer, linetype=None):
    """Returns or changes the linetype of a layer
    Parameters:
      layer = name of an existing layer
      linetype[opt] = name of a linetype
    Returns:
      If linetype is not specified, name of the current linetype
      If linetype is specified, name of the previous linetype
    Example:
      import rhinoscriptsyntax as rs
      layers = rs.LayerNames()
      if layers:
      for layer in layers:
      if rs.LayerLinetype(layer)!="Continuous":
      rs.LayerLinetype(layer,"Continuous")
    See Also:
      LayerPrintColor
      LayerPrintWidth
    """
    layer = __getlayer(layer, True)
    index = layer.LinetypeIndex
    rc = scriptcontext.doc.Linetypes[index].Name
    if linetype:
        if not isinstance(linetype, str): linetype = str(linetype)
        index = scriptcontext.doc.Linetypes.Find(linetype, True)
        if index==-1: return scriptcontext.errorhandler()
        layer.LinetypeIndex = index
        layer.CommitChanges()
        scriptcontext.doc.Views.Redraw()
    return rc


def LayerLocked(layer, locked=None):
    """Returns or changes the locked mode of a layer
    Parameters:
      layer = name of an existing layer
      locked[opt] = new layer locked mode
    Returns:
      If locked is not specified, the current layer locked mode
      If locked is specified, the previous layer locked mode
    Example:
      import rhinoscriptsyntax as rs
      layers = rs.LayerNames()
      if layers:
      for layer in layers:
      if rs.LayerLocked(layer): rs.LayerLocked(layer, False)
    See Also:
      LayerVisible
    """
    layer = __getlayer(layer, True)
    rc = layer.IsLocked
    if locked!=None and locked!=rc:
        layer.IsLocked = locked
        layer.CommitChanges()
        scriptcontext.doc.Views.Redraw()
    return rc


def LayerMaterialIndex(layer,index=None):
    """Returns or changes the material index of a layer. A material index of -1
    indicates that no material has been assigned to the layer. Thus, the layer
    will use Rhino's default layer material
    Parameters:
      layer = name of existing layer
      index [opt] = the new material index
    Returns:
      a zero-based material index if successful
    Example:
      import rhinoscriptsyntax as rs
      index = rs.LayerMaterialIndex("Default")
      if index is not None:
      if index==-1:
      print "The default layer does not have a material assigned."
      else:
      print "The default layer has a material assigned."
    See Also:
      
    """
    layer = __getlayer(layer, True)
    rc = layer.RenderMaterialIndex
    if index is not None and index>=-1:
        layer.RenderMaterialIndex = index
        layer.CommitChanges()
        scriptcontext.doc.Views.Redraw()
    return rc


def LayerId(layer):
    """Returns the identifier of a layer given the layer's name.
    Parameters:
      layer = name of existing layer
    Returns:
      String - The layer's identifier if successful.
      Null - If not successful, or on error.
    Example:
      import rhinoscriptsyntax as  rs
      id = rs.LayerId('Layer 01')
    See Also:
      LayerName
    """
    idx = scriptcontext.doc.Layers.FindByFullPath(layer, True)
    return str(scriptcontext.doc.Layers[idx].Id) if idx >= 0 else None


def LayerName(layer_id, fullpath=True):
    """Return the name of a layer given it's identifier
    Parameters:
      layer_id = layer identifier
      fullpath [opt] = return the full path name or short name
    Returns:
      the layer's name if successful otherwise None
    Example:
      import rhinoscriptsyntax as rs
      layers = rs.LayerIds()
      if layers:
      for layer in layers: print rs.LayerName(layer)
    See Also:
      LayerId
    """
    layer = __getlayer(layer_id, True)
    if fullpath: return layer.FullPath
    return layer.Name


def LayerNames(sort=False):
    """Returns the names of all layers in the document.
    Parameters:
      sort [opt] = return a sorted list of the layer names
    Returns:
      list of strings
    Example:
      import rhinoscriptsyntax as rs
      layers = rs.LayerNames()
      if layers:
    See Also:
      LayerCount
    """
    rc = []
    for layer in scriptcontext.doc.Layers:
        if not layer.IsDeleted: rc.append(layer.FullPath)
    if sort: rc.sort()
    return rc


def LayerOrder(layer):
    """Returns the current display order index of a layer as displayed in Rhino's
    layer dialog box. A display order index of -1 indicates that the current
    layer dialog filter does not allow the layer to appear in the layer list
    Parameters:
      layer = name of existing layer
    Returns:
      0 based index
    Example:
      import rhinoscriptsyntax as rs
      index = rs.LayerOrder("Default")
      if index is not None:
      if index==-1: print "The layer does not display in the Layer dialog."
      else: print "The layer does display in the Layer dialog."
    See Also:
      
    """
    layer = __getlayer(layer, True)
    return layer.SortIndex


def LayerPrintColor(layer, color=None):
    """Returns or changes the print color of a layer. Layer print colors are
    represented as RGB colors.
    Parameters:
      layer = name of existing layer
      color[opt] = new print color
    Returns:
      if color is not specified, the current layer print color
      if color is specified, the previous layer print color
      None on error
    Example:
      import rhinoscriptsyntax as rs
      layers = rs.LayerNames()
      if layers:
      for layer in layers:
      black = rs.coercecolor((0,0,0))
      if rs.LayerPrintColor(layer)!=black:
      rs.LayerPrintColor(layer, black)
    See Also:
      LayerLinetype
      LayerPrintWidth
    """
    layer = __getlayer(layer, True)
    rc = layer.PlotColor
    if color:
        color = rhutil.coercecolor(color)
        layer.PlotColor = color
        layer.CommitChanges()
        scriptcontext.doc.Views.Redraw()
    return rc


def LayerPrintWidth(layer, width=None):
    """Returns or changes the print width of a layer. Print width is specified
    in millimeters. A print width of 0.0 denotes the "default" print width.
    Parameters:
      layer = name of existing layer
      width[opt] = new print width
    Returns:
      if width is not specified, the current layer print width
      if width is specified, the previous layer print width
    Example:
      import rhinoscriptsyntax as rs
      layers = rs.LayerNames()
      if layers:
      for layer in layers:
      if rs.LayerPrintWidth(layer)!=0:
      rs.LayerPrintWidth(layer, 0)
    See Also:
      LayerLinetype
      LayerPrintColor
    """
    layer = __getlayer(layer, True)
    rc = layer.PlotWeight
    if width is not None and width!=rc:
        layer.PlotWeight = width
        layer.CommitChanges()
        scriptcontext.doc.Views.Redraw()
    return rc


def LayerVisible(layer, visible=None, force_visible=False):
    """Returns or changes the visible property of a layer.
    Parameters:
      layer = name of existing layer
      visible[opt] = new visible state
    Returns:
      if visible is not specified, the current layer visibility
      if visible is specified, the previous layer visibility
    Example:
      import rhinoscriptsyntax as rs
      layers = rs.LayerNames()
      if layers:
      for layer in layers:
      if rs.LayerVisible(layer)==False:
      rs.LayerVisible(layer,True)
    See Also:
      LayerLocked
    """
    layer = __getlayer(layer, True)
    rc = layer.IsVisible
    if visible is not None and visible!=rc:
        if visible and force_visible:
            scriptcontext.doc.Layers.ForceLayerVisible(layer.Id)
        else:
            layer.IsVisible = visible
            layer.CommitChanges()
        scriptcontext.doc.Views.Redraw()
    return rc


def ParentLayer(layer, parent=None):
    """Return or modify the parent layer of a layer
    Parameters:
      layer = name of an existing layer
      parent[opt] = name of new parent layer. To remove the parent layer,
        thus making a root-level layer, specify an empty string
    Returns:
      If parent is not specified, the name of the current parent layer
      If parent is specified, the name of the previous parent layer
      None if the layer does not have a parent
    Example:
      import rhinoscriptsyntax as rs
      layers = rs.LayerNames()
      for layer in layers:
      parent = rs.ParentLayer(layer)
      print "Layer:", layer, ", Parent:", parent
    See Also:
      LayerChildren
    """
    layer = __getlayer(layer, True)
    parent_id = layer.ParentLayerId
    oldparent = None
    if parent_id!=System.Guid.Empty:
        oldparentlayer = scriptcontext.doc.Layers.Find(parent_id, False)
        if oldparentlayer is not None:
            oldparentlayer = scriptcontext.doc.Layers[oldparentlayer]
            oldparent = oldparentlayer.FullPath
    if parent is None: return oldparent
    if parent=="":
        layer.ParentLayerId = System.Guid.Empty
    else:
        parent = __getlayer(parent, True)
        layer.ParentLayerId = parent.Id
    layer.CommitChanges()
    return oldparent


def PurgeLayer(layer):
    """Removes an existing layer from the document. The layer will be removed
    even if it contains geometry objects. The layer to be removed cannot be the
    current layer
    empty.
    Parameters:
      layer = the name or id of an existing empty layer
    Returns:
      True or False indicating success or failure
    Example:
      import rhinoscriptsyntax as rs
      layer = rs.GetString("Layer to purge")
      if layer: rs.PurgeLayer(layer)
    See Also:
      AddLayer
      CurrentLayer
      DeleteLayer
      RenameLayer
    """
    layer = __getlayer(layer, True)
    rc = scriptcontext.doc.Layers.Purge( layer.LayerIndex, True)
    scriptcontext.doc.Views.Redraw()
    return rc

def RenameLayer(oldname, newname):
    """Renames an existing layer
    Parameters:
      oldname = original layer name
      newname = new layer name
    Returns: 
      The new layer name if successful otherwise None
    Example:
      import rhinoscriptsyntax as rs
      oldname = rs.GetString("Old layer name")
      if oldname:
      newname = rs.GetString("New layer name")
      if newname: rs.RenameLayer(oldname, newname)
    See Also:
      AddLayer
      CurrentLayer
      DeleteLayer
    """
    if oldname and newname:
        layer = __getlayer(oldname, True)
        layer.Name = newname
        layer.CommitChanges()
        return newname