import rhinoscriptsyntax as rs

def CopyObjectsToLayer():
  """
  Copy selected objects to a different layer
  """
  # Get the objects to copy
  objectIds = rs.GetObjects("Select objects")
  if( type(objectIds) is list ):
    # Make sure select objects are unselected
    rs.UnselectObjects( objectIds )
    
    # Get all layer names
    layerNames = rs.LayerNames()
    
    if( type(layerNames) is list ):
      layerNames.sort()
      # Get the destination layer
      layer = rs.ComboListBox(layerNames, "Destination Layer <" + rs.CurrentLayer() + ">")
      if( layer!=None ):
        # Add the new layer if necessary
        if( not rs.IsLayer(layer) ): rs.AddLayer(layer)
        # Copy the objects
        newObjectIds = rs.CopyObjects(objectIds)
        if( type(newObjectIds) is list ):
          for id in newObjectIds:
            # Set the layer of the copied objects
            rs.ObjectLayer( id, layer )
        # Select the newly copied objects
        rs.SelectObjects( newObjectIds )

##########################################################################
# Here we check to see if this file is being executed as the "main" python
# script instead of being used as a module by some other python script
# This allows us to use the module which ever way we want.
if( __name__ == '__main__' ):
  #call function defined above
  CopyObjectsToLayer()