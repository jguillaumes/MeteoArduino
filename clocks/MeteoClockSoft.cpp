/*
 * MeteoClockSoft.cpp
 *
 *  Created on: Sep 25, 2018
 *      Author: jguillaumes
 */

#include <Arduino.h>
#include <Time.h>

#include "MeteoClockSoft.h"

//+
// Empty constructor
//-
MeteoClockSoft::MeteoClockSoft() {
}

//+
// Empty destructor
//-
MeteoClockSoft::~MeteoClockSoft() {
}


//+
// Set (adjust) the time using separate parameters for each
// date and time component.
// There is no formal checking done. If the combo is not correct the
// results are undefined.
//-

void MeteoClockSoft::setClock(int year, int month, int day,
		                 int hour, int minute, int second) {
	setTime(hour, minute, second, day, month, year); // @suppress("Invalid arguments")
}

//+
// Get the current date and time as a YYYYMMDDhhmmss string
//-
String MeteoClockSoft::getClock() {
	char timbuf[15];

	sprintf(timbuf, "%04d%02d%02d%02d%02d%02d", year(), month(), day(), 	 // @suppress("Invalid arguments")
			                                    hour(), minute(), second()); // @suppress("Invalid arguments")


	return String(timbuf);
}
