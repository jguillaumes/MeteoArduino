#include "ReadTemperature.h"
#include "ReadHumidity.h"

void setup() {
	int rc=0;

	Serial.begin(9600);		// For debugging only
	rc = thInitialize();
	rc = higInitialize();
}


void loop() {
	float temp = thRead();
	Serial.print(" Temperature: ");
	Serial.print(temp);
	Serial.print(" C - ");

	float humidity = higRead();
	Serial.print(" Humidity: ");
	Serial.print(humidity);

	Serial.println();
	delay(5000);
}
