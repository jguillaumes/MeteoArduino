/*
 * ReadBarometer.cpp
 *
 *  Created on: Jan 19, 2018
 *      Author: jguillaumes
 */

#include "ReadBarometer.h"

static boolean barOK = false;


// Declare Barometer for I2C connection (A4=>SCL, A5=>SDA)
Adafruit_BMP280 barometer;

int barInitialize() {
	if (!barometer.begin()) {
		barOK = false;
		return 2;
	} else {
		barOK = true;
	}
	return 0;
}

float barRead() {
	if (!barOK) {
		if (!barometer.begin()) {
			return -999.00;
		}
	}
	return barometer.readPressure() / 100.0;
}


