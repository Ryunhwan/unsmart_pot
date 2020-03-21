# -*-coding: utf-8 -*-
import os
import RPi.GPIO as GPIO
import Adafruit_DHT
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import time
import board
from time import time as unixtime
import datetime
import pyrebase
import threading
from numpy import interp

import urllib.request
def internet_on(host='http://google.com'):
    try:
        urllib.request.urlopen(host) #Python 3.x
        print('internet connect')
        return True
    except:
        print('internet disconnect')
        return False

while True:
    time.sleep(5)
    if not internet_on():
        print('## CHECK INTERNET CONNECTION..')
        continue
    else:
        print('## SUCCESS INTERNET CONNECTION!')
        break

firebase_project_id = 'manu-smart-farm'
config = {
    "apiKey": "AIzaSyCCYpXxKwlT_-D76x2BdwSTUAADcNYZxd8",
    "authDomain": firebase_project_id + ".firebaseapp.com",
    "databaseURL": "https://" + firebase_project_id + ".firebaseio.com",
    "storageBucket": firebase_project_id + ".appspot.com"
}
firebase = pyrebase.initialize_app(config)
db = firebase.database()

#TODO 처음에 crop종류 읽어서 분기타도록 구현
device = ''
crop = 'mush_insect'
if crop == 'mush_insect':
    device = 'device1'
elif crop == 'vege_fish':
    device = 'device2'


db_sensor_data_loc = device + '/sensor_data'
db_control_data_loc = device + '/control_data'

###
is_control_auto = db.child(db_control_data_loc + '/auto').get().val()
is_fan_on = db.child(db_control_data_loc + '/fan').get().val()
is_water_pump_on = db.child(db_control_data_loc + '/water_pump').get().val()
is_light_on = db.child(db_control_data_loc + '/light').get().val()

humidity_goal = db.child(db_control_data_loc + '/humidity_goal').get().val()
lux_goal = db.child(db_control_data_loc + '/lux_goal').get().val()
soil_humidity_goal = db.child(db_control_data_loc + '/soil_humidity_goal').get().val()
temp_goal = db.child(db_control_data_loc + '/temp_goal').get().val()
water_level_goal = db.child(db_control_data_loc + '/water_level_goal').get().val()
###

print('@@@database access success@@@')

GPIO.setmode(GPIO.BCM) # set the board numbering system to BCM

# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

# mosfet pin setting
mosfet1 = 4  # FAN
mosfet2 = 18  # PTC
mosfet3 = 22  # PUMP
mosfet4 = 27  # LED

# HCR
PIN_TRIGGER = 24
PIN_ECHO = 23
GPIO.setup(PIN_TRIGGER, GPIO.OUT)
GPIO.setup(PIN_ECHO, GPIO.IN)

#MOSFET
GPIO.setup(mosfet1, GPIO.OUT)
GPIO.setup(mosfet2, GPIO.OUT)
GPIO.setup(mosfet3, GPIO.OUT)
GPIO.setup(mosfet4, GPIO.OUT)


sensor = Adafruit_DHT.DHT11
pin = 17
def get_humidity_temperature():
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    return humidity, temperature

print('MOSFET all off')
GPIO.output(4,False)   # fan
GPIO.output(18,False)  # ptc
GPIO.output(22,False)  # pump
GPIO.output(27,False)  # led
db.child(db_control_data_loc + '/water_pump').set(False)
db.child(db_control_data_loc + '/light').set(False)
db.child(db_control_data_loc + '/fan').set(False)
time.sleep(3)

# fan & ptc control
def temp_control():
    global is_fan_on
    while True:
        time.sleep(1)
        is_control_auto = db.child(db_control_data_loc + '/auto').get().val()
        is_fan_on = db.child(db_control_data_loc + '/fan').get().val()
        GPIO.output(4, is_fan_on)

        humidity, temperature = get_humidity_temperature()

        # auto 모드인 경우
        if is_control_auto:
            # 목표 온도보다 현재 온도가 높은 경우
            if temperature >= temp_goal:
                if is_fan_on:
                    print('fan on continue')
                else:
                    print('fan on!')
                    is_fan_on = True
                    GPIO.output(4, is_fan_on)
                    db.child(db_control_data_loc + '/fan').set(is_fan_on)
            # 목표 온도보다 현재 온도가 낮은 경우
            elif temperature < temp_goal:
                if is_fan_on:
                    print('heater on!')
                    GPIO.output(4, is_fan_on)
                    GPIO.output(18, True)
                else:
                    print('heater continue')
            else:
                continue

def temp_control_thread_start():
    temp_control_thread = threading.Thread(target=temp_control)
    temp_control_thread.daemon = True
    temp_control_thread.start()
    print('## temp control thread start')

def water_pump_control():
    global is_water_pump_on
    print(crop)
    if crop == 'vege_fish':
        while True:
            time.sleep(1)
            is_control_auto = db.child(db_control_data_loc + '/auto').get().val()
            is_water_pump_on = db.child(db_control_data_loc + '/water_pump').get().val()
            water_level_goal = db.child(db_control_data_loc + '/water_level_goal').get().val()

            GPIO.output(22, is_water_pump_on)

            GPIO.output(PIN_TRIGGER, GPIO.LOW)
            # print("Waiting for sensor to settle")
            time.sleep(1)
            print("Calculating distance")
            GPIO.output(PIN_TRIGGER, GPIO.HIGH)
            time.sleep(0.00001)
            GPIO.output(PIN_TRIGGER, GPIO.LOW)
            while GPIO.input(PIN_ECHO) == 0:
                pulse_start_time = time.time()
            while GPIO.input(PIN_ECHO) == 1:
                pulse_end_time = time.time()
            pulse_duration = pulse_end_time - pulse_start_time
            distance = round(pulse_duration * 17150)  # , 2
            print("Distance:", distance, "cm")

            # auto 모드인 경우
            if is_control_auto:
                # 목표 수위가 현재 수위보다 높은 경우
                if water_level_goal >= distance:
                    if is_water_pump_on:
                        print('water pump on continue')
                    else:
                        print('water pump on!')
                        is_water_pump_on = True
                        GPIO.output(22, is_water_pump_on)
                        db.child(db_control_data_loc + '/water_pump').set(is_water_pump_on)
                # 목표 수위가 현재 수위보다 낮은 경우
                elif water_level_goal < distance:
                    if is_water_pump_on:
                        print('water pump off!')
                        is_water_pump_on = False
                        GPIO.output(22, is_water_pump_on)
                        db.child(db_control_data_loc + '/water_pump').set(is_water_pump_on)
                    else:
                        print('water pump off continue')
                else:
                    continue

    elif crop == 'mush_insect':
        while True:
            time.sleep(1)
            soil_humidity_goal = db.child(db_control_data_loc + '/soil_humidity_goal').get().val()
            is_control_auto = db.child(db_control_data_loc + '/auto').get().val()
            is_water_pump_on = db.child(db_control_data_loc + '/water_pump').get().val()
            soil_humidity = round(interp(format(mcp.read_adc(1)),[0,1024],[100,0]),2)
            humidity, temperature = get_humidity_temperature()

            # auto 모드인 경우
            if is_control_auto:
                # 목표 흙습도가 현재 흙습도보다 높은 경우
                if soil_humidity_goal >= soil_humidity:
                    if is_water_pump_on:
                        print('water pump on continue')
                    else:
                        print('water pump on!')
                        is_water_pump_on = True
                        GPIO.output(22, is_water_pump_on)
                        db.child(db_control_data_loc + '/water_pump').set(is_water_pump_on)
                # 목표 흙습도가 현재 흙습도보다 낮은 경우
                elif soil_humidity_goal < soil_humidity:
                    if is_water_pump_on:
                        print('water pump off!')
                        is_water_pump_on = False
                        GPIO.output(22, is_water_pump_on)
                        db.child(db_control_data_loc + '/water_pump').set(is_water_pump_on)
                    else:
                        print('water pump off continue')
                else:
                    continue




def water_pump_control_thread_start():
    water_pump_control_thread = threading.Thread(target=water_pump_control)
    water_pump_control_thread.daemon = True
    water_pump_control_thread.start()
    print('## water pump control thread start')

def stream_handler(message):
    global is_control_auto, is_fan_on, is_water_pump_on, is_light_on
    print(message)
    is_control_auto = db.child(db_control_data_loc + '/auto').get().val()

    path = message["path"]
    data = message["data"]

    if path ==  '/light':
        GPIO.output(27, data)

    if not is_control_auto:
        try:
            if data['fan'] or not data['fan']:
                is_fan_on = data['fan']
                GPIO.output(4, is_fan_on)
        except:
            print('error')
        try:
            if path == '/fan':
                is_fan_on = data
                GPIO.output(4, is_fan_on)
        except:
            print('error')
        try:
            if data['water_pump'] or not data['water_pump']:
                is_water_pump_on = data['water_pump']
                GPIO.output(22, is_water_pump_on)
        except:
            print('error')
        try:
            if path == "/water_pump":
                is_water_pump_on = data
                GPIO.output(22, is_water_pump_on)
        except:
            print('error')

control_data_stream = db.child(db_control_data_loc).stream(stream_handler)


def run():
    print('start')
    temp_control_thread_start()
    water_pump_control_thread_start()

    while True:
        GPIO.output(PIN_TRIGGER, GPIO.LOW)
        # print("Waiting for sensor to settle")
        time.sleep(1)
        print("Calculating distance")
        GPIO.output(PIN_TRIGGER, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(PIN_TRIGGER, GPIO.LOW)
        while GPIO.input(PIN_ECHO) == 0:
            pulse_start_time = time.time()
        while GPIO.input(PIN_ECHO) == 1:
            pulse_end_time = time.time()
        pulse_duration = pulse_end_time - pulse_start_time
        distance = round(pulse_duration * 17150)
        humidity, temperature = get_humidity_temperature()
        now = int(unixtime())
        lux = round(interp(mcp.read_adc(0),[0,1024],[100,0]),2)
        soil_humidity = round(interp(format(mcp.read_adc(1)),[0,1024],[100,0]),2)
        data = {
            "date": now,
            "humidity": humidity,
            "temperature": temperature,
            "water_level": distance,
            "soil_humidity": soil_humidity,
            "lux": lux
        }
        print(data)
        # push to database
        db.child(db_sensor_data_loc).push(data)
        time.sleep(10)



if __name__ == '__main__':
    run()
