import random
import sys
import bluetooth as bt

from syslog import openlog,closelog,syslog
from syslog import LOG_USER,LOG_EMERG,LOG_ALERT,LOG_CRIT,LOG_ERR,LOG_WARNING,LOG_NOTICE,LOG_INFO,LOG_DEBUG
import time as tm
from datetime import datetime,time
from elasticsearch import client
from elasticsearch_dsl import connections,DocType,Date,Float,Long,Search,Text
from elasticsearch import ConnectionError,TransportError
from urllib3.exceptions import NewConnectionError

_sevMap = {"EMERG": LOG_EMERG, "ALERT": LOG_ALERT, "CRIT": LOG_CRIT,\
          "WARNING": LOG_WARNING, "NOTICE": LOG_NOTICE, "INFO": LOG_INFO,\
          "ERR": LOG_ERR, "DEBUG": LOG_DEBUG}

VERSION = "1.1.0"
FW_VERSION="00.00.00"

def logMessage(message,level="INFO"):
    """
    Send a log message to syslog.
    Parameters:
        - message: text to send
        - level: priority level (with the usual values, in string form)
    """
    openlog(ident="WEATHER",facility=LOG_USER)
    severity = _sevMap[level]
    syslog(severity,message)
    closelog()

class WeatherData(DocType):
    """
    Helper class to serialize a Weather observation datapoint
    """
    _index = 'weather-' + VERSION + '-' + datetime.utcnow().strftime("%Y.%m.%d")
    _lastToday=0                            # Serial number for the day
    _curDay = "YYYY.mm.dd"                  # Day we are currently processing
    tsa = Long()                            # Doc serial number
    time = Date(default_timezone='UTC')     # Placeholder for observation datetime
    temperature = Float()                   # Placeholder for temperature
    humidity = Float()                      # Placeholder for humidity %
    pressure = Float()                      # Placeholder for atm. pressure
    light = Float()                         # Placeholder for light level
    version=Text()                          # Placeholder for software version
    fwVersion=Text()                        # Placeholder for firmware version

    def save(self,** kwargs):
        """
        Save a weather observation
        """
        day = self.time.strftime("%Y.%m.%d")        # Check observation date
        nday = int(self.time.strftime("%Y%m%d"))
        if day != WeatherData._curDay:              # Date changed?
            WeatherData._curDay = day               # Yes, change index name
            WeatherData._index = 'weather-' + VERSION + '-' + day
            WeatherData._lastToday = getTopTSA(self.time)
            print("Starting at tsa {0:d} for {1:d}"\
                       .format(WeatherData._lastToday, nday))
            logMessage(level="INFO",\
                       message="Starting at tsa {0:d} for {1:d}"\
                       .format(WeatherData._lastToday, nday))
        # Compute the tsa for the new document and increment serial number
        self.tsa = nday * 1000000 + WeatherData._lastToday
        # self._id = self._curDay + "-" + "{0:06d}".format(WeatherData._lastToday)
        WeatherData._lastToday = WeatherData._lastToday + 1
        # Save the document
        return super().save(index=WeatherData._index,** kwargs)

    def create_template(conn):
        """
        Prepare the ES index template. Read it from file weather-template.json
        Parameters:
            - conn: Elasticsearch connection
        """
        with open('weather-template.json','r') as tempFile:
            template = tempFile.read()
            templname = 'weather-' + VERSION + '-*'
            client.IndicesClient(conn).put_template(name=templname,\
                                                body=template)

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
            esConn = connections.create_connection(hosts=hosts[hostIdx],timeout=5)
            WeatherData.create_template(esConn)
            WeatherData.init(index=WeatherData._index)
            connected = True
        except (ConnectionError, NewConnectionError, TransportError):
            msg = "Host %s not available." % hosts[hostIdx]
            print("WARNING: %s" % msg)
            logMessage(level="WARNING", message=msg)
            hostIdx += 1
            retries += 1
            if hostIdx >= numHosts:
                hostIdx = 0
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
    

def connectBT(addr, serv):
    """
    Connect to bluetooth of weather sensors device
    Parameters:
        - address: BT address of the device, in hex form (XX:XX:XX:XX:XX:XX)
        - service: UUID of the RFCOMM service in the device
    """
    print("Service: {0:s}, address:{1:s}".format(addr,serv))
    srvlist = bt.find_service(uuid = serv, address = addr)
    if len(srvlist) == 0:
        msg = "BT service not available."
        print(msg)
        logMessage(level="ERR", message=msg)
        return False, 0, ""
    else:
        srv = srvlist[0]
        port = srv["port"]
        name = srv["name"]
        host = srv["host"]
        sock=bt.BluetoothSocket(bt.RFCOMM)
        sock.connect((host,port))
        return True, sock, name

def parseLine(line):
    """
    Parse a line into its timestamp, temperature, humidity,
    pressure and light.
    Parameters:
        - line: Line to parse
    Returns:
        timestamp (string), temp (float), humidity (float), pressure (float),
        light (float)

    """
    tokens = line.split(':')
    stamp=""
    temp=-999.0
    humt=-999.0
    pres=-999.0
    lght=-999.0
    for t in tokens:
        if t[0:1] == 'C':
            stamp = datetime.strptime(t[1:], '%Y%m%d%H%M%S')
        elif t[0:1] == 'T':
            temp = float(t[1:])
        elif t[0:1] == 'H':
            humt = float(t[1:])
        elif t[0:1] == 'P':
            pres = float(t[1:])
        elif t[0:1] == 'L':
            lght = float(t[1:])
    return stamp,temp,humt,pres,lght    

def saveData(conn, line):
    """
    Send a line of data to ES
    Parameters:
        - conn: ES connection
        - line: Line of data (DATA:C...) from the BT device
    """
    stamp, temp, humt, pres, lght = parseLine(line)
    w = WeatherData()
    w.time = stamp
    w.temperature = temp
    w.humidity = humt
    w.pressure = pres
    w.light = lght
    w.version = VERSION
    w.fwVersion = FW_VERSION
    w.save()       

def connect_wait_ES(hostlist):
    phase=0
    retrChangePhase=10
    delays=[5,30]
    while True:
        try:
            connected,esConn,hostIdx = connectES(hosts=hostlist)
            if connected:
                print("Connected to ES host: ", hostlist[hostIdx])
                break
            else:
                logMessage(message="Connection try failed", level="ERR")
                print("Could not connect to ES, retryng...")
                if phase == 0:
                    tm.sleep(delays[0])
                    retrChangePhase -= 1
                    if retrChangePhase <= 0:
                        phase = 1
                        msg = 'Switching to {0:d} seconds delay.'.format(delays[1])
                        print(msg)
                        logMessage(level="INFO",message=msg)
                    else:
                        pass
                else:
                    tm.sleep(delays[1])                    
        except:
            msg = "Unexpected exception trying to connect to ES: %s" % sys.exc_info()[0]
            logMessage(level="CRIT",message=msg)
            print(msg)
    return esConn


def connect_wait_BT(address,service):
    phase=0
    retrChangePhase=10
    delays=[5,60]
    while True:
        connected, sock, name = connectBT(addr=address, serv=service)
        if connected:
            print("Connected to weather service at \"%s\" on %s" % (name,address))
            return sock
            break
        else:
            if phase == 0:
                tm.sleep(delays[0])
                retrChangePhase -= 1
                if retrChangePhase <= 0:
                    phase = 1
                    msg = 'Switching to {0:d} seconds delay.'.format(delays[1])
                    print(msg)
                    logMessage(level="INFO",message=msg)
                else:
                    pass
            else:
                tm.sleep(delays[1])

def openFile():
    filename = "weather-" + datetime.utcnow().strftime("%Y.%m.%d") + ".dat"
    file = open(filename, 'a')
    return file

