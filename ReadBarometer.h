/*
 * ReadBarometer.h
 *
 *  Created on: Jan 19, 2018
 *      Author: jguillaumes
 */

#ifndef READBAROMETER_H_
#define READBAROMETER_H_

#include <Adafruit_BMP280.h>

int barInitialize(void);
float barRead(void);




#endif /* READBAROMETER_H_ */
