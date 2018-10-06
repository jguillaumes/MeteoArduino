/*
 * MeteoEEPROM.cpp
 *
 *  Created on: Oct 5, 2018
 *      Author: jguillaumes
 */

#include <string.h>
#include <Arduino.h>
#include <EEPROM.h>

#include "MeteoEEPROM.h"

MeteoEEPROM::MeteoEEPROM() {
//	memset(&data, 0, sizeof(struct EepromData));
//	strncpy(data.eyecatcher, _ME_CATCHER, _SIZ_CATCHER);
//	_crc = 0;
}

/*
unsigned long MeteoEEPROM::eepromCRC() {
	//return 1;
	const unsigned long crc_table[16] = {
			0x00000000, 0x1db71064, 0x3b6e20c8, 0x26d930ac,
			0x76dc4190, 0x6b6b51f4, 0x4db26158, 0x5005713c,
			0xedb88320, 0xf00f9344, 0xd6d6a3e8, 0xcb61b38c,
			0x9b64c2b0, 0x86d3d2d4, 0xa00ae278, 0xbdbdf21c
	};

	unsigned long crc = ~0L;

	for (unsigned int index = 0 ; index < sizeof(struct EepromData)  ; ++index) {
		crc = crc_table[(crc ^ EEPROM[index]) & 0x0f] ^ (crc >> 4);
		crc = crc_table[(crc ^ (EEPROM[index] >> 4)) & 0x0f] ^ (crc >> 4);
		crc = ~crc;
	}
	return crc;
}
*/

void MeteoEEPROM::readEEPROM() {
	// unsigned long crc=0;
	struct EepromData d;
	byte *ptr = (byte *) &d;

//	for (unsigned int i=0; i<sizeof(d); i++) {
//		*(ptr++) = EEPROM.read(_ME_ADDRESS+i);
//	}

	EEPROM.get(_ME_ADDRESS, d);
	if (strcmp(d.eyecatcher, _ME_CATCHER)!=0) {
		Serial.println("INFO: Initializing EEPROM");
		strncpy(data.eyecatcher,_ME_CATCHER, _SIZ_CATCHER+1);
		strncpy(data.devName,   _ME_DEF_DEVNAME, _SIZ_DEVNAME+1);
		strncpy(data.hwVersion, _ME_DEF_HWVERSION, _SIZ_HWVERSION+1);
		data.pollDelay = _ME_DEF_POLLDELAY;
		writeEEPROM();
	} else {
		memcpy(&data, &d, sizeof(struct EepromData));
	}
}

void MeteoEEPROM::writeEEPROM() {
	EEPROM.put(_ME_ADDRESS, data);
}
