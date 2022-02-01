# Test of custom relay board using AW9523 GPIO extender driving
# 16x Stemma relay modules.  This is on channel 5 of a tca9548a
# I2C expander

import time
from datetime import datetime
import board
import busio
import adafruit_tca9548a
import adafruit_aw9523
import RPi.GPIO as GPIO
import adafruit_bme280

Relay_Ch1 = 26
Relay_Ch2 = 20
Relay_Ch3 = 21

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(Relay_Ch1,GPIO.OUT)
GPIO.setup(Relay_Ch2,GPIO.OUT)
GPIO.setup(Relay_Ch3,GPIO.OUT)

GPIO.output(Relay_Ch1,GPIO.HIGH) # set valve power relay off

# Create I2C bus as normal
i2c = busio.I2C(board.SCL, board.SDA)

# Create the TCA9548A object and give it the I2C bus
tca = adafruit_tca9548a.TCA9548A(i2c)

# Initialize the I2C GPIO extender that runs the relay modules
aw = adafruit_aw9523.AW9523(tca[5],address=0x58)

# Initialize the temperature/pressure sensors

#bme280a = adafruit_bme280.Adafruit_BME280_I2C(tca[5])


num_relays = 16

relay_pins = []
for i in range(0,num_relays):
    relay_pins.append(aw.get_pin(i))
    # relay is an output, initialize to low
    relay_pins[i].switch_to_output(value=False)



while True:
    for i in range(0,num_relays):
    #for i in range(6,8):
        #print("\nTemperature: %0.1f C" % bme280a.temperature)
        #print("Humidity: %0.1f %%" % bme280a.humidity)
        #print("Pressure: %0.1f hPa" % bme280a.pressure)
        print(datetime.now().strftime("%m/%d/%Y, %H:%M:%S")+" opening valve "+str(i))
        relay_pins[i].switch_to_output(value=False)
        relay_pins[i].value = True
        if relay_pins[i].value == True:
            print(" relay reads energized ")
        else:
            print(" relay reads denergized ")
        GPIO.output(Relay_Ch1,GPIO.LOW) # set valve power relay on
        time.sleep(5)
        GPIO.output(Relay_Ch1,GPIO.HIGH) # set valve power relay off
        time.sleep(0.01)
        #relay_pins[i].switch_to_output(value=False)
        print(datetime.now().strftime("%m/%d/%Y, %H:%M:%S")+" closing valve "+str(i))
        relay_pins[i].value = False
        time.sleep(1)
    
