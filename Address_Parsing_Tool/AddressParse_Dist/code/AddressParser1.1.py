import arcpy,re,usaddress,collections

inLayer = arcpy.GetParameterAsText(0)
addressField = arcpy.GetParameterAsText(1)
outDir = arcpy.GetParameterAsText(2)
outName = arcpy.GetParameterAsText(3)
parseBool = arcpy.GetParameterAsText(4)
flagBool = arcpy.GetParameterAsText(5)
errorLogBool = arcpy.GetParameterAsText(6)
errorLogDir = arcpy.GetParameterAsText(7)
sumStatsBool = arcpy.GetParameterAsText(8)

#Initialize Variables
parseErrorCount = 0
rowCount = 0
logEveryN = 10000
objectID = "OBJECTID"
uniqueID = "UNIQUE_IDENTIFIER"
addNumPref = "ADDNUMPREFIX"
addNum = "ADDNUM"
addNumSuff = "ADDNUMSUFFIX"
prefix = "PREFIX"
streetName = "STREETNAME"
streetType = "STREETTYPE"
suffix = "SUFFIX"
unitType = "UNITTYPE"
unitID = "UNITID"
characterField = "Character_Flag"
incompleteField = "Incomplete_Data_Flag"
extraneousField = "Extraneous_Data_Flag"
parseErrorField = "Parse_Error_Flag"
completenessFields = ['AddressNumber','StreetNamePreType','StreetName','StreetNamePostType']
extraneousFieldsArray = ['StreetNamePostModifier','PlaceName','StateName','ZipCode',
        'SecondStreetName','SecondStreetNamePostDirectional','SubaddressIdentifier','SubaddressType',
        'USPSBoxGroupID','USPSBoxGroupType','USPSBoxID','USPSBoxType','BuildingName',
        'CornerOf','IntersectionSeparator','LandmarkName','NotAddress','Recipient']
#Make duplicate of parcel feature class and add new fields
arcpy.AddMessage("Creating New Layer")
arcpy.FeatureClassToFeatureClass_conversion(inLayer, outDir, outName)
outLayer = outDir +"/"+ outName
fieldList = arcpy.ListFields(outLayer)

#Delete all existing address parser tool fields
for field in fieldList:
    if field.name == uniqueID:
        arcpy.DeleteField_management(outLayer,uniqueID)
    if field.name == addNumPref:
        arcpy.DeleteField_management(outLayer,[addNumPref,addNum,addNumSuff,prefix,streetName,streetType,suffix,unitType,unitID])
    if field.name == extraneousField:
        arcpy.DeleteField_management(outLayer,extraneousField)
    if field.name == characterField:
        arcpy.DeleteField_management(outLayer,[characterField,incompleteField,parseErrorField])

#Add new fields
arcpy.AddField_management(outLayer,uniqueID, "LONG")
if parseBool == 'true':
    arcpy.AddMessage("Adding Address Element Fields")
    arcpy.AddField_management(outLayer, addNumPref, "TEXT", "", "", 50)
    arcpy.AddField_management(outLayer, addNum, "TEXT", "", "", 50)
    arcpy.AddField_management(outLayer, addNumSuff, "TEXT", "", "", 50)
    arcpy.AddField_management(outLayer, prefix, "TEXT", "", "", 50)
    arcpy.AddField_management(outLayer, streetName, "TEXT", "", "", 50)
    arcpy.AddField_management(outLayer, streetType, "TEXT", "", "", 50)
    arcpy.AddField_management(outLayer, suffix, "TEXT", "", "", 50)
    arcpy.AddField_management(outLayer, unitType, "TEXT", "", "", 50)
    arcpy.AddField_management(outLayer, unitID, "TEXT", "", "", 50)  
if parseBool == 'true' or flagBool == 'true':
    arcpy.AddField_management(outLayer,extraneousField, "TEXT", "", "", 255)
if flagBool== 'true':
    arcpy.AddMessage("Adding Flag Fields")
    arcpy.AddField_management(outLayer,characterField, "TEXT", "", "", 255)
    arcpy.AddField_management(outLayer,incompleteField, "TEXT", "", "", 255)
    arcpy.AddField_management(outLayer,parseErrorField, "SHORT")
    
regex = re.compile("[^a-zA-Z0-9.,'\s]")

#Create error log file
if errorLogBool == 'true':
    if errorLogDir == "" or errorLogDir is None:
        errorLogDir = outDir
    logFile = open(errorLogDir+"/"+outName+"_errorLog.txt","w")
    arcpy.AddMessage("Creating Error Log")
    
#Iterate through addresses
arcpy.AddMessage("Processing...")
whereClause = addressField+" IS NOT NULL OR "+addressField+" <> ''"
updateCursor = arcpy.UpdateCursor(outLayer,where_clause = whereClause,sort_fields = objectID)
for row in updateCursor:
    rowCount += 1
    addressParsed = {}
    address_type = ''
    characterComment = ''
    incompleteComment = ''
    extraneousComment = ''
    extraneousLogFile = ''
    parseErrorLogFile = ''
    addressTypeLogFile = ''
    parseError = 0
    address = row.getValue(addressField)
    numObjectID = row.getValue(objectID)
    row.setValue(uniqueID,numObjectID)
    if flagBool== 'true':
        #Handle Character Flag
        characterFlagArray = re.findall(regex,address)
        badCharacters = ' '.join(characterFlagArray)
        if badCharacters != '':
            characterComment = "Flagged Chars: " + badCharacters +" "
    #Run usaddress
    try:
        addressParsed, address_type = usaddress.tag(address)
    except usaddress.RepeatedLabelError as e:
        parseError = 1
        parseErrorCount += 1
        parseErrorLogFile = str(e)
    if addressParsed:
        #Handle extraneous data flag
        for parseKey in addressParsed.iterkeys():
            for extraneousKey in extraneousFieldsArray:
                if parseKey == extraneousKey:
                    extraneousComment += addressParsed[parseKey] + " "
        #Handle completeness data flag
        if flagBool == 'true':
            addNumCheck = stNameCheck = stTypeCheck = stPreCheck = 0
            for key in addressParsed.iterkeys():
                if key == 'AddressNumber':
                    addNumCheck = 1
                elif key == 'StreetNamePreType':
                    stPreCheck = 1
                elif key == 'StreetName':
                    stNameCheck = 1
                elif key == 'StreetNamePostType':
                    stTypeCheck = 1
            if addNumCheck == 0 or stNameCheck == 0 or (stPreCheck == 0 and stTypeCheck == 0):
                incompleteComment = "Possible Missing Elements:"
                if addNumCheck == 0:
                    incompleteComment += " Address Number "
                if stNameCheck == 0:
                    incompleteComment += " Street Name " 
                if stPreCheck == 0 and stTypeCheck == 0:
                    incompleteComment += " Street Name Pre-Type or Street Type "
            if stPreCheck == 1 and stTypeCheck == 1:
                incompleteComment += "Cannot have both Street Name Pre-Type and Street Type "
            if address_type == "Intersection":
                incompleteComment += "Address Type: Intersection not acceptable "
            if address_type == "Ambiguous":
                incompleteComment += "Address is ambiguous "
    
    #Write record to log file if necessary
    if parseErrorLogFile != '' and errorLogBool== 'true':
        logFile.write("---------------------------------------- "+objectID+": "+str(numObjectID)+" ----------------------------------------\n")
        if parseErrorLogFile != '':
            logFile.write(parseErrorLogFile)
            logFile.write("\n")

    #Parse addresses and update row
    if parseBool== 'true':
        prefixCombined = ''
        streetNameCombined = ''
        #Get addressComponents
        for key in addressParsed.iterkeys():
            if key == 'AddressNumberPrefix':
                row.setValue(addNumPref,addressParsed[key])
            elif key == 'AddressNumber':
                strippedAddress = addressParsed["AddressNumber"].strip()
                #791A
                if re.search("^\d{1,7}[a-zA-Z]$", strippedAddress) is not None:
                    replace = re.search("^\d{1,7}", strippedAddress).group() + "*"
                    strippedAddress = re.sub(r'^\d{1,7}', replace ,strippedAddress)
                    vv = (strippedAddress).split("*")
                    if len(vv) > 0:
                        addNumSuffix = ""
                        for i in range(len(vv)-1):
                            addNumSuffix = addNumSuffix + str(vv[i+1])
                        addNumber = str(vv[0])
                    row.setValue(addNumSuff,addNumSuffix.strip())
                    row.setValue(addNum,addNumber.strip())
                #107-108    
                elif re.search("^\d{1,7}(\s)?[-&](\s)?\d{1,7}$", strippedAddress) is not None:
                    replace = re.search("^\d{1,7}", strippedAddress).group() + "*"
                    strippedAddress = re.sub(r'^\d{1,7}', replace ,strippedAddress)
                    vv = (strippedAddress).split("*")
                    if len(vv) > 0:
                        extraneousData = ""
                        for i in range(len(vv)-1):
                            extraneousData = extraneousData + str(vv[i+1])
                        addNumber = str(vv[0])
                    extraneousComment += extraneousData.strip()
                    row.setValue(addNum,addNumber.strip())
                #Standard grid address    
                elif re.search("^[\w]+(?<=\d)(?=\D)+(\s)?[a-zA-Z]\d{1,7}$", strippedAddress) is not None:
                    strippedAddress = strippedAddress.replace(" ","")
                    replace = re.search("^[\w]+(?<=\d)(?=\D)+[\w]", strippedAddress).group() + "*"
                    strippedAddress = re.sub(r'^[\w]+(?<=\d)(?=\D)+[\w]', replace ,strippedAddress)
                    vv = (strippedAddress).split("*")
                    if len(vv) > 0:
                        addNumber = ""
                        for i in range(len(vv)-1):
                            addNumber = addNumber + str(vv[i+1])
                        addNumPre = str(vv[0])
                    row.setValue(addNumPref,addNumPre.strip())
                    row.setValue(addNum,addNumber.strip())
                #Grid with letter attached at the end
                elif re.search("^[\w]+(?<=\d)(?=\D)+(\s)?[a-zA-Z]\d{1,7}?[a-zA-Z]$", strippedAddress) is not None:
                    strippedAddress = strippedAddress.replace(" ","")
                    replace1 = re.search("^[\w]\d{1,7}(\w)", strippedAddress).group() + "*"
                    strippedAddress1 = re.sub(r'^[\w]\d{1,7}(\w)', replace1 ,strippedAddress)
                    vv = (strippedAddress1).split("*")
                    if len(vv) > 0:
                        addNumPre = str(vv[0])
                        replace2 = re.search("^\d{1,7}", str(vv[1])).group() + "*"
                        strippedAddress2 = re.sub(r'^\d{1,7}', replace2 ,str(vv[1]))
                        tt = (strippedAddress2).split("*")
                        if len(tt) > 0:
                            addNumberSuffix = ""
                            for i in range(len(tt)-1):
                                addNumberSuffix = addNumberSuffix + str(tt[i+1])
                            addNumber = str(tt[0])
                            
                    row.setValue(addNumPref,addNumPre.strip())
                    row.setValue(addNum,addNumber.strip())
                #Grid hyphen or space followed by number W456N345-87
                elif re.search("^[\w]+(?<=\d)(?=\D)+(\s)?[a-zA-Z]\d{1,7}[-\s]\d{1,3}$", strippedAddress) is not None:
                    strippedAddress = strippedAddress.replace(" ","")
                    replace1 = re.search("^[\w]\d{1,7}(\w)", strippedAddress).group() + "*"
                    strippedAddress1 = re.sub(r'^[\w]\d{1,7}(\w)', replace1 ,strippedAddress)
                    vv = (strippedAddress1).split("*")
                    if len(vv) > 0:
                        addNumPre = str(vv[0])
                        replace2 = re.search("^\d{1,7}", str(vv[1])).group() + "*"
                        strippedAddress2 = re.sub(r'^\d{1,7}', replace2 ,str(vv[1]))
                        tt = (strippedAddress2).split("*")
                        if len(tt) > 0:
                            extraneousData = ""
                            for i in range(len(tt)-1):
                                extraneousData = extraneousData + str(tt[i+1])
                            addNumber = str(tt[0])
                            
                    row.setValue(addNumPref,addNumPre.strip())
                    row.setValue(addNum,addNumber.strip())
                    extraneousComment += extraneousData.strip()
                #N123    
                elif re.search("^[a-zA-Z]+(?=\d)", strippedAddress) is not None:
                    replace = re.search("^[\w]", strippedAddress).group() + "*"
                    strippedAddress = re.sub(r'^[\w]', replace ,strippedAddress)
                    vv = (strippedAddress).split("*")
                    if len(vv) > 0:
                        addNumber = ""
                        for i in range(len(vv)-1):
                            addNumber = addNumber + str(vv[i+1])
                        addNumPre = str(vv[0])
                    row.setValue(addNumPref,addNumPre.strip())
                    row.setValue(addNum,addNumber.strip())
                #...-457    
                elif re.search("[\s-]\d{1,7}$", strippedAddress) is not None:
                    replace = "*" + re.search("\d{1,7}$", strippedAddress).group()
                    strippedAddress = re.sub(r'(\s)\d{1,7}$', replace ,strippedAddress)
                    vv = (strippedAddress).split("*")
                    if len(vv) > 0:
                        extraneousData = ""
                        for i in range(len(vv)-1):
                            extraneousData = extraneousData + str(vv[i+1])
                        addNumber = str(vv[0])
                    extraneousComment += extraneousData.strip()
                    row.setValue(addNum,addNumber.strip())
                #...-123A
                elif re.search("[\s-]\d{1,7}[a-zA-z]", strippedAddress) is not None:
                    replace = "*" + re.search("\d{1,7}[a-zA-z]", strippedAddress).group()
                    strippedAddress = re.sub(r'[\s-]\d{1,7}[a-zA-z]', replace ,strippedAddress)
                    vv = (strippedAddress).split("*")
                    if len(vv) > 0:
                        extraneousData = ""
                        for i in range(len(vv)-1):
                            extraneousData = extraneousData + str(vv[i+1])
                        addNumber = str(vv[0])
                    extraneousComment += extraneousData.strip()
                    row.setValue(addNum,addNumber.strip())  
                else:
                    row.setValue(addNum,addressParsed[key].strip())
            elif key == 'AddressNumberSuffix':
                row.setValue(addNumSuff,addressParsed[key].strip())
            elif key == 'StreetNamePostType':
                row.setValue(streetType,addressParsed[key].strip())
            elif key == 'StreetNamePostDirectional':
                row.setValue(suffix,addressParsed[key].strip())
            elif key == 'OccupancyType':
                row.setValue(unitType,addressParsed[key].strip())
            elif key == 'OccupancyIdentifier':
                row.setValue(unitID,addressParsed[key].strip())
            #Combine certain fields
            if key == 'StreetNamePreDirectional' or key == 'StreetNamePreType':
                prefixCombined += addressParsed[key]+ " "
            if key == 'StreetNamePreModifier' or key == 'StreetName':
                streetNameCombined += addressParsed[key] + " "
            row.setValue(prefix,prefixCombined.strip())
            row.setValue(streetName,streetNameCombined.strip())
    #Update row for flags
    if flagBool== 'true':
        row.setValue(characterField,characterComment.strip())
        row.setValue(incompleteField,incompleteComment.strip())
        row.setValue(parseErrorField,parseError)
    if parseBool== 'true' or flagBool== 'true':
        row.setValue(extraneousField,extraneousComment.strip())    
    updateCursor.updateRow(row)
    if (rowCount % logEveryN) == 0:
        arcpy.AddMessage("Processed "+str(rowCount)+" records")
del(updateCursor)
if errorLogBool== 'true':
    logFile.write("\nTotal Number of Parse Errors: "+str(parseErrorCount))
    logFile.close()

#Produce summary stats on parse fields
if parseBool == 'true' and sumStatsBool == 'true':
    arcpy.Frequency_analysis(outLayer,outDir +"/"+outName+"_Prefix_Stats",prefix)
    arcpy.Frequency_analysis(outLayer,outDir +"/"+outName+"_StreetName_Stats",streetName)
    arcpy.Frequency_analysis(outLayer,outDir +"/"+outName+"_StreetType_Stats",streetType)
    arcpy.Frequency_analysis(outLayer,outDir +"/"+outName+"_Suffix_Stats",suffix)
arcpy.SetParameterAsText(9, outDir +"/"+outName)