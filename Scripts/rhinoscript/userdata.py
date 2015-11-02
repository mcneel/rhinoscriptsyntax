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
    Example:
      import rhinoscriptsyntax as rs
      rs.DeleteDocumentData( "MySection1", "MyEntry1" )
      rs.DeleteDocumentData( "MySection1", "MyEntry2" )
      rs.DeleteDocumentData( "MySection2", "MyEntry1" )
    See Also:
      DocumentDataCount
      GetDocumentData
      IsDocumentData
      SetDocumentData
    """
    return scriptcontext.doc.Strings.Delete(section, entry)


def DocumentDataCount():
    """Returns the number of user data strings in the current document
    Parameters:
      None
    Returns:
      the number of user data strings in the current document
    Example:
      import rhinoscriptsyntax as rs
      count = rs.DocumentDataCount()
      print "RhinoScript document user data count: ", count
    See Also:
      DeleteDocumentData
      GetDocumentData
      IsDocumentData
      SetDocumentData
    """
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
    Example:
      import rhinoscriptsyntax as rs
      value = rs.GetDocumentData("MySection1", "MyEntry1")
      print value
      
      value = rs.GetDocumentData("MySection1", "MyEntry2")
      print value
      
      value = rs.GetDocumentData("MySection2", "MyEntry1")
      print value
    See Also:
      DeleteDocumentData
      DocumentDataCount
      IsDocumentData
      SetDocumentData
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


def GetDocumentUserText(key=None):
    """Returns user text stored in the document
    Parameters:
      key[opt] = key to use for retrieving user text. If empty, all keys are returned
    Returns:
      If key is specified, then the associated value if successful.
      If key is not specified, then a list of key names if successful.
      If not successful, or on error.
    Example:
      import rhinoscriptsyntax as rs
      print rs.GetDocumentUserText("Designer")
      print rs.GetDocumentUserText("Notes")
    See Also:
      SetDocumentUserText
    """
    if key: return scriptcontext.doc.Strings.GetValue(key)
    return [scriptcontext.doc.Strings.GetKey(i) for i in range(scriptcontext.doc.Strings.Count)]


def GetUserText(object_id, key=None, attached_to_geometry=False):
    """Returns user text stored on an object.
    Parameters:
      object_id = the object's identifies
      key[opt] = the key name. If omitted all key names for an object are returned
      attached_to_geometry[opt] = location on the object to retrieve the user text
    Returns:
      if key is specified, the associated value if successful
      if key is not specified, a list of key names if successful
    Example:
      import rhinoscriptsyntax as rs
      obj = rs.GetObject("Select object")
      if obj:
      print rs.GetUserText(obj, "PartNo")
      print rs.GetUserText(obj, "Price")
    See Also:
      IsUserText
      SetUserText
    """
    obj = rhutil.coercerhinoobject(object_id, True, True)
    source = None
    if attached_to_geometry: source = obj.Geometry
    else: source = obj.Attributes
    rc = None
    if key: return source.GetUserString(key)
    userstrings = source.GetUserStrings()
    return [userstrings.GetKey(i) for i in range(userstrings.Count)]


def IsDocumentData():
    """Verifies the current document contains user data
    Parameters:
      None
    Returns:
      True or False indicating the presence of Script user data
    Example:
      import rhinoscriptsyntax as rs
      result = rs.IsDocumentData()
      if result:
      print "This document contains Script document user data"
      else:
      print "This document contains no Script document user data"
    See Also:
      DeleteDocumentData
      DocumentDataCount
      GetDocumentData
      SetDocumentData
    """
    return scriptcontext.doc.Strings.Count>0


def IsUserText(object_id):
    """Verifies that an object contains user text
    Parameters:
      object_id = the object's identifier
    Returns:
      0 = no user text
      1 = attribute user text
      2 = geometry user text
      3 = both attribute and geometry user text
    Example:
      import rhinoscriptsyntax as rs
      obj = rs.GetObject("Select object") 
      if obj:
      usertext_type = rs.IsUserText(obj)
      if usertext_type==0: print "Object has no user text"
      elif usertext_type==1: print "Object has attribute user text"
      elif usertext_type==2: print "Object has geometry user text"
      elif usertext_type==3: print "Object has attribute and geometry user text"
    See Also:
      GetUserText
      SetUserText
    """
    obj = rhutil.coercerhinoobject(object_id, True, True)
    rc = 0
    if obj.Attributes.UserStringCount: rc = rc|1
    if obj.Geometry.UserStringCount: rc = rc|2
    return rc


def SetDocumentData(section, entry, value):
    """Adds or sets a user data string to the current document
    Parameters:
      section = the section name
      entry = the entry name
      value  = the string value
    Returns:
      The previous value
    Example:
      import rhinoscriptsyntax as rs
      rs.SetDocumentData( "MySection1", "MyEntry1", "MyValue1" )
      rs.SetDocumentData( "MySection1", "MyEntry2", "MyValue2" )
      rs.SetDocumentData( "MySection2", "MyEntry1", "MyValue1" )
    See Also:
      DeleteDocumentData
      DocumentDataCount
      GetDocumentData
      IsDocumentData
    """
    return scriptcontext.doc.Strings.SetString(section, entry, value)


def SetDocumentUserText(key, value=None):
    """Sets or removes user text stored in the document
    Parameters:
      key = key name to set
      value[opt] = The string value to set. If omitted the key/value pair
        specified by key will be deleted
    Returns:
      True or False indicating success
    Example:
      import rhinoscriptsyntax as rs
      rs.SetDocumentUserText("Designer", "Steve Baer")
      rs.SetDocumentUserText("Notes", "Added some layer and updated some geometry")
    See Also:
      GetDocumentUserText
    """
    if value: scriptcontext.doc.Strings.SetString(key,value)
    else: scriptcontext.doc.Strings.Delete(key)
    return True


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
    Example:
      import rhinoscriptsyntax as rs
      obj = rs.GetObject("Select object")
      if obj:
      rs.SetUserText( obj, "PartNo", "KM40-4960" )
      rs.SetUserText( obj, "Price", "1.25" )
    See Also:
      GetUserText
      IsUserText
    """
    obj = rhutil.coercerhinoobject(object_id, True, True)
    if type(key) is not str: key = str(key)
    if value and type(value) is not str: value = str(value)
    if attach_to_geometry: return obj.Geometry.SetUserString(key, value)
    return obj.Attributes.SetUserString(key, value)