#ifndef _READ_TEMPERATURE_H
#define _READ_TEMPERATURE_H

#include <OneWire.h>

#define THERMOMETER_PIN		10
#define DS18B20				0x28
#define TH_START_CONVERSION	0x44
#define TH_READ_SCRATCHPAD	0xbe

int thInitialize(void);
float thRead(void);

#endif
