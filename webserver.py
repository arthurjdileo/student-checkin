from __future__ import print_function
from flask import *
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from datetime import *
import webbrowser
from main import *
import json
app = Flask(__name__)

# for search page, gets the range of the student's in/outs for the day
def getStudentRange(studentId):
    values = readValues()
    index = 1
    for col in range(1, len(values)):
        for val in values[col]:
            if ids[studentId] == val:
                index += 1
                return ("A" + str(index) + ":Z" + str(index))
        index += 1
    return -1


CURRENT_DAY_RANGE = "Template"

updateSpreadsheetVals(SPREADSHEET_ID, CURRENT_DAY_RANGE)
values = readValues()


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/", methods=['POST','GET'])
def parse():
    if request.method == "POST":
        try:
            # gets the current sheet to input data on
            CURRENT_DAY_RANGE = newDay()
            CURRENT_DAY_SHEETID = findSheetId(CURRENT_DAY_RANGE)
            updateSpreadsheetVals(SPREADSHEET_ID, CURRENT_DAY_RANGE)
            values = readValues()
            print(values)
        except:
            exit()

        # refreshes the values of the page
        studentId = int(request.form.getlist('studentId')[0])
        # is the student an ECA student?
        if studentId in whitelist:
            # is the student already checked in? if so, check them out.
            updateSpreadsheetVals(SPREADSHEET_ID, CURRENT_DAY_RANGE)
            values = readValues()
            if isCheckedIn(values, studentId):
                # add out time to doc
                checkOut(values, studentId, CURRENT_DAY_RANGE, CURRENT_DAY_SHEETID)
            else:
                # check in the student
                checkIn(values, studentId, CURRENT_DAY_RANGE, CURRENT_DAY_SHEETID)
            # update vals
            updateSpreadsheetVals(SPREADSHEET_ID, CURRENT_DAY_RANGE)
            values = readValues()
        return render_template("home.html")

@app.route("/logs")
def logs():
    return render_template("logs.html")

@app.route("/search", methods=['POST','GET'])
def search():
    # did the user submit the form?
    searched=False
    if request.method == "POST":
        searched=True
        # get all of the sheets ids into a list
        sheet_metadata = service.spreadsheets().get(
            spreadsheetId=SPREADSHEET_ID).execute()
        sheets = sheet_metadata.get('sheets', '')
        sheetIds = list()
        for sheet in range(len(sheets)):
            #skip the template file
            if sheet == 0:
                continue
            sheetIds.append(findSheetId(sheets[sheet]["properties"]["title"]))
        # get the sheet range of just the student
        studentRange = getStudentRange(int(request.form.getlist('studentId')[0]))
        return render_template("search.html", sheetIds=sheetIds,
                               studentRange=studentRange, searched=searched)
    # render w/o any details
    return render_template("search.html")


@app.route("/edit", methods=["POST","GET"])
def edit():
    #IN-PROGRESS
    updateSpreadsheetVals(SPREADSHEET_ID, "Template")
    values = readValues()
    roster = list()
    print(values)
    for r in range(len(values)):
        if r == 0:
            continue
        temp = list()
        for c in range(len(values[0])):
            if c == 2:
                break
            temp.append(values[r][c])
        roster.extend([temp])

    print(roster)
    return render_template("edit.html", roster=roster)

if __name__ == "__main__":
    app.run(debug=True)