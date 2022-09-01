#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  1 11:48:27 2022

@author: pi
"""
import time
import board
import digitalio
import adafruit_pcf8574

print("PCF8574 keypad test")

i2c = board.I2C()
pcf0 = adafruit_pcf8574.PCF8574(i2c,address=0x20)
pcf1 = adafruit_pcf8574.PCF8574(i2c,address=0x21)

# These are the pin assignments for the 16 key pad

cols0 = [2,3,4,5]
rows0 = [0,1,7,6]

# These are the pin assignments for the 4 key pad

cols1 = [3,2,1,0]
rows1 = [4]

rowports0 = [pcf0.get_pin(n) for n in rows0]
colports0 = [pcf0.get_pin(n) for n in cols0]

rowports1 = [pcf1.get_pin(n) for n in rows1]
colports1 = [pcf1.get_pin(n) for n in cols1]

for port in rowports0:
    port.switch_to_output(value=True)

for port in colports0:
    port.switch_to_input(pull=digitalio.Pull.UP)

for port in rowports1:
    port.switch_to_output(value=True)

for port in colports1:
    port.switch_to_input(pull=digitalio.Pull.UP)

    
done = False

while not done:
   for r in range(0,4):
       rowports0[r].value = False
       for c in range(0,4):
           val = colports0[c].value
           if not val:
               print('upper',r,c,val)
       rowports0[r].value = True    
   for r in [0]:
       rowports1[r].value = False
       for c in range(0,4):
           val = colports1[c].value
           if not val:
               print('lower',r,c,val)
       rowports1[r].value = True    
       