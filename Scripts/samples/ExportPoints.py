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
    
    """
    Using a 'with' loop to open the file, we do not need to clean
    up or close the file when we are done, Python takes care of it.
    Here, we'll write the points with a line break, otherwise
    all the points will end up on one line.
    """
    with open(filename, "w")as file:
        
        for id in objectIds:
            #process point clouds
            if( rs.IsPointCloud(id) ):
                points = rs.PointCloudPoints(id)
                for pt in points:
                    # convert the point list to a string, 
                    # add a new line character, and write to the file
                    file.write(str(pt)+ "\n")
            elif( rs.IsPoint(id) ):
                point = rs.PointCoordinates(id)
                file.write(str(point)+ "\n")
    

##########################################################################
# Here we check to see if this file is being executed as the "main" python
# script instead of being used as a module by some other python script
# This allows us to use the module which ever way we want.
if( __name__ == '__main__' ):
    ExportPoints()
