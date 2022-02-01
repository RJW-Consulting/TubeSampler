#!/usr/bin/python3
# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import sys
import time

# Add system path to find relay_ Python packages
sys.path.append('.')
sys.path.append('..')
sys.path.append('/home/pi/PycharmProjects/samplerDev/R421A08-rs485-8ch-relay-board-master')
import relay_modbus
from relay_boards import AlicatMFC
import struct
import sampler

s = sampler.sampler()
# Required: Configure serial port, for example:
#   On Windows: 'COMx'
#   On Linux:   '/dev/ttyUSB0'
SERIAL_PORT = '/dev/ttyS0'

FUNCTION_WRITE_MULTIPLE_REGISTERS = 16

print('Getting started Alicat MFC\n')

# Create MODBUS object
_modbus = relay_modbus.Modbus(serial_port=SERIAL_PORT)


def hibyte(num):
    return num >> 8

def lobyte(num):
    return num & 0xFF

# Open serial port
try:
    _modbus.open()
except relay_modbus.SerialOpenException as err:
    print(err)
    sys.exit(1)

mfc = AlicatMFC.AlicatMFC(_modbus, address=3)

s.setPump(True)
print('setting to 1 LPM')
mfc.setpoint(1.0)
time.sleep(2)
rbdata = mfc.readback()
print(rbdata)
time.sleep(5)
print('setting to 5 LPM')
mfc.setpoint(5.0)
time.sleep(2)
rbdata = mfc.readback()
print(rbdata)
time.sleep(5)
print('setting to 3 LPM')
mfc.setpoint(3.0)
time.sleep(2)
rbdata = mfc.readback()
print(rbdata)
time.sleep(5)
s.setPump(False)
