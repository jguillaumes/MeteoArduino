#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  4 13:57:49 2018

@author: jguillaumes
"""

import weatherLib as wl
import sys

tracebacks = True

def exception_handler(exception_type, exception, traceback, debug_hook=sys.excepthook):
    if tracebacks:
        debug_hook(exception_type, exception, traceback)
    else:
        print ("%s: %s" % (exception_type.__name__, exception))


sys.excepthook = exception_handler

#es_hosts  = [ 'elastic00.jguillaumes.dyndns.org','elastic01.jguillaumes.dyndns.org','elastic02.jguillaumes.dyndns.org']

es_hosts = ['localhost']
conn = wl.connect_wait_ES(hostlist=es_hosts)

testfile = open('weather0.dat', 'r')

for line in testfile:
    wl.saveData(conn=conn, line=line)
    
