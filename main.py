from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import datetime
import time

#full id num.jpg


# Goes through student list in template file and links id numbers to students
# stores in a dictionary
def getECADictionary(values):
    ecaDict = dict()
    idColumn = 1
    nameCol = 0

    for i in range(1, len(values)):
        ecaDict[int(values[i][idColumn])] = values[i][nameCol]
    return ecaDict

# Uses above dictionary to keep a whitelist of the student's that can use it
def getWhitelist(ids):
    whitelist = set()
    for key in ids:
        whitelist.add(int(key))
    return whitelist

# duplicates the template sheet. names the file the respective date
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

# finds the row index that pertains to the specific student based off ID
def findStudentIndex(studentId):
    index = 1
    for col in range(1, len(values)):
        for val in values[col]:
            if ids[studentId] == val:
                return index
        index += 1
    return -1 # can't find

# gets the current time. format: HH:MM:SS AM/PM
def getTime():
    return datetime.datetime.now().strftime("%I:%M%p")

#gets the current date. format: MM:DD:YY
def getDate():
    return datetime.datetime.now().strftime("%m/%d/%y")

#gets a list of the current sheets in the document
def getSheets():
    sheet_metadata = service.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID).execute()
    sheets = sheet_metadata.get('sheets', '')
    listOfSheets = set()
    for sheet in sheets:
        listOfSheets.add(sheet["properties"]["title"])
    return listOfSheets

# finds the next time in cell to use for the specific student.
# used for when a student checks in twice
def findNextTimeInIndex(studentId):
    #even row index
    rowIndex = findStudentIndex(studentId)

    for headerIndex in range(len(values[0])):
        if headerIndex % 2 == 0:
            if values[rowIndex][headerIndex] == "--":
                return headerIndex
    return -1 # out of space

# finds the next time out cell to use for the specific student.
# used for when a student checks out twice
def findNextTimeOutIndex(studentId):
    #odd row index
    rowIndex = findStudentIndex(studentId)

    for headerIndex in range(len(values[0])):
        if headerIndex % 2 == 1:
            if values[rowIndex][headerIndex] == "--":
                return headerIndex
    return -1 # out of space

# converts a (i,j) index of r,c to a sheets format of A:Z
def indicesToRange(studentIndex, headerIndex):
    headerCol = chr(65+headerIndex)
    return "%s%s" % (headerCol, studentIndex+1)

# inserts the current time for the specific student, in a in/out cell for the specific day
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

# checks if the current student is checked in
def isCheckedIn(studentId):
    checkedInIndex = findNextTimeInIndex(studentId)
    checkedOutIndex = findNextTimeOutIndex(studentId)
    if checkedInIndex < checkedOutIndex: return False
    else: return True

# detects if there is a new day and updates the current sheet to edit
def newDay():
    sheets = getSheets()
    currentDate = getDate()
    if currentDate not in sheets:
        duplicateSheet(currentDate)
    return currentDate

# changes the background color of a cell
def changeCellColor():
    redRequest = \
        {
            "requests": [
                {
                    "updateCell": {
                        "range": {
                            "sheetId": 1126291390,
                            "startRowIndex": 1,
                            "endRowIndex": 1,
                            "startColumnIndex": 1,
                            "endColumnIndex": 1
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "backgroundColor": {
                                    "red": 1,
                                    "green": 0,
                                    "blue": 0
                                }
                            }
                        },
                        "fields": "userEnteredFormat(backgroundColor)"
                    }
                }
            ]
        }

    request = service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID,
                                                 body=redRequest)
    return request.execute()



# Credentials (don't touch)
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('sheets', 'v4', http=creds.authorize(Http()))


# Call the Sheets API
SPREADSHEET_ID = '1jsNGLL-Nr0gkaAhqweQqjuPVxup0DfgTLf81X3gdmZU'
CURRENT_DAY_RANGE = "Template"

ids = getECADictionary(values)
whitelist = getWhitelist(ids)

while True:
    # gets the current sheet to input data on
    CURRENT_DAY_RANGE = newDay()
    # refreshes the values of the page
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                                 range=CURRENT_DAY_RANGE).execute()
    values = result.get('values', [])
    # waits for input from barcode scanner (can be inserted manually)
    studentId = input("Enter ID: ")
    studentId = int(studentId)
    # is the student an ECA student?
    if studentId in whitelist:
        # is the student already checked in? if so, check them out.
        if isCheckedIn(studentId):
            # add out time to doc
            insertTime(studentId, "out", CURRENT_DAY_RANGE)
            # update vals
            result = service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=CURRENT_DAY_RANGE).execute()
            values = result.get('values', [])
        else:
            # check in the student
            insertTime(studentId, "in",CURRENT_DAY_RANGE)
            # update vals
            result = service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID,
                range=CURRENT_DAY_RANGE).execute()
            values = result.get('values', [])