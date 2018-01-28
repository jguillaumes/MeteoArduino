/*
 * BTComms.cpp
 *
 *  Created on: Jan 28, 2018
 *      Author: jguillaumes
 */

#include "BTComms.h"
#include "iostream.h"

SoftwareSerial bt(RXPIN, TXPIN);


int commInitialize(int nrets) {
	int rc = -1;
	String inbuf;
	int retries = nrets;

	bt.begin(BTSPEED);
	bt.listen();

	while(rc==-1 && retries-- >= 0) {
		bt.println(BT_AT);
		inbuf = commRead();

		Serial.print("inbuf="); Serial.println(inbuf);

		if (inbuf.equals(BT_OK)) {
			bt.print(BT_PIN);
			bt.println(BTPIN);
			inbuf = commRead();
			if (inbuf.equals(BT_OK)) {
				bt.println(BT_RST);
				inbuf = commRead();
				if (inbuf.equals(BT_OK)) {
					rc = 0;
				}
			}
		}

		if (rc != 0 ) {
			Serial.println("Comm link failed.");
		}
	}

	return rc;
}

String commRead(unsigned long timeout) {
	bt.setTimeout(1000);
	return bt.readString();
}

