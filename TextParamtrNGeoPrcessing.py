## Course no: CRP 556
## Assignment 7
## Submitted by: Fatema
## Date: 11/10/2021
## Python version 3.7.9



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
    # city to process as string
    cityName = arcpy.GetParameterAsText(6)

    # starting to Geo process
    #'Selecting city'
    arcpy.AddMessage('Selecting city')
    cityBoundary = arcpy.Select_analysis(city_boundaries, where_clause = 'NAME10 = \'' + cityName + '\'')

    #'Buffering city to accomodate open space at city limits'
    arcpy.AddMessage('Buffering city')
    cityBoundaryBuffer = arcpy.Buffer_analysis(cityBoundary, buffer_distance_or_field = str(buff_dist))# + ' METERS')

    #'Clipping census blocks to city limits'
    arcpy.AddMessage('Clipping census blocks')
    cityCensusBlocks = arcpy.Clip_analysis(state_census, cityBoundary)

    #'Clipping public lands to those near city'
    arcpy.AddMessage('Clipping public lands')
    cityPublicLands = arcpy.Clip_analysis(public_lands, cityBoundaryBuffer)

    #'Merging parks and public lands data'
    arcpy.AddMessage('Merging parks and public lands data')
    openMerge = arcpy.Merge_management([city_parks, cityPublicLands])

    #'Buffering open space by walking distance threshold'
    arcpy.AddMessage('Buffering open space')
    cityPublicBuffer = arcpy.Buffer_analysis(openMerge, buffer_distance_or_field = str(buff_dist))# + ' METERS')

    # Intersect buffered open space with census bloc features
    cityIntersectBuffer = arcpy.Intersect_analysis([cityCensusBlocks, cityPublicBuffer])#, 'int_census')

    # Create fields to store analysis information
    # Block Access will store the total area w/i walking distance of open space
    addAccess = arcpy.AddField_management(cityCensusBlocks, 'BLK_ACCESS', 'DOUBLE', 10, 3)
    # Access_Fraction will store a normalized ranking of the total area w/i walking distance/total census block area
    # Calculate to see how much of a census block is within the walkable buffer of open space
    addFrac = arcpy.AddField_management(cityCensusBlocks, 'ACC_FRAC', 'DOUBLE', 10, 3)

    arcpy.AddMessage('Census blocks: ' + str([fld.name for fld in arcpy.ListFields(cityCensusBlocks)]))
    #'Processing data by Census Blocks...'
    arcpy.AddMessage('Starting calculations')
    with arcpy.da.UpdateCursor(cityCensusBlocks, ['GEOID10', addAccess.getInput(1), addFrac.getInput(1), 'SHAPE@AREA']) as ucur:
        for urow in ucur:
            cumArea = 0.0
            #A census block may be in multiple features, so cumulate by census identifier, GEOID10
            with arcpy.da.SearchCursor(cityIntersectBuffer, 'SHAPE@AREA', '"GEOID10" = \'' + urow[0] + '\'') as scur:
                for srow in scur:
                    cumArea += srow[0]
            #Update with total area of census block in walkable buffer
            urow[1] = cumArea
            #Normalize above by dividing by total area of census block
            urow[2] = cumArea/urow[3]
            #Commit new values to 
            ucur.updateRow(urow)

    gnt = arcpy.GenerateNearTable_analysis(cityCensusBlocks, openMerge, closest = 'ALL', search_radius = str(buff_dist))# + ' METERS')

    addInv = arcpy.AddField_management(gnt, 'INV_DIST', 'DOUBLE')
    arcpy.CalculateField_management(gnt, addInv.getInput(1), str(buff_value)+ ' - !NEAR_DIST!', 'PYTHON')

    stats = arcpy.Statistics_analysis(gnt, statistics_fields = [[addInv.getInput(1), 'SUM']], case_field = 'IN_FID')#descGnt.OIDFieldName)

    descCensus = arcpy.Describe(cityCensusBlocks)
    sumField = stats.getInput(1).split()[1] + '_' + addInv.getInput(1)
    arcpy.JoinField_management(cityCensusBlocks, descCensus.OIDFieldName, stats, 'IN_FID', [sumField])

    arcpy.AddMessage('Copying at ' + str(time.process_time()) + ' seconds')

    ## copying the final output to the GDB
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


