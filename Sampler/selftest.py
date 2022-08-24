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
import matplotlib.pyplot as plt

def times2secs(start, times):
    return [(t-start).total_seconds() for t in times]

sampler = Sampler()
tester = Tester(sampler)
print('System test initializing.')
tester.startSystemLeakTest()
done = False
fig, ax = plt.subplots()
capped = False
data = None
startTime = None


try:
    while not done:
        res = tester.checkTest(inletCapped=capped)
        if 'message' in res:
            print(res['message'])
        if res['state'] == TesterState.SYS_TEST_INITIALIZING:
            x=input('Then press Return')
            capped = True
            startTime = datetime.datetime.now()
        if res['state'] == TesterState.SYS_TEST_CONTINUING:
            data = res['data']
            ax.clear()
            ax.plot(times2secs(startTime,data['times']),data['clearingFlows'])
            fig.canvas.draw()
            fig.canvas.flush_events()        
        if res['state'] == TesterState.SYS_TEST_COMPLETE: 
            print('Test complete')
            if res['result'] == 'pass':
                print('No leaks detected.')
            else:
                print('Leak detected.')
            done = True
        time.sleep(0.1)
    
    x = input('Press enter.')
        


except KeyboardInterrupt:
    print('Aborting self test')
    sampler.setPump(False)
    sampler.setTube(16,False)

