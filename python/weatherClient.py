#!/usr/bin/python3

import time     
import sys
import configparser

from weatherLib import logMessage,logException,setupLog,\
                       saveData,\
                       connect_wait_ES,\
                       connect_wait_BT,\
                       openFile,\
                       getLine, waitAnswer

from elasticsearch import ConnectionTimeout

logger = setupLog()

config = configparser.ConfigParser()
cf = config.read(['/etc/weartherClient.ini','/usr/local/etc/weatherClient.ini','weatherClient.ini'])
logMessage(level="INFO",message="Configuration loaded from configuration files [{l}]".format(l=cf))

w_address = config['bluetooth']['address']
w_service = config['bluetooth']['service']
es_hosts = eval(config['elastic']['hosts'])

sock   = connect_wait_BT(address=w_address, service=w_service)

try:
    esConn = connect_wait_ES(hostlist=es_hosts)

    if not esConn:
        sock.send('BYE   ')
        sock.close()
        sys.exit

    f  = openFile()

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
        elif cmd == "INFO:":
            logMessage(level="INFO", message=line)
        elif cmd == "ERROR":
            logMessage(level="WARNING", message="Error in firmware/hardware: {0:s}".format(line))      
        elif cmd == "HARDW":
            logMessage(level="CRITICAL",message=line)
        elif cmd == "BEGIN":
            now = time.gmtime()   # So send current time to set RTC...
            timcmd = "TIME " + time.strftime("%Y%m%d%H%M%S",now) + "\r"
            logMessage(level="INFO", message="Setting time, command: {0:s}".format(timcmd))
            sock.send(timcmd)
            waitAnswer(sock,"OK-000")
        else:
            logMessage(level="WARNING",message="Non-processable line: {0:s}".format(line))
                
except KeyboardInterrupt:
    logMessage(level="INFO", message="Ending process, closing BT socket.")
    sock.send(b'BYE  ')
    waitAnswer(sock, "OK-BYE")
    sock.close()
    sys.exit

except Exception as e:
    logException(message="Unexpected exception caught")
    logMessage(level="CRITICAL",message="Unexpected error, trying to close...")
    sock.send(b'BYE  ')
    sock.close()
    raise
