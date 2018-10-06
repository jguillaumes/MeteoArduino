#include <Arduino.h>
#include <string.h>
#include "MeteoClock.h"

//+
// Parse a C string in the format YYYYMMDDhhmmss into its components
// Parameters:
// - const char *tim: the string to parse
// - struct ComptTime comp: pointer to the destination CompTime structure
//-

void MeteoClock::parseTime(const char *tim, struct CompTime *comp) {
	char buffer[8];

	memset(buffer,0,8);
	memcpy(buffer,tim,4);	 comp->year=atoi(buffer);
	memset(buffer,0,8);
	memcpy(buffer,tim+4,2);	 comp->month = atoi(buffer);
	memcpy(buffer,tim+6,2);	 comp->day   = atoi(buffer);
	memcpy(buffer,tim+8,2);	 comp->hour  = atoi(buffer);
	memcpy(buffer,tim+10,2); comp->minute= atoi(buffer);
	memcpy(buffer,tim+12,2); comp->second= atoi(buffer);
}

//+
// Set the clock from a CompTime structure
//-
void MeteoClock::setClock(struct CompTime &ct) {
	setClock(ct.year, ct.month, ct.day, ct.hour, ct.minute, ct.second);
}

//+
// Print the members of a CompTime structure (for debugging)
//-
void MeteoClock::printCT(struct CompTime &ct) {
	char buffer[80];
	sprintf(buffer, "%d %d %d %d %d %d\n", ct.year, ct.month, ct.day,
			ct.hour, ct.minute, ct.second);
	Serial.write(buffer);
}

//+
// Set (adjust) the clock from a YYYMMDDhhmmss string
// There is no formal checking done. If the string is not correct the
// results are undefined.
//-
void MeteoClock::setClock(const String &timestamp) {
	struct CompTime ct;
	parseTime(timestamp, &ct);
	//printCT(ct);
	setClock(ct);
}
