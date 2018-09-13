#!/usr/bin/python3

import time     
import sys
import configparser
                       
from weatherLib.weatherQueue import WeatherQueue
from weatherLib.weatherBT import WeatherBT
from weatherLib.weatherUtil import WLogger,openFile,parseLine
from weatherLib.weatherDB import WeatherDB
from weatherLib.weatherDoc import WeatherData


logger = WLogger()

config = configparser.ConfigParser()
cf = config.read(['/etc/weartherClient.ini','/usr/local/etc/weatherClient.ini','weatherClient.ini'])
logger.logMessage(level="INFO",message="Configuration loaded from configuration files [{l}]".format(l=cf))

w_address = config['bluetooth']['address']
w_service = config['bluetooth']['service']

pg_host     = config['postgres']['host']
pg_user     = config['postgres']['user']
pg_password = config['postgres']['password']
pg_database = config['postgres']['database']

es_hosts = eval(config['elastic']['hosts'])

wQueue = WeatherQueue()
wdb = WeatherDB(pg_host,pg_user,pg_password,pg_database)

blue = WeatherBT.connect_wait(address=w_address, service=w_service)


try:
    #esConn = connect_wait_ES(hostlist=es_hosts)

    #if not esConn:
    #    sock.send('BYE   ')
    #    sock.close()
    #    sys.exit

    f  = openFile()
    tsa = 1

    logger.logMessage(message="Start weather processing.", level="INFO")    
    while True:
        line = blue.getLine()
        cmd = line[0:5]
        if cmd == "DATA ":             # It is a data line so...
            f.write(line+'\n')        # ... write it!
            f.flush()                 # Don't wait, write now!
            wQueue.pushLine(line)
            stamp,temp,humt,pres,lght,firmware,clock,thermometer,hygrometer,barometer = parseLine(line)
            
            doc = WeatherData()
            doc.init(_tsa=tsa, _time=stamp, _temperature=temp, _humidity=humt, _pressure=pres, _light=lght,
                     _fwVersion=firmware, _isBarometer=barometer, _isClock=clock,
                     _isThermometer=thermometer, _isHygrometer=hygrometer)
            logger.logMessage(level="DEBUG",message=doc.to_dict())
            wdb.insertObs(doc)
            tsa += 1
            #try:
            #    saveData(esConn,line) # Send to ES cluster
            #except ConnectionTimeout as ect:
            #    logException(message="Error sending to ES")
            #    logMessage(level="WARNING",message="Datapoint lost: {0:s}".format(line))
            #    logMessage(level="INFO", message="Trying to switch ES connection")
            #    esConn = connect_wait_ES(hostlist=es_hosts)   # Try to connect again
        elif cmd == "INFO:":
            logger.logMessage(level="INFO", message=line)
        elif cmd == "ERROR":
            logger.logMessage(level="WARNING", message="Error in firmware/hardware: {0:s}".format(line))      
        elif cmd == "HARDW":
            logger.logMessage(level="CRITICAL",message=line)
        elif cmd == "BEGIN":
            now = time.gmtime()   # So send current time to set RTC...
            timcmd = "TIME " + time.strftime("%Y%m%d%H%M%S",now) + "\r"
            logger.logMessage(level="INFO", message="Setting time, command: {0:s}".format(timcmd))
            blue.send(timcmd)
            blue.waitAnswer("OK-000")
        else:
            logger.logMessage(level="WARNING",message="Non-processable line: {0:s}".format(line))
                
except KeyboardInterrupt:
    logger.logMessage(level="INFO", message="Ending process, closing BT socket.")
    blue.send(b'BYE  ')

    blue.waitAnswer("OK-BYE")
    blue.close()
    sys.exit

except Exception as e:
    logger.logException(message="Unexpected exception caught")
    logger.logMessage(level="CRITICAL",message="Unexpected error, trying to close...")
    blue.send(b'BYE  ')
    blue.close()
    raise
