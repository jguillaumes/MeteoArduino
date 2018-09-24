import logging
import logging.config
import threading
import signal
import pkg_resources
import os

from datetime import datetime
from time import sleep
import pytz

class WLogger(object):
    sevMap = {"CRITICAL": logging.CRITICAL, "ERROR": logging.ERROR, \
              "WARNING": logging.WARNING, "INFO": logging.INFO,\
              "DEBUG": logging.DEBUG, "NOTSET": logging.NOTSET}

    def __init__(self,loggerName='weather'):
        """
        Setup logging
        """
        conf_file = pkg_resources.resource_filename(__name__,'logging.conf')
        conf_list = [conf_file,'~/logging.conf','./logging.conf']
        logging.config.fileConfig(conf_list)
        self.wLogger = logging.getLogger(loggerName)
    
    def logMessage(self,message,level="INFO"):
        """
        Send a log message to syslog.
        Parameters:
            - message: text to send
            - level: priority level (with the usual values, in string form)
        """
        severity = self.sevMap[level]
        self.wLogger.log(severity,message)
    
    def logException(self,message):
        """
        Send an exception message to the loggers
        Parameter:
            - message: text to add to the exception
        """
        self.wLogger.exception(message)

    def setLevel(self,level=logging.INFO):
        """
        Set the level of the underlying logger programatically
        Parameters:
            - level: level to set (default is INFO)
        """
        theLevel = self.sevMap[level]
        self.wLogger.setLevel(theLevel)

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

def openFile(directory):
    """
    Open (and create) a new data file to store the raw messages got
    from de gizmo
    Parameters:
        - directory: Directory where to put the file
    """
    filename = os.path.join(directory,"weather-" + datetime.utcnow().strftime("%Y.%m.%d") + ".dat")
    file = open(filename, 'a')
    return file

