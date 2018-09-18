#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 18 11:15:50 2018

@author: jguillaumes
"""

import os
import sys

import datetime

import elasticsearch as es
import elasticsearch.helpers as eshelp
import psycopg2 as pg

tempFile   = 'temp-notsa-scan.dat'
tempSorted = 'temp-notsa-sorted.dat'
dbDumpFile = 'temp-notsa-dumpdb.dat'
matchFile  = 'temp-notsa-match.dat'
renumFile  = 'temp-notsa-renum.dat'
indexName  = 'weather-*'

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
    search = { "_source": { "includes": ["time","tsa"]}, "query":{"bool": {"must_not": {"exists":{"field":"tsa"}}}}}
    
    logger.logMessage('Begin: Getting documents from elasticsearch')
    
    result = eshelp.scan(client, query=search, index=indexName)
    
    numrecs = 0
    with open(tempFile,'w') as f:
        for hit in result:
            source = hit['_source']
            tsa   = 0
            time  = source['time']
            docid = hit['_id']
            idx = hit['_index']
            f.write("{0:014d};{1:25s};{2:32s};{3:31s}\n".format(tsa,time,docid,idx))
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
    sortCommand = 'sort {0} -n --key 1,15 --key 16,41 -o {1}'.format(tempFile,tempSorted) 
    rc  = os.system(sortCommand)
    if rc != 0:
        raise Exception('Error returned by sort program: {0:d}'.format(rc))
    logger.logMessage('End  : Sorting records')

def step030():
    """
    Dump the rows from the postgresql table
    """
    logger.logMessage('Begin: get data from table')
    
    query = 'select tsa,time from weather ' +\
            'where esDocId is null ' + \
            'order by time;'
    
    pgConn  = pg.connect(host=host,user=user,password=password,database=database)    
    with pgConn:
        with pgConn.cursor() as c:
            c.execute(query)
            numrecs = 0
            with open(dbDumpFile,'w') as f:
                for row in c.fetchall():
                    tsa = row[0]
#                    time= row[1].astimezone(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S%z')
                    time= row[1].astimezone(datetime.timezone.utc).isoformat()
                    f.write('{0:014d};{1:25s}\n'.format(tsa,time))
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
    sKey = ''
    mKey = ''
    def readFile(f):
        line = f.readline().rstrip()
        if line == '':
            key = 'ZZZZZZZZZZZZZZZZZZZZZZZZZ'
            return None,key
        else:
            sp = line.split(';')
            key = '{0:25s}'.format(sp[1])
            return sp,key

    m = open(dbDumpFile,'r')
    s = open(tempSorted,'r')
    numrecs = 0
    with open(matchFile,'w') as match:
        mFields,mKey = readFile(m)
        sFields,sKey = readFile(s)
        while mFields != None or sFields != None:
            if sKey == mKey:
                match.write('{0:014d};{1:25s};{2:32s};{3:31s}\n'.format(int(mFields[0]),mKey,sFields[2],sFields[3]))
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
    logger.logMessage('End  : matching work files')

def step045() -> None:
    """
    Renumber fake TSAs
    """
    logger.logMessage('Begin: Renumbering tsa')
    numRead = 0
    curDay = ''
    curNumDay = 0
    curFakeTsa = 800000
    theTsa = 0
    def readFile(f) -> []:
        nonlocal numRead
        line = f.readline().rstrip();
        if line != '':
            numRead += 1
            return line.split(';')
        else:
            return None
        
    with open(matchFile,'r') as f:
        with open(renumFile,'w') as w:
            fields = readFile(f)
            while fields != None:
                thisDay = fields[1][0:10]
                if thisDay == curDay:
                    curFakeTsa += 1
                else:
                    curDay = thisDay
                    curNumDay = int(curDay[0:4])*10000 + int(curDay[5:7])*100 + int(curDay[8:10])
                    curFakeTsa = 800001
                theTsa = curNumDay * 1000000 + curFakeTsa
                w.write('{0:014d};{1:25s};{2:32s};{3:31s}\n'.format(theTsa, fields[1], fields[2],fields[3]))
                fields = readFile(f)
    logger.logMessage('Renumbered {0:d} records'.format(numRead))
    logger.logMessage('End: Renumbering tsa')


def step050():
    """
    Update the postgres database with tsas and document ids
    """
    logger.logMessage('Begin: updating database')
    update_sql = 'update weather set tsa=$1, esDocId = $2 where time = $3;'
    pgConn  = pg.connect(host=host,user=user,password=password,database=database)    
    c = pgConn.cursor()
    c.execute('prepare updtDocid as {0}'.format(update_sql))
    numUpdates = 0
    with open(matchFile,'r') as f:
        line = f.readline().rstrip()
        while line != '':
            fields = line.split(';')
            tsa  = int(fields[0])
            time = fields[1] 
            docid = fields[2]
            try:
                dic = { 'esDocId': docid, 'tsa': tsa , 'time': time }
                c.execute('execute updtDocid (%(tsa)s,%(esDocId)s,%(time)s)',dic)
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

def step060() -> None:
    """
    Update the tsa of documents in elasticsearch
    """
    logger.logMessage('Begin: elasticsearch bulk update')
    client  = es.Elasticsearch(hostlist)

    def generate():
        with open(renumFile,'r') as f:
            line = f.readline().rstrip()
            while line != '':
                fields = line.split(';')
                oper = { '_index': fields[3], 
                        '_op_type': 'update',
                        '_id': fields[2].rstrip(),
                        '_type': 'doc',
                        '_source:': {'doc': {'tsa': fields[0]}}}
                
                yield oper
                line = f.readline().rstrip()
    result = eshelp.bulk(client,generate())
    logger.logMessage('Bulk result: {0}'.format(result))
    logger.logMessage('End  : elasticsearch bulk update')
    

logger.logMessage("Starting...")
#logger.setLevel("INFO")

step010()
step020()
step030()
step040()
step045()
logger.setLevel("DEBUG")
step050()
step060()

logger.logMessage("Finished")
