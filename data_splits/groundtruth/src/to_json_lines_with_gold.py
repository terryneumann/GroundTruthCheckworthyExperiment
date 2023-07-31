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
gt_raw = pd.read_excel('GroundTruthPreExperiment.xlsx')
gt_raw['source'] = 'Claim: ' + gt_raw['source']

non_gold = gt_raw.loc[~gt_raw.topic.str.contains('Gold')].reset_index().drop(columns=['index'])
gold = gt_raw.loc[gt_raw.topic.str.contains('Gold')]

# stratified sample by topic across the two splits
# odds of seeing a gold claim are > 1/3

non_gold_1 = non_gold.groupby('topic', group_keys=False).apply(lambda x: x.sample(frac=0.5))
non_gold_2 = non_gold[~non_gold.source.isin(non_gold_1.source.tolist())]

split0 = pd.concat([non_gold_1, gold]).\
    to_json('GroundTruthCheckworthyExperiment/GroundTruthCheckworthyExperiment/test_split0.manifest', 
            orient = 'records',
            lines=True)

split1 = pd.concat([non_gold_2, gold]).\
    to_json('GroundTruthCheckworthyExperiment/GroundTruthCheckworthyExperiment/test_split1.manifest', 
            orient = 'records',
            lines=True)

split_test = pd.DataFrame.from_dict({'source':['Hello'], 'topic':['test']}).\
    to_json('GroundTruthCheckworthyExperiment/GroundTruthCheckworthyExperiment/test_split_hello.manifest',
            orient = 'records', 
            lines=True)

gold_json = pd.Series(gold.topic.values,index=gold.source).to_dict()

with open("GroundTruthCheckworthyExperiment/GroundTruthCheckworthyExperiment/gold.json", "w") as outfile:
    json.dump(gold_json, outfile)
