/*
 * MeteoClock.h
 *
 * Abstract class to represent clock devices.
 * It defines the basic operations of clocks. There will be
 * implementations based on RTC (DS3231) and software timing.
 *
 *  Created on: Sep 25, 2018
 *      Author: jguillaumes
 *
 */

#ifndef METEOCLOCK_H_
#define METEOCLOCK_H_

#include <Arduino.h>


class MeteoClock {
public:
	virtual ~MeteoClock() {}
	virtual void setClock(String &timestamp) = 0;
	virtual void setClock(int year, int month, int day,
						  int hour, int minute, int second) = 0;

	virtual String getClock() = 0;
};

#endif /* METEOCLOCK_H_ */
