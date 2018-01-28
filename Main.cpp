#include <Arduino.h>

#include "RTClib.h"

#include "ReadTemperature.h"
#include "ReadHumidity.h"
#include "ReadBarometer.h"
#include "BTComms.h"

RTC_DS3231 rtc;



void setup() {
	int rc=0;

	Serial.begin(9600);		// For debugging only

	rc = commInitialize();
	if (rc != 0) Serial.println("Bluetooth commns not initialized.");

	rc = thInitialize();
	if (rc != 0) Serial.println("Thermometer not initialized.");

	rc = higInitialize();
	if (rc != 0) Serial.println("Hygrometer not initialized.");

	rc = barInitialize();
	if (rc != 0) Serial.println("Barometer not initialized.");

	rc =  rtc.begin();
	if (rc != 0) Serial.println("RTC not found.");

	Serial.println("*** Init completed ***");
}


void loop() {
	char timbuf[17];
	DateTime now = rtc.now();
	sprintf(timbuf, "%04d%02d%02d%02d%02d%02d", now.year(), now.month(), now.day(),
			                                        now.hour(), now.minute(), now.second());

	Serial.print("DATA");
	Serial.print(timbuf);
	Serial.print(":");

	float temp = thRead();
	Serial.print("T");
	Serial.print(temp);
	Serial.print(":");

	float humidity = higRead();
	Serial.print("H");
	Serial.print(humidity);
	Serial.print(":");

	float pressure = barRead();
	Serial.print("P");
	Serial.print(pressure);
	Serial.print(":");

	Serial.println();
	delay(5000);
}
