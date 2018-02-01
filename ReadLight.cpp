/*
 * ReadLight.cpp
 *
 *  Created on: Jan 29, 2018
 *      Author: jguillaumes
 */

#include <Arduino.h>
#include "ReadLight.h"



int lightInitialize() {
	return 0;
}


float lightRead() {
	return (float) analogRead(LIGHT_PIN);
}

