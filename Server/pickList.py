from json import load as loadJSON
from os import startfile
from platform import system
from subprocess import call as subCall
from tkinter import *
from tkinter.filedialog import asksaveasfilename
from tkinter.ttk import *

from PIL import Image, ImageTk

import GUI
import tba
from team import Team


class PickList:
    # every function that takes *args does so because tkinter likes to provide variables that I don't need or care about

    def __init__(self, parent, *args):
        self.pickList = []
        self.tags = []
        self.teams = []
        self.remainingTeams = []
        self.parent = parent
        # team picking page of notebook
        self.page = Frame(parent)
        parent.add(self.page, text="Pick List")

        # setup team list container
        self.teamlistLabelFrame = LabelFrame(self.page, text="Teams")
        self.teamlistLabelFrame.pack(side=LEFT, fill=Y)

        # search bar
        self.searchText = StringVar()
        self.searchText.set("Search")
        self.searchText.trace('w', self.search)
        searchBar = Entry(self.teamlistLabelFrame, textvariable=self.searchText)
        searchBar.pack(anchor=N, fill=X)

        # scroll bar
        teamsScrollBar = Scrollbar(self.teamlistLabelFrame)

        self.teamsListBox = Listbox(self.teamlistLabelFrame, yscrollcommand=teamsScrollBar.set, selectmode=SINGLE)
        self.teamsListBox.pack(side=LEFT, fill=Y)
        self.teamsListBox.bind("<Double-Button-1>", self.selectTeamFromTeamList)
        self.teamsListBox.bind("<Right>", self.addToPickList)

        self.reloadTeams(GUI.event)

        teamsScrollBar.config(command=self.teamsListBox.yview)

        # button to add team to pick list (we'll have drag and drop too)
        Button(self.teamlistLabelFrame, text="Add", command=self.addToPickList).pack(anchor=NE)
        Button(self.teamlistLabelFrame, text="Blacklist", command=self.blackList).pack(anchor=NE)
        teamsScrollBar.pack(side=RIGHT, fill=Y)  # pack this after so its left of the button

        # blacklist
        self.blacklistLabelFrame = LabelFrame(self.page, text="Blacklist")
        self.blacklistLabelFrame.pack(side=LEFT, fill=Y)

        self.blackListBox = Listbox(self.blacklistLabelFrame, selectmode=SINGLE)
        self.blackListBox.pack(side=LEFT, fill=Y)
        self.blackListBox.bind("<Double-Button-1>", self.selectTeamFromBlackList)

        Button(self.blacklistLabelFrame, text="Remove from blacklist", command=self.unBlackList).pack(anchor=NE)

        # this should be in the middle: team info
        self.teamInfoFrame = Frame(self.page)
        self.teamInfoFrame.pack(side=LEFT, fill=BOTH, expand=True)

        # pick list, should be on the right
        self.pickListLabelFrame = LabelFrame(self.page, text="Pick List")
        self.pickListLabelFrame.pack(side=RIGHT, fill=Y)

        # scroll bar
        pickListScrollBar = Scrollbar(self.pickListLabelFrame)
        pickListScrollBar.pack(side=RIGHT, fill=Y)

        self.pickListBox = Listbox(self.pickListLabelFrame, yscrollcommand=pickListScrollBar.set, selectmode=SINGLE)
        self.pickListBox.bind("<Double-Button-1>", self.selectTeamFromPickList)
        self.pickListBox.bind("<Up>", self.rearrangeUp)
        self.pickListBox.bind("<Down>", self.rearrangeDown)
        self.pickListBox.bind("<Left>", self.removeFromPickList)
        self.pickListBox.pack(side=RIGHT, fill=Y)

        # remove from picklist button
        Button(self.pickListLabelFrame, text="Remove", command=self.removeFromPickList).pack(anchor=NW)

        # save picklist button
        Button(self.pickListLabelFrame, text="Save", command=self.savePickList).pack(anchor=NW)

        # add tag button
        Button(self.pickListLabelFrame, text="Add tag", command=self.addTag).pack(anchor=NW)

    ###############
    # UI FUNCTIONS
    ###############

    def fixLineNumbers(self):
        for i in range(self.pickListBox.size()):
            teamNumberStr = str(self.pickList[i])

            self.pickListBox.delete(i)
            self.pickListBox.insert(i, str(i + 1) + ". " + teamNumberStr)
            self.pickListBox.insert(i, str(i + 1) + ". " + teamNumberStr)

    def search(self, *args):
        self.teamsListBox.delete(0, END)
        for i in self.remainingTeams:
            if self.searchText.get() in str(i):
                self.teamsListBox.insert(END, i)

    def rearrangeUp(self, *args):
        try:
            index = self.pickListBox.curselection()[0]
        except IndexError:
            return

        if index == 0:
            return

        self.pickList[index], self.pickList[index - 1] = self.pickList[index - 1], self.pickList[index]
        self.tags[index], self.tags[index - 1] = self.tags[index - 1], self.tags[index]
        self.fixLineNumbers()
        self.pickListBox.selection_set(index - 1)

    def rearrangeDown(self, *args):
        try:
            index = self.pickListBox.curselection()[0]
        except IndexError:
            return

        if index == self.pickListBox.size() - 1:
            return

        self.pickList[index], self.pickList[index + 1] = self.pickList[index + 1], self.pickList[index]
        self.tags[index], self.tags[index + 1] = self.tags[index + 1], self.tags[index]
        self.fixLineNumbers()
        self.pickListBox.selection_set(index + 1)

    def selectTeamFromTeamList(self, *args):
        if not tba.isOnline():
            return

        selected = self.teamsListBox.curselection()
        self.selectTeamFromList(self.teamsListBox.get(selected))

    def selectTeamFromPickList(self, *args):
        self.selectTeamFromList(str(self.pickList[self.pickListBox.curselection()[0]]))

    def selectTeamFromBlackList(self, *args):
        self.selectTeamFromList(str(self.blackListBox.get(self.blackListBox.curselection())))

    def selectTeamFromList(self, teamNumber):
        if not tba.isOnline():
            return
        # TODO: use team module instead
        # do we? idk? this whole thing has gone to crap and i cant wait to nuke it

        team = Team(teamNumber)

        teamname = team.name

        attendedEvents = "Attended events:\n"
        for event, record in team.attendedEvents.items():
            attendedEvents += "{}:{}".format(event, record)
            attendedEvents += '\n'

        for child in self.teamInfoFrame.winfo_children():
            child.destroy()

        header = Label(self.teamInfoFrame, text="Team " + str(teamNumber) + " : " + teamname,
                       font=("Helvetica", 20, "bold"))
        header.grid(row=0, column=0, columnspan=9999)

        attendedEvents = Label(self.teamInfoFrame, text=attendedEvents)
        attendedEvents.grid(row=1, column=0)

        # setup team image
        img = Image.open(team.image)

        def onImageClick(event):
            if system() == 'Darwin':  # macOS
                subCall(('open', team.image))
            elif system() == 'Windows':  # Windows
                startfile(team.image)
            else:  # linux variants
                subCall(('xdg-open', team.image))

        # 231 x 231 is about the size of our defualt image, use that as our max size
        img.thumbnail((231, 231), Image.ANTIALIAS)

        self.photo = ImageTk.PhotoImage(img)
        imgLabel = Label(self.teamInfoFrame, image=self.photo)
        imgLabel.bind("<Button-1>", onImageClick)  # call onImageClick when mouse1 is pressed on the image
        imgLabel.grid(row=1, column=1, padx=10, pady=10)

        # display scouting data
        scoutingDataFrame = Frame(self.teamInfoFrame)
        scoutingDataFrame.grid(row=2, column=0, columnspan=2, sticky=NSEW)

        # setup scroll bars and listbox to display the data
        scrollx = Scrollbar(scoutingDataFrame, orient=HORIZONTAL)
        scrolly = Scrollbar(scoutingDataFrame)
        scoutingDataLB = Listbox(scoutingDataFrame, xscrollcommand=scrollx.set, yscrollcommand=scrolly.set)
        scrollx.config(command=scoutingDataLB.xview)
        scrolly.config(command=scoutingDataLB.yview)

        scrollx.grid(row=1, column=0, sticky=EW)
        scrolly.grid(row=0, column=1, sticky=NS)
        scoutingDataLB.grid(row=0, column=0, sticky=NSEW)
        scoutingDataFrame.columnconfigure(0, weight=1)

        # setup seperate box for comments because massimo wants it
        commentsScrollx = Scrollbar(scoutingDataFrame, orient=HORIZONTAL)
        commentsScrolly = Scrollbar(scoutingDataFrame)
        commentsLB = Listbox(scoutingDataFrame, xscrollcommand=commentsScrollx.set, yscrollcommand=commentsScrolly.set)
        commentsScrollx.config(command=commentsLB.xview)
        commentsScrolly.config(command=commentsLB.yview)

        commentsScrollx.grid(row=3, column=0)
        commentsScrolly.grid(row=2, column=1)
        commentsLB.grid(row=2, column=0, sticky=NSEW)
        commentsLB.insert(END, "Comments:")

        # load template
        with open("template.json", "r") as f:
            template = loadJSON(f)

        # loop though our scouting data, grab each question, and display it

        # categorize our data
        # vars for ints
        totals = {}
        increments = {}

        # non-ints
        nonInts = {}  # going to be like this {question0:[data from match 1, match 2, match 3], question1:[...
        for key_, value_ in team.JSONdata.items():
            for key, value in value_.items():

                if key == "robot" or key == "match":
                    continue

                if type(value) is int:
                    try:
                        totals[key] += value
                        increments[key] += 1
                    except KeyError:
                        totals[key] = value
                        increments[key] = 1

                else:
                    if type(value) == bool:
                        value = "Yes" if value else "No"

                    try:
                        nonInts[key].append(value)
                    except KeyError:
                        nonInts[key] = [value]

        for key, value in totals.items():
            # find the question
            question = ""
            for i in template:
                try:
                    if i['jsonLabel'] == key:
                        question = i['question']
                except KeyError:
                    pass

            # add this question to our data output
            scoutingDataLB.insert(END, question + " : " + str(round((float(value) / increments[key]), 2)))

        for key, value in nonInts.items():
            # find the question
            # this is pretty similar to the previous loop and could probably be combined but at this point idk
            if key != "comments":
                question = ""
                for i in template:
                    try:
                        if i['jsonLabel'] == key:
                            question = i['question']
                    except KeyError:
                        pass

                # add it to our box/output
                scoutingDataLB.insert(END, question + ":")

            for i in value:
                if i.strip() != '':
                    if key == "comments":
                        commentsLB.insert(END, "    " + i)
                    else:
                        scoutingDataLB.insert(END, "    " + i)

    def savePickList(self):
        file = asksaveasfilename(initialdir=GUI.filedir, title="Save Picklist", filetypes=(("Text files", "*.txt"),))

        if file == "":
            return

        if not file.endswith('.txt'):
            file += '.txt'

        with open(file, 'wt') as f:
            for i in range(len(self.pickList)):
                f.write(str(self.pickList[i]))
                f.write(": " + self.tags[i])
                f.write('\n')

    def addTag(self):
        self.tagIndex = self.pickListBox.curselection()[0]

        self.tagSv = StringVar()
        self.tagSv.set(self.tags[self.tagIndex])
        self.tagSv.trace('w', self.changeTag)

        popUp = Toplevel()
        Entry(popUp, textvariable=self.tagSv).pack()

    def changeTag(self, *args):
        # worker function for addTag()
        self.tags[self.tagIndex] = self.tagSv.get()

    # list manipulation

    def addToPickList(self, *args):
        if not tba.isOnline():
            return

        # TODO: store the picklist in an array of teams instead of strings/ints
        try:
            self.pickList.append(self.teamsListBox.get(self.teamsListBox.curselection()))
        except TclError:
            return

        length = self.pickListBox.size()

        self.pickListBox.insert(END,
                                str(length + 1) + ". " + str(self.teamsListBox.get(self.teamsListBox.curselection())))
        self.tags.append("")
        del (self.remainingTeams[self.remainingTeams.index(self.teamsListBox.get(self.teamsListBox.curselection()))])
        self.teamsListBox.delete(self.teamsListBox.curselection())

    def removeFromPickList(self, *args):
        # literally the inverse of addToPickList
        try:
            del self.pickList[self.pickListBox.curselection()[0]]
        except IndexError:
            return

        index = self.pickListBox.curselection()[0]

        self.teamsListBox.insert(END, self.pickListBox.get(index)[len(str(index)) + 2:])
        self.remainingTeams.append(self.pickListBox.get(index)[len(str(index)) + 2:])
        self.pickListBox.delete(index)
        del (self.tags[index])
        self.fixLineNumbers()

    def blackList(self, *args):
        # blacklists a team
        try:
            self.blackListBox.insert(END, self.teamsListBox.get(self.teamsListBox.curselection()))
        except TclError:
            return

        del (self.remainingTeams[self.remainingTeams.index(self.teamsListBox.get(self.teamsListBox.curselection()))])
        self.teamsListBox.delete(self.teamsListBox.curselection())

    def unBlackList(self, *args):
        # inverse of blacklist()
        try:
            self.teamsListBox.insert(END, self.blackListBox.get(self.blackListBox.curselection()))
        except TclError:
            return

        self.remainingTeams.append(self.blackListBox.get(self.blackListBox.curselection()))
        self.blackListBox.delete(self.blackListBox.curselection())

    def reloadTeams(self, eventcode):
        try:
            self.pickListBox.delete(0, END)
        except AttributeError:  # we haven't created it yet
            pass

        self.teamsListBox.delete(0, END)

        if tba.isOnline():
            teams = tba.getTeams(eventcode)
        else:
            teams = ["No internet connection"]

        self.teams = []
        for team in teams:
            self.teamsListBox.insert(END, str(team))
            self.teams.append(team)

        self.remainingTeams = self.teams

    '''def graph(self, data):
        # data should be an array of bools or ints
        dataType = type(data[0])

        if dataType == bool:
            labels = ['YES', 'NO']
        elif dataType == int:
            labels = []
            for i in data:
                toAdd = str(i)
                if toAdd not in labels:
                    labels.append(toAdd)
        else:
            return
        # TODO: add the data into an array and display the chart
        # https://matplotlib.org/gallery/pie_and_polar_charts/pie_features.html'''
