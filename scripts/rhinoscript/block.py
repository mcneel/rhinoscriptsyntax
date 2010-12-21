import Rhino
import scriptcontext
import utility as rhutil
import math
import System.Guid

def __InstanceObjectFromId( id ):
    id = rhutil.coerceguid(id)
    if id is None: return scriptcontext.errorhandler()
    objref = Rhino.DocObjects.ObjRef(id)
    instance = objref.Object()
    objref.Dispose()
    return instance


def BlockContainerCount(block_name):
    """
    Returns number of block definitions that contain a specified
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
    """
    Returns names of the block definitions that contain a specified block definition.
    Parameters:
      block_name = the name of an existing block definition
    Returns:
      A list of block definition names if successful
      None on error
    """
    idef = scriptcontext.doc.InstanceDefinitions.Find(block_name, True)
    if idef is None: return scriptcontext.errorhandler()
    containers = idef.GetContainers()
    if containers is None: return scriptcontext.errorhandler()
    rc = []
    for item in containers:
        if not item.IsDeleted: rc.append(item.Name)
    return rc


def BlockCount():
    "Returns the number of block definitions in the document"
    table = scriptcontext.doc.InstanceDefinitions
    count = table.Count
    rc = 0
    for i in xrange(count):
        idef = table[i]
        if idef and not idef.IsDeleted: rc+=1
    return rc


def BlockDescription(block_name, description=None):
    """
    Returns or sets the description of a block definition
    Parameters:
      block_name = the name of an existing block definition
      description[opt] = The new description.
    Returns:
      if description is not specified, the current description
      if description is specified, the previous description
      None on error
    """
    idef = scriptcontext.doc.InstanceDefinitions.Find(block_name, True)
    if idef is None: return scriptcontext.errorhandler()
    rc = idef.Description
    if description: table.Modify( idef, idef.Name, description )
    return rc


def BlockInstanceCount(block_name):
    """
    Counts number of instances of the block in the document.
    Nested instances are not included in the count.
    Parameters:
      block_name = the name of an existing block definition
    """
    idef = scriptcontext.doc.InstanceDefinitions.Find(block_name, True)
    if idef is None: return 0
    refs = idef.GetReferences()
    if not refs: return 0
    return len(refs)


def BlockInstanceInsertPoint(object_id):
    """
    Returns the insertion point of a block instance.
    Parameters:
      object_id = The identifier of an existing block insertion object
    Returns:
      list representing 3D point if successful
      None on error
    """
    instance = __InstanceObjectFromId(object_id)
    if( instance==None ): return scriptcontext.errorhandler()
    xf = instance.InstanceXform
    pt = Rhino.Geometry.Point3d.Origin
    pt.Transform(xf)
    return pt


def BlockInstanceName(object_id):
    """
    Returns the block name of a block instance
    Parameters:
      object_id = The identifier of an existing block insertion object
    """
    instance = __InstanceObjectFromId(object_id)
    if( instance==None ): return scriptcontext.errorhandler()
    idef = instance.InstanceDefinition
    if( idef==None ): return scriptcontext.errorhandler()
    return idef.Name


def BlockInstances(block_name):
    """
    Returns the identifiers of the inserted instances of a block.
    Parameters:
      block_name = the name of an existing block definition
    Returns:
      list of guids identifying the instances of a block
      None on error  
    """
    idef = scriptcontext.doc.InstanceDefinitions.Find(block_name, True)
    if( idef==None ): return scriptcontext.errorhandler()
    instances = idef.GetReferences(0)
    if( instances==None ): return scriptcontext.errorhandler()
    rc = [item.Id for item in instances]
    return rc


def BlockInstanceXform(object_id):
    """
    Returns the location of a block instance relative to the world coordinate
    system origin (0,0,0). The position is returned as a 4x4 transformation
    matrix
    Parameters:
      object_id = The identifier of an existing block insertion object  
    """
    instance = __InstanceObjectFromId(object_id)
    if( instance==None ): return scriptcontext.errorhandler()
    xf = instance.InstanceXform
    matrix = [(xf.M00, xf.M01, xf.M02, xf.M03),
              (xf.M10, xf.M11, xf.M12, xf.M13),
              (xf.M20, xf.M21, xf.M22, xf.M23),
              (xf.M30, xf.M31, xf.M32, xf.M33)]
    return matrix


def BlockNames( sort=False ):
    """
    Returns the names of all block definitions in the document
    Parameters:
      sort = return a sorted list
    """
    ideflist = scriptcontext.doc.InstanceDefinitions.GetList(True)
    if( ideflist==None ): return None
    rc = [item.Name for item in ideflist]
    if(sort): rc.sort()
    return rc


def BlockObjectCount( block_name ):
    """
    Returns the number of objects that make up a block definition
    Parameters:
      block_name = name of an existing block definition
    """
    idef = scriptcontext.doc.InstanceDefinitions.Find(block_name, True)
    if idef is None: return 0
    return idef.ObjectCount


def BlockObjects( block_name ):
    """
    Returns the identifiers of the objects that make up a block definition
    Parameters:
      block_name = name of an existing block definition
    Returns:
      list of identifiers on success
    """
    idef = scriptcontext.doc.InstanceDefinitions.Find(block_name, True)
    if idef is None: return scriptcontext.errorhandler()
    rhobjs = idef.GetObjects()
    if not rhobjs: return scriptcontext.errorhandler()
    return [obj.Id for obj in rhobjs]


def BlockPath( block_name ):
    """
    Returns the path to the source of a linked or embedded block definition.
    A linked or embedded block definition is a block definition that was
    inserted from an external file.
    Parameters:
      block_name = name of an existing block definition
    Returns:
      path to the linked block on success
      None on error
    """
    idef = scriptcontext.doc.InstanceDefinitions.Find(block_name, True)
    if( idef==None ): return scriptcontext.errorhandler()
    return idef.SourceArchive


def DeleteBlock( block_name ):
    """
    Deletes a block definition and all of it's inserted instances.
    Parameters:
      block_name = name of an existing block definition
    Returns:
      True or False indicating success or failure  
    """
    return scriptcontext.doc.InstanceDefinitions.Delete(index, True, False)


def ExplodeBlockInstance( object_id ):
  """
  Explodes a block instance into it's geometric components. The
  exploded objects are added to the document
  Parameters:
    object_id = The identifier of an existing block insertion object  
  Returns:
    list of identifiers for the newly exploded objects on success
    None on failure
  """
  instance = __InstanceObjectFromId(object_id)
  if( instance==None ): return scriptcontext.errorhandler()
  subobjects = instance.GetSubObjects()
  if( subobjects==None ): return scriptcontext.errorhandler()
  persistSelect = (instance.IsSelected(False)>=2)
  instance.Select(False, True)
  rc = list()
  for item in subobjects:
      id = scriptcontext.doc.Objects.AddObject(item)
      if( id!=System.Guid.Empty ):
          rc.append(id)
          if( persistSelect ):
              rhobj = scriptcontext.doc.Objects.Find(id)
              rhobj.Select(True, True)
  if( len(rc)>0 ):
      scriptcontext.doc.Objects.Delete( Rhino.DocObjects.ObjRef(instance) )
      scriptcontext.doc.Views.Redraw()
      return rc
  return scriptcontext.errorhandler()


def InsertBlock( block_name, insertion_point, scale=(1,1,1), angle_degrees=0, rotation_normal=(0,0,1) ):
    """
    Inserts a block whose definition already exists in the document
    Parameters:
      block_name = name of an existing block definition
      insertion_point = insertion point for the block
      scale [opt] = x,y,z scale factors
      angle_degrees [opt] = rotation angle in degrees
      rotation_normal [opt] = the axis of rotation.
    Returns:
      id for the block that was added to the doc on success
      None on failure
    """
    insertion_point = rhutil.coerce3dpoint(insertion_point)
    rotation_normal = rhutil.coerce3dvector(rotation_normal)
    if( insertion_point==None or rotation_normal==None ):
        return scriptcontext.errorhandler()
    angle_radians = math.radians(angle_degrees)
    
    trans = Rhino.Geometry.Transform
    move = trans.Translation(insertion_point[0],insertion_point[1],insertion_point[2])
    scale = trans.Scale(Rhino.Geometry.Plane.WorldXY, scale[0], scale[1], scale[2])
    rotate = trans.Rotation(angle_radians, rotation_normal, Rhino.Geometry.Point3d.Origin)
    xform = move * scale * rotate
    return InsertBlock2( block_name, xform )


def InsertBlock2( block_name, xform ):
    """
    Inserts a block whose definition already exists in the document
    Parameters:
      block_name = name of an existing block definition
      xform = 4x4 transformation matrix to apply
    Returns:
      id for the block that was added to the doc on success
      None on failure
    """
    idef = scriptcontext.doc.InstanceDefinitions.Find(block_name, True)
    if( idef==None ): return scriptcontext.errorhandler()
    xform = rhutil.coercexform(xform)
    if( xform==None ): return scriptcontext.errorhandler()
    if( xform.IsValid ):
        id = scriptcontext.doc.Objects.AddInstanceObject(idef.Index, xform )
        if( id != System.Guid.Empty ):
            scriptcontext.doc.Views.Redraw()
            return id
    return scriptcontext.errorhandler()


def IsBlock( block_name ):
    """
    Verifies the existence of a block definition in the document.
    Parameters:
      block_name = name of an existing block definition
    Returns:
      True or False
    """
    idef = scriptcontext.doc.InstanceDefinitions.Find(block_name, True)
    return (idef!=None)


def IsBlockEmbedded( block_name ):
    """
    Verifies a block definition is embedded, or linked, from an external file.
    Parameters:
      block_name = name of an existing block definition
    Returns:
      True or False
    """
    idef = scriptcontext.doc.InstanceDefinitions.Find(block_name, True)
    if( idef==None or idef.IsDeleted ): return False
    ut = Rhino.DocObjects.InstanceDefinitionUpdateType
    return (idef.UpdateType==ut.Embedded or idef.UpdateType==ut.LinkedAndEmbedded)


def IsBlockInstance( object_id ):
    """
    Verifies an object is a block instance
    Parameters:
      object_id = The identifier of an existing block insertion object
    Returns:
      True or False
    """
    instance = __InstanceObjectFromId(object_id)
    return (instance!=None)


def IsBlockInUse( block_name, where_to_look=0 ):
    """
    Verifies that a block definition is being used by an inserted instance
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
    if( idef==None or idef.IsDeleted ): return False
    return idef.InUse(where_to_look)


def IsBlockReference( block_name ):
    """
    Verifies that a block definition is from a reference file.
    Parameters:
      block_name = name of an existing block definition
    Returns:
      True or False
    """
    idef = scriptcontext.doc.InstanceDefinitions.Find(block_name, True)
    if( idef==None or idef.IsDeleted ): return False
    return idef.IsReference


def RenameBlock( block_name, new_name ):
    """
    Renames an existing block definition
    Parameters:
      block_name = name of an existing block definition
      new_name = name to change to
    Returns:
      True or False indicating success or failure
    """
    idef = scriptcontext.doc.InstanceDefinitions.Find(block_name, True)
    if( idef==None or idef.IsDeleted ): return False
    description = idef.Description
    rc = scriptcontext.doc.InstanceDefinitions.Modify(idef, new_name, description, False)
    return rc
