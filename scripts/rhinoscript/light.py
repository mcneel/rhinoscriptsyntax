import scriptcontext
import utility as rhutil
import Rhino.Geometry
import math


def __coercelight(id, raise_if_missing=False):
    light = rhutil.coercegeometry(id)
    if isinstance(light, Rhino.Geometry.Light): return light
    if raise_if_missing: raise ValueError("unable to retrieve light from %s"%id)


def AddDirectionalLight(start_point, end_point):
    """Adds a new directional light object to the document
    Parameters:
      start_point: starting point of the light
      end_point: ending point and direction of the light
    Returns:
      identifier of the new object if successful
    """
    start = rhutil.coerce3dpoint(start_point, True)
    end = rhutil.coerce3dpoint(end_point, True)
    light = Rhino.Geometry.Light()
    light.LightStyle = Rhino.Geometry.LightStyle.WorldDirectional
    light.Location = start
    light.Direction = end-start
    index = scriptcontext.doc.Lights.Add(light)
    if index<0: raise Exception("unable to add light to LightTable")
    rc = scriptcontext.doc.Lights[index].Id
    scriptcontext.doc.Views.Redraw()
    return rc


def AddLinearLight(start_point, end_point, width=None):
    """Adds a new linear light object to the document
    Parameters:
      start_point: starting point of the light
      end_point: ending point and direction of the light
      width[opt]: width of the light
    Returns:
      identifier of the new object if successful
      None on error
    """
    start = rhutil.coerce3dpoint(start_point, True)
    end = rhutil.coerce3dpoint(end_point, True)
    if width is None:
        radius=0.5
        units = scriptcontext.doc.ModelUnitSystem
        if units!=Rhino.UnitSystem.None:
            scale = Rhino.RhinoMath.UnitScale(Rhino.UnitSystem.Inches, units)
            radius *= scale
        width = radius
    light = Rhino.Geometry.Light()
    light.LightStyle = Rhino.Geometry.LightStyle.WorldLinear
    light.Location = start
    v = end-start
    light.Direction = v
    light.Length = light.Direction
    light.Width = -light.Width
    plane = Rhino.Geometry.Plane(light.Location, light.Direction)
    xaxis = plane.XAxis
    xaxis.Unitize()
    plane.XAxis = xaxis
    light.Width = xaxis * min(width, v.Length/20)
    #light.Location = start - light.Direction
    index = scriptcontext.doc.Lights.Add(light)
    if index<0: raise Exception("unable to add light to LightTable")
    rc = scriptcontext.doc.Lights[index].Id
    scriptcontext.doc.Views.Redraw()
    return rc


def AddPointLight(point):
    """Adds a new point light object to the document
    Parameters:
      point = the 3d location of the point
    Returns:
      identifier of the new object if successful
    """
    point = rhutil.coerce3dpoint(point, True)
    light = Rhino.Geometry.Light()
    light.LightStyle = Rhino.Geometry.LightStyle.WorldPoint
    light.Location = point
    index = scriptcontext.doc.Lights.Add(light)
    if index<0: raise Exception("unable to add light to LightTable")
    rc = scriptcontext.doc.Lights[index].Id
    scriptcontext.doc.Views.Redraw()
    return rc


def AddRectangularLight(origin, width_point, height_point):
    """Adds a new rectangular light object to the document
    Parameters:
      origin = 3d origin point of the light
      width_point = 3d width and direction point of the light
      height_point = 3d height and direction point of the light
    Returns:
      identifier of the new object if successful
    """
    origin = rhutil.coerce3dpoint(origin, True)
    ptx = rhutil.coerce3dpoint(width_point, True)
    pty = rhutil.coerce3dpoint(height_point, True)
    length = pty-origin
    width = ptx-origin
    normal = Rhino.Geometry.Vector3d.CrossProduct(width, length)
    normal.Unitize()
    light = Rhino.Geometry.Light()
    light.LightStyle = Rhino.Geometry.LightStyle.WorldRectangular
    light.Location = origin
    light.Width = width
    light.Length = length
    light.Direction = normal
    index = scriptcontext.doc.Lights.Add(light)
    if index<0: raise Exception("unable to add light to LightTable")
    rc = scriptcontext.doc.Lights[index].Id
    scriptcontext.doc.Views.Redraw()
    return rc


def AddSpotLight(origin, radius, apex_point):
    """Adds a new spot light object to the document
    Parameters:
      origin = 3d origin point of the light
      radius = radius of the cone
      apex_point = 3d apex point of the light
    Returns:
      identifier of the new object
    """
    origin = rhutil.coerce3dpoint(origin, True)
    apex_point = rhutil.coerce3dpoint(apex_point, True)
    if radius<0: radius=1.0
    light = Rhino.Geometry.Light()
    light.LightStyle = Rhino.Geometry.LightStyle.WorldSpot
    light.Location = apex_point
    light.Direction = origin-apex_point
    light.SpotAngleRadians = math.atan(radius / (light.Direction.Length))
    light.HotSpot = 0.50
    index = scriptcontext.doc.Lights.Add(light)
    if index<0: raise Exception("unable to add light to LightTable")
    rc = scriptcontext.doc.Lights[index].Id
    scriptcontext.doc.Views.Redraw()
    return rc


def EnableLight(object_id, enable=None):
    """Enables or disables a light object
    Parameters:
      object_id = the light object's identifier
      enable[opt] = the light's enabled status
    Returns:
      if enable is not specified, the current enabled status 
      if enable is specified, the previous enabled status
      None on error
    """
    light = __coercelight(object_id, True)
    rc = light.IsEnabled
    if enable is not None and enable!=rc:
        light.IsEnabled = enable
        id = rhutil.coerceguid(object_id)
        if not scriptcontext.doc.Lights.Modify(id, light):
            return scriptcontext.errorhandler()
        scriptcontext.doc.Views.Redraw()
    return rc

def IsDirectionalLight(object_id):
    """Verifies a light object is a directional light
    Parameters:
      object_id = the light object's identifier
    Returns:
      True or False
    """
    light = __coercelight(object_id, True)
    return light.IsDirectionalLight


def IsLight(object_id):
    """Verifies an object is a light object
    Parameters:
      object_id: the light object's identifier
    Returns:
      True or False
    """
    light = __coercelight(object_id, False)
    return light is not None


def IsLightEnabled(object_id):
    """Verifies a light object is enabled
    Parameters:
      object_id: the light object's identifier
    Returns:
      True or False
    """
    light = __coercelight(object_id, True)
    return light.IsEnabled


def IsLightReference(object_id):
    """Verifies a light object is referenced from another file
    Parameters:
      object_id: the light object's identifier
    Returns:
      True or False
    """
    light = __coercelight(object_id, True)
    return light.IsReference


def IsLinearLight(object_id):
    """Verifies a light object is a linear light
    Parameters:
      object_id = the light object's identifier
    Returns:
      True or False
    """
    light = __coercelight(object_id, True)
    return light.IsLinearLight


def IsPointLight(object_id):
    """Verifies a light object is a point light
    Parameters:
      object_id = the light object's identifier
    Returns:
      True or False
    """
    light = __coercelight(object_id, True)
    return light.IsPointLight


def IsRectangularLight(object_id):
    """Verifies a light object is a rectangular light
    Parameters:
      object_id = the light object's identifier
    Returns:
      True or False
    """
    light = __coercelight(object_id, True)
    return light.IsRectangularLight


def IsSpotLight(object_id):
    """Verifies a light object is a spot light
    Parameters:
      object_id = the light object's identifier
    Returns:
      True or False
    """
    light = __coercelight(object_id, True)
    return light.IsSpotLight


def LightColor(object_id, color=None):
    """Returns or changes the color of a light
    Parameters:
      object_id = the light object's identifier
      color[opt] = the light's new color
    Returns:
      if color is not specified, the current color 
      if color is specified, the previous color
    """
    light = __coercelight(object_id, True)
    rc = light.Diffuse
    if color:
        color = rhutil.coercecolor(color, True)
        if color!=rc:
            light.Diffuse = color
            id = rhutil.coerceguid(object_id, True)
            if not scriptcontext.doc.Lights.Modify(id, light):
                return scriptcontext.errorhandler()
            scriptcontext.doc.Views.Redraw()
    return rc


def LightCount():
    "Returns the number of light objects in the document"
    return scriptcontext.doc.Lights.Count


def LightDirection(object_id, direction=None):
    """Returns or changes the direction of a light object
    Parameters:
      object_id = the light object's identifier
      direction[opt] = the light's new direction
    Returns:
      if direction is not specified, the current direction
      if direction is specified, the previous direction
    """
    light = __coercelight(object_id, True)
    rc = light.Direction
    if direction:
        direction = rhutil.coerce3dvector(direction, True)
        if direction!=rc:
            light.Direction = direction
            id = rhutil.coerceguid(object_id, True)
            if not scriptcontext.doc.Lights.Modify(id, light):
                return scriptcontext.errorhandler()
            scriptcontext.doc.Views.Redraw()
    return rc


def LightLocation(object_id, location=None):
    """Returns or changes the location of a light object
    Parameters:
      object_id = the light object's identifier
      location[opt] = the light's new location
    Returns:
      if location is not specified, the current location
      if location is specified, the previous location
    """
    light = __coercelight(object_id, True)
    rc = light.Location
    if location:
        location = rhutil.coerce3dpoint(location, True)
        if location!=rc:
            light.Location = location
            id = rhutil.coerceguid(object_id, True)
            if not scriptcontext.doc.Lights.Modify(id, light):
                return scriptcontext.errorhandler()
            scriptcontext.doc.Views.Redraw()
    return rc


def LightName(object_id, name=None):
    """Returns or changes the name of a light object
    Parameters:
      object_id = the light object's identifier
      name[opt] = the light's new name
    Returns:
      if name is not specified, the current name
      if name is specified, the previous name
    """
    light = __coercelight(object_id, True)
    rc = light.Name
    if name and name!=rc:
        light.Name = name
        id = rhutil.coerceguid(object_id, True)
        if not scriptcontext.doc.Lights.Modify(id, light):
            return scriptcontext.errorhandler()
        scriptcontext.doc.Views.Redraw()
    return rc


def LightObjects():
    "Returns list of identifiers of light objects in the document"
    count = scriptcontext.doc.Lights.Count
    rc = []
    for i in range(count):
        rhlight = scriptcontext.doc.Lights[i]
        if not rhlight.IsDeleted: rc.append(rhlight.Id)
    return rc


def RectangularLightPlane(object_id):
    """Returns the plane of a rectangular light object
    Parameters:
      object_id = the light object's identifier
    Returns:
      the plane if successful
      None on error
    """
    light = __coercelight(object_id, True)
    if light.LightStyle!=Rhino.Geometry.LightStyle.WorldRectangular:
        return scriptcontext.errorhandler()
    location = light.Location
    length = light.Length
    width = light.Width
    direction = light.Direction
    plane = Rhino.Geometry.Plane(location, length, width)
    return plane, (length.Length, width.Length)


def SpotLightHardness(object_id, hardness=None):
    """Returns or changes the hardness of a spot light. Spotlight hardness
    controls the fully illuminated region.
    Parameters:
      object_id = the light object's identifier
      hardness[opt] = the light's new hardness
    Returns:
      if hardness is not specified, the current hardness
      if hardness is specified, the previous hardness
    """
    light = __coercelight(object_id, True)
    if light.LightStyle!=Rhino.Geometry.LightStyle.WorldSpot:
        return scriptcontext.errorhandler()
    rc = light.HotSpot
    if hardness and hardness!=rc:
        light.HotSpot = hardness
        id = rhutil.coerceguid(object_id, True)
        if not scriptcontext.doc.Lights.Modify(id, light):
            return scriptcontext.errorhandler()
        scriptcontext.doc.Views.Redraw()
    return rc


def SpotLightRadius(object_id, radius=None):
    """Returns or changes the radius of a spot light.
    Parameters:
      object_id = the light object's identifier
      radius[opt] = the light's new radius
    Returns:
      if radius is not specified, the current radius
      if radius is specified, the previous radius
    """
    light = __coercelight(object_id, True)
    if light.LightStyle!=Rhino.Geometry.LightStyle.WorldSpot:
        return scriptcontext.errorhandler()
    radians = light.SpotAngleRadians
    rc = light.Direction.Length * math.tan(radians)
    if radius and radius!=rc:
        radians = math.atan(radius/light.Direction.Length)
        light.SpotAngleRadians = radians
        id = rhutil.coerceguid(object_id, True)
        if not scriptcontext.doc.Lights.Modify(id, light):
            return scriptcontext.errorhandler()
        scriptcontext.doc.Views.Redraw()
    return rc


def SpotLightShadowIntensity(object_id, intensity=None):
    """Returns or changes the shadow intensity of a spot light.
    Parameters:
      object_id = the light object's identifier
      intensity[opt] = the light's new intensity
    Returns:
      if intensity is not specified, the current intensity
      if intensity is specified, the previous intensity
    """
    light = __coercelight(object_id, True)
    if light.LightStyle!=Rhino.Geometry.LightStyle.WorldSpot:
        return scriptcontext.errorhandler()
    rc = light.SpotLightShadowIntensity
    if intensity and intensity!=rc:
        light.SpotLightShadowIntensity = intensity
        id = rhutil.coerceguid(object_id, True)
        if not scriptcontext.doc.Lights.Modify(id, light):
            return scriptcontext.errorhandler()
        scriptcontext.doc.Views.Redraw()
    return rc
