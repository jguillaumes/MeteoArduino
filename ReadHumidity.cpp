
#include "ReadHumidity.h"

DHT dht(HIGRO_PIN, DHTTYPE);

int higInitialize() {

	pinMode(HIGRO_PIN, INPUT);
	dht.begin();
	return(0);
}

float higRead() {
	// float t = dht.readTemperature(0);
	// Serial.print("T2:"); Serial.println(t);
	float h = dht.readHumidity();
	if (isnan(h)) h = -999.00;
	return h;
}
