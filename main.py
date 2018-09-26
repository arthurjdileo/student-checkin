from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import datetime
import time

def getECADictionary(values):
    ecaDict = dict()
    idColumn = 1
    nameCol = 0

    for i in range(1, len(values)):
        ecaDict[int(values[i][idColumn])] = values[i][nameCol]
    return ecaDict

def getWhitelist(ids):
    whitelist = set()
    for key in ids:
        whitelist.add(int(key))
    return whitelist

def duplicateSheet(currentDate):
    requestBody = \
        {
            "destinationSpreadsheetId": SPREADSHEET_ID,
        }

    request = service.spreadsheets().sheets().copyTo(
        spreadsheetId=SPREADSHEET_ID,
        sheetId=0,
        body=requestBody)
    duplicated = request.execute()

    requestBody2 = \
        {
            "requests": [
                {
                    "updateSheetProperties": {
                        "properties": {
                            "sheetId": duplicated["sheetId"],
                            "title": currentDate
                        },
                        "fields": "title",
                    }
                }
            ]
        }

    request = service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID,
                                                 body=requestBody2)
    request.execute()
    return duplicated["title"]

def findStudentIndex(studentId):
    #finds the row index of the student's details
    # iterates col-major
    index = 1
    for col in range(1, len(values)):
        for val in values[col]:
            if ids[studentId] == val:
                return index
        index += 1
    return -1 # can't find

def getTime():
    return datetime.datetime.now().strftime("%I:%M%p")

def getDate():
    return datetime.datetime.now().strftime("%m/%d/%y")

def getSheets():
    sheet_metadata = service.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID).execute()
    sheets = sheet_metadata.get('sheets', '')
    listOfSheets = set()
    for sheet in sheets:
        listOfSheets.add(sheet["properties"]["title"])
    return listOfSheets

def findNextTimeInIndex(studentId):
    #even row index
    rowIndex = findStudentIndex(studentId)

    for headerIndex in range(len(values[0])):
        if headerIndex % 2 == 0:
            if values[rowIndex][headerIndex] == "--":
                return headerIndex
    return -1 # out of space

def findNextTimeOutIndex(studentId):
    #odd row index
    rowIndex = findStudentIndex(studentId)

    for headerIndex in range(len(values[0])):
        if headerIndex % 2 == 1:
            if values[rowIndex][headerIndex] == "--":
                return headerIndex
    return -1 # out of space

def indicesToRange(studentIndex, headerIndex):
    headerCol = chr(65+headerIndex)
    print("%s%s" % (headerCol, studentIndex+1))
    return "%s%s" % (headerCol, studentIndex+1)

def insertTime(studentId, status, CURRENT_DAY_RANGE):
    studentIndex = findStudentIndex(studentId)
    if status == "in": headerIndex = findNextTimeInIndex(studentId)
    else: headerIndex = findNextTimeOutIndex(studentId)
    currentTime = getTime()
    body = {
        "range": CURRENT_DAY_RANGE + "!" + indicesToRange(studentIndex, headerIndex),
        "majorDimension": "ROWS",
        'values': [[currentTime]]
    }
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=(CURRENT_DAY_RANGE + "!" + indicesToRange(studentIndex,headerIndex)),
        valueInputOption="USER_ENTERED", body=body).execute()

def isCheckedIn(studentId):
    checkedInIndex = findNextTimeInIndex(studentId)
    checkedOutIndex = findNextTimeOutIndex(studentId)
    if checkedInIndex < checkedOutIndex: return False
    else: return True

def newDay():
    sheets = getSheets()
    currentDate = getDate()
    if currentDate not in sheets:
        duplicateSheet(currentDate)
    return currentDate


# Credentials (don't touch)
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('sheets', 'v4', http=creds.authorize(Http()))


# # Call the Sheets API
SPREADSHEET_ID = '1jsNGLL-Nr0gkaAhqweQqjuPVxup0DfgTLf81X3gdmZU'
RANGE_NAME = 'A:Z'

CURRENT_DAY_RANGE = "Template"
result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                            range=RANGE_NAME).execute()
values = result.get('values', [])
print(values)

ids = getECADictionary(values)
whitelist = getWhitelist(ids)

while True:
    CURRENT_DAY_RANGE = newDay()
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                                 range=CURRENT_DAY_RANGE).execute()
    values = result.get('values', [])
    studentId = input("Enter ID: ")
    studentId = int(studentId)
    if studentId in whitelist:
        if isCheckedIn(studentId):
            insertTime(studentId, "out", CURRENT_DAY_RANGE)
            result = service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=CURRENT_DAY_RANGE).execute()
            values = result.get('values', [])
        else:
            insertTime(studentId, "in",CURRENT_DAY_RANGE)
            result = service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=CURRENT_DAY_RANGE).execute()
            values = result.get('values', [])