#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 10:35:03 2018

@author: jguillaumes
"""

import json
import elasticsearch_dsl as dsl
from elasticsearch.helpers import bulk
from datetime import date,timedelta

batchFileName = 'UpdateWeather.json'
es_host  = 'elastic00:9200'
srchDate =  date(2018,2,5)
oneDay   = timedelta(days=1)
srchDate1= srchDate + oneDay
serial = 0
numDay = srchDate.year * 10000 + srchDate.month * 100 + srchDate.day
numDay = numDay * 1000000
esconn = dsl.connections.create_connection(hosts=es_host, timeout=5)

batchFile = open(batchFileName,'w')

s = dsl.Search(index='weather-*').query("range", time={"gte": srchDate, "lt": srchDate1})\
       .sort('time')[0:25000]

batchList = []


for h in s.execute().hits:
#    print(h.meta.id)
    serial += 1
    newTsa = numDay + serial
    item = {
        '_index': h.meta.index,
        '_op_type': 'update',
        '_type': 'doc',

        '_id': h.meta.id,
        'doc': { 
            'tsa': newTsa
        }
    }
    doc = item['doc']
    doc['version'] = '1.0.0'
    doc['fwVersion'] = '01.00.00'
    batchFile.write(json.dumps(item))
    batchList.append(item)
    batchFile.write("\n")

batchFile.close()

ok, nok = bulk(client=esconn, actions=batchList, stats_only=True)

print("{0:d} entries updated OK, {1:d} failed".format(ok,nok))


esconn = None

