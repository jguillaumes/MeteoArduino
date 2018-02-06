#!/usr/bin/python3

import time     
import sys
from weatherLib import connectES,logMessage,saveData,connectBT
from elasticsearch import ConnectionTimeout
from datetime import datetime

def connect_wait_ES():
    while True:
        try:
            connected,esConn,hostIdx = connectES(hosts=es_hosts)
            if connected:
                print("Connected to ES host: ", es_hosts[hostIdx])
                break
            else:
                logMessage(message="Connection try failed", level="ERR")
                print("Coulnd not connect to ES, retryng...")
        except:
            msg = "Unexpected exception trying to connect to ES: %s" % sys.exc_info()[0]
            logMessage(level="CRIT",message=msg)
            print(msg)
            sys.exit(16)
    return esConn


def connect_wait_BT():
    phase=0
    retries=0
    retrChangePhase=10
    delays=[5,60]
    while True:
        connected, sock, name = connectBT(addr=w_address, serv=w_service)
        if connected:
            print("Connected to weather service at \"%s\" on %s" % (name,w_address))
            return sock
            break
        else:
            if phase == 0:
                time.sleep(delays[0])
                retrChangePhase -= 1
                if retrChangePhase <= 0:
                    phase = 1
                    msg = 'Switching to {0:d} seconds delay.'.format(delays[1])
                    print(msg)
                    logMessage(level="INFO",message=msg)
                else:
                    pass
            else:
                time.sleep(delays[1])

def openFile():
    filename = "weather-" + datetime.utcnow().strftime("%Y.%m.%d") + ".dat"
    file = open(filename, 'a')
    return file

es_hosts  = [ 'elastic00.jguillaumes.dyndns.org',\
              'elastic01.jguillaumes.dyndns.org',\
              'elastic02.jguillaumes.dyndns.org']
w_address = "00:14:03:06:45:72"
w_service = "00001101-0000-1000-8000-00805f9b34fb"



sock   = connect_wait_BT()
esConn = connect_wait_ES()
f      = openFile()

try:
    print("Start weather processing...")
    logMessage(message="Start weather processing.", level="INFO")    
    line = ""
    while True:
        byte = sock.recv(1)                   # Get byte from socket
        if byte == b'\r':                     # Carriage return?
            byte = sock.recv(1)               # Consume LF
            if byte != b'\n':                 # IF not LF, big trouble: discard line
                line = ""
            else:                             # We've got a good line.
                if line[0:4] == "DATA":       # It is a data line so...
                    f.write(line+'\n')        # ... write it!
                    f.flush()                 # Don't wait, write now!
                    try:
                        saveData(esConn,line) # Send to ES cluster
                    except ConnectionTimeout as ect:
                        print("Error sending to ES: ", sys.exc_info()[0])
                        print("Datapoint lost: ", line)
                        logMessage(level="ERR", message="Error sending to ES: {0:s}".format(repr(ect)))
                else:
                    print("Non-data line: " + line)
                    if line[0:2] == "AT":     # First characters got after connection
                        now = time.gmtime()   # So send current time to set RTC...
                        cmd = "TIME " + time.strftime("%Y%m%d%H%M%S",now) + "\r"
                        print("Setting time, command: " + cmd)
                        sock.send(cmd)
                line = ""                     # Clear line to get next one
        else:
            line = line + byte.decode()       # Add character to current working line

except KeyboardInterrupt:
    print("Closing socket...")
    logMessage(level="INFO", message="Ending process, closing BT socket.")
    sock.send("BYE ")
    sock.close()
    sys.exit(0)

except Exception as e:
    msg = "Exception: {0:s}".format(repr(e))
    print(msg)
    logMessage(level="CRIT", message=msg)
    print("Unexpected error, trying to close...")
    sock.send("BYE ")
    sock.close()
    raise
