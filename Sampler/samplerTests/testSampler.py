#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 27 09:37:02 2021

@author: pi
"""

from sampler import sampler
import datetime
import time

s = sampler()

setpoint = float(100)

s.setSampleFlow(setpoint)
time.sleep(0.001)

stats = s.getSampleMFCStatus()

dwellTime = 0.5

logfilename = '/home/pi/SamplerDev/logs/valveTest_HanPS_12V_ValveReplaced.dat'

s.setClearingFlow(1.0)
time.sleep(0.001)
s.setPump(True)

try:
    for tube in range(1,17):
        s.setTube(tube,True)
        lastTime = datetime.datetime.now()
        while (datetime.datetime.now()-lastTime).total_seconds() < (dwellTime*60):
            logline = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S.%f ,")+str(tube)+', '+str(round(s.getSampleFlow(),1))
            print(logline)
            f = open(logfilename,'a')
            f.write(logline+'\n')
            f.close()
    s.setPump(False)
    s.setTube(16,False)
    print('Test complete')       
except KeyboardInterrupt:
    print('Aborting test')
    s.setPump(False)
    s.setTube(16,False)       
    



