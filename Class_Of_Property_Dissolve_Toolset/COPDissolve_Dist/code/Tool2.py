import arcpy
import re

inTABLE = arcpy.GetParameterAsText(0)
outNAME = arcpy.GetParameterAsText(1)
outDIR = arcpy.GetParameterAsText(2)
copFIELD = arcpy.GetParameterAsText(3)
pinFIELD = arcpy.GetParameterAsText(4)
nativeCOPDomains = arcpy.GetParameterAsText(5)
nativeALTDomains = arcpy.GetParameterAsText(6)
ALTDomains = arcpy.GetParameterAsText(7)

COPdomainARRAY = re.split(",", nativeCOPDomains)
v1COPDomains = ['1', '2', '3', '4', '5', '5M', '6', '7']

arcpy.AddMessage("Using these COP domains: " + nativeCOPDomains)

ALTdomainARRAY = re.split(",", nativeALTDomains)
v1ALTDomains = re.split(",", ALTDomains)

arcpy.AddMessage("Using these Native ALT domains: " + nativeALTDomains)
arcpy.AddMessage("Mapped to these ALT domains: " + ALTDomains)

def getCOPvalue(classIN):
    for f in range(len(COPdomainARRAY)):
        if str(COPdomainARRAY[f]) == str(classIN):
            return v1COPDomains[f]
    return ""

def getALTvalue(classIN):
    for f in range(len(COPdomainARRAY)):
        if str(COPdomainARRAY[f]) == str(classIN):
            return ""
    for f in range(len(ALTdomainARRAY)):
        if str(ALTdomainARRAY[f]) == str(classIN):
            return v1ALTDomains[f]
    return classIN

def compareValues(classIN,assignedClass):
    assignedClassArray = re.split(",",assignedClass)
    for f in range(len(assignedClassArray)):
        if str(assignedClassArray[f]) == str(classIN):
            return False
    return True

arcpy.TableToTable_conversion(inTABLE, outDIR, "temp")

outTABLE = outDIR +"\\temp"

arcpy.AddMessage("Making some fields")
arcpy.AddField_management(outTABLE, "PROPCLASS", "TEXT", "", "", 150)
arcpy.AddField_management(outTABLE, "AUXCLASS", "TEXT", "", "", 150)

previousPIN = ""

arcpy.AddMessage("Processing Class of Property - This could take several minutes...")
cursorCOP = arcpy.UpdateCursor(outTABLE,sort_fields = pinFIELD)
countCursor = 0
iterations = 1000
iterationCount = 1000
for row in cursorCOP:
    currentPIN = row.getValue(pinFIELD)
    currentCOPclass = getCOPvalue(row.getValue(copFIELD))
    currentALTclass = getALTvalue(row.getValue(copFIELD))
    if currentPIN == previousPIN:
        if currentCOPclass != "" and assignedCOP =="":
            assignedCOP = currentCOPclass
        elif currentCOPclass != "" and compareValues(currentCOPclass,assignedCOP):
            assignedCOP = assignedCOP + "," + currentCOPclass
        if currentALTclass != "" and assignedALT == "":
            assignedALT = currentALTclass
        elif currentALTclass != "" and compareValues(currentALTclass,assignedALT):
            assignedALT = assignedALT + "," + currentALTclass
    else:
        assignedCOP = currentCOPclass
        assignedALT = currentALTclass
    previousPIN = currentPIN
    row.setValue("PROPCLASS", assignedCOP)
    cursorCOP.updateRow(row)
    row.setValue("AUXCLASS", assignedALT)
    cursorCOP.updateRow(row)
    countCursor = countCursor + 1
    if countCursor == iterationCount:
        arcpy.AddMessage(str(iterationCount) + " records processed")
        iterationCount = iterationCount + iterations
#Make stats field
stats = []
stats.append(["PROPCLASS","LAST"])
stats.append(["AUXCLASS", "LAST"])

arcpy.AddMessage("Dissolving")
arcpy.Statistics_analysis(outTABLE, outDIR +"/"+ outNAME ,stats, pinFIELD)
arcpy.Delete_management(outTABLE)
