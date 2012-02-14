import Rhino
import scriptcontext
import utility as rhutil
import math
import System.Guid

def __InstanceObjectFromId( id, raise_if_missing ):
    rhobj = rhutil.coercerhinoobject(id, True, raise_if_missing)
    if isinstance(rhobj, Rhino.DocObjects.InstanceObject): return rhobj
    if raise_if_missing: raise ValueError("unable to find InstanceObject")


def BlockContainerCount(block_name):
    """Returns number of block definitions that contain a specified
    block definition
    Parameters:
      block_name = the name of an existing block definition
    """
    idef = scriptcontext.doc.InstanceDefinitions.Find(block_name, True)
    if idef is None: return 0
    containers = idef.GetContainers()
    if not containers: return 0
    return len(containers)


def BlockContainers(block_name):
    """Returns names of the block definitions that contain a specified block
    definition.
    Parameters:
      block_name = the name of an existing block definition
    Returns:
      A list of block definition names
    """
    idef = scriptcontext.doc.InstanceDefinitions.Find(block_name, True)
    if not idef: raise ValueError("%s does not exist in InstanceDefinitionsTable"%block_name)
    containers = idef.GetContainers()
    rc = []
    for item in containers:
        if not item.IsDeleted: rc.append(item.Name)
    return rc


def BlockCount():
    "Returns the number of block definitions in the document"
    return scriptcontext.doc.InstanceDefinitions.ActiveCount


def BlockDescription(block_name, description=None):
    """Returns or sets the description of a block definition
    Parameters:
      block_name = the name of an existing block definition
      description[opt] = The new description.
    Returns:
      if description is not specified, the current description
      if description is specified, the previous description
    """
    idef = scriptcontext.doc.InstanceDefinitions.Find(block_name, True)
    if not idef: raise ValueError("%s does not exist in InstanceDefinitionsTable"%block_name)
    rc = idef.Description
    if description: table.Modify( idef, idef.Name, description )
    return rc


def BlockInstanceCount(block_name,reference_level=0):
    """Counts number of instances of the block in the document.
    Nested instances are not included in the count.
    Parameters:
      block_name = the name of an existing block definition
      reference_level [opt] = int :     
        0 = get top level references in active document.
        1 = get top level and nested references in active document.
        2 = check for references from other instance definitions
      
    """
    idef = scriptcontext.doc.InstanceDefinitions.Find(block_name, True)
    if not idef: raise ValueError("%s does not exist in InstanceDefinitionsTable"%block_name)
    refs = idef.GetReferences(reference_level)
    return len(refs)


def BlockInstanceInsertPoint(object_id):
    """Returns the insertion point of a block instance.
    Parameters:
      object_id = The identifier of an existing block insertion object
    Returns:
      list representing 3D point if successful
    """
    instance = __InstanceObjectFromId(object_id, True)
    xf = instance.InstanceXform
    pt = Rhino.Geometry.Point3d.Origin
    pt.Transform(xf)
    return pt


def BlockInstanceName(object_id):
    """Returns the block name of a block instance
    Parameters:
      object_id = The identifier of an existing block insertion object
    """
    instance = __InstanceObjectFromId(object_id, True)
    idef = instance.InstanceDefinition
    return idef.Name


def BlockInstances(block_name):
    """Returns the identifiers of the inserted instances of a block.
    Parameters:
      block_name = the name of an existing block definition
    Returns:
      list of guids identifying the instances of a block
    """
    idef = scriptcontext.doc.InstanceDefinitions.Find(block_name, True)
    if not idef: raise ValueError("%s does not exist in InstanceDefinitionsTable"%block_name)
    instances = idef.GetReferences(0)
    return [item.Id for item in instances]


def BlockInstanceXform(object_id):
    """Returns the location of a block instance relative to the world coordinate
    system origin (0,0,0). The position is returned as a 4x4 transformation
    matrix
    Parameters:
      object_id = The identifier of an existing block insertion object  
    """
    instance = __InstanceObjectFromId(object_id, True)
    return instance.InstanceXform


def BlockNames( sort=False ):
    """Returns the names of all block definitions in the document
    Parameters:
      sort = return a sorted list
    """
    ideflist = scriptcontext.doc.InstanceDefinitions.GetList(True)
    rc = [item.Name for item in ideflist]
    if(sort): rc.sort()
    return rc


def BlockObjectCount(block_name):
    """Returns the number of objects that make up a block definition
    Parameters:
      block_name = name of an existing block definition
    """
    idef = scriptcontext.doc.InstanceDefinitions.Find(block_name, True)
    if not idef: raise ValueError("%s does not exist in InstanceDefinitionsTable"%block_name)
    return idef.ObjectCount


def BlockObjects(block_name):
    """Returns the identifiers of the objects that make up a block definition
    Parameters:
      block_name = name of an existing block definition
    Returns:
      list of identifiers on success
    """
    idef = scriptcontext.doc.InstanceDefinitions.Find(block_name, True)
    if not idef: raise ValueError("%s does not exist in InstanceDefinitionsTable"%block_name)
    rhobjs = idef.GetObjects()
    return [obj.Id for obj in rhobjs]


def BlockPath(block_name):
    """Returns the path to the source of a linked or embedded block definition.
    A linked or embedded block definition is a block definition that was
    inserted from an external file.
    Parameters:
      block_name = name of an existing block definition
    Returns:
      path to the linked block on success
      None on error
    """
    idef = scriptcontext.doc.InstanceDefinitions.Find(block_name, True)
    if not idef: raise ValueError("%s does not exist in InstanceDefinitionsTable"%block_name)
    return idef.SourceArchive


def DeleteBlock(block_name):
    """Deletes a block definition and all of it's inserted instances.
    Parameters:
      block_name = name of an existing block definition
    Returns:
      True or False indicating success or failure  
    """
    return scriptcontext.doc.InstanceDefinitions.Delete(index, True, False)


def ExplodeBlockInstance(object_id):
    """Explodes a block instance into it's geometric components. The
    exploded objects are added to the document
    Parameters:
      object_id = The identifier of an existing block insertion object  
    Returns:
      identifiers for the newly exploded objects on success
    """
    instance = __InstanceObjectFromId(object_id, True)
    rc = scriptcontext.doc.Objects.AddExplodedInstancePieces(instance)
    if rc:
        scriptcontext.doc.Objects.Delete(instance, True)
        scriptcontext.doc.Views.Redraw()
        return rc


def InsertBlock( block_name, insertion_point, scale=(1,1,1), angle_degrees=0, rotation_normal=(0,0,1) ):
    """Inserts a block whose definition already exists in the document
    Parameters:
      block_name = name of an existing block definition
      insertion_point = insertion point for the block
      scale [opt] = x,y,z scale factors
      angle_degrees [opt] = rotation angle in degrees
      rotation_normal [opt] = the axis of rotation.
    Returns:
      id for the block that was added to the doc
    """
    insertion_point = rhutil.coerce3dpoint(insertion_point, True)
    rotation_normal = rhutil.coerce3dvector(rotation_normal, True)
    angle_radians = math.radians(angle_degrees)
    trans = Rhino.Geometry.Transform
    move = trans.Translation(insertion_point[0],insertion_point[1],insertion_point[2])
    scale = trans.Scale(Rhino.Geometry.Plane.WorldXY, scale[0], scale[1], scale[2])
    rotate = trans.Rotation(angle_radians, rotation_normal, Rhino.Geometry.Point3d.Origin)
    xform = move * scale * rotate
    return InsertBlock2( block_name, xform )


def InsertBlock2(block_name, xform):
    """Inserts a block whose definition already exists in the document
    Parameters:
      block_name = name of an existing block definition
      xform = 4x4 transformation matrix to apply
    Returns:
      id for the block that was added to the doc on success
    """
    idef = scriptcontext.doc.InstanceDefinitions.Find(block_name, True)
    if not idef: raise ValueError("%s does not exist in InstanceDefinitionsTable"%block_name)
    xform = rhutil.coercexform(xform, True)
    id = scriptcontext.doc.Objects.AddInstanceObject(idef.Index, xform )
    if id!=System.Guid.Empty:
        scriptcontext.doc.Views.Redraw()
        return id


def IsBlock(block_name):
    """Verifies the existence of a block definition in the document.
    Parameters:
      block_name = name of an existing block definition
    Returns:
      True or False
    """
    idef = scriptcontext.doc.InstanceDefinitions.Find(block_name, True)
    return (idef is not None)


def IsBlockEmbedded(block_name):
    """Verifies a block definition is embedded, or linked, from an external file.
    Parameters:
      block_name = name of an existing block definition
    Returns:
      True or False
    """
    idef = scriptcontext.doc.InstanceDefinitions.Find(block_name, True)
    if not idef: raise ValueError("%s does not exist in InstanceDefinitionsTable"%block_name)
    ut = Rhino.DocObjects.InstanceDefinitionUpdateType
    return (idef.UpdateType==ut.Embedded or idef.UpdateType==ut.LinkedAndEmbedded)


def IsBlockInstance( object_id ):
    """Verifies an object is a block instance
    Parameters:
      object_id = The identifier of an existing block insertion object
    Returns:
      True or False
    """
    return  __InstanceObjectFromId(object_id, False) is not None


def IsBlockInUse( block_name, where_to_look=0 ):
    """Verifies that a block definition is being used by an inserted instance
    Parameters:
      block_name = name of an existing block definition
      where_to_look [opt] = One of the following values
           0 = Check for top level references in active document
           1 = Check for top level and nested references in active document
           2 = Check for references in other instance definitions
    Returns:
      True or False
    """
    idef = scriptcontext.doc.InstanceDefinitions.Find(block_name, True)
    if not idef: raise ValueError("%s does not exist in InstanceDefinitionsTable"%block_name)
    return idef.InUse(where_to_look)


def IsBlockReference(block_name):
    """Verifies that a block definition is from a reference file.
    Parameters:
      block_name = name of an existing block definition
    Returns:
      True or False
    """
    idef = scriptcontext.doc.InstanceDefinitions.Find(block_name, True)
    if not idef: raise ValueError("%s does not exist in InstanceDefinitionsTable"%block_name)
    return idef.IsReference


def RenameBlock( block_name, new_name ):
    """Renames an existing block definition
    Parameters:
      block_name = name of an existing block definition
      new_name = name to change to
    Returns:
      True or False indicating success or failure
    """
    idef = scriptcontext.doc.InstanceDefinitions.Find(block_name, True)
    if not idef: raise ValueError("%s does not exist in InstanceDefinitionsTable"%block_name)
    description = idef.Description
    rc = scriptcontext.doc.InstanceDefinitions.Modify(idef, new_name, description, False)
    return rc
