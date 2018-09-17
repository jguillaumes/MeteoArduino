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

__INSERT_OBS__ = "insert into weather " + \
                                      "(tsa, time, temperature, humidity, pressure, " + \
                                      "light, fwVersion, swVersion, version, " + \
                                      "isThermometer, isBarometer, isHygrometer, isClock) " + \
                             "values (%(tsa)s, %(time)s, %(temperature)s, %(humidity)s, %(pressure)s, " + \
                                     "%(light)s, %(fwVersion)s, %(swVersion)s, %(version)s, " + \
                                     "%(isThermometer)s, %(isBarometer)s, %(isHygrometer)s, %(isClock)s); " 


class WeatherDB(object):
    """
    WeatherDB: Class to manage the storage of observations into a postgresql
    database.
    The class contains methods to reconnect to the database and to do the 
    insertion of the rows containing the observations.
    """
    _logger = WLogger()
    
    def __init__(self,host,user,password,database):
        """
        Establish a postgresql connection and
        ready the WeatherDB object.
        It tries to connect once. If the connection is not posible it
        doesn't abort; the connection object is set to None it can be
        retried afterwards.
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
            self.theConn = pg.connect(host=host,user=user,password=password,database=database)    
            cur = self.theConn.cursor()
            cur.execute('set search_path to \'weather\';')
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
        """
        Close the connection.
        """
        if self.theConn is not None:
            self.theConn.close()
            self.theConn = None

    def reconnect(self):
        """
        reconnect: try to connect to the postgres database
        Returns:
            True if the connection was made
            False otherwise
        """
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
            return True
        except:
            WeatherDB._logger.logException(message="Connection to database {0:s} on host {1:s} failed." \
                                               .format(self._theDatabase,self._theHost))
            return False            
        finally:
            if cur is not None:
                cur.close()
        

    def insertObs(self,theObservation):
        if self.theConn is not None:
            with self.theConn as conn:
                with self.theConn.cursor() as c:
                    dic = theObservation.to_dict()
                    if dic['temperature'] == -999:
                        dic['temperature'] = None
                    if dic['pressure'] == -999:
                        dic['pressure'] = None
                    if dic['humidity'] == -999:
                        dic['humidity'] = None
                    c.execute(__INSERT_OBS__, dic)
                    conn.commit()
                    WeatherDB._logger.logMessage(level="DEBUG", message="Inserted row: {0}".format(theObservation.tsa))
        else:
            raise pg.InterfaceError()

class WeatherDBThread(threading.Thread):
    _logger = WLogger()

    def __init__(self,weatherQueue,weatherDb,event,retryInterval=5):
        super(WeatherDBThread, self).__init__()
        self.theDb    = weatherDb
        self.theQueue = weatherQueue
        self.theEvent = event
        self.name = 'WeatherDBThread'
        self._stopSwitch = False
        self._theRetryInterval = retryInterval


    def stop(self):
        self._stopSwitch = True
        
    def run(self):
        WeatherDBThread._logger.logMessage("Starting thread {0}.".format(self.getName()), level="INFO")

        while not self._stopSwitch:
            self.theEvent.wait()
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
                    connected = False
                    while not self._stopSwitch and not connected:
                        WeatherDB._logger.logMessage(level="INFO",message="Waiting {0} seconds to retry".format(self._theRetryInterval))
                        time.sleep(self._theRetryInterval)
                        connected = self.theDb.reconnect()
                except:
                    WeatherDBThread._logger.logException('Exception trying to store observation {0}'.format(newTsa))
            self.theEvent.clear()
        WeatherDBThread._logger.logMessage("Thread {0} stopped by request.".format(self.getName()), level="INFO")
        