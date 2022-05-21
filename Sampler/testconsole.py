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
from samplerConsole import SamplerConsole
import os
import sys
from datetime import datetime
import time

# first, set up our arguments

s = Sampler()
con = SamplerConsole(s)



    
done = False
tube = 0
clearingFlow = 0
sampleFlow = 0

logsecs = 1

con.clear()


i=1
done=False

while not done:
    con.showStatus()
    con.move(20,1)
    print(str(i))
    time.sleep(logsecs)
    i+=1
    

     

       
   

