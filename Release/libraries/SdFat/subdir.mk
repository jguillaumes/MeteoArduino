################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
CPP_SRCS += \
/Users/jguillaumes/Arduino/libraries/SdFat/MinimumSerial.cpp \
/Users/jguillaumes/Arduino/libraries/SdFat/Sd2Card.cpp \
/Users/jguillaumes/Arduino/libraries/SdFat/SdBaseFile.cpp \
/Users/jguillaumes/Arduino/libraries/SdFat/SdBaseFilePrint.cpp \
/Users/jguillaumes/Arduino/libraries/SdFat/SdFat.cpp \
/Users/jguillaumes/Arduino/libraries/SdFat/SdFatErrorPrint.cpp \
/Users/jguillaumes/Arduino/libraries/SdFat/SdFatUtil.cpp \
/Users/jguillaumes/Arduino/libraries/SdFat/SdFile.cpp \
/Users/jguillaumes/Arduino/libraries/SdFat/SdSpiAVR.cpp \
/Users/jguillaumes/Arduino/libraries/SdFat/SdSpiArduino.cpp \
/Users/jguillaumes/Arduino/libraries/SdFat/SdSpiSAM3X.cpp \
/Users/jguillaumes/Arduino/libraries/SdFat/SdSpiSoft.cpp \
/Users/jguillaumes/Arduino/libraries/SdFat/SdSpiTeensy3.cpp \
/Users/jguillaumes/Arduino/libraries/SdFat/SdStream.cpp \
/Users/jguillaumes/Arduino/libraries/SdFat/SdVolume.cpp \
/Users/jguillaumes/Arduino/libraries/SdFat/StdioStream.cpp \
/Users/jguillaumes/Arduino/libraries/SdFat/istream.cpp \
/Users/jguillaumes/Arduino/libraries/SdFat/ostream.cpp 

LINK_OBJ += \
./libraries/SdFat/MinimumSerial.cpp.o \
./libraries/SdFat/Sd2Card.cpp.o \
./libraries/SdFat/SdBaseFile.cpp.o \
./libraries/SdFat/SdBaseFilePrint.cpp.o \
./libraries/SdFat/SdFat.cpp.o \
./libraries/SdFat/SdFatErrorPrint.cpp.o \
./libraries/SdFat/SdFatUtil.cpp.o \
./libraries/SdFat/SdFile.cpp.o \
./libraries/SdFat/SdSpiAVR.cpp.o \
./libraries/SdFat/SdSpiArduino.cpp.o \
./libraries/SdFat/SdSpiSAM3X.cpp.o \
./libraries/SdFat/SdSpiSoft.cpp.o \
./libraries/SdFat/SdSpiTeensy3.cpp.o \
./libraries/SdFat/SdStream.cpp.o \
./libraries/SdFat/SdVolume.cpp.o \
./libraries/SdFat/StdioStream.cpp.o \
./libraries/SdFat/istream.cpp.o \
./libraries/SdFat/ostream.cpp.o 

CPP_DEPS += \
./libraries/SdFat/MinimumSerial.cpp.d \
./libraries/SdFat/Sd2Card.cpp.d \
./libraries/SdFat/SdBaseFile.cpp.d \
./libraries/SdFat/SdBaseFilePrint.cpp.d \
./libraries/SdFat/SdFat.cpp.d \
./libraries/SdFat/SdFatErrorPrint.cpp.d \
./libraries/SdFat/SdFatUtil.cpp.d \
./libraries/SdFat/SdFile.cpp.d \
./libraries/SdFat/SdSpiAVR.cpp.d \
./libraries/SdFat/SdSpiArduino.cpp.d \
./libraries/SdFat/SdSpiSAM3X.cpp.d \
./libraries/SdFat/SdSpiSoft.cpp.d \
./libraries/SdFat/SdSpiTeensy3.cpp.d \
./libraries/SdFat/SdStream.cpp.d \
./libraries/SdFat/SdVolume.cpp.d \
./libraries/SdFat/StdioStream.cpp.d \
./libraries/SdFat/istream.cpp.d \
./libraries/SdFat/ostream.cpp.d 


# Each subdirectory must supply rules for building sources it contributes
libraries/SdFat/MinimumSerial.cpp.o: /Users/jguillaumes/Arduino/libraries/SdFat/MinimumSerial.cpp
	@echo 'Building file: $<'
	@echo 'Starting C++ compile'
	"/Applications/Eclipse.app/Contents/Eclipse//arduinoPlugin/packages/arduino/tools/avr-gcc/4.9.2-atmel3.5.4-arduino2/bin/avr-g++" -c -g -Os -Wall -Wextra -std=gnu++11 -fpermissive -fno-exceptions -ffunction-sections -fdata-sections -fno-threadsafe-statics -flto -mmcu=atmega328p -DF_CPU=16000000L -DARDUINO=10802 -DARDUINO_AVR_UNO -DARDUINO_ARCH_AVR   -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/cores/arduino" -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/variants/standard" -I"/Users/jguillaumes/Arduino/libraries/OneWire-master" -I"/Users/jguillaumes/Arduino/libraries/SdFat" -I"/Users/jguillaumes/Arduino/libraries/SdFat/utility" -I"/Users/jguillaumes/Arduino/libraries/DHT" -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" -D__IN_ECLIPSE__=1 -x c++ "$<"  -o  "$@"
	@echo 'Finished building: $<'
	@echo ' '

libraries/SdFat/Sd2Card.cpp.o: /Users/jguillaumes/Arduino/libraries/SdFat/Sd2Card.cpp
	@echo 'Building file: $<'
	@echo 'Starting C++ compile'
	"/Applications/Eclipse.app/Contents/Eclipse//arduinoPlugin/packages/arduino/tools/avr-gcc/4.9.2-atmel3.5.4-arduino2/bin/avr-g++" -c -g -Os -Wall -Wextra -std=gnu++11 -fpermissive -fno-exceptions -ffunction-sections -fdata-sections -fno-threadsafe-statics -flto -mmcu=atmega328p -DF_CPU=16000000L -DARDUINO=10802 -DARDUINO_AVR_UNO -DARDUINO_ARCH_AVR   -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/cores/arduino" -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/variants/standard" -I"/Users/jguillaumes/Arduino/libraries/OneWire-master" -I"/Users/jguillaumes/Arduino/libraries/SdFat" -I"/Users/jguillaumes/Arduino/libraries/SdFat/utility" -I"/Users/jguillaumes/Arduino/libraries/DHT" -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" -D__IN_ECLIPSE__=1 -x c++ "$<"  -o  "$@"
	@echo 'Finished building: $<'
	@echo ' '

libraries/SdFat/SdBaseFile.cpp.o: /Users/jguillaumes/Arduino/libraries/SdFat/SdBaseFile.cpp
	@echo 'Building file: $<'
	@echo 'Starting C++ compile'
	"/Applications/Eclipse.app/Contents/Eclipse//arduinoPlugin/packages/arduino/tools/avr-gcc/4.9.2-atmel3.5.4-arduino2/bin/avr-g++" -c -g -Os -Wall -Wextra -std=gnu++11 -fpermissive -fno-exceptions -ffunction-sections -fdata-sections -fno-threadsafe-statics -flto -mmcu=atmega328p -DF_CPU=16000000L -DARDUINO=10802 -DARDUINO_AVR_UNO -DARDUINO_ARCH_AVR   -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/cores/arduino" -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/variants/standard" -I"/Users/jguillaumes/Arduino/libraries/OneWire-master" -I"/Users/jguillaumes/Arduino/libraries/SdFat" -I"/Users/jguillaumes/Arduino/libraries/SdFat/utility" -I"/Users/jguillaumes/Arduino/libraries/DHT" -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" -D__IN_ECLIPSE__=1 -x c++ "$<"  -o  "$@"
	@echo 'Finished building: $<'
	@echo ' '

libraries/SdFat/SdBaseFilePrint.cpp.o: /Users/jguillaumes/Arduino/libraries/SdFat/SdBaseFilePrint.cpp
	@echo 'Building file: $<'
	@echo 'Starting C++ compile'
	"/Applications/Eclipse.app/Contents/Eclipse//arduinoPlugin/packages/arduino/tools/avr-gcc/4.9.2-atmel3.5.4-arduino2/bin/avr-g++" -c -g -Os -Wall -Wextra -std=gnu++11 -fpermissive -fno-exceptions -ffunction-sections -fdata-sections -fno-threadsafe-statics -flto -mmcu=atmega328p -DF_CPU=16000000L -DARDUINO=10802 -DARDUINO_AVR_UNO -DARDUINO_ARCH_AVR   -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/cores/arduino" -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/variants/standard" -I"/Users/jguillaumes/Arduino/libraries/OneWire-master" -I"/Users/jguillaumes/Arduino/libraries/SdFat" -I"/Users/jguillaumes/Arduino/libraries/SdFat/utility" -I"/Users/jguillaumes/Arduino/libraries/DHT" -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" -D__IN_ECLIPSE__=1 -x c++ "$<"  -o  "$@"
	@echo 'Finished building: $<'
	@echo ' '

libraries/SdFat/SdFat.cpp.o: /Users/jguillaumes/Arduino/libraries/SdFat/SdFat.cpp
	@echo 'Building file: $<'
	@echo 'Starting C++ compile'
	"/Applications/Eclipse.app/Contents/Eclipse//arduinoPlugin/packages/arduino/tools/avr-gcc/4.9.2-atmel3.5.4-arduino2/bin/avr-g++" -c -g -Os -Wall -Wextra -std=gnu++11 -fpermissive -fno-exceptions -ffunction-sections -fdata-sections -fno-threadsafe-statics -flto -mmcu=atmega328p -DF_CPU=16000000L -DARDUINO=10802 -DARDUINO_AVR_UNO -DARDUINO_ARCH_AVR   -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/cores/arduino" -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/variants/standard" -I"/Users/jguillaumes/Arduino/libraries/OneWire-master" -I"/Users/jguillaumes/Arduino/libraries/SdFat" -I"/Users/jguillaumes/Arduino/libraries/SdFat/utility" -I"/Users/jguillaumes/Arduino/libraries/DHT" -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" -D__IN_ECLIPSE__=1 -x c++ "$<"  -o  "$@"
	@echo 'Finished building: $<'
	@echo ' '

libraries/SdFat/SdFatErrorPrint.cpp.o: /Users/jguillaumes/Arduino/libraries/SdFat/SdFatErrorPrint.cpp
	@echo 'Building file: $<'
	@echo 'Starting C++ compile'
	"/Applications/Eclipse.app/Contents/Eclipse//arduinoPlugin/packages/arduino/tools/avr-gcc/4.9.2-atmel3.5.4-arduino2/bin/avr-g++" -c -g -Os -Wall -Wextra -std=gnu++11 -fpermissive -fno-exceptions -ffunction-sections -fdata-sections -fno-threadsafe-statics -flto -mmcu=atmega328p -DF_CPU=16000000L -DARDUINO=10802 -DARDUINO_AVR_UNO -DARDUINO_ARCH_AVR   -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/cores/arduino" -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/variants/standard" -I"/Users/jguillaumes/Arduino/libraries/OneWire-master" -I"/Users/jguillaumes/Arduino/libraries/SdFat" -I"/Users/jguillaumes/Arduino/libraries/SdFat/utility" -I"/Users/jguillaumes/Arduino/libraries/DHT" -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" -D__IN_ECLIPSE__=1 -x c++ "$<"  -o  "$@"
	@echo 'Finished building: $<'
	@echo ' '

libraries/SdFat/SdFatUtil.cpp.o: /Users/jguillaumes/Arduino/libraries/SdFat/SdFatUtil.cpp
	@echo 'Building file: $<'
	@echo 'Starting C++ compile'
	"/Applications/Eclipse.app/Contents/Eclipse//arduinoPlugin/packages/arduino/tools/avr-gcc/4.9.2-atmel3.5.4-arduino2/bin/avr-g++" -c -g -Os -Wall -Wextra -std=gnu++11 -fpermissive -fno-exceptions -ffunction-sections -fdata-sections -fno-threadsafe-statics -flto -mmcu=atmega328p -DF_CPU=16000000L -DARDUINO=10802 -DARDUINO_AVR_UNO -DARDUINO_ARCH_AVR   -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/cores/arduino" -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/variants/standard" -I"/Users/jguillaumes/Arduino/libraries/OneWire-master" -I"/Users/jguillaumes/Arduino/libraries/SdFat" -I"/Users/jguillaumes/Arduino/libraries/SdFat/utility" -I"/Users/jguillaumes/Arduino/libraries/DHT" -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" -D__IN_ECLIPSE__=1 -x c++ "$<"  -o  "$@"
	@echo 'Finished building: $<'
	@echo ' '

libraries/SdFat/SdFile.cpp.o: /Users/jguillaumes/Arduino/libraries/SdFat/SdFile.cpp
	@echo 'Building file: $<'
	@echo 'Starting C++ compile'
	"/Applications/Eclipse.app/Contents/Eclipse//arduinoPlugin/packages/arduino/tools/avr-gcc/4.9.2-atmel3.5.4-arduino2/bin/avr-g++" -c -g -Os -Wall -Wextra -std=gnu++11 -fpermissive -fno-exceptions -ffunction-sections -fdata-sections -fno-threadsafe-statics -flto -mmcu=atmega328p -DF_CPU=16000000L -DARDUINO=10802 -DARDUINO_AVR_UNO -DARDUINO_ARCH_AVR   -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/cores/arduino" -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/variants/standard" -I"/Users/jguillaumes/Arduino/libraries/OneWire-master" -I"/Users/jguillaumes/Arduino/libraries/SdFat" -I"/Users/jguillaumes/Arduino/libraries/SdFat/utility" -I"/Users/jguillaumes/Arduino/libraries/DHT" -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" -D__IN_ECLIPSE__=1 -x c++ "$<"  -o  "$@"
	@echo 'Finished building: $<'
	@echo ' '

libraries/SdFat/SdSpiAVR.cpp.o: /Users/jguillaumes/Arduino/libraries/SdFat/SdSpiAVR.cpp
	@echo 'Building file: $<'
	@echo 'Starting C++ compile'
	"/Applications/Eclipse.app/Contents/Eclipse//arduinoPlugin/packages/arduino/tools/avr-gcc/4.9.2-atmel3.5.4-arduino2/bin/avr-g++" -c -g -Os -Wall -Wextra -std=gnu++11 -fpermissive -fno-exceptions -ffunction-sections -fdata-sections -fno-threadsafe-statics -flto -mmcu=atmega328p -DF_CPU=16000000L -DARDUINO=10802 -DARDUINO_AVR_UNO -DARDUINO_ARCH_AVR   -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/cores/arduino" -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/variants/standard" -I"/Users/jguillaumes/Arduino/libraries/OneWire-master" -I"/Users/jguillaumes/Arduino/libraries/SdFat" -I"/Users/jguillaumes/Arduino/libraries/SdFat/utility" -I"/Users/jguillaumes/Arduino/libraries/DHT" -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" -D__IN_ECLIPSE__=1 -x c++ "$<"  -o  "$@"
	@echo 'Finished building: $<'
	@echo ' '

libraries/SdFat/SdSpiArduino.cpp.o: /Users/jguillaumes/Arduino/libraries/SdFat/SdSpiArduino.cpp
	@echo 'Building file: $<'
	@echo 'Starting C++ compile'
	"/Applications/Eclipse.app/Contents/Eclipse//arduinoPlugin/packages/arduino/tools/avr-gcc/4.9.2-atmel3.5.4-arduino2/bin/avr-g++" -c -g -Os -Wall -Wextra -std=gnu++11 -fpermissive -fno-exceptions -ffunction-sections -fdata-sections -fno-threadsafe-statics -flto -mmcu=atmega328p -DF_CPU=16000000L -DARDUINO=10802 -DARDUINO_AVR_UNO -DARDUINO_ARCH_AVR   -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/cores/arduino" -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/variants/standard" -I"/Users/jguillaumes/Arduino/libraries/OneWire-master" -I"/Users/jguillaumes/Arduino/libraries/SdFat" -I"/Users/jguillaumes/Arduino/libraries/SdFat/utility" -I"/Users/jguillaumes/Arduino/libraries/DHT" -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" -D__IN_ECLIPSE__=1 -x c++ "$<"  -o  "$@"
	@echo 'Finished building: $<'
	@echo ' '

libraries/SdFat/SdSpiSAM3X.cpp.o: /Users/jguillaumes/Arduino/libraries/SdFat/SdSpiSAM3X.cpp
	@echo 'Building file: $<'
	@echo 'Starting C++ compile'
	"/Applications/Eclipse.app/Contents/Eclipse//arduinoPlugin/packages/arduino/tools/avr-gcc/4.9.2-atmel3.5.4-arduino2/bin/avr-g++" -c -g -Os -Wall -Wextra -std=gnu++11 -fpermissive -fno-exceptions -ffunction-sections -fdata-sections -fno-threadsafe-statics -flto -mmcu=atmega328p -DF_CPU=16000000L -DARDUINO=10802 -DARDUINO_AVR_UNO -DARDUINO_ARCH_AVR   -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/cores/arduino" -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/variants/standard" -I"/Users/jguillaumes/Arduino/libraries/OneWire-master" -I"/Users/jguillaumes/Arduino/libraries/SdFat" -I"/Users/jguillaumes/Arduino/libraries/SdFat/utility" -I"/Users/jguillaumes/Arduino/libraries/DHT" -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" -D__IN_ECLIPSE__=1 -x c++ "$<"  -o  "$@"
	@echo 'Finished building: $<'
	@echo ' '

libraries/SdFat/SdSpiSoft.cpp.o: /Users/jguillaumes/Arduino/libraries/SdFat/SdSpiSoft.cpp
	@echo 'Building file: $<'
	@echo 'Starting C++ compile'
	"/Applications/Eclipse.app/Contents/Eclipse//arduinoPlugin/packages/arduino/tools/avr-gcc/4.9.2-atmel3.5.4-arduino2/bin/avr-g++" -c -g -Os -Wall -Wextra -std=gnu++11 -fpermissive -fno-exceptions -ffunction-sections -fdata-sections -fno-threadsafe-statics -flto -mmcu=atmega328p -DF_CPU=16000000L -DARDUINO=10802 -DARDUINO_AVR_UNO -DARDUINO_ARCH_AVR   -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/cores/arduino" -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/variants/standard" -I"/Users/jguillaumes/Arduino/libraries/OneWire-master" -I"/Users/jguillaumes/Arduino/libraries/SdFat" -I"/Users/jguillaumes/Arduino/libraries/SdFat/utility" -I"/Users/jguillaumes/Arduino/libraries/DHT" -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" -D__IN_ECLIPSE__=1 -x c++ "$<"  -o  "$@"
	@echo 'Finished building: $<'
	@echo ' '

libraries/SdFat/SdSpiTeensy3.cpp.o: /Users/jguillaumes/Arduino/libraries/SdFat/SdSpiTeensy3.cpp
	@echo 'Building file: $<'
	@echo 'Starting C++ compile'
	"/Applications/Eclipse.app/Contents/Eclipse//arduinoPlugin/packages/arduino/tools/avr-gcc/4.9.2-atmel3.5.4-arduino2/bin/avr-g++" -c -g -Os -Wall -Wextra -std=gnu++11 -fpermissive -fno-exceptions -ffunction-sections -fdata-sections -fno-threadsafe-statics -flto -mmcu=atmega328p -DF_CPU=16000000L -DARDUINO=10802 -DARDUINO_AVR_UNO -DARDUINO_ARCH_AVR   -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/cores/arduino" -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/variants/standard" -I"/Users/jguillaumes/Arduino/libraries/OneWire-master" -I"/Users/jguillaumes/Arduino/libraries/SdFat" -I"/Users/jguillaumes/Arduino/libraries/SdFat/utility" -I"/Users/jguillaumes/Arduino/libraries/DHT" -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" -D__IN_ECLIPSE__=1 -x c++ "$<"  -o  "$@"
	@echo 'Finished building: $<'
	@echo ' '

libraries/SdFat/SdStream.cpp.o: /Users/jguillaumes/Arduino/libraries/SdFat/SdStream.cpp
	@echo 'Building file: $<'
	@echo 'Starting C++ compile'
	"/Applications/Eclipse.app/Contents/Eclipse//arduinoPlugin/packages/arduino/tools/avr-gcc/4.9.2-atmel3.5.4-arduino2/bin/avr-g++" -c -g -Os -Wall -Wextra -std=gnu++11 -fpermissive -fno-exceptions -ffunction-sections -fdata-sections -fno-threadsafe-statics -flto -mmcu=atmega328p -DF_CPU=16000000L -DARDUINO=10802 -DARDUINO_AVR_UNO -DARDUINO_ARCH_AVR   -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/cores/arduino" -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/variants/standard" -I"/Users/jguillaumes/Arduino/libraries/OneWire-master" -I"/Users/jguillaumes/Arduino/libraries/SdFat" -I"/Users/jguillaumes/Arduino/libraries/SdFat/utility" -I"/Users/jguillaumes/Arduino/libraries/DHT" -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" -D__IN_ECLIPSE__=1 -x c++ "$<"  -o  "$@"
	@echo 'Finished building: $<'
	@echo ' '

libraries/SdFat/SdVolume.cpp.o: /Users/jguillaumes/Arduino/libraries/SdFat/SdVolume.cpp
	@echo 'Building file: $<'
	@echo 'Starting C++ compile'
	"/Applications/Eclipse.app/Contents/Eclipse//arduinoPlugin/packages/arduino/tools/avr-gcc/4.9.2-atmel3.5.4-arduino2/bin/avr-g++" -c -g -Os -Wall -Wextra -std=gnu++11 -fpermissive -fno-exceptions -ffunction-sections -fdata-sections -fno-threadsafe-statics -flto -mmcu=atmega328p -DF_CPU=16000000L -DARDUINO=10802 -DARDUINO_AVR_UNO -DARDUINO_ARCH_AVR   -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/cores/arduino" -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/variants/standard" -I"/Users/jguillaumes/Arduino/libraries/OneWire-master" -I"/Users/jguillaumes/Arduino/libraries/SdFat" -I"/Users/jguillaumes/Arduino/libraries/SdFat/utility" -I"/Users/jguillaumes/Arduino/libraries/DHT" -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" -D__IN_ECLIPSE__=1 -x c++ "$<"  -o  "$@"
	@echo 'Finished building: $<'
	@echo ' '

libraries/SdFat/StdioStream.cpp.o: /Users/jguillaumes/Arduino/libraries/SdFat/StdioStream.cpp
	@echo 'Building file: $<'
	@echo 'Starting C++ compile'
	"/Applications/Eclipse.app/Contents/Eclipse//arduinoPlugin/packages/arduino/tools/avr-gcc/4.9.2-atmel3.5.4-arduino2/bin/avr-g++" -c -g -Os -Wall -Wextra -std=gnu++11 -fpermissive -fno-exceptions -ffunction-sections -fdata-sections -fno-threadsafe-statics -flto -mmcu=atmega328p -DF_CPU=16000000L -DARDUINO=10802 -DARDUINO_AVR_UNO -DARDUINO_ARCH_AVR   -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/cores/arduino" -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/variants/standard" -I"/Users/jguillaumes/Arduino/libraries/OneWire-master" -I"/Users/jguillaumes/Arduino/libraries/SdFat" -I"/Users/jguillaumes/Arduino/libraries/SdFat/utility" -I"/Users/jguillaumes/Arduino/libraries/DHT" -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" -D__IN_ECLIPSE__=1 -x c++ "$<"  -o  "$@"
	@echo 'Finished building: $<'
	@echo ' '

libraries/SdFat/istream.cpp.o: /Users/jguillaumes/Arduino/libraries/SdFat/istream.cpp
	@echo 'Building file: $<'
	@echo 'Starting C++ compile'
	"/Applications/Eclipse.app/Contents/Eclipse//arduinoPlugin/packages/arduino/tools/avr-gcc/4.9.2-atmel3.5.4-arduino2/bin/avr-g++" -c -g -Os -Wall -Wextra -std=gnu++11 -fpermissive -fno-exceptions -ffunction-sections -fdata-sections -fno-threadsafe-statics -flto -mmcu=atmega328p -DF_CPU=16000000L -DARDUINO=10802 -DARDUINO_AVR_UNO -DARDUINO_ARCH_AVR   -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/cores/arduino" -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/variants/standard" -I"/Users/jguillaumes/Arduino/libraries/OneWire-master" -I"/Users/jguillaumes/Arduino/libraries/SdFat" -I"/Users/jguillaumes/Arduino/libraries/SdFat/utility" -I"/Users/jguillaumes/Arduino/libraries/DHT" -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" -D__IN_ECLIPSE__=1 -x c++ "$<"  -o  "$@"
	@echo 'Finished building: $<'
	@echo ' '

libraries/SdFat/ostream.cpp.o: /Users/jguillaumes/Arduino/libraries/SdFat/ostream.cpp
	@echo 'Building file: $<'
	@echo 'Starting C++ compile'
	"/Applications/Eclipse.app/Contents/Eclipse//arduinoPlugin/packages/arduino/tools/avr-gcc/4.9.2-atmel3.5.4-arduino2/bin/avr-g++" -c -g -Os -Wall -Wextra -std=gnu++11 -fpermissive -fno-exceptions -ffunction-sections -fdata-sections -fno-threadsafe-statics -flto -mmcu=atmega328p -DF_CPU=16000000L -DARDUINO=10802 -DARDUINO_AVR_UNO -DARDUINO_ARCH_AVR   -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/cores/arduino" -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/variants/standard" -I"/Users/jguillaumes/Arduino/libraries/OneWire-master" -I"/Users/jguillaumes/Arduino/libraries/SdFat" -I"/Users/jguillaumes/Arduino/libraries/SdFat/utility" -I"/Users/jguillaumes/Arduino/libraries/DHT" -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" -D__IN_ECLIPSE__=1 -x c++ "$<"  -o  "$@"
	@echo 'Finished building: $<'
	@echo ' '


