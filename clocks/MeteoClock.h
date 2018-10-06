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

struct CompTime {
	int year;
	int month;
	int day;
	int hour;
	int minute;
	int second;
};

class MeteoClock {
public:
	virtual ~MeteoClock() {}
	virtual void setClock(int year, int month, int day,
						  int hour, int minute, int second);
	virtual void setClock(struct CompTime &ct);
	virtual String getClock() = 0;
	virtual void setClock(const String &timestamp);

	static void parseTime(const char *, struct CompTime *);
	static void inline parseTime(const String &tim, struct CompTime *comp) {
		parseTime(tim.c_str(), comp);
	}
	static void printCT(struct CompTime &ct);
};

#endif /* METEOCLOCK_H_ */
