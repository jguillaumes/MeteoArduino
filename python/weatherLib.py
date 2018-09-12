import random
import sys
import bluetooth as bt
import logging
import logging.config


import time as tm
from datetime import datetime
import pytz
from elasticsearch import client
from elasticsearch_dsl import connections,DocType,Date,Float,Long,Search,Text,Boolean
from elasticsearch import ConnectionError,TransportError
from urllib3.exceptions import NewConnectionError

_sevMap = {"CRITICAL": logging.CRITICAL, "ERROR": logging.ERROR, \
          "WARNING": logging.WARNING, "INFO": logging.INFO,\
          "DEBUG": logging.DEBUG, "NOTSET": logging.NOTSET}

# VERSION: Version of the Elastic document (change it and it will make a new index)
VERSION = "2.0.0"
# FW_VERSION: Default firmware version, when not informed in message
FW_VERSION="02.00.00"
# SW_VERSION: Version of THIS software; gets stored in Elastic
SW_VERSION="2.1.0"

__wLogger__ = None

def setupLog():
    """
    Setup logging
    Returns:
        Logger object
    """
    global __wLogger__
    logging.config.fileConfig("logging.conf")
    __wLogger__ = logging.getLogger("log")
    return __wLogger__

def logMessage(message,level="INFO"):
    """
    Send a log message to syslog.
    Parameters:
        - message: text to send
        - level: priority level (with the usual values, in string form)
    """
    severity = _sevMap[level]
    __wLogger__.log(severity,message)

def logException(message):
    """
    Send an exception message to the loggers
    Parameter:
        - message: text to add to the exception
    """
    __wLogger__.exception(message)


class WeatherData(DocType):
    """
    Helper class to serialize a Weather observation datapoint
    """
    _indexname = 'weather-' + VERSION + '-' + datetime.utcnow().strftime("%Y.%m.%d")
    _lastToday=0                            # Serial number for the day
    _curDay = "YYYY.mm.dd"                  # Day we are currently processing
    tsa = Long()                            # Doc serial number
    time = Date(default_timezone='UTC')     # Placeholder for observation datetime
    temperature = Float()                   # Placeholder for temperature
    humidity = Float()                      # Placeholder for humidity %
    pressure = Float()                      # Placeholder for atm. pressure
    light = Float()                         # Placeholder for light level
    version=Text()                          # Placeholder for document version
    fwVersion=Text()                        # Placeholder for firmware version
    swVersion=Text()                        # Placeholder for software version
    isClock=Boolean()                       # Placeholder: clock present indicator
    isThermometer=Boolean()                 # Placeholder: thermometer present indicator
    isHygrometer=Boolean()                  # Placeholder: hybrometer present indicator
    isBarometer=Boolean()                   # Placeholder: Barometer present indicator
    
    def save(self,** kwargs):
        """
        Save a weather observation
        """
        day = self.time.strftime("%Y.%m.%d")        # Check observation date
        nday = int(self.time.strftime("%Y%m%d"))
        if day != WeatherData._curDay:              # Date changed?
            WeatherData._curDay = day               # Yes, change index name
            WeatherData._indexname = 'weather-' + VERSION + '-' + day
            WeatherData._lastToday = getTopTSA(self.time)
            logMessage(level="INFO",\
                       message="Starting at tsa {0:d} for {1:d}"\
                       .format(WeatherData._lastToday, nday))
        # Compute the tsa for the new document and increment serial number
        self.tsa = nday * 1000000 + WeatherData._lastToday + 1
        # self._id = self._curDay + "-" + "{0:06d}".format(WeatherData._lastToday)
        WeatherData._lastToday = WeatherData._lastToday + 1
        # Save the document
        return super().save(index=WeatherData._indexname,** kwargs)

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
            esConn = connections.create_connection(hosts=hosts[hostIdx],timeout=10)
            WeatherData.create_template(esConn)
            WeatherData.init(index=WeatherData._indexname)
            connected = True
        except (ConnectionError, NewConnectionError, TransportError):
            msg = "Host %s not available." % hosts[hostIdx]
            logException(message=msg)
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
    logMessage(level="INFO",message="Service: {0:s}, address:{1:s}".format(serv,addr))
    srvlist = bt.find_service(uuid = serv, address = addr)
    if len(srvlist) == 0:
        msg = "BT service not available."
        logMessage(level="WARNING", message=msg)
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
    # print(tokens)
    stamp=""
    temp=-999.0
    humt=-999.0
    pres=-999.0
    lght=-999.0
    clock=False
    thermometer=False
    barometer=False
    hygrometer=False
    firmware=""
    for t in tokens:
        if t == 'DATA ':
            pass # ignore header
        elif t[0:1] == 'C':
            stamp = datetime.strptime(t[1:], '%Y%m%d%H%M%S').replace(tzinfo=pytz.UTC)
        elif t[0:1] == 'T':
            temp = float(t[1:])
        elif t[0:1] == 'H':
            humt = float(t[1:])
        elif t[0:1] == 'P':
            pres = float(t[1:])
        elif t[0:1] == 'L':
            lght = float(t[1:])
        elif t[0:1] == 'F':
            firmware = t[1:]
        elif t[0:1] == 'D':
            devList = t[1:]
            # print(devList)
            clock       = devList[0:1] == 'C'
            thermometer = devList[1:2] == 'T'
            hygrometer  = devList[2:3] == 'H'
            barometer   = devList[3:4] == 'P'
    return stamp,temp,humt,pres,lght,firmware,clock,thermometer,hygrometer,barometer    

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


def connect_wait_BT(address,service):
    phase=0
    retrChangePhase=10
    delays=[5,60]
    while True:
        connected, sock, name = connectBT(addr=address, serv=service)
        if connected:
            logMessage(level="INFO",message="Connected to weather service at \"%s\" on %s" % (name,address))
            return sock
            break
        else:
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

def openFile():
    filename = "weather-" + datetime.utcnow().strftime("%Y.%m.%d") + ".dat"
    file = open(filename, 'a')
    return file

def getLine(socket):
    """ 
    Read a line from a socket connection.
    It reads characters from a socket until it gets a CR+LF combination. The
    CR+LF is *not* returned as part of the read line. 
    If a line does not include the LF (the terminator is just a CR, it's
    discarded.
    Parameters:
    - socket: opened socket
    Returns:
    Received string        
    """
    line = ""
    onLoop = True                             # End of loop switch
    while onLoop:
        byte = socket.recv(1)                 # Get byte from socket
        if byte == b'\r':                     # Carriage return?
            byte = socket.recv(1)             # Consume LF
            if byte != b'\n':                 # IF not LF, big trouble: discard line
                line = ""
            else:
                onLoop = False                # End of loop, line ready
        else:
            try:
                line = line + byte.decode()   # Add character to current working line
            except UnicodeDecodeError as e:
                msg = "Error decoding received byte: {0:s}".format(repr(e))
                logMessage(level="WARNING",message=msg)
    return line                              # The line is complete
            
def waitAnswer(socket, answer,retries=5):
    """
    Wait for a specific answer, discarding all the read lines until that
    answer is read or the number of retries is exhausted.
    Parameters:
        - socket: Open socket to read
        - answer: text (6 characters) to expect
        - retries: Number of lines to read until leaving
    Returns:
        Boolean (true = anwer found, false = retries exhausted)
    """
    answ = ""
    remain = retries
    while answ != answer[0:6] and remain > 0:
        line = getLine(socket)
        logMessage(level="INFO",message=line)
        answ = line[0:6]
        remain -= 1
    return answ == answer[0:6]

