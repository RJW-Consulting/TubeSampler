#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 12:20:13 2022

@author: Robin Weber

tester.py

Sequential tube sampler leak testing module.

"""

import datetime
import time
import sampler
from enum import Enum

TARGET_MAX_SAMPLE_FLOW = 0.1 # SCCM
TARGET_SYSTEM_MAX_TIME = 30 # seconds
TARGET_MAX_CLEARING_FLOW = 0.001 # liters
TARGET_TUBE_MAX_TIME = 10 # seconds
TEST_SAMPLE_FLOW = 100.0 # SCCM
TEST_CLEARING_FLOW = 1.0 # SLPM
PUMP_WARMUP_SECS = 5
NUM_TUBES = 16

class TesterState(Enum):
    IDLE = 0
    SYS_TEST_INITIALIZING = 1
    SYS_TEST_STARTING = 2
    SYS_TEST_CONTINUING = 3
    SYS_TEST_COMPLETE = 4
    TUBE_TEST_INITIALIZING = 5
    TUBE_TEST_STARTING = 6
    TUBE_TEST_CONTINUING = 7
    TUBE_TEST_COMPLETE = 8
    

class TestType(Enum):
    NONE = 0
    SYSTEM_TEST = 1
    TUBE_TEST = 2

    
class Tester():
    def __init__(self, theSampler):
        self.sampler = theSampler
        self.test = TestType.NONE
        self.state = TesterState.IDLE
        self.inletCapped = False
        self.tubesInstalled = False
        self.tubeData = {}
        self.tubeResults = []
        self.tubeAvFlows = []
        self.clearData()
        self.startTime = None
        self.clearingFlowThreshold = TARGET_MAX_CLEARING_FLOW
        self.sampleFlowThreshold = TARGET_MAX_SAMPLE_FLOW
        self.tubeTestTime = TARGET_TUBE_MAX_TIME
        self.systemTestTime = TARGET_SYSTEM_MAX_TIME
        self.sampleFlow = TEST_SAMPLE_FLOW
        self.clearingFlow = TEST_CLEARING_FLOW
        self.pumpOnDelay = PUMP_WARMUP_SECS
        self.tubeNumber = 0
        self.tubesToTest = []
        self.tubesTested = []
        self.tubeStartTime = None
    
    def clearData(self):
        self.dataTimes = []
        self.dataSampleFlows = []
        self.dataClearingFlows = []
        self.dataSampleP = []
        self.dataClearingP = []
        self.dataInletP = []
        self.dataRegP = []
        
    def setClearingFlow(self,flow):
        self.clearingFlow = flow
        
    def setSampleFlow(self,flow):
        self.sampleFlow = flow
        
        
    def startSystemLeakTest(self):
        self.test = TestType.SYSTEM_TEST
        self.state = TesterState.SYS_TEST_INITIALIZING
        return
    
    def startTubeLeakTest(self, tubesToTest=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16], sampleFlowThresh=TARGET_MAX_SAMPLE_FLOW, testTime=TARGET_TUBE_MAX_TIME):
        self.test = TestType.TUBE_TEST
        self.tubesToTest = tubesToTest
        self.sampleFlowThreshold = sampleFlowThresh
        self.tubeTestTime = testTime
        self.state = TesterState.TUBE_TEST_INITIALIZING

        return
        
    def addDataPoint(self):
        time = datetime.datetime.now()
        ps = self.sampler.getPressures()
        cf = self.sampler.getClearingFlow()
        sf = self.sampler.getSampleFlow()
        self.dataTimes.append(time)
        self.dataSampleFlows.append(sf)
        self.dataClearingFlows.append(cf)
        self.dataSampleP.append(ps['p_samp'])
        self.dataClearingP.append(ps['p_clear'])
        self.dataInletP.append(ps['p_vac'])
        self.dataRegP.append(ps['p_reg'])
        
    def getDataDict(self):
        dataDict = {}
        dataDict['times'] = self.dataTimes
        dataDict['sampleFlows'] = self.dataSampleFlows
        dataDict['clearingFlows'] = self.dataClearingFlows
        dataDict['samplePs'] = self.dataSampleP
        dataDict['clearingPs'] = self.dataClearingP
        dataDict['inletPs'] = self.dataInletP
        dataDict['regPs'] = self.dataRegP
        return dataDict

    def getTubeData(self):
        if self.tubeNumber > 0:
            self.tubeData[self.tubeNumber] = self.getDataDict()
        return self.tubeData
        
    def setTube(self,tubenum):
        if self.tubeNumber > 0:
            self.sampler.setTube(self.tubeNumber,False)
        if tubenum > 0:
            self.sampler.setTube(tubenum,True,downstreamOnly=True)
            self.tubeNumber = tubenum
            self.tubeStartTime = datetime.datetime.now()
            
    def pumpDelay(self):
        st = datetime.datetime.now()
        while (datetime.datetime.now() - st).total_seconds() < self.pumpOnDelay:
            time.sleep(0.1)
        
    def checkTest(self, inletCapped=False, tubesInstalled=False):
        retVal = {}
        if self.test == TestType.SYSTEM_TEST:
            if self.state == TesterState.SYS_TEST_INITIALIZING:
                if not inletCapped:
                    # instruct user to cap inlet
                    retVal['message'] = 'Please cap off sample inlet.'
                else:                    
                    self.clearData()
                    self.state = TesterState.SYS_TEST_STARTING
                    self.inletCapped = inletCapped
            if self.state == TesterState.SYS_TEST_STARTING:
                # take a first data point while pump is off
                self.addDataPoint()
                # Assume user has capped inlet, turn on the pump
                self.sampler.setClearingFlow(self.clearingFlow)
                self.sampler.setSampleFlow(self.sampleFlow)
                self.sampler.setPump(True)
                self.pumpDelay()
                self.startTime = datetime.datetime.now()
                time.sleep(1)
                self.addDataPoint()
                retVal['message'] = 'System test started.'
                self.state = TesterState.SYS_TEST_CONTINUING
            if self.state == TesterState.SYS_TEST_CONTINUING:
                self.addDataPoint()
                retVal['message'] = 'Test in progress...'
                timeSpent = datetime.datetime.now() - self.startTime
                retVal['data'] = self.getDataDict()        
                if timeSpent.total_seconds() >= TARGET_SYSTEM_MAX_TIME:
                    clearingFlow = self.dataClearingFlows[-1]
                    sampleFlow = self.dataSampleFlows[-1]
                    if clearingFlow > self.clearingFlowThreshold or sampleFlow > self.sampleFlowThreshold:
                        retVal['result'] = 'fail'
                    else:
                        retVal['result'] = 'pass'
                    self.sampler.setPump(False)
                    self.state = TesterState.SYS_TEST_COMPLETE
                    retVal['message'] = 'System test complete.  Please uncap sample inlet.'
        if self.test == TestType.TUBE_TEST:
            if self.state == TesterState.TUBE_TEST_INITIALIZING:
                if not tubesInstalled:
                    # instruct user to cap inlet
                    retVal['message'] = 'Install and secure sample tubes.'
                else:                    
                    self.clearData()
                    self.state = TesterState.TUBE_TEST_STARTING
                    self.tubesInstalled = tubesInstalled
            if self.state == TesterState.TUBE_TEST_STARTING:
                # take a first data point while pump is off
                #self.addDataPoint()
                # Assume user has installed the tubes, turn on the pump
                self.sampler.setClearingFlow(self.clearingFlow)
                self.sampler.setSampleFlow(self.sampleFlow)
                self.sampler.setPump(True)
                self.pumpDelay()
                self.startTime = datetime.datetime.now()
                retVal['message'] = 'Tube test started.'
                self.setTube(self.tubesToTest.pop(0))
                self.state = TesterState.TUBE_TEST_CONTINUING
            if self.state == TesterState.TUBE_TEST_CONTINUING:
                self.addDataPoint()
                retVal['tubeData'] = self.getTubeData()
                retVal['message'] = 'Testing tube '+str(self.tubeNumber)+'...'
                timeSpent = datetime.datetime.now() - self.tubeStartTime
                if timeSpent.total_seconds() >= TARGET_TUBE_MAX_TIME:
                    numsamps = len(self.dataSampleFlows)
                    halfsamps = int(numsamps/2)
                    samps = self.dataSampleFlows[-halfsamps:]
                    sampleFlow = sum(samps)/len(samps)
                    if sampleFlow > self.sampleFlowThreshold:
                        self.tubeResults.append('fail')
                    else:
                        self.tubeResults.append('pass')
                    self.tubeAvFlows.append(sampleFlow)
                    if len(self.tubesToTest) > 0:
                        self.tubesTested.append(self.tubeNumber)                        
                        self.setTube(self.tubesToTest.pop(0))
                        self.clearData()
                    else:
                        self.tubesTested.append(self.tubeNumber)
                        self.setTube(0)
                        self.sampler.setPump(False)
                        self.state = TesterState.SYS_TEST_COMPLETE
                        retVal['message'] = 'Tube test complete.'
                retVal['tubeNumber'] = self.tubeNumber
                retVal['tubesTested'] = self.tubesTested
                retVal['results'] = self.tubeResults
                retVal['tubeAvFlows'] = self.tubeAvFlows
           
                
        if self.startTime:
            retVal['duration'] = datetime.datetime.now() - self.startTime
        retVal['test'] = self.test
        retVal['state'] = self.state
        return retVal

 