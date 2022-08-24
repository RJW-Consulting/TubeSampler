#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 20 14:05:44 2022

@author: pi
"""

from sampler import Sampler
import time

# Sampler Console

basex = 1
basey = 1
colWid = 7
col0 = basex
col1 = col0 + colWid
col2 = col1 + colWid
col3 = col2 + colWid
col4 = col3 + colWid
col5 = col4 + colWid
col6 = col5 + colWid
col7 = col6 + colWid
col8 = col7 + colWid
col9 = col8 + colWid

lline1 = basey+1
vline1 = basey+2
lline2 = basey+3
vline2 = basey+4
lline3 = basey+6
vline3 = basey+7
lline4 = basey+9
vline4 = basey+10

mesline = 20


posits = {'lPvac':(lline1,col0, 'Pvac   '),
          'lPreg':(lline1,col1, 'Preg   '),
          'lPclr':(lline1,col2,'Pclr   '),
          'lPsamp':(lline1,col3,'Psamp  '),
          'lPmod0':(lline1,col4,'Pmod0  '),
          'lPmod1':(lline1,col5,'Pmod1  '),
          'lTmod0':(lline1,col6,'Tmod0  '),
          'lTmod1':(lline1,col7,'Tmod1  '),
          'lFclr':(lline1,col8,'Fclr  '),
          'lFsamp':(lline1,col9,'FSamp  '),
          'vPvac':(vline1,col0, '%.0f    '),
          'vPreg':(vline1,col1, '%.0f    '),
          'vPclr':(vline1,col2, '%.0f    '),
          'vPsamp':(vline1,col3, '%.0f    '),
          'vPmod0':(vline1,col4,'%.1f    '),
          'vPmod1':(vline1,col5,'%.1f    '),
          'vTmod0':(vline1,col6,'%.1f  '),
          'vTmod1':(vline1,col7,'%.1f  '),
          'vFclr':(vline1,col8,'%.3f  '),
          'vFsamp':(vline1,col9,'%.1f  '),

          'lSPclr':(lline2,col8,'SPclr  '),
          'lSPsamp':(lline2,col9,'SPsamp  '),
          'vSPclr':(vline2,col8,'%.3f  '),
          'vSPsamp':(vline2,col9,'%.1f  '),
          
          'lTot01':(lline3,col1, 'Tot01   '),
          'lTot02':(lline3,col2, 'Tot02   '),
          'lTot03':(lline3,col3, 'Tot03   '),
          'lTot04':(lline3,col4, 'Tot04   '),
          'lTot05':(lline3,col5, 'Tot05   '),
          'lTot06':(lline3,col6, 'Tot06   '),
          'lTot07':(lline3,col7, 'Tot07   '),
          'lTot08':(lline3,col8, 'Tot08   '),
          
          'vTot01':(vline3,col1, '%.0f   '),
          'vTot02':(vline3,col2, '%.0f   '),
          'vTot03':(vline3,col3, '%.0f   '),
          'vTot04':(vline3,col4, '%.0f   '),
          'vTot05':(vline3,col5, '%.0f   '),
          'vTot06':(vline3,col6, '%.0f   '),
          'vTot07':(vline3,col7, '%.0f   '),
          'vTot08':(vline3,col8, '%.0f   '),
          
          'lTot09':(lline4,col1, 'Tot09   '),
          'lTot10':(lline4,col2, 'Tot10   '),
          'lTot11':(lline4,col3, 'Tot11   '),
          'lTot12':(lline4,col4, 'Tot12   '),
          'lTot13':(lline4,col5, 'Tot13   '),
          'lTot14':(lline4,col6, 'Tot14   '),
          'lTot15':(lline4,col7, 'Tot15   '),
          'lTot16':(lline4,col8, 'Tot16   '),
          
          'vTot09':(vline4,col1, '%.0f   '),
          'vTot10':(vline4,col2, '%.0f   '),
          'vTot11':(vline4,col3, '%.0f   '),
          'vTot12':(vline4,col4, '%.0f   '),
          'vTot13':(vline4,col5, '%.0f   '),
          'vTot14':(vline4,col6, '%.0f   '),
          'vTot15':(vline4,col7, '%.0f   '),
          'vTot16':(vline4,col8, '%.0f   '),
          
          }
class SamplerConsole():
    
    def __init__(self, sampler):
        self.s = sampler
    

    def move (self,y, x):
        print("\033[%d;%dH" % (y, x),end='')
        
    def clear(self):
        blankln = ' '*80
        for y in range(0,24):
            self.move(y,0)
            print(blankln,end='')

    def putVal(self,label,value):
        l = posits['l'+label]
        self.move(l[0],l[1])
        print(l[2],end='')
        v = posits['v'+label]
        self.move(v[0],v[1])
        try:
            print(v[2]%value,end='')
        except:
            print('***   ',end='')

    def showStatus(self):
        ps = self.s.getPressures()
        self.putVal('Pvac',ps['p_vac'])
        self.putVal('Preg',ps['p_reg'])
        self.putVal('Pclr',ps['p_clear'])
        self.putVal('Psamp',ps['p_samp'])
        self.putVal('Pmod0',ps['p_mod0'])
        self.putVal('Pmod1',ps['p_mod1'])
        ts = self.s.getTemperatures()
        self.putVal('Tmod0',ts['t_mod0_l'])
        self.putVal('Tmod1',ts['t_mod1_u'])
        self.putVal('Fclr',self.s.getClearingFlow())
        self.putVal('Fsamp',self.s.getSampleFlow())
        stats = self.s.getClearingMFCStatus()
        self.putVal('SPclr',stats['setpoint'])
        stats = self.s.getSampleMFCStatus()
        self.putVal('SPsamp',stats['setpoint'])
        tots = self.s.getTubeTotals()
        for n in range(0,16):
            self.putVal('Tot'+'%02d'%(n+1),tots[n])
            
    def msgline(self,message):
        self.move(mesline,1)
        print(message)

# test code
'''
s = Sampler()
cons = SamplerConsole(s)

cons.clear()

done = False
i=0
try:
    while not done:
        cons.showStatus()
        time.sleep(1)        
        cons.move(20,0)
        print(i)
        i+=1
        

except KeyboardInterrupt:
    cons.move(20,0)
    print('Done')
    
'''    