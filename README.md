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
- Atmospheric pressure sensor, based on a BMP280 chip
- Light sensor, based on a photoresistor read analogically

### Communications

The device will use an HC-06 based Serial-to-Bluetooth transceiver to send the data it gets to a nearby computer which will do the graphing and reporting.

### Storage

Initial plans called to use a local microSD to store the data in case it could not be transmitted. This is being re-evaluated. The first version will **not** store any data locally.

### Microcontroller

The device will use a nano-Arduino clone as microcontroller. The possibility of using a *raw* MCU will be considered.

## General design

Due to the author soldering (dis)abilities, the different sensors will be bought in ready-to-use format. There are plenty of sources available for that, and they are very cheap.


