from tkinter import *
from tkinter.ttk import *

import tba


class PickList:
    def __init__(self, parent, *args):
        self.pickList = []
        self.parent = parent
        # team picking page of notebook
        self.page = Frame(parent)
        parent.add(self.page, text="Pick List")

        # setup team list container
        self.teamlistLabelFrame = LabelFrame(self.page, text="Teams")
        self.teamlistLabelFrame.pack(side=LEFT, fill=Y)

        # scroll bar
        teamsScrollBar = Scrollbar(self.teamlistLabelFrame)

        self.teamsListBox = Listbox(self.teamlistLabelFrame, yscrollcommand=teamsScrollBar.set, selectmode=SINGLE)
        self.teamsListBox.pack(side=LEFT, fill=Y)
        self.teamsListBox.bind("<Double-Button-1>", self.selectTeamFromTeamList)

        # TODO: load teams from tba
        self.teamsListBox.insert(END, "772")
        self.teamsListBox.insert(END, "4618")
        self.teamsListBox.insert(END, "254")
        self.teamsListBox.insert(END, "5406")
        self.teamsListBox.insert(END, "2056")
        self.teamsListBox.insert(END, "4939")
        self.teamsListBox.insert(END, "4039")
        self.teamsListBox.insert(END, "1310")
        self.teamsListBox.insert(END, "1360")

        teamsScrollBar.config(command=self.teamsListBox.yview)

        # button to add team to pick list (we'll have drag and drop too)
        Button(self.teamlistLabelFrame, text="Add", command=self.addToPickList).pack(anchor=N, side=RIGHT)
        teamsScrollBar.pack(side=RIGHT, fill=Y)  # pack this after so its left of the button

        # this should be in the middle: team info
        self.teamInfoFrame = Frame(self.page)
        self.teamInfoFrame.pack(side=LEFT, fill=BOTH)

        self.teamInfoHeader = StringVar()
        teamInfoHeaderLabel = Label(self.teamInfoFrame, textvariable=self.teamInfoHeader)
        teamInfoHeaderLabel.grid(row=0, column=0)

        self.teamAttendedEvents = StringVar()
        attenedEvents = Label(self.teamInfoFrame, textvariable=self.teamAttendedEvents)
        attenedEvents.grid(row=1, column=0)

        # pick list, should be on the right
        self.pickListLabelFrame = LabelFrame(self.page, text="Pick List")
        self.pickListLabelFrame.pack(side=RIGHT, fill=Y)

        # scroll bar
        pickListScrollBar = Scrollbar(self.pickListLabelFrame)
        pickListScrollBar.pack(side=RIGHT, fill=Y)

        self.pickListBox = Listbox(self.pickListLabelFrame, yscrollcommand=pickListScrollBar.set, selectmode=SINGLE)
        self.pickListBox.bind("<Double-Button-1>", self.selectTeamFromPickList)

        # remove from picklist button
        Button(self.pickListLabelFrame, text="Remove", command=self.removeFromPickList).pack(anchor=N, side=LEFT)
        self.pickListBox.pack(side=LEFT, fill=Y)  # pack this after so button is to the left

    def selectTeamFromTeamList(self, *args):
        self.selectTeamFromList(self.teamsListBox.get(self.teamsListBox.curselection()))

    def selectTeamFromPickList(self, *args):
        self.selectTeamFromList(self.pickListBox.get(self.pickListBox.curselection()))

    def selectTeamFromList(self, teamnumber):
        # from here we pull up all the data we have on that team from our sources (scouting data and tba),
        # this is a placeholder
        # TODO: use team module instead
        teaminfo = tba.getTeamInfo(teamnumber)

        teamname = teaminfo['teamName']

        attendedEvents = "Attended events:\n"
        for event, record in teaminfo['attendedEvents'].items():
            attendedEvents += "{}:{}".format(event, record)
            attendedEvents += '\n'

        self.teamInfoHeader.set("Team " + teamnumber + " : " + teamname)
        self.teamAttendedEvents.set(attendedEvents)

    def addToPickList(self):
        # TODO: store the picklist in an array of teams instead of strings/ints
        self.pickList.append(self.teamsListBox.get(self.teamsListBox.curselection()))

        length = self.pickListBox.size()

        self.pickListBox.insert(END,
                                str(length + 1) + ". " + str(self.teamsListBox.get(self.teamsListBox.curselection())))
        self.teamsListBox.delete(self.teamsListBox.curselection())

    def removeFromPickList(self):
        # literally the inverse of addToPickList
        del self.pickList[self.pickListBox.curselection()[0]]

        index = self.pickListBox.curselection()[0]

        self.teamsListBox.insert(END, self.pickListBox.get(index)[len(str(index)) + 2:])
        self.pickListBox.delete(index)
        self.fixLineNumbers()

    def fixLineNumbers(self):
        for i in range(self.pickListBox.size()):
            teamNumberStr = str(self.pickList[i])

            self.pickListBox.delete(i)
            self.pickListBox.insert(i, str(i + 1) + ". " + teamNumberStr)
