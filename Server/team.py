import json
from os import fsencode, fsdecode, listdir

import GUI
import tba

teams = []


class Team:
    def __init__(self, teamNumber):
        self.number = teamNumber
        tbaInfo = tba.getTeamInfo(teamNumber)

        self.name = None
        self.attendedEvents = None

        if tba.isOnline():  # will be false if no internet or can't connect to tba
            self.name = tbaInfo['teamName']
            self.attendedEvents = tbaInfo['attendedEvents']

        self.getTeamInfoFromJSON()

        if not inList(self, teams):
            teams.append(self)

    def getTeamInfoFromJSON(self):
        # loop through each JSON file and find our team data

        rawJSON = []
        for file in listdir(fsencode(GUI.filedir)):
            fileName = fsdecode(file)

            if fileName.lower().endswith(".json"):
                try:
                    with open(file) as f:
                        fileJson = json.load(f)

                        for i in fileJson:
                            try:
                                if i['robot'] == str(self.number):
                                    rawJSON.append(i)

                            except TypeError:  # whatever we just encountered wasn't a dict, so we should ignore it
                                continue
                            except KeyError:  # this was a dict, but not one which contains our JSON data
                                continue
                except FileNotFoundError:
                    self.JSONdata = []

        # sort into a dict keyed by match number
        self.JSONdata = {}
        for i in rawJSON:
            match = i['match']

            while 1:
                if match in self.JSONdata:
                    match = str(match) + '_'
                else:
                    self.JSONdata[match] = i
                    break


def inList(team, l):
    if type(l) is not list or type(team) is not Team:
        return False

    for i in l:
        if type(i) is Team:
            print(i.number)
            print(team.number)
            print(i.number == team.number)
            print()
            if i.number == team.number:
                return True

    return False


def loadAllTeamsData(teams):
    for team in teams:
        Team(team)
