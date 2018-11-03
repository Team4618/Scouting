import json
from os.path import isfile
from re import findall as findallRe
from struct import pack as stpack
from threading import Thread
from tkinter import *
from tkinter.ttk import *
from uuid import getnode

import bluetooth
from pyqrcode import create as createQR

import GUI

# static vars
uuid = "cb3bd26c-4436-11e8-842f-0ed5f89f718b"

verification = "4618 SCOUTING APP"

textOutput = None  # this is used to output text. None shouldn't be a problem because its declared in GUI init


class scoutingUI:
    def __init__(self, parent, *args):
        self.page = Frame(parent)
        parent.add(self.page, text="Scouting")

        # all of our output that would normally go on console will go here
        outputScrollBar = Scrollbar(self.page)
        outputScrollBar.grid(row=0, column=1, rowspan=999, sticky=NS)

        self.output = Text(self.page, background="black", foreground="white", yscrollcommand=outputScrollBar.set)
        self.output.grid(row=0, column=0, rowspan=999)
        outputScrollBar.config(command=self.output.yview)

        global textOutput
        textOutput = self.output

        #####

        # get MAC address, which might be BT address (works in 1 test so far)
        # taken from www.geeksforgeeks.org/extracting-mac-address-using-python/, method 3
        adrr = ":".join(findallRe('..', '%012x' % getnode())).encode().upper()

        # create qr code from address
        self.qr = createQR(adrr)

        # setup tkinter image with the qr code
        self.qrBm = BitmapImage(data=self.qr.xbm(scale=5))
        self.qrBm.config(background="white")
        Label(self.page, image=self.qrBm).grid(row=2, column=2)
        Label(self.page, text=adrr).grid(row=3, column=2)

        #####

        # start button
        global clicked
        clicked = False

        self.startButton = Button(self.page, text="Start", command=self.startBtnClick)

        self.startButton.grid(row=1, column=2, columnspan=2, sticky=EW)

        #####

        # textbox to set verification

        self.verificationText = StringVar()
        self.verificationText.set(verification)
        self.verificationText.trace("w", self.setVerification)
        verificationTextBox = Entry(self.page, textvariable=self.verificationText)
        verificationTextBox.grid(row=4, column=2)

    def setVerification(self, *args):
        global verification
        verification = self.verificationText.get()

    def startBtnClick(self):
        global clicked
        if not clicked:
            Thread(target=startBT).start()
            clicked = True
            self.startButton.grid_remove()


def printtoGUI(obj):
    textOutput.insert(END, obj + '\n')


def startBT():
    global socket

    printtoGUI("Creating BT socket")

    socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    socket.bind(('', bluetooth.PORT_ANY))
    socket.listen(10)  # will accept max 10 connections at a time

    # tell other devices about our service, providing UUID and specifying a serial connection
    bluetooth.advertise_service(socket, "4618 Scouting Server", service_id=uuid, service_classes=[uuid, bluetooth.
                                SERIAL_PORT_CLASS], profiles=[bluetooth.SERIAL_PORT_PROFILE])

    while 1:
        printtoGUI("Waiting for connection...")
        conn = socket.accept()[0]
        printtoGUI("Connection received")
        Thread(target=handleConnection, args=(conn,)).start()

    socket.close()


def handleConnection(s):
    # first read: get verification
    # is it necessary? idk
    while 1:
        # read data
        data = s.recv(1024)

        if not data:
            # data is null
            printtoGUI("Connection closed remotely")
            s.close()
            return

        if data.decode("utf-8") != verification:
            printtoGUI("Verification unsuccessful, closing")
            s.close()
            return

        printtoGUI("Verification successful")
        s.send(verification)  # send verification back
        break

    # load template to send later
    with open("template.json", "r") as f:
        template = json.load(f)  # load as json to get rid of whitespace and make message smaller

    templateStr = json.dumps(template)

    sucess = False
    while not sucess:  # loop until client recives template
        printtoGUI("sending template")
        # send template with questions in it
        s.send(stpack("!i", len(templateStr)))  # send length of message
        # sleep(1)  # prevents tcp from merging the length of the message with the actual message
        s.send(templateStr)

        # read 1.5: get verification
        while 1:
            # read data
            data = s.recv(1)  # auto converts to a string

            if not data:
                # data is null
                printtoGUI("Connection closed remotely")
                s.close()
                return

            if data == 'Y':
                print(data)
                sucess = True
                break
            elif data == 'N':
                sucess = False
                break

    printtoGUI("sent")
    # second read: get the data
    lastRead = ''
    lastReadEquals = False
    while 1:
        # read data
        data = s.recv(1024)

        if data == lastRead:
            if lastReadEquals:
                # safe to assume the connection was closed
                printtoGUI("Connection closed remotely")
                s.close()
                return

            lastReadEquals = True
            lastRead = data
            # no need to process identical data
            continue

        lastRead = data

        if not data:
            # probably all null, ignore it
            continue

        try:
            msgJSON = json.loads(data)
        except ValueError:
            printtoGUI("Message not JSON formatted: " + data)
            continue

        match = str(msgJSON["match"])

        # check if the json file for that match already exists, and if it doesn't, make it
        jArray = [msgJSON]
        if isfile(GUI.filedir + "/" + match + ".json"):
            with open(GUI.filedir + "/" + match + ".json", "r") as f:
                tmp = json.load(f)

                if isinstance(jArray, list):
                    jArray = tmp
                    jArray.append(msgJSON)

        with open(GUI.filedir + "/" + match + ".json", "wb") as f:
            json.dump(jArray, f, indent=4)

        printtoGUI("Wrote data to " + match + ".json")
