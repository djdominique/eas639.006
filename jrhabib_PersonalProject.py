## For our final project, we wanted to learn how to automate watershed delineation. The only data needed for this process is elevation data
## and a lat-long location which is our outlet location. In this project we are finding the watershed for a Napa Valley California 
## vineyard and the outlet location is their irrigation pump. Using elevation data of Napa Valley and the irrigation pump location, we can 
## determine the watershed for this vineyard. To complete this process, we will have to use 3 toolboxes within arcpy: Conversion tools, 
## Data Management tools, and Spatial Analyst tools. Irrigation, especially in regard to crop or agricultural businesses, is a very 
## important thing. Therefore, being able to calculate and find the watershed in which these businesses are getting water from with their 
## irrigation pump, is very beneficial. Once one has determined their watershed, they can create a map or conduct further analysis
## such as determining the area of the watershed.

## Rather than typing it here, we have included a short synopsis of the tool and why it was used within each code chunk.


## The very first step is to combine the idnividual rasters into one larger one. Nappa Valley had their elevation data split into two 
## regions, so we need to do this step to combine them and create one elevation raster for the entire region.

with arcpy.EnvManager(scratchWorkspace=r"E:\Personal_Project\MyProject.gdb", workspace=r"E:\Personal_Project\MyProject.gdb"):
    arcpy.management.MosaicToNewRaster("Elev_02_400;Elev_02_200", r"E:\Personal_Project\MyProject.gdb", "CombinedRaster.tif", 'PROJCS["NAD_1983_StatePlane_California_II_FIPS_0402_Feet",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Lambert_Conformal_Conic"],PARAMETER["False_Easting",6561666.666666666],PARAMETER["False_Northing",1640416.666666667],PARAMETER["Central_Meridian",-122.0],PARAMETER["Standard_Parallel_1",38.33333333333334],PARAMETER["Standard_Parallel_2",39.83333333333334],PARAMETER["Latitude_Of_Origin",37.66666666666666],UNIT["Foot_US",0.3048006096012192]]', "32_BIT_FLOAT", None, 1, "LAST", "FIRST")

## After combining our two rasters, we then need to use the fill tool. We use this tool to get rid of any imperfections that might've occured
## when merging the two elevation datasets.

out_surface_raster = arcpy.sa.Fill("tif", None)
out_surface_raster.save(r"E:\Personal_Project\MyProject.gdb\Fill_Raster")

## Once we have the combined elevation raster, we are good to go! The first thing we will do is calculate the flow direction. This tool
## creates a raster of flow using the elevation data, going from each cell to its downslope neighbor. This will tell us where the water
## is flowing.

out_flow_direction_raster = arcpy.sa.FlowDirection(r"E:\Personal_Project\MyProject.gdb\Fill_Raster", "NORMAL", None, "D8")
out_flow_direction_raster.save(r"E:\Personal_Project\MyProject.gdb\FlowDir")

## With the flow direction creted, we can then create the flow accumulation. This tool produces a raster that displays the accumulated
## flow within each cell. In other words, this tool calculates, for each cell, how much is flowing into it from each cell.

out_accumulation_raster = arcpy.sa.FlowAccumulation(r"E:\Personal_Project\MyProject.gdb\FlowDir", None, "FLOAT", "D8")
out_accumulation_raster.save(r"E:\Personal_Project\MyProject.gdb\FlowAcc")

## With both of those created, we need to then generate the point location of our irrigation pump. This was done by inputing the lat/long locations
## in an excel sheet, saving it as a CSV, and bringing it in. 

arcpy.management.XYTableToPoint("Point.csv", r"E:\Personal_Project\MyProject.gdb\Point_Location", "long", "lat", None, 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119521E-09;0.001;0.001;IsHighPrecision')

## Now having created our outlet location, we need to use the snap pour point tool. What this tool does is search a specified distance
## around the irrigation pump, and then it finds the cell with the highest accumulated flow. This allows us to generate an outflow
## location for the watershed of interest.

out_raster = arcpy.sa.SnapPourPoint(r"E:\Personal_Project\MyProject.gdb\Point_Location", r"E:\Personal_Project\MyProject.gdb\FlowAcc", 1000, "OBJECTID")
out_raster.save(r"E:\Personal_Project\MyProject.gdb\SnapPoint")

## After finding the our outflow location, we input this value and our flow direction into the watershed tool. This will
## produce a raster that delineates the watershed for the area. 

out_raster = arcpy.sa.Watershed(r"E:\Personal_Project\MyProject.gdb\FlowDir", r"E:\Personal_Project\MyProject.gdb\SnapPoint", "Value")
out_raster.save(r"E:\Personal_Project\MyProject.gdb\WatershedRaster")

## Our final, but not needed, step was to convert this watershed raster into a polygon. 

arcpy.conversion.RasterToPolygon(r"E:\Personal_Project\MyProject.gdb\WatershedRaster", r"E:\Personal_Project\MyProject.gdb\Watershed", "SIMPLIFY", "Value", "SINGLE_OUTER_PART", None)
