#!/usr/bin/python3

import Adafruit_BBIO.GPIO as GPIO
import os

os.system('config-pin P9.17 spi_cs')
os.system('config-pin P9.18 spi')
os.system('config-pin P9.21 spi')
os.system('config-pin P9.22 spi_sclk')

GPIO.setup('P8_10', GPIO.OUT)
GPIO.output('P8_10',GPIO.HIGH)

GPIO.setup('P8_9', GPIO.OUT)
GPIO.output('P8_9',GPIO.HIGH)


print('\nSPI pins and CMODE are set\n')
