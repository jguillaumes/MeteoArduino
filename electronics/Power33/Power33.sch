EESchema Schematic File Version 2
LIBS:power
LIBS:device
LIBS:transistors
LIBS:conn
LIBS:linear
LIBS:regul
LIBS:74xx
LIBS:cmos4000
LIBS:adc-dac
LIBS:memory
LIBS:xilinx
LIBS:microcontrollers
LIBS:dsp
LIBS:microchip
LIBS:analog_switches
LIBS:motorola
LIBS:texas
LIBS:intel
LIBS:audio
LIBS:interface
LIBS:digital-audio
LIBS:philips
LIBS:display
LIBS:cypress
LIBS:siliconi
LIBS:opto
LIBS:atmel
LIBS:contrib
LIBS:valves
LIBS:Power33-cache
EELAYER 25 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L LM1117-3.3 U1
U 1 1 5B9C02EC
P 3050 1500
F 0 "U1" H 2900 1625 50  0000 C CNN
F 1 "LM1117-3.3" H 3050 1625 50  0000 L CNN
F 2 "TO_SOT_Packages_THT:TO-220_Horizontal" H 3050 1500 50  0001 C CNN
F 3 "" H 3050 1500 50  0001 C CNN
	1    3050 1500
	1    0    0    -1  
$EndComp
$Comp
L CP C2
U 1 1 5B9C03E7
P 3800 1750
F 0 "C2" H 3825 1850 50  0000 L CNN
F 1 "10uF" H 3825 1650 50  0000 L CNN
F 2 "Capacitors_THT:CP_Radial_D5.0mm_P2.50mm" H 3838 1600 50  0001 C CNN
F 3 "" H 3800 1750 50  0001 C CNN
	1    3800 1750
	1    0    0    -1  
$EndComp
$Comp
L CP C1
U 1 1 5B9C0441
P 2300 1750
F 0 "C1" H 2325 1850 50  0000 L CNN
F 1 "10uf" H 2325 1650 50  0000 L CNN
F 2 "Capacitors_THT:CP_Radial_D5.0mm_P2.50mm" H 2338 1600 50  0001 C CNN
F 3 "" H 2300 1750 50  0001 C CNN
	1    2300 1750
	1    0    0    -1  
$EndComp
$Comp
L USB_OTG J1
U 1 1 5B9C0550
P 2050 1050
F 0 "J1" H 1850 1500 50  0000 L CNN
F 1 "USB_OTG" H 1850 1400 50  0000 L CNN
F 2 "Connectors_USB:USB_Micro-B_Molex-105017-0001" H 2200 1000 50  0001 C CNN
F 3 "" H 2200 1000 50  0001 C CNN
	1    2050 1050
	1    0    0    -1  
$EndComp
NoConn ~ 2350 1050
NoConn ~ 2350 1150
NoConn ~ 2350 1250
NoConn ~ 1950 1450
$Comp
L R R1
U 1 1 5B9C07DE
P 4400 1650
F 0 "R1" V 4480 1650 50  0000 C CNN
F 1 "470" V 4400 1650 50  0000 C CNN
F 2 "Resistors_THT:R_Axial_DIN0414_L11.9mm_D4.5mm_P5.08mm_Vertical" V 4330 1650 50  0001 C CNN
F 3 "" H 4400 1650 50  0001 C CNN
	1    4400 1650
	1    0    0    -1  
$EndComp
$Comp
L LED D1
U 1 1 5B9C0814
P 4250 1900
F 0 "D1" H 4250 2000 50  0000 C CNN
F 1 "LED" H 4250 1800 50  0000 C CNN
F 2 "LEDs:LED-3MM" H 4250 1900 50  0001 C CNN
F 3 "" H 4250 1900 50  0001 C CNN
	1    4250 1900
	1    0    0    -1  
$EndComp
$Comp
L Conn_01x02_Male J2
U 1 1 5B9C0B7E
P 4950 1650
F 0 "J2" H 4950 1750 50  0000 C CNN
F 1 "Conn_01x02_Male" H 4950 1450 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x02_Pitch2.54mm" H 4950 1650 50  0001 C CNN
F 3 "" H 4950 1650 50  0001 C CNN
	1    4950 1650
	-1   0    0    -1  
$EndComp
$Comp
L Conn_01x02_Male J4
U 1 1 5B9C0B73
P 5900 1650
F 0 "J4" H 5900 1750 50  0000 C CNN
F 1 "Conn_01x02_Male" H 5900 1450 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x02_Pitch2.54mm" H 5900 1650 50  0001 C CNN
F 3 "" H 5900 1650 50  0001 C CNN
	1    5900 1650
	-1   0    0    -1  
$EndComp
$Comp
L Conn_01x02_Male J3
U 1 1 5B9C0BD3
P 5450 1650
F 0 "J3" H 5450 1750 50  0000 C CNN
F 1 "Conn_01x02_Male" H 5450 1450 50  0000 C CNN
F 2 "Pin_Headers:Pin_Header_Straight_1x02_Pitch2.54mm" H 5450 1650 50  0001 C CNN
F 3 "" H 5450 1650 50  0001 C CNN
	1    5450 1650
	-1   0    0    -1  
$EndComp
Wire Wire Line
	2050 1900 3850 1900
Wire Wire Line
	3050 1900 3050 1800
Connection ~ 3050 1900
Wire Wire Line
	2350 850  2750 850 
Wire Wire Line
	2750 850  2750 1500
Wire Wire Line
	2050 1450 2050 1900
Connection ~ 2300 1900
Wire Wire Line
	3800 1600 3800 1500
Wire Wire Line
	2300 1600 2300 1500
Wire Wire Line
	2300 1500 2750 1500
Wire Wire Line
	3800 1900 4100 1900
Connection ~ 3800 1900
Wire Wire Line
	4400 1800 4400 1900
Connection ~ 3800 1500
Wire Wire Line
	3800 1900 3800 2200
Wire Wire Line
	4750 2200 4750 1750
Wire Wire Line
	4750 1500 4750 1650
Connection ~ 4400 1500
Connection ~ 4750 1500
Connection ~ 4750 2200
Connection ~ 5250 1500
Wire Wire Line
	3350 1500 5700 1500
Wire Wire Line
	3800 2200 5700 2200
Wire Wire Line
	5250 2200 5250 1750
Wire Wire Line
	5250 1500 5250 1650
Wire Wire Line
	5700 1500 5700 1650
Wire Wire Line
	5700 2200 5700 1750
Connection ~ 5250 2200
$EndSCHEMATC
