/*
 * BTComms.h
 *
 *  Created on: Jan 28, 2018
 *      Author: jguillaumes
 */

#ifndef BTCOMMS_H_
#define BTCOMMS_H_

#include <Arduino.h>
#include <SoftwareSerial.h>

#define RXPIN 3
#define TXPIN 2

#define BTSPEED 9600L
#define BTNAME "WeatherLog"
#define BTPIN  "0000"
#define BTRETRIES 5
#define BTTIMEOUT 1000

const char BT_OK[]  PROGMEM ="OK";
const char BT_AT[]  PROGMEM = "AT";
const char BT_PIN[] PROGMEM = "AT+PIN";
const char BT_RST[] PROGMEM = "AT+RESET";

int commInitialize(int nrets=BTRETRIES);
String commRead(unsigned long timeout=BTTIMEOUT);

#endif /* BTCOMMS_H_ */
