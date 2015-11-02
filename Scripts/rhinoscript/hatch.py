import scriptcontext
import utility as rhutil
import Rhino
import System.Guid

def AddHatch(curve_id, hatch_pattern=None, scale=1.0, rotation=0.0):
    """Creates a new hatch object from a closed planar curve object
    Parameters:
      curve_id = identifier of the closed planar curve that defines the
          boundary of the hatch object
      hatch_pattern[opt] = name of the hatch pattern to be used by the hatch
          object. If omitted, the current hatch pattern will be used
      scale[opt] = hatch pattern scale factor
      rotation[opt] = hatch pattern rotation angle in degrees.
    Returns:
      identifier of the newly created hatch on success
      None on error
    Example:
      import rhinoscriptsyntax as rs
      circle = rs.AddCircle(rs.WorldXYPlane(), 10.0)
      if rs.IsHatchPattern("Grid"):
      rs.AddHatch( circle, "Grid" )
      else:
      rs.AddHatch( circle, rs.CurrentHatchPattern() )
    See Also:
      AddHatches
      CurrentHatchPattern
      HatchPatternNames
    """
    rc = AddHatches(curve_id, hatch_pattern, scale, rotation)
    if rc: return rc[0]
    return scriptcontext.errorhandler()


def AddHatches(curve_ids, hatch_pattern=None, scale=1.0, rotation=0.0):
    """Creates one or more new hatch objects a list of closed planar curves
    Parameters:
      curve_ids = identifiers of the closed planar curves that defines the
          boundary of the hatch objects
      hatch_pattern[opt] = name of the hatch pattern to be used by the hatch
          object. If omitted, the current hatch pattern will be used
      scale[opt] = hatch pattern scale factor
      rotation[opt] = hatch pattern rotation angle in degrees.
    Returns:
      identifiers of the newly created hatch on success
      None on error
    Example:
      import rhinoscriptsyntax as rs
      curves = rs.GetObjects("Select closed planar curves", rs.filter.curve)
      if curves:
      if rs.IsHatchPattern("Grid"):
      rs.AddHatches( curves, "Grid" )
      else:
      rs.AddHatches( curves, rs.CurrentHatchPattern() )
    See Also:
      AddHatch
      CurrentHatchPattern
      HatchPatternNames
    """
    id = rhutil.coerceguid(curve_ids, False)
    if id: curve_ids = [id]
    index = scriptcontext.doc.HatchPatterns.CurrentHatchPatternIndex
    if hatch_pattern and hatch_pattern!=index:
        if isinstance(hatch_pattern, int):
            index = hatch_pattern
        else:
            index = scriptcontext.doc.HatchPatterns.Find(hatch_pattern, True)
        if index<0: return scriptcontext.errorhandler()
    curves = [rhutil.coercecurve(id, -1, True) for id in curve_ids]
    rotation = Rhino.RhinoMath.ToRadians(rotation)
    hatches = Rhino.Geometry.Hatch.Create(curves, index, rotation, scale)
    if not hatches: return scriptcontext.errorhandler()
    ids = []
    for hatch in hatches:
        id = scriptcontext.doc.Objects.AddHatch(hatch)
        if id==System.Guid.Empty: continue
        ids.append(id)
    if not ids: return scriptcontext.errorhandler()
    scriptcontext.doc.Views.Redraw()
    return ids


def AddHatchPatterns(filename, replace=False):
    """Adds hatch patterns to the document by importing hatch pattern definitions
    from a pattern file.
    Parameters:
      filename = name of the hatch pattern file
      replace[opt] = If hatch pattern names already in the document match hatch
          pattern names in the pattern definition file, then the existing hatch
          patterns will be redefined
    Returns:
      Names of the newly added hatch patterns if successful
      None on error
    Example:
      import rhinoscriptsyntax as rs
      filename = rs.OpenFileName("Import", "Pattern Files (*.pat)|*.pat||")
      if filename:
      patterns = rs.AddHatchPatterns(filename)
      if patterns:
      for pattern in patterns: print pattern
    See Also:
      HatchPatternCount
      HatchPatternNames
    """
    patterns = Rhino.DocObjects.HatchPattern.ReadFromFile(filename, True)
    if not patterns: return scriptcontext.errorhandler()
    rc = []
    for pattern in patterns:
         index = scriptcontext.doc.HatchPatterns.Add(pattern)
         if index>=0:
             pattern = scriptcontext.doc.HatchPatterns[index]
             rc.append(pattern.Name)
    if not rc: return scriptcontext.errorhandler()
    return rc


def CurrentHatchPattern(hatch_pattern=None):
    """Returns or sets the current hatch pattern file
    Parameters:
      hatch_pattern[opt] = name of an existing hatch pattern to make current
    Returns:
      if hatch_pattern is not specified, the current hatch pattern
      if hatch_pattern is specified, the previous hatch pattern
      None on error
    Example:
      import rhinoscriptsyntax as rs
      if rs.IsHatchPattern("Hatch2"): rs.CurrentHatchPattern("Hatch2")
    See Also:
      HatchPatternCount
      HatchPatternNames
    """
    rc = scriptcontext.doc.HatchPatterns.CurrentHatchPatternIndex
    if hatch_pattern:
        index = scriptcontext.doc.HatchPatterns.Find(hatch_pattern, True)
        if index<0: return scriptcontext.errorhandler()
        scriptcontext.doc.HatchPatterns.CurrentHatchPatternIndex = index
    return rc


def ExplodeHatch(hatch_id, delete=False):
    """Explodes a hatch object into its component objects. The exploded objects
    will be added to the document. If the hatch object uses a solid pattern,
    then planar face Brep objects will be created. Otherwise, line curve objects
    will be created
    Parameters:
      hatch_id = identifier of a hatch object
      delete[opt] = delete the hatch object
    Returns:
      list of identifiers for the newly created objects
      None on error
    Example:
      import rhinoscriptsyntax as rs
      id = rs.GetObject("Select object")
      if rs.IsHatch(id): rs.ExplodeHatch(id, True)
    See Also:
      IsHatch
      HatchPattern
      HatchRotation
      HatchScale
    """
    rhobj = rhutil.coercerhinoobject(hatch_id, True, True)
    pieces = rhobj.HatchGeometry.Explode()
    if not pieces: return scriptcontext.errorhandler()
    attr = rhobj.Attributes
    rc = []
    for piece in pieces:
        id = None
        if isinstance(piece, Rhino.Geometry.Curve):
            id = scriptcontext.doc.Objects.AddCurve(piece, attr)
        elif isinstance(piece, Rhino.Geometry.Brep):
            id = scriptcontext.doc.Objects.AddBrep(piece, attr)
        if id: rc.append(id)
    if delete: scriptcontext.doc.Objects.Delete(rhobj)
    return rc


def HatchPattern(hatch_id, hatch_pattern=None):
    """Returns or changes a hatch object's hatch pattern
    Parameters:
      hatch_id = identifier of a hatch object
      hatch_pattern[opt] = name of an existing hatch pattern to replace the
          current hatch pattern
    Returns:
      if hatch_pattern is not specified, the current hatch pattern
      if hatch_pattern is specified, the previous hatch pattern
      None on error
    Example:
      import rhinoscriptsyntax as rs
      objects = rs.AllObjects()
      if objects is not None:
      for obj in objects:
      if rs.IsHatch(obj) and rs.HatchPattern(obj)=="Solid":
      rs.SelectObject(obj)
    See Also:
      AddHatch
      AddHatches
      HatchRotation
      HatchScale
      IsHatch
    """
    hatchobj = rhutil.coercerhinoobject(hatch_id, True, True)
    if not isinstance(hatchobj, Rhino.DocObjects.HatchObject):
        return scriptcontext.errorhandler()
    old_index = hatchobj.HatchGeometry.PatternIndex
    if hatch_pattern:
        new_index = scriptcontext.doc.HatchPatterns.Find(hatch_pattern, True)
        if new_index<0: return scriptcontext.errorhandler()
        hatchobj.HatchGeometry.PatternIndex = new_index
        hatchobj.CommitChanges()
        scriptcontext.doc.Views.Redraw()
    return scriptcontext.doc.HatchPatterns[old_index].Name


def HatchPatternCount():
    """Returns the number of hatch patterns in the document
    Parameters:
      None
    Returns:
      the number of hatch patterns in the document
    Example:
      import rhinoscriptsyntax as rs
      print "There are", rs.HatchPatternCount(), "hatch patterns."
    See Also:
      HatchPatternNames
    """
    return scriptcontext.doc.HatchPatterns.Count


def HatchPatternDescription(hatch_pattern):
    """Returns the description of a hatch pattern. Note, not all hatch patterns
    have descriptions
    Parameters:
      hatch_pattern = name of an existing hatch pattern
    Returns:
      description of the hatch pattern on success otherwise None
    Example:
      import rhinoscriptsyntax as rs
      patterns = rs.HatchPatternNames()
      for pattern in patterns:
      description = rs.HatchPatternDescription(pattern)
      if description:print pattern, "-", description
    See Also:
      HatchPatternCount
      HatchPatternNames
    """
    index = scriptcontext.doc.HatchPatterns.Find(hatch_pattern, True)
    if index<0: return scriptcontext.errorhandler()
    return scriptcontext.doc.HatchPatterns[index].Description


def HatchPatternFillType(hatch_pattern):
    """Returns the fill type of a hatch pattern.
        0 = solid, uses object color
        1 = lines, uses pattern file definition
        2 = gradient, uses fill color definition
    Parameters:
      hatch_pattern = name of an existing hatch pattern
    Returns:
      hatch pattern's fill type if successful otherwise None
    Example:
      import rhinoscriptsyntax as rs
      patterns = rs.HatchPatternNames()
      for pattern in patterns:
      fill = rs.HatchPatternFillType(pattern)
      print pattern, "-", fill
    See Also:
      HatchPatternCount
      HatchPatternNames
    """
    index = scriptcontext.doc.HatchPatterns.Find(hatch_pattern, True)
    if index<0: return scriptcontext.errorhandler()
    return int(scriptcontext.doc.HatchPatterns[index].FillType)


def HatchPatternNames():
    """Returns the names of all of the hatch patterns in the document
    Parameters:
      None
    Returns:
      the names of all of the hatch patterns in the document
    Example:
      import rhinoscriptsyntax as rs
      patterns = rs.HatchPatternNames()
      for pattern in patterns:
      description = rs.HatchPatternDescription(pattern)
      if description: print pattern, "-", description
      else: print pattern
    See Also:
      HatchPatternCount
    """
    rc = []
    for i in range(scriptcontext.doc.HatchPatterns.Count):
        hatchpattern = scriptcontext.doc.HatchPatterns[i]
        if hatchpattern.IsDeleted: continue
        rc.append(hatchpattern.Name)
    return rc

def HatchRotation(hatch_id, rotation=None):
    """Returns or modifies the rotation applied to the hatch pattern when
    it is mapped to the hatch's plane
    Parameters:
      hatch_id = identifier of a hatch object
      rotation[opt] = rotation angle in degrees
    Returns:
      if rotation is not defined, the current rotation angle
      if rotation is specified, the previous rotation angle
      None on error
    Example:
      import rhinoscriptsyntax as rs
      objects = rs.AllObjects()
      if objects:
      for obj in objects:
      if rs.IsHatch(obj) and rs.HatchRotation(obj)>0:
      rs.HatchRotation(obj,0)
    See Also:
      AddHatch
      AddHatches
      HatchPattern
      HatchScale
      IsHatch
    """
    hatchobj = rhutil.coercerhinoobject(hatch_id, True, True)
    if not isinstance(hatchobj, Rhino.DocObjects.HatchObject):
        return scriptcontext.errorhandler()
    rc = hatchobj.HatchGeometry.PatternRotation
    rc = Rhino.RhinoMath.ToDegrees(rc)
    if rotation is not None and rotation!=rc:
        rotation = Rhino.RhinoMath.ToRadians(rotation)
        hatchobj.HatchGeometry.PatternRotation = rotation
        hatchobj.CommitChanges()
        scriptcontext.doc.Views.Redraw()
    return rc


def HatchScale(hatch_id, scale=None):
    """Returns or modifies the scale applied to the hatch pattern when it is
    mapped to the hatch's plane
    Parameters:
      hatch_id = identifier of a hatch object
      scale[opt] = scale factor
    Returns:
      if scale is not defined, the current scale factor
      if scale is defined, the previous scale factor
      None on error
    Example:
      import rhinoscriptsyntax as rs
      objects = rs.NormalObjects()
      if objects:
      for obj in objects:
      if rs.IsHatch(obj) and rs.HatchScale(obj)>1.0:
      rs.HatchScale(obj, 1.0)
    See Also:
      HatchPattern
      HatchRotation
      IsHatch
    """
    hatchobj = rhutil.coercerhinoobject(hatch_id)
    if not isinstance(hatchobj, Rhino.DocObjects.HatchObject):
        return scriptcontext.errorhandler()
    rc = hatchobj.HatchGeometry.PatternScale
    if scale and scale!=rc:
        hatchobj.HatchGeometry.PatternScale = scale
        hatchobj.CommitChanges()
        scriptcontext.doc.Views.Redraw()
    return rc


def IsHatch(object_id):
    """Verifies the existence of a hatch object in the document
    Parameters:
      object_id = identifier of an object
    Returns:
      True or False
    Example:
      import rhinoscriptsyntax as rs
      obj = rs.GetObject("Select object")
      if rs.IsHatch(obj): print "Object is a hatch"
      else: print "Object is not a hatch"
    See Also:
      HatchPattern
      HatchRotation
      HatchScale
    """
    rhobj = rhutil.coercerhinoobject(object_id, True, False)
    return isinstance(rhobj, Rhino.DocObjects.HatchObject)


def IsHatchPattern(name):
    """Verifies the existence of a hatch pattern in the document
    Parameters:
      name = the name of a hatch pattern
    Returns:
      True or False
    Example:
      import rhinoscriptsyntax as rs
      hatch = rs.GetString("Hatch pattern name")
      if rs.IsHatchPattern(hatch): print "The hatch pattern exists."
      else: print "The hatch pattern does not exist."
    See Also:
      IsHatchPatternCurrent
      IsHatchPatternReference
    """
    return scriptcontext.doc.HatchPatterns.Find(name, True)>=0


def IsHatchPatternCurrent(hatch_pattern):
    """Verifies that a hatch pattern is the current hatch pattern
    Parameters:
      hatch_pattern = name of an existing hatch pattern
    Returns:
      True or False
      None on error
    Example:
      import rhinoscriptsyntax as rs
      hatch = rs.GetString("Hatch pattern name")
      if rs.IsHatchPattern(hatch):
      if rs.IsHatchPatternCurrent(hatch):
      print "The hatch pattern is current."
      else:
      print "The hatch pattern is not current."
      else: print "The hatch pattern does not exist."
    See Also:
      IsHatchPattern
      IsHatchPatternReference
    """
    index = scriptcontext.doc.HatchPatterns.Find(hatch_pattern, True)
    if index<0: return scriptcontext.errorhandler()
    return index==scriptcontext.doc.HatchPatterns.CurrentHatchPatternIndex


def IsHatchPatternReference(hatch_pattern):
    """Verifies that a hatch pattern is from a reference file
    Parameters:
      hatch_pattern = name of an existing hatch pattern
    Returns:
      True or False
      None on error
    Example:
      import rhinoscriptsyntax as rs
      hatch = rs.GetString("Hatch pattern name")
      if rs.IsHatchPattern(hatch):
      if rs.IsHatchPatternReference(hatch):
      print "The hatch pattern is reference."
      else:
      print "The hatch pattern is not reference."
      else:
      print "The hatch pattern does not exist."
    See Also:
      IsHatchPattern
      IsHatchPatternCurrent
    """
    index = scriptcontext.doc.HatchPatterns.Find(hatch_pattern, True)
    if index<0: return scriptcontext.errorhandler()
    return scriptcontext.doc.HatchPatterns[index].IsReference