## Assignment 5
## Course no: CRP 556
## Submitted by: Fatema Nourin
## Python Version: 3.7.10
## Joining values from excel files to a  shapefile, and then createing a new shapefile from the joined values





import csv
import os
import arcpy
from arcpy import env
import pandas as pd
import numpy as np

arcpy.env.overwriteOutput = True


##------------------created a dataframe from the shapefile Micro points with columns microReg, X and Y--------------------------

fc = r'Assignment_5\micro_points-072810.shp'                  
shape_file_df = pd.DataFrame(columns = ['MicroReg', 'X', 'Y'])

i = 0                                                   
with arcpy.da.SearchCursor(fc, ['MICRORREGI', 'SHAPE@XY'])as cursor:
    for row in cursor:
        ##    print(row)
        shape_file_df.loc[i, :] = [row[0], row[1][0], row[1][1]]      
        i = i+1


##------------------created one dataframe from the excel old files with column microReg------------------------------------------

shape_file_df["MicroReg"] = numpy.array(shape_file_df["MicroReg"], numpy.int32)


arcpy.env.workspace = r"Assignment_5/excel_old/"

xlF = arcpy.ListFiles('*.xls')

excel_np = np.array([], np.int32)

for f in xlF:    ### looping thorough the folder of excel_old files
    pf = pd.read_excel(arcpy.env.workspace + "/"+ f)
    a_df = np.array(pf.loc[:, "MICRO"])
    excel_np = np.hstack((excel_np, a_df))   ## horizontal stack to add rows


excel_np = np.unique(excel_np)
excel_file_df = pd.DataFrame(excel_np.T, columns = ["Micro_excel"]) ##Transposed to create vertical columns

final_table = pd.merge(shape_file_df, excel_file_df, left_on = "MicroReg", right_on = "Micro_excel")   ## created a left join on the excel dataframe and only the matched alues are jioined in this dataframe
print(final_table.head(20))

final_table.iloc[:, :3].to_csv(r'Assignment_5/test2.csv', index=False)  ##Saved the dataframe as a CSV file
   
in_table = 'test2.csv'
field_list = arcpy.ListFields(in_table)

spatialRef = arcpy.Describe(fc).spatialReference
sr = arcpy.SpatialReference(4326)  ## for wgs 84
arcpy.env.outputCoordinateSystem = sr

path = r'Assignment_5/shapefile'
file_name = 'newShape2.shp'
newFC = arcpy.CreateFeatureclass_management(path, file_name, 'POINT')
print(newFC.getMessages(0))  ## 0 gives feature created message, 1 gives warning message, 2 gives error message if any
arcpy.env.workspace = path   ##path for the newFC

validmic = arcpy.ValidateFieldName('MicroReg')
validx = arcpy.ValidateFieldName('X')
validy = arcpy.ValidateFieldName('Y')

arcpy.AddField_management(newFC, validmic, 'LONG')
arcpy.AddField_management(newFC, validx, 'DOUBLE')
arcpy.AddField_management(newFC, validy, 'DOUBLE')
print('Finished adding new fields')

##------------------Populated the newshapefile using the values from the joined dataframe using Insert Cursor------------------------------------------
attr = []
searchFields = ['MicroReg', 'X', 'Y']

insert = arcpy.da.InsertCursor(newFC, ['SHAPE@XY', validmic, validx, validy])
with arcpy.da.SearchCursor(in_table, searchFields) as search:
    for row in search: 
        xVal = row[1]
        yVal = row[2]
        validmic = row[0]
        point = arcpy.Point(xVal, yVal)
        rowList = [point, row[0], row[1], row[2]]
        attr.append(rowList)
        insert.insertRow(rowList)
    del insert



