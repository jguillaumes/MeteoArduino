#!/usr/bin/python3

import time     
import sys
import configparser
import threading
import os.path

script_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(script_path)
                       
from weatherLib.weatherQueue import WeatherQueue,QueueJanitorThread
from weatherLib.weatherBT import WeatherBT
from weatherLib.weatherUtil import WLogger,openFile,WatchdogThread
from weatherLib.weatherDB import WeatherDB,WeatherDBThread
from weatherLib.weatherES import WeatherES,WeatherESThread

dbThread = None
esThread = None
janitorThread = None
watchdogThread = None

logger = WLogger()
dataEvent = threading.Event()
dataEvent.clear()

config = configparser.ConfigParser()
cf = config.read(['/etc/weartherClient.ini','/usr/local/etc/weatherClient.ini','weatherClient.ini'])
logger.logMessage(level="INFO",message="Configuration loaded from configuration files [{l}]".format(l=cf))


data_dir  = config['data']['directory']

w_address = config['bluetooth']['address']
w_service = config['bluetooth']['service']

pg_host     = config['postgres']['host']
pg_user     = config['postgres']['user']
pg_password = config['postgres']['password']
pg_database = config['postgres']['database']
pg_retry    = int(config['postgres']['retryDelay'])

es_hosts = eval(config['elastic']['hosts'])

janitor_period  = int(config['janitor']['period'])
watchdog_period = int(config['watchdog']['period'])

wQueue = WeatherQueue(data_dir)
wdb = WeatherDB(pg_host,pg_user,pg_password,pg_database)
dbThread = WeatherDBThread(wQueue,wdb,dataEvent,pg_retry)

wes = WeatherES(es_hosts)
esThread = WeatherESThread(wQueue,wes,dataEvent)

janitorThread = QueueJanitorThread(wQueue,period=janitor_period)

threadList = [esThread, dbThread, janitorThread ]
watchdogThread = WatchdogThread(threadList,period=watchdog_period)

blue = WeatherBT.connect_wait(address=w_address, service=w_service)
dbThread.start()
esThread.start()
janitorThread.start()
watchdogThread.start()

try:

    f  = openFile(data_dir)

    logger.logMessage(message="Start weather processing.", level="INFO")    
    while True:
        line = blue.getLine()
        cmd = line[0:5]
        if cmd == "DATA ":              # It is a data line so...
            f.write(line+'\n')          # ... write it!
            f.flush()                   # Don't wait, write now!
            wQueue.pushLine(line)
            dataEvent.set()             # Send event: data received
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

    if watchdogThread is not None:
        watchdogThread.stop()
    if dbThread is not None:
        dbThread.stop()
    if esThread is not None:
        esThread.stop()
    if janitorThread is not None:
        janitorThread.stop()
    dataEvent.set()             # Awake threads so they can finish
    sys.exit()

except Exception as e:
    logger.logException(message="Unexpected exception caught")
    logger.logMessage(level="CRITICAL",message="Unexpected error, trying to close...")
    if watchdogThread is not None:
        watchdogThread.stop()
    if dbThread is not None:
        dbThread.stop()
    if esThread is not None:
        esThread.stop()
    if janitorThread is not None:
        janitorThread.stop()
    dataEvent.set()             # Awake threads so they can finish
    blue.send(b'BYE  ')
    blue.close()
    raise
