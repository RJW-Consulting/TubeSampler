#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SeqSampler.py

Base-level command line application for running Goldstein Lab's
sequential sorbent tube sampler.

Created on Mon May 16 2021

@author: Robin Weber

Command line syntax:
    python seqsampler.py sequenceFileName [-w time to begin] [-l logFileName]
    
"""

from sampler import Sampler
from sequencer import Sequencer
from samplerConsole import SamplerConsole
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
parser.add_argument('--pumpoff')
parser.add_argument('--logsecs')
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

pumpoff = args.pumpoff

logfilename = '/home/pi/SamplerLogs/sampler_log_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'.txt'
if args.log:
    logfilename = '/home/pi/SamplerLogs/'+args.log
    
logsecs = 1
if args.logsecs:
    logsecs =float(args.logsecs)   
    


s = Sampler()
seq = Sequencer(s)
seq.load(seqFile)
con = SamplerConsole(s)



doTubes =[1,2,3,4,5,6,7,8,9,10,12,13,14,15,16]  # tube 11 is dead for now

def logLine():
    header = 'time,Pvac,Preg,Pclearing,Psample,Tsampler,clearingFlow,sampleFlow,tube,total1,total2,total3,total4,total5,total6,total7,total8,total9,total10,total11,total12,total13,total14,total15,total16'
    pressures = s.getPressures()
    temperatures = s.getTemperatures()
    pVac = round(pressures['p_vac'],0)
    pReg = round(pressures['p_reg'],0)
    pClear = round(pressures['p_clear'],0)
    pSamp = round(pressures['p_samp'],0)
    t=temperatures['t_mod0_l']
    if t:
        tSamp = round(t,1)
    else:
        tSamp = '***'
    clearingFlow = round(s.getClearingFlow(),1)
    sampleFlow = round(s.getSampleFlow(),1)
    tube = s.currentTube()
    totals = s.getTubeTotals()
    totals = [round(x,1) for x in totals]
    time = datetime.now().strftime("%m/%d/%Y %H:%M:%S.%f")
    line = f'{time},{pVac},{pReg},{pClear},{pSamp},{tSamp},{clearingFlow},{sampleFlow},{tube},{totals[0]},{totals[1]},{totals[2]},{totals[3]},{totals[4]},{totals[5]},{totals[6]},{totals[7]},{totals[8]},{totals[9]},{totals[10]},{totals[11]},{totals[12]},{totals[13]},{totals[14]},{totals[15]}'
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
        

if not pumpoff:
    s.setPump(True)
    
done = False
tube = 0
clearingFlow = 0
sampleFlow = 0

logline,header = logLine()
lineToLogFile(header)

con.clear()

try:
    while not done:
        newTube,clearingFlow,sampleFlow = seq.currentTubeAndFlows()
        if newTube == 0:
            s.setTube(tube,False)
        elif newTube != tube:
            tube = newTube
            s.setClearingFlow(clearingFlow)
            s.setSampleFlow(sampleFlow)
            s.setTube(tube,True)
        logline,header = logLine()
        lineToLogFile(logline)
        con.showStatus()
        con.msgline(datetime.now().strftime("%m/%d/%Y %H:%M:%S"))
        done = seq.done()
        if not done:
            time.sleep(logsecs)
    s.setPump(False)
    s.setTube(16,False)
    print('Sequence complete')       

except KeyboardInterrupt:
    print('Aborting sequence')
    s.setPump(False)
    s.setTube(16,False)
       
   

