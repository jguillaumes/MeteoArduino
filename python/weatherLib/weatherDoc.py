# -*- coding: utf-8 -*-

from weatherLib.weatherUtil import WLogger
from weatherLib.constants import VERSION,SW_VERSION

from datetime import datetime

from elasticsearch import client
from elasticsearch_dsl import DocType,Date,Float,Boolean,Long,Text

class WeatherData(DocType):
    """
    Helper class to serialize a Weather observation datapoint
    """
    _logger = WLogger()
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

    def init(self,_tsa,_time,_temperature,_humidity,_pressure,_light,
                 _fwVersion,_isClock,_isThermometer,
                 _isHygrometer,_isBarometer, _version=VERSION, _swVersion=SW_VERSION):
        self.tsa = _tsa
        self.time = _time
        self.temperature = _temperature
        self.humidity = _humidity
        self.pressure = _pressure
        self.light = _light
        self.version = _version
        self.fwVersion = _fwVersion
        self.swVersion = _swVersion
        self.isClock = _isClock
        self.isThermometer = _isThermometer
        self.isHygrometer = _isHygrometer
        self.isBarometer = _isBarometer

    @staticmethod
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

        