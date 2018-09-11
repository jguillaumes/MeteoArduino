#!/usr/bin/python3

import time     
import sys
from weatherLib import logMessage,logException,setupLog,\
                       saveData,\
                       connect_wait_ES,\
                       connect_wait_BT,\
                       openFile,\
                       getLine
from elasticsearch import ConnectionTimeout

logger = setupLog()

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
    sock.send('BYE   ')
    sock.close()
    sys.exit

f  = openFile()

try:
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
                logException(message="Error sending to ES")
                logMessage(level="WARNING",message="Datapoint lost: {0:s}".format(line))
                logMessage(level="INFO", message="Trying to switch ES connection")
                esConn = connect_wait_ES(hostlist=es_hosts)   # Try to connect again
        else:
            logMessage(level="WARNING",message="Non-data line: {0:s}".format(line))
            if cmd == "BEGIN":     # First characters got after connection
                now = time.gmtime()   # So send current time to set RTC...
                timcmd = "TIME " + time.strftime("%Y%m%d%H%M%S",now) + "\r"
                logMessage(level="INFO", message="Setting time, command: {0:s}".format(timcmd))
                sock.send(timcmd)
            elif cmd == "ERROR":
                logMessage(level="CRITICAL", message="Error in firmware/hardware: {0:s}".format(line))
                
        line = ""                     # Clear line to get next one

except KeyboardInterrupt:
    logMessage(level="INFO", message="Ending process, closing BT socket.")
    sock.send(b'BYE  ')
    sock.close()
    sys.exit

except Exception as e:
    logException(message="Unexpected exception caught")
    logMessage(level="CRITICAL",message="Unexpected error, trying to close...")
    sock.send(b'BYE  ')
    sock.close()
    raise
