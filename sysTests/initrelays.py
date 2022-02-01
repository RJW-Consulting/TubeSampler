##################################################

#           P26 ----> Relay_Ch1
#			P20 ----> Relay_Ch2
#			P21 ----> Relay_Ch3

##################################################
#!/usr/bin/python
# -*- coding:utf-8 -*-
import RPi.GPIO as GPIO
from datetime import datetime
import time

Relay_Ch1 = 26
Relay_Ch2 = 20
Relay_Ch3 = 21

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(Relay_Ch1,GPIO.OUT)
GPIO.setup(Relay_Ch2,GPIO.OUT)
GPIO.setup(Relay_Ch3,GPIO.OUT)

GPIO.output(Relay_Ch1,GPIO.HIGH) # set valve power relay off
GPIO.output(Relay_Ch2,GPIO.HIGH) # set pump power relay off
GPIO.output(Relay_Ch3,GPIO.LOW)  # set peripheral (MFCs, valve relay boards) power on

log = open('/home/pi/SamplerDev/sampler.log','a')
log.writelines(datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'  Power relays Initialized\n')
log.close()



