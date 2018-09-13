#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 13 19:16:35 2018

@author: jguillaumes
"""

import psycopg2 as pg
from weatherLib.weatherUtil import WLogger
#from weatherLib.WeatherDoc import WeatherData

__INSERT_OBS__ = "insert into weather.weather " + \
                                      "(tsa, time, temperature, humidity, pressure, " + \
                                      "light, fwVersion, swVersion, version, " + \
                                      "isThermometer, isBarometer, isHygrometer, isClock) " + \
                             "values (%(tsa)s, %(time)s, %(temperature)s, %(humidity)s, %(pressure)s, " + \
                                     "%(light)s, %(fwVersion)s, %(swVersion)s, %(version)s, " + \
                                     "%(isThermometer)s, %(isBarometer)s, %(isHygrometer)s, %(isClock)s); " 


class WeatherDB(object):
    _logger = WLogger()
    
    def __init__(self,host,user,password,database):
        """
        Establish a postgresql connection and
        ready the WeatherDB object.
        Parameters:
            - host: machine hosting the pgsql instalce
            - user: connection username
            - password: connection password
            - database: database name
        """
        try:
            self.theConn = pg.connect(host=host,user=user,password=password,database=database)    
            cur = self.theConn.cursor()
            cur.execute('set search_path to \'WEATHER\';')
            WeatherDB._logger.logMessage(level="INFO",
                                         message="Connection to database {0:s} on host {1:s} established." \
                                                   .format(database,host))
        except:
            WeatherDB._logger.logException(message="Connection to database {0:s} on host {1:s} failed." \
                                                   .format(database,host))
        finally:
            cur.close()

    def close(self):
        self.theConn.close()
        self.theConn = None

    def insertObs(self,theObservation):
        with self.theConn:
            with self.theConn.cursor() as c:
                c.execute(__INSERT_OBS__, theObservation.to_dict())
                WeatherDB._logger.logMessage(level="DEBUG", message="Inserted row: {0}".format(theObservation.to_dict()))

