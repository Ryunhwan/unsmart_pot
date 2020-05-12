
import RPi.GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import Adafruit_DHT

# HCR
PIN_TRIGGER = 24
PIN_ECHO = 23

# MOSFET
PIN_FAN = 4
PIN_PTC = 18
PIN_WATER_PUMP = 22
PIN_LED = 27

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

def get_air_humidity():
    sensor = Adafruit_DHT.DHT11
    pin = 17
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    return humidity

def get_air_temp():
    sensor = Adafruit_DHT.DHT11
    pin = 17
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    return temperature