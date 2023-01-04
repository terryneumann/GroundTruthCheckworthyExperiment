#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  2 16:29:09 2023

@author: tdn897
"""

import json

with open('/Users/tdn897/Downloads/output1.json') as json_file:
    data1 = json.load(json_file)

with open('/Users/tdn897/Downloads/output2.json') as json_file:
    data2 = json.load(json_file)
