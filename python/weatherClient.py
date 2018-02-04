#!/usr/bin/python3

import time     
import sys
from weatherLib import connectES,logMessage,saveData,connectBT
from elasticsearch import ConnectionTimeout

def connect_wait_ES():
    while True:
        try:
            connected,esConn,hostIdx = connectES(hosts=es_hosts)
            if connected:
                print("Connected to ES host: ", es_hosts[hostIdx])
                break
            else:
                logMessage(message="Connection try failed", level="ERROR")
                print("Coulnd not connect to ES, retryng...")
        except:
            msg = "Unexpected exception trying to connect to ES: %s" % sys.exc_info()[0]
            logMessage(level="CRIT",message=msg)
            print(msg)
            sys.exit(16)
    return esConn


def connect_wait_BT():
    while True:
        connected, sock, name = connectBT(addr=w_address, serv=w_service)
        if connected:
            print("Connected to weather service at \"%s\" on %s" % (name,w_address))
            return sock
            break



es_hosts  = [ 'elastic00.jguillaumes.dyndns.org',\
              'elastic01.jguillaumes.dyndns.org',\
              'elastic02.jguillaumes.dyndns.org']
w_address = "00:14:03:06:45:72"
w_service = "00001101-0000-1000-8000-00805f9b34fb"
file = "weather.dat"

sock   = connect_wait_BT()
esConn = connect_wait_ES()

f = open(file, 'w')

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
                    except ConnectionTimeout:
                        print("Error sending to ES: ", sys.exc_info()[0])
                        print("Datapoint lost: ", line)
                        pass
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
    sock.send("BYE ")
    sock.close()

except:
    print("Exception: ", sys.exc_info()[0])
    print("Unexpected error, trying to close...")
    sock.send("BYE ")
    sock.close()
    raise
