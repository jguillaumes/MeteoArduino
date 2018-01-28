#ifndef _READ_HUMIDITY_H
#define _READ_HUMIDITY_H

#include <Arduino.h>
#include "DHT.h"

#define HIGRO_PIN 		A6
#define DHTTYPE			22

int higInitialize(void);
float higRead(void);

#endif
