from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import datetime

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
result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                            range=RANGE_NAME).execute()
values = result.get('values', [])

whitelist = [2019240, 2019291,2019039,2019153,2019654]
ids = {2019240: "Arthur DiLeo Jr.", 2019291: "Nicholas Fierro", 2019039: "Charley Baker", 2019153: "Stephen Ciupinski", 2019654: "Jack Roddy"}

timedIn = list()
timedOut = list()
timedOut.extend(whitelist)

def duplicateSheet():
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
                            "title": datetime.datetime.now().strftime("%B %Y")
                        },
                        "fields": "title",
                    }
                }
            ]
        }

    request = service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID,
                                                 body=requestBody2)
    request.execute()
    return duplicated

def findStudentIndex(studentId):
    #finds the row index of the student's details
    # iterates col-major
    index = 1
    for col in range(len(values)):
        if col == 0:
            continue
        for val in values[col]:
            if ids[studentId] == val:
                return index
        index += 1
    return -1 # can't find

def getTime():
    return datetime.datetime.now().strftime("%I:%M%p")

def getDate():
    return datetime.datetime.now().strftime("%B %d, %Y")

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
    return "%s%s" % (headerCol, studentIndex+1)

def insertTime(studentId, status):
    studentIndex = findStudentIndex(studentId)
    if status == "in": headerIndex = findNextTimeInIndex(studentId)
    else: headerIndex = findNextTimeOutIndex(studentId)
    currentTime = getTime()
    body = {
        "range": indicesToRange(studentIndex, headerIndex),
        "majorDimension": "ROWS",
        'values': [[currentTime]]
    }
    service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range=indicesToRange(studentIndex,headerIndex),
        valueInputOption="USER_ENTERED", body=body).execute()

def isCheckedIn(studentId):
    checkedInIndex = findNextTimeInIndex(studentId)
    checkedOutIndex = findNextTimeOutIndex(studentId)
    if checkedInIndex < checkedOutIndex: return False
    else: return True


while True:
    studentId = input("Enter ID: ")
    studentId = int(studentId)
    if studentId in whitelist:
        if isCheckedIn(studentId):
            insertTime(studentId, "out")
            result = service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=RANGE_NAME).execute()
            values = result.get('values', [])
        else:
            insertTime(studentId, "in")
            result = service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=RANGE_NAME).execute()
            values = result.get('values', [])