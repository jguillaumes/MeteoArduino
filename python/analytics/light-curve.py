#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 25 23:15:00 2018

@author: jguillaumes
"""

import pandas as pd
import sqlalchemy as sql
from plotnine import ggplot,geom_line,aes

url = 'postgres://weather:weather@ct01.jguillaumes.dyndns.org/weather'

conn = sql.create_engine(url)

dades = pd.read_sql(con=conn,sql='select time at time zone \'utc\' as timestamp,light from weather order by time asc')

dades_idx = dades.set_index('timestamp')

m = dades_idx.to_period('D').groupby('timestamp').mean().reset_index()

m['timestamp'] = m.apply(lambda x: x[0].start_time, axis=1)

ggplot(m) + geom_line(aes(x='timestamp',y='light'))

