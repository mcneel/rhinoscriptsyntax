import Rhino.DocObjects.Layer
import scriptcontext
import utility as rhutil


def __getlayer(name_or_id):
    if not name_or_id: return None
    id = rhutil.coerceguid(name_or_id)
    if id: name_or_id = id
    layer = scriptcontext.doc.Layers.Find(name_or_id, True)
    if layer>=0: return scriptcontext.doc.Layers[layer]


def AddLayer(name=None, color=None, visible=True, locked=False, parent=None):
    """
    Add a new layer to the document
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
      The name of the new layer if successful.
      None if not successful or on error
    """
    layer = Rhino.DocObjects.Layer.GetDefaultLayerProperties()
    if name: layer.Name = str(name)
    color = rhutil.coercecolor(color)
    if color: layer.Color = color
    layer.IsVisible = visible
    layer.IsLocked = locked
    if parent:
        parentIndex = scriptcontext.doc.Layers.Find(parent, True)
        if parentIndex>=0:
            parentId = scriptcontext.doc.Layers[parentIndex].Id
            layer.ParentLayerId = parentId
    index = scriptcontext.doc.Layers.Add(layer)
    return scriptcontext.doc.Layers[index].Name


def CurrentLayer(layer=None):
    """
    Returns or changes the current layer
    Parameters:
      layer[opt] = the name or Guid of an existing layer to make current
    Returns:
      If a layer name is not specified, the name of the current layer
      If a layer name is specified, the name of the previous current layer
      None if not successful or on error
    """
    rc = scriptcontext.doc.Layers.CurrentLayer.Name
    layer = __getlayer(layer)
    if layer:
        scriptcontext.doc.Layers.SetCurrentLayerIndex(layer.LayerIndex, True)
    return rc


def DeleteLayer(layer):
    """
    Removes an existing layer from the document. The layer to be removed cannot
    be the current layer. Unlike the PurgeLayer method, the layer must be empty,
    or contain no objects, before it can be removed. Any layers that are
    children of the specified layer will also be removed if they are also empty.
    Parameters:
      layer = the name or id of an existing empty layer
    Returns:
      True or False indicating success or failure
    """
    layer = __getlayer(layer)
    if not layer: return False
    rc = scriptcontext.doc.Layers.Delete( layer.LayerIndex, True)
    return rc


def ExpandLayer( layer, expand ):
    """
    Expands a layer. Expanded layers can be viewed in Rhino's layer dialog
    Parameters:
      layer = name of the layer to expand
      expand = True to expand, False to collapse
    Returns:
      True or False indicating success or failure
    """
    layer = __getlayer(layer)
    if layer is None or layer.IsExpanded==expand: return False
    layer.IsExpanded = expand
    return scriptcontext.doc.Layers.Modify(layer, layer.LayerIndex, True)


def IsLayer(layer):
    """
    Verifies the existance of a layer in the document
    Parameter:
      layer = the name or id of a layer to search for
    """
    layer = __getlayer(layer)
    return layer is not None


def IsLayerChangeable(layer):
    "Verifies that the objects on a layer can be changed (normal)"
    layer = __getlayer(layer)
    if layer is None: return scriptcontext.errorhandler()
    rc = layer.IsVisible and not layer.IsLocked
    return rc


def IsLayerChildOf(layer, test):
    """
    Verifies that a layer is a child of another layer
    Parameters:
      layer = the name or id of the layer to test against
      test = the name or id to the layer to test
    """
    layer = __getlayer(layer)
    test = __getlayer(test)
    if layer is None or test is None: return scriptcontext.errorhandler()
    return test.IsChildOf(layer)


def IsLayerCurrent(layer):
    "Verifies that a layer is the current layer"
    layer = __getlayer(layer)
    if layer is None: return scriptcontext.errorhandler()
    return layer.LayerIndex == scriptcontext.doc.Layers.CurrentLayerIndex


def IsLayerEmpty(layer):
    "Verifies that an existing layer is empty, or contains no objects"
    layer = __getlayer(layer)
    if layer is None: return scriptcontext.errorhandler()
    rhobjs = scriptcontext.doc.Objects.FindByLayer(layer)
    if rhobjs is None or len(rhobjs)<1: return True
    return False


def IsLayerExpanded(layer):
    """
    Verifies that a layer is expanded. Expanded layers can be viewed in
    Rhino's layer dialog
    """
    layer = __getlayer(layer)
    if layer is None: return scriptcontext.errorhandler()
    return layer.IsExpanded   


def IsLayerLocked(layer):
    "Verifies that a layer is locked."
    layer = __getlayer(layer)
    if layer is None: return scriptcontext.errorhandler()
    return layer.IsLocked


def IsLayerOn(layer):
    "Verifies that a layer is on."
    layer = __getlayer(layer)
    if layer is None: return scriptcontext.errorhandler()
    return layer.IsVisible


def IsLayerSelectable(layer):
    "Verifies that an existing layer is selectable (normal and reference)"
    layer = __getlayer(layer)
    if layer is None: return scriptcontext.errorhandler()
    rc = layer.IsVisible and not layer.IsLocked
    return rc


def IsLayerParentOf(layer, test):
    """
    Verifies that a layer is a parent of another layer
    Parameters:
      layer = the name or id of the layer to test against
      test = the name or id to the layer to test
    """
    layer = __getlayer(layer)
    test = __getlayer(test)
    if layer is None or test is None: return scriptcontext.errorhandler()
    return test.IsParentOf(layer)


def IsLayerReference(layer):
    "Verifies that a layer is from a reference file."
    layer = __getlayer(layer)
    if layer is None: return scriptcontext.errorhandler()
    return layer.IsReference


def IsLayerVisible(layer):
    "Verifies that a layer is visible (normal, locked, and reference)"
    layer = __getlayer(layer)
    if layer is None: return scriptcontext.errorhandler()
    return layer.IsVisible


def LayerChildCount(layer):
    "Returns the number of immediate child layers of a layer"
    layer = __getlayer(layer)
    if layer is None: return scriptcontext.errorhandler()
    children = layer.GetChildren()
    if children is None: return 0
    return children.Length


def LayerChildren(layer):
    """
    Returns the immediate child layers of a layer
    Parameters:
      layer = the name or id of an existing layer
    Returns:
      List of children if the layer has children
      None on error or if the layer does not have children
    """
    layer = __getlayer(layer)
    if layer is None: return scriptcontext.errorhandler()
    children = layer.GetChildren()
    if children: return list(children)
    return scriptcontext.errorhandler()


def LayerColor(layer, color=None):
    """
    Returns or changes the color of a layer.
    Parameters:
      layer = name or id of an existing layer
      color [opt] = the new color value. If omitted, the current layer color is returned.
    Returns:
      If a color value is not specified, the current color value on success
      If a color value is specified, the previous color value on success
      None if not successful, or on error.
    """
    layer = __getlayer(layer)
    if layer is None: return scriptcontext.errorhandler()
    rc = layer.Color
    color = rhutil.coercecolor(color)
    if color:
        layer.Color = color
        if scriptcontext.doc.Layers.Modify(layer, layer.LayerIndex, False):
            scriptcontext.doc.Views.Redraw()
    return rc


def LayerCount():
    "Returns the number of layers in the document"
    return scriptcontext.doc.Layers.ActiveCount


def LayerLinetype(layer, linetype=None):
    """
    Returns or changes the linetype of a layer
    Parameters:
      layer = name of an existing layer
      linetype[opt] = name of a linetype
    Returns:
      If linetype is not specified, name of the current linetype
      If linetype is specified, name of the previous linetype
      None on error
    """
    layer = __getlayer(layer)
    if layer is None: return scriptcontext.errorhandler()
    index = layer.LinetypeIndex
    rc = scriptcontext.doc.Linetypes[index].Name
    if linetype:
        index = scriptcontext.doc.Linetypes.Find(str(linetype), True)
        if index==-1: return scriptcontext.errorhandler()
        layer.LinetypeIndex = index
        layer.CommitChanges()
        scriptcontext.doc.Views.Redraw()
    return rc


def LayerLocked(layer, locked=None):
    """
    Returns or changes the locked mode of a layer
    Parameters:
      layer = name of an existing layer
      locked[opt] = new layer locked mode
    Returns:
      If locked is not specified, the current layer locked mode
      If locked is specified, the previous layer locked mode
      None on error
    """
    layer = __getlayer(layer)
    if layer is None: return scriptcontext.errorhandler()
    rc = layer.IsLocked
    if locked and locked!=rc:
        layer.IsLocked = locked
        layer.CommitChanges()
        scriptcontext.doc.Views.Redraw()
    return rc


def LayerMaterialIndex( layer ):
    """
    Returns the material index of a layer. A material index of -1 indeicates
    that no material has been assigned to the layer. Thus, the layer will use
    Rhino's default layer material
    Parameters:
      layer = name of existing layer
    """
    layer = __getlayer(layer)
    if layer is None: return scriptcontext.errorhandler()
    return layer.RenderMaterialIndex


def LayerNames(sort=False):
    """
    Returns the names of all layers in the document.
    Parameters:
      sort [opt] = return a sorted list of the layer names
    Returns
      list of strings if successful
      None if not successful
    """
    count = scriptcontext.doc.Layers.Count
    if count<1: return scriptcontext.errorhandler()
    rc = []
    table = scriptcontext.doc.Layers
    for i in xrange(count):
        layer = table[i]
        if not layer.IsDeleted: rc.append(layer.Name)
    if sort: rc.sort()
    return rc

def LayerOrder(layer):
    """
    Returns the current display order index of a layer as displayed in Rhino's
    layer dialog box. A display order index of -1 indicates that the current
    layer dialog filter does not allow the layer to appear in the layer list
    Parameters:
      layer = name of existing layer
    Returns:
      0 based index
      None on error    
    """
    layer = __getlayer(layer)
    if layer is None: return scriptcontext.errorhandler()
    return layer.SortIndex


def LayerPrintColor(layer, color=None):
    """
    Returns or changes the print color of a layer. Layer print colors are
    represented as RGB colors.
    Parameters:
      layer = name of existing layer
      color[opt] = new print color
    Returns:
      if color is not specified, the current layer print color
      if color is specified, the previous layer print color
      None on error
    """
    layer = __getlayer(layer)
    if layer is None: return scriptcontext.errorhandler()
    rc = layer.PlotColor
    color = rhutil.coercecolor(color)
    if color:
        layer.PlotColor = color
        layer.CommitChanges()
        scriptcontext.doc.Views.Redraw()
    return rc


def LayerPrintWidth(layer, width=None):
    """
    Returns or changes the print width of a layer. Print width is specified in
    millimeters. A print width of 0.0 denotes the "default" print width.
    Parameters:
      layer = name of existing layer
      width[opt] = new print width
    Returns:
      if width is not specified, the current layer print width
      if width is specified, the previous layer print width
      None on error
    """
    layer = __getlayer(layer)
    if layer is None: return scriptcontext.errorhandler()
    rc = layer.PlotWeight
    if width is not None and width!=rc:
        layer.PlotWeight = width
        layer.CommitChanges()
        scriptcontext.doc.Views.Redraw()
    return rc


def LayerVisible(layer, visible=False):
    """
    Returns or changes the visible property of a layer.
    Parameters:
      layer = name of existing layer
      visible[opt] = new visible state
    Returns:
      if visible is not specified, the current layer visibility
      if visible is specified, the previous layer visibility
      None on error
    """
    layer = __getlayer(layer)
    if layer is None: return scriptcontext.errorhandler()
    rc = layer.IsVisible
    if visible is not None and visible!=rc:
        layer.IsVisible = visible
        layer.CommitChanges()
        scriptcontext.doc.Views.Redraw()
    return rc

