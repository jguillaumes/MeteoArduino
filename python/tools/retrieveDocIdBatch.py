#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 18 11:15:50 2018

@author: jguillaumes
"""

import os
import sys

import elasticsearch as es
import elasticsearch.helpers as eshelp
import psycopg2 as pg

tempFile   = 'temp-scan.dat'
tempSorted = 'temp-sorted.dat'
dbDumpFile = 'temp-dumpdb.dat'
matchFile  = 'temp-match.dat'
indexName  = 'weather-1.0.0-2018.03'
dateInterval = { 'start': '2018-03-01T00:00:00+00', 'end': '2018-03-31T23:59:59+00' }

host = 'ct01'
user = 'weather'
password = 'weather'
database = 'weather'
#hostlist = [ {'host:':'localhost', 'port':9200} ]
hostlist = [
        {'host':'elastic00','port':9200},
        {'host':'elastic01','port':9200},
        {'host':'elastic02','port':9200},
            ]


script_path = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir))
sys.path.append(script_path)

from weatherLib.weatherUtil import WLogger


logger = WLogger(loggerName='weather.tools')


def step010():
    """
    Dump the elasticsearch index into a file
    """
    client  = es.Elasticsearch(hostlist)
    search = { "_source": { "includes": ["time","tsa"]}, "query":{"exists":{"field":"tsa"}}}
    
    logger.logMessage('Begin: Getting documents from elasticsearch')
    
    result = eshelp.scan(client, query=search, index=indexName)
    
    numrecs = 0
    with open(tempFile,'w') as f:
        for hit in result:
            source = hit['_source']
            tsa   = source['tsa']
            time  = source['time']
            docid = hit['_id']
            f.write("{0:14d};{1:25s};{2:32s}\n".format(tsa,time,docid))
            numrecs += 1
            if numrecs % 1000 == 0:
                logger.logMessage(level='DEBUG',message="{0:9d} records written".format(numrecs))
        logger.logMessage("Total records: {0:d}".format(numrecs))
    
    result.close()
    logger.logMessage('End  : Getting documents from elasticsearch')

def step020():
    """
    Sort the elasticsearch file dump
    """
    logger.logMessage('Begin: Sorting records')
    sortCommand = 'sort {0} -n --key 1,15 -o {1}'.format(tempFile,tempSorted) 
    os.system(sortCommand)
    logger.logMessage('End:   Sorting records')

def step030():
    """
    Dump the rows from the postgresql table
    """
    logger.logMessage('Begin: get data from table')
    
    query = 'select tsa,time from weather ' +\
            'where time between %(start)s and %(end)s ' + \
                   'and esDocId is null ' + \
            'order by tsa;'
    
    pgConn  = pg.connect(host=host,user=user,password=password,database=database)    
    with pgConn:
        with pgConn.cursor() as c:
            c.execute(query,dateInterval)
            numrecs = 0
            with open(dbDumpFile,'w') as f:
                for row in c.fetchall():
                    tsa = row[0]
                    time= row[1].isoformat()
                    f.write('{0:14d};{1:25s}\n'.format(tsa,time))
                    numrecs += 1
                    if numrecs % 1000 == 0:
                        logger.logMessage(level='DEBUG',message="{0:9d} rows dumped".format(numrecs))
                logger.logMessage("Total rows: {0:d}".format(numrecs))
    
    logger.logMessage('End  : get data from table')

def step040():
    """
    Matching, db <-> elastic, db is master
    """
    logger.logMessage('Begin: matching work files')
    sKey = -1
    mKey = -1
    def readFile(f):
        line = f.readline().rstrip()
        if line == '':
            key = 99999999999999
            return None,key
        else:
            sp = line.split(';')
            key = int(sp[0])
            return sp,key

    m = open(dbDumpFile,'r')
    s = open(tempSorted,'r')
    numrecs = 0
    with open(matchFile,'w') as match:
        mFields,mKey = readFile(m)
        sFields,sKey = readFile(s)
        while mFields != None or sFields != None:
            if sKey == mKey:
                match.write('{0:14d};{1:32s}\n'.format(mKey,sFields[2]))
                numrecs += 1
                if numrecs % 1000 == 0:
                    logger.logMessage(level='DEBUG',message="{0:9d} records matched".format(numrecs))
                sFields,sKey = readFile(s)
                mFields,mKey = readFile(m)
            elif sKey < mKey:
                sFields,sKey = readFile(s)
            else:
                mFields,mKey = readFile(m)
        logger.logMessage("Total matched: {0:d}".format(numrecs))

    m.close()
    s.close()
    logger.logMessage('End: matching work files')

def step050():
    """
    Update the postgres database with document ids
    """
    logger.logMessage('Begin: updating database')
    update_sql = 'update weather set esDocId = $1 where tsa = $2;'
    pgConn  = pg.connect(host=host,user=user,password=password,database=database)    
    c = pgConn.cursor()
    c.execute('prepare updtDocid as {0}'.format(update_sql))
    numUpdates = 0
    with open(matchFile,'r') as f:
        line = f.readline().rstrip()
        while line != '':
            fields = line.split(';')
            tsa = int(fields[0])
            docid = fields[1]
            try:
                dic = { 'esDocId': docid, 'tsa': tsa }
                c.execute('execute updtDocid (%(esDocId)s,%(tsa)s)',dic)
                numUpdates += 1
                if numUpdates % 250 == 0:
                    pgConn.commit()
                    logger.logMessage(level='DEBUG',message="{0:9d} commited updates".format(numUpdates))
            except:
                logger.logException('Exception while updating database')
                pgConn.rollback()
                raise
            line = f.readline().rstrip()
    pgConn.commit()
    logger.logMessage("Total updates: {0:d}".format(numUpdates))
    c.close()
    pgConn.close()
    logger.logMessage('End  : updating database')




logger.logMessage("Starting...")
logger.setLevel("INFO")

step010()
step020()
step030()
step040()
logger.setLevel("DEBUG")
step050()

logger.logMessage("Finished")
