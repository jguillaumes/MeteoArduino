
#include "ReadHumidity.h"

dht hig;

int higInitialize() {

	return(0);
}

float higRead() {
	float h = -999.00;

	int chk = hig.read(DHT22_PIN);
	if (chk == DHTLIB_OK) {
		h = hig.humidity;
	}
	return h;
}

float higTemp() {
	float t = -999.00;

	int chk = hig.read(DHT22_PIN);
	if (chk == DHTLIB_OK) {
		t = hig.temperature;
	}
	return t;
}

