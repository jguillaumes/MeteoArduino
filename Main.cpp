#include <Arduino.h>

#define DEBUG

#include "RTClib.h"
#include "ReadTemperature.h"
#include "ReadHumidity.h"
#include "ReadBarometer.h"
#include "ReadLight.h"
// #include "SDLogger.h"
#include "HC06Module.h"

#ifdef DEBUG
const int pollDelay=5000;
#else
const int pollDelay=15000;
#endif

#define FWVERSION "01.00.00"

RTC_DS3231 rtc;
// SDLogger logger(80,10);
HC06Module bt(3,2);



bool firstConnection = true;

void setup() {
	int rc=0;

#ifdef DEBUG
	Serial.begin(9600);		// For debugging only
	char msg[80];
	sprintf(msg, "CPU clock: %ld", F_CPU);
	Serial.println(msg);
#endif

	bt.begin();				// Startup BT

	rc = thInitialize();
#ifdef DEBUG
	if (rc != 0) Serial.println("Thermometer not initialized.");
#endif

	rc = higInitialize();
#ifdef DEBUG
	if (rc != 0) Serial.println("Hygrometer not initialized.");
#endif

	rc = barInitialize();
#ifdef DEBUG
	if (rc != 0) Serial.println("Barometer not initialized.");
#endif

	rc = lightInitialize();

	rc =  rtc.begin();

	/* --
	if (!logger.isOk()) {
		Serial.println("Logger not ready");
		Serial.println(logger.getMessage());
	} else {
		if (!logger.newFile("WEATHER.DAT")) {
			logger.oldFile("WEATHER.DAT");
		}
	}
	-- */
	// Serial.println("*** Init completed ***");
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
	float temp;
	DateTime now = rtc.now();
	sprintf(timbuf, "%04d%02d%02d%02d%02d%02d", now.year(), now.month(), now.day(),
			                                        now.hour(), now.minute(), now.second());
	char stemp[10], shumt[10], spres[10], slght[10];

	temp = thRead();
	if (temp==-999.00) {		// No thermometre?
		temp = barTemp();		// Try BMP180
		if (temp==-999.00) {	// No BMP180?
			temp = higTemp();	// Try DHT22
		}
	}
	dtostrf(temp, 5, 2, stemp);
	dtostrf(higRead(), 5, 2, shumt);
	dtostrf(barRead(), 6, 2, spres);
	dtostrf(lightRead(), 6, 2, slght);

	sprintf(line, "DATA:C%s:F%s:T%s:H%s:P%s:L%s", timbuf, FWVERSION, stemp, shumt, spres, slght);

#ifdef DEBUG
	Serial.println(line);
#endif

	if (bt.isConnected()) {
		if (firstConnection) {
			char buff[64];
			sprintf(buff, "FVER %s", FWVERSION);
			for(unsigned int i=0; i<strlen(buff); i++) {
				bt.writeByte(buff[i]);
			}
			bt.writeLine("");
			firstConnection = false;
		}
		for (unsigned int i=0; i<strlen(line); i++) {
			bt.writeByte(line[i]);
		}
		bt.writeLine("");
		String cmd = bt.readLine();
		if (cmd.length() != 0) processCommand(cmd);
	} else {
		bt.checkConnection();
	}

	// if (logger.isOk()) {
	// 	logger.append((byte *) line, strlen(line));
	// 	logger.flush();
	// }

	delay(pollDelay);
}
