#!/usr/bin/python3

import time     
import sys
import configparser
                       
from weatherLib.weatherQueue import WeatherQueue
from weatherLib.weatherBT import WeatherBT
from weatherLib.weatherUtil import WLogger,openFile
from weatherLib.weatherDB import WeatherDB,WeatherDBThread
from weatherLib.weatherES import WeatherES,WeatherESThread

dbThread = None

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
pg_retry    = config['postgres']['retryDelay']

es_hosts = eval(config['elastic']['hosts'])

wQueue = WeatherQueue()
wdb = WeatherDB(pg_host,pg_user,pg_password,pg_database,pg_retry)
dbThread = WeatherDBThread(wQueue,wdb)

wes = WeatherES(es_hosts)
esThread = WeatherESThread(wQueue,wes)

blue = WeatherBT.connect_wait(address=w_address, service=w_service)
dbThread.start()
esThread.start()


try:

    f  = openFile()

    logger.logMessage(message="Start weather processing.", level="INFO")    
    while True:
        line = blue.getLine()
        cmd = line[0:5]
        if cmd == "DATA ":             # It is a data line so...
            f.write(line+'\n')        # ... write it!
            f.flush()                 # Don't wait, write now!
            wQueue.pushLine(line)
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
    if dbThread is not None:
        if dbThread.is_alive():
            dbThread._stop()
    if esThread is not None:
        if esThread.is_alive():
            esThread._stop();
    sys.exit

except Exception as e:
    logger.logException(message="Unexpected exception caught")
    logger.logMessage(level="CRITICAL",message="Unexpected error, trying to close...")
    blue.send(b'BYE  ')
    blue.close()
    raise
