#include <Arduino.h>
#include <avr/sleep.h>
#include <avr/wdt.h>
#include <string.h>

#define DEBUG 1

#include "clocks/MeteoClockRTC.h"
#include "clocks/MeteoClockSoft.h"

#include "sensors/ReadTemperature.h"
#include "sensors/ReadHumidity.h"
#include "sensors/ReadBarometer.h"
#include "sensors/ReadLight.h"

#include "HC05Module.h"
#include "MeteoEEPROM.h"
#include "MeteoMessages.h"

// Firmware version string
#define FWVERSION "03.00.00"
// External interrupt pin used by the RTC
#define SQ_PIN 3
// Size of the input buffer
#define INBUF_SIZE 40
// Size of the output buffer
#define OUTBUF_SIZE 128
// Timeout for command reads (in milis)
#define READ_TIMEOUT 1000
// MCU timer prescaler value
#define PRESCALER	 1024
// MCU timer tick frequency (in Hz)
#define INT_FREQ_HZ		1

MeteoClockRTC  rtcClock;
MeteoClockSoft softClock;
HC05Module bt(2);
MeteoEEPROM ee;
MeteoMessages msgs;

//struct {
//	struct EepromData data;
//} eeprom;

bool firstConnection = true;			// First connection flag
bool swClockSet = false;				// Is the software clock set?
bool rtcPresent = false;				// RTC detected flag
volatile bool doRead = true;			// Read sensors timing flag, read at startup
volatile bool wdTriggered = false;		// Flag: Watchdog triggered
enum deviceEnum { DE_CLOCK=0, DE_THERMOMETER=1, DE_HIGROMETER=2,
	              DE_BAROMETER=3, DE_LIGHT=4 };
char devList[] = "     ";				// List of present devices
static char line[OUTBUF_SIZE];			// Buffer to build output messages
static char inBuff[INBUF_SIZE];			// Buffer for incoming commands


//+
// Put the MCU to sleep
// Use IDLE mode to get the USART interrupts
// Remember the goal is not to save power, but to have correct
// timing of our readings
//-
void sleepNow() {
	set_sleep_mode(SLEEP_MODE_IDLE);
	sleep_mode();
}

//+
// RTC SQW interrupt service routine
// It keeps a counter of invocations. Each pollDelay seconds
// it will raise the global doRead flag so the main loop will
// make a sensor reading.
//-
void sqInterrupt() {
	static int sqCounter = -1;			// The flag is up at startup, so we have
										// to count from minus one.
	wdt_reset();						// Reset the watchdog timer
	if (++sqCounter >= ee.data.pollDelay) {
		doRead = true;
		sqCounter = 0;
	}
}

//+
// Watchdog interrupt routine.
// Resets itself and asserts the 'watchdog triggered' and
// 'time to read' flags.
//-
ISR(WDT_vect) {
	wdTriggered = true;
	doRead = true;
}
//+
// MCU timer1 compare interruption
//-
ISR(TIMER1_COMPA_vect) {
	static int timCounter = -1;

	wdt_reset();
		if (++timCounter >= ee.data.pollDelay) {
		doRead = true;
		timCounter = 0;
	}
}


//+
// Enable the MCU timer
//-
void enableMCUTimer() {
	uint32_t matchReg = F_CPU / (PRESCALER * INT_FREQ_HZ) - 1;
	cli();									// Inhibit interrupts
	TCCR1A = 0;
	TCCR1B = 0;
	TCNT1  = 0;
	OCR1A  = matchReg;
	TCCR1B |= (1 << WGM12);					// CTC mode
	TCCR1B |= (1 << CS12) | (1 << CS10);	// Set prescaler at 1024
	TIMSK1 |= (1 << OCIE1A);				// Enable timer comparer interrupt
	sei();									// Enable interrupts
}

//+
// Disable timer1
//-
void disableMCUTimer() {
	cli();
	TCCR1B  &= ~((1<<CS10) | (1<<CS12));
	sei();
}


//+
// Enable watchdog in interrupt + reset mode
//-
void enableWatchdog() {
    MCUSR &= ~(1<<WDRF);
    cli();							// Disable interrupts during timed change
    WDTCSR |= (1<<WDCE) | (1<<WDE);	// Enable changes, 4 cycles to go
    WDTCSR = (1<<WDP0) | (1<<WDP3);	// Clear reset mode, set 8s timeout
    sei();							// Enable interrupts
    WDTCSR |= (1<<WDIE) | (1<<WDE);	// Enable interrupt and reset modes
}

void checkClock() {
	bool clockNow = rtcPresent;

	if (!rtcClock.checkClock()) {
		rtcPresent = false;
		devList[DE_CLOCK] = '-';
		detachInterrupt(INT1);
		enableMCUTimer();
	} else {
		rtcPresent = true;
		devList[DE_CLOCK] = 'C';
		disableMCUTimer();
		rtcClock.enableInterrupt();
		if (!swClockSet) {
			DateTime now = rtcClock.getDateTime();
			softClock.setClock(now.year(), now.month(), now.day(),
					           now.hour(), now.minute(), now.second());
			swClockSet = true;
		}
		attachInterrupt(INT1, sqInterrupt, FALLING);
	}
	if (clockNow != rtcPresent) {
		if (rtcPresent) {
			msgs.getMessage(CLOCKDET, line);
		} else {
			msgs.getMessage(CLOCKLST, line);
		}
		Serial.println(line);
	}
}

void setup() {
	int rc=0;
	char msg[80];

	// Disable watchdog, just in case
	MCUSR=0;
	wdt_disable();

	Serial.begin(9600);

	while (!bt.begin()) {
		Serial.println("ERROR: No BT connection");
	}

	Serial.println("");

	ee.readEEPROM();
	// eeprom.data.pollDelay = 5;


#ifdef DEBUG
	sprintf(msg, "DEBUG: CPU clock: %ld", F_CPU);
	Serial.println(msg);
#endif

	rc = thPrepare();
	if (rc != 0) {
		msgs.getMessage(THERMNOK, line);
		Serial.println(line);
		devList[DE_THERMOMETER] = '-';
	} else {
		devList[DE_THERMOMETER] = 'T';
	}
	rc = higInitialize();
	if (rc != 0) {
		msgs.getMessage(HYGRONOK, line);
		Serial.println(line);
		devList[DE_HIGROMETER] = '-';
	} else {
		devList[DE_HIGROMETER] = 'H';
	}

	rc = barInitialize();
	if (rc != 0) {
		msgs.getMessage(BAROMNOK, line);
		Serial.println(line);
		devList[DE_BAROMETER] = '-';
	} else {
		devList[DE_BAROMETER] = 'P';
	}

	rc = lightInitialize();
	devList[DE_LIGHT] = 'L';

	checkClock();

	//+
	// Set up the interrupt pin
	// That pin will get the SQW signals from the RTC and will act
	// on the falling flank
	//-
	pinMode(SQ_PIN, INPUT_PULLUP);
	enableWatchdog();

	sprintf(msg, "INFO : F:%s W:%s N:%s DLY:%d", FWVERSION, ee.data.hwVersion,
			                                       ee.data.devName, ee.data.pollDelay);
	Serial.println(msg);


}

//+
// Read an incoming command from the serial line (hopefully connected to the HC-05)
// The accepted command terminators are NL or CR+NL
// If a command terminator has not been received in READ_TIMEOUT milliseconds
// the read will be rejected and a timeout will be signaled (returning FALSE).
//-
bool readCommand() {
	bool eos = false;
	bool timeout = false;
	int numChars = 0;
	char *buffPtr = inBuff;
	unsigned long timecontrol = millis();

	while (!eos && numChars < INBUF_SIZE && !timeout) {
		if (millis() - timecontrol < READ_TIMEOUT) {
			if (Serial.available()) {
				char c = Serial.read();
				if (c == 0x0a) {		// Got command terminator
					eos = true;
					*(buffPtr++) = 0x0;	// Terminate the command line
				} else if (c == 0x0d) {
					continue;			// Ignore CR by itself. The terminator must be NL or CR+NL
				} else {
					*(buffPtr++) = c;	// Got char, append to buffer
					numChars++;
				}
			}
		} else {
			timeout = true;			// Didn't get a complete command
			*(buffPtr++) = 0x0;		// Terminate partial command
		}
	}
	return !timeout;
}

//+
// Process a command string
//-
void processCommand(String cmd) {
	bool cmdOk = false;

	String theCmd = cmd.substring(0,5);
	if (theCmd.equals("TIME ")) {
		String t = cmd.substring(5,19);
		checkClock();
		if (rtcPresent) {
			rtcClock.setClock(t);
		}
		softClock.setClock(t);
		swClockSet = true;
		cmdOk = true;
	} else if (theCmd.equals("BYE  ")) {
		Serial.println("OK-BYE");
		cmdOk = true;
		for (int i=0; i<5 && bt.checkConnection(); i++) delay(1000);
		if (bt.checkConnection()) {
			Serial.println("KO-ONL");
		} else {
			firstConnection = true;
		}
		return;
	} else if (theCmd.equals("INFO ")) {
		sprintf(line, "INFO : F:%s W:%s N:%s DLY:%d", FWVERSION, ee.data.hwVersion,
				                                        ee.data.devName, ee.data.pollDelay);
		Serial.println(line);
		cmdOk = true;
	} else if (theCmd.equals("DLAY ")) {
		int newDelay = atoi(cmd.substring(5,7).c_str());
		if (newDelay < 1 || newDelay > 60) {
			Serial.println("KO-INV");
		} else {
			ee.data.pollDelay = newDelay;
			ee.writeEEPROM();
		}
		cmdOk = true;
	} else if (theCmd.equals("NAME ")){
		strncpy(ee.data.devName, cmd.substring(5,13).c_str(), _SIZ_DEVNAME+1);
		cmdOk = true;
	}
	if (cmdOk) {
		Serial.println("OK-000");
	} else {
		sprintf(line, "KO-UNK [%s]", theCmd.c_str());
		Serial.println(line);
	}
}

//  TIME 20180220221700
//  BYE

//+
// Read the sensors and send a DATA line thru the USART
//-
void readSensors() {
	String theTime;
	float temp, press, humdt, light;

	// If we have an RTC, check it's still working. If not, switch to MPU soft clock
	if (rtcPresent) {
		checkClock();
		if (rtcPresent) {
			theTime = rtcClock.getClock();
		}
	}

	// If we've got no RTC, use software clock and check if it has came back
	if (!rtcPresent) {
		theTime = softClock.getClock();
		checkClock();
	}
	char stemp[10], shumt[10], spres[10], slght[10];

	temp = thRead();
	press = barRead();
	humdt = higRead();
	light = lightRead();

	if (temp==-999.00) {		// No thermometre?
		temp = barTemp();		// Try BMP180
		if (temp==-999.00) {	// No BMP180?
			temp = higTemp();	// Try DHT22
		}
		if (devList[DE_THERMOMETER] == 'T') {
			msgs.getMessage(THERMLST, line);
			Serial.println(line);
			devList[DE_THERMOMETER] = '-';
		}
	} else {
		if (devList[DE_THERMOMETER] == '-') {
			msgs.getMessage(THERMDET, line);
			Serial.println(line);
			devList[DE_THERMOMETER] = 'T';
		}
	}

	if (press == -999.00) {
		if (devList[DE_BAROMETER] == 'P') {
			msgs.getMessage(BAROMLST, line);
			Serial.println(line);
			devList[DE_BAROMETER] = '-';
		}
	} else {
		if (devList[DE_BAROMETER] == '-') {
			msgs.getMessage(BAROMDET, line);
			Serial.println(line);
			devList[DE_BAROMETER] = 'P';
		}
	}

	if (humdt == -999.00) {
		if (devList[DE_HIGROMETER] == 'H') {
			msgs.getMessage(HYGROLST, line);
			Serial.println(line);
			devList[DE_HIGROMETER] = '-';
		}
	} else {
		if (devList[DE_HIGROMETER] == '-') {
			msgs.getMessage(HYGRODET, line);
			Serial.println(line);
			devList[DE_HIGROMETER] = 'H';
		}
	}

	dtostrf(temp, 5, 2, stemp);
	dtostrf(press, 6, 2, spres);
	dtostrf(humdt, 5, 2, shumt);
	dtostrf(light, 6, 2, slght);

	sprintf(line, "DATA :C%s:F%s:T%s:H%s:P%s:L%s:D%s:W%s:N%s", theTime.c_str(), FWVERSION, stemp,
			shumt, spres, slght, devList,ee.data.hwVersion,ee.data.devName);

	if (bt.checkConnection()) {
		if (firstConnection) {
			msgs.getMessage(BEGINPGM, line);
			firstConnection = false;
		}
		Serial.println(line);
	}
}

//+
// Main loop
//-
void loop() {
	if (wdTriggered) {
		msgs.getMessage(WATCHDOG, line);
		Serial.println(line);
		Serial.flush();
		wdTriggered = false;
	}

	if (doRead) {
		doRead = false;
		readSensors();
		if (!swClockSet) {
			msgs.getMessage(TIMEREQS, line);
			Serial.println(line);
		}
		Serial.flush();
	}
	if (Serial.available()) {
		if (readCommand()) {
			Serial.flush();
		} else {
			msgs.getMessage(COMNDTMO, line);
			Serial.println(line);
		}
		processCommand(String(inBuff));
	}
	sleepNow();					// Wait for next interrupt
}
