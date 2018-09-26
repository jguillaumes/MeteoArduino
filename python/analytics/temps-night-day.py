#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 26 08:42:58 2018

@author: jguillaumes
"""

import pandas as pd
import sqlalchemy as sql
from plotnine import *

url   = 'postgres://weather:weather@ct01.jguillaumes.dyndns.org/weather'
query = 'select time at time zone \'utc\' as timestamp, temperature, light > 50 as daytime from weather order by time'
 
conn = sql.create_engine(url)

dades = pd.read_sql(con=conn,sql=query)

daylies = dades.set_index('timestamp').to_period('D').groupby(['timestamp','daytime']).mean().reset_index()

daylies['timestamp'] = daylies.apply(lambda x: x[0].start_time, axis=1)
daylies['daytime'] = daylies.apply(lambda x: 'Day' if x[1] else 'Night',axis=1)


flattemps = daylies.pivot(index='timestamp',columns='daytime',values='temperature').dropna().reset_index()
flattemps['Difference'] = flattemps.apply(lambda x: x[1] - x[2],axis=1)

dailies = flattemps.set_index('timestamp').stack().reset_index()
dailies.columns=['day','time','temperature']

ggplot(dailies) + geom_point(aes(x='day',y='temperature',color='time')) + 
