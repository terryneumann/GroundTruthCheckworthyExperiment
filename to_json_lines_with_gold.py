#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  2 13:12:18 2023

@author: tdn897
"""

import pandas as pd
import json
import numpy as np
import os


os.chdir('/Users/tdn897/Desktop/Misinformation Detection Paper/')

nsplits = 2

gt_raw = pd.read_excel('GroundTruthPreExperiment.xlsx')


out = []
for index, row in gt_raw.iterrows():
    row['source'] = 'Claim: ' + row['source']
    out.append(row['labels'].split('|'))
    
gt_raw['labels'] = out

non_gold = gt_raw.loc[gt_raw['topic']!='Gold']
gold = gt_raw.loc[gt_raw['topic']=='Gold']


len_split = len(non_gold)/nsplits
arr = np.arange(len(non_gold))
np.random.shuffle(arr)


for spl in range(nsplits):
    start_split = int((spl*len_split))
    end_split = int(((spl + 1)*len_split)) - 1
    non_gold_split = non_gold.loc[non_gold.index.isin(arr[start_split:end_split])]
    lines = pd.concat([non_gold_split, gold])
    lines.to_json('GroundTruthCheckworthyExperiment/GroundTruthCheckworthyExperiment/test_split' + str(spl) + '.manifest', 
                  orient = 'records', 
                  lines=True)


