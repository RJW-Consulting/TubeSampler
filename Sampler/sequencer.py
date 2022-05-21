#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  7 10:35:16 2022

@author: pi
"""

"""
File: sequencer.py

Sorbent tube sampler sequencer class
Takes a sequence described by a CSV file and tells the tube number,
sample flow rate, and clearing flow rate to use at any given time 
within the sampling period.

Author: Robin Weber
Started: 4/5/2022 

This is a temporary script file.
"""

import datetime
import pandas as pd
import time
import sys
import sampler

NUM_TUBES = 16

COLUMN_TNUM = 'Tube number'
COLUMN_SFLOW = 'Sample flow [SCCM]'
COLUMN_CFLOW = 'Clearing flow [SLPM]'
COLUMN_SDATE = 'Start date'
COLUMN_EDATE = 'End date'
COLUMN_STIME = 'Start time'
COLUMN_ETIME = 'End time'
COLUMN_MAXVOL = 'Maximum volume [CC]'


dtypes = {COLUMN_TNUM:'int64',COLUMN_SFLOW:'float64',COLUMN_CFLOW:'float64',
          COLUMN_SDATE:'datetime64',COLUMN_EDATE:'datetime64',
          COLUMN_STIME:'datetime64', COLUMN_ETIME:'datetime64', 
          COLUMN_MAXVOL:'datetime64'}

class Sequencer():
    def __init__(self, sampler):
        self.sampler = sampler
        self.sequence = None
        self.step_done = None
        
    def load(self,filename):
        try:
            self.sequence = pd.read_csv(filename,parse_dates=[COLUMN_SDATE,COLUMN_EDATE,COLUMN_STIME,COLUMN_ETIME], infer_datetime_format=True)
            self.step_done = [False] * self.sequence.shape[0]
        except IOError as e:
            print("I/O error({0}): {1}".format(e.errno, e.strerror))
        except Exception as err:
            print(f"Unexpected error opening {filename} is",repr(err))
            sys.exit(1)  # or replace this with "raise" ?
        
    def numSteps(self):
        return self.sequence.shape[0]
    
    def tubeForStep(self, step):
        tube = 0
        if step < self.numSteps():
            tube = self.sequence.at[step,COLUMN_TNUM]
        return tube
    
    def clearingFlowForStep(self,step):
        flow = 0
        if step < self.numSteps():
            flow = self.sequence.at[step,COLUMN_CFLOW]
        return float(flow)
        
    def sampleFlowForStep(self,step):
        flow = 0
        if step < self.numSteps():
            flow = self.sequence.at[step,COLUMN_SFLOW]
        return float(flow)

    def maxVolumeForStep(self,step):
        flow = 0
        if step < self.numSteps():
            flow = self.sequence.at[step,COLUMN_MAXVOL]
        return flow
        
    
    def test_StartDate(self,line):
        retval = False
        startDate = self.sequence.at[line,COLUMN_SDATE]
        if pd.isna(startDate):
            retval = True
        else:
            now = datetime.datetime.now()
            if startDate <= now:
                retval = True
        return retval

    def test_EndDate(self,line):
        retval = False
        endDate = self.sequence.at[line,COLUMN_EDATE]
        if pd.isna(endDate):
            retval = True
        else:
            endDate = datetime.datetime.combine(endDate.date(),datetime.time(23,59,59))
            now = datetime.datetime.now()
            if endDate >= now:
                retval = True
        return retval

    def test_StartTime(self,line):
        retval = False
        startTime = self.sequence.at[line,COLUMN_STIME]
        if pd.isna(startTime):
            retval = True
        else:
            now = datetime.datetime.now()
            if startTime.time() <= now.time():
                retval = True
        return retval

    def test_EndTime(self,line):
        retval = False
        endTime = self.sequence.at[line,COLUMN_ETIME]
        if pd.isna(endTime):
            retval = True
        else:
            now = datetime.datetime.now()
            if endTime.time() >= now.time():
                retval = True
        return retval
    
    def test_step(self,line):
        tests = self.test_StartDate(line) 
        tests &= self.test_EndDate(line)  
        tests &= self.test_StartTime(line)  
        tests &= self.test_EndTime(line)  
        tests &= (not self.step_done[line])
        return tests
    
    def currentTube(self):
        tube = 0
        for step in range(0,self.numSteps()):
            if self.test_step(step):
                tube = self.tubeForStep(step)
                return tube
        return tube

    def updateTotals(self):
        self.sampler.updateTubeTotals()
        for step in range(0,self.numSteps()):
            tube = self.tubeForStep(step)
            total = self.sampler.getTubeTotal(tube)
            maxVol = self.maxVolumeForStep(step)
            if total >= maxVol:
                self.step_done[step] = True
        
        
    def currentTubeAndFlows(self):
        tube = 0
        clearingFlow = 0
        sampleFlow = 0
        self.updateTotals()
        for step in range(0,self.numSteps()):
            if self.test_step(step):
                tube = self.tubeForStep(step)
                clearingFlow = self.clearingFlowForStep(step)
                sampleFlow = self.sampleFlowForStep(step)
                return tube,clearingFlow,sampleFlow
        return tube,clearingFlow,sampleFlow
    
    def done(self):
        isdone = True
        for d in self.step_done:
            isdone &= d
        return isdone

