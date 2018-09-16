# -*- coding: utf-8 -*-

import os
import sys
import pickle

import elasticsearch as es
import elasticsearch_dsl as esd

script_path = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir))
sys.path.append(script_path)

from weatherLib.weatherDoc import WeatherData
from weatherLib.weatherDB import WeatherDB
from weatherLib.weatherUtil import WLogger

dumpFile='./weather-dump.dat'
logger = WLogger(loggerName='weather.tools')

hostlist = [
        {'host':'elastic00','port':9200},
        {'host':'elastic01','port':9200},
        {'host':'elastic02','port':9200},
            ]

client = es.Elasticsearch(hostlist)

doc = WeatherData(using=client,index='weather-2.0.0-2018.09.16')
srch = doc.search().filter

s = doc.search(using=client).filter('range', **{'tsa': {'lt':20180916001872}}).scan()


logger.logMessage("Collecting documents from elasticsearch.")
doclist = [ d.to_dict() for d in list(s)]
    
logger.logMessage("Dumping list of collected documents into {0}.".format(dumpFile))
with open(dumpFile,'w') as f:
    pickle.dump(doclist,f)
    


#wdb = WeatherDB('pi03','weather','weather','weather')

#for doc in doclist:
    #wdb._logger.logMessage(level='DEBUG',message=
    # wdb.insertObs(doc)
