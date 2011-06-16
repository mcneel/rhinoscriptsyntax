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
    """
    rhobj = rhutil.coercerhinoobject(hatch_id, True, True)
    if not isinstance(rhobj, Rhino.DocObjects.HatchObject):
        return scriptcontext.errorhandler()
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
    return rc


def HatchPattern(hatch_id, hatch_pattern=None):
    """Returns or changes a hatch object's hatch pattern
    Paramters:
      hatch_id = identifier of a hatch object
      hatch_pattern[opt] = name of an existing hatch pattern to replace the
          current hatch pattern
    Returns:
      if hatch_pattern is not specified, the current hatch pattern
      if hatch_pattern is specified, the previous hatch pattern
      None on error
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
    "Returns the number of hatch patterns in the document"
    return scriptcontext.doc.HatchPatterns.Count


def HatchPatternDescription(hatch_pattern):
    """Returns the description of a hatch pattern. Note, not all hatch patterns
    have descriptions
    Parameters:
      hatch_pattern = name of an existing hatch pattern
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
    """
    index = scriptcontext.doc.HatchPatterns.Find(hatch_pattern, True)
    if index<0: return scriptcontext.errorhandler()
    rc = scriptcontext.doc.HatchPatterns[index].FillType
    return int(rc)


def HatchPatternNames():
    "Returns the names of all of the hatch patterns in the document"
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
    Paramters:
      object_id = identifier of an object
    Returns:
      True or False
    """
    rhobj = rhutil.coercerhinoobject(object_id, True, False)
    return isinstance(rhobj, Rhino.DocObjects.HatchObject)


def IsHatchPattern(name):
    """Verifies the existence of a hatch pattern in the document
    Parameters:
      name = the name of a hatch pattern
    Returns:
      True or False
    """
    return scriptcontext.doc.HatchPatterns.Find(name, True)>=0


def IsHatchPatternCurrent(hatch_pattern):
    """Verifies that a hatch pattern is the current hatch pattern
    Parameters:
      hatch_pattern = name of an existing hatch pattern
    Returns:
      True or False
      None on error
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
    """
    index = scriptcontext.doc.HatchPatterns.Find(hatch_pattern, True)
    if index<0: return scriptcontext.errorhandler()
    return scriptcontext.doc.HatchPatterns[index].IsReference
