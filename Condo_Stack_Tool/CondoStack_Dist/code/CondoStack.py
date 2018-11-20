import arcpy
import re

inParcel = arcpy.GetParameterAsText(0)
inLink = arcpy.GetParameterAsText(1)
outName = arcpy.GetParameterAsText(2)
outDir = arcpy.GetParameterAsText(3)
newTaxField = arcpy.GetParameterAsText(4)
parcelPINfield = arcpy.GetParameterAsText(5)
altTaxField = arcpy.GetParameterAsText(6)
linkParcelPINfield = arcpy.GetParameterAsText(7)
linkTaxPINfield = arcpy.GetParameterAsText(8)



#Get summary stats for the link table with link PINs > 1
arcpy.AddMessage("Finding Parcels to Stack...")
outputStats = outDir + "/" + "Outputstats"
arcpy.Delete_management(outputStats)
arcpy.Frequency_analysis(inLink, outputStats, [linkParcelPINfield])
arcpy.TableToTable_conversion(outputStats, outDir, "OutputstatsTrimmed" , '"Frequency" > ' + str(1))
arcpy.Delete_management(outputStats)

#Make duplicate of parcel feature class
arcpy.AddMessage("Creating Temporary Feature Class...")
arcpy.FeatureClassToFeatureClass_conversion(inParcel, outDir, "Temp")
tempClass = outDir +"/"+ "Temp"

#Create new tax field and copy alt tax field into to new tax field
arcpy.AddMessage("Adding new field: "+newTaxField)
arcpy.AddField_management(tempClass, newTaxField, "TEXT", "", "", 50)
arcpy.CalculateField_management(tempClass, newTaxField,"!"+altTaxField+"!", "PYTHON_9.3")

#Join summary stats to feature class to get condo parcels
outputStatsTrim = outDir + "/" + "OutputstatsTrimmed"
arcpy.Delete_management(outputStatsTrim)
arcpy.JoinField_management(tempClass, parcelPINfield, outputStatsTrim, linkParcelPINfield)

#Export condo parcels to a separate feature class and export non-condos to the output feature class
outClass = outDir +"/"+ outName
condoClass = outDir +"/"+ "CondoParcels"

##NEED TO TEST THIS CASE
if parcelPINfield == linkParcelPINfield:
    linkPINfield = linkParcelPINfield + "_1"
else:
    linkPINfield = linkParcelPINfield    

whereClause1 = "" + linkPINfield + " Is Not Null"
whereClause2 = "" + linkPINfield + " Is Null"

arcpy.FeatureClassToFeatureClass_conversion(tempClass, outDir, "CondoParcels", whereClause1)
arcpy.AddMessage("Creating " + outName)
arcpy.FeatureClassToFeatureClass_conversion(tempClass, outDir, outName, whereClause2)

#Delete Temp and Trimmed Table
arcpy.Delete_management(outputStatsTrim)
arcpy.Delete_management(tempClass)

#Get fields of parcel feature class and remove read only fields
fields = [f.name for f in arcpy.ListFields(str(condoClass))]
desc = arcpy.Describe(condoClass)
for field in desc.fields:
    if field.editable == False:
        fields.remove(field.name)

def buildWhereClause(table, field, value):
    # Add DBMS-specific field delimiters
    fieldDelimited = arcpy.AddFieldDelimiters(table, field)
    # Determine field type
    fieldType = arcpy.ListFields(table, field)[0].type
    # Add single-quotes for string field values
    if str(fieldType) == 'String':
        value = "'%s'" % value
    # Format WHERE clause
    whereClause = "%s = %s" % (fieldDelimited, value)
    return whereClause

#Iterate through condo parcels
arcpy.AddMessage("Processing...")
updateCursorParcel = arcpy.UpdateCursor(condoClass,sort_fields = parcelPINfield)
for row in updateCursorParcel:
    #Get current parcel pin and make a tax list for the link table
    currentPIN = row.getValue(parcelPINfield)
    taxPINarray = list()    
    #Get the current record
    parcelRecordArray = list()
    for field in fields:
        parcelRecordArray.append(row.getValue(field))
        
    #Search link table for pin
    whereclause = buildWhereClause(inLink,linkParcelPINfield,currentPIN)
    searchCursorLink = arcpy.SearchCursor(inLink,where_clause=whereclause)
        
    #If parcel pin exists in link table, get all associated tax pins 
    rows = None
    for rows in searchCursorLink:
        currentTaxPIN = rows.getValue(linkTaxPINfield)
        taxPINarray.append(currentTaxPIN)
    if not rows:
        taxPINarray.append(currentPIN)
    del(searchCursorLink)
    
    # Add duplicate parcels based on size of taxPINarray
    if len(taxPINarray) > 1:
        #Create insert cursor for outClass
        insertCursorParcel = arcpy.InsertCursor(outClass,fields)

        # Loop for number of tax pins in the array
        for i in range(len(taxPINarray)):
            newRow = insertCursorParcel.newRow()
            newRow.shape = row.shape
                
            # Update the record with previous attribute values, -1 link field at the end is None
            for j in range(len(parcelRecordArray)-1):
                newRow.setValue(str(fields[j]),parcelRecordArray[j])
                    
            #Add the tax pin
            newRow.setValue(newTaxField,taxPINarray[i])
                
            #Insert the row
            insertCursorParcel.insertRow(newRow)
        
        del(insertCursorParcel)
    
del(updateCursorParcel)

#Remove Condo Parcels Table and delete frequency, linktaxpin field
arcpy.Delete_management(condoClass)
arcpy.DeleteField_management(outClass,["Frequency", linkPINfield])
arcpy.SetParameterAsText(9, outClass)
