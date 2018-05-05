import json
import socket
from os import path, makedirs
from sys import argv
from threading import Thread
from tkFileDialog import askdirectory

import bluetooth
from enum import Enum
from tkinter import *


# enums
class NetworkingType(Enum):
    hotSpot = "Hotspot"
    BT = "Bluetooth"
    none = "None"


# static vars
port = 4618
uuid = "cb3bd26c-4436-11e8-842f-0ed5f89f718b"

netType = NetworkingType.BT
folder = "files"
verification = "4618 SCOUTING APP"


def main(args=[], gui=False):
    global folder, netType
    if not gui:
        if len(args) < 1:
            args = argv

        for i in NetworkingType:
            if args[1].lower() == i.value:
                netType = i

        if len(args) > 2:
            folder = args[2]

    if not path.isdir(folder):
        makedirs(folder)
    if netType == NetworkingType.none:
        print "No need for a server, just collect the JSON files from the devices at the end of the day."
    elif netType == NetworkingType.hotSpot:
        mainHotSpot()
    else:
        mainBT()


def mainHotSpot():
    print "Creating server socket"

    tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcpSocket.bind(('', port))
    tcpSocket.listen(10)

    while 1:
        print "Waiting for connection..."
        conn, adress = tcpSocket.accept()
        print "Connection recived"
        Thread(target=handleConnection, args=(conn,)).start()


def mainBT():
    print "Creating BT socket"

    btSocket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    btSocket.bind(('', bluetooth.PORT_ANY))
    btSocket.listen(10)

    bluetooth.advertise_service(btSocket, "4618 Scouting Server", service_id=uuid, service_classes=[uuid, bluetooth.
                                SERIAL_PORT_CLASS], profiles=[bluetooth.SERIAL_PORT_PROFILE])

    while 1:
        print "Waiting for connection..."
        conn, info = btSocket.accept()
        print "Connection Recived"
        Thread(target=handleConnection, args=(conn,)).start()


def handleConnection(s):
    # first read: get verification
    # is it necessary? idk
    while 1:
        # read data
        data = s.recv(1024)  # auto converts to a string

        if not data:
            # data is null
            print "Connection closed remotely"
            return

        if data != verification:
            print "Verification unsuccessful, closing"
            s.close()
            return

        print "Verification successful"
        s.send(verification)  # send verification back
        break

    # second read: get the data
    lastRead = ''
    lastReadEquals = False
    while 1:
        # read data
        data = s.recv(1024)

        if data == lastRead:
            if lastReadEquals:
                # safe to assume the connection was closed
                print "Connection closed remotely"
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
            print "Message not JSON formatted: " + data
            continue

        match = str(msgJSON["match"])

        jArray = [msgJSON]
        if path.isfile(folder + "/" + match + ".json"):
            with open(folder + "/" + match + ".json", "r") as f:
                tmp = json.load(f)

                if isinstance(jArray, list):
                    jArray = tmp
                    jArray.append(msgJSON)

        with open(folder + "/" + match + ".json", "wb") as f:
            json.dump(jArray, f, indent=4)

        print "Wrote data to " + match + ".json"


if __name__ == '__main__':
    # this is the file being executed, run our gui
    # setup tk
    root = Tk()  # window
    root.title("Scouting server")

    # all of our output that would normally go on console will go here
    outputScrollBar = Scrollbar(root)
    outputScrollBar.grid(row=0, column=1, rowspan=999, sticky=NS)

    output = Text(root, background="black", foreground="white", yscrollcommand=outputScrollBar.set)
    output.grid(row=0, column=0, rowspan=999)
    outputScrollBar.config(command=output.yview)

    #####

    # Select file and display name
    outputDirFrame = Frame(root, borderwidth=5)
    outputDir = StringVar()
    outputDir.set("No folder selcted")


    def trimFileDir():
        fileDir = askdirectory()  # opens file chooser window
        if len(fileDir) > 25:
            fileDir = "..." + fileDir[-25:]  # last 22 chars of the string
        return fileDir


    choseFileBtn = Button(outputDirFrame, text="Choose folder to save files",
                          command=lambda: outputDir.set(trimFileDir()))
    choseFileBtn.pack()

    Label(outputDirFrame, textvariable=outputDir).pack()

    outputDirFrame.grid(row=0, column=2)

    #####

    # radio buttons for networking mode
    def setNetType(type):
        global netType
        netType = type


    netTypeContainer = Frame(root)
    Label(netTypeContainer, text="Networking Type").pack()
    # can't do these in a for loop because it won't actually change netType
    Radiobutton(netTypeContainer, text=NetworkingType.BT.value, variable=netType, value=NetworkingType.BT,
                indicatoron=0, command=lambda: setNetType(NetworkingType.BT)).pack()  # Bluetooth
    Radiobutton(netTypeContainer, text=NetworkingType.hotSpot.value, variable=netType, value=NetworkingType.hotSpot,
                indicatoron=0, command=lambda: setNetType(NetworkingType.hotSpot)).pack()  # Hotspot
    Radiobutton(netTypeContainer, text=NetworkingType.none.value, variable=netType, value=NetworkingType.none,
                indicatoron=0, command=lambda: setNetType(NetworkingType.none)).pack()  # None

    netTypeContainer.grid(row=0, column=3)

    #####

    # start button
    clicked = False
    def startBtnClick():
        global clicked
        if not clicked:
            Thread(target=main, args=([], True)).start()
            clicked=True
    Button(root, text="Start", command=startBtnClick).grid(row=1, column=2,
        columnspan=2, sticky=EW)

    #####

    # overload stdout (print) to our gui
    class TextRedirector(object):
        def __init__(self, widget, tag="stdout"):
            self.widget = widget
            self.tag = tag

        def write(self, str):
            self.widget.insert(END, str)

    sys.stdout = TextRedirector(output, "stdout")
    sys.stderr = TextRedirector(output, "stderr")
    print  # hangs without this (idk why)

    #####

    root.mainloop()
