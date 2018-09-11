#!/usr/bin/python3

import time     
import sys
from weatherLib import logMessage,saveData,\
                       connect_wait_ES,\
                       connect_wait_BT,\
                       openFile,\
                       getLine
from elasticsearch import ConnectionTimeout


#es_hosts  = [ 'elastic00.jguillaumes.dyndns.org',\
#              'elastic01.jguillaumes.dyndns.org',\
#              'elastic02.jguillaumes.dyndns.org']
# es_hosts = [ 'macjordi.jguillaumes.dyndns.org' ]
es_hosts = ['127.0.0.1']
# w_address = "00:14:03:06:45:72"
# w_address = "00:21:13:02:54:4C"

w_address ='00:21:13:02:63:B7'
w_service = '00001101-0000-1000-8000-00805f9b34fb'

sock   = connect_wait_BT(address=w_address, service=w_service)
esConn = connect_wait_ES(hostlist=es_hosts)

if not esConn:
    logMessage(level="ERR", message="ES not available, exiting")
    sock.send('BYE   ')
    sock.close()
    sys.exit(8)

f  = openFile()

try:
    print("Start weather processing...")
    logMessage(message="Start weather processing.", level="INFO")    
    while True:
        line = getLine(sock)
        cmd = line[0:5]
        if cmd == "DATA ":             # It is a data line so...
            f.write(line+'\n')        # ... write it!
            f.flush()                 # Don't wait, write now!
            try:
                saveData(esConn,line) # Send to ES cluster
            except ConnectionTimeout as ect:
                print("Error sending to ES: ", sys.exc_info()[0])
                print("Datapoint lost: ", line)
                logMessage(level="ERR",  message="Error sending to ES: {0:s}".format(repr(ect)))
                logMessage(level="INFO", message="Trying to switch ES connection")
                esConn = connect_wait_ES(hostlist=es_hosts)   # Try to connect again
        else:
            print("Non-data line: " + line)
            if cmd == "BEGIN":     # First characters got after connection
                now = time.gmtime()   # So send current time to set RTC...
                timcmd = "TIME " + time.strftime("%Y%m%d%H%M%S",now) + "\r"
                logMesssage(level="INFO", message="Setting time, command: {0:s}".format(timcmd))
                sock.send(timcmd)
            elif cmd == "ERROR":
                logMessage(level="ERR", message="Error in firmware/hardware: {0:s}".format(line))
                
        line = ""                     # Clear line to get next one

except KeyboardInterrupt:
    print("Closing socket...")
    logMessage(level="INFO", message="Ending process, closing BT socket.")
    sock.send(b'BYE  ')
    sock.close()
    sys.exit(0)

except Exception as e:
    msg = "Exception: {0:s}".format(repr(e))
    print(msg)
    logMessage(level="CRIT", message=msg)
    print("Unexpected error, trying to close...")
    sock.send(b'BYE  ')
    sock.close()
    raise
