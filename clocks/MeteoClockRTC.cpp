/*
 * MeteoClockRTC.cpp
 *
 *  Created on: Sep 25, 2018
 *      Author: jguillaumes
 */

#include <Arduino.h>

#include "MeteoClockRTC.h"


MeteoClockRTC::~MeteoClockRTC() {
	RTC_DS3231 *rtc  = (RTC_DS3231 *) _theRTC;
	delete rtc;
	_theRTC = NULL;
}

//+
// Constructor: creates a new RTC_DS3231 instance and stores a pointer
// to it as a private variable.
// The variable is stored as a void pointer so the header file does not
// have to #include the RTClib.h. If it did there would be name conflicts
// with the software clock
//-
MeteoClockRTC::MeteoClockRTC() {
	RTC_DS3231 *rtc = new RTC_DS3231;
	this->_theRTC = (void *) rtc;
}

//+
// Enable output of square waves at 1Hz to trigger
// interrupts
//-
void MeteoClockRTC::enableInterrupt() {
	RTC_DS3231 *rtc = (RTC_DS3231 *) this->_theRTC;
	rtc->begin();
	rtc->writeSqwPinMode(DS3231_SquareWave1Hz);
}

//+
// Disable output of square waves
//-
void MeteoClockRTC::disableInterrupt() {
	RTC_DS3231 *rtc = (RTC_DS3231 *) this->_theRTC;
	rtc->begin();
	rtc->writeSqwPinMode(DS3231_OFF);
}


//+
// Set (adjust) the clock using separate parameters for each
// date and time component.
// There is no formal checking done. If the combo is not correct the
// results are undefined.
//-
void MeteoClockRTC::setClock(int year, int month, int day,
					  int hour, int minute, int second){
	DateTime dt(year, month, day, hour, minute, second);
	((RTC_DS3231 *) this->_theRTC)->adjust(dt);
}

//+
// Get the current date and time as a YYYYMMDDhhmmss string
//-
String MeteoClockRTC::getClock() {
	DateTime now;
	char timbuf[15];

	now = ((RTC_DS3231 *) this->_theRTC)->now();
	sprintf(timbuf, "%04d%02d%02d%02d%02d%02d", now.year(), now.month(), now.day(),
			                                    now.hour(), now.minute(), now.second());
	return String(timbuf);
}

DateTime MeteoClockRTC::getDateTime() {
	return ((RTC_DS3231 *)this)->now();
}

//+
// Verify if the clock is physically present on the 2WI bus
// responds with consistent results.
//-
bool MeteoClockRTC::checkClock() {
	bool rtcPresent;
	RTC_DS3231 *rtc = (RTC_DS3231 *) _theRTC;

	// rtc->begin();
	if (rtc->now().year() > 2100) {
		rtcPresent = false;
	} else {
		rtcPresent = true;
	}
	return rtcPresent;
}
