#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  2 16:29:09 2023

@author: tdn897
"""

import json
import os
import pandas as pd
import numpy as np

def score_fake_news_decipher(key, content_json):
    if 'fake' in key and 'Real' in content_json[key]:
        content_json[key] = 0
    elif 'fake' in key and 'Fake' in content_json[key]:
        content_json[key] = 1
    elif 'real' in key and 'Real' in content_json[key]:
        content_json[key] = 1
    elif 'real' in key and 'Fake' in content_json[key]:
        content_json[key] = 0
    return content_json

def generate_gold_list(gold_attention_data):
    gt_raw = pd.read_excel(gold_attention_data)
    gold_list = gt_raw.loc[gt_raw['topic']=='Gold'].source.tolist()
    return gold_list
                    
               
def get_scores_from_assessments(content_json, max_likert):
    for key in list(content_json.keys()):
        if 'assessment' in key and 'specify' not in key:
            answer = False
            i = 0
            while not answer:
                i += 1
                answer = content_json[key][str(i)] 
            content_json[key] = i
    return content_json
            
            
def get_worker_info(key, worker_id, worker_info, content_json):
    if 'demog' in key or 'identification' in key:
        if worker_id not in list(worker_info.keys()):
            worker_info.update({worker_id: {key: content_json[key]}})
        else:
            worker_info[worker_id].update({key:content_json[key]})

def get_consolidated_responses(key, content_json, worker_id, consolidated_responses, dataObjectId):
    if 'assessment' in key:
        if worker_id not in list(consolidated_responses[dataObjectId]['responses'].keys()):
            consolidated_responses[dataObjectId]['responses'].update({worker_id:{key:content_json[key]}})
        else:
            consolidated_responses[dataObjectId]['responses'][worker_id].update({key:content_json[key]})




def raw_to_dict(consolidated_request, gold_list, max_likert_score):
    all_items = os.listdir(consolidated_request)
    worker_info = {}
    consolidated_responses = {}
    for item in all_items:
        with open(consolidated_request + item) as json_file:
            survey_responses = json.load(json_file)
            for row in range(len(survey_responses)):
                
                dataObjectId = survey_responses[row]['datasetObjectId']
                dataObject = survey_responses[row]['dataObject']['content']
                annotations = survey_responses[row]['annotations']
                                
                if dataObjectId not in consolidated_responses:
                    consolidated_responses.update({dataObjectId:{'content': dataObject, 'responses': {}}})

                
                for worker in range(len(annotations)):
                    worker_response = annotations[worker]
                    worker_id = worker_response['workerId']
                    content_json = json.loads(worker_response['annotationData']['content'])             
                    
                    ### Convert radio buttons to integer scores
                    content_json = get_scores_from_assessments(content_json = content_json, max_likert = max_likert_score)
                    
                    
                    ### 0. Add worker to dictionary if doesn't exist
                    if worker_id not in list(worker_info.keys()):
                        worker_info.update({worker_id:{'num_gold':0,
                                                       'num_gold_correct':0,
                                                       'num_questions':1}})
                    else:
                        worker_info[worker_id]['num_questions'] += 1
                        
                 
                    ### 1. Extract All Relevant Info from content_json
                    for key in list(content_json.keys()):
                        
                        content_json = score_fake_news_decipher(key=key, 
                                                                content_json=content_json)

                        
                        get_worker_info(key=key,
                                        worker_id = worker_id, 
                                        worker_info=worker_info,
                                        content_json=content_json)
                        
                        get_consolidated_responses(key=key, 
                                                    content_json=content_json, 
                                                    worker_id=worker_id, 
                                                    consolidated_responses=consolidated_responses, 
                                                    dataObjectId=dataObjectId)
                        
                        

                                
                    ### 2. Analyze gold data for each worker
                    if dataObject in gold_list:
                        worker_info[worker_id]['num_gold'] += 1
                        worker_veracity_score = content_json['assessment_truth']
                        if worker_veracity_score in [max_likert_score - 1, max_likert_score]:
                            worker_info[worker_id]['num_gold_correct'] += 1
                    
    return worker_info, consolidated_responses


def dict_to_dataframe(worker_info, consolidated_responses):
    
    worker_info_frame = pd.DataFrame.from_dict(worker_info, orient='index')
    
    response_frame = pd.DataFrame()
    for c in list(consolidated_responses.keys()):
        claim = consolidated_responses[c]['content']
        for worker in list(consolidated_responses[c]['responses'].keys()):
            worker_response = {c + '--' + worker: consolidated_responses[c]['responses'][worker]}
            row = pd.DataFrame.from_dict(worker_response, orient = 'index')
            row['claim'] = claim
            row['worker'] = worker
            response_frame = pd.concat([row, response_frame])
    # reorder columns
    cols = response_frame.columns.tolist()
    cols = cols[-1:] + cols[:-1]    
    cols = cols[-1:] + cols[:-1]
    response_frame = response_frame[cols]
    
    return response_frame, worker_info_frame


###############################
############## MAIN
###############################


os.chdir('/Users/tdn897/Desktop/Misinformation Detection Paper/GroundTruthCheckworthyExperiment/GroundTruthCheckworthyExperiment/experimental_data_raw/')

                   
consolidated_request_dir = ['checkworthy-pre-experiment-pilot-mt-3a/annotations/consolidated-annotation/consolidation-request/iteration-1/',
                        'checkworthy-pre-experiment-pilot-mt-3b/annotations/consolidated-annotation/consolidation-request/iteration-1/']
gold_attention_data = '../../../GroundTruthPreExperiment.xlsx'
max_likert_score = 6


gold_list = generate_gold_list(gold_attention_data=gold_attention_data)
consolidated_responses_frame = pd.DataFrame()
worker_info_frame = pd.DataFrame()


for i in range(len(consolidated_request_dir)):
    worker_info, consolidated_responses = raw_to_dict(consolidated_request=consolidated_request_dir[i],
                                                      gold_list = gold_list, 
                                                      max_likert_score = max_likert_score)
    
    cr_frame, wi_frame = dict_to_dataframe(worker_info = worker_info, 
                                           consolidated_responses = consolidated_responses)
    
    consolidated_responses_frame = pd.concat([cr_frame, consolidated_responses_frame])
    worker_info_frame = pd.concat([wi_frame, worker_info_frame])


consolidated_responses_frame.to_csv('../experimental_data_clean/consolidated_responses_clean.csv', index=False)
worker_info_frame.to_csv('../experimental_data_clean/worker_info_clean.csv')
        
        
            
                
                        