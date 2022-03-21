import csv
import arcpy 

# empty shapefile must already exist, be of a point geometry type 
# and have a BIOMASS attribute
cursor = arcpy.InsertCursor("auxiliar.shp")

# assume a `data.csv` file like:
# y,x,biomass
# 61.4571,-148.7781,12
# 62.7899,-142.583,13
# 61.0742,-149.3066,14

with open('data.csv', 'rb') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Create the feature
        feature = cursor.newRow()

        # Add the point geometry to the feature
        vertex = arcpy.CreateObject("Point")
        vertex.X = row['x']
        vertex.Y = row['y']
        feature.shape = vertex

        # Add attributes
        feature.BIOMASS = row['biomass']

        # write to shapefile
        cursor.insertRow(feature)

# clean up
del cursor