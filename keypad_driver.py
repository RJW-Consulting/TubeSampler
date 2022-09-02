#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  1 11:48:27 2022

@author: Robin Weber

Sequential Tube Sampler Keypad Driver 
"""
import board
import digitalio
import adafruit_pcf8574
import keyboard
import time
import datetime

REPEAT_TIME = 0.1
TIME_TO_REPEAT = 0.5

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

upper_map = [['1','2','3','up'],
             ['4','5','6','down'],
             ['7','8','9','left'],
             ['.','0','enter','right']]

lower_map = ['enter','delete','backspace','tab']

for port in rowports0:
    port.switch_to_output(value=True)

for port in colports0:
    port.switch_to_input(pull=digitalio.Pull.UP)

for port in rowports1:
    port.switch_to_output(value=True)

for port in colports1:
    port.switch_to_input(pull=digitalio.Pull.UP)

    
done = False

def scanForKey():
   upperKey = None
   lowerKey = None
   
   for r in range(0,4):
       rowports0[r].value = False
       for c in range(0,4):
           val = colports0[c].value
           if not val:
               upperKey = upper_map[r][c]
       rowports0[r].value = True    
   for r in [0]:
       rowports1[r].value = False
       for c in range(0,4):
           val = colports1[c].value
           if not val:
               lowerKey = lower_map[c]
       rowports1[r].value = True
   return upperKey,lowerKey

def pressKey(upper,lower):
    if upper:
        keyboard.press_and_release(upper)
    if lower:
        keyboard.press_and_release(lower)

    
held = False
firstPress = True
firstDownTime = None
lastUpper = None
lastLower = None
    
while not done:
    upper,lower = scanForKey()
    if not upper and not lower:
        held = False
        firstDownTime = None
        lastUpper = lastLower = None
        firstPress = True
        continue
    else:
        if not held:
            firstDownTime = datetime.datetime.now()
    if (lastUpper == upper) and (lastLower == lower):
        held = True
    if firstPress:
        pressKey(upper,lower)
        lastUpper = upper
        lastLower = lower
        firstPress = False
    if held and (datetime.datetime.now() - firstDownTime).total_seconds() < TIME_TO_REPEAT:
        continue
    if held:
        pressKey(upper,lower)
        lastUpper = upper
        lastLower = lower
        time.sleep(REPEAT_TIME)
     
