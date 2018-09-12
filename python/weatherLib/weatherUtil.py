import logging
import logging.config

from datetime import datetime
import pytz



__sevMap__ = {"CRITICAL": logging.CRITICAL, "ERROR": logging.ERROR, \
              "WARNING": logging.WARNING, "INFO": logging.INFO,\
              "DEBUG": logging.DEBUG, "NOTSET": logging.NOTSET}


# Logging object
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
    severity = __sevMap__[level]
    __wLogger__.log(severity,message)

def logException(message):
    """
    Send an exception message to the loggers
    Parameter:
        - message: text to add to the exception
    """
    __wLogger__.exception(message)

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

def openFile():
    filename = "weather-" + datetime.utcnow().strftime("%Y.%m.%d") + ".dat"
    file = open(filename, 'a')
    return file

