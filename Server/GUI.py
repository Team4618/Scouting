from os import chdir, path, getcwd
from tkinter import *
from tkinter.filedialog import askdirectory
from tkinter.ttk import *

import pickList
import scouting

# static vars
filedir = "files"


class GUI:
    def __init__(self, parent, *args):
        self.parent = parent

        # main notebook
        self.root = Notebook(parent)
        self.root.pack(expand=True, fill=BOTH)

        self.scoutingPage = scouting.scoutingUI(self.root)
        self.pickListPage = pickList.pickList(self.root)

        self.root.select(1)  # select the pick list page

        chooseFileBtn = Button(parent, text="Choose data folder", command=self.getFileDir)
        chooseFileBtn.pack()

        # set our working directory
        chdir(path.dirname(__file__))

        # set a reference to the current directory where we're looking for data
        self.fileStrVar = StringVar()

        global filedir
        filedir = getcwd() + "\\files"

        if len(filedir) > 20:
            filedir = "..." + filedir[-17:]

        self.fileStrVar.set(filedir)
        Label(parent, textvariable=self.fileStrVar).pack()

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


class team:
    def __init__(self, teamNumber):
        pass


if __name__ == "__main__":
    root = Tk()
    root.title("Robotics")
    app = GUI(root)
    root.mainloop()
