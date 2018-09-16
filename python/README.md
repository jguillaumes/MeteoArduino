# Python client application
This application listens to the information transmitted by the gizmo (via BlueTooth) and processes it. Currently it:

- Stores the raw data line into a text file
- Sends the collected data to a ElasticSearch cluster

It also sets the date in the gizmo from the computer where it is executing.

## Required python environment

This scripts require Python version 3. They require the following python modules to be installed:

- pybluez
- pytz
- elasticsearch
- elasticsearch-dsl
- psycopg2
- sqlite3


