import time
import RPi.GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import Adafruit_DHT
from numpy import interp

from database import *

# HCR
PIN_TRIGGER = 24
PIN_ECHO = 23

# MOSFET
PIN_FAN = 4
PIN_PTC = 18
PIN_WATER_PUMP = 22
PIN_LED = 27

device = 'device1'
db_sensor_data_loc = device + '/sensor_data'
db_control_data_loc = device + '/control_data'

def get_mcp(SPI_PORT, SPI_DEVICE):
    return Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

def sensor_initialization():
    GPIO.setmode(GPIO.BCM)  # set the board numbering system to BCM

    GPIO.setup(PIN_TRIGGER, GPIO.OUT)
    GPIO.setup(PIN_ECHO, GPIO.IN)

    # MOSFET
    GPIO.setup(PIN_FAN, GPIO.OUT)
    GPIO.setup(PIN_PTC, GPIO.OUT)
    GPIO.setup(PIN_WATER_PUMP, GPIO.OUT)
    GPIO.setup(PIN_LED, GPIO.OUT)

    GPIO.output(PIN_FAN, False)  # fan
    GPIO.output(PIN_PTC, False)  # ptc
    GPIO.output(PIN_WATER_PUMP, False)  # pump
    GPIO.output(PIN_LED, False)  # led

    time.sleep(1)

    fan_status = True  # fan on
    ptc_status = False  # ptc off
    water_pump_status = False  # pump off
    led_status = False  # led off

    GPIO.output(PIN_FAN, fan_status)
    GPIO.output(PIN_PTC, ptc_status)
    GPIO.output(PIN_WATER_PUMP, water_pump_status)
    GPIO.output(PIN_LED, led_status)

    return fan_status, ptc_status, water_pump_status, led_status


def get_air_humidity():
    sensor = Adafruit_DHT.DHT11
    pin = 17
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    return humidity

def get_temperature():
    sensor = Adafruit_DHT.DHT11
    pin = 17
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    return temperature

def get_water_level():
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
    return water_level

def get_soil_humidity(mcp):
    return round(interp(format(mcp.read_adc(1)), [0, 1024], [100, 0]), 2)

def get_lux(mcp):
    return round(interp(mcp.read_adc(0), [0, 1024], [100, 0]), 2)

def ptc_control(is_ptc_on, temperature, temp_goal):
    if temperature >= temp_goal:
        if is_ptc_on:
            print('# ptc off')
            GPIO.output(PIN_PTC, False)
            set_data(db_control_data_loc + '/ptc', False)
            return
        else:
            print('# ptc off continue')
            return
    else:
        if not is_ptc_on:
            print('# ptc on continue')
            return
        else:
            print('# ptc on')
            GPIO.output(PIN_PTC, True)
            set_data(db_control_data_loc + '/ptc', True)
            return

def soil_water_pump_control(soil_humidity, soil_humidity_goal):
    if soil_humidity < soil_humidity_goal:
        GPIO.output(PIN_WATER_PUMP, True)
        set_data(db_control_data_loc + '/water_pump', True)
        time.sleep(1)
        GPIO.output(PIN_WATER_PUMP, False)
        set_data(db_control_data_loc + '/water_pump', False)