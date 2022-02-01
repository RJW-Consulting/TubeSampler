#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 27 09:37:02 2021

@author: pi
"""

from sampler import sampler
import datetime
import time


print('Starting temperature test')
s = sampler()

setpoint = float(100)

s.setSampleFlow(setpoint)
time.sleep(0.001)

stats = s.getSampleMFCStatus()

dwellTime = 10

logfilename = '/home/pi/SamplerDev/logs/SingleValveTes2.dat'

s.setClearingFlow(1.0)
time.sleep(0.001)
#s.setPump(True)

try:
    headerWritten = False
    for valve in range(1,9):
        s.setTube(valve,True)
        lastTime = datetime.datetime.now()
        while (datetime.datetime.now()-lastTime).total_seconds() < (dwellTime*60):
            print('getting temperatures')
            temps = s.getTemperatures()
            tline = str(round(temps['t_mod0_u'],1))+', '+str(round(temps['t_mod0_l'],1))+', '+str(round(temps['t_mod1_u'],1))+', '+str(round(temps['t_mod1_l'],1))
            print('getting pressures')
            pressures = s.getPressures()
            pline = str(round(pressures['p_vac'],1))+', '+str(round(pressures['p_reg'],1))+', '+str(round(pressures['p_clear'],1))+', '+str(round(pressures['p_samp'],1))
            logline = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S.%f ,")+str(valve)+', '+str(round(s.getSampleFlow(),1))+', '+tline+ ', '+pline
            print(logline)
            print('writing log file')
            f = open(logfilename,'a')
            if not headerWritten:
                f.write('time, valve, flow, Tmod0_upper, Tmod0_lower, Tmod1_upper, Tmod1_lower, Pvac, Preg, Pclear, Psamp \n')
                headerWritten = True
            f.write(logline+'\n')
            f.close()
            time.sleep(1)
        s.setTube(valve,False)
    s.setPump(False)
    s.setTube(16,False)
    print('Test complete')       
except KeyboardInterrupt:
    print('Aborting test')
    s.setPump(False)
    s.setTube(16,False)       
    



