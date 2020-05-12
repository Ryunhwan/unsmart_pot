# -*-coding: utf-8 -*-
import os
import RPi.GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

import board
from time import time as unixtime
import datetime
import pyrebase
import threading
from numpy import interp

from check_function import *
from database import *
from sensor import *
from control import *

while True:
    time.sleep(5)
    if not check_internet_on():
        print('## CHECK INTERNET CONNECTION..')
        continue
    else:
        print('## SUCCESS INTERNET CONNECTION!')
        break


device = 'device1'
db_sensor_data_loc = device + '/sensor_data'
db_control_data_loc = device + '/control_data'
fan_gpio_pin = 4
ptc_gpio_pin = 18
pump_gpio_pin = 22
led_gpio_pin = 27

crop = get_data(device + '/config/crops')
print('## main crop: ', crop)

# remove sensor database
db.child(db_sensor_data_loc).remove()

print('## DATABASE ACCESS SUCCESS!')

mcp = get_mcp(0,0)
fan_status, ptc_status, water_pump_status, light_status = sensor_initialization()

set_data(db_control_data_loc + '/fan', fan_status)
set_data(db_control_data_loc + '/ptc', ptc_status)
set_data(db_control_data_loc + '/water_pump', water_pump_status)
set_data(db_control_data_loc + '/light', light_status)

# 자동제어인 경우
# 1초 간격으로 돌면서 서버에 저장된 목표치와 현재 수집한 센서 데이터 비교
# on/off 여부를 바로바로 결정

if crop == 'mush_insect':
    while True:
        temperature = get_temperature()
        air_humidity = get_air_humidity()
        soil_humidity = get_soil_humidity(mcp)
        lux = get_lux(mcp)
        temperature_goal = get_data(db_control_data_loc + '/temp_goal')
        soil_humidity_goal = get_data(db_control_data_loc + '/soil_humidity_goal')
        air_humidity_goal = get_data(db_control_data_loc + '/humidity_goal')

        print('# temperature: ', temperature)
        print('# temperature goal: ', temperature_goal)
        print('# air humidity: ', air_humidity)
        print('# air humidity goal: ', air_humidity_goal)
        print('# soil humidity: ', soil_humidity)
        print('# soil humidity goal: ', soil_humidity_goal)
        print('# lux: ', lux)

        is_ptc_on = get_data(db_control_data_loc + '/ptc')
        print('# ptc: ', is_ptc_on)
        ptc_control(is_ptc_on, temperature, temperature_goal)



elif crop == 'vege_fish':
    while True:
        temperature = get_temperature()
        air_humidity = get_air_humidity()
        water_level = get_water_level()
        lux = get_lux(mcp)
        temperature_goal = get_data(db_control_data_loc + '/temp_goal')
        air_humidity_goal = get_data(db_control_data_loc + '/humidity_goal')
        water_level_goal = get_data(db_control_data_loc + '/water_level_goal')

        print('# temperature: ', temperature)
        print('# temperature goal: ', temperature_goal)
        print('# air humidity: ', air_humidity)
        print('# air humidity goal: ', air_humidity_goal)
        print('# water level: ', water_level)
        print('# water level goal: ', water_level_goal)
        print('# lux: ', lux)