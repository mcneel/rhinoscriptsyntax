import scriptcontext
import utility as rhutil

def DeleteDocumentData(section=None, entry=None):
    """Removes user data strings from the current document
    Parameters:
      section = section name. If omitted, all sections and their corresponding
        entries are removed
      entry = entry name. If omitted, all entries for section are removed
    Returns:
      True or False indicating success or failure
    """
    return scriptcontext.doc.Strings.Delete(section, entry)


def DocumentDataCount():
    "Returns the number of user data strings in the current document"
    return scriptcontext.doc.Strings.Count


def GetDocumentData(section=None, entry=None):
    """Returns a user data item from the current document
    Parameters:
      section[opt] = section name. If omitted, all section names are returned
      entry[opt] = entry name. If omitted, all entry names for section are returned
    Returns:
      list of all section names if section name is omitted
      list of all entry names for a section if entry is omitted
      value of the entry if both section and entry are specified
    """
    if section is None:
        rc = scriptcontext.doc.Strings.GetSectionNames()
        if rc: return list(rc)
        return []
    if entry is None:
        rc = scriptcontext.doc.Strings.GetEntryNames(section)
        if rc: return list(rc)
        return []
    return scriptcontext.doc.Strings.GetValue(section, entry)


def GetUserText(object_id, key=None, attached_to_geometry=False):
    """Returns user text that is stored on an object.
    Parameters:
      object_id = the object's identifies
      key[opt] = the key name. If omitted all key names for an object are returned
      attached_to_geometry[opt] = location on the object to retrieve the user text
    Returns:
      if key is specified, the associated value if successful
      if key is not specified, a list of key names if successful
    """
    obj = rhutil.coercerhinoobject(object_id, True, True)
    source = None
    if attached_to_geometry: source = obj.Geometry
    else: source = obj.Attributes
    rc = None
    if key:
        return source.GetUserString(key)
    else:
        userstrings = source.GetUserStrings()
        rc = [userstrings.GetKey(i) for i in range(userstrings.Count)]
        return rc


def IsDocumentData():
    """Verifies the current document contains  user data
    Returns:
      True or False indicating the presence of Script user data
    """
    return scriptcontext.doc.Strings.Count>0


def IsUserText(object_id):
    """Verifies that an object contains user text
    Returns:
      0 = no user text
      1 = attribute user text
      2 = geometry user text
      3 = both attribute and geometry user text
    """
    obj = rhutil.coercerhinoobject(object_id, True, True)
    rc = 0
    if obj.Attributes.UserStringCount>0: rc = rc|1
    if obj.Geometry.UserStringCount>0: rc = rc|2
    return rc


def SetDocumentData(section, entry, value):
    """Adds or sets a user data string to the current document
    Parameters:
      section = the section name
      entry = the entry name
      value  = the string value
    Returns:
      The previous value
    """
    return scriptcontext.doc.Strings.SetString(section, entry, value)


def SetUserText(object_id, key, value=None, attach_to_geometry=False):
    """Sets or removes user text stored on an object.
    Parameters:
      object_id = the object's identifier
      key = the key name to set
      value[opt] = the string value to set. If omitted, the key/value pair
          specified by key will be deleted
      attach_to_geometry[opt] = location on the object to store the user text
    Returns:
      True or False indicating success or failure 
    """
    obj = rhutil.coercerhinoobject(object_id, True, True)
    if attach_to_geometry: return obj.Geometry.SetUserString(key, value)
    return obj.Attributes.SetUserString(key, value)
