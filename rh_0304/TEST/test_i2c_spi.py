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
import busio
import adafruit_am2320

# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))


# create the I2C shared bus
i2c = busio.I2C(board.SCL, board.SDA)
am = adafruit_am2320.AM2320(i2c)



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
    value1 = mcp.read_adc_difference(0)
    print('Channel 0 minus 1: {0}'.format(value1))
    value2 = mcp.read_adc_difference(2)
    print('Channel 1 minus 2: {0}'.format(value2))
    value3 = mcp.read_adc_difference(3)
    print('Channel 2 minus 3: {0}'.format(value3))
    time.sleep(2)
#i2c
    print("Temperature: ", am.temperature)
    print("Humidity: ", am.relative_humidity)
    time.sleep(2)

