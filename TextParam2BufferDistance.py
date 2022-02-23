## Course no: CRP 556
## Assignment 7
## Submitted by: Fatema
## Date: 11/10/2021
## Python version 3.7.9
## This script takes input parameters as text and also takes two buffer distance around a shapefile



# import modules
import arcpy
import os
import time
import traceback

try:

    time.process_time()

    # Checking to see if output geodatabase exists, if not, create it
    cwd = os.getcwd()
    arcpy.AddMessage('cwd is ' + cwd)

    # setting up environments
    arcpy.env.scratchWorkspace = 'in_memory'
    arcpy.AddMessage('scratch is ' + str(arcpy.env.scratchWorkspace))
    ##arcpy.env.workspace = outputGDB
    arcpy.env.overwriteOutput = True

    # setting up inputs -
    # all city boundaries for Iowa
    city_boundaries = arcpy.GetParameterAsText(0)
    # US census blocks for Iowa from 2010
    state_census = arcpy.GetParameterAsText(1)
    # open space #2, city parks
    city_parks = arcpy.GetParameterAsText(2)
    # open space #1, state and county lands
    public_lands = arcpy.GetParameterAsText(3)

    # setting up output feature class variable
    output_fc = arcpy.GetParameterAsText(4)

    # distance to buffer features as float
    buff_dist = arcpy.GetParameterAsText(5) #Meters
    buff_value = buff_dist.split()[0]

    # distance to buffer features as float
    buff_dist2 = arcpy.GetParameterAsText(6) #Meters
    buff_value2 = buff_dist2.split()[0]
    
    # city to process as string
    cityName = arcpy.GetParameterAsText(7)

    # starting to the geoprocessing task
    
    #'Selecting city'
    arcpy.AddMessage('Selecting city')
    cityBoundary = arcpy.Select_analysis(city_boundaries, where_clause = 'NAME10 = \'' + cityName + '\'')

    #'Buffering city to accomodate open space at city limits'
   
    arcpy.AddMessage('Buffering city')
    cityBoundaryBuffer1 = arcpy.Buffer_analysis(cityBoundary, buffer_distance_or_field = str(buff_dist))# + ' METERS')

    #'Clipping census blocks to city limits'
    arcpy.AddMessage('Clipping census blocks')
    cityCensusBlocks = arcpy.Clip_analysis(state_census, cityBoundary)

    #'Clipping public lands to those near city'

    arcpy.AddMessage('Clipping public lands')
    cityPublicLands1 = arcpy.Clip_analysis(public_lands, cityBoundaryBuffer1)

    #'Merging parks and public lands data'
    arcpy.AddMessage('Merging parks and public lands data')
    openMerge1 = arcpy.Merge_management([city_parks, cityPublicLands1])

    #'Buffering open space by walking distance threshold'
    arcpy.AddMessage('Buffering open space')
    cityPublicBuffer1 = arcpy.Buffer_analysis(openMerge1, buffer_distance_or_field = str(buff_dist))# + ' METERS')

    # Intersect buffered open space with census bloc features
    cityIntersectBuffer1 = arcpy.Intersect_analysis([cityCensusBlocks, cityPublicBuffer1])#, 'int_census')


  #'Buffering city to accomodate open space at city limits'
   
    arcpy.AddMessage('Buffering city')
    cityBoundaryBuffer2 = arcpy.Buffer_analysis(cityBoundary, buffer_distance_or_field = str(buff_dist2))# + ' METERS')

    #'Clipping census blocks to city limits'
    arcpy.AddMessage('Clipping census blocks')
    cityCensusBlocks = arcpy.Clip_analysis(state_census, cityBoundary)

    #'Clipping public lands to those near city'

    arcpy.AddMessage('Clipping public lands')
    cityPublicLands2 = arcpy.Clip_analysis(public_lands, cityBoundaryBuffer2)

    #'Merging parks and public lands data'
    arcpy.AddMessage('Merging parks and public lands data')
    openMerge2 = arcpy.Merge_management([city_parks, cityPublicLands2])

    #'Buffering open space by walking distance threshold'
    arcpy.AddMessage('Buffering open space')
    cityPublicBuffer2 = arcpy.Buffer_analysis(openMerge2, buffer_distance_or_field = str(buff_dist2))# + ' METERS')

    # Intersect buffered open space with census bloc features
    cityIntersectBuffer2 = arcpy.Intersect_analysis([cityCensusBlocks, cityPublicBuffer2])#, 'int_census')


    # Creating fields to store analysis information
    # Block Access will store the total area w/i walking distance of open space
    addAccess1 = arcpy.AddField_management(cityCensusBlocks, 'BLK_ACCS1', 'DOUBLE', 10, 3)
    # Access_Fraction will store a normalized ranking of the total area w/i walking distance/total census block area
    # Calculate to see how much of a census block is within the walkable buffer of open space
    addFrac1 = arcpy.AddField_management(cityCensusBlocks, 'ACC_FRAC1', 'DOUBLE', 10, 3)

    # Setting up progressor bar to display progress of block by block analysis
    # First get total number of features to process
    row_count = int(arcpy.GetCount_management(cityCensusBlocks).getOutput(0))
    i = 0
    arcpy.SetProgressor('step', 'Processing Census Blocks...', 0, row_count, 1)
    
    arcpy.AddMessage('Census blocks: ' + str([fld.name for fld in arcpy.ListFields(cityCensusBlocks)]))
    #'Processing data by Census Blocks...'
    arcpy.AddMessage('Starting calculations')
    with arcpy.da.UpdateCursor(cityCensusBlocks, ['GEOID10', addAccess1.getInput(1), addFrac1.getInput(1), 'SHAPE@AREA']) as ucur:
        for urow in ucur:
            cumArea = 0.0
            #A census block may be in multiple features, so cumulate by census identifier, GEOID10
            with arcpy.da.SearchCursor(cityIntersectBuffer1, 'SHAPE@AREA', '"GEOID10" = \'' + urow[0] + '\'') as scur:
                for srow in scur:
                    cumArea += srow[0]
            #Update with total area of census block in walkable buffer
            urow[1] = cumArea
            #Normalize above by dividing by total area of census block
            urow[2] = cumArea/urow[3]
            #Commit new values to 
            ucur.updateRow(urow)
    arcpy.ResetProgressor()

    gnt1 = arcpy.GenerateNearTable_analysis(cityCensusBlocks, openMerge1, closest = 'ALL', search_radius = str(buff_dist))# + ' METERS')

    addInv1 = arcpy.AddField_management(gnt1, 'INV_D1', 'DOUBLE')
    arcpy.CalculateField_management(gnt1, addInv1.getInput(1), str(buff_value)+ ' - !NEAR_DIST!', 'PYTHON')

    stats1 = arcpy.Statistics_analysis(gnt1, statistics_fields = [[addInv1.getInput(1), 'SUM']], case_field = 'IN_FID')#descGnt.OIDFieldName)

    descCensus = arcpy.Describe(cityCensusBlocks)
    sumField = stats1.getInput(1).split()[1] + '_' + addInv1.getInput(1)
    arcpy.JoinField_management(cityCensusBlocks, descCensus.OIDFieldName, stats1, 'IN_FID', [sumField])

    arcpy.AddMessage('Copying at ' + str(time.process_time()) + ' seconds')




    # Create fields to store analysis information
    # Block Access will store the total area w/i walking distance of open space
    addAccess2 = arcpy.AddField_management(cityCensusBlocks, 'BLK_ACCS2', 'DOUBLE', 10, 3)
    # Access_Fraction will store a normalized ranking of the total area w/i walking distance/total census block area
    # Calculate to see how much of a census block is within the walkable buffer of open space
    addFrac2 = arcpy.AddField_management(cityCensusBlocks, 'ACC_FRAC2', 'DOUBLE', 10, 3)

    # Set up progressor bar to display progress of block by block analysis
    # First get total number of features to process
    row_count = int(arcpy.GetCount_management(cityCensusBlocks).getOutput(0))
    i = 0
    arcpy.SetProgressor('step', 'Processing Census Blocks second time...', 0, row_count, 1)
    
    arcpy.AddMessage('Census blocks: ' + str([fld.name for fld in arcpy.ListFields(cityCensusBlocks)]))
    #'Processing data by Census Blocks...'
    arcpy.AddMessage('Starting calculations second time')
    with arcpy.da.UpdateCursor(cityCensusBlocks, ['GEOID10', addAccess2.getInput(1), addFrac2.getInput(1), 'SHAPE@AREA']) as ucur:
        for urow in ucur:
            cumArea = 0.0
            #A census block may be in multiple features, so cumulate by census identifier, GEOID10
            with arcpy.da.SearchCursor(cityIntersectBuffer2, 'SHAPE@AREA', '"GEOID10" = \'' + urow[0] + '\'') as scur:
                for srow in scur:
                    cumArea += srow[0]
            #Update with total area of census block in walkable buffer
            urow[1] = cumArea
            #Normalize above by dividing by total area of census block
            urow[2] = cumArea/urow[3]
            #Commit new values to 
            ucur.updateRow(urow)
    arcpy.ResetProgressor()

    gnt2 = arcpy.GenerateNearTable_analysis(cityCensusBlocks, openMerge2, closest = 'ALL', search_radius = str(buff_dist2))# + ' METERS')

    addInv2 = arcpy.AddField_management(gnt2, 'INV_D2', 'DOUBLE')
    arcpy.CalculateField_management(gnt2, addInv2.getInput(1), str(buff_value2)+ ' - !NEAR_DIST!', 'PYTHON')

    stats2 = arcpy.Statistics_analysis(gnt2, statistics_fields = [[addInv2.getInput(1), 'SUM']], case_field = 'IN_FID')#descGnt.OIDFieldName)

    descCensus2 = arcpy.Describe(cityCensusBlocks)
    sumField2 = stats2.getInput(1).split()[1] + '_' + addInv2.getInput(1)
    arcpy.JoinField_management(cityCensusBlocks, descCensus2.OIDFieldName, stats2, 'IN_FID', [sumField2])

    arcpy.AddMessage('Copying at second time' + str(time.process_time()) + ' seconds')





    ## copy the final output to the GDB
    arcpy.CopyFeatures_management(cityCensusBlocks, output_fc)
    arcpy.AddMessage('Done at ' + str(time.process_time()) + ' seconds')


except:
    # Get the traceback object
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]

    # Concatenate information together concerning the error into a message string
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    arcpy.AddMessage(pymsg + "\n")

    if arcpy.GetMessages(2) not in pymsg:
        msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
        arcpy.AddError(msgs)
        arcpy.AddMessage(msgs)


