#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 13 12:14:02 2018

@author: jguillaumes
"""

import os
import sqlite3
import configparser
import threading
import calendar
import pkg_resources

from time import sleep

from weatherLib.weatherUtil import WLogger,parseLine

_SELECT_TSA   = 'select maxtsa from tsas where day = ?'
_INSERT_QUEUE = 'insert into queue(id, data, isES, isDB) values(?,?,0,0)'
_INSERT_DAY   = 'insert into tsas(day, maxtsa) values(?,1)'
_UPDATE_TSA   = 'update tsas set maxtsa = ? where day = ?'
_SELECT_DB    = 'select id,data,isDB from queue where isDB = 0 order by isDB,id'
_UPDATE_DB    = 'update queue set isDB = 1 where id = ?'
_SELECT_ES    = 'select id,data,isDB from queue where isES = 0 order by isES,id'
_UPDATE_ES    = 'update queue set isES = 1 where id = ?'
_PURGE_QUEUE  = 'delete from queue where isDB=1 and isES=1'
_COUNT_QUEUE  = 'select count(*) from queue where isDB=1 and isES=1'

class WeatherQueue(object):
    """
    Weather measurements queue.
    Implemented on a sqlite3 database
    """

    def __init__(self,dbdir):
        """
        Initialize the queue database connection and, if necessary,
        create the database. Also create the lock object that will
        be used to synchronize access
        """
        self.logger = WLogger()
        self.theLock = threading.Lock()
        self.curDay = 0
        self.curTSA = 0

        ini_file = pkg_resources.resource_filename(__name__,'./database/wQueue.ini')
        config = configparser.ConfigParser()
        config.read([ini_file])

        tableDDL   = config['queueDatabase']['table']
        tsasDDL    = config['queueDatabase']['control']
        indexESDDL = config['queueDatabase']['indexES']
        indexDBDDL = config['queueDatabase']['indexDB']
        dbFile = os.path.join(dbdir,'wQueue.db')

        try:
            self.theConn = sqlite3.connect(dbFile,check_same_thread=False)
            self.theConn.isolation_level = 'IMMEDIATE'
            self.theConn.execute(tableDDL)
            self.theConn.execute(indexESDDL)
            self.theConn.execute(indexDBDDL)
            self.theConn.execute(tsasDDL)
            self.theConn.commit()
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
                result = self.theConn.execute(_SELECT_TSA, [datestamp])
                resCol = result.fetchone()
                if resCol == None:
                    self.theConn.execute(_INSERT_DAY, [datestamp])
                else:
                    theTsa = resCol[0] + 1
                    self.theConn.execute(_UPDATE_TSA, [theTsa, datestamp])
                fullTsa = (stamp.year * 10000 +
                           stamp.month * 100  +
                           stamp.day) * 1000000 + theTsa
                self.theConn.execute(_INSERT_QUEUE, [fullTsa,line])
                self.theConn.commit()
            except:
                self.logger.logException('Error inserting line into the queue database')
                self.theConn.rollback()

    def getDbQueue(self):
        """
        Get al the queue lines NOT marked as inserted into the database.
        (isDB == 0)
        """
        with self.theLock:
            try:
                result = self.theConn.execute(_SELECT_DB)
                queueContent = result.fetchall()
                return queueContent
            except:
                self.logger.logException('Error fetching DB queue')
                self.theConn.rollback()
                return None
            
    def markDbQueue(self, theId):
        """
        Mark a queue entry as inserted into the database
        Parameters:
            - theId: row identifier to mark
        """
        with self.theLock:
            with self.theConn:
                self.theConn.execute(_UPDATE_DB, [theId])
                self.theConn.commit()
                self.logger.logMessage(level='DEBUG', 
                                       message = 'Queue entry {0} marked as DB-done'.format(theId))
                
    def getESQueue(self):
        """
        Get al the queue lines NOT marked as indexed in elasticserch.
        (isES == 0)
        """
        with self.theLock:
            try:
                result = self.theConn.execute(_SELECT_ES)
                queueContent = result.fetchall()
                return queueContent
            except:
                self.logger.logException('Error fetching ES queue')
                self.theConn.rollback()
                return None
            
    def markESQueue(self, theId):
        """
        Mark a queue entry as indexed in elasticsearch
        Parameters:
            - theId: row identifier to mark
        """
        with self.theLock:
            with self.theConn:
                self.theConn.execute(_UPDATE_ES, [theId])
                self.theConn.commit()
                self.logger.logMessage(level='DEBUG', 
                                       message = 'Queue entry {0} marked as ES-done'.format(theId))
                
    def purgeQueue(self):
        with self.theLock:
            with self.theConn as conn:
                result = conn.execute(_COUNT_QUEUE)
                r = result.fetchone()
                count = r[0]
                self.logger.logMessage(message="About to purge {0} queue entries.".format(count))
                conn.execute(_PURGE_QUEUE)
                conn.commit()
                self.logger.logMessage(message="Queue purged.")
    
class QueueJanitorThread(threading.Thread):
    """
    Class to implement a thread to do maintenance tasks in the queue
    database.
    It will awake itself periodically to delete the queue elements
    which have already been processed.
    """
    _logger = WLogger()

    def __init__(self,queue,period=60):
        super(QueueJanitorThread, self).__init__()

        self.theQueue = queue
        self.thePeriod = period
        self._stopSwitch = False
        self.name = 'QueueJanitorThread'
        self._pending = False
        QueueJanitorThread._logger.logMessage("Janitor configured to run every {0} seconds".format(period))

    def stop(self):
        self._stopSwitch = True

    def run(self):
        """
        Run method.
        It creates a timer object and schedules it according to the configured
        perdiod. 
        The method runs an infinite loop with 1-second delays to check if the 
        termination flag (_stopSwitch) has been raised. In this case it cancels
        the timer request (if pending) and ends.
        """
        theTimer = None
        self._pending = False
        QueueJanitorThread._logger.logMessage("Starting thread {0}.".format(self.getName()), level="INFO")
        while not self._stopSwitch:
            if not self._pending:
                theTimer = threading.Timer(self.thePeriod,self.doCleanup)
                theTimer.name = "JanitorTimer"
                self._pending = True
                theTimer.start()
            sleep(1)
        theTimer.cancel()
        QueueJanitorThread._logger.logMessage("Thread {0} stopped by request.".format(self.getName()), level="INFO")

    def doCleanup(self):
        """
        This method is scheduled inside a Timer object by the run() loop.
        """
        self.theQueue.purgeQueue()
        self._pending = False




            