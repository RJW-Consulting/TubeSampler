#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SeqSampler.py

Base-level cammand-line application for running Goldstein Lab's
sequential sorbent tube sampler.

Created on Mon May 16 2021

@author: Robin Weber

Command line syntax:
    python seqsampler.py sequenceFileName [-w time to begin] [-l logFileName]
    
"""

from sampler import Sampler
from sequencer import Sequencer
import os
import sys
from datetime import datetime
import time
import argparse

# first, set up our arguments
parser = argparse.ArgumentParser(description='Control the sequential sampler.')
parser.add_argument('seqFile')
parser.add_argument('--wait')
parser.add_argument('--log')

args = parser.parse_args()

if not args.seqFile:
    print('Error: must specify sequence file')
    exit()

seqFile = args.seqFile

if not os.path.exists(seqFile):
    print('Sequence file "'+seqFile+'" does not exist.')
    exit()
    
waitStr = args.wait

waitTill = None
if waitStr:
    waitTill = datetime.strptime(waitStr,'%H:%M')
    n=datetime.now()
    n = n.replace(hour=waitTill.hour, minute=waitTill.minute, second=0, microsecond=0)
    waitTill = n


logfilename = '/home/pi/samplerLogs/sampler_log_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.txt'
if args.log:
    logfilename = '/home/pi/samplerLogs/'+args.log
    
    
    


s = Sampler()
seq = Sequencer(s)



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

if waitTill:
    while waitTill > datetime.now():
        timeToWait = waitTill-datetime.now()
        print(' waiting until '+waitTill.strftime("%m/%d/%Y %H:%M:%S.")+', time till start '+str(timeToWait)+'     ',end='\r')
        time.sleep(1)
        

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
    



