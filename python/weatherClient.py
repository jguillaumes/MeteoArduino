#!/usr/bin/python3

import time     
import sys
import configparser
import threading
import os.path

script_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(script_path)
                       
from weatherLib.weatherQueue import WeatherQueue,QueueJanitorThread
from weatherLib.weatherBT import WeatherBTThread
from weatherLib.weatherUtil import WLogger
from weatherLib.weatherDB import WeatherDB,WeatherDBThread
from weatherLib.weatherES import WeatherES,WeatherESThread
from weatherLib.watchdog import WatchdogThread

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

btThread = WeatherBTThread(address = w_address,
                           service = w_service,
                           queue   = wQueue,
                           event   = dataEvent,
                           directory = data_dir)

threadList = [btThread, esThread, dbThread, janitorThread]
watchdogThread = WatchdogThread(threadList,period=watchdog_period)

dbThread.start()
esThread.start()
btThread.start()
janitorThread.start()
watchdogThread.start()

try:
    while True:
        logger.logMessage("Timestamp")
        time.sleep(60)
                
except KeyboardInterrupt:
    logger.logMessage(level="INFO", message="Ending process, stopping worker threads.")

    watchdogThread.stop()
    for t in threadList:
        if t is not None:
            t.stop()
            dataEvent.set()
    for t in threadList:
        if t is not None:
            t.join()
    watchdogThread.join()
    logger.logMessage("Process ended, all threads stopped")
    exit

except Exception as e:
    logger.logException(message="Unexpected exception caught")
    logger.logMessage(level="CRITICAL",message="Unexpected error, trying to close...")
    watchdogThread.stop()
    for t in threadList:
        if t is not None:
            t.stop()
            dataEvent.set()
    for t in threadList:
        if t is not None:
            t.join()
    watchdogThread.join()
    raise
