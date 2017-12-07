# Import arcpy module
import arcpy
import re
import os
from arcpy import env

# Developed by Angie Limbach, Spring 2014 for the LinkWISCONSIN Address Point and Parcel Mapping Project
# Additional contributions by Codie See, Mitch Johnson, Chris Scheele and David Vogel, Summer 2015 for the V1 and V2 Wisconsin Statewide Parcel Initiative projects
# Local variables:
in_fc = arcpy.GetParameterAsText(0)  #Input Feature Class
sum_table = arcpy.GetParameterAsText(1) #Input summary table
in_field = arcpy.GetParameterAsText(2)  #This is the input field to complete the join with
join_field = arcpy.GetParameterAsText(3) #This is the field that's joining-up with in_field
field_list = arcpy.GetParameterAsText(4) #This is the field that will be calculated into the standardized field (contains the user defined shtandards)
output_fc = arcpy.GetParameterAsText(5) # This is the name of the output feature class.
output_fc_temp = output_fc + "WORKING"
arcpy.Delete_management("in_memory")
dynamic_workspace = "in_memory" # os.path.dirname(in_fc) # <-- use this in case we want to execute code on disk
arcpy.AddMessage("WRITING TO MEMORY")
arcpy.FeatureClassToFeatureClass_conversion(in_fc, dynamic_workspace, output_fc_temp)
arcpy.AddMessage("BEGINNING SCRIPT")
# Add a new field to hold the results, name it the same as it was in the table (presuming "_ST2" at the end).
arcpy.AddField_management(dynamic_workspace+"\\"+output_fc_temp, in_field+"_ST2", "TEXT", "", "", 100) # add a new field to calculate output results into
# Process: Join Field
arcpy.AddMessage("BEGINNING TABLE JOIN")
arcpy.MakeFeatureLayer_management ( dynamic_workspace+"\\"+output_fc_temp, "output_fc_feature_layer") # must make a feature layer for the input feature class (to execute the join on)
arcpy.AddJoin_management("output_fc_feature_layer", in_field, sum_table, join_field) # join the input table to the feature layer created in the line above 
# Process: Calculate Field
arcpy.AddMessage("BEGINNING FIELD CALCULATION")
arcpy.AddMessage("YOUR STANDARDIZED OUTPUT WILL BE WRITTEN TO: "+in_field+"_ST2") 
arcpy.CalculateField_management("output_fc_feature_layer", in_field+"_ST2", "!"+os.path.basename(sum_table)+"."+str(field_list)+"!", "PYTHON") # calculate the standardized values from the input table to the newly created field - via the feature layer join  
# Process: Delete Field
arcpy.AddMessage("DELETING EXCESS FIELDS")
#arcpy.RemoveJoin_management(os.path.dirname(in_fc)+"\\"+output_fc)
arcpy.DeleteField_management(dynamic_workspace+"\\"+output_fc_temp, field_list)
arcpy.AddMessage("WRITING OUTPUT FC")
arcpy.FeatureClassToFeatureClass_conversion(dynamic_workspace+"\\"+output_fc_temp, os.path.dirname(in_fc), output_fc)
#arcpy.AddMessage("DELETING IN_MEMORY ... almost done!!")
#arcpy.Delete_management("in_memory")
arcpy.SetParameterAsText(6, os.path.dirname(in_fc)+"\\"+output_fc)