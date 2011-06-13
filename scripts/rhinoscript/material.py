import Rhino.DocObjects
import scriptcontext
import utility as rhutil
from layer import __getlayer


def AddMaterialToLayer(layer):
    """Add material to a layer and returns the new material's index. If the
    layer already has a material, then the layer's current material index is
    returned
    Parameters:
      layer = name of an existing layer.
    Returns:
      Material index of the layer if successful
      None if not successful or on error
    """
    layer = __getlayer(layer, True)
    if layer.RenderMaterialIndex>-1: return layer.RenderMaterialIndex
    material_index = scriptcontext.doc.Materials.AddMaterial()
    layer.RenderMaterialIndex = material_index
    if scriptcontext.doc.Layers.Modify( layer, layer.LayerIndex, True):
        scriptcontext.doc.Views.Redraw()
        return material_index
    return scriptcontext.errorhandler()


def AddMaterialToObject(object_id):
    """Adds material to an object and returns the new material's index. If the
    object already has a material, the the object's current material index is
    returned.
    Parameters:
      object_id = identifier of an object
    Returns:
      material index of the object
    """
    rhino_object = rhutil.coercerhinoobject(object_id, True, True)
    attr = rhino_object.Attributes
    if attr.MaterialSource!=Rhino.DocObjects.ObjectMaterialSource.MaterialFromObject:
        attr.MaterialSource = Rhino.DocObjects.ObjectMaterialSource.MaterialFromObject
        scriptcontext.doc.Objects.ModifyAttributes(rhino_object, attr, True)
        attr = rhino_object.Attributes
    material_index = attr.MaterialIndex
    if material_index>-1: return material_index
    material_index = scriptcontext.doc.Materials.AddMaterial()
    attr.MaterialIndex = material_index
    scriptcontext.doc.Objects.ModifyAttributes(rhino_object, attr, True)
    return material_index

    
def CopyMaterial(source_index, destination_index):
    """Copies definition of a source material to a destination material
    Parameters:
      source_index, destination_index = indices of materials to copy
    Returns:
      True or False indicating success or failure
    """
    if source_index==destination_index: return False
    source = scriptcontext.doc.Materials[source_index]
    if source is None: return False
    rc = scriptcontext.doc.Materials.Modify(source, destination_index, True)
    if rc: scriptcontext.doc.Views.Redraw()
    return rc


def IsMaterialDefault(material_index):
    """Verifies a material is a copy of Rhino's built-in "default" material.
    The default material is used by objects and layers that have not been
    assigned a material.
    Parameters:
      material_index = the zero-based material index
    Returns:
      True or False indicating success or failure
    """
    mat = scriptcontext.doc.Materials[material_index]
    return mat and mat.IsDefaultMaterial


def IsMaterialReference(material_index):
    """Verifies a material is referenced from another file
    Parameters:
      material_index = the zero-based material index
    Returns:
      True or False indicating success or failure
    """
    mat = scriptcontext.doc.Materials[material_index]
    return mat and mat.IsReference


def MatchMaterial(source, destination):
    """Copies the material definition from one material to one or more objects
    Parameters:
      source = source material index -or- identifier of the source object.
        The object must have a material assigned
      destination = indentifier(s) of the destination object(s)
    Returns:
      number of objects that were modified if successful
      None if not successful or on error
    """
    source_id = rhutil.coerceguid(source)
    source_mat = None
    if source_id:
        rhobj = rhutil.coercerhinoobject(source_id, True, True)
        source = rhobj.Attributes.MaterialIndex
    mat = scriptcontext.doc.Materials[source]
    if not mat: return scriptcontext.errorhandler()
    destination_id = rhutil.coerceguid(destination)
    if destination_id: destination = [destination]
    ids = [rhutil.coerceguid(d) for d in destination]
    rc = 0
    for id in ids:
        rhobj = scriptcontext.doc.Objects.Find(id)
        if rhobj:
            rhobj.Attributes.MaterialIndex = source
            rhobj.Attributes.MaterialSource = Rhino.DocObjects.ObjectMaterialSource.MaterialFromObject
            rhobj.CommitChanges()
            rc += 1
    if rc>0: scriptcontext.doc.Views.Redraw()
    return rc


def MaterialBump(material_index, filename=None):
    """Returns or modifies a material's bump bitmap filename
    Parameters:
      material_index = zero based material index
      filename[opt] = the bump bitmap filename
    Returns:
      if filename is not specified, the current bump bitmap filename
      if filename is specified, the previous bump bitmap filename
      None if not successful or on error
    """
    mat = scriptcontext.doc.Materials[material_index]
    if mat is None: return scriptcontext.errorhandler()
    texture = mat.GetBumpTexture()
    rc = texture.FileName if texture else ""
    if filename:
        mat.SetBumpTexture(filename)
        mat.CommitChanges()
        scriptcontext.doc.Views.Redraw()
    return rc


def MaterialColor(material_index, color=None):
    """Returns or modifies a material's diffuse color.
    Parameters:
      material_index = zero based material index
      color[opt] = the new color value
    Returns:
      if color is not specified, the current material color
      if color is specified, the previous material color
      None on error
    """
    mat = scriptcontext.doc.Materials[material_index]
    if mat is None: return scriptcontext.errorhandler()
    rc = mat.DiffuseColor
    color = rhutil.coercecolor(color)
    if color:
        mat.DiffuseColor = color
        mat.CommitChanges()
        scriptcontext.doc.Views.Redraw()
    return rc


def MaterialEnvironmentMap(material_index, filename=None):
    """Returns or modifies a material's environment bitmap filename.
    Parameters:
      material_index = zero based material index
      filename[opt] = the environment bitmap filename
    Returns:
      if filename is not specified, the current environment bitmap filename
      if filename is specified, the previous environment bitmap filename
      None if not successful or on error
    """
    mat = scriptcontext.doc.Materials[material_index]
    if mat is None: return scriptcontext.errorhandler()
    texture = mat.GetEnvironmentTexture()
    rc = texture.FileName if texture else ""
    if filename:
        mat.SetEnvironmentTexture(filename)
        mat.CommitChanges()
        scriptcontext.doc.Views.Redraw()
    return rc


def MaterialName(material_index, name=None):
    """Returns or modifies a material's user defined name
    Parameters:
      material_index = zero based material index
      name[opt] = the new name
    Returns:
      if name is not specified, the current material name
      if name is specified, the previous material name
      None on error
    """
    mat = scriptcontext.doc.Materials[material_index]
    if mat is None: return scriptcontext.errorhandler()
    rc = mat.Name
    if name:
        mat.Name = name
        mat.CommitChanges()
    return rc


def MaterialReflectiveColor(material_index, color=None):
    """Returns or modifies a material's reflective color.
    Parameters:
      material_index = zero based material index
      color[opt] = the new color value
    Returns:
      if color is not specified, the current material reflective color
      if color is specified, the previous material reflective color
      None on error
    """
    mat = scriptcontext.doc.Materials[material_index]
    if mat is None: return scriptcontext.errorhandler()
    rc = mat.ReflectionColor
    color = rhutil.coercecolor(color)
    if color:
        mat.ReflectionColor = color
        mat.CommitChanges()
        scriptcontext.doc.Views.Redraw()
    return rc


def MaterialShine(material_index, shine=None):
    """Returns or modifies a material's shine value
    Parameters:
      material_index = zero based material index
      shine[opt] = the new shine value. A material's shine value ranges from 0.0 to 255.0, with
        0.0 being matte and 255.0 being glossy
    Returns:
      if shine is not specified, the current material shine value
      if shine is specified, the previous material shine value
      None on error
    """
    mat = scriptcontext.doc.Materials[material_index]
    if mat is None: return scriptcontext.errorhandler()
    rc = mat.Shine
    if shine:
        mat.Shine = shine
        mat.CommitChanges()
        scriptcontext.doc.Views.Redraw()
    return rc


def MaterialTexture(material_index, filename=None):
    """Returns or modifies a material's texture bitmap filename
    Parameters:
      material_index = zero based material index
      filename[opt] = the texture bitmap filename
    Returns:
      if filename is not specified, the current texture bitmap filename
      if filename is specified, the previous texture bitmap filename
      None if not successful or on error
    """
    mat = scriptcontext.doc.Materials[material_index]
    if mat is None: return scriptcontext.errorhandler()
    texture = mat.GetBitmapTexture()
    rc = texture.FileName if texture else ""
    if filename:
        mat.SetBitmapTexture(filename)
        mat.CommitChanges()
        scriptcontext.doc.Views.Redraw()
    return rc


def MaterialTransparency(material_index, transparency=None):
    """Returns or modifies a material's transparency value
    Parameters:
      material_index = zero based material index
      transparency[opt] = the new transparency value. A material's transparency value ranges from 0.0 to 1.0, with
        0.0 being opaque and 1.0 being transparent
    Returns:
      if transparency is not specified, the current material transparency value
      if transparency is specified, the previous material transparency value
      None on error
    """
    mat = scriptcontext.doc.Materials[material_index]
    if mat is None: return scriptcontext.errorhandler()
    rc = mat.Transparency
    if transparency:
        mat.Transparency = transparency
        mat.CommitChanges()
        scriptcontext.doc.Views.Redraw()
    return rc


def MaterialTransparencyMap(material_index, filename=None):
    """Returns or modifies a material's transparency bitmap filename
    Parameters:
      material_index = zero based material index
      filename[opt] = the transparency bitmap filename
    Returns:
      if filename is not specified, the current transparency bitmap filename
      if filename is specified, the previous transparency bitmap filename
      None if not successful or on error
    """
    mat = scriptcontext.doc.Materials[material_index]
    if mat is None: return scriptcontext.errorhandler()
    texture = mat.GetTransparencyTexture()
    rc = texture.FileName if texture else ""
    if filename:
        mat.SetTransparencyTexture(filename)
        mat.CommitChanges()
        scriptcontext.doc.Views.Redraw()
    return rc


def ResetMaterial(material_index):
    """Resets a material to Rhino's default material
    Parameters:
      material_index = zero based material index
    Returns:
      True or False indicating success or failure
    """
    mat = scriptcontext.doc.Materials[material_index]
    if mat is None: return False
    rc = scriptcontext.doc.Materials.ResetMaterial(material_index)
    scriptcontext.doc.Views.Redraw()
    return rc
