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

firebase_project_id = 'manu-smart-farm'
config = {
    "apiKey": "AIzaSyCCYpXxKwlT_-D76x2BdwSTUAADcNYZxd8",
    "authDomain": firebase_project_id + ".firebaseapp.com",
    "databaseURL": "https://" + firebase_project_id + ".firebaseio.com",
    "storageBucket": firebase_project_id + ".appspot.com"
}
firebase = pyrebase.initialize_app(config)
db = firebase.database()

db_sensor_data_loc = 'device1/sensor_data'
db_control_data_loc = 'device1/control_data'

is_control_auto = db.child(db_control_data_loc + '/auto').get().val()
is_fan_on = db.child(db_control_data_loc + '/fan').get().val()
is_water_pump_on = db.child(db_control_data_loc + '/water_pump').get().val()
is_light_on = db.child(db_control_data_loc + '/light').get().val()

print('@@@database access success@@@')

GPIO.setmode(GPIO.BCM)
SPI_PORT = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

#mosfet pin setting
pin = 17
mosfet1 = 4 #FAN
mosfet2 = 18 #PTC
mosfet3 = 22 #PUMP
mosfet4 = 27 #LED

#HCR
PIN_TRIGGER = 24
PIN_ECHO = 23
GPIO.setup(PIN_TRIGGER, GPIO.OUT)
GPIO.setup(PIN_ECHO, GPIO.OUT)

def HCR_setting():
    GPIO.output(PIN_TRIGGER, GPIO.LOW)
    time.sleep(1)
    print('Calculating distance')
    GPIO.output(PIN_TRIGGER, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(PIN_TRIGGER, GPIO.LOW)
    while GPIO.input(PIN_ECHO) == 0:
        pulse_start_time = time.time()
    while GPIO.input(PIN_ECHO) == 1:
        pulse_end_time = time.time()
    pulse_duration = pulse_end_time - pulse_start_time
    distance = round(pulse_duration * 17150)
    print('Distance:',distance,'cm')

#MOSFET
GPIO.setup(mosfet1, GPIO.OUT)
GPIO.setup(mosfet2, GPIO.OUT)
GPIO.setup(mosfet3, GPIO.OUT)
GPIO.setup(mosfet4, GPIO.OUT)

print('MOSFET all off')
GPIO.output(4,False)
GPIO.output(18,False)
GPIO.output(22,False)
GPIO.output(27,False)
time.sleep(2)
print('start')
print('auto:', is_control_auto)
print('fan:', is_fan_on)
print('water_pump:', is_water_pump_on)
print('light:', is_light_on)

#HCR_setting()
GPIO.output(4,is_fan_on) #FAN
GPIO.output(18,False) #PTC
#GPIO.output(22,is_water_pump_on) #PUMP
GPIO.output(27,is_light_on) #LED


sensor = Adafruit_DHT.DHT11
print('Press Ctrl-C to quit...')
while True:
    # Grab the difference between channel 0 and 1 (i.e. channel 0 minus 1).
    # Note you can specify any value in 0-7 to grab other differences:
    #  - 0: Return channel 0 minus channel 1
    #  - 1: Return channel 1 minus channel 0
    #  - 2: Return channel 2 minus channel 3
    #  - 3: Return channel 3 minus channel 2
    #  - 4: Return channel 4 minus channel 5
    #  - 5: Return channel 5 minus channel 4
    #  - 6: Return channel 6 minus channel 7
    #  - 7: Return channel 7 minus channel 6
#spi
    values = [0]*8
    for i in range(8):
       # The read_adc function will get the value of the specified channel (0-7).
       values[i] = mcp.read_adc(i)
    #value1 = mcp.read_adc_difference(0)
    #print('Channel 0 minus 1: {0}'.format(value1))
    #value2 = mcp.read_adc_difference(2)
    #print('Channel 1 minus 2: {0}'.format(value2))
    #value3 = mcp.read_adc_difference(3)
    #print('Channel 2 minus 3: {0}'.format(value3))
    con = interp1d([0,1024],[100,0])
    int=0
    int= con(values[1])
    print('ch01 convert to '.int)
    print('ch00 : {0}'.format(values[0]))
    print('ch01 : {0}'.format(values[1]))
    print('ch02 : {0}'.format(values[2]))
    time.sleep(1)

    print('PTC & FAN  on')
    GPIO.output(4,True)
    GPIO.output(18,True)
    GPIO.output(22,False)
    GPIO.output(27,False)
    time.sleep(5)

    print('MOSFET all off')
    GPIO.output(4,False)
    GPIO.output(18,False)
    GPIO.output(22,False)
    GPIO.output(27,False)
    time.sleep(2)

#dht_11
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
    time.sleep(1)


    print('Fan only on')
    GPIO.output(4,True)
    GPIO.output(18,False)
    GPIO.output(22,False)
    GPIO.output(27,False)
    time.sleep(5)

    print('MOSFET all off')
    GPIO.output(4,False)
    GPIO.output(18,False)
    GPIO.output(22,False)
    GPIO.output(27,False)
    time.sleep(2)

#hcr
    GPIO.output(PIN_TRIGGER, GPIO.LOW)
    #print("Waiting for sensor to settle")
    time.sleep(1)
    print("Calculating distance")
    GPIO.output(PIN_TRIGGER, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(PIN_TRIGGER, GPIO.LOW)
    while GPIO.input(PIN_ECHO)==0:
     pulse_start_time = time.time()
    while GPIO.input(PIN_ECHO)==1:
     pulse_end_time = time.time()
    pulse_duration = pulse_end_time - pulse_start_time
    distance = round(pulse_duration * 17150) #, 2
    print("Distance:",distance,"cm")

    print('pump only on')
    GPIO.output(4,False)
    GPIO.output(18,False)
    GPIO.output(22,True)
    GPIO.output(27,False)
    time.sleep(5)

    print('MOSFET all off')
    GPIO.output(4,False)
    GPIO.output(18,False)
    GPIO.output(22,False)
    GPIO.output(27,False)
    time.sleep(2)

    print('LED only on')
    GPIO.output(4,False)
    GPIO.output(18,False)
    GPIO.output(22,False)
    GPIO.output(27,True)
    time.sleep(5)

    print('MOSFET all off')
    GPIO.output(4,False)
    GPIO.output(18,False)
    GPIO.output(22,False)
    GPIO.output(27,False)
    time.sleep(2)



    print('MOSFET all on')
    GPIO.output(4,True)
    GPIO.output(18,True)
    GPIO.output(22,True)
    GPIO.output(27,True)
    time.sleep(2)

    print('MOSFET all off')
    GPIO.output(4,False)
    GPIO.output(18,False)
    GPIO.output(22,False)
    GPIO.output(27,False)
    time.sleep(2)





ht_sensor = Adafruit_DHT.DHT11
def get_humidity_temperature():
    humidity, temperature = Adafruit_DHT.read_retry(ht_sensor, 22)
    return humidity, temperature

def fan_control():
    global is_fan_on
    while True:
        time.sleep(2)
        humidity, temperature = get_humidity_temperature()

        if is_control_auto:
            if temperature >= 28.0 and is_fan_on == False:
                print('fan on!')
                is_fan_on = True
            elif temperature <= 25.0 and is_fan_on == True:
                print('fan off!')
                is_fan_on = False
            else:
                continue
            db.child(db_control_data_loc + '/fan').set(is_fan_on)
            GPIO.output(4, is_fan_on)

def fan_control_thread_start():
    fan_control_thread = threading.Thread(target=fan_control)
    fan_control_thread.daemon = True
    fan_control_thread.start()


def stream_handler(message):
    global is_control_auto, is_fan_on, is_water_pump_on, is_light_on
    path = message["path"]
    data = message["data"]
    if path == "/auto":
        is_control_auto = data
    if path == "/fan":
        is_fan_on = data
        #if not is_control_auto:

    if path == "/light":
        is_light_on = data
    if path == "/water_pump":
        is_water_pump_on = data

control_data_stream = db.child(db_control_data_loc).stream(stream_handler)


def run():
    print('start')
    fan_control_thread_start()

    while True:
        time.sleep(10)
        humidity, temperature = get_humidity_temperature()
        now = int(unixtime())
        data = {"date": now, "humidity": humidity, "temperature": temperature}
        print(data)
        # push to database
        db.child(db_sensor_data_loc).push(data)



if __name__ == '__main__':
    run()

