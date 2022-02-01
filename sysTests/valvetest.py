import os
import sys

sys.path.append('/home/pi/SamplerDev/ModuleLibs/R421A08-rs485-8ch-relay-board-master')

import time
import relay_boards
import relay_modbus
import RPi.GPIO as GPIO
import busio
import board
from datetime import datetime
from board import SCL, SDA
from adafruit_neotrellis.neotrellis import NeoTrellis
from adafruit_neotrellis.multitrellis import MultiTrellis
import adafruit_tca9548a
import adafruit_ahtx0


# create the i2c object for the trellis
i2c = busio.I2C(SCL, SDA)

# Create the TCA9548A I2C multiplexer object and give it the I2C bus
tca = adafruit_tca9548a.TCA9548A(i2c)

trelli = [
    [NeoTrellis(i2c, False, addr=0x2E), NeoTrellis(i2c, False, addr=0x2F)]
    ]
trellis = MultiTrellis(trelli)

OFF = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 75, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
INDIGO = (60, 0, 255)
PURPLE = (180, 0, 255)
DPURPLE = (255, 0, 255)

# Create the RHT sensor objects for the two manifold modules
rht0 = adafruit_ahtx0.AHTx0(tca[4])
rht1 = adafruit_ahtx0.AHTx0(tca[5])

for y in range(4):
    for x in range(8):
        trellis.color(x, y, OFF)


Relay_Ch1 = 26
Relay_Ch2 = 20
Relay_Ch3 = 21

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(Relay_Ch1,GPIO.OUT)
GPIO.setup(Relay_Ch2,GPIO.OUT)
GPIO.setup(Relay_Ch3,GPIO.OUT)

GPIO.output(Relay_Ch1,GPIO.HIGH) # set valve power relay off

SERIAL_PORT = '/dev/ttyS0'

def check(res):
    print(res)

if __name__ == '__main__':
    print('Getting started R421A08 relay board\n')

    # Create MODBUS object
    _modbus = relay_modbus.Modbus(serial_port=SERIAL_PORT)

    # Open serial port
    try:
        _modbus.open()
    except relay_modbus.SerialOpenException as err:
        print(err)
        sys.exit(1)

    # Create relay board object
    board0 = relay_boards.R421A08(_modbus, address=1)
    board1 = relay_boards.R421A08(_modbus, address=2)

    print('Status all relays:')
    print('Module 1:')
    check(board0.print_status_all())
    print('Module 2:')
    check(board1.print_status_all())
    time.sleep(1)

    numValves = 16
    numTubes = 8
    tubeValves = [[1,16],[2,15],[3,14],[4,13],[5,12],[6,11],[7,10],[8,9]]

    def setValve(board, vnum, state):
        if state:
            board.on(vnum)
            GPIO.output(Relay_Ch1,GPIO.LOW) # set valve power relay on
        else:
            GPIO.output(Relay_Ch1,GPIO.HIGH) # set valve power relay off
            board.off(vnum)

    def tubeLights(board, tnum):
        tlights = [[[0,0],[0,1]],[[1,0],[1,1]],[[2,0],[2,1]],[[3,0],[3,1]],[[4,0],[4,1]],[[5,0],[5,1]],[[6,0],[6,1]],[[7,0],[7,1]],
                   [[0,2],[0,3]],[[1,2],[1,3]],[[2,2],[2,3]],[[3,2],[3,3]],[[4,2],[4,3]],[[5,2],[5,3]],[[6,2],[6,3]],[[7,2],[7,3]]]
        num = tnum
        if board == board1:
            num += 8
        return tlights[num]
    
    def setTube(board, tnum, state):
        lights = tubeLights(board, tnum)
        if state:
            board.on(tubeValves[tnum][0])
            board.on(tubeValves[tnum][1])
            trellis.color(lights[0][0], lights[0][1], GREEN)
            trellis.color(lights[1][0], lights[1][1], GREEN)
            GPIO.output(Relay_Ch1,GPIO.LOW) # set valve power relay on
        else:
            GPIO.output(Relay_Ch1,GPIO.HIGH) # set valve power relay off
            board.off(tubeValves[tnum][0])
            board.off(tubeValves[tnum][1])
            trellis.color(lights[0][0], lights[0][1], OFF)
            trellis.color(lights[1][0], lights[1][1], OFF)

    
    
    print('set all valves off')
    for i in range(1,numValves+1):
        setValve(board0,i,False)
        setValve(board1,i,False)

    dwellSecs = 60*20
    dwellSecs = 5
 
    while True:
        #for i in range(1,numValves+1):
        '''
        for i in range(7,7+1):
            print(datetime.now().strftime("%m/%d/%Y, %H:%M:%S")+' valve '+str(i)+' on')
            setValve(i,True)
            time.sleep(5)
            print(datetime.now().strftime("%m/%d/%Y, %H:%M:%S")+' valve '+str(i)+' off')
            setValve(i,False)
            time.sleep(1)
        '''
        print("\nTemperature 0: %0.1f C" % rht0.temperature)
        print("Humidity 0: %0.1f %%" % rht0.relative_humidity)
        print("\nTemperature 1: %0.1f C" % rht0.temperature)
        print("Humidity 1: %0.1f %%" % rht0.relative_humidity)
        if True:
            for i in range(0,numTubes):
                print(datetime.now().strftime("%m/%d/%Y, %H:%M:%S")+' tube '+str(i)+' on')
                setTube(board0,i,True)
                time.sleep(dwellSecs)
                print(datetime.now().strftime("%m/%d/%Y, %H:%M:%S")+' tube '+str(i)+' off')
                setTube(board0,i,False)
                time.sleep(1)
        if True:
            for i in range(0,numTubes):
            #for i in range(4,4+1):
                print(datetime.now().strftime("%m/%d/%Y, %H:%M:%S")+' tube '+str(i+8)+' on')
                setTube(board1,i,True)
                time.sleep(dwellSecs)
                print(datetime.now().strftime("%m/%d/%Y, %H:%M:%S")+' tube '+str(i+8)+' off')
                setTube(board1,i,False)
                time.sleep(1)
        
    '''
    print('Turn relay 1 on')
    check(board.on(1))
    time.sleep(1)

    print('Turn relay 1 off')
    check(board.off(1))
    time.sleep(1)

    print('Toggle relay 8')
    check(board.toggle(8))
    time.sleep(1)

    print('Latch relays 6 on, all other relays off')
    check(board.latch(6))
    time.sleep(1)

    print('Turn relay 4 on for 5 seconds, all other relays off')
    check(board.delay(4, delay=5))
    time.sleep(6)

    print('Turn relays 3, 7 and 8 on')
    check(board.toggle_multi([3, 7, 8]))
    time.sleep(1)

    print('Turn all relays on')
    check(board.on_all())
    time.sleep(1)

    print('Turn all relays off')
    check(board.off_all())
    time.sleep(1)
'''
    