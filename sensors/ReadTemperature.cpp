#include "ReadTemperature.h"

OneWire thermometer(THERMOMETER_PIN);			// Thermometer OneWire handler
byte th_addr[8];								// Thermometer OneWire address

int thPrepare() {
	int result = -1;

#ifdef DEBUG
	Serial.println("DEBUG: Trying to initialize DS18B20 thermometer.");
#endif

	thermometer.reset_search();
	if (thermometer.search(th_addr)) {
		if (OneWire::crc8(th_addr, 7) != th_addr[7]) {
			Serial.println("ERROR: Thermometer CRC is not valid!");
			result = 2;
		} else {
			if (th_addr[0] != DS18B20) {
				Serial.println("ERROR: Unexpected chip signature");
				result = 4;
			} else {
				result = 0;
			}
		}
	} else {
		result = 8;
#ifdef DEBUG
		Serial.println("DEBUG: DS18B20 not found.");
#endif
	}
#ifdef DEBUG
	char buffer[80];
	sprintf(buffer, "DEBUG: End of DS18B20 prep, result=%d",result);
	Serial.println(buffer);
#endif
	return result;
}

float thRead() {
	byte data[12];								// Read buffer
	int i;
	byte crc;									// Data CRC
	byte cfg;									// Chip configuration byte
	int16_t raw;								// Raw/binary temperature

	float temp = 0;

	if (thPrepare() != 0) {
		return -999.0;
	}

	thermometer.reset();
	thermometer.select(th_addr);
	thermometer.write(TH_START_CONVERSION, 0);// Conversion, no parasitic power
	delay(750);									// Wait for conversion

	thermometer.reset();
	thermometer.select(th_addr);
	thermometer.write(TH_READ_SCRATCHPAD);		// Read temperature

	for (i = 0; i < 9; i++) {						// Get 9 bytes
		data[i] = thermometer.read();
	}
	crc = OneWire::crc8(data, 8);
	if (crc != data[8]) {
		Serial.println("ERROR: Thermometer data CRC is wrong");
		temp = -999.00;
		return temp;
	}

	cfg = data[4] & 0x60;						// Config byte
	raw = (data[1] << 8) | data[0];				// Raw temperature data (binary)

	// at lower res, the low bits are undefined, so let's zero them
	if (cfg == 0x00)
		raw = raw & ~7;  // 9 bit resolution, 93.75 ms
	else if (cfg == 0x20)
		raw = raw & ~3; // 10 bit res, 187.5 ms
	else if (cfg == 0x40)
		raw = raw & ~1; // 11 bit res, 375 ms
	// default is 12 bit resolution, 750 ms conversion time
	temp = (float) raw / 16.0;					// Get temp in Celsius

	return temp;
}

