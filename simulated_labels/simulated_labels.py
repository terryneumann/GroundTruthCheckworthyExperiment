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
import openai
import wandb
import pandas as pd
import time
from sklearn.model_selection import train_test_split
from plotnine import *


key = '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'
openai.api_key = key
labelers_per_instance = 40
p_white = 0.8

checkworthiness = {'LGBTQ':{'White':0.4, 'Black':0.4},
                   'Black Americans':{'White':0.4, 'Black':0.7},
                   'Illegal Immigration':{'White':0.5, 'Black':0.5},
                   'USA':{'White':0.7, 'Black':0.4}
                  }



def race_function(p_white):
        if np.random.uniform() > p_white:
            return 'Black'
        else:
            return 'White'

def generate_labels(d, p_white, labelers_per_instance, checkworthiness):
    black_pct = []
    white_pct = []
    combined_pct = []
    for index, row in d.iterrows():
        score = {'White':[],'Black':[], 'Combined':[]}
        for labeler in range(labelers_per_instance):
            race = race_function(p_white = p_white)
            odds = checkworthiness[row['topic']][race]
            if np.random.uniform() <= odds:
                label = 1
            else:
                label = 0
            score[race].append(label)
            score['Combined'].append(label)
        white_pct.append(np.mean(score['White']))
        black_pct.append(np.mean(score['Black']))
        combined_pct.append(np.mean(score['Combined']))
    d['white_pct'] = white_pct
    d['black_pct'] = black_pct
    d['combined_pct'] = combined_pct
    return d


d = pd.read_excel('/Users/tdn897/Desktop/Misinformation Detection Paper/GroundTruthPreExperiment.xlsx')
d = generate_labels(d=d, 
                    p_white=p_white, 
                    labelers_per_instance=labelers_per_instance,
                    checkworthiness=checkworthiness)

        
train, test = train_test_split(d, test_size=0.4)



labels = ['white_pct', 'black_pct', 'combined_pct']


for label in labels:
    print('\n\n\n\n Label: ' + label)
    prompt = "Please give a rating between 0 and 1 for the following claim, with higher numbers indicating higher potential for harm to individual people or groups of people if left unverified. Rate the claim between 0.67 and 1 if you think the claim could cause significant harm if left unverified. Rate the claim between 0.34 and 0.66 if you are unsure whether it could cause harm if left unverified. Rate the claim between 0 and 0.33 if you think the claim is true and self-evident, or if you are sure that it's unlikely to cause any harm."   
    for index, row in train.iterrows():
        prompt = prompt + ' \nExample: ' + row['source'] + ' => Rating: ' + str(round(row[label], 3))
        
    predicted_responses = []
    for index, row in test.iterrows():
        time.sleep(2)
        given_prompt = prompt + ' \nExample: ' + str(row['source']) + ' => Rating: '
        response = openai.Completion.create(
            engine="text-davinci-001",
            prompt=given_prompt,
            temperature=0.2,
            max_tokens=256,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0)
        clean_response = response['choices'][0]['text'].strip()
        print(given_prompt + ' ' + clean_response)
        predicted_responses.append(float(clean_response))
    test[label + 'predicted'] = predicted_responses

g = (ggplot(test)
 + geom_boxplot(aes(x='topic', y='white_pctpredicted')))