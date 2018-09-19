# -*- coding: utf-8 -*-

import os
import sys

import psycopg2 as pg
import elasticsearch as es
import elasticsearch.helpers as eshelp

import pandas as pd
import sqlalchemy as sql
import datetime as dt

script_path = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir))
sys.path.append(script_path)

from weatherLib.weatherUtil import WLogger

logger = WLogger(loggerName='weather.tools')
logger.logMessage("Starting...")

candidatesFile='/tmp/dupe-candidates.dat'
sortedCandidatesFile='/tmp/dupe-candidates-sorted.dat'
dbDumpFile='/tmp/dupe-dbdump.dat'
matchFile='/tmp/dupe-match.dat'
renumFile='/tmp/dupe-renum.dat'

indexName = 'weather-*'

host = 'ct01'
user = 'weather'
password = 'weather'
database = 'weather'
pgurl='postgres://weather:weather@localhost/weather'

hostlist = [
        {'host':'elastic00','port':9200},
        {'host':'elastic01','port':9200},
        {'host':'elastic02','port':9200},
            ]

def step010():
    """
    Build list of time intervals to query elasticSearch and
    perform query to get candidates
    """
    logger.logMessage('Begin: Getting candidate documents from elasticsearch')

    def limitHour(d):
        thish = d.start_time.tz_localize(tz='UTC')
        nexth = thish + dt.timedelta(hours=1)
        return { 'range': { 'time': {'gte':thish, 'lt':nexth } } }
        
    conn = sql.create_engine(pgurl)
    client = es.Elasticsearch(hostlist)
    dupesDF = pd.read_sql_table('weather_dupes',conn).set_index('time')
    hours =dupesDF.to_period('H').reset_index()['time'].unique()
    ranges = [ limitHour(h) for h in hours ]
    query = { 
        '_source': [ 'tsa','time' ],
        'query': { 
            'bool': { 'should': ranges } 
        } 
    }
    #logger.logMessage(level='DEBUG',message='Query body: {0}'.format(query))
    hits = eshelp.scan(client=client,index=indexName,doc_type='doc',query=query)
    numRecs = 0
    with open(candidatesFile,'w') as f:
        for h in hits:
            src = h['_source']
            tsa = int(src['tsa'])
            time = src['time']
            docid = h['_id']
            idx = h['_index']
            f.write(f'{tsa:014d};{time:25s};{docid:32s};{idx:32s}\n')        
            numRecs += 1
            if numRecs % 1000 == 0:
                logger.logMessage(level='DEBUG',message="{0:9d} records written".format(numRecs))
        logger.logMessage(message="{0:9d} total records written".format(numRecs))
    logger.logMessage('End: Getting candidate documents from elasticsearch')

def step020():
    """
    Sort the elasticsearch candidates (by time)
    """
    logger.logMessage('Begin: Sorting records')
    sortCommand = 'sort {0} -t \';\' --key 2 -o {1}'.format(candidatesFile,sortedCandidatesFile) 
    rc  = os.system(sortCommand)
    if rc != 0:
        raise Exception('Error returned by sort program: {0:d}'.format(rc))
    logger.logMessage('End  : Sorting records')

def step030():
    """
    Dump the rows from the postgresql table
    """
    logger.logMessage('Begin: get data from table')
    
    query = 'select tsa,time at time zone \'utc\' from weather_dupes ' + \
    'order by time;'
    
    pgConn  = pg.connect(host=host,user=user,password=password,database=database)    
    with pgConn:
        with pgConn.cursor() as c:
            c.execute(query)
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
    sKey = ''
    mKey = ''
    def readFile(f):
        line = f.readline().rstrip()
        if line == '':
            key = 'ZZZZZZZZZZZZZZZZZZZZZZZZZ'
            return None,key
        else:
            sp = line.split(';')
            key = '{0:25s}'.format(sp[1])[0:19]
            return sp,key

    m = open(dbDumpFile,'r')
    s = open(sortedCandidatesFile,'r')
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
                logger.logMessage(level='WARNING',message='Record not matched: {0}'.format(mFields))
                mFields,mKey = readFile(m)
        logger.logMessage("Total matched: {0:d}".format(numrecs))

    m.close()
    s.close()
    logger.logMessage('End  : matching work files')


def step050() -> None:
    """
    Renumber fake TSAs
    """
    logger.logMessage('Begin: Renumbering tsa')
    numRead = 0
    curDay = ''
    curNumDay = 0
    curFakeTsa = 900000
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
                    curFakeTsa = 900001
                theTsa = curNumDay * 1000000 + curFakeTsa
                w.write('{0:014d};{1:25s};{2:32s};{3:31s}\n'.format(theTsa, fields[1], fields[2],fields[3]))
                fields = readFile(f)
    logger.logMessage('Renumbered {0:d} records'.format(numRead))
    logger.logMessage('End: Renumbering tsa')

def step060():
    """
    Update the postgres database with tsas and document ids
    """
    logger.logMessage('Begin: updating database')
    update_sql = 'update weather_work set tsa=$1, esDocId = $2 where time = $3;'
    pgConn  = pg.connect(host=host,user=user,password=password,database=database)    
    c = pgConn.cursor()
#    c.execute('drop table weather_work')
#    c.execute('create table weather_work (like weather excluding constraints)')
#    c.execute('insert into weather_work select * from weather_dupes')
#    c.execute('create index weather_work_time on weather_work(time)')
    pgConn.commit()
    c.execute('prepare updtDocid as {0}'.format(update_sql))
    numUpdates = 0
    with open(renumFile,'r') as f:
        line = f.readline().rstrip()
        while line != '':
            fields = line.split(';')
            tsa  = int(fields[0])
            time = fields[1].rstrip() 
            docid = fields[2].rstrip()
            try:
                dic = { 'esDocId': docid, 'tsa': tsa , 'time': time+"+00:00" }
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

def step070() -> None:
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


#step010()
#step020()
#step030()
#step040()
#step050()
step060()
#step070()



