import json
from os import fsencode, fsdecode, listdir, path, getcwd

import GUI
import tba

teams = []

imagetypes = [".jpg", ".jpeg", ".jpe", ".jfif", ".jif"]  # jpgs
imagetypes += [".png"]  # pngs


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

        self.image = GUI.filedir + "\\images\\default.jpg"
        for extension in imagetypes:
            imgpath = GUI.filedir + "\\images\\" + str(teamNumber) + extension
            if path.isfile(imgpath):
                self.image = imgpath
                break

            imgpath = GUI.filedir + "\\images\\" + str(teamNumber) + extension.upper()
            if path.isfile(imgpath):
                self.image = imgpath
                break

        if not inList(self, teams):
            teams.append(self)

    def getTeamInfoFromJSON(self):
        # loop through each JSON file and find our team data

        rawJSON = []
        for file in listdir(GUI.filedir):
            if file.lower().endswith(".json"):
                try:
                    with open(GUI.filedir + '\\' + file) as f:
                        fileJson = json.load(f)

                        for i in fileJson:
                            try:
                                if i['robot'] == int(self.number):
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
            if i.number == team.number:
                return True

    return False


def loadAllTeamsData(teams):
    for team in teams:
        Team(team)


def getTeamFromArray(number):
    for team in teams:
        if team.number == number:
            return team

    return None
