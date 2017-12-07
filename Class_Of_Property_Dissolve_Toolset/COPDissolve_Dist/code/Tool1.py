# Import arcpy module
import arcpy
import re

# Script arguments
Adams_Parcel_13 = arcpy.GetParameterAsText(0)
inDir = arcpy.GetParameterAsText(1)
outFC = arcpy.GetParameterAsText(2)
g1 = arcpy.GetParameterAsText(3) # Field in the above feature class to parse
g2 = arcpy.GetParameterAsText(4) # Field in the above feature class to parse
g3 = arcpy.GetParameterAsText(5) # Field in the above feature class to parse
g4 = arcpy.GetParameterAsText(6) # Field in the above feature class to parse
g5 = arcpy.GetParameterAsText(7) # Field in the above feature class to parse
g6 = arcpy.GetParameterAsText(8) # Field in the above feature class to parse
g7 = arcpy.GetParameterAsText(9) # Field in the above feature class to parse
g5m = arcpy.GetParameterAsText(10) # Field in the above feature class to parse
w1 = arcpy.GetParameterAsText(11) # Field in the above feature class to parse
w2 = arcpy.GetParameterAsText(12) # Field in the above feature class to parse
w3 = arcpy.GetParameterAsText(13) # Field in the above feature class to parse
w4 = arcpy.GetParameterAsText(14) # Field in the above feature class to parse
w5 = arcpy.GetParameterAsText(15) # Field in the above feature class to parse
w6 = arcpy.GetParameterAsText(16) # Field in the above feature class to parse
w7 = arcpy.GetParameterAsText(17) # Field in the above feature class to parse
w8 = arcpy.GetParameterAsText(18) # Field in the above feature class to parse
w9 = arcpy.GetParameterAsText(19) # Field in the above feature class to parse
x1 = arcpy.GetParameterAsText(20) # Field in the above feature class to parse
x2 = arcpy.GetParameterAsText(21) # Field in the above feature class to parse
x3 = arcpy.GetParameterAsText(22) # Field in the above feature class to parse
x4 = arcpy.GetParameterAsText(23) # Field in the above feature class to parse

# Local variables:
Parcel_Copy_shp = Adams_Parcel_13

# Process: Feature Class to Feature Class
arcpy.FeatureClassToFeatureClass_conversion(Adams_Parcel_13, inDir, outFC, "")

# Process: Add Field
arcpy.AddField_management(inDir +"/"+ outFC, "PROPCLASS", "TEXT", "", "", "150", "PROPCLASS", "NULLABLE", "NON_REQUIRED", "")

# Process: Add Field (2)
arcpy.AddField_management(inDir +"/"+ outFC, "AUXCLASS", "TEXT", "", "", "150", "AUXCLASS", "NULLABLE", "NON_REQUIRED", "")

def vetValue(inValue):
   if inValue is not None:
      stringin = re.sub(r"[^\d.]","", str(inValue)) # A regex to clean out all non-alphanumeric (exception of .)
      if stringin != "":
         return float(stringin)
      else:
         return 0
   else:
      return 0
cursorCOP = arcpy.UpdateCursor(inDir +"/"+ outFC)
cursorCOP_ALT = arcpy.UpdateCursor(inDir +"/"+ outFC)
for row in cursorCOP:
   stringSet = ""
   stringlength = 0
   if vetValue(row.getValue(g1)) > 0:
	  stringSet = stringSet + "1" # Should never need a comma
   if vetValue(row.getValue(g2)) > 0:
	  stringSet = stringSet + ",2" 
   if vetValue(row.getValue(g3)) > 0:
	  stringSet = stringSet + ",3" 
   if vetValue(row.getValue(g4)) > 0:
	  stringSet = stringSet + ",4" 
   if vetValue(row.getValue(g5)) > 0:
	  stringSet = stringSet + ",5" 
   if vetValue(row.getValue(g6)) > 0:
	  stringSet = stringSet + ",6" 
   if vetValue(row.getValue(g7)) > 0:
	  stringSet = stringSet + ",7" 
   if vetValue(row.getValue(g5m)) > 0:
	  stringSet = stringSet + ",5M" 
   stringSet = re.sub(r"^,|,$", "", stringSet) # takes care of any leading or trailing ","s
   stringSet = re.sub(r",,+", ",", stringSet) # takes care of any multiple ","s ... pairs them down to just one ","
   row.setValue("PROPCLASS", stringSet) 
   cursorCOP.updateRow(row)
for row in cursorCOP_ALT:
   stringSet = ""
   stringlength = 0
   if (w1 <> ""):
      if vetValue(row.getValue(w1)) > 0:
         stringSet = stringSet + "W1" # Should never need a comma	
   if (w2 <> ""):
      if vetValue(row.getValue(w2)) > 0:
         stringSet = stringSet + ",W2" 
   if (w3 <> ""):
      if vetValue(row.getValue(w3)) > 0:
         stringSet = stringSet + ",W3" 
   if (w4 <> ""):
      if vetValue(row.getValue(w4)) > 0:
         stringSet = stringSet + ",W4" 
   if (w5 <> ""):
      if vetValue(row.getValue(w5)) > 0:
         stringSet = stringSet + ",W5" 
   if (w6 <> ""):
      if vetValue(row.getValue(w6)) > 0:
         stringSet = stringSet + ",W6" 
   if (w7 <> ""):
      if vetValue(row.getValue(w7)) > 0:
         stringSet = stringSet + ",W7" 
   if (w8 <> ""):
      if vetValue(row.getValue(w8)) > 0:
         stringSet = stringSet + ",W8" 
   if (w9 <> ""):
      if vetValue(row.getValue(w8)) > 0:
         stringSet = stringSet + ",W9" 
   if (x1 <> ""):
      if vetValue(row.getValue(x1)) > 0:
         stringSet = stringSet + ",X1" 
   if (x2 <> ""):
      if vetValue(row.getValue(x2)) > 0:
         stringSet = stringSet + ",X2" 
   if (x3 <> ""):
      if vetValue(row.getValue(x3)) > 0:
         stringSet = stringSet + ",X3" 
   if (x4 <> ""):
      if vetValue(row.getValue(x4)) > 0:
         stringSet = stringSet + ",X4" 		 
   stringSet = re.sub(r"^,|,$", "", stringSet) # takes care of any leading or trailing ","s
   stringSet = re.sub(r",,+", ",", stringSet) # takes care of any multiple ","s ... pairs them down to just one ","
   row.setValue("AUXCLASS", stringSet) 
   cursorCOP_ALT.updateRow(row)
