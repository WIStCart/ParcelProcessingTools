import xml.etree.ElementTree as ET
import csv
import glob
import arcpy
import os

inDir = arcpy.GetParameterAsText(0) #raw_input("Input xml directory: ")
outDIR = arcpy.GetParameterAsText(1) #raw_input("Output GDB: ")
outNAME = arcpy.GetParameterAsText(2) #raw_input("Output table name: ")
cleanChar = arcpy.GetParameterAsText(3)
replaceChar = arcpy.GetParameterAsText(4)
recognizeZeroAsCOP = arcpy.GetParameterAsText(5)
recognizeZeroAsAUXCOP = arcpy.GetParameterAsText(6)
addressFlag = "No Site Address Assigned" #raw_input("Address Flag: ")
inDir = inDir.replace("\\", "//")
OUTPUT_TO_USER = ""
if replaceChar == "NONE":
    replaceChar = ""
#Create CSV writer and write header
arcpy.AddMessage("V1")
outFile = open(inDir+'/out.csv','wb')
outSchema = open(inDir+'/Schema.ini','wb')
outSchema.write("[out.csv]"+"\n")
writer = csv.writer(outFile,quoting=csv.QUOTE_ALL)
#header = ['LocalID1', 'LocalID1_Cleaned','LocalID2','ParcelID','year','siteAddress1',\
#          'siteAddress2','siteAddressFull','siteCity','siteState','siteZIP','owner1',\
#          'owner2','mailingAddress','COP','ALT_COP','county','muniName','muniNumber',\
#          'school','totalTaxableLand','totalImprovementLand','totalValue','fairMarketValue',\
#          'totalTax','netTax','inferredAcreage']
headerSchema = ['TAXPARCELID Text Width 100', 'TAXPARCELID_CLEANED Text Width 100','TAXPARCELID_2 Text Width 100','PARCELID Text Width 100','TAXROLLYEAR Text Width 10','SITEADRESS Text Width 200',\
          'SITEADRESS_2 Text Width 200','SITEADRESS_FULL Text Width 200','PLACENAME Text Width 100','STATE Text Width 50','ZIPCODE Text Width 50','OWNERNME1 Text Width 254',\
          'OWNERNME2 Text Width 254','PSTLADRESS Text Width 200','PROPCLASS Text Width 150','AUXCLASS Text Width 150','CONAME Text Width 50','MUNINAME Text Width 100','MUNIFIPS Text Width 50',\
          'SCHOOLDISTNO Text Width 50','LNDVALUE Text Width 50','IMPVALUE Text Width 50','CNTASSDVALUE Text Width 50','ESTFMKVALUE Text Width 50',\
          'GRSPRPTA Text Width 50','NETPRPTA Text Width 50', 'INFERREDACREAGE Text Width 50']
header = ['TAXPARCELID', 'TAXPARCELID_CLEANED','TAXPARCELID_2','PARCELID','TAXROLLYEAR','SITEADRESS',\
          'SITEADRESS_2','SITEADRESS_FULL','PLACENAME','STATE','ZIPCODE','OWNERNME1',\
          'OWNERNME2','PSTLADRESS','PROPCLASS','AUXCLASS','CONAME','MUNINAME','MUNIFIPS',\
          'SCHOOLDISTNO','LNDVALUE','IMPVALUE','CNTASSDVALUE','ESTFMKVALUE',\
          'GRSPRPTA','NETPRPTA', 'INFERREDACREAGE']

writer.writerow(header)

countFields = 1
for i in headerSchema:
    outSchema.write("Col"+ str(countFields)+"="+i+"\n")#"Col"+ str(countFields)+"="+ i +" text width 255"+"\n")
    countFields = countFields + 1

#Ignores namespace, http://www.revenue.wi.gov/slf
def nsTag(tag):
    return str( ET.QName('http://www.revenue.wi.gov/slf', tag) )

#Takes a list of elements and returns a list of text from each element
def eList2Str(elementList):
    strList = list()
    for element in elementList:
        string = element.text
        strList.append(string)
    return strList

print "Processing XML"
#Loop through all xmls in directory
path = str(inDir)+'//*.xml'
#arcpy.AddMessage(path)
for fname in glob.glob(path):    
    arcpy.AddMessage("Processing: "+ fname)
    # Open current XML document
    tree = ET.parse(str(fname))
    root = tree.getroot()
    fileHeader = root.find(nsTag('FileHeader'))
    taxYear = fileHeader.find(nsTag('TaxYear')).text
    
    record = 0
    
    #Loop through all records in this XML document
    for item in tree.iter(tag=nsTag("Item")):
        # Skip over record with personal property
        if item.find(nsTag('ValuationInfo')+'/'+nsTag('PersonalProperty')) is None:
            record = record + 1
        #Get record PIN and remove hyphens based on user input
            recordNumber = item[0].text
            propertyInfo = item.find(nsTag('PropertyInfo'))
            localID = 'None'
            localID_Clean = 'None'
            localID2 = 'None'
            localID3 = 'None'
            if propertyInfo.find(nsTag('LocalID1')) is not None:
                localID = propertyInfo[0].text
                localID_Clean = (propertyInfo[0].text).replace(cleanChar,replaceChar)
            if propertyInfo.find(nsTag('LocalID2')) is not None:
                localID2 = propertyInfo[1].text
            if propertyInfo.find(nsTag('LocalID3')) is not None:
                localID3 = propertyInfo[2].text
            #Get owner and address info
            ownerAndAddressInfo = item.find(nsTag('OwnerAndAddressInfo'))
            #arcpy.AddMessage(ownerAndAddressInfo)
            #Get Mailing Address
            mailAddress1 = ''
            mailAddress2 = ''
            mailAddressFull = ''
            mailAddressCity = ''
            mailAddressState = ''
            mailAddressZIP = ''           
            mailAddressPC = ''           
            mailAddressCountry = ''           
            if ownerAndAddressInfo.find(nsTag('MailingAddress')) is not None:
                MailAddress = ownerAndAddressInfo.find(nsTag('MailingAddress'))
                if MailAddress.find(nsTag('USAddress')) is not None:
                    USAddress = MailAddress.find(nsTag('USAddress'))
                    if USAddress.find(nsTag('AddressLine1')) is not None:
                       mailAddress1 = USAddress.find(nsTag('AddressLine1')).text
                       mailAddressFull = mailAddress1
                    if USAddress.find(nsTag('AddressLine2')) is not None:
                       mailAddress2 = USAddress.find(nsTag('AddressLine2')).text
                       mailAddressFull = mailAddressFull + " " + mailAddress2
                    if USAddress.find(nsTag('City')) is not None:
                       mailAddressCity = USAddress.find(nsTag('City')).text
                       if mailAddressFull == '':
					       mailAddressFull = mailAddressCity
                       else:
                           mailAddressFull = mailAddressFull + ", " + mailAddressCity
                    if USAddress.find(nsTag('State')) is not None:
                       mailAddressState = USAddress.find(nsTag('State')).text
                       mailAddressFull = mailAddressFull + ", " + mailAddressState
                    if USAddress.find(nsTag('ZIPCode')) is not None:
                       mailAddressZIP = USAddress.find(nsTag('ZIPCode')).text
                       if mailAddressZIP is not None:
					       mailAddressFull = mailAddressFull + " " + mailAddressZIP
                    mailingAddress = mailAddressFull
                else:
                    if MailAddress.find(nsTag('ForeignAddress')) is not None:
                        foreignAddress = MailAddress.find(nsTag('ForeignAddress'))
                        if foreignAddress.find(nsTag('AddressLine1')) is not None:
                            mailAddress1 = foreignAddress.find(nsTag('AddressLine1')).text
                            mailAddressFull = mailAddress1
                        if foreignAddress.find(nsTag('AddressLine2')) is not None:
                            mailAddress2 = foreignAddress.find(nsTag('AddressLine2')).text
                            mailAddressFull = mailAddressFull + " " + mailAddress2
                        if foreignAddress.find(nsTag('City')) is not None:
                            mailAddressCity = foreignAddress.find(nsTag('City')).text
                            mailAddressFull = mailAddressFull + ", " + mailAddressCity
                        if foreignAddress.find(nsTag('ProvinceOrState')) is not None:
                            mailAddressState = foreignAddress.find(nsTag('ProvinceOrState')).text
                            mailAddressFull = mailAddressFull + ", " + mailAddressState
                        if foreignAddress.find(nsTag('PostalCode')) is not None:
                            mailAddressPC = foreignAddress.find(nsTag('PostalCode')).text
                            mailAddressFull = mailAddressFull + " " + mailAddressPC
                        if foreignAddress.find(nsTag('Country')) is not None:
                            mailAddressCountry = foreignAddress.find(nsTag('Country')).text
                            mailAddressFull = mailAddressFull + ", " + mailAddressCountry
                        mailingAddress = mailAddressFull
                #mailingAddress = ','.join(eList2Str(foreignAddress.getchildren()))  
            #Get Property Address
            propertyAddress1 = ''
            propertyAddress2 = ''
            propertyAddressFull = ''
            propertyAddressCity = ''
            propertyAddressState = ''
            propertyAddressZIP = ''
            if ownerAndAddressInfo.find(nsTag('SiteAddress')) is not None:
                siteAddress = ownerAndAddressInfo.find(nsTag('SiteAddress'))
                if siteAddress.find(nsTag('AddressLine1')) is not None:
                    propertyAddress1 = siteAddress.find(nsTag('AddressLine1')).text
                if siteAddress.find(nsTag('AddressLine2')) is not None:
                    propertyAddress2 = siteAddress.find(nsTag('AddressLine2')).text
                    if propertyAddress1 == "":
                        propertyAddressFull = propertyAddress1
                    else:
                        propertyAddressFull = propertyAddress1 + ' ' + propertyAddress2
                else:
                    propertyAddressFull = propertyAddress1
                if siteAddress.find(nsTag('City')) is not None:
                    propertyAddressCity = siteAddress.find(nsTag('City')).text
                if siteAddress.find(nsTag('State')) is not None:
                    propertyAddressState = siteAddress.find(nsTag('State')).text
                if siteAddress.find(nsTag('ZIPCode')) is not None:
                    propertyAddressZIP = siteAddress.find(nsTag('ZIPCode')).text
            #Get owner information taking the first two owners and factoring owner type (individual,combined,business)
            ownerNames = list()
            owner = ownerAndAddressInfo.findall(nsTag('Owner'))
            numOwners = len(owner)
            if numOwners >= 2:
               for  i in range(2):
                   if owner[i].find(nsTag('Individual')) is not None:
                       individual = owner[i].find(nsTag('Individual'))
                       name = ' '.join(eList2Str(individual[0].getchildren()))
                       ownerNames.append(name)
                   elif owner[i].find(nsTag('Business')) is not None:
                       business = owner[i].find(nsTag('Business')+'/'+nsTag('Name'))
                       businessName = business[0].text
                       #Account for businessline2
                       if len(business) > 1:
                           businessName = businessName+' '+business[1].text
                       ownerNames.append(businessName)
                   elif owner[i].find(nsTag('CombinedName')) is not None:
                       combinedName = owner[i].find(nsTag('CombinedName'))
                       name = combinedName[0].text
                       ownerNames.append(name)
            else:
                if owner[0].find(nsTag('Individual')) is not None:
                    individual = owner[0].find(nsTag('Individual'))
                    name = ' '.join(eList2Str(individual[0].getchildren()))
                    ownerNames.append(name)
                elif owner[0].find(nsTag('Business')) is not None:
                    business = owner[0].find(nsTag('Business')+'/'+nsTag('Name'))
                    businessName = business[0].text
                    #Account for businessline2
                    if len(business) > 1:
                        businessName = businessName+' '+business[1].text
                    ownerNames.append(businessName)
                elif owner[0].find(nsTag('CombinedName')) is not None:
                    combinedName = owner[0].find(nsTag('CombinedName'))
                    name = combinedName[0].text
                    ownerNames.append(name)
                ownerNames.append('')
                
            #Get Valuation info
            valuationInfo = item.find(nsTag('ValuationInfo'))
            
            #Get COPs for this record
            realProperty = valuationInfo.find(nsTag('RealProperty'))
            COPclasses = list()
            COP = list()
            COPALT = list()
            altTaxCOPdomains = ['ExemptFederalAcres','ExemptStateAcres','ExemptCountyAcres','ExemptOtherAcres','CountyForestCropLand']
            altCOPdomains = ['X1','X2','X3','X4','W4']
            taxCOPdomains = ['Class1','Class2','Class3','Class4','Class5','Class5M','Class6','Class7',\
            'PFCRegularClass1','PFCRegularClass2','PFCSpecialClass','MFLAfter2004Open',\
            'MFLAfter2004Closed','MFLBefore2005Open','MFLBefore2005Closed']
            COPdomains = ['1','2','3','4','5','5M','6','7','W1','W2','W3','W5','W6','W7','W8']
            inferredAcreage = 0
        #Go through cop domains
            for f in range(len(taxCOPdomains)):
                if realProperty.find(nsTag(str(taxCOPdomains[f]))) is not None:
                    propertyClass = realProperty.find(nsTag(str(taxCOPdomains[f])))
                    acres = propertyClass.find(nsTag('Acres'))
                    tempAcres = float(acres.text)
                    if  tempAcres > 0:
                        COPclasses.append(COPdomains[f])
                        inferredAcreage += tempAcres
                    elif recognizeZeroAsCOP == 'true':
                        COPclasses.append(COPdomains[f])
                        inferredAcreage += tempAcres
            #Go through alt domains
            for f in range(len(altTaxCOPdomains)):
                if realProperty.find(nsTag(str(altTaxCOPdomains[f]))) is not None:
                    propertyClass = realProperty.find(nsTag(str(altTaxCOPdomains[f])))
                    tempAcres = float(propertyClass.text)
                    if tempAcres > 0:
                        COPclasses.append(altCOPdomains[f])
                        inferredAcreage += tempAcres
                    elif recognizeZeroAsAUXCOP == 'true':
                        COPclasses.append(altCOPdomains[f])
                        inferredAcreage += tempAcres                       
            #Sort COPclasses into COP and COPAlt
            COPDomain = ['1','2','3','4','5','5M','6','7']
            COPAltDomain = ['X1','X2','X3','X4','W1','W2','W3','W4','W5','W6','W7','W8']
            for i in range(len(COPclasses)):
                for f in range(len(COPDomain)):
                    if COPclasses[i] == str(COPDomain[f]):
                        COP.append(COPclasses[i])
                for k in range(len(COPAltDomain)):
                    if COPclasses[i] == str(COPAltDomain[k]):
                        COPALT.append(COPclasses[i])
                        
            #Create total COP and COPALT fields
            if len(COP) > 0:
                totalCOP = ','.join(COP)
            else:
                totalCOP = ''
            if len(COPALT) > 0:
                totalAltCOP = ','.join(COPALT)
            else:
                totalAltCOP = ''
            
            #Get Jurisdiction info
            jurisdictionInfo = item.find(nsTag('JurisdictionInfo'))
            county = jurisdictionInfo.find(nsTag('County'))
            countyNum,countyName = county[0].text.split(" ",1)
            municipality = jurisdictionInfo.find(nsTag('Municipality'))
            muniNumber = municipality.find(nsTag('MuniNumber')).text
            if municipality.find(nsTag('MuniName')) is not None:
                muniName = municipality.find(nsTag('MuniName')).text
            else:
                muniName = ''
            school = jurisdictionInfo.find(nsTag('School'))
            schoolCode = school.find(nsTag('Code')).text

            #Get tax summary
            if item.find(nsTag('TaxSummary')) is not None:
                taxSummary = item.find(nsTag('TaxSummary'))
                totalTaxableLand = taxSummary.find(nsTag('LandTaxableTotal')).text
                totalTaxableImprovements = taxSummary.find(nsTag('ImprovementsTaxableTotal')).text
                totalTaxableValue = taxSummary.find(nsTag('TotalTaxableValue')).text
                if taxSummary.find(nsTag('EstimatedFairMarketValue')) is not None:
                    fairMarketValue = taxSummary.find(nsTag('EstimatedFairMarketValue')).text
                else:
                    fairMarketValue = ''
                if taxSummary.find(nsTag('TaxTotal')) is not None:
                    totalTax = taxSummary.find(nsTag('TaxTotal')).text
                else:
                    totalTax = ''
                if taxSummary.find(nsTag('NetTax')) is not None:
                    netTax = taxSummary.find(nsTag('NetTax')).text
                else:
                    netTax = ''
            else:
                taxSummary = ''
                fairMarketValue = ''
                totalTaxableLand = ''
                totalTaxableImprovements = ''
                totalTaxableValue = ''
                totalTax = ''
                netTax = ''
                
            
            #Assemble current row and write to csv
            row = list()
            row.append(localID)
            row.append(localID_Clean)
            row.append(localID2)
            row.append(localID3)
            row.append(taxYear)
            row.append(propertyAddress1)
            row.append(propertyAddress2)
            row.append(propertyAddressFull)
            row.append(muniName)
            row.append(propertyAddressState)
            row.append(propertyAddressZIP)
            row.append(ownerNames[0])
            row.append(ownerNames[1])
            row.append(mailingAddress)
            row.append(totalCOP)
            row.append(totalAltCOP)
            row.append(countyName)
            row.append(propertyAddressCity)
            row.append(muniNumber)
            row.append(schoolCode)
            row.append(totalTaxableLand)
            row.append(totalTaxableImprovements)
            row.append(totalTaxableValue)
            row.append(fairMarketValue)
            row.append(totalTax)
            row.append(netTax)
            row.append (str(inferredAcreage))
            writer.writerow(row)
            item.clear() 
outFile.close()
outSchema.close()
arcpy.AddMessage("Finished processing XML, now creating DBF")
arcpy.TableToTable_conversion(inDir+'/out.csv', outDIR, outNAME)

os.remove(inDir+'/out.csv')
os.remove(inDir+'/Schema.ini')
arcpy.AddMessage("Complete!")
