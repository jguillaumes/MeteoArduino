/*
 * ReadBarometer.cpp
 *
 *  Created on: Jan 19, 2018
 *      Author: jguillaumes
 */

#include "ReadBarometer.h"

static boolean barOK = false;


// Declare Barometer for I2C connection (A4=>SCL, A5=>SDA)
Adafruit_BMP085_Unified barometer = Adafruit_BMP085_Unified(18000);

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

	sensors_event_t event;
	barometer.getEvent(&event);
	if (event.pressure) {
		return event.pressure;
	} else {
		return -999.00;
	}
}

float barTemp() {
	float temperature = 0;
	if (!barOK) {
		if (!barometer.begin()) {
			return -999.00;
		}
	}
	barometer.getTemperature(&temperature);
	return temperature;
}
