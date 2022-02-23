## Course no: CRP 556
## Submitted by: Fatema Nourin
## Python Version: 3.7.10
## Pupose: This code works on utilizing numpy and matplotlib packages.
## Date: 11/19/2021

import arcpy, os
#from arcpy.sa import *
import numpy as np
import matplotlib.pyplot as plt


arcpy.CheckOutExtension('Spatial')
os.chdir(r"C:\Users\fnourin\Downloads\Assignment8-selected")
cwd = os.getcwd()
arcpy.env.workspace = cwd

arcpy.env.overwriteOutput = True
fc = "mw_states.shp"
array = arcpy.da.FeatureClassToNumPyArray(fc, ["OID@", "SHAPE@XY", "STATE_NAME", "STATE_ABBR", "POP1999", 'MALES', 'FEMALES', 'AREA'])


#Bar chart plot with another attribute total population of interest:..............
x = np.arange(len(array['STATE_ABBR']))
plt.subplot(111)
plt.bar(x +0.1, array['POP1999'])
plt.xticks(x + 0.4, array['STATE_ABBR'])
plt.ylabel('Number of Population')
plt.title('Number of Population in Midwestern States')
plt.savefig('Pop1999.png', dpi = 400, bbox_inches = 'tight')

#### Erroneous plot with no xalabel ticks...........
plt.xlabel('State population')
plt.ylabel('Males')
plt.title('Population vs Males')
plt.plot(array['POP1999'], array['MALES'], 'or')
plt.savefig("Males vs Population_bkg2.png")

### Regular Plot..................................
# regular plot

fig, ax = plt.subplots()
fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(array['AREA'], array['POP1999'], 'o', label = 'Population')
ax.set_xlabel('State Area')
ax.set_ylabel('Poplulation')
ax.set_title('State Population in 1999 Versus Area')
fig.autofmt_xdate() # tilt x axis labels to fit
for i in array:
    plt.annotate(i[3], xy=(i[7],i[4]))# label the points with their state
plt.savefig('populationarea.png', dpi = 300, bbox_inches = 'tight')
