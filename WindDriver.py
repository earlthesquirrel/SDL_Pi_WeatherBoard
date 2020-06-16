#!/usr/bin/env python
#
# Weather Board Driver
#

# imports

import sys
import time
from datetime import datetime
import random 
import binascii
import struct

import config

import subprocess
import RPi.GPIO as GPIO
import smbus

sys.path.append('./RTC_SDL_DS3231')
sys.path.append('./Adafruit_Python_GPIO')
sys.path.append('./Pi_WeatherRack_Earl')
sys.path.append('./SDL_Pi_TCA9545')


import SDL_DS3231
import Pi_WeatherRack as Pi_WeatherRack

import SDL_Pi_TCA9545
#/*=========================================================================
#    I2C ADDRESS/BITS
#    -----------------------------------------------------------------------*/
TCA9545_ADDRESS =                         (0x73)    # 1110011 (A0+A1=VDD)
#/*=========================================================================*/

#/*=========================================================================
#    CONFIG REGISTER (R/W)
#    -----------------------------------------------------------------------*/
TCA9545_REG_CONFIG            =          (0x00)
#    /*---------------------------------------------------------------------*/

TCA9545_CONFIG_BUS0  =                (0x01)  # 1 = enable, 0 = disable 
TCA9545_CONFIG_BUS1  =                (0x02)  # 1 = enable, 0 = disable 
TCA9545_CONFIG_BUS2  =                (0x04)  # 1 = enable, 0 = disable 
TCA9545_CONFIG_BUS3  =                (0x08)  # 1 = enable, 0 = disable 

#/*=========================================================================*/

################
# Device Present State Variables
###############

#indicate interrupt has happened from as3936

as3935_Interrupt_Happened = False;

config.DS3231_Present = False
config.ADS1015_Present = False
config.ADS1115_Present = False

#############
# Test Function to see if sensors present
#############

def returnStatusLine(device, state):

	returnString = device
	if (state == True):
		returnString = returnString + ":   \t\tPresent" 
	else:
		returnString = returnString + ":   \t\tNot Present"
	return returnString


###############   
#
# WeatherRack Weather Sensors
#
# GPIO Numbering Mode GPIO.BCM
#

anemometerPin = 26
rainPin = 21

# constants

SDL_MODE_INTERNAL_AD = 0
SDL_MODE_I2C_ADS1015 = 1    # internally, the library checks for ADS1115 or ADS1015 if found

#sample mode means return immediately.  THe wind speed is averaged at sampleTime or when you ask, whichever is longer
SDL_MODE_SAMPLE = 0
#Delay mode means to wait for sampleTime and the average after that time.
SDL_MODE_DELAY = 1

weatherStation = Pi_WeatherRack.Pi_WeatherRack(anemometerPin, rainPin, 0,0, SDL_MODE_I2C_ADS1015)

weatherStation.setWindMode(SDL_MODE_SAMPLE, 5.0)
#weatherStation.setWindMode(SDL_MODE_DELAY, 5.0)

################

# DS3231/AT24C32 Setup
filename = time.strftime("%Y-%m-%d%H:%M:%SRTCTest") + ".txt"
starttime = datetime.utcnow()

ds3231 = SDL_DS3231.SDL_DS3231(1, 0x68)


try:

	#comment out the next line after the clock has been initialized
	#ds3231.write_now()
	print "----------------- "
	print "DS3231=\t\t%s" % ds3231.read_datetime()
	config.DS3231_Present = True
	print "----------------- "
	print "----------------- "
	print " AT24C32 EEPROM"
	print "----------------- "
	print "writing first 4 addresses with random data"
	for x in range(0,4):
		value = random.randint(0,255)
		print "address = %i writing value=%i" % (x, value) 	
		ds3231.write_AT24C32_byte(x, value)
	print "----------------- "
	
	print "reading first 4 addresses"
	for x in range(0,4):
		print "address = %i value = %i" %(x, ds3231.read_AT24C32_byte(x)) 
	print "----------------- "

except IOError as e:
	#    print "I/O error({0}): {1}".format(e.errno, e.strerror)
	config.DS3231_Present = False
	# do the AT24C32 eeprom

###############   

# Main Loop - sleeps 10 seconds
# Tests all I2C and WeatherRack devices on Weather Board 


# Main Program

print ""
print "Weather Board Driver -- Wind Only"
print ""
print ""
print "Program Started at:"+ time.strftime("%Y-%m-%d %H:%M:%S")
print ""



print "----------------------"
print returnStatusLine("DS3231",config.DS3231_Present)
print returnStatusLine("ADS1015",config.ADS1015_Present)
print returnStatusLine("ADS1115",config.ADS1115_Present)
print "----------------------"


block1 = ""
block2 = ""

while True:

	print "----------------- "
	if (config.DS3231_Present == True):
		print " DS3231 Real Time Clock"
	else:
		print " DS3231 Real Time Clock Not Present"
	
	print "----------------- "
	#

	if (config.DS3231_Present == True):
		currenttime = datetime.utcnow()

		deltatime = currenttime - starttime
	 
		print "Raspberry Pi=\t" + time.strftime("%Y-%m-%d %H:%M:%S")

		print "DS3231=\t\t%s" % ds3231.read_datetime()
	
		print "DS3231 Temperature= \t%0.2f C" % ds3231.getTemp()
		print "----------------- "



	print "----------------- "
	print " WeatherRack Weather Sensors" 
	print " WeatherRack Local"	
	print "----------------- "
	#
	print "----------------- "


 	currentWindSpeed = weatherStation.current_wind_speed()/1.6
  	currentWindGust = weatherStation.get_wind_gust()/1.6
  	print("Wind Speed=\t%0.2f MPH")%(currentWindSpeed)

    	print("MPH wind_gust=\t%0.2f MPH")%(currentWindGust)
  	if (config.ADS1015_Present or config.ADS1115_Present):	
		print "Wind Direction=\t\t\t %0.2f Degrees" % weatherStation.current_wind_direction()
		print "Wind Direction Voltage=\t\t %0.3f V" % weatherStation.current_wind_direction_voltage()

	print "----------------- "

	if (config.FRAM_Present):
		print " FRAM Present"
	else:
		print " FRAM Not Present"
	print "----------------- "

        if (config.FRAM_Present):
		print "writing first 3 addresses with random data"
		for x in range(0,3):
			value = random.randint(0,255)
                	print "address = %i writing value=%i" % (x, value)
                	fram.write8(x, value)
        	print "----------------- "

        	print "reading first 3 addresses"
        	for x in range(0,3):
                	print "address = %i value = %i" %(x, fram.read8(x))
	print "----------------- "

	print "Sleeping 10 seconds"
	time.sleep(10.0)
