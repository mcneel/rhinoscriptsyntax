import scriptcontext
import utility as rhutil
import Rhino


def __getlinetype(name_or_id):
    id = rhutil.coerceguid(name_or_id)
    if id: name_or_id = id
    linetype = scriptcontext.doc.Linetypes.Find(name_or_id, True)
    if linetype>=0: return scriptcontext.doc.Linetypes[linetype]


def IsLinetype(name_or_id):
    """Verifies the existance of a linetype in the document
    Parameters:
      name_or_id = The name or identifier of an existing linetype.
    Returns: 
      True or False
    Example:
      import rhinoscriptsyntax as rs
      name = rs.GetString("Linetype name")
      if rs.IsLinetype(name): print "The linetype exists."
      else: print "The linetype does not exist"
    See Also:
      IsLinetypeReference
    """
    lt = __getlinetype(name_or_id)
    return lt is not None


def IsLinetypeReference(name_or_id):
    """Verifies that an existing linetype is from a reference file
    Parameters:
      name_or_id = The name or identifier of an existing linetype. 
    Returns: 
      True or False
    Example:
      import rhinoscriptsyntax as rs
      name = rs.GetString("Linetype name")
      if rs.IsLinetype(name):
      if rs.IsLinetypeReference(name):
      print "The linetype is a reference linetype."
      else:
      print "The linetype is not a reference linetype."
      else:
      print "The linetype does not exist."
    See Also:
      IsLinetype
    """
    lt = __getlinetype(name_or_id)
    if lt is None: raise ValueError("unable to coerce %s into linetype"%name_or_id)
    return lt.IsReference


def LinetypeCount():
    """Returns number of linetypes in the document
    Parameters:
      None
    Returns:
      the number of linetypes in the document
    Example:
      import rhinoscriptsyntax as rs
      count = rs.LinetypeCount()
      print "There are", count, "linetypes."
    See Also:
      LinetypeNames
    """
    return scriptcontext.doc.Linetypes.Count


def LinetypeNames(sort=False):
    """Returns names of all linetypes in the document
    Parameters:
      sort[opt] = return a sorted list of the linetype names
    Returns:
      list of strings if successful
    Example:
      import rhinoscriptsyntax as rs
      names = rs.LinetypeNames()
      if names:
      for name in names: print name
    See Also:
      LinetypeCount
    """
    count = scriptcontext.doc.Linetypes.Count
    rc = []
    for i in xrange(count):
        linetype = scriptcontext.doc.Linetypes[i]
        if not linetype.IsDeleted: rc.append(linetype.Name)
    if sort: rc.sort()
    return rc