# MISO = 23
# MOSI = 24
# CS   = 25
# mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

import time
# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

import time
import board
#import busio
import Adafruit_DHT

import RPi.GPIO as GPIO

from numpy import interp

GPIO.setmode(GPIO.BCM) # set the board numbering system to BCM

# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))


# Sensor should be set to Adafruit_DHT.DHT11,
# Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302.
sensor = Adafruit_DHT.DHT11

#dht11 pin setting
pin = 17

#mosfet pin setting
mosfet1 = 4 #FAN
mosfet2 = 18 #PTC
mosfet3 = 22 #PUMP
mosfet4 = 27 #LED


#HCR
PIN_TRIGGER = 24 #18
PIN_ECHO = 23 #16
GPIO.setup(PIN_TRIGGER, GPIO.OUT)
GPIO.setup(PIN_ECHO, GPIO.IN)

#MOSFET
GPIO.setup(mosfet1, GPIO.OUT)
GPIO.setup(mosfet2, GPIO.OUT)
GPIO.setup(mosfet3, GPIO.OUT)
GPIO.setup(mosfet4, GPIO.OUT)

print('MOSFETall off')
GPIO.output(4,False)
GPIO.output(18,False)
GPIO.output(22,False)
GPIO.output(27,False)


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
    print('ch00 : {0}'.format(values[0]))
    int=interp(format(values[1]),[0,1024],[100,0])
    print('ch01 : ',round(int,2),'%')
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


print('MOSFET all off')
GPIO.output(4,False)
GPIO.output(18,False)
GPIO.output(22,False)
GPIO.output(27,False)
GPIO.cleanup() # the clean-up function will reset all the configurations made in this script.
