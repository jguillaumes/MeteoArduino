#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 13 12:14:02 2018

@author: jguillaumes
"""

import sqlite3
import configparser
import threading
import calendar

from weatherLib.weatherUtil import WLogger,parseLine

__SELECT_TSA__   = 'select maxtsa from tsas where day = ?'
__INSERT_QUEUE__ = 'insert into queue(id, data, isES, isDB) values(?,?,0,0)'
__INSERT_DAY__   = 'insert into tsas(day, maxtsa) values(?,1)'
__UPDATE_TSA__   = 'update tsas set maxtsa = ? where day = ?'
__SELECT_DB__    = 'select id,data,isDB from queue where isDB = 0 order by isDB,id'
__UPDATE_DB__    = 'update queue set isDB = 1 where id = ?'
__SELECT_ES__    = 'select id,data,isDB from queue where isES = 0 order by isDB,id'


class WeatherQueue(object):
    """
    Weather measurements queue.
    Implemented on a sqlite3 database
    """

    def __init__(self):
        """
        Initialize the queue database connection and, if necessary,
        create the database. Also create the lock object that will
        be used to synchronize access
        """
        self.logger = WLogger()
        self.theLock = threading.Lock()
        self.theEvent = DataReceived()
        self.theEvent.clear()
        self.curDay = 0
        self.curTSA = 0

        config = configparser.ConfigParser()
        config.read(['./database/wQueue.ini'])

        dbFile     = config['queueDatabase']['file']
        tableDDL   = config['queueDatabase']['table']
        tsasDDL    = config['queueDatabase']['control']
        indexESDDL = config['queueDatabase']['indexES']
        indexDBDDL = config['queueDatabase']['indexDB']

        try:
            self.theConn = sqlite3.connect(dbFile,check_same_thread=False)
            self.theConn.execute(tableDDL)
            self.theConn.execute(indexESDDL)
            self.theConn.execute(indexDBDDL)
            self.theConn.execute(tsasDDL)
            self.logger.logMessage(level="INFO",message="Queue database opened at {0:s}".format(dbFile))
        except:
            self.logger.logException('Error initializing queue database')

        

    def pushLine(self,line):
        """
        Push a line into the queue.
        This function blocks until the database is not locked
        """
        stamp,_,_,_,_,_,_,_,_,_ = parseLine(line)
        datestamp = calendar.timegm(stamp.date().timetuple())
        theTsa = 1
        
        with self.theLock:
            try:
                result = self.theConn.execute(__SELECT_TSA__, [datestamp])
                resCol = result.fetchone()
                if resCol == None:
                    self.theConn.execute(__INSERT_DAY__, [datestamp])
                else:
                    theTsa = resCol[0] + 1
                    self.theConn.execute(__UPDATE_TSA__, [theTsa, datestamp])
                fullTsa = (stamp.year * 10000 +
                           stamp.month * 100  +
                           stamp.day) * 1000000 + theTsa
                self.theConn.execute(__INSERT_QUEUE__, [fullTsa,line])
                self.theConn.commit()
                self.theEvent.set()
            except:
                self.logger.logException('Error inserting line into the queue database')
                self.theConn.rollback()

    def getDbQueue(self):
        with self.theLock:
            try:
                result = self.theConn.execute(__SELECT_DB__)
                queueContent = result.fetchall()
                return queueContent
            except:
                self.logger.logException('Error recovering DB queue')
                self.theConn.rollback()
                return None
            
    def markDbQueue(self, theId):
        with self.theLock:
            with self.theConn:
                self.theConn.execute(__UPDATE_DB__, [theId])
                self.logger.logMessage(level='DEBUG', 
                                       message = 'Queue entry {0} marked as DB-done'.format(theId))
                
                
class DataReceived(threading.Event):
    
    def __init__(self):
        super(DataReceived, self).__init__()
        pass
    
            