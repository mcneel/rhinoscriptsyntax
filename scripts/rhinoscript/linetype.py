import scriptcontext
import utility as rhutil
import Rhino


def __getlinetype(name_or_id):
    if not name_or_id: return None
    id = rhutil.coerceguid(name_or_id)
    if id: name_or_id = id
    linetype = scriptcontext.doc.Linetypes.Find(name_or_id, True)
    if linetype>=0: return scriptcontext.doc.Linetypes[linetype]


def IsLinetype(name_or_id):
    """
    Verifies the existance of a linetype in the document
    Returns:
      True or False
    """
    lt = __getlinetype(name_or_id)
    return lt is not None


def IsLinetypeReference(name_or_id):
    """
    Verifies that an existing linetype is from a reference file
    Returns:
      True or False
      None on error
    """
    lt = __getlinetype(name_or_id)
    if lt is None: return scriptcontext.errorhandler()
    return lt.IsReference


def LinetypeCount():
    """
    Returns the number of linetypes in the document
    """
    return scriptcontext.doc.Linetypes.Count


def LinetypeNames(sort=False):
    """
    Returns the names of all linetypes in the document
    Parameters:
      sort [opt] = return a sorted list of the linetype names
    Returns
      list of strings if successful
      None if not successful
    """
    count = scriptcontext.doc.Linetypes.Count
    if count<1: return scriptcontext.errorhandler()
    rc = []
    table = scriptcontext.doc.Linetypes
    for i in xrange(count):
        linetype = table[i]
        if not linetype.IsDeleted: rc.append(linetype.Name)
    if sort: rc.sort()
    return rc
