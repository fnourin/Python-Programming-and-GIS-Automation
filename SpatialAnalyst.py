## Assignment 8
## Course no: CRP 556
## Submitted by: Fatema Nourin
## Python Version: 3.7.10
## Pupose: This code works on utilizing Spatial Analyst extension and numpy and matplotlibpackages.
    
import arcpy, os
from arcpy.sa import *

arcpy.CheckOutExtension('Spatial')

cwd = os.getcwd()
arcpy.env.workspace = cwd

arcpy.env.overwriteOutput = True

# creating a scratch folder, use as scratch workspace
arcpy.env.scratchWorkspace = cwd
arcpy.env.scratchWorkspace = arcpy.env.scratchFolder

indem = Raster('las_dem.tif')
# setting cell size to DEM cell size and snap raster to same
arcpy.env.cellSize = indem.meanCellHeight
Arcpy.env.snapRaster = indem

# calculating elevation difference between dsm and dem (building/vegetation height)
diff = Raster('las_dsm.tif') - indem
diff.save('dsm-dem.tif')

# calculating slope
slope = Slope(indem, 'PERCENT_RISE')
# creating a raster of only slopes greater than 5%
slopeGT5 = Con(slope > 5, slope)
# creating a raster of elevation where slopes are greater than 5% (long form)
elevAtSlopeGT5 = Con(slope, indem, '', 'VALUE > 5')

# creating flow direction, sinks (areas where flow stops/concentrates) and watersheds
fd = FlowDirection(indem)
sinks = Sink(fd)
watersheds = Watershed(fd, sinks)
watersheds.save('ws_' + indem.name + '.tif')

# creating a hillshade for visualization
hillshade = Hillshade(indem)
hillshade.save('hs_' + indem.name + '.tif')

# getting raster properties from Describe object and Raster object
desc = arcpy.Describe(indem)
print('isInteger from Describe is ' + str(desc.isInteger))
print('isInteger is Raster is ' + str(indem.isInteger))
print('max elevation is ' + str(indem.maximum))
