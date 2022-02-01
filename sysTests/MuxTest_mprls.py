# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# This example shows using two TSL2491 light sensors attached to TCA9548A channels 0 and 1.
# Use with other I2C sensors would be similar.
import time
import board
import busio
import adafruit_mprls
import adafruit_tca9548a
import adafruit_bme280


# Create I2C bus as normal
i2c = busio.I2C(board.SCL, board.SDA)

# Create the TCA9548A object and give it the I2C bus
tca = adafruit_tca9548a.TCA9548A(i2c)

#bme1 = adafruit_bme280.Adafruit_BME280_I2C(tca[3])
# For each sensor, create it using the TCA9548A channel instead of the I2C object
mprls0 = adafruit_mprls.MPRLS(tca[0])
mprls1 = adafruit_mprls.MPRLS(tca[1])
mprls2 = adafruit_mprls.MPRLS(tca[2])
mprls3 = adafruit_mprls.MPRLS(tca[3])

# After initial setup, can just use sensors as normal.
while True:
    try:
        print(int(mprls0.pressure), int(mprls1.pressure), int(mprls2.pressure), int(mprls3.pressure))
        #print(int(mprls0.pressure))
    except:
        pass
    time.sleep(0.5)
    
