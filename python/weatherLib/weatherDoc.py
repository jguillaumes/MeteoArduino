# -*- coding: utf-8 -*-

from weatherLib.weatherUtil import WLogger
from weatherLib.constants import VERSION,SW_VERSION

from datetime import datetime

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
        """
        Set up the document attributes from the measurement variables and the
        version constants.
        The id of the document will be set to the TSA number converted to a string 
        prefixed with a "T".
        """
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
        self.meta.id = "T{0}".format(_tsa)


    def save(self, client, ** kwargs):
        """
        Save a weather observation
        Check if the day has changed to swith indexes.
        """
        day = self.time.strftime("%Y.%m.%d")        # Check observation date
        if day != WeatherData._curDay:              # Date changed?
            WeatherData._curDay = day               # Yes, change index name
            newIdx = 'weather-' + VERSION + '-' + day
            WeatherData._indexname = newIdx
            WeatherData._logger.logMessage(level="INFO",
                                           message="Switching to new index {0}".format(newIdx))
        return super().save(using=client, index=WeatherData._indexname, ** kwargs)
        