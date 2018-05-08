#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 26 16:06:51 2018

@author: jguillaumes
"""
import json
import elasticsearch_dsl as dsl
from weatherLib import parseLine,connect_wait_ES,WeatherData,VERSION,FW_VERSION,SW_VERSION
from elasticsearch.helpers import bulk
from datetime import date,datetime,timedelta

es_hosts  = [ 'elastic00.jguillaumes.dyndns.org',\
              'elastic01.jguillaumes.dyndns.org',\
              'elastic02.jguillaumes.dyndns.org']

fileName = "weather-2018.04.04.dat"
bulkFile = 'bulk-insert.json'
numdocs = 0
curindex = None

with open(bulkFile,'w') as outfile:
    with open(fileName) as file:
        numtsa = 1
        for line in file:
            stamp,temp,humd,pres,light = parseLine(line)
            # print(stamp,temp,humd,pres,light)

            tsa = stamp.year * 10000 + stamp.month * 100 + stamp.day
            tsa = tsa * 1000000 + numtsa
            numtsa += 1

            index = {
                'index': {
                    '_index': "weather-" + VERSION + "-" + stamp.strftime("%Y.%m.%d"),
                    '_type': "doc"
                }
            }

            w = WeatherData()
            w.time = stamp.isoformat()
            w.temperature = temp
            w.humidity = humd
            w.pressure = pres
            w.light = light
            w.version = VERSION
            w.fwVersion = FW_VERSION
            w.swVersion = SW_VERSION
            w.tsa = tsa

            json.dump(index,outfile)
            print("\r",file=outfile)

            json.dump(w.to_dict(),outfile)
            print("\r",file=outfile)
            numdocs += 1
outfile.close()
print("Generated {0:d} documents.".format(numdocs))
