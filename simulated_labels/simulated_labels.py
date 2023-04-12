#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  2 13:12:18 2023

@author: tdn897
"""

import pandas as pd
import numpy as np
import json
import os
import openai
import wandb
import time
from sklearn.model_selection import train_test_split
from plotnine import *
from sklearn.metrics import mean_squared_error
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from bleu import list_bleu, multi_list_bleu


os.chdir('/Users/tdn897/Desktop/Misinformation Detection Paper/')

with open('openaikey.txt') as f:
    key = f.readlines()
openai.api_key = key[0]


d = pd.read_excel('GroundTruthPreExperiment.xlsx')      
train, test = train_test_split(d, test_size=0.5)




##############################
# training prompt - few shot
##############################


prompt = "Rate the following claim as 3 if the claim could cause significant harm if false. \
Rate the following claim as 2 if the claim could cause medium harm if false or if you are uncertain whether it could cause harm or not. \
Rate the following claim as 1 if the claim is unlikely to cause harm if false. \
Also, provide a brief (1-2 sentence) justification for your assessment. Write your responses like the following: RATING: [insert rating here] --- JUSTIFICATION: [insert justification here]"
   
example = 0
for index, row in train.iterrows():
    example += 1
    prompt = prompt + ' Example ' + str(example) + ': ' + row['source'] + ' => RATING: ' + str(row['gold_terry']) + ' --- JUSTIFICATION: ' + row['gold_justification_terry']
    
predicted_responses = []
for index, row in test.iterrows():
    time.sleep(2)
    given_prompt = prompt + ' \nExample: ' + str(row['source']) + ' => '
    response = openai.Completion.create(
        engine="text-davinci-001",
        prompt=given_prompt,
        temperature=0.5,
        max_tokens=500,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0)
    clean_response = response['choices'][0]['text'].strip()
    print(given_prompt + ' ' + clean_response)
    predicted_responses.append(clean_response)


ratings = []
justifications = []

for elem in predicted_responses:
    both = elem.split(' --- ')
    ratings.append(int(both[0].replace('RATING: ', '')))
    justifications.append(both[1].replace('JUSTIFICATION: ', ''))


test['few_shot_ratings'] = ratings
test['few_shot_justifications'] = justifications


##############################
# training prompt - zero shot
##############################


prompt = "Rate the following claim as 3 if the claim could cause significant harm if false. \
Rate the following claim as 2 if the claim could cause medium harm if false or if you are uncertain whether it could cause harm or not. \
Rate the following claim as 1 if the claim is unlikely to cause harm if false. \
Also, provide a brief (1-2 sentence) justification for your assessment. Write your responses like the following: RATING: [insert rating here] --- JUSTIFICATION: [insert justification here]"


predicted_responses = []
for index, row in test.iterrows():
    time.sleep(2)
    given_prompt = prompt + ' \Claim: ' + str(row['source']) + ' => '
    response = openai.Completion.create(
        engine="text-davinci-001",
        prompt=given_prompt,
        temperature=0.5,
        max_tokens=500,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0)
    clean_response = response['choices'][0]['text'].strip()
    print(given_prompt + ' ' + clean_response)
    predicted_responses.append(clean_response)


ratings = []
justifications = []

for elem in predicted_responses:
    both = elem.split(' --- ')
    ratings.append(int(both[0].replace('RATING: ', '')))
    justifications.append(both[1].replace('JUSTIFICATION: ', ''))


test['zero_shot_ratings'] = ratings
test['zero_shot_justifications'] = justifications

test.to_csv('gpt3_test_data.csv', index = False)


##############################
# evaluation of methods
##############################

def cosine_distance(a, b):
    return np.dot(a, b)/(np.linalg.norm(a)*np.linalg.norm(b))



test = pd.read_csv('gpt3_test_data.csv')


#MSE of labels
mean_squared_error(test['gold_terry'], test['zero_shot_ratings'])
mean_squared_error(test['gold_terry'], test['few_shot_ratings'])


#Justification similarity

cosine_zero_shot = []
cosine_few_shot = []

bleu_zero_shot = []
bleu_few_shot = []

model = SentenceTransformer('bert-base-nli-mean-tokens')

for index, row in test.iterrows():
    
    # Cosine distance of BERT sentence embeddings
    sentence_embeddings = model.encode([row['gold_justification_terry'], 
                                        row['zero_shot_justifications'],
                                        row['few_shot_justifications']])
    cosine_distance(sentence_embeddings[0][:], sentence_embeddings[1][:])
    cosine_zero_shot.append(cosine_distance(sentence_embeddings[0][:], sentence_embeddings[1][:]))
    cosine_few_shot.append(cosine_distance(sentence_embeddings[0][:], sentence_embeddings[2][:]))
    
    # BLEU score
    bleu_zero_shot.append(list_bleu([row['gold_justification_terry']], [row['zero_shot_justifications']]))
    bleu_few_shot.append(list_bleu([row['gold_justification_terry']], [row['few_shot_justifications']]))
    
    

np.mean(cosine_zero_shot)
np.mean(cosine_few_shot)

np.mean(bleu_zero_shot)
np.mean(bleu_few_shot)
