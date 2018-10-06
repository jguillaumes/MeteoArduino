/*
 * MeteoMessages.h
 *
 *  Created on: Oct 6, 2018
 *      Author: jguillaumes
 */

#ifndef METEOMESSAGES_H_
#define METEOMESSAGES_H_

#include <avr/pgmspace.h>

#define	NUM_MESSAGES	15
	enum {
		CLOCKDET = 0,
		CLOCKLST = 1,
		THERMNOK = 2,
		HYGRONOK = 3,
		BAROMNOK = 4,
		THERMDET = 5,
		THERMLST = 6,
		BAROMDET = 7,
		BAROMLST = 8,
		HYGRODET = 9,
		HYGROLST = 10,
		TIMEREQS = 11,
		WATCHDOG = 12,
		COMNDTMO = 13,
		BEGINPGM = 14
	};

//                                   ....+....1....+....2....+....3....+....4....+....6...
	const char PROGMEM MCLOCKDET[] = "HARDW: Clock detected";
	const char PROGMEM MCLOCKLST[] = "HARDW: Clock lost!! - Using software timekeeping";
	const char PROGMEM MTHERMNOK[] = "HARDW: Thermometer not initialized.";
	const char PROGMEM MHYGRONOK[] = "HARDW: Hygrometer not initialized.";
	const char PROGMEM MBAROMNOK[] = "HARDW: Barometer not initialized.";
	const char PROGMEM MTHERMDET[] = "HARDW: Thermometer detected.";
	const char PROGMEM MTHERMLST[] = "HARDW: Thermometer lost.";
	const char PROGMEM MBAROMDET[] = "HARDW: Barometer detected.";
	const char PROGMEM MBAROMLST[] = "HARDW: Barometer lost.";
	const char PROGMEM MHYGRODET[] = "HARDW: Hygrometer detected.";
	const char PROGMEM MHYGROLST[] = "HARDW: Hygrometer lost.";
	const char PROGMEM MTIMEREQS[] = "TIME?";
	const char PROGMEM MWATCHDOG[] = "CRIT : Watchdog triggered, continuing...";
	const char PROGMEM MCOMNDTMO[] = "ERROR: Timeout reading command, input ignored";
	const char PROGMEM MBEGINPGM[] = "BEGIN:";


class MeteoMessages {
public:
	MeteoMessages() {}
	virtual ~MeteoMessages() {};

	void getMessage(int num, char *buff) {
		strcpy_P(buff, messageTable[num]);
	}
private:

	const char * messageTable[NUM_MESSAGES] = { MCLOCKDET, MCLOCKLST,
	                                            MTHERMNOK, MHYGRONOK,
												MBAROMNOK,
												MTHERMDET, MTHERMLST,
	                                            MBAROMDET, MBAROMLST,
	                                            MHYGRODET, MHYGROLST,
	                                            MTIMEREQS, MWATCHDOG,
	                                            MCOMNDTMO, MBEGINPGM };
};

#endif /* METEOMESSAGES_H_ */
