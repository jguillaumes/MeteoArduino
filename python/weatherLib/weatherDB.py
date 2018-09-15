#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 13 19:16:35 2018

@author: jguillaumes
"""

import threading
import time

import psycopg2 as pg
from weatherLib.weatherUtil import WLogger,parseLine
from weatherLib.weatherDoc import WeatherData

__INSERT_OBS__ = "insert into weather.weather " + \
                                      "(tsa, time, temperature, humidity, pressure, " + \
                                      "light, fwVersion, swVersion, version, " + \
                                      "isThermometer, isBarometer, isHygrometer, isClock) " + \
                             "values (%(tsa)s, %(time)s, %(temperature)s, %(humidity)s, %(pressure)s, " + \
                                     "%(light)s, %(fwVersion)s, %(swVersion)s, %(version)s, " + \
                                     "%(isThermometer)s, %(isBarometer)s, %(isHygrometer)s, %(isClock)s); " 


class WeatherDB(object):
    _logger = WLogger()
    
    def __init__(self,host,user,password,database,retryInterval=5):
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
            cur = None
            self.theConn = None
            
            self._theHost = host
            self._theUser = user
            self._thePassword = password
            self._theDatabase = database
            self._theRetryInterval = retryInterval
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
            if cur is not None:
                cur.close()

    def close(self):
        if self.theConn is not None:
            self.theConn.close()
            self.theConn = None

    def reconnect(self):
        while True:
            try:
                cur = None
                self.theConn = pg.connect(host=self._theHost,
                                          user=self._theUser,
                                          password=self._thePassword,
                                          database=self._theDatabase)    
                cur = self.theConn.cursor()
                cur.execute('set search_path to \'WEATHER\';')
                WeatherDB._logger.logMessage(level="INFO",
                                         message="Connection to database {0:s} on host {1:s} established." \
                                                   .format(self._theDatabase,self._theHost))
                break
            except:
                WeatherDB._logger.logException(message="Connection to database {0:s} on host {1:s} failed." \
                                                   .format(self._theDatabase,self._theHost))
                WeatherDB._logger.logMessage(level="INFO",message="Waiting {0} seconds to retry".format(self._theRetryInterval))
                time.sleep(self._theRetryInterval)
            finally:
                if cur is not None:
                    cur.close()
        

    def insertObs(self,theObservation):
        if self.theConn is not None:
            with self.theConn as conn:
                with self.theConn.cursor() as c:
                    c.execute(__INSERT_OBS__, theObservation.to_dict())
                    conn.commit()
                    c.close()
                    WeatherDB._logger.logMessage(level="DEBUG", message="Inserted row: {0}".format(theObservation.tsa))
        else:
            raise pg.InterfaceError()

class WeatherDBThread(threading.Thread):
    _logger = WLogger()

    def __init__(self,weatherQueue,weatherDb):
        super(WeatherDBThread, self).__init__()
        self.theDb    = weatherDb
        self.theQueue = weatherQueue
        self.name = 'WeatherDBThread'

        
    def run(self):
        WeatherDBThread._logger.logMessage(level="INFO", message="DB store thread starting")
        while True:
            self.theQueue.theEvent.wait()
            q = self.theQueue.getDbQueue()
            WeatherDBThread._logger.logMessage(level='DEBUG',
                                               message="{0} items to insert in database".format(len(q)))
            for item in q:
                line = item[1]
                newTsa = item[0]
                stamp,temp,humt,pres,lght,firmware,clock,thermometer,hygrometer,barometer = parseLine(line)
                doc = WeatherData()
                doc.init(_tsa=newTsa, _time=stamp, _temperature=temp, _humidity=humt, _pressure=pres, _light=lght,
                         _fwVersion=firmware, _isBarometer=barometer, _isClock=clock,
                         _isThermometer=thermometer, _isHygrometer=hygrometer)
                try:
                    self.theDb.insertObs(doc)
                    self.theQueue.markDbQueue(newTsa)
                except pg.IntegrityError as ie:
                    WeatherDBThread._logger.logMessage(level="ERROR", 
                                                       message="Can't store tsa {0}: {1}".format(newTsa, ie))
                except pg.InterfaceError as ex:
                    WeatherDBThread._logger.logException(message="Can't talk to postgresql ({0})".format(ex))
                    self.theDb.reconnect()
                except:
                    WeatherDBThread._logger.logException('Exception trying to store observation {0}'.format(newTsa))
            self.theQueue.theEvent.clear()
            
        