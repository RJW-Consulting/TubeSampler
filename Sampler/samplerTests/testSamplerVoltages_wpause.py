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

dwellTime = 20

logfilename = '/home/pi/SamplerDev/logs/samplingTest_ValvePower_wpause_12-5V_2secBetween.dat'

s.setClearingFlow(1.0)
time.sleep(0.001)
#s.setPump(True)

headerWritten = False

def writelog():
    global headerWritten
    header = 'time, tube, setpt, flow, clearing_flow, Tmod0_upper, Tmod0_lower, Tmod1_upper, Tmod1_lower,valve_I ,valve_Vbus, valve_Vshunt, Pvac, Preg, Pclear, Psamp \n'
    #print('getting temperatures')
    temps = s.getTemperatures()
    tline = str(round(temps['t_mod0_u'],1))+', '+str(round(temps['t_mod0_l'],1))+', '+str(round(temps['t_mod1_u'],1))+', '+str(round(temps['t_mod1_l'],1))
    #print('getting pressures')
    pressures = s.getPressures()
    #print('getting valve pwer')
    vpower = s.getValvePower()
    mfcStats = s.getSampleMFCStatus()
    mfcSetPoint = mfcStats['setpoint']
    pline = str(round(vpower['valve_I'],1))+', '+str(round(vpower['valve_Vbus'],2))+', '+str(round(vpower['valve_Vshunt'],3))+', '+str(round(pressures['p_vac'],1))+', '+str(round(pressures['p_reg'],1))+', '+str(round(pressures['p_clear'],1))+', '+str(round(pressures['p_samp'],1))
    logline = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S.%f ,")+str(tube)+', '+str(round(mfcSetPoint,1))+', '+str(round(s.getSampleFlow(),1))+', '+str(round(s.getClearingFlow(),2))+', '+tline+ ', '+pline
    print(header)
    print(logline)
    #print('writing log file')
    f = open(logfilename,'a')
    if not headerWritten:
        f.write(header+'\n')
        headerWritten = True
    f.write(logline+'\n')
    f.close()
    
    
try:
    headerWritten = False
    for tube in range(1,17):
        savetube = tube
        for i in range(0,15):
            tube = 0
            writelog()
            tube = savetube
            time.sleep(1)
        s.setTube(tube,True,pauseBetween=2)
        lastTime = datetime.datetime.now()
        while (datetime.datetime.now()-lastTime).total_seconds() < (dwellTime*60):
            writelog()
            time.sleep(1)
        s.setTube(tube,False)
    s.setPump(False)
    s.setTube(16,False)
    print('Test complete')       
except KeyboardInterrupt:
    print('Aborting test')
    s.setPump(False)
    s.setTube(16,False)       
    



