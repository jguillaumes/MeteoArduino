#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 13 12:14:02 2018

@author: jguillaumes
"""

import sqlite3
import configparser
import threading
from weatherLib.weatherUtil import logException,logMessage

__INSERT_SQL__ = 'insert into queue(data, isES, isDB) values(?,0,0)'

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
        self.theLock = threading.Lock()

        config = configparser.ConfigParser()
        config.read(['./database/wQueue.ini'])

        dbFile     = config['queueDatabase']['file']
        tableDDL   = config['queueDatabase']['table']
        indexESDDL = config['queueDatabase']['indexES']
        indexDBDDL = config['queueDatabase']['indexDB']

        try:
            self.theConn = sqlite3.connect(dbFile,check_same_thread=False)
            self.theConn.execute(tableDDL)
            self.theConn.execute(indexESDDL)
            self.theConn.execute(indexDBDDL)
            logMessage(level="INFO",message="Queue database opened at {0:s}".format(dbFile))
        except:
            logException('Error initializing queue database')


    def pushLine(self,line):
        """
        Push a line into the queue.
        This function blocks until the database is not locked
        """
        with self.theLock:
            try:
                self.theConn.execute(__INSERT_SQL__, [line])
                self.theConn.commit()
            except:
                logException('Error inserting line into the queue database')
                self.theConn.rollback()
