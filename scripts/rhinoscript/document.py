import scriptcontext
import Rhino
import System.Enum

def CreatePreviewImage(filename, view=None, size=None, flags=0, wireframe=False):
    """Creates a bitmap preview image of the current model
    Parameters:
      filename = name of the bitmap file to create
      view[opt] = title of the view. If omitted, the active view is used
      size[opt] = two integers that specify width and height of the bitmap
      flags[opt] = Bitmap creation flags. Can be the combination of:
          1 = honor object highlighting
          2 = draw construction plane
          4 = use ghosted shading
      wireframe[opt] = If True then a wireframe preview image. If False,
          a rendered image will be created
    Returns:
      True or False indicating success or failure
    """
    rhview = scriptcontext.doc.Views.ActiveView
    if view is not None:
        rhview = scriptcontext.doc.Views.Find(view, False)
        if rhview is None: return False
    rhsize = rhview.ClientRectangle.Size
    if size: rhsize = System.Drawing.Size(size[0], size[1])
    ignore_highlights = (flags&1)!=1
    drawcplane = (flags&2)==2
    useghostedshading = (flags&4)==4
    if wireframe:
        return rhview.CreateWireframePreviewImage(filename, rhsize, ignore_highlights, drawcplane)
    else:
        return rhview.CreateShadedPreviewImage(filename, rhsize, ignore_highlights, drawcplane, useghostedshading)


def DocumentModified(modified=None):
    """Returns or sets the document's modified flag. This flag indicates whether
    or not any changes to the current document have been made. NOTE: setting the
    document modified flag to False will prevent the "Do you want to save this
    file..." from displaying when you close Rhino.
    Parameters:
      modified [optional] = the modified state, either True or False
    Returns:
      if no modified state is specified, the current modified state
      if a modified state is specified, the previous modified state
    """
    oldstate = scriptcontext.doc.Modified
    if modified is not None and modified!=oldstate:
        scriptcontext.doc.Modified = modified
    return oldstate


def DocumentName():
    "Returns the name of the currently loaded Rhino document (3DM file)"
    return scriptcontext.doc.Name


def DocumentPath():
    "Returns path of the currently loaded Rhino document (3DM file)"
    return scriptcontext.doc.Path


def EnableRedraw(enable=True):
    """Enables or disables screen redrawing
    Returns:
      previous screen redrawing state
    """
    old = scriptcontext.doc.Views.RedrawEnabled
    if old!=enable: scriptcontext.doc.Views.RedrawEnabled = enable
    return old


def ExtractPreviewImage(filename, modelname=None):
    """Extracts the bitmap preview image from the specified model (.3dm)
    Parameters:
      filename = name of the bitmap file to create. The extension of
         the filename controls the format of the bitmap file created.
         (.bmp, .tga, .jpg, .jpeg, .pcx, .png, .tif, .tiff)
      modelname [opt] = The model (.3dm) from which to extract the
         preview image. If omitted, the currently loaded model is used.
    Returns:
      True or False indicating success or failure
    """
    return scriptcontext.doc.ExtractPreviewImage(filename, modelname)


def IsDocumentModified():
    "Verifies that the current document has been modified in some way"
    return scriptcontext.doc.Modified


def Notes(newnotes=None):
    """Returns or sets the document's notes. Notes are generally created
    using Rhino's Notes command
    Parameters:
      newnotes[opt] = new notes to set
    Returns:
      if newnotes is omitted, the current notes if successful
      if newnotes is specified, the previous notes if successful
    """
    old = scriptcontext.doc.Notes
    if newnotes is not None: scriptcontext.doc.Notes = newnotes
    return old


def ReadFileVersion():
    """Returns the file version of the current document. Use this function to
    determine which version of Rhino last saved the document. Note, this
    function will not return values from referenced or merged files.
    """
    return scriptcontext.doc.ReadFileVersion()


def Redraw():
    "Redraws all views"
    scriptcontext.doc.Views.Redraw()


def UnitAbsoluteTolerance(tolerance=None, in_model_units=True):
    """Resturns or sets the document's absolute tolerance. Absolute tolerance
    is measured in drawing units. See Rhino's document properties command
    (Units and Page Units Window) for details
    Parameters:
      tolerance [opt] = the absolute tolerance to set
      in_model_units[opt] = Return or modify the document's model units (True)
                            or the document's page units (False)
    Returns:
      if tolerance is not specified, the current absolute tolerance
      if tolerance is specified, the previous absolute tolerance
    """
    rc = 0
    if in_model_units:
        rc = scriptcontext.doc.ModelAbsoluteTolerance
        if tolerance is not None:
            scriptcontext.doc.ModelAbsoluteTolerance = tolerance
    else:
        rc = scriptcontext.doc.PageAbsoluteTolerance
        if tolerance is not None:
            scriptcontext.doc.PageAbsoluteTolerance = tolerance
    return rc


def UnitAngleTolerance(angle_tolerance_degrees=None, in_model_units=True):
    """Returns or sets the document's angle tolerance. Angle tolerance is
    measured in degrees. See Rhino's DocumentProperties command
    (Units and Page Units Window) for details
    Parameters:
      angle_tolerance_degrees [opt] = the angle tolerance to set
      in_model_units [opt] = Return or modify the document's model units (True)
                             or the document's page units (False)
    Returns:
      if angle_tolerance_degrees is not specified, the current angle tolerance
      if angle_tolerance_degrees is specified, the previous angle tolerance
    """
    rc = 0
    if in_model_units:
        rc = scriptcontext.doc.ModelAngleToleranceDegrees
        if angle_tolerance_degrees is not None:
            scriptcontext.doc.ModelAngleToleranceDegrees = angle_tolerance_degrees
    else:
        rc = scriptcontext.doc.PageAngleToleranceDegrees
        if angle_tolerance_degrees is not None:
            scriptcontext.doc.PageAngleToleranceDegrees = angle_tolerance_degrees
    return rc


def UnitRelativeTolerance(relative_tolerance=None, in_model_units=True):
    """Returns or sets the document's relative tolerance. Relative tolerance
    is measured in percent. See Rhino's DocumentProperties command
    (Units and Page Units Window) for details
    Parameters:
      relative_tolerance [opt] = the relative tolerance in percent
      in_model_units [opt] = Return or modify the document's model units (True)
                             or the document's page units (False)
    Returns:
      if relative_tolerance is not specified, the current tolerance in percent
      if relative_tolerance is specified, the previous tolerance in percent
    """
    rc = 0
    if in_model_units:
        rc = scriptcontext.doc.ModelRelativeTolerance
        if relative_tolerance is not None:
            scriptcontext.doc.ModelRelativeTolerance = relative_tolerance
    else:
        rc = scriptcontext.doc.PageRelativeTolerance
        if relative_tolerance is not None:
            scriptcontext.doc.PageRelativeTolerance = relative_tolerance
    return rc


def UnitScale(to_system, from_system=None):
  """Returns the scale factor for changing between unit systems.
  Parameters:
    to_system = The unit system to convert to. The unit systems are are:
       0 - No unit system
       1 - Microns (1.0e-6 meters)
       2 - Millimeters (1.0e-3 meters)
       3 - Centimeters (1.0e-2 meters)
       4 - Meters
       5 - Kilometers (1.0e+3 meters)
       6 - Microinches (2.54e-8 meters, 1.0e-6 inches)
       7 - Mils (2.54e-5 meters, 0.001 inches)
       8 - Inches (0.0254 meters)
       9 - Feet (0.3408 meters, 12 inches)
      10 - Miles (1609.344 meters, 5280 feet)
      11 - *Reserved for custom Unit System*
      12 - Angstroms (1.0e-10 meters)
      13 - Nanometers (1.0e-9 meters)
      14 - Decimeters (1.0e-1 meters)
      15 - Dekameters (1.0e+1 meters)
      16 - Hectometers (1.0e+2 meters)
      17 - Megameters (1.0e+6 meters)
      18 - Gigameters (1.0e+9 meters)
      19 - Yards (0.9144  meters, 36 inches)
      20 - Printer point (1/72 inches, computer points)
      21 - Printer pica (1/6 inches, (computer picas)
      22 - Nautical mile (1852 meters)
      23 - Astronomical (1.4959787e+11)
      24 - Lightyears (9.46073e+15 meters)
      25 - Parsecs (3.08567758e+16)
    from_system [opt] = the unit system to convert from (see above). If omitted,
        the document's current unit system is used
  Returns:
    the scale factor for changing between unit systems
  """
  if from_system is None:
      from_system = scriptcontext.doc.ModelUnitSystem
  if type(from_system) is int:
      from_system = System.Enum.ToObject(Rhino.UnitSystem, from_system)
  if type(to_system) is int:
      to_system = System.Enum.ToObject(Rhino.UnitSystem, to_system)
  return Rhino.RhinoMath.UnitScale(from_system, to_system)


def UnitSystem(unit_system=None, scale=False, in_model_units=True):
    """Returns or sets the document's units system. See Rhino's DocumentProperties
    command (Units and Page Units Window) for details
    Parameters:
      unit_system = The unit system to set the document to. The unit systems are:
         0 - No unit system
         1 - Microns (1.0e-6 meters)
         2 - Millimeters (1.0e-3 meters)
         3 - Centimeters (1.0e-2 meters)
         4 - Meters
         5 - Kilometers (1.0e+3 meters)
         6 - Microinches (2.54e-8 meters, 1.0e-6 inches)
         7 - Mils (2.54e-5 meters, 0.001 inches)
         8 - Inches (0.0254 meters)
         9 - Feet (0.3408 meters, 12 inches)
        10 - Miles (1609.344 meters, 5280 feet)
        11 - *Reserved for custom Unit System*
        12 - Angstroms (1.0e-10 meters)
        13 - Nanometers (1.0e-9 meters)
        14 - Decimeters (1.0e-1 meters)
        15 - Dekameters (1.0e+1 meters)
        16 - Hectometers (1.0e+2 meters)
        17 - Megameters (1.0e+6 meters)
        18 - Gigameters (1.0e+9 meters)
        19 - Yards (0.9144  meters, 36 inches)
        20 - Printer point (1/72 inches, computer points)
        21 - Printer pica (1/6 inches, (computer picas)
        22 - Nautical mile (1852 meters)
        23 - Astronomical (1.4959787e+11)
        24 - Lightyears (9.46073e+15 meters)
        25 - Parsecs (3.08567758e+16)
      scale [opt] = Scale existing geometry based on the new unit system.
          If not specified, any existing geometry is not scaled (False)
      in_model_units [opt] = Return or modify the document's model units (True)
          or the document's page units (False). The default is True.
    Returns:
      if unit_system is no specified, then the current unit system
      if unit_system is specified, then the previous unit system
      None on error
    """
    if (unit_system is not None and (unit_system<1 or unit_system>25)):
        raise ValueError("unit_system value of %s is not valid"%unit_system)
    rc = None
    if in_model_units:
        rc = int(scriptcontext.doc.ModelUnitSystem)
        if unit_system is not None:
            unit_system = System.Enum.ToObject(Rhino.UnitSystem, unit_system)
            scriptcontext.doc.AdjustModelUnitSystem(unit_system, scale)
    else:
        rc = int(scriptcontext.doc.PageUnitSystem)
        if unit_system is not None:
            unit_system = System.Enum.ToObject(Rhino.UnitSystem, unit_system)
            scriptcontext.doc.AdjustPageUnitSystem(unit_system, scale)
    return rc
