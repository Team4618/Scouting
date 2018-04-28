import json
import socket
from os import path, makedirs
from sys import argv
from thread import start_new_thread

import bluetooth
from enum import Enum


# enums
class NetworkingType(Enum):
    hotSpot = 0
    BT = 1
    none = 2


# static vars
port = 4618
uuid = "cb3bd26c-4436-11e8-842f-0ed5f89f718b"

netType = NetworkingType.BT
folder = "files"
verification = "4618 SCOUTING APP"


def main():
    global folder, netType
    if len(argv) > 1:
        if argv[1].lower == "hotspot":
            netType = NetworkingType.hotSpot
        elif argv[1].lower == "bt" or argv[1].lower == "bluetooth":
            netType = NetworkingType.BT
        elif argv[1].lower == "none":
            netType = NetworkingType.none

    if len(argv) > 2:
        folder = argv[2]

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
        start_new_thread(handleConnection, (conn,))


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
        start_new_thread(handleConnection, (conn,))


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
    main()
