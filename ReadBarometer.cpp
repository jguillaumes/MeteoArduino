/*
 * ReadBarometer.cpp
 *
 *  Created on: Jan 19, 2018
 *      Author: jguillaumes
 */

#include "ReadBarometer.h"


// Declare Barometer for I2C connection (A4=>SCL, A5=>SDA)
Adafruit_BMP280 barometer;

int barInitialize() {
	if (!barometer.begin()) {
		Serial.println("No barometer found!");
		return 2;
	}
	return 0;
}

float barRead() {
	return barometer.readPressure() / 100.0;
}


