#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 18 09:49:13 2018

@author: jguillaumes
"""

# -*- coding: utf-8 -*-

import os
import sys

import psycopg2 as pg
import psycopg2.extras
import elasticsearch as es

script_path = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir))
sys.path.append(script_path)

from weatherLib.weatherDoc import WeatherData
from weatherLib.weatherUtil import WLogger


__UPDATE_DOC__   = 'update weather set esDocId = %(esDocId)s where tsa = %(tsa)s;'
__SELECT_DOC__   = 'select tsa,time from weather where esDocId is null order by tsa;'


host = 'localhost'
user = 'weather'
password = 'weather'
database = 'weather'

logger = WLogger(loggerName='weather.tools')
logger.logMessage("Starting...")

hostlist = [
        {'host':'elastic00','port':9200},
        {'host':'elastic01','port':9200},
        {'host':'elastic02','port':9200},
            ]

pgConn  = pg.connect(host=host,user=user,password=password,database=database,
                     cursor_factory=psycopg2.extras.RealDictCursor)    
client  = es.Elasticsearch(hostlist)


def getData() -> []:
    with pgConn.cursor() as c:
        c.execute(__SELECT_DOC__)
        return c.fetchall()


data = getData()
with pgConn:
    for d in data:
        doc = WeatherData()
        w_tsa = d['tsa']
        w_time = d['time']
        filt = doc.search(using=client).\
                filter('term',time=w_time)
        result = filt.scan()
        for d in result:
            dic = { 'esDocId': d.meta.id, 'tsa': d.tsa }
            with pgConn.cursor() as c:
                logger.logMessage("Updating {0}, id={1}".format(w_tsa,d.meta.id))
                c.execute(__UPDATE_DOC__, dic)
