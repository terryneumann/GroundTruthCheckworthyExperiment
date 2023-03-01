#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  2 13:12:18 2023

@author: tdn897
"""

import pandas as pd
import json

gt_raw = pd.read_excel('/Users/tdn897/Desktop/Misinformation Detection Paper/GroundTruthPreExperiment.xlsx')

out = []
for index, row in gt_raw.iterrows():
    row['source'] = 'Claim: ' + row['source']
    out.append(row['labels'].split('|'))
    
gt_raw['labels'] = out
gt_raw.to_json('/Users/tdn897/Desktop/Misinformation Detection Paper/GroundTruthCheckworthyExperiment/GroundTruthCheckworthyExperiment/test.manifest', orient = 'records', lines=True)
