# -*- coding: utf-8 -*-

import os
import sys

import psycopg2 as pg
import psycopg2.extras
import elasticsearch as es
import elasticsearch.client as escl

script_path = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir))
sys.path.append(script_path)

from weatherLib.weatherDoc import WeatherData
from weatherLib.weatherUtil import WLogger


__CREATE_TEMP   = "create table if not exists weather_temp (like weather_dupes excluding constraints);"
__TRUNCATE_TEMP = 'truncate table weather_temp;'
__SELECT_DUPES  = "select * from weather_dupes order by tsa, time;" 
__INSERT_DUPES  = "insert into weather_temp " + \
                                      "(tsa, time, temperature, humidity, pressure, " + \
                                      "light, fwVersion, swVersion, version, " + \
                                      "isThermometer, isBarometer, isHygrometer, isClock) " + \
                             "values (%(tsa)s, %(time)s, %(temperature)s, %(humidity)s, %(pressure)s, " + \
                                     "%(light)s, %(fwVersion)s, %(swVersion)s, %(version)s, " + \
                                     "%(isThermometer)s, %(isBarometer)s, %(isHygrometer)s, %(isClock)s); " 

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
pgConn.cursor().execute(__CREATE_TEMP)
pgConn.cursor().execute(__TRUNCATE_TEMP)
pgConn.commit()

def getData() -> []:
    with pgConn.cursor() as c:
        c.execute(__SELECT_DUPES)
        return c.fetchall()


data = getData()
lastTsa = 0
lastDay = 0
fakeTsa = 0
for d in data:
    tsa = d['tsa']
    #logger.logMessage(level='DEBUG',message=('tsa: {0} / last: {1}'.format(tsa,lastTsa)))
    if lastTsa != tsa:
        theday = tsa // 1000000
        if theday != lastDay:
            fakeTsa = 900001
            lastDay = theday
    else:
        d['tsa'] = theday * 1000000 + fakeTsa
        fakeTsa += 1
    lastTsa = tsa
    try:
        #logger.logMessage(level='DEBUG',message=('tsa: {0}'.format(d['tsa'])))
        sql = "insert into weather_temp (" + ", ".join(d.keys()) + ") values (" + ", ".join(["%("+k+")s" for k in d]) + ");"    
        pgConn.cursor().execute(sql,d)
    except:
        logger.logException('Error executing {0}'.format(sql))
        pgConn.rollback()
        break
pgConn.commit()
    

def scanIndex(indexName, filtered):
    doc = WeatherData(using=client)
    s_filt = doc.search(using=client,index=indexName).\
                  filter('range', **{'tsa': {'lt':20180916001872}})
    s_all  = doc.search(using=client,index=indexName)
    logger.logMessage("Collecting and saving documents from elasticsearch.")

    if filtered:
        logger.logMessage("Using filtered scan.")
        s = s_filt.scan()
    else:
        logger.logMessage("Using unfiltered scan.")
        s = s_all.scan()

    dumpFile = './dump-{0}.dmp'.format(indexName)
    duplicates = './duplicates-{0}.dat'.format(indexName)

    logger.logMessage('Dumping to file {0}'.format(dumpFile))
    fakeTSA = 1
    
    with open(dumpFile,'w') as f:
        num = 0
        for d in s:
            dic = d.to_dict()
            
            if not 'fwVersion' in dic:
                dic['fwVersion'] = '00.00.00'
            if dic['fwVersion'] < '02.00.00':
                if not 'version' in dic:
                    dic['version'] = '1.0.0'
                if not 'swVersion' in dic:
                    dic['swVersion'] = dic['version']
                for k in ['isThermometer','isBarometer','isClock','isHygrometer']:
                    dic[k] = True
                if not 'tsa' in dic:
                    dic['tsa'] = fakeTSA
                    fakeTSA += 1
            # logger.logMessage(dic,"DEBUG")
            with pgConn.cursor() as cur:
                try:
                    cur.execute(__INSERT_OBS__, dic)
                except KeyError:
                    logger.logMessage(level="ERROR",message="Wrong document: {0}".format(dic))
                    pgConn.rollback()
                    raise
                except pg.IntegrityError:
                    logger.logMessage(level="WARNING",message="TSA {0} is duplicated.".format(dic['tsa']))
                    with open(duplicates,'a') as d:
                        d.write('{0}\n'.format(dic))   
            f.write("{0}\n".format(dic))
            num += 1
            if num % 500 == 0:
                pgConn.commit()
                logger.logMessage(level="DEBUG",message="Saved {0} documents.".format(num))
        logger.logMessage("Document scan ended, {0} documents written.".format(num))
        pgConn.commit()
        

def getIndexes():
    catClient = escl.CatClient(client)
    allIndices = catClient.indices(index='weather-*',format='json')
    indices = [i for i in allIndices if i['status'] != 'close']
    indices.sort(key=lambda x: x['index'])
    names = [n['index'] for n in indices]
    return names



#client  = es.Elasticsearch(hostlist)
#indices = getIndexes()

        


#for doc in doclist:
    #wdb._logger.logMessage(level='DEBUG',message=
    # wdb.insertObs(doc)
