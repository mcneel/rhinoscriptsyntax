import Rhino
import System.Drawing.Color
import System.Array
import System.Guid
import time
import System.Windows.Forms.Clipboard
import scriptcontext
import math
import string

#should work all of the time unless we can't find the standard lib
__cfparse = None
try:
    import ConfigParser
except ImportError:
    __cfparse = None
else:
    __cfparse = ConfigParser

def Angle(point1, point2, plane=True):
    """
    Measures the angle between two points
    Parameters:
      point1, point2: the input points
      plane[opt] = Boolean or Plane
        If True, angle calculation is based on the world coordinate system.
        If False, angle calculation is based on the active construction plane
        If a plane is provided, angle calculation is with respect to this plane
    Returns:
      tuple containing the following elements if successful
        element 0 = the X,Y angle in degrees
        element 1 = the elevation
        element 2 = delta in the X direction
        element 3 = delta in the Y direction
        element 4 = delta in the Z direction
      None if not successful
    """
    pt1 = coerce3dpoint(point1)
    if pt1 is None:
        pt1 = coercerhinoobject(point1)
        if isinstance(pt1, Rhino.DocObjects.PointObject): pt1 = pt1.Geometry.Location
        else: pt1=None
    pt2 = coerce3dpoint(point2)
    if pt2 is None:
        pt2 = coercerhinoobject(point2)
        if isinstance(pt2, Rhino.DocObjects.PointObject): pt2 = pt2.Geometry.Location
        else: pt2=None
    point1 = pt1
    point2 = pt2
    if point1 is None or point2 is None: return scriptcontext.errorhandler()
    vector = point2 - point1
    x = vector.X
    y = vector.Y
    z = vector.Z
    if plane!=True:
        plane = coerceplane(plane)
        if plane is None:
            plane = scriptcontext.doc.Views.ActiveView.ActiveViewport.ConstructionPlane()
        vfrom = point1 - plane.Origin
        vto = point2 - plane.Origin
        x = vto * plane.XAxis - vfrom * plane.XAxis
        y = vto * plane.YAxis - vfrom * plane.YAxis
        z = vto * plane.ZAxis - vfrom * plane.ZAxis
    h = math.sqrt( x * x + y * y)
    angle_xy = math.degrees( math.atan2( y, x ) )
    elevation = math.degrees( math.atan2( z, h ) )
    return angle_xy, elevation, x, y, z


def Angle2(line1, line2):
    """Measures the angle between two lines"""
    line1 = coerceline(line1)
    line2 = coerceline(line2)
    if line1 is None or line2 is None: return scriptcontext.errorhandler()
    vec0 = line1.To - line1.From
    vec1 = line2.To - line2.From
    if( not vec0.Unitize() or not vec1.Unitize() ): return scriptcontext.errorhandler()
    dot = vec0 * vec1
    dot = clamp(-1,1,dot)
    angle = math.acos(dot)
    reflex_angle = 2.0*math.pi - angle
    angle = math.degrees(angle)
    reflex_angle = math.degrees(reflex_angle)
    return angle, reflex_angle


def ClipboardText(text=None):
    """
    Returns or sets a text string to the Windows clipboard
    Parameters:
      text: [opt] text to set
    Returns:
      if text is not specified, the current text in the clipboard
      if text is specified, the previous text in the clipboard
      None if not successful, or on error
    """
    rc = None
    if( System.Windows.Forms.Clipboard.ContainsText() ):
        rc = System.Windows.Forms.Clipboard.GetText()
    if( text!=None ):
        System.Windows.Forms.Clipboard.SetText(str(text))
    return rc


def ColorAdjustLuma( rgb, luma, scale=False ):
    """
    Changes the luminance of a red-green-blue value. Hue and saturation are not
    affected
    Parameters:
      rgb = initial rgb value
      luma = The luminance in units of 0.1 percent of the total range. A
          value of luma = 50 corresponds to 5 percent of the maximum luminance
      scale[opt] = if True, luma specifies how much to increment or decrement the
          current luminance. If False, luma specified the absolute luminance.
    Returns:
      modified rgb value if successful
      None on error
    """
    rgb = coercecolor(rgb)
    if rgb is None: return scriptcontext.errorhandler()
    hsl = Rhino.Display.ColorHSL(rgb)
    luma = luma / 1000.0
    if scale==True: luma = hsl.L + luma
    hsl.L = luma
    rgb = hsl.ToArgbColor()
    return rgb.ToArgb()


def ColorBlueValue(rgb):
    "Retrieves intensity value for the blue component of an RGB color"
    rgb = coercecolor(rgb)
    if rgb is None: return scriptcontext.errorhandler()
    return rgb.B


def ColorGreenValue(rgb):
    "Retrieves intensity value for the green component of an RGB color"
    rgb = coercecolor(rgb)
    if rgb is None: return scriptcontext.errorhandler()
    return rgb.G


def ColorHLSToRGB(hls):
    "Converts colors from hue-lumanence-saturation to RGB"
    if len(hls)==3:
        hls = Rhino.Display.ColorHSL(hls[0]/240.0, hls[2]/240.0, hls[1]/240.0)
    elif len(hls)==4:
        hls = Rhino.Display.ColorHSL(hls[3]/240.0, hls[0]/240.0, hls[2]/240.0, hls[1]/240.0)
    else:
        return scriptcontext.errorhandler()
    rgb = hls.ToArgbColor()
    return rgb.ToArgb()


def ColorRedValue(rgb):
    "Retrieves intensity value for the red component of an RGB color"
    rgb = coercecolor(rgb)
    if rgb is None: return scriptcontext.errorhandler()
    return rgb.R


def ColorRGBToHLS(rgb):
    "Converts colors from RGB to HLS"
    rgb = coercecolor(rgb)
    if rgb is None: return scriptcontext.errorhandler()
    hls = Rhino.Display.ColorHSL(rgb)
    return (hls.H, hls.S, hls.L, hls.A)


def CullDuplicatePoints(points, tolerance=-1):
    """
    Removes duplicates from a list of 3-D points.
    Parameters:
      points = A list of 3-D points.
      tolerance [opt] = The minimum distance between points. Points that fall
                        within this tolerance will be discarded. If omitted,
                        Rhino's internal zero tolerance is used.
    Returns:
      A list of 3-D points with duplicates removed if successful.
      None if not successful or on error.
    """
    points = coerce3dpointlist(points)
    if points is None: return scriptcontext.errorhandler()
    if tolerance is None or tolerance < 0:
        tolerance = Rhino.RhinoMath.ZeroTolerance
    return Rhino.Geometry.Point3d.CullDuplicates(points, tolerance)


def Distance(point1, point2):
    """
    Measures the distance between two 3-D points, or between a 3-D point and
    an array of 3-D points.
    Parameters:
      point1 = The first 3-D point.
      point2 = The second 3-D point or list of 3-D points.
    Returns:
      If point2 is a 3-D point then the distance if successful.
      If point2 is a list of points, then an list of distances if successful.
      None if not successful, or on error.
    """
    from_pt = coerce3dpoint(point1)
    to_pt = coerce3dpoint(point2)
    if from_pt and to_pt:
        vec = to_pt - from_pt
        return vec.Length
    # check if we have a list of points
    to_pt = coerce3dpointlist(point2)
    if to_pt is None: return scriptcontext.errorhandler()
    distances = []
    for point in to_pt:
        vec = point - from_pt
        distances.append(vec.Length)
    if len(distances)==0: return scriptcontext.errorhandler()
    return distances


def GetSettings(filename, section=None, entry=None):
    """
    Returns a string from a specified section in a Windows-style initialization file.
    Parameters:
      filename = name of the initialization file
      section[opt] = section containing the entry
      entry[opt] = entry whose associated string is to be returned
    Returns:
      If section is not specified, a list containing all section names
      If entry is not specified, a list containing all entry names for a given section
      If section and entry are specied, a value for entry
      None if not successful or on error
    """
    if __cfparse is None: return scriptcontext.errorhandler()
    try:
        cp = ConfigParser.ConfigParser()
        cp.read(filename)
        if not section: return cp.sections()
        section = string.lower(section)
        if not entry: return cp.options(section)
        entry = string.lower(entry)
        return cp.get(section, entry)
    except IOError:
        return scriptcontext.errorhander()
    return scriptcontext.errorhandler()


def Polar(point, angle_degrees, distance, plane=None):
    """
    Returns the 3D point that is a specified angle and distance
    from a 3D point
    Parameters:
      point = the point to transform
      plane[opt] = plane to base the transformation. If omitted, the world
        x-y plane is used
    Returns:
      resulting point is successful
      None on error
    """
    point = coerce3dpoint(point)
    if point is None: return scriptcontext.errorhandler()
    plane = coerceplane(plane)
    angle = math.radians(angle_degrees)
    if plane is None: plane = Rhino.Geometry.Plane.WorldXY
    offset = plane.XAxis
    offset.Unitize()
    offset *= distance
    rc = point+offset
    xform = Rhino.Geometry.Transform.Rotation(angle, plane.ZAxis, point)
    rc.Transform(xform)
    return rc


def Sleep(milliseconds):
    """
    Suspends execution of a running script for the specified interval
    """
    sec = milliseconds / 1000.0
    time.sleep(sec)
    Rhino.RhinoApp.Wait() #keep the message pump alive
    

def SortPointList(points, tolerance=None):
    """
    Sorts a list of points so they will be connected in a "reasonable" polyline order
    Parameters:
      points = the points to sort
      tolerance[opt] = minimum distance between points. Points that fall within this tolerance
        will be discarded. If omitted, Rhino's internal zero tolerance is used.
    Returns:
      a list of sorted 3-D points if successful
      None on error
    """
    points = coerce3dpointlist(points)
    if points is None: return scriptcontext.errorhandler()
    if tolerance is None: tolerance = Rhino.RhinoMath.ZeroTolerance
    return Rhino.Geometry.Point3d.SortAndCullPointList(points, tolerance)


def SortPoints(points, ascending=True, order=0):
    "Sorts an array of 3D points"
    def __cmpXYZ( a, b ):
        rc = cmp(a.X, b.X)
        if rc==0: rc = cmp(a.Y, b.Y)
        if rc==0: rc = cmp(a.Z, b.Z)
        return rc
    def __cmpXZY( a, b ):
        rc = cmp(a.X, b.X)
        if rc==0: rc = cmp(a.Z, b.Z)
        if rc==0: rc = cmp(a.Y, b.Y)
        return rc
    def __cmpYXZ( a, b ):
        rc = cmp(a.Y, b.Y)
        if rc==0: rc = cmp(a.X, b.X)
        if rc==0: rc = cmp(a.Z, b.Z)
        return rc
    def __cmpYZX( a, b ):
        rc = cmp(a.Y, b.Y)
        if rc==0: rc = cmp(a.Z, b.Z)
        if rc==0: rc = cmp(a.X, b.X)
        return rc
    def __cmpZXY( a, b ):
        rc = cmp(a.Z, b.Z)
        if rc==0: rc = cmp(a.X, b.X)
        if rc==0: rc = cmp(a.Y, b.Y)
        return rc
    def __cmpZYX( a, b ):
        rc = cmp(a.Z, b.Z)
        if rc==0: rc = cmp(a.Y, b.Y)
        if rc==0: rc = cmp(a.X, b.X)
        return rc
    
    sortfunc = __cmpXYZ
    if order==1: sortfunc = __cmpXZY
    elif order==2: sortfunc = __cmpYXZ
    elif order==3: sortfunc = __cmpYZX
    elif order==4: sortfunc = __cmpZXY
    elif order==5: sortfunc = __cmpZYX
    reverse = not ascending
    return sorted(points, sortfunc, None, reverse)


def Str2Pt(point):
    "converts a formatted string value into a 3-D point value"
    return coerce3dpoint(point)


def clamp(lowvalue, highvalue, value):
    if lowvalue>=highvalue: raise Exception("lowvalue must be less than highvalue")
    if value<lowvalue: return lowvalue
    if value>highvalue: return highvalue
    return value


def frange(start, stop, step):
    "a float version of the range function"
    rc = []
    x = start
    while( x<=stop ):
        rc.append(x)
        x+=step
    return rc


def coerce3dpoint(point):
    "Convert input into a Rhino.Geometry.Point3d if possible."
    if point is None or type(point) is Rhino.Geometry.Point3d: return point
    if type(point) is list or type(point) is tuple:
        length = len(point)
        if length==3 and type(point[0]) is not list and type(point[0]) is not Rhino.Geometry.Point3d:
            return Rhino.Geometry.Point3d(point[0], point[1], point[2])
        return None
    if type(point) is Rhino.Geometry.Vector3d or type(point) is Rhino.Geometry.Point3f:
        return Rhino.Geometry.Point3d(point.X, point.Y, point.Z)
    if type(point) is str:
        point = point.split(',')
        return Rhino.Geometry.Point3d( float(point[0]), float(point[1]), float(point[2]) )
    return None


def coerce2dpoint(point):
    "Convert input into a Rhino.Geometry.Point2d if possible."
    if point is None or type(point) is Rhino.Geometry.Point2d: return point
    if type(point) is list or type(point) is tuple:
        length = len(point)
        if length==2 and type(point[0]) is not list and type(point[0]) is not Rhino.Geometry.Point2d:
            return Rhino.Geometry.Point2d(point[0], point[1])
        return None
    if type(point) is Rhino.Geometry.Vector3d or type(point) is Rhino.Geometry.Point3d:
        return Rhino.Geometry.Point2d(point.X, point.Y)
    if type(point) is str:
        point = point.split(',')
        return Rhino.Geometry.Point2d( float(point[0]), float(point[1]) )
    return None


def coerce3dvector(vector):
    "Convert input into a Rhino.Geometry.Vector3d if possible."
    if vector is None or type(vector) is Rhino.Geometry.Vector3d: return vector
    if type(vector) is list or type(vector) is tuple:
        length = len(vector)
        if length==3 and type(vector[0]) is not list:
            return Rhino.Geometry.Vector3d(vector[0], vector[1], vector[2])
        return None
    if type(vector) is Rhino.Geometry.Point3d or type(vector) is Rhino.Geometry.Point3f:
        return Rhino.Geometry.Vector3d(vector.X, vector.Y, vector.Z)
    if type(vector) is Rhino.Geometry.Vector3f:
        return Rhino.Geometry.Vector3d(vector.X, vector.Y, vector.Z)
    return None


def coerce3dpointlist(points):
    if points is None: return None
    if isinstance(points, System.Array[Rhino.Geometry.Point3d]):
        return list(points)
    if isinstance(points, Rhino.Collections.Point3dList): return list(points)
    if type(points) is list or type(points) is tuple:
        count = len(points)
        if count>0 and (coerce3dpoint(points[0]) is not None):
            return [coerce3dpoint(points[i]) for i in xrange(count)]
        elif count>2 and type(points[0]) is not list:
            point_count = count/3
            rc = []
            for i in xrange(point_count):
                pt = Rhino.Geometry.Point3d(points[i*3], points[i*3+1], points[i*3+2])
                rc.append(pt)
            return rc
    return None


def coerce2dpointlist(points):
    if points is None or isinstance(points, System.Array[Rhino.Geometry.Point2d]):
        return points
    if type(points) is list or type(points) is tuple:
        count = len(points)
        if count>0 and type(points[0]) is Rhino.Geometry.Point2d:
            rc = System.Array.CreateInstance(Rhino.Geometry.Point2d, count)
            for i in xrange(count): rc[i] = points[i]
            return rc
        elif count>1 and type(points[0]) is not list:
            point_count = count/2
            rc = System.Array.CreateInstance(Rhino.Geometry.Point2d,point_count)
            for i in xrange(point_count):
                rc[i] = Rhino.Geometry.Point2d(points[i*2], points[i*2+1])
            return rc
        elif count>0 and type(points[0]) is list:
            point_count = count
            rc = System.Array.CreateInstance(Rhino.Geometry.Point2d,point_count)
            for i in xrange(point_count):
                pt = points[i]
                rc[i] = Rhino.Geometry.Point2d(pt[0],pt[1])
            return rc
        return None
    return None


def coerceplane(plane):
    "Convert input into a Rhino.Geometry.Plane if possible."
    if type(plane) is Rhino.Geometry.Plane: return plane
    if plane is None: return None
    if type(plane) is list or type(plane) is tuple:
        length = len(plane)
        if length==3 and type(plane[0]) is not list:
            rc = Rhino.Geometry.Plane.WorldXY
            rc.Origin = Rhino.Geometry.Point3d(plane[0],plane[1],plane[2])
            return rc
        if length==9 and type(plane[0]) is not list:
            origin = Rhino.Geometry.Point3d(plane[0],plane[1],plane[2])
            xpoint = Rhino.Geometry.Point3d(plane[3],plane[4],plane[5])
            ypoint = Rhino.Geometry.Point3d(plane[6],plane[7],plane[8])
            rc     = Rhino.Geometry.Plane(origin, xpoint, ypoint)
            return rc
        if length==3 and (type(plane[0]) is list or type(plane[0]) is tuple):
            origin = Rhino.Geometry.Point3d(plane[0][0],plane[0][1],plane[0][2])
            xpoint = Rhino.Geometry.Point3d(plane[1][0],plane[1][1],plane[1][2])
            ypoint = Rhino.Geometry.Point3d(plane[2][0],plane[2][1],plane[2][2])
            rc     = Rhino.Geometry.Plane(origin, xpoint, ypoint)
            return rc
    return None


def coercexform(xform):
    "Convert input into a Rhino.Transform if possible."
    t = type(xform)
    if t is Rhino.Geometry.Transform: return xform
    if( (t is list or t is tuple) and len(xform)==4 and len(xform[0])==4):
        xf = Rhino.Geometry.Transform()
        for i in range(4):
            for j in range(4):
                xf[i,j] = xform[i][j]
        return xf
    return None


def coerceguid(id):
    if type(id) is System.Guid: return id
    if type(id) is str and len(id)>30:
        try:
            id = System.Guid(id)
            return id
        except:
            pass
    if (type(id) is list or type(id) is tuple) and len(id)==1:
        return coerceguid(id[0])
    return None


def coerceguidlist(ids):
    if ids is None: return None
    rc = []
    if( type(ids) is list or type(ids) is tuple ): pass
    else: ids = [ids]
    for id in ids:
        id = coerceguid(id)
        if id: rc.append(id)
    if len(rc)==0: return None
    return rc


def coerceboundingbox(bbox):
    if bbox is None or type(bbox) is Rhino.Geometry.BoundingBox: return bbox
    points = coerce3dpointlist(bbox)
    if points: return Rhino.Geometry.BoundingBox(points)
    return None


def coercecolor(c):
    if c is None or type(c) is System.Drawing.Color: return c
    if type(c) is list or type(c) is tuple:
        if len(c)==3: return System.Drawing.Color.FromArgb(c[0], c[1], c[2])
        elif len(c)==4: return System.Drawing.Color.FromArgb(c[0], c[1], c[2], c[3])
    if type(c)==type(1): return System.Drawing.Color.FromArgb(c)
    return None


def coerceline(line):
    if line is None or type(line) is Rhino.Geometry.Line: return line
    points = coerce3dpointlist(line)
    if points and len(points)>1: return Rhino.Geometry.Line(points[0], points[1])
    return None


def coercebrep( id ):
    "attempt to get polysurface geometry from the document with a given id"
    id = coerceguid(id)
    if id is None: return None
    objref = Rhino.DocObjects.ObjRef(id)
    brep = objref.Brep()
    objref.Dispose()
    return brep


def coercecurve( id, segment_index=-1 ):
    "attempt to get curve geometry from the document with a given id"
    if isinstance(id, Rhino.Geometry.Curve): return id
    if type(id) is Rhino.DocObjects.ObjRef: return id.Curve()
    id = coerceguid(id)
    if id is None: return None
    objref = Rhino.DocObjects.ObjRef(id)
    curve = objref.Curve()
    if curve and segment_index>=0 and type(curve) is Rhino.Geometry.PolyCurve:
        curve = curve.SegmentCurve(segment_index)
    objref.Dispose()
    return curve


def coercesurface(object_id):
    "attempt to get surface geometry from the document with a given id"
    if isinstance(object_id, Rhino.Geometry.Surface): return object_id
    if type(object_id) is Rhino.DocObjects.ObjRef: return object_id.Face()
    object_id = coerceguid(object_id)
    if object_id is None: return None
    objref = Rhino.DocObjects.ObjRef(object_id)
    srf = objref.Surface()
    objref.Dispose()
    return srf


def coercemesh( object_id ):
    "attempt to get mesh geometry from the document with a given id"
    object_id = coerceguid(object_id)
    if object_id is None: return None
    objref = Rhino.DocObjects.ObjRef(object_id)
    mesh = objref.Mesh()
    objref.Dispose()
    return mesh


def coercerhinoobject(object_id):
    "attempt to get RhinoObject from the document with a given id"
    object_id = coerceguid(object_id)
    if object_id is None: return None
    return scriptcontext.doc.Objects.Find(object_id)
