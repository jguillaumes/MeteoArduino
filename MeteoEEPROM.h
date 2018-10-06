/*
 * MeteoEEPROM.h
 *
 *  Created on: Oct 5, 2018
 *      Author: jguillaumes
 */

#ifndef METEOEEPROM_H_
#define METEOEEPROM_H_

#define _ME_ADDRESS 		0
#define _ME_ADDR_CRC        ((_ME_ADDRESS)+sizeof(struct EepromData))

#define _ME_CATCHER	        "WEATHER"
#define _ME_DEF_DEVNAME	    "WGIZMO00"
#define _ME_DEF_HWVERSION	"02.01.00"
#define _ME_DEF_POLLDELAY	5

#define _SIZ_CATCHER	8
#define _SIZ_DEVNAME	8
#define _SIZ_HWVERSION	8

struct EepromData {
	char eyecatcher[_SIZ_CATCHER+1];
	char devName[_SIZ_DEVNAME+1];
	char hwVersion[_SIZ_HWVERSION+1];
	int  pollDelay;
};

class MeteoEEPROM {
public:
	MeteoEEPROM();
	~MeteoEEPROM() {};
	void readEEPROM();
	void writeEEPROM();

	struct EepromData data;

private:
	// unsigned long eepromCRC();
	unsigned long _crc;
};

#endif /* METEOEEPROM_H_ */
