import arcpy
import re

inTABLE = arcpy.GetParameterAsText(0)
outNAME = arcpy.GetParameterAsText(1)
outDIR = arcpy.GetParameterAsText(2)
copFIELDS = arcpy.GetParameterAsText(3)
nativeCOPDomains = arcpy.GetParameterAsText(4)
nativeALTDomains = arcpy.GetParameterAsText(5)
ALTDomains = arcpy.GetParameterAsText(6)

COPfieldARRAY = re.split(";", copFIELDS)
arcpy.AddMessage("Using these COP fields: " + ','.join(COPfieldARRAY))

COPdomainARRAY = re.split(",", nativeCOPDomains)
v1COPDomains = ['1', '2', '3', '4', '5', '5M', '6', '7']

arcpy.AddMessage("Using these COP domains: " + nativeCOPDomains)

ALTdomainARRAY = re.split(",", nativeALTDomains)
v1ALTDomains = re.split(",", ALTDomains)

arcpy.AddMessage("Using these Native ALT domains: " + nativeALTDomains)
arcpy.AddMessage("Mapped to these ALT domains: " + ALTDomains)

def getCOPvalue(INclass):
    if INclass is None:
        return ""
    else:
        classIN = str(INclass).strip()
        for f in range(len(COPdomainARRAY)):
            if str(COPdomainARRAY[f]) == str(classIN):
                return v1COPDomains[f]
        return ""

def getALTvalue(INclass):
    if INclass is None:
        return ""
    else:
        classIN = str(INclass).strip()
        for f in range(len(COPdomainARRAY)):
            if str(COPdomainARRAY[f]) == str(classIN):
                return ""
        for f in range(len(ALTdomainARRAY)):
            if str(ALTdomainARRAY[f]) == str(classIN):
                return v1ALTDomains[f]
        return classIN


try:
    arcpy.FeatureClassToFeatureClass_conversion(inTABLE, outDIR, outNAME)
except:
    pass
try:
    arcpy.TableToTable_conversion(inTABLE, outDIR, outNAME)
except:
    pass

outTABLE = outDIR +"/"+ outNAME

arcpy.AddMessage("Making some fields")
arcpy.AddField_management(outTABLE, "PROPCLASS", "TEXT", "", "", 150)
arcpy.AddField_management(outTABLE, "AUXCLASS", "TEXT", "", "", 150)

arcpy.AddMessage("Processing Class of Property")
cursorCOP = arcpy.UpdateCursor(outTABLE)
for row in cursorCOP:
    currentCOParray = list()
    currentALTarray = list()
    for column in range(len(COPfieldARRAY)):
        currentCOP = getCOPvalue(row.getValue(COPfieldARRAY[column]))
        if currentCOP != "":
            currentCOParray.append(currentCOP)
        currentALT = getALTvalue(row.getValue(COPfieldARRAY[column]))
        if currentALT != "":
            currentALTarray.append(currentALT)
    if currentCOParray:
        currentCOPclass = ','.join(map(str, currentCOParray))
    else:
        currentCOPclass = ""
    if  currentALTarray:
        currentALTclass = ','.join(map(str, currentALTarray))
    else:
        currentALTclass = ""
    row.setValue("PROPCLASS", currentCOPclass)
    cursorCOP.updateRow(row)
    row.setValue("AUXCLASS", currentALTclass)
    cursorCOP.updateRow(row)
