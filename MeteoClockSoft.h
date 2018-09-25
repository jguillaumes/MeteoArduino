/*
 * MeteoClockSoft.h
 *
 * Clock handling based on software timekeeping
 *
 *  Created on: Sep 25, 2018
 *      Author: jguillaumes
 */

#ifndef METEOCLOCKSOFT_H_
#define METEOCLOCKSOFT_H_

#include "MeteoClock.h"

class MeteoClockSoft: public MeteoClock {
public:
	MeteoClockSoft();
	virtual ~MeteoClockSoft();

	virtual void setClock(String &timestamp) ;
	virtual void setClock(int year, int month, int day,
						  int hour, int minute, int second) ;
	virtual String getClock();

};

#endif /* METEOCLOCKSOFT_H_ */
