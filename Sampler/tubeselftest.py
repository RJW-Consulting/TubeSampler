#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 15:09:23 2022
test shell fortester.py

@author: Robin Weber
"""

from sampler import Sampler
from tester import Tester, TesterState, TestType
import datetime
import time
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.pyplot import draw, show

def times2secs(start, times):
    return [(t-start).total_seconds() for t in times]

sampler = Sampler()
tester = Tester(sampler)
print('Tube self test initializing.')
tester.startTubeLeakTest(tubesToTest=[4,6])
done = False
capped = False
data = None
startTime = None
currTube = 0

winPos = 50
stagger = 20

def plotTube(tubeNum, res, pos):
    fig, ax = plt.subplots()
    data = res['tubeData'][tubeNum]
    ax.plot(times2secs(data['times'][0],data['times']),data['sampleFlows'])
    plt.title('tube '+str(tubeNum))
    plt.show(block=False)
    fig.canvas.manager.window.move(pos,pos)
    fig.canvas.draw()
    fig.canvas.flush_events()
    plt.pause(0.1)



try:
    while not done:
        res = tester.checkTest(tubesInstalled=capped)
        if 'message' in res:
            print(res['message'])
        if res['state'] == TesterState.TUBE_TEST_INITIALIZING:
            x=input('Then press Return')
            capped = True
            startTime = datetime.datetime.now()
        if res['state'] == TesterState.TUBE_TEST_CONTINUING:
            if currTube != res['tubeNumber']:
                if currTube:
                    plotTube(currTube,res,winPos)
                    winPos += stagger
                currTube = res['tubeNumber']
        if res['state'] == TesterState.SYS_TEST_COMPLETE: 
            plotTube(res['tubeNumber'],res,winPos)
            print('Test complete, results:')
            for t,r,f in zip(res['tubesTested'],res['results'],res['tubeAvFlows']):
                print('Tube '+str(t)+': '+r+'  Av Flow: '+str(f)+' SCCM')
            done = True
        time.sleep(0.1)
    
    x = input('Press enter.')
        


except KeyboardInterrupt:
    print('Aborting self test')
    sampler.setPump(False)
    sampler.setTube(16,False)

