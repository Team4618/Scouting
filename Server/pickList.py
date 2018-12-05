from tkinter import *
from tkinter.filedialog import asksaveasfilename
from tkinter.ttk import *

import GUI
import tba


class PickList:
    # every function that takes *args does so because tkinter likes to provide variables that I don't need or care about
    def __init__(self, parent, *args):
        self.pickList = []
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

        # TODO: load teams from tba
        self.reloadTeams(GUI.event)

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
        self.pickListBox.bind("<Up>", self.rearrangeUp)
        self.pickListBox.bind("<Down>", self.rearrangeDown)
        self.pickListBox.bind("<Left>", self.removeFromPickList)
        self.pickListBox.pack(side=RIGHT, fill=Y)

        # remove from picklist button
        Button(self.pickListLabelFrame, text="Remove", command=self.removeFromPickList).pack(anchor=NW)

        # save picklist button
        Button(self.pickListLabelFrame, text="Save", command=self.savePickList).pack(anchor=NW)

    def selectTeamFromTeamList(self, *args):
        if not tba.isOnline():
            return

        selected = self.teamsListBox.curselection()
        self.selectTeamFromList(self.teamsListBox.get(selected))

    def selectTeamFromPickList(self, *args):
        self.selectTeamFromList(self.pickListBox.get(self.pickListBox.curselection()))

    def selectTeamFromList(self, teamnumber):
        if not tba.isOnline():
            return

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
        self.teamsListBox.delete(self.teamsListBox.curselection())

    def removeFromPickList(self, *args):
        # literally the inverse of addToPickList
        try:
            del self.pickList[self.pickListBox.curselection()[0]]
        except IndexError:
            return

        index = self.pickListBox.curselection()[0]

        self.teamsListBox.insert(END, self.pickListBox.get(index)[len(str(index)) + 2:])
        self.pickListBox.delete(index)
        self.fixLineNumbers()

    def fixLineNumbers(self):
        for i in range(self.pickListBox.size()):
            teamNumberStr = str(self.pickList[i])

            self.pickListBox.delete(i)
            self.pickListBox.insert(i, str(i + 1) + ". " + teamNumberStr)

    def search(self, *args):
        self.teamsListBox.delete(0, END)
        for i in self.teams:
            if self.searchText.get() in i:
                self.teamsListBox.insert(END, i)

    def rearrangeUp(self, *args):
        try:
            index = self.pickListBox.curselection()[0]
        except IndexError:
            return

        if index == 0:
            return

        self.pickList[index], self.pickList[index - 1] = self.pickList[index - 1], self.pickList[index]
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
        self.fixLineNumbers()
        self.pickListBox.selection_set(index + 1)

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

        for team in teams:
            self.teamsListBox.insert(END, str(team))

    def savePickList(self):
        file = asksaveasfilename(initialdir=GUI.filedir, title="Save Picklist", filetypes=(("Text files", "*.txt"),))

        if file == "":
            return

        if not file.endswith('.txt'):
            file += '.txt'

        with open(file, 'wt') as f:
            for i in self.pickList:
                f.write(str(i))
                f.write('\n')
