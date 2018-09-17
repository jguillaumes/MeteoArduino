#include <Arduino.h>

#define DEBUG 1

#include "RTClib.h"
#include "Time.h"
#include "ReadTemperature.h"
#include "ReadHumidity.h"
#include "ReadBarometer.h"
#include "ReadLight.h"
#include "HC05Module.h"

#ifdef DEBUG
const int pollDelay=5000;
#else
const int pollDelay=15000;
#endif

#define FWVERSION "02.00.01"

RTC_DS3231 rtc;
HC05Module bt(2);

bool firstConnection = true;
bool rtcPresent = false;
enum deviceEnum { DE_CLOCK=0, DE_THERMOMETER=1, DE_HIGROMETER=2,
	              DE_BAROMETER=3, DE_LIGHT=4 };
char devList[] = "     ";

void checkClock() {
	rtc.begin();
	if (rtc.now().year() > 2100) {
		rtcPresent = false;
		devList[DE_CLOCK] = '-';
	} else {
		rtcPresent = true;
		devList[DE_CLOCK] = 'C';
	}
}

void setup() {
	int rc=0;
	char msg[80];

	while (!bt.begin()) {
		Serial.println("ERROR: No BT connection");
	}

	Serial.println("");

#ifdef DEBUG
	sprintf(msg, "DEBUG: CPU clock: %ld", F_CPU);
	Serial.println(msg);
#endif

	rc = thPrepare();
	if (rc != 0) {
		Serial.println("HARDW: Thermometer not initialized.");
		devList[DE_THERMOMETER] = '-';
	} else {
		devList[DE_THERMOMETER] = 'T';
	}
	rc = higInitialize();
	if (rc != 0) {
		Serial.println("HARDW: Hygrometer not initialized.");
		devList[DE_HIGROMETER] = '-';
	} else {
		devList[DE_HIGROMETER] = 'H';
	}

	rc = barInitialize();
	if (rc != 0) {
		Serial.println("HARDW: Barometer not initialized.");
		devList[DE_BAROMETER] = '-';
	} else {
		devList[DE_BAROMETER] = 'P';
	}

	rc = lightInitialize();
	devList[DE_LIGHT] = 'L';

	checkClock();
	if (!rtcPresent) {
		Serial.println("ERROR: RTC not present");
	} else {
		DateTime ara = rtc.now();
		setTime(ara.hour(), ara.minute(), ara.second(),
				ara.day(), ara.month(), ara.year());
	}

	sprintf(msg, "INFO : F:%s", FWVERSION);
	Serial.println(msg);
}

void processCommand(String cmd) {
	bool cmdOk = false;

	String theCmd = cmd.substring(0,5);
	if (theCmd.equals("TIME ")) {
		if (rtcPresent) {
			DateTime dt(atoi(cmd.substring(5,9).c_str()),
					    atoi(cmd.substring(9,11).c_str()),
					    atoi(cmd.substring(11,13).c_str()),
					    atoi(cmd.substring(13,15).c_str()),
					    atoi(cmd.substring(15,17).c_str()),
					    atoi(cmd.substring(17,19).c_str()));
			rtc.adjust(dt);
		} else {
			setTime(atoi(cmd.substring(13,15).c_str()),
					atoi(cmd.substring(15,17).c_str()),
					atoi(cmd.substring(17,19).c_str()),
					atoi(cmd.substring(11,13).c_str()),
					atoi(cmd.substring(9,11).c_str()),
					atoi(cmd.substring(5,9).c_str()));
			checkClock();
			if (rtcPresent) Serial.println("HARDW: Clock detected");
		}
		cmdOk = true;
	} else if (theCmd.equals("BYE  ")) {
		Serial.println("OK-BYE");
		cmdOk = true;
		for (int i=0; i<5 && bt.checkConnection(); i++) delay(1000);
		if (bt.checkConnection()) {
			Serial.println("KO-ONL");
		} else {
			firstConnection = true;
		}
		return;
	} else if (theCmd.equals("INFO ")) {
		char buff[80];
		sprintf(buff,"INFO F:%s", FWVERSION);
		Serial.println(buff);
		cmdOk = true;
	}

	if (cmdOk) {
		Serial.println("OK-000");
	} else {
		Serial.println("KO-UNK [" + theCmd + "]" );
	}
}

//  TIME 20180220221700
//  BYE

void loop() {
	DateTime now;
	char timbuf[17];
	char line[80];
	float temp, press, humdt, light;

	// If we have an RTC, check it's still working. If not, switch to MPU soft clock
	if (rtcPresent) {
		checkClock();
		if (rtcPresent) {
			now = rtc.now();
			sprintf(timbuf, "%04d%02d%02d%02d%02d%02d", now.year(), now.month(), now.day(),
														now.hour(), now.minute(), now.second());
		} else {
			Serial.println("HARDW: Clock lost!! - Using software timer");
		}
	}

	// If we've got no RTC, use software clock and check if it has came back
	if (!rtcPresent) {
		sprintf(timbuf, "%04d%02d%02d%02d%02d%02d", year(), month(), day(),
				                                    hour(), minute(), second());
		checkClock();
		if (rtcPresent) Serial.println("HARDW: Clock detected");
	}
	char stemp[10], shumt[10], spres[10], slght[10];

	temp = thRead();
	press = barRead();
	humdt = higRead();
	light = lightRead();

	if (temp==-999.00) {		// No thermometre?
		temp = barTemp();		// Try BMP180
		if (temp==-999.00) {	// No BMP180?
			temp = higTemp();	// Try DHT22
		}
		if (devList[DE_THERMOMETER] == 'T') {
			Serial.println("HARDW: Thermometer lost");
			devList[DE_THERMOMETER] = '-';
		}
	} else {
		if (devList[DE_THERMOMETER] == '-') {
			Serial.println("HARDW: Thermometer detected");
			devList[DE_THERMOMETER] = 'T';
		}
	}

	if (press == -999.00) {
		if (devList[DE_BAROMETER] == 'P') {
			Serial.println("HARDW: Barometer lost");
			devList[DE_BAROMETER] = '-';
		}
	} else {
		if (devList[DE_BAROMETER] == '-') {
			Serial.println("HARDW: Barometer detected");
			devList[DE_BAROMETER] = 'P';
		}
	}

	if (humdt == -999.00) {
		if (devList[DE_HIGROMETER] == 'H') {
			Serial.println("HARDW: Higrometer lost");
			devList[DE_HIGROMETER] = '-';
		}
	} else {
		if (devList[DE_HIGROMETER] == '-') {
			Serial.println("HARDW: Higrometer detected");
			devList[DE_HIGROMETER] = 'H';
		}
	}

	dtostrf(temp, 5, 2, stemp);
	dtostrf(press, 6, 2, spres);
	dtostrf(humdt, 5, 2, shumt);
	dtostrf(light, 6, 2, slght);

	sprintf(line, "DATA :C%s:F%s:T%s:H%s:P%s:L%s:D%s", timbuf, FWVERSION, stemp,
			shumt, spres, slght, devList);

	if (bt.checkConnection()) {
		if (firstConnection) {
			Serial.println("BEGIN:");
			firstConnection = false;
		}
		Serial.println(line);
		String cmd = Serial.readString();
		if (cmd.length() != 0) processCommand(cmd);
	}

	delay(pollDelay);
}
