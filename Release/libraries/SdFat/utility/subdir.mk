################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
CPP_SRCS += \
/Users/jguillaumes/Arduino/libraries/SdFat/utility/FmtNumber.cpp 

LINK_OBJ += \
./libraries/SdFat/utility/FmtNumber.cpp.o 

CPP_DEPS += \
./libraries/SdFat/utility/FmtNumber.cpp.d 


# Each subdirectory must supply rules for building sources it contributes
libraries/SdFat/utility/FmtNumber.cpp.o: /Users/jguillaumes/Arduino/libraries/SdFat/utility/FmtNumber.cpp
	@echo 'Building file: $<'
	@echo 'Starting C++ compile'
	"/Applications/Eclipse.app/Contents/Eclipse//arduinoPlugin/packages/arduino/tools/avr-gcc/4.9.2-atmel3.5.4-arduino2/bin/avr-g++" -c -g -Os -Wall -Wextra -std=gnu++11 -fpermissive -fno-exceptions -ffunction-sections -fdata-sections -fno-threadsafe-statics -flto -mmcu=atmega328p -DF_CPU=16000000L -DARDUINO=10802 -DARDUINO_AVR_UNO -DARDUINO_ARCH_AVR   -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/cores/arduino" -I"/Applications/Eclipse.app/Contents/Eclipse/arduinoPlugin/packages/arduino/hardware/avr/1.6.20/variants/standard" -I"/Users/jguillaumes/Arduino/libraries/OneWire-master" -I"/Users/jguillaumes/Arduino/libraries/SdFat" -I"/Users/jguillaumes/Arduino/libraries/SdFat/utility" -I"/Users/jguillaumes/Arduino/libraries/DHT" -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" -D__IN_ECLIPSE__=1 -x c++ "$<"  -o  "$@"
	@echo 'Finished building: $<'
	@echo ' '


