#!/usr/bin/python3

import time     
import sys
from weatherLib import logMessage,saveData,\
                       connect_wait_ES,\
                       connect_wait_BT,\
                       openFile
from datetime import datetime
import calendar

#w_address = "00:14:03:06:45:72"

w_address = "00:21:13:02:54:4C"
w_service = "00001101-0000-1000-8000-00805f9b34fb"

sock   = connect_wait_BT(address=w_address, service=w_service)


def getLine():
    line = ""
    onLoop = True
    while onLoop:
        byte = sock.recv(1)                   # Get byte from socket
        if byte == b'\r':                     # Carriage return?
            byte = sock.recv(1)               # Consume LF
            if byte != b'\n':                 # IF not LF, big trouble: discard line
                line = ""
            else:
                onLoop = False;
        else:
            line = line + byte.decode()
    return line


try:
    d = datetime.utcnow()
    timeString = d.strftime("%Y%m%d%H%M%S")
    l = getLine()
    print(l)
    sock.send("TIME "  + timeString + "\r\n")
    l = getLine()
    while l != 'OK-000':
        print(l)
        l = getLine()

    print(l)
    sock.send("BYE  ")
    sock.close()
    sys.exit(0)
    

except KeyboardInterrupt:
    print("Closing socket...")
    logMessage(level="INFO", message="Ending process, closing BT socket.")
    sock.send("BYE  ")
    sock.close()
    sys.exit(0)

except Exception as e:
    msg = "Exception: {0:s}".format(repr(e))
    print(msg)
    logMessage(level="CRIT", message=msg)
    print("Unexpected error, trying to close...")
    sock.send("BYE  ")
    sock.close()
    raise
