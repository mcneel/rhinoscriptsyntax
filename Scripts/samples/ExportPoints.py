# Export the coordinates of point and point cloud objects to a text file.
import rhinoscriptsyntax as rs

def ExportPoints():
    #Get the points to export
    objectIds = rs.GetObjects("Select Points",rs.filter.point | rs.filter.pointcloud,True,True)
    if( objectIds==None ): return

    #Get the filename to create
    filter = "Text File (*.txt)|*.txt|All Files (*.*)|*.*||"
    filename = rs.SaveFileName("Save point coordinates as", filter)
    if( filename==None ): return
    
    file = open(filename, "w")
    for id in objectIds:
        #process point clouds
        if( rs.IsPointCloud(id) ):
            points = rs.PointCloudPoints(id)
            for pt in points:
                file.writeline(str(pt))
        elif( rs.IsPoint(id) ):
            point = rs.PointCoordinates(id)
            file.writeline(str(point))
    file.close()


##########################################################################
# Here we check to see if this file is being executed as the "main" python
# script instead of being used as a module by some other python script
# This allows us to use the module which ever way we want.
if( __name__ == '__main__' ):
    ExportPoints()
