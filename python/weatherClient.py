#!/usr/bin/python3

import bluetooth as bt
import time     
import sys
from weatherData import WeatherData
from datetime import datetime
from elasticsearch_dsl import connections
from elasticsearch import ConnectionTimeout

def saveData(conn, line):
    tokens = line.split(':')
    stamp=""
    temp=-999.0
    humt=-999.0
    pres=-999.0
    lght=-999.0
    for t in tokens:
        if t[0:1] == 'C':
            stamp = datetime.strptime(t[1:], '%Y%m%d%H%M%S')
        elif t[0:1] == 'T':
            temp = float(t[1:])
        elif t[0:1] == 'H':
            humt = float(t[1:])
        elif t[0:1] == 'P':
            pres = float(t[1:])
        elif t[0:1] == 'L':
            lght = float(t[1:])
    w = WeatherData()
    w.time = stamp
    w.temperature = temp
    w.humidity = humt
    w.pressure = pres
    w.light = lght
    w.save()       

w_address = "00:14:03:06:45:72"
w_service = "00001101-0000-1000-8000-00805f9b34fb"
es_hosts  = [ 'elastic00.jguillaumes.dyndns.org','elastic01.jguillaumes.dyndns.org']
file = "weather.dat"

srvlist = bt.find_service(uuid = w_service, address = w_address)
if len(srvlist) == 0:
    print("Weather service not found. Check the remote device.")
    sys.exit(8);

srv = srvlist[0]
port = srv["port"]
name = srv["name"]
host = srv["host"]

print("Weather service at \"%s\" on %s" % (name,host))

esConn = connections.create_connection(hosts=es_hosts,timeout=20)
print("Connection to elasticsearch cluster established.")
WeatherData.init()
WeatherData.create_template(esConn)


f = open(file, 'w')

sock=bt.BluetoothSocket(bt.RFCOMM)
sock.connect((host,port))

print("Connected to weather service.")

try:
    
    line = ""
    while True:
        byte = sock.recv(1)                   # Get byte from socket
        if byte == b'\r':                     # Carriage return?
            byte = sock.recv(1)               # Consume LF
            if byte != b'\n':                 # IF not LF, big trouble: discard line
                line = ""
            else:                             # We've got a good line.
                if line[0:4] == "DATA":       # It is a data line so...
                    f.write(line+'\n')        # ... write it!
                    f.flush()                 # Don't wait, write now!
                    try:
                        saveData(esConn,line) # Send to ES cluster
                    except ConnectionTimeout:
                        print("Error sending to ES: ", sys.exc_info()[0])
                        print("Datapoint lost: ", line)
                        pass
                else:
                    print("Non-data line: " + line)
                    if line[0:2] == "AT":     # First characters got after connection
                        now = time.gmtime()   # So send current time to set RTC...
                        cmd = "TIME " + time.strftime("%Y%m%d%H%M%S",now) + "\r"
                        print("Setting time, command: " + cmd)
                        sock.send(cmd)
                line = ""                     # Clear line to get next one
        else:
            line = line + byte.decode()       # Add character to current working line

except KeyboardInterrupt:
    print("Closing socket...")
    sock.send("BYE ")
    sock.close()

except:
    print("Exception: ", sys.exc_info()[0])
    print("Unexpected error, trying to close...")
    sock.send("BYE ")
    sock.close()
    raise
