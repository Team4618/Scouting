from os import chdir, path, getcwd
from tkinter import *
from tkinter.filedialog import askdirectory
from tkinter.ttk import *

import pickList
import scouting
from tba import getTeamEvents, isOnline

# static vars
filedir = "files"
team = 4618
events = getTeamEvents(team)

if not isOnline():
    event = "No internet connection"
else:
    event = next((iter(events.values())))  # default value


class GUI:
    def __init__(self, parent, *args):
        self.parent = parent

        # main notebook
        self.root = Notebook(parent)
        self.root = Notebook(parent)
        self.root.pack(expand=True, fill=BOTH)

        self.scoutingPage = scouting.ScoutingUI(self.root)
        self.pickListPage = pickList.PickList(self.root)

        self.root.select(1)  # select the pick list page

        chooseFileBtn = Button(parent, text="Choose data folder", command=self.getFileDir)
        chooseFileBtn.pack(side=LEFT)

        # set our working directory
        chdir(path.dirname(__file__))

        # set a reference to the current directory where we're looking for data
        self.fileStrVar = StringVar()

        global filedir
        filedir = getcwd() + "\\files"

        if len(filedir) > 20:
            filedir = "..." + filedir[-17:]

        self.fileStrVar.set(filedir)
        Label(parent, textvariable=self.fileStrVar).pack(side=LEFT)

        # selector for event
        self.eventSV = StringVar()
        self.eventSV.set(event)

        self.eventSV.trace('w', self.onEventChange)

        eventList = ["No internet connection"]

        if isOnline():
            eventList = list(events.keys())

        eventChooser = OptionMenu(parent, self.eventSV, *eventList)
        eventChooser.pack(side=RIGHT)

        Label(parent, text="Event:").pack(side=RIGHT)

    def printToUI(self):
        # this will print to our UI in the scouting tab
        pass

    def getFileDir(self):
        global fileDir
        fileDir = askdirectory()  # opens file chooser window
        if len(fileDir) > 20:
            fileDir = "..." + fileDir[-17:]  # last 17 chars of the string

        self.fileStrVar.set(fileDir)
        return fileDir

    def onEventChange(self, *args2):
        if not isOnline():
            return

        event = events[self.eventSV.get()]
        self.pickListPage.reloadTeams(event)


if __name__ == "__main__":
    root = Tk()
    root.title("Robotics")
    root.iconbitmap('icon.ico')
    app = GUI(root)
    root.mainloop()

    if scouting.clicked:
        scouting.socket.close()
