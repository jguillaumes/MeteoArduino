/*
 * MeteoClockRTC.h
 *
 * Clock handling based on an DS3231 RTC chip.
 *
 *  Created on: Sep 25, 2018
 *      Author: jguillaumes
 */

#ifndef METEOCLOCKRTC_H_
#define METEOCLOCKRTC_H_
#include <RTCLib.h>

#include "Arduino.h"
#include "MeteoClock.h"


class MeteoClockRTC: public MeteoClock {

public:
	using MeteoClock::setClock;

	virtual ~MeteoClockRTC();
	MeteoClockRTC();

	virtual void setClock(int year, int month, int day,
						  int hour, int minute, int second);
	virtual String getClock();
	DateTime getDateTime();

	void enableInterrupt();
	void disableInterrupt();
	bool checkClock();

private:
	void *_theRTC; // Pointer to a RTC_DS3231 object, stored as void*
	               // to avoid having to include the RTClib header

};

#endif /* METEOCLOCKRTC_H_ */
