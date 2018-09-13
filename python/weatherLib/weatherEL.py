import sys
import random

import time as tm
from datetime import datetime
from elasticsearch import client
from elasticsearch_dsl import connections,DocType,Date,Float,Long,Search,Text,Boolean
from elasticsearch import ConnectionError,TransportError
from urllib3.exceptions import NewConnectionError

from weatherLib.constants import VERSION,SW_VERSION
from weatherLib.weatherUtil import WLogger,parseLine


def connectES(hosts,maxRetries=6):
    """
    Connect to elasticsearch. Do a round-robbin among the hosts in the
    'hosts' array with a maximum if maxRetries attempts
    Parameters:
        - Hosts: array of hostnames (strings)
        - maxRetries: Maximum number of attempts
    """
    numHosts = len(hosts)
    retries = 0
    connected = False
    random.seed()
    hostIdx = random.randint(0,numHosts-1)
    while (connected == False) and (retries < maxRetries):
        try:
            esConn = connections.create_connection(hosts=hosts[hostIdx],timeout=10)
            WeatherData.create_template(conn=esConn)
            WeatherData.init(index=WeatherData._indexname)
            connected = True
        except (ConnectionError, NewConnectionError, TransportError):
            msg = "Host %s not available." % hosts[hostIdx]
            logException(message=msg)
            hostIdx += 1
            retries += 1
            if hostIdx >= numHosts:
                hostIdx = 0
        except:
            logException("Unexpected exception, please fix.")
            raise
    if connected:
        return True,esConn,hostIdx
    else:
        return False,0,-1

def getTopTSA(tsaDay):
    """
    Get the top transaction serial identifier (tsa) for a certain day
    Parameters:
        - day: day (datetime) to search for
    Returns:
        - Top tsa for day 
    """
    tsaBegin = tsaDay.year * 10000 + tsaDay.month * 100 + tsaDay.day
    tsaBegin = tsaBegin * 1000000
    tsaEnd   = tsaBegin + 999999
    s = Search().query("range", tsa= { "gte":tsaBegin ,"lt": tsaEnd}).params(size=0)
    s.aggs.metric('top_tsa', 'max', field='tsa')
    #print (s.to_dict())  
    r = s.execute()
    toptsa = r.aggregations.top_tsa.value
    if toptsa == None:
        return 0
    else:
        return int(toptsa % 1000000)
    
def connect_wait_ES(hostlist):
    phase=0
    retrChangePhase=10
    delays=[5,30]
    while True:
        try:
            connected,esConn,hostIdx = connectES(hosts=hostlist)
            if connected:
                logMessage(level="INFO",message="Connected to ES host: {0:s}".format(hostlist[hostIdx]))
                break
            else:
                logMessage(message="Connection try failed", level="ERROR")
                logMessage(message="Could not connect to ES, retryng...",level="WARNING")
                if phase == 0:
                    tm.sleep(delays[0])
                    retrChangePhase -= 1
                    if retrChangePhase <= 0:
                        phase = 1
                        msg = 'Switching to {0:d} seconds delay.'.format(delays[1])
                        logMessage(level="INFO",message=msg)
                    else:
                        pass
                else:
                    tm.sleep(delays[1])       
        except KeyboardInterrupt:
            logMessage(level="INFO", message="Interrupted by CTRL/C")
            raise
        except:
            msg = "Unexpected exception trying to connect to ES: %s" % sys.exc_info()[0]
            logMessage(level="CRITICAL",message=msg)
    return esConn
def saveData(conn, line):
    """
    Send a line of data to ES
    Parameters:
        - conn: ES connection
        - line: Line of data (DATA:C...) from the BT device
    """
    stamp, temp, humt, pres, lght, firm, clock, therm, hygro, baro = parseLine(line)
    w = WeatherData()
    w.time = stamp
    w.temperature = temp
    w.humidity = humt
    w.pressure = pres
    w.light = lght
    w.version = VERSION
    w.fwVersion = firm
    w.swVersion = SW_VERSION
    w.isClock = clock
    w.isThermometer = therm
    w.isHygrometer = hygro
    w.isBarometer = baro
    w.save()       


    def save(self, tsa, ** kwargs):
        """
        Save a weather observation
        """
        day = self.time.strftime("%Y.%m.%d")        # Check observation date
        nday = int(self.time.strftime("%Y%m%d"))
        if day != WeatherData._curDay:              # Date changed?
            WeatherData._curDay = day               # Yes, change index name
            WeatherData._indexname = 'weather-' + VERSION + '-' + day
            WeatherData._lastToday = getTopTSA(self.time)
            self._logger.logMessage(level="INFO",\
                                    message="Starting at tsa {0:d} for {1:d}"\
                                        .format(WeatherData._lastToday, nday))
        # Compute the tsa for the new document and increment serial number
        self.tsa = nday * 1000000 + WeatherData._lastToday + 1
        # self._id = self._curDay + "-" + "{0:06d}".format(WeatherData._lastToday)
        WeatherData._lastToday = WeatherData._lastToday + 1
        # Save the document
        return super().save(index=WeatherData._indexname,** kwargs)

