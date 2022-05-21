#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  8 10:43:12 2022

@author: Robin Weber

Unit tests for tube sampler hardware interface layer
"""

from sampler import sampler
import unittest

class TestSampler(unittest.TestCase):
#    def __init__(self,arg):
#        unittest.TestCase.__init__(self,arg)
#        self.sampler = sampler()
    @classmethod    
    def setUpClass(cls):
        cls.sampler = sampler()
        
    def test_rawVacPressure(self):
        p = TestSampler.sampler.getRawVacPressure()
        self.assertIsNotNone(p)
        self.assertGreater(p,0)
        self.assertLessEqual(p,2000)
        
    def test_regVacPressure(self):
        p = TestSampler.sampler.getRegVacPressure()
        self.assertIsNotNone(p)
        self.assertGreater(p,0)
        self.assertLessEqual(p,2000)
        
    def test_clearingVacPressure(self):
        p = TestSampler.sampler.getClearingPressure()
        self.assertIsNotNone(p)
        self.assertGreater(p,0)
        self.assertLessEqual(p,2000)
        
    def test_sampleVacPressure(self):
        p = TestSampler.sampler.getSamplePressure()
        self.assertIsNotNone(p)
        self.assertGreater(p,0)
        self.assertLessEqual(p,2000)
        
    def test_AmbientPressure0(self):
        p = TestSampler.sampler.getAmbientPressure0()
        self.assertIsNotNone(p)
        self.assertGreater(p,0)
        self.assertLessEqual(p,2000)

    def test_AmbientPressure1(self):
        p = TestSampler.sampler.getAmbientPressure1()
        self.assertIsNotNone(p)
        self.assertGreater(p,0)
        self.assertLessEqual(p,2000)
        
   
    
    