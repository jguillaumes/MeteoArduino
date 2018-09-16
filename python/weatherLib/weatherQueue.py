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

__SELECT_TSA__   = 'select maxtsa from tsas where day = ?'
__INSERT_QUEUE__ = 'insert into queue(id, data, isES, isDB) values(?,?,0,0)'
__INSERT_DAY__   = 'insert into tsas(day, maxtsa) values(?,1)'
__UPDATE_TSA__   = 'update tsas set maxtsa = ? where day = ?'
__SELECT_DB__    = 'select id,data,isDB from queue where isDB = 0 order by isDB,id'
__UPDATE_DB__    = 'update queue set isDB = 1 where id = ?'
__SELECT_ES__    = 'select id,data,isDB from queue where isES = 0 order by isES,id'
__UPDATE_ES__    = 'update queue set isES = 1 where id = ?'
__PURGE_QUEUE__  = 'delete from queue where isDB=1 and isES=1'
__COUNT_QUEUE__  = 'select count(*) from queue where isDB=1 and isES=1'

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
                result = self.theConn.execute(__SELECT_DB__)
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
                self.theConn.execute(__UPDATE_DB__, [theId])
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
                result = self.theConn.execute(__SELECT_ES__)
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
                self.theConn.execute(__UPDATE_ES__, [theId])
                self.theConn.commit()
                self.logger.logMessage(level='DEBUG', 
                                       message = 'Queue entry {0} marked as ES-done'.format(theId))
                
    def purgeQueue(self):
        with self.theLock:
            with self.theConn as conn:
                result = conn.execute(__COUNT_QUEUE__)
                r = result.fetchone()
                count = r[0]
                self.logger.logMessage(message="About to purge {0} queue entries.".format(count))
                conn.execute(__PURGE_QUEUE__)
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
        QueueJanitorThread._logger.logMessage("Janitor configured to run every {0} seconds".format(period))

    def stop(self):
        self._stopSwitch = True

    def run(self):
        QueueJanitorThread._logger.logMessage("Starting thread {0}.".format(self.getName()), level="INFO")
        while not self._stopSwitch:
            self.theQueue.purgeQueue()
            sleep(self.thePeriod)
        QueueJanitorThread._logger.logMessage("Thread {0} stopped by request.".format(self.getName()), level="INFO")




            