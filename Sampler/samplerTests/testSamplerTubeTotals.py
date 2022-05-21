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
offTime = 0.1

logFileTime = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
logfilename = '/home/pi/SamplerDev/logs/tubeTotalsTest_'+logFileTime+'.csv'

doTubes =[1,2,3,4,5,6,7,8,9,10,12,13,14,15,16]  # tube 11 is dead for now

def logLine():
    header = 'time,Pvac,Preg,Pclearing,Psample,clearingFlow,sampleFlow,tube,total1,total2,total3,total4,total5,total6,total7,total8,total9,total10,total11,total12,total13,total14,total15,total16'
    pressures = s.getPressures()
    pVac = round(pressures['p_vac'],0)
    pReg = round(pressures['p_reg'],0)
    pClear = round(pressures['p_clear'],0)
    pSamp = round(pressures['p_samp'],0)
    clearingFlow = round(s.getClearingFlow(),1)
    sampleFlow = round(s.getSampleFlow(),1)
    tube = s.currentTube()
    totals = s.getTubeTotals()
    totals = [round(x,1) for x in totals]
    time = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S.%f")
    line = f'{time},{pVac},{pReg},{pClear},{pSamp},{clearingFlow},{sampleFlow},{tube},{totals[0]},{totals[1]},{totals[2]},{totals[3]},{totals[4]},{totals[5]},{totals[6]},{totals[7]},{totals[8]},{totals[9]},{totals[10]},{totals[11]},{totals[12]},{totals[13]},{totals[14]},{totals[15]}'
    return line,header

def lineToLogFile(logline):
    f = open(logfilename,'a')
    f.write(logline+'\n')
    f.close()

s.setClearingFlow(1.0)
time.sleep(0.001)
s.setPump(True)

try:
    logline,header = logLine()
    lineToLogFile(header)
    s.resetTubeTotals()
    s.resetSampleTotal()
    for tube in doTubes:
        s.setTube(tube,True)
        lastTime = datetime.datetime.now()
        while (datetime.datetime.now()-lastTime).total_seconds() < (dwellTime*60):
            s.updateTubeTotals()
            logline,header = logLine()
            print(header)
            print(logline)
            lineToLogFile(logline)
        s.setTube(tube,False)
        lastTime = datetime.datetime.now()
        while (datetime.datetime.now()-lastTime).total_seconds() < (offTime*60):
            s.updateTubeTotals()
            logline,header = logLine()
            print(header)
            print(logline)
            lineToLogFile(logline)
    s.setPump(False)
    s.setTube(16,False)
    print('Test complete')       
except KeyboardInterrupt:
    print('Aborting test')
    s.setPump(False)
    s.setTube(16,False)       
    



