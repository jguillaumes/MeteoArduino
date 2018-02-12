# MeteoArduino - Small Arduino-Based meteorological station

This project consists on building a basic meteorological monitoring and registering station using an 
Arduino and a few sensors.

It measures the basic weather parameters:
- Temperature
- Atmospheric pressure
- Humidity
- Light level

The data is logged into a microSD card and sent to a nearby receiver using a bluetooth link. The "station" has no user interface, apart from a RESET and a TEST button.

## Materials

### Sensors used

- Temperature sensor, based on a DS18B20 chip.
- Humidity sensor, based on a DHT22 chip. This chip also measures temperature, but that measurement will not be used
- Atmospheric pressure sensor, based on a BMP180 chip
- Light sensor, based on a photoresistor read analogically

### Communications

The device will use an HC-06 based Serial-to-Bluetooth transceiver to send the data it gets to a nearby computer which will do the graphing and reporting.

### Storage

Initial plans called to use a local microSD to store the data in case it could not be transmitted. This is being re-evaluated. The first version will **not** store any data locally.

### Microcontroller

The device will use a nano-Arduino clone as microcontroller. The possibility of using a *raw* MCU will be considered.

## General design

Due to the author soldering (dis)abilities, the different sensors will be bought in ready-to-use format. There are plenty of sources available for that, and they are very cheap.

## General information

The initial design called for a BMP-280 based barometric sensor. Unfortunately that piece of hardware does not tolerate the 5V level of the Arduino board. A bi-directional level converted capable of supporting I2C must be used, and I had no one available. So I switched to the less precise (but good enough) BMP-180, in a breakout form which includes resistors to make it able to stand a 5V signal level. The specific piece is this: https://www.amazon.es/gp/product/B00M1PMSF2/ref=oh_aui_detailpage_o00_s00?ie=UTF8&psc=1

The second version of this project will use a stand-alone ATMega328P running at 8MHz in an all 3.3V circuit so the use of the BMP-280 will be reconsidered.

The BMP-180 branch of this project contains the software adapted for the BMP-180. The master branch uses the BMP-280.


