#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 14 09:33:23 2022

@author: pi
"""

import sampler
import time

s=sampler.sampler()

s.setSampleFlow(500)
s.setClearingFlow(1.0)
s.setPump(True)

try:
    while True:
        sampleFlow = s.getSampleFlow()
        print('sample flow = '+str(sampleFlow))
        time.sleep(0.5)
except KeyboardInterrupt:
    print('Aborting test')
    s.setPump(False)
