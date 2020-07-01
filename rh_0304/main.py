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

while True:
    time.sleep(5)
    if not check_internet_on():
        print('## CHECK INTERNET CONNECTION..')
        continue
    else:
        print('## SUCCESS INTERNET CONNECTION!')
        break


crop = get_data(device + '/config/crops')
print('## main crop: ', crop)
mcp = get_mcp(0,0)

db.child(db_sensor_data_loc).remove() # remove sensor data in database

fan_status, ptc_status, water_pump_status, light_status = sensor_initialization()
set_data(db_control_data_loc + '/fan', fan_status)
set_data(db_control_data_loc + '/ptc', ptc_status)
set_data(db_control_data_loc + '/water_pump', water_pump_status)
set_data(db_control_data_loc + '/light', light_status)
print('## DATABASE ACCESS SUCCESS!')


# 수동제어
def stream_handler(message):
    print(message)
    path = message["path"]
    data = message["data"]

    try:
        if path == '/light':
            set_data(db_control_data_loc + '/light', data)
            GPIO.output(PIN_LED, data)
    except:
        print('error')
    try:
        if data['light'] or not data['light']:
            GPIO.output(PIN_LED, data['light'])
    except:
        print('error')

    try:
        if data['led_auto'] or not data['led_auto']:
            GPIO.output(PIN_LED, data['led_auto'])
    except:
        print('error')

    if path == 'soil_humidity_goal':
        set_data(db_control_data_loc + '/soil_humidity_goal', data)
    elif path == 'humidity_goal':
        set_data(db_control_data_loc + '/humidity_goal', data)
    elif path == 'temp_goal':
        set_data(db_control_data_loc + '/temp_goal', data)

    try:
        if data['fan'] or not data['fan']:
            GPIO.output(PIN_FAN, data['fan'])
    except:
        print('error')
    try:
        if path == '/fan':
            GPIO.output(PIN_FAN, data)
    except:
        print('error')
    try:
        if data['water_pump'] or not data['water_pump']:
            GPIO.output(PIN_WATER_PUMP, data['water_pump'])
    except:
        print('error')
    try:
        if path == "/water_pump":
            GPIO.output(PIN_WATER_PUMP, data)
    except:
        print('error')

control_data_stream = db.child(db_control_data_loc).stream(stream_handler)

# 자동제어
system_timer = 0
water_pump_timer = 0
while True:
    # 자동제어가 아닌 경우는 계속 스킵
    auto = get_data(db_control_data_loc + '/auto')
    if not auto:
        print('# 수동제어모드')
        continue
    temperature = get_temperature()
    air_humidity = get_air_humidity()
    water_level = get_water_level()
    soil_humidity = get_soil_humidity(mcp)
    lux = get_lux(mcp)
    data = {
        "date": int(unixtime()),
        "humidity": air_humidity,
        "temperature": temperature,
        "water_level": water_level,
        "soil_humidity": soil_humidity,
        "lux": lux,
    }
    print(data)
    db.child(db_sensor_data_loc).push(data) # push to database

    # 현재 시간 불러와서 led 제어
    hour_now = int(time.strftime('%H'))
    min_now = int(time.strftime('%M'))
    check_led_timer(hour_now, min_now)

    if crop == 'mush_insect':
        temperature_goal = get_data(db_control_data_loc + '/temp_goal')
        soil_humidity_goal = get_data(db_control_data_loc + '/soil_humidity_goal')
        air_humidity_goal = get_data(db_control_data_loc + '/humidity_goal')

        # print('# temperature: ', temperature)
        # print('# temperature goal: ', temperature_goal)
        # print('# air humidity: ', air_humidity)
        # print('# air humidity goal: ', air_humidity_goal)
        # print('# soil humidity: ', soil_humidity)
        # print('# soil humidity goal: ', soil_humidity_goal)
        # print('# lux: ', lux)

        is_ptc_on = get_data(db_control_data_loc + '/ptc')
        # print('# ptc: ', is_ptc_on)
        ptc_control(is_ptc_on, temperature, temperature_goal)

        is_water_pump_on = get_data(db_control_data_loc + '/water_pump')
        # print('# water_pump: ', is_water_pump_on)
        # water pump는 가끔 켜져야 함
        if water_pump_timer == 3:
            mush_water_pump_control(soil_humidity, soil_humidity_goal)
            water_pump_timer = 0
        else:
            water_pump_timer += 1


    elif crop == 'vege_fish':
        temperature_goal = get_data(db_control_data_loc + '/temp_goal')
        air_humidity_goal = get_data(db_control_data_loc + '/humidity_goal')
        water_level_goal = get_data(db_control_data_loc + '/water_level_goal')

        # print('# temperature: ', temperature)
        # print('# temperature goal: ', temperature_goal)
        # print('# air humidity: ', air_humidity)
        # print('# air humidity goal: ', air_humidity_goal)
        # print('# water level: ', water_level)
        # print('# water level goal: ', water_level_goal)
        # print('# lux: ', lux)

        is_ptc_on = get_data(db_control_data_loc + '/ptc')
        # print('# ptc: ', is_ptc_on)
        ptc_control(is_ptc_on, temperature, temperature_goal)

        # 물높이 자동제어 없어졌다고 해서 일단 빼놨음
        # is_water_pump_on = get_data(db_control_data_loc + '/water_pump')
        # print('# water_pump: ', is_water_pump_on)
        # fish_water_pump_control(is_water_pump_on, water_level, water_level_goal)

    if system_timer == 10000:
        db.child(db_sensor_data_loc).remove()  # remove sensor data in database
    else:
        system_timer += 1
