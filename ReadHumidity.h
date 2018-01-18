#ifndef _READ_HUMIDITY_H
#define _READ_HUMIDITY_H

#include "DHT.h"

#define HIGRO_PIN 		9
#define DHTTYPE			22

int higInitialize(void);
float higRead(void);

#endif
