import json
from os import path, makedirs
from re import findall as findallRe
from struct import pack as stpack
from sys import argv
from threading import Thread
from tkFileDialog import askdirectory
from uuid import getnode

import bluetooth
from pyqrcode import create as createQR
from Tkinter import *
from ttk import *


# static vars
uuid = "cb3bd26c-4436-11e8-842f-0ed5f89f718b"

folder = "files"
verification = "4618 SCOUTING APP"


def main(args=[], gui=False):
    global folder, netType
    if not gui:  # we're not running our gui, probably being called from a different file

        if len(args) < 1:  # probably running from command line, we should use argv
            args = argv

        if len(args) > 1:  # grab the directory where we're going to save our files
            folder = args[1]

    if not path.isdir(folder):
        makedirs(folder)

    startBT()


def startBT():
    global socket
    print "Creating BT socket"

    socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    socket.bind(('', bluetooth.PORT_ANY))

    socket.listen(10)  # will accept max 10 connections at a time

    # tell other devices about our service, providing UUID and specifying a serial connection
    bluetooth.advertise_service(socket, "4618 Scouting Server", service_id=uuid, service_classes=[uuid, bluetooth.
                                SERIAL_PORT_CLASS], profiles=[bluetooth.SERIAL_PORT_PROFILE])

    while 1:
        print "Waiting for connection..."
        conn = socket.accept()[0]
        print "Connection received"
        Thread(target=handleConnection, args=(conn,)).start()

    btSocket.close()


def handleConnection(s):
    # first read: get verification
    # is it necessary? idk
    while 1:
        # read data
        data = s.recv(1024)  # auto converts to a string

        if not data:
            # data is null
            print "Connection closed remotely"
            s.close()
            return

        if data != verification:
            print "Verification unsuccessful, closing"
            s.close()
            return

        print "Verification successful"
        s.send(verification)  # send verification back
        break

    # load template to send later
    with open("template.json", "r") as f:
        template = json.load(f)  # load as json to get rid of whitespace and make message smaller

    templateStr = json.dumps(template)

    sucess = False
    while not sucess:  # loop until client recives template
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
                print "Connection closed remotely"
                s.close()
                return

            if data == 'Y':
                sucess = True
                break
            elif data == 'N':
                sucess = False
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
            print "Message not JSON formatted: " + data
            continue

        match = str(msgJSON["match"])

        # check if the json file for that match already exists, and if it doesn't, make it
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
        global folder
        fileDir = askdirectory()  # opens file chooser window
        folder = fileDir
        if len(fileDir) > 20:
            fileDir = "..." + fileDir[-17:]  # last 17 chars of the string
        return fileDir


    choseFileBtn = Button(outputDirFrame, text="Choose folder to save files",
                          command=lambda: outputDir.set(trimFileDir()))
    choseFileBtn.pack()

    Label(outputDirFrame, textvariable=outputDir).pack()

    outputDirFrame.grid(row=0, column=2)

    #####

    # get MAC address, which might be BT address (works in 1 test so far)
    # taken from www.geeksforgeeks.org/extracting-mac-address-using-python/, method 3
    adrr = ":".join(findallRe('..', '%012x' % getnode())).upper()

    # create qr code from address
    qr = createQR(adrr)

    # setup tkinter image with the qr code
    qrBm = BitmapImage(data=qr.xbm(scale=5))
    qrBm.config(background="white")
    Label(root, image=qrBm).grid(row=2, column=2)

    #####

    # start button
    clicked = False


    def startBtnClick():
        global clicked
        if not clicked:
            Thread(target=main, args=([], True)).start()
            clicked = True
            startButton.grid_remove()


    startButton = Button(root, text="Start", command=startBtnClick)

    startButton.grid(row=1, column=2, columnspan=2, sticky=EW)

    #####

    # textbox to set verification
    def setVerification(*args):
        global verification
        verification = verificationText.get()


    verificationText = StringVar()
    verificationText.set(verification)
    verificationText.trace("w", setVerification)
    verificationTextBox = Entry(root, textvariable=verificationText)
    verificationTextBox.grid(row=3, column=2)

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

    #####

    root.mainloop()

    socket.close()
