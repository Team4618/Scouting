from json import load as loadJSON
from operator import itemgetter
from os import listdir
from tkinter import *

import GUI


class Sort:
    def __init__(self, parent, *args):
        self.parent = parent
        self.page = Frame(parent)

        parent.add(self.page, text="Sort data")

        # init our scouting questions
        self.questionsFrame = LabelFrame(self.page, text="Questions")

        self.questionsListBox = Listbox(self.questionsFrame, selectmode=SINGLE)
        self.questionsListBox.bind("<Double-Button-1>", self.selectQuestion)
        self.refreshQuestions()

        self.questionsFrame.pack(fill=BOTH)
        self.questionsListBox.pack(fill=BOTH)
        self.reverseButton = Button(self.questionsFrame, text="Reverse order")

        self.sortedLB = Listbox(self.questionsFrame, selectmode=SINGLE)
        self.sortedLB.pack(fill=BOTH)
        self.reverseButton.pack(anchor=SE)

    def refreshQuestions(self):

        with open('template.json', 'r') as template:
            for i in loadJSON(template):
                if i['type'] == 'header' or i['type'] == 'space':
                    continue

                self.questionsListBox.insert(END, i['question'])

    def selectQuestion(self, *args):
        self.reverseButton.destroy()
        question = self.questionsListBox.get(self.questionsListBox.curselection())
        self.reversed = False

        sortedListBox = self.sortedLB
        self.reverseButton = Button(self.questionsFrame, text="Reverse order",
                                    command=lambda: self.reverse(question, sortedListBox))
        self.reverseButton.pack(anchor=SE)

        self.updateSort(question, sortedListBox, reversed=self.reversed)

    def reverse(self, question, listBox):
        self.reversed = not self.reversed
        self.updateSort(question, listBox, reversed=self.reversed)

    def updateSort(self, question, listBox, reversed=False):
        listBox.delete(0, END)

        data = {}
        jsonLabel = ""
        isRdo = False
        with open('template.json') as t:
            template = loadJSON(t)

            for i in template:
                if i["type"] == "header" or i["type"] == "space":
                    continue

                if i['question'] == question:
                    isRdo = i['type'] == 'rdoBtn'
                    jsonLabel = i['jsonLabel']

        for file in listdir(GUI.filedir):
            if file.lower().endswith(".json"):
                with open(GUI.filedir + '\\' + file) as f:
                    fileJson = loadJSON(f)

                for i in fileJson:
                    try:
                        robot = i['robot']
                        toAdd = i[jsonLabel]

                        if isRdo:
                            if toAdd == '':
                                continue

                            toAdd = int(toAdd)

                        if robot in data:
                            data[robot].append(toAdd)
                        else:
                            data[robot] = [toAdd]
                    except KeyError:  # that question isn't in this data
                        continue

        # now we have to do some operations depending on what datatype we're working with
        # get our datatype

        datatype = type(data[list(data.keys())[0]][0])

        newData = {}
        if datatype == int:
            # turn everything into averages
            for team, value in data.items():
                total = 0.0
                for i in value:
                    total += i

                total /= len(value)

                newData[team] = total

        elif datatype == bool:
            # calculate our average (false = 0, true = 1, >=.5 is true)
            for team, value in data.items():
                total = 0.0
                for i in value:
                    total += 1 if i else 0

                total /= len(value)

                newData[team] = total * 100

        sortedData = sorted(newData.items(), key=itemgetter(1), reverse=reversed)

        for i in sortedData:
            listBox.insert(END, i)
