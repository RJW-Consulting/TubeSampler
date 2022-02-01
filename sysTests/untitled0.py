#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 24 17:43:48 2021

@author: pi
"""

from PyMenus import Menu

m = Menu()

def func():

  print("Hello, world.")

m.add_option("Option 1", func)

m.show()
