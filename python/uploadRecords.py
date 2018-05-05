#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 26 16:06:51 2018

@author: jguillaumes
"""
import json
import elasticsearch_dsl as dsl
from weatherLib import parseLine,connect_wait_ES
from elasticsearch.helpers import bulk
from datetime import date,timedelta

es_hosts  = [ 'elastic00.jguillaumes.dyndns.org',\
              'elastic01.jguillaumes.dyndns.org',\
              'elastic02.jguillaumes.dyndns.org']

fileName = "weather-2018.04.04.dat"

with open(fileName) as file:
    for line in file:
        stamp,temp,humd,pres,light = parseLine(line)
        print(stamp,temp,humd,pres,light)


