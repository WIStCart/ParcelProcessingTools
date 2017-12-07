import arcpy
import re
import os
from arcpy import env

def clean(field,nullList,case):
    #Create a cursor with null values queried out
    query = '("' + field + '" IS NOT ' + "" + "NULL" + ')'
    cursor = arcpy.UpdateCursor(out_mem, query)

    #If uppercase is selected
    if case == 'true':
        #Loop through each row in a given field
        for row in cursor:
            #Strip whitespace and uppercase alpha characters
            row.setValue(field, (row.getValue(field).strip()).upper())
            cursor.updateRow(row) 

            #Check for null values
            count = 0
            found = False
            while (found == False) and (count < len(nullList)):
                if row.getValue(field) == nullList[count]:
                    row.setValue(field, None)
                    cursor.updateRow(row)
                    found = True
                else:
                    count += 1
    else:
        arcpy.AddMessage("Here")
        #Loop through each row in a given field
        for row in cursor:
            #Strip whitespace and uppercase alpha characters
            row.setValue(field, (row.getValue(field).strip()))
            cursor.updateRow(row) 

            #Check for null values
            count = 0
            found = False
            while (found == False) and (count < len(nullList)):
                if row.getValue(field) == nullList[count]:
                    row.setValue(field, None)
                    cursor.updateRow(row)
                    found = True
                else:
                    count += 1

#Input Parameters
in_fc = arcpy.GetParameterAsText(0)
out_fc = arcpy.GetParameterAsText(1)
nullDomains = "," + arcpy.GetParameterAsText(2)
caseBool = arcpy.GetParameterAsText(3)

#Convert null domains to a list and add <Null>, <NULL>
nullArray = re.split(",", nullDomains)
nullArray.append("<Null>")
nullArray.append("<NULL>")

#Create copy of feature class in memory
arcpy.FeatureClassToFeatureClass_conversion(in_fc, "in_memory", os.path.basename(out_fc)+"MEMORY")
out_mem = "in_memory\\"+os.path.basename(out_fc)+"MEMORY"

#Get fields in feature class and loop through them
fieldList = arcpy.ListFields(out_mem)
for field in fieldList:
    if field.name != "OBJECTID" and field.name != "SHAPE" and field.name != "SHAPE_LENGTH" and field.name != "SHAPE_AREA": 
        if field.type == "String":
            clean(field.name,nullArray,caseBool);

#Write feature class from memory
arcpy.FeatureClassToFeatureClass_conversion(out_mem, os.path.dirname(out_fc), os.path.basename(out_fc))
arcpy.Delete_management(out_mem)