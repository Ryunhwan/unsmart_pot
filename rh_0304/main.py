# -*-coding: utf-8 -*-
import os
import RPi.GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import time
import board
from time import time as unixtime
import datetime
import pyrebase
import threading
from numpy import interp

from check_function import *
from database import *
from sensor import *

device = 'device1'
db_sensor_data_loc = device + '/sensor_data'
db_control_data_loc = device + '/control_data'
fan_gpio_pin = 4
ptc_gpio_pin = 18
pump_gpio_pin = 22
led_gpio_pin = 27

while True:
    time.sleep(5)
    if not check_internet_on():
        print('## CHECK INTERNET CONNECTION..')
        continue
    else:
        print('## SUCCESS INTERNET CONNECTION!')
        break

crop = get_data(device + '/config/crops')
print(crop) #

# remove sensor database
db.child(db_sensor_data_loc).remove()

print('@@@database access success@@@')

mcp = get_mcp(0,0)
sensor_initialization()
print('wait..')
time.sleep(2)

GPIO.output(4,True)   # fan on
GPIO.output(18,False)  # ptc off
GPIO.output(22,False)  # pump off
GPIO.output(27,False)  # led off

set_data(db_control_data_loc + '/fan', True)
set_data(db_control_data_loc + '/ptc', False)
set_data(db_control_data_loc + '/water_pump', False)
set_data(db_control_data_loc + '/light', False)

