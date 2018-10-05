/*
 * ReadBarometer.h
 *
 *  Created on: Jan 19, 2018
 *      Author: jguillaumes
 */

#ifndef READBAROMETER_H_
#define READBAROMETER_H_

#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BMP085_U.h>

int barInitialize(void);
float barRead(void);
float barTemp(void);

#endif /* READBAROMETER_H_ */
