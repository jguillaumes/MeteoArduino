import time as tm

import elasticsearch
import threading

from weatherLib.constants import VERSION
from weatherLib.weatherUtil import WLogger,parseLine
from weatherLib.weatherDoc import WeatherData

class WeatherES(object):
    """
    WeatherES: Class to manage the connection to the ElasticSearch cluster
    Currently its only function is to initialize the ElasticSearch client
    """
    _logger = WLogger()
    
    def __init__(self,hosts,retryDelay=5, elTimeout=10):
        """
        Initialize the WeatherEL object.
        Parameters:
            - hosts: list of elasticsearch ingest nodes to try to connect to
            - retryDelay: delay between reconnection attempts
            - elTimeout: timeout for elasticsearch operations
        """
        self.theHosts = hosts
        self.theDelay = retryDelay
        self.theTimeOut = elTimeout
        numHosts = len(self.theHosts)
        hostlist = [ {'host':h, 'port':9200,'timeout':self.theTimeOut} for h in self.theHosts ]
        self.theClient = elasticsearch.Elasticsearch(hosts=hostlist,max_retries=numHosts)
             
    
class WeatherESThread(threading.Thread):
    _logger = WLogger()

    def __init__(self,weatherQueue,weatherES,event):
        super(WeatherESThread, self).__init__()
        self.theES    = weatherES
        self.theQueue = weatherQueue
        self.theEvent = event
        self.name = 'WeatherESThread'
        self._stopSwitch = False
        
    def stop(self):
        self._stopSwitch = True
        
    def run(self):
        WeatherESThread._logger.logMessage("Starting thread {0}.".format(self.getName()), level="INFO")

        templname = 'weather-' + VERSION + '-*'
        while not self._stopSwitch:
            try:
                ic = elasticsearch.client.IndicesClient(self.theES.theClient)
                if not ic.exists_template(templname):
                    templFileName = 'weather-' + VERSION + '-template.json'
                    with open(templFileName) as templFile:
                        templateBody = templFile.read()
                    ic.put_template(name=templname,body=templateBody)
                    WeatherESThread._logger.logMessage(level="INFO",message="Template {0} created.".format(templname))
                else:
                    WeatherESThread._logger.logMessage(level="INFO",message="Template {0} already exists.".format(templname))

                break
            
            except:
                WeatherESThread._logger.logException(
                        message='Error trying to create the document template.')
                tm.sleep(5)
        if self._stopSwitch:
            WeatherESThread._logger.logMessage("Thread {0} stopped by request.".format(self.getName()), level="INFO")
        else:
            WeatherESThread._logger.logMessage(level="INFO", message="ES template established.")

        while not self._stopSwitch:
            self.theEvent.wait()
            q = self.theQueue.getESQueue()
            WeatherESThread._logger.logMessage(level='DEBUG',
                                               message="{0} docs to index".format(len(q)))

            for item in q:
                line = item[1]
                newTsa = item[0]
                stamp,temp,humt,pres,lght,firmware,clock,thermometer,hygrometer,barometer = parseLine(line)
                doc = WeatherData()
                doc.init(_tsa=newTsa, _time=stamp, _temperature=temp, _humidity=humt, _pressure=pres, _light=lght,
                         _fwVersion=firmware, _isBarometer=barometer, _isClock=clock,
                         _isThermometer=thermometer, _isHygrometer=hygrometer)
                try:
                    doc.save(client=self.theES.theClient)
                    WeatherES._logger.logMessage(level="DEBUG", message="Indexed doc: {0}".format(doc.tsa))

                    self.theQueue.markESQueue(newTsa)
                except:
                    WeatherESThread._logger.logException('Exception trying to push observation {0}'.format(newTsa))
            self.theEvent.clear()
        WeatherESThread._logger.logMessage("Thread {0} stopped by request.".format(self.getName()), level="INFO")


