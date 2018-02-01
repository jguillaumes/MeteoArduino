#include <Arduino.h>

#include "RTClib.h"

#include "ReadTemperature.h"
#include "ReadHumidity.h"
#include "ReadBarometer.h"
#include "ReadLight.h"
#include "SDLogger.h"
#include "HC06Module.h"


RTC_DS3231 rtc;
SDLogger logger(80,10);
HC06Module bt(3,2);


void setup() {
	int rc=0;

	Serial.begin(9600);		// For debugging only
	bt.begin();				// Startup BT

	rc = thInitialize();
	if (rc != 0) Serial.println("Thermometer not initialized.");

	rc = higInitialize();
	if (rc != 0) Serial.println("Hygrometer not initialized.");

	rc = barInitialize();
	if (rc != 0) Serial.println("Barometer not initialized.");

	rc = lightInitialize();

	rc =  rtc.begin();

	if (!logger.isOk()) {
		Serial.println("Logger not ready");
		Serial.println(logger.getMessage());
	} else {
		if (!logger.newFile("WEATHER.DAT")) {
			logger.oldFile("WEATHER.DAT");
		}
	}

	Serial.println("*** Init completed ***");
}

void processCommand(String cmd) {
	bool cmdOk = false;

	String theCmd = cmd.substring(0,4);
	if (theCmd.equals("TIME")) {
		DateTime dt(atoi(cmd.substring(5,9).c_str()),
				    atoi(cmd.substring(9,11).c_str()),
				    atoi(cmd.substring(11,13).c_str()),
				    atoi(cmd.substring(13,15).c_str()),
				    atoi(cmd.substring(15,17).c_str()),
				    atoi(cmd.substring(17,19).c_str()));
		rtc.adjust(dt);
		cmdOk = true;
	} else if (theCmd.equals("BYE ")) {
		bt.writeLine("OK-BYE");
		cmdOk = true;
		for (int i=0; i<5 && bt.isConnected(); i++) {
			bt.checkConnection();
		}
		if (bt.isConnected()) {
			bt.writeLine("KO-ONL");
		}
		return;
	}

	if (cmdOk) {
		bt.writeLine("OK-000");
	} else {
		bt.writeLine("KO-UNK [" + theCmd + "]" );
	}
}

//  TIME 20180131220000
//  BYE

void loop() {
	char timbuf[17];
	char line[80];
	DateTime now = rtc.now();
	sprintf(timbuf, "%04d%02d%02d%02d%02d%02d", now.year(), now.month(), now.day(),
			                                        now.hour(), now.minute(), now.second());
	char stemp[10], shumt[10], spres[10], slght[10];

	dtostrf(thRead(), 5, 2, stemp);
	dtostrf(higRead(), 5, 2, shumt);
	dtostrf(barRead(), 6, 2, spres);
	dtostrf(lightRead(), 6, 2, slght);

	sprintf(line, "DATA:C%s:T%s:H%s:P%s:L%s", timbuf, stemp, shumt, spres, slght);
	Serial.println(line);

	if (bt.isConnected()) {
		for (unsigned int i=0; i<strlen(line); i++) {
			bt.writeByte(line[i]);
		}
		bt.writeLine("");
		String cmd = bt.readLine();
		if (cmd.length() != 0) processCommand(cmd);
	} else {
		bt.checkConnection();
	}

	if (logger.isOk()) {
		logger.append((byte *) line, strlen(line));
		logger.flush();
	}

	delay(5000);
}
