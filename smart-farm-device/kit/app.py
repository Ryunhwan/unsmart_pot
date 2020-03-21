# -*-coding: utf-8 -*-
import os
import RPi.GPIO as GPIO
import Adafruit_DHT
import time
from time import time as unixtime
import datetime
import pyrebase
import threading

firebase_project_id = 'manu-smart-farm'
config = {
    "apiKey": "AIzaSyCCYpXxKwlT_-D76x2BdwSTUAADcNYZxd8",
    "authDomain": firebase_project_id + ".firebaseapp.com",
    "databaseURL": "https://" + firebase_project_id + ".firebaseio.com",
    "storageBucket": firebase_project_id + ".appspot.com"
}
firebase = pyrebase.initialize_app(config)
db = firebase.database()
db_user_id = '117997964887554732385' # static user

db_sensor_data_loc = 'users/' + db_user_id +'/sensor_data'
db_control_data_loc = 'users/' + db_user_id + '/control_data'

is_control_auto = db.child(db_control_data_loc + '/auto').get().val()
is_fan_on = db.child(db_control_data_loc + '/fan').get().val()
is_water_pump_on = db.child(db_control_data_loc + '/water_pump').get().val()
is_light_on = db.child(db_control_data_loc + '/light').get().val()

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
GPIO.output(18, is_fan_on)

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
            GPIO.output(18, is_fan_on)

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
    # TODO fan_control이 thread로 도는게 아니라
    # TODO 여기서 분기를 타는 방식으로 구현할 수도 있겠다
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
