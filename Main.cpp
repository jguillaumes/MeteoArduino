#include "ReadTemperature.h"
#include "ReadHumidity.h"
#include "ReadBarometer.h"

void setup() {
	int rc=0;

	Serial.begin(9600);		// For debugging only
	rc = thInitialize();
	rc = higInitialize();
	rc = barInitialize();
	Serial.println("*** Init completed ***");
}


void loop() {
	float temp = thRead();
	Serial.print(" Temperature: ");
	Serial.print(temp);
	Serial.print(" C - ");

	float humidity = higRead();
	Serial.print(" Humidity: ");
	Serial.print(humidity);
	Serial.print("% - ");

	float pressure = barRead();
	Serial.print("Pressure: ");
	Serial.print(pressure);
	Serial.print("hPa ");

	Serial.println();
	delay(5000);
}
