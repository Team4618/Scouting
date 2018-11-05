from tkinter import *
from tkinter.ttk import *

import tba


class PickList:
    def __init__(self, parent, *args):
        self.parent = parent
        # team picking page of notebook
        self.page = Frame(parent)
        parent.add(self.page, text="Pick List")

        # setup team list container
        self.teamlistLabelFrame = LabelFrame(self.page, text="Teams")
        self.teamlistLabelFrame.pack(side=LEFT, fill=Y)

        # scroll bar
        teamsScrollBar = Scrollbar(self.teamlistLabelFrame)
        teamsScrollBar.pack(side=RIGHT, fill=Y)

        self.teamsListBox = Listbox(self.teamlistLabelFrame, yscrollcommand=teamsScrollBar.set)
        self.teamsListBox.pack(side=LEFT, fill=Y)
        self.teamsListBox.bind("<Double-Button-1>", self.selectTeamFromList)

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

        self.rightSide = Frame(self.page)
        self.rightSide.pack(side=LEFT, fill=BOTH)

        self.rightSideHeader = StringVar()
        rightSideStuff = Label(self.rightSide, textvariable=self.rightSideHeader)
        rightSideStuff.grid(row=0, column=0)

        self.teamAttendedEvents = StringVar()
        attenedEvents = Label(self.rightSide, textvariable=self.teamAttendedEvents)
        attenedEvents.grid(row=1, column=0)

        self.teamMedia = PhotoImage()
        teamMedia = Label(self.rightSide, image=self.teamMedia)

    def selectTeamFromList(self, *args):
        # from here we pull up all the data we have on that team from our sources (scouting data and tba),
        # this is a placeholder
        teamnumber = self.teamsListBox.get(self.teamsListBox.curselection())
        teaminfo = tba.getTeamInfo(teamnumber)

        teamname = teaminfo['teamName']

        attendedEvents = "Attended events:\n"
        for event, record in teaminfo['attendedEvents'].items():
            attendedEvents += "{}:{}".format(event, record)
            attendedEvents += '\n'

        self.rightSideHeader.set("Team " + teamnumber + " : " + teamname)
        self.teamAttendedEvents.set(attendedEvents)
