# Import arcpy module
import arcpy

# Developed By: Codie See, Mitch Johnson, Chris Scheele, and David Vogel, Summer 2015 for the V1 and V2 Wisconsin Statewide Parcel Initiative projects
# Local variables:
in_fc = arcpy.GetParameterAsText(0)  #Input Feature Class
in_field = arcpy.GetParameterAsText(1) #Input summary field (the field to be summarized)
out_DB = arcpy.GetParameterAsText(2) # Path to output file geodatabase
table_name = arcpy.GetParameterAsText(3) # A string, to be used as the name of the table 

arcpy.AddMessage(in_fc)
arcpy.AddMessage(in_field)

arcpy.Statistics_analysis(in_fc, out_DB + "/" + table_name , [[in_field, "COUNT"]], in_field)
arcpy.AddField_management(out_DB + "/" + table_name , in_field + "_ST1", "TEXT", "", "", 100)
temp = "COUNT_" + in_field
arcpy.DeleteField_management(out_DB + "/" + table_name, [temp])
arcpy.SetParameterAsText(4, out_DB + "/" + table_name)