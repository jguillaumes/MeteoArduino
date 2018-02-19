#ifndef _READ_HUMIDITY_H
#define _READ_HUMIDITY_H

#include <Arduino.h>
#include "dht.h"

#define DHT22_PIN  		8

int higInitialize(void);
float higRead(void);
float higTemp(void);
#endif
