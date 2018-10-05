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
// Set (adjust) the time from a YYYMMDDhhmmss string
// There is no formal checking done. If the string is not correct the
// results are undefined.
//-
void MeteoClockSoft::setClock(String &timestamp) {
	uint16_t year  = atoi(timestamp.substring(0,4).c_str());
	uint8_t  month = atoi(timestamp.substring(4,6).c_str());
	uint8_t  day   = atoi(timestamp.substring(6,8).c_str());
	uint8_t  hour  = atoi(timestamp.substring(8,10).c_str());
	uint8_t  minute  = atoi(timestamp.substring(10,12).c_str());
	uint8_t  second  = atoi(timestamp.substring(12,14).c_str());

	this->setClock(year, month, day, hour, minute, second);
}

//+
// Set (adjust) the time using separate parameters for each
// date and time component.
// There is no formal checking done. If the combo is not correct the
// results are undefined.
//-

void MeteoClockSoft::setClock(int year, int month, int day,
		                 int hour, int minute, int second) {
	setTime(hour, minute, second, day, month, year);
}

//+
// Get the current date and time as a YYYYMMDDhhmmss string
//-
String MeteoClockSoft::getClock() {
	char timbuf[17];

	sprintf(timbuf, "%04d%02d%02d%02d%02d%02d", year(), month(), day(),
			                                    hour(), minute(), second());


	return String(timbuf);
}
