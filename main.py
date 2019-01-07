#!/usr/bin/env python

from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from datetime import *
import webbrowser

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

# updates variable with correct values in spreadsheet
def updateSpreadsheetVals(values):
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=CURRENT_DAY_RANGE).execute()
    return result.get('values', [])

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
                            "title": currentDate,
                            "index": 1
                        },
                        "fields": "title, index",
                    }
                }
            ]
        }

    request = service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID,
                                                 body=requestBody2)
    request.execute()
    return duplicated["sheetId"]

def removeSheet(sheetName):
    sheetID = findSheetId(sheetName)
    requestBody = \
        {
            "requests": [
                {
                    "deleteSheet": {
                        "sheetId": sheetID
                    }
                }
            ]
        }

    request = service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID,
                                                 body=requestBody)
    request.execute()

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
    return datetime.now().strftime("%I:%M%p")

#gets the current date. format: MM:DD:YY
def getDate():
    return datetime.now().strftime("%m/%d/%y")

#gets day of week in numerical form. format: NUM{0,6}
def getWeek():
    return date.today().weekday()

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

# runs through the check in process
def checkIn(studentId, CURRENT_DAY_RANGE, CURRENT_DAY_SHEETID):
    insertTime(studentId, "in", CURRENT_DAY_RANGE)
    changeCellColor(CURRENT_DAY_SHEETID, findStudentIndex(studentId),
                    "green")

# runs through the check out process
def checkOut(studentId, CURRENT_DAY_RANGE, CURRENT_DAY_SHEETID):
    insertTime(studentId, "out", CURRENT_DAY_RANGE)
    changeCellColor(CURRENT_DAY_SHEETID, findStudentIndex(studentId),
                    "red")

# checks if the current student is checked in
def isCheckedIn(studentId):
    checkedInIndex = findNextTimeInIndex(studentId)
    checkedOutIndex = findNextTimeOutIndex(studentId)
    if checkedInIndex < checkedOutIndex: return False
    else: return True

#gets a list of the current sheets in the document
def getSheets():
    sheet_metadata = service.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID).execute()
    sheets = sheet_metadata.get('sheets', '')
    listOfSheets = list()
    for sheet in sheets:
        listOfSheets.append(sheet["properties"]["title"])
    return listOfSheets

# detects if there is a new day and updates the current sheet to edit
def newDay():
    sheets = getSheets()
    currentDate = getDate()
    # assure we are only making pages for the weekdays
    week = getWeek()
    if currentDate not in sheets and week not in {6,7}:
        duplicateSheet(currentDate)
    return currentDate

# finds the sheetID given string name of sheet
def findSheetId(title):
    sheet_metadata = service.spreadsheets().get(
        spreadsheetId=SPREADSHEET_ID).execute()
    sheets = sheet_metadata.get('sheets', '')
    sheetIdDict = dict()
    for i in range(len(sheets)):
        sheetIdDict[sheets[i]["properties"]["title"]] = sheets[i]["properties"]["sheetId"]
    return sheetIdDict[title]


# changes the background color of a cell
def changeCellColor(CURRENT_SHEETID, studentIndex, type):
    redRequest = \
        {
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": CURRENT_SHEETID,
                            "startRowIndex": studentIndex,
                            "endRowIndex": studentIndex+1,
                            "startColumnIndex": 0,
                            "endColumnIndex": 1
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "backgroundColor": {
                                    "red": 0.95686,
                                    "green": 0.78039,
                                    "blue": 0.76471
                                }
                            }
                        },
                        "fields": "userEnteredFormat.backgroundColor"
                    }
                }
            ]
        }

    greenRequest = \
        {
            "requests": [
                {
                    "repeatCell": {
                        "range": {
                            "sheetId": CURRENT_SHEETID,
                            "startRowIndex": studentIndex,
                            "endRowIndex": studentIndex + 1,
                            "startColumnIndex": 0,
                            "endColumnIndex": 1
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "backgroundColor": {
                                    "red": 0.71765,
                                    "green": 0.88235,
                                    "blue": 0.80392
                                }
                            }
                        },
                        "fields": "userEnteredFormat.backgroundColor"
                    }
                }
            ]
        }

    if type == "red":
        request = service.spreadsheets().batchUpdate(spreadsheetId=SPREADSHEET_ID,
                                                 body=redRequest)
    else:
        request = service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body=greenRequest)
    return request.execute()

# checks out all students coloring only the students that have actually signed in
def autoCheckout(ecaDict, CURRENT_DAY_RANGE, CURRENT_DAY_SHEETID):
    for studentId in ecaDict:
        if isCheckedIn(studentId):
            checkOut(studentId, CURRENT_DAY_RANGE, CURRENT_DAY_SHEETID)
        else:
            insertTime(studentId, "out", CURRENT_DAY_RANGE)

# deletes sheets older than 30 days
def expirePages(CURRENT_DAY_RANGE):
    delta = timedelta(days=30)
    CURRENT_DAY_RANGE = datetime.strptime(CURRENT_DAY_RANGE, "%m/%d/%y")
    delimiter = CURRENT_DAY_RANGE - delta
    sheets = getSheets()
    for i in range(1, len(sheets)):
        if datetime.strptime(sheets[i], "%m/%d/%y") < (delimiter):
            removeSheet(sheets[i])

# Opens the google sheet w/ day as current sheet
def openDoc(sheetId):
    url = "https://docs.google.com/spreadsheets/u/1/d/1jsNGLL-Nr0gkaAhqweQqjuPVxup0DfgTLf81X3gdmZU/edit#gid=" + str(sheetId)
    webbrowser.open_new(url)


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

result = service.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID,
    range=CURRENT_DAY_RANGE).execute()
values = result.get('values', [])

ids = getECADictionary(values)
whitelist = getWhitelist(ids)

# lists commands
print("**********")
print("Clean - Delete sheets older than 30 days.")
print("Out - Checks out all students for the day. Students not highlighted were absent.")
print("**********")

if __name__ == "__main__":
    while True:

        # waits for input from barcode scanner (can be inserted manually)
        studentId = input("Enter ID: ")

        # gets the current sheet to input data on
        try:
            CURRENT_DAY_RANGE = newDay()
            CURRENT_DAY_SHEETID = findSheetId(CURRENT_DAY_RANGE)
        except:
            print("This program does not work on the weekends.")
            exit()

        # refreshes the values of the page
        values = updateSpreadsheetVals(values)

        # remove sheets older than 30 days
        if studentId.lower() == "clean":
            expirePages(CURRENT_DAY_RANGE)
            print("Sheets older than 30 days have been deleted!")

        # auto checks out
        elif studentId.lower() == "out":
            autoCheckout(ids, CURRENT_DAY_RANGE, CURRENT_DAY_SHEETID)
            print("All students have been checked out for the day.")

        # opens doc on today's sheet
        elif studentId.lower() == "open":
            openDoc(CURRENT_DAY_SHEETID)

        # runs thru normal procedure
        else:
            # avoids error where ID returns .jpg as the ID num
            if ".JPG" in studentId:
                studentId = studentId[:7]
            studentId = int(studentId)
            # is the student an ECA student?
            if studentId in whitelist:
                # is the student already checked in? if so, check them out.
                if isCheckedIn(studentId):
                    # add out time to doc
                    checkOut(studentId, CURRENT_DAY_RANGE, CURRENT_DAY_SHEETID)
                else:
                    # check in the student
                    checkIn(studentId, CURRENT_DAY_RANGE, CURRENT_DAY_SHEETID)
                # update vals
                values = updateSpreadsheetVals(values)