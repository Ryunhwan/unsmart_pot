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

device = 'device1'
crop_loc = device + '/config/crops'
crop = db.child(crop_loc).get().val()
print(crop)

db_sensor_data_loc = device + '/sensor_data'
db_control_data_loc = device + '/control_data'

# remove sensor database
db.child(db_sensor_data_loc).remove()

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
GPIO.output(4,True)   # fan
GPIO.output(18,False)  # ptc
GPIO.output(22,False)  # pump
GPIO.output(27,False)  # led

db.child(db_control_data_loc + '/water_pump').set(False)
db.child(db_control_data_loc + '/light').set(False)
db.child(db_control_data_loc + '/fan').set(True)
db.child(db_control_data_loc + '/ptc').set(False)
time.sleep(3)

# fan & ptc control
def temp_control():
    global is_fan_on
    while True:
        time.sleep(1)

        is_control_auto = db.child(db_control_data_loc + '/auto').get().val()
        is_fan_on = db.child(db_control_data_loc + '/fan').get().val()
        temp_goal = db.child(db_control_data_loc + '/temp_goal').get().val()
        is_ptc_on = db.child(db_control_data_loc + '/ptc').get().val()

        print('is_fan_on: ', is_fan_on)
        print('is_ptc_on: ', is_ptc_on)
        humidity, temperature = get_humidity_temperature()
        print('temp_goal: ', temp_goal)
        print('temperature: ', temperature)

        # auto 모드인 경우
        if is_control_auto:
            db.child(db_control_data_loc + '/fan').set(True)
            if temperature >= temp_goal:
                if is_ptc_on:
                    print('# ptc off!')
                    is_ptc_on = False
                    GPIO.output(18, is_ptc_on)
                    db.child(db_control_data_loc + '/ptc').set(is_ptc_on)
                else:
                    print('# ptc off continue')
            elif temperature < temp_goal:
                if is_ptc_on:
                    print('# ptc on continue')
                else:
                    print('# ptc on!')
                    is_ptc_on = True
                    GPIO.output(18, is_ptc_on)
                    db.child(db_control_data_loc + '/ptc').set(is_ptc_on)
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
            soil_humidity_goal = db.child(db_control_data_loc + '/soil_humidity_goal').get().val()
            humidity_goal = db.child(db_control_data_loc + '/humidity_goal').get().val()
            is_control_auto = db.child(db_control_data_loc + '/auto').get().val()
            is_water_pump_on = db.child(db_control_data_loc + '/water_pump').get().val()
            soil_humidity = round(interp(format(mcp.read_adc(1)),[0,1024],[100,0]),2)
            humidity, temperature = get_humidity_temperature()
            water_level_goal = db.child(db_control_data_loc + '/water_level_goal').get().val()

            print('## water_pump_control')
            print('is_control_auto: ', is_control_auto)
            print('is_water_pump_on: ', is_water_pump_on)
            print('soil_humidity: ', soil_humidity)
            print('soil_humidity_goal: ', soil_humidity_goal)
            print('air_humidity: ', humidity)
            print('air_humidity_goal: ', humidity_goal)
            print('air_temperature: ', temperature)
            print('water_level_goal: ', water_level_goal)

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
            distance = 21 - round(pulse_duration * 17150)  # , 2
            print("Distance:", distance, "cm")

            # auto 모드인 경우
            if is_control_auto:
                if (water_level_goal >= distance) or (humidity_goal >= humidity):
                    if is_water_pump_on:
                        print('water pump on continue')
                    else:
                        print('water pump on!')
                        is_water_pump_on = True
                        GPIO.output(22, is_water_pump_on)
                        db.child(db_control_data_loc + '/water_pump').set(is_water_pump_on)
                elif (water_level_goal < distance) or (humidity_goal < humidity):
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
            humidity_goal = db.child(db_control_data_loc + '/humidity_goal').get().val()
            is_control_auto = db.child(db_control_data_loc + '/auto').get().val()
            is_water_pump_on = db.child(db_control_data_loc + '/water_pump').get().val()
            soil_humidity = round(interp(format(mcp.read_adc(1)),[0,1024],[100,0]),2)
            humidity, temperature = get_humidity_temperature()
            water_level_goal = db.child(db_control_data_loc + '/water_level_goal').get().val()

            print('## water_pump_control')
            print('is_control_auto: ', is_control_auto)
            print('is_water_pump_on: ', is_water_pump_on)
            print('soil_humidity: ', soil_humidity)
            print('soil_humidity_goal: ', soil_humidity_goal)
            print('air_humidity: ', humidity)
            print('air_humidity_goal: ', humidity_goal)
            print('air_temperature: ', temperature)
            print('water_level_goal: ', water_level_goal)

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
            distance = 21 - round(pulse_duration * 17150)  # , 2
            print("Distance:", distance, "cm")


            # auto 모드인 경우
            if is_control_auto:
                if (soil_humidity_goal >= soil_humidity) or (humidity_goal >= humidity) :
                    if is_water_pump_on:
                        print('water pump on continue')
                    else:
                        print('water pump on!')
                        is_water_pump_on = True
                        GPIO.output(22, is_water_pump_on)
                        db.child(db_control_data_loc + '/water_pump').set(is_water_pump_on)
                elif (soil_humidity_goal < soil_humidity) or (humidity_goal < humidity) :
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


# light control
def light_control():
    global is_light_on
    while True:
        time.sleep(1)
        is_control_auto = db.child(db_control_data_loc + '/auto').get().val()
        is_light_on = db.child(db_control_data_loc + '/light').get().val()
        lux_goal = db.child(db_control_data_loc + '/lux_goal').get().val()
        lux = round(interp(mcp.read_adc(0),[0,1024],[100,0]),2)

        print('## is_light_on: ', is_light_on)
        print('## lux_goal: ', lux_goal)
        print('## lux: ', lux)

        if is_control_auto:
            if lux >= lux_goal:
                if is_light_on:
                    print('## light off!')
                    is_light_on = False
                    GPIO.output(27, is_light_on)
                    db.child(db_control_data_loc + '/light').set(is_light_on)
                else:
                    print('## light off continue')
            elif lux < lux_goal:
                if is_light_on:
                    print('## light on continue')
                else:
                    print('## light on!')
                    is_light_on = True
                    GPIO.output(27, is_light_on)
                    db.child(db_control_data_loc + '/light').set(is_light_on)
            else:
                continue

def light_control_thread_start():
    light_control_thread = threading.Thread(target=light_control)
    light_control_thread.daemon = True
    light_control_thread.start()
    print('## light control thread start')


def stream_handler(message):
    global is_control_auto, is_fan_on, is_water_pump_on, is_light_on
    print(message)
    is_control_auto = db.child(db_control_data_loc + '/auto').get().val()

    path = message["path"]
    data = message["data"]

    if path ==  '/light':
        db.child(db_control_data_loc + '/light').set(data)
        GPIO.output(27, data)

    elif path == 'soil_humidity_goal':
        db.child(db_control_data_loc + '/soil_humidity_goal').set(data)
    elif path == 'humidity_goal':
        db.child(db_control_data_loc + '/humidity_goal').set(data)
    elif path == 'temp_goal':
        db.child(db_control_data_loc + '/temp_goal').set(data)


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
    light_control_thread_start()

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
        water_level = 21 - round(pulse_duration * 17150)
        humidity, temperature = get_humidity_temperature()
        now = int(unixtime())
        lux = round(interp(mcp.read_adc(0),[0,1024],[100,0]),2)
        soil_humidity = round(interp(format(mcp.read_adc(1)),[0,1024],[100,0]),2)
        data = {
            "date": now,
            "humidity": humidity,
            "temperature": temperature,
            "water_level": water_level,
            "soil_humidity": soil_humidity,
            "lux": lux,
        }
        print(data)
        # push to database
        db.child(db_sensor_data_loc).push(data)
        time.sleep(10)



if __name__ == '__main__':
    run()
