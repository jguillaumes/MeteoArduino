#!/usr/bin/python3

import time     
import sys
import configparser

from weatherLib import logMessage,logException,setupLog,\
                       saveData,\
                       connect_wait_ES,\
                       openFile
                       
from weatherLib.weatherQueue import WeatherQueue
from weatherLib.weatherBT import WeatherBT

from elasticsearch import ConnectionTimeout

logger = setupLog()

config = configparser.ConfigParser()
cf = config.read(['/etc/weartherClient.ini','/usr/local/etc/weatherClient.ini','weatherClient.ini'])
logMessage(level="INFO",message="Configuration loaded from configuration files [{l}]".format(l=cf))

w_address = config['bluetooth']['address']
w_service = config['bluetooth']['service']
es_hosts = eval(config['elastic']['hosts'])

wQueue = WeatherQueue()
bt = WeatherBT.connect_wait(address=w_address, service=w_service)


try:
    #esConn = connect_wait_ES(hostlist=es_hosts)

    #if not esConn:
    #    sock.send('BYE   ')
    #    sock.close()
    #    sys.exit

    f  = openFile()

    logMessage(message="Start weather processing.", level="INFO")    
    while True:
        line = bt.getLine()
        cmd = line[0:5]
        if cmd == "DATA ":             # It is a data line so...
            f.write(line+'\n')        # ... write it!
            f.flush()                 # Don't wait, write now!
            wQueue.pushLine(line)
            #try:
            #    saveData(esConn,line) # Send to ES cluster
            #except ConnectionTimeout as ect:
            #    logException(message="Error sending to ES")
            #    logMessage(level="WARNING",message="Datapoint lost: {0:s}".format(line))
            #    logMessage(level="INFO", message="Trying to switch ES connection")
            #    esConn = connect_wait_ES(hostlist=es_hosts)   # Try to connect again
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
            bt.send(timcmd)
            bt.waitAnswer("OK-000")
        else:
            logMessage(level="WARNING",message="Non-processable line: {0:s}".format(line))
                
except KeyboardInterrupt:
    logMessage(level="INFO", message="Ending process, closing BT socket.")
    bt.send(b'BYE  ')
    bt.waitAnswer("OK-BYE")
    bt.close()
    sys.exit

except Exception as e:
    logException(message="Unexpected exception caught")
    logMessage(level="CRITICAL",message="Unexpected error, trying to close...")
    bt.send(b'BYE  ')
    bt.close()
    raise
