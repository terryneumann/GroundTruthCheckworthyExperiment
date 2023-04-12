#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  2 16:29:09 2023

@author: tdn897
"""

import json
import os
import pandas as pd


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

def generate_gold_scores_dict(gold_attention_data):
    all_items = os.listdir(gold_attention_data)
    gold_scores = {}
    for item in all_items:
        with open(gold_attention_data + item) as json_file:
            gold = json.load(json_file)
            for row in range(len(gold)):
                dataObjectId = gold[row]['datasetObjectId']
                dataObject = gold[row]['dataObject']['content']
                annotations = json.loads(gold[row]['annotations'][0]['annotationData']['content'])['find_the_nouns']['entities']
                nouns_range = []
                for noun in range(len(annotations)):
                    start  = annotations[noun]['startOffset']
                    end = annotations[noun]['endOffset']
                    g = [i for i in range(start, end+1)]
                    nouns_range += g
                gold_scores.update({dataObjectId: {'content': dataObject, 'nouns_tokens': nouns_range}})
    return gold_scores
                    
                    

def calc_f1_score_text_span(gold, user):
    gold = set(gold)
    user = set(user)
    common = gold.intersection(user)
    num_same = len(common)
    if len(gold) == 0 or len(user) == 0:
        return int(gold == user)
    if num_same == 0:
        return 0
    precision = 1.0 * num_same / len(user)
    recall = 1.0 * num_same / len(gold)
    f1 = (2 * precision * recall) / (precision + recall)
    return f1


def raw_to_dict(consolidated_request):
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
                
                for worker in range(len(annotations)):
                    worker_response = annotations[worker]
                    worker_id = worker_response['workerId']
                    content_json = json.loads(worker_response['annotationData']['content'])             
                    
                    ### Extract Worker info
                    if content_json['yesOrNo']['no']:
                        for key in list(content_json.keys()):
                            content_json = score_fake_news_decipher(key=key, content_json=content_json)
                            if 'assessment' not in key and 'yesOrNo' not in key and 'mturk' not in key and 'attention' not in key and 'hit' not in key:
                                if worker_id not in list(worker_info.keys()):
                                    worker_info.update({worker_id: {key: content_json[key]}})
                                else:
                                    worker_info[worker_id].update({key:content_json[key]})
                    
                    
                    ### Extract Noun Info as Attention Check for Each Worker/Instance
                    # worker_labels = content_json['find_the_nouns']['entities']
                    # worker_nouns_list = []
                    # for noun in range(len(worker_labels)):
                    #     start  = worker_labels[noun]['startOffset']
                    #     end = worker_labels[noun]['endOffset']
                    #     g = [i for i in range(start, end+1)]
                    #     worker_nouns_list += g
                    # ### Calculate F1 score    
                    # gold_nouns_list = gold_scores_dict[dataObjectId]['nouns_tokens']
                    # f1 = calc_f1_score_text_span(gold = gold_nouns_list, user = worker_nouns_list)
                    
                    ### Extract Consolidated responses
                    if dataObjectId not in consolidated_responses:
                        consolidated_responses.update({dataObjectId:{'content': dataObject, 'responses': {}}})
                    for key in list(content_json.keys()):
                        if 'assessment' in key:
                            if worker_id not in list(consolidated_responses[dataObjectId]['responses'].keys()):
                                consolidated_responses[dataObjectId]['responses'].update({worker_id:{key:content_json[key]}})
                            else:
                                consolidated_responses[dataObjectId]['responses'][worker_id].update({key:content_json[key]})
                    consolidated_responses[dataObjectId]['responses'][worker_id].update({'mturk_username':content_json['mturk_username']})
                    #consolidated_responses[dataObjectId]['responses'][worker_id].update({'f1_attention_check': f1})
                                
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
worker_items_dir = 'checkworthy-pre-experiment-pilot-mt-2/annotations/worker-response/iteration-1'
consolidated_request = 'checkworthy-pre-experiment-pilot-mt-2/annotations/consolidated-annotation/consolidation-request/iteration-1/'
#gold_attention_data = 'checkworthy-pre-experiment-15c/checkworthy-pre-experiment-pilot-nouns-gold/annotations/consolidated-annotation/consolidation-request/iteration-1/'

#gold_scores_dict = generate_gold_scores_dict(gold_attention_data=gold_attention_data)
worker_info, consolidated_responses = raw_to_dict(consolidated_request=consolidated_request)
consolidated_responses_frame, worker_info_frame = dict_to_dataframe(worker_info = worker_info, consolidated_responses = consolidated_responses)
consolidated_responses_frame['response_length'] = consolidated_responses_frame.assessment_checkworthy_justification.str.len()

consolidated_responses_frame.to_csv('../experimental_data_clean/consolidated_responses_clean.csv', index=False)
worker_info_frame.to_csv('../experimental_data_clean/worker_info_clean.csv')
        
        
            
                
                        