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

def generate_gold_dict(gold_attention_data):
    gold_dict = {}
    gt_raw = pd.read_excel(gold_attention_data)
    gold_list = gt_raw.loc[gt_raw['topic'].str.contains('Gold')].source.tolist()
    for i in range(len(gold_list)):
        gold_test = gt_raw.loc[gt_raw['source']==gold_list[i]].topic.tolist()
        gold_dict.update({gold_list[i]: gold_test[0]})
    return gold_dict
                    
               
def get_scores_from_assessments(content_json, max_likert):
    for key in list(content_json.keys()):
        if 'assessment' in key and 'specify' not in key:
            answer = False
            i = 0
            while not answer:
                i += 1
                answer = content_json[key][str(i)] 
            content_json[key] = i
        elif 'assessment' in key and 'specify' in key:
            groups_specify = []
            for k in list(content_json[key].keys()):
                if content_json[key][k] == True:
                    groups_specify.append(k)
            if 'NONE' in groups_specify:
                final = 'NONE'
            else:
                final = '; '.join(groups_specify)
            content_json[key] = final
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




def raw_to_dict(consolidated_request, gold_dict, max_likert_score):
    all_items = os.listdir(consolidated_request)
    worker_info = {}
    consolidated_responses = {}
    gold_question_quality = {}
    for item in all_items:
        with open(consolidated_request + item) as json_file:
            survey_responses = json.load(json_file)
            for row in range(len(survey_responses)):
                
                dataObjectId = survey_responses[row]['datasetObjectId']
                dataObject = survey_responses[row]['dataObject']['content']
                dataObject = dataObject.replace('Claim: ', '')
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
                    if dataObject in gold_dict.keys():
                        worker_info[worker_id]['num_gold'] += 1
                        worker_veracity_score = content_json['assessment_truth']
                        if dataObject not in gold_question_quality:
                            gold_question_quality.update({dataObject:{'num_seen':1,'num_correct':0}})
                        else:
                            gold_question_quality[dataObject]['num_seen'] += 1
                        # Check False gold data
                        if (gold_dict[dataObject] == 'Gold_False') and (worker_veracity_score in [max_likert_score - 1, max_likert_score]):
                            worker_info[worker_id]['num_gold_correct'] += 1
                            gold_question_quality[dataObject]['num_correct'] += 1
                        # Check True gold data    
                        elif (gold_dict[dataObject] == 'Gold_True') and (worker_veracity_score in [1, 2]):
                            worker_info[worker_id]['num_gold_correct'] += 1
                            gold_question_quality[dataObject]['num_correct'] += 1

    return worker_info, consolidated_responses, gold_question_quality


def dict_to_dataframe(worker_info, consolidated_responses, gold_question_quality):
    
    worker_info_frame = pd.DataFrame.from_dict(worker_info, orient='index')
    gold_quality_frame = pd.DataFrame.from_dict(gold_question_quality, orient='index').reset_index()
    
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
    
    return response_frame, worker_info_frame, gold_quality_frame


###############################
############## MAIN
###############################


os.chdir('/Users/tdn897/Desktop/Misinformation Detection Paper/GroundTruthCheckworthyExperiment/GroundTruthCheckworthyExperiment/experimental_data_raw/')
gold_attention_data = '../../../GroundTruthPreExperiment.xlsx'
max_likert_score = 6

regions = ['east-1', 'east-2', 'west-2']
data_splits = ['0', '1']
reps = ['0', '1', '2', '3', '4', '5']



gold_dict = generate_gold_dict(gold_attention_data=gold_attention_data)
consolidated_responses_frame = pd.DataFrame()
worker_info_frame = pd.DataFrame()
gold_quality_frame = pd.DataFrame()


for region in regions:
    for spl in data_splits:
        for rep in reps:
            
            consolidated_request_dir = 'checkworthy-main-experiment-' + region + '-split-' + spl + '-rep-' + rep +\
                '/annotations/consolidated-annotation/consolidation-request/iteration-1/'
            
            if os.path.isdir(consolidated_request_dir):
            
            
                worker_info, consolidated_responses, gold_question_quality = raw_to_dict(
                    consolidated_request=consolidated_request_dir,
                    gold_dict = gold_dict, 
                    max_likert_score = max_likert_score)
                
                cr_frame, wi_frame, gq_frame = dict_to_dataframe(
                    worker_info = worker_info,
                    consolidated_responses = consolidated_responses,
                    gold_question_quality = gold_question_quality)
                
                wi_frame['job'] = region + '-split-' + spl + '-rep-' + rep
                wi_frame['region'] = region
                
                consolidated_responses_frame = pd.concat([cr_frame, consolidated_responses_frame])
                worker_info_frame = pd.concat([wi_frame, worker_info_frame])
                gold_quality_frame = pd.concat([gq_frame, gold_quality_frame])


worker_info_frame['pct_gold_correct'] = np.where(worker_info_frame['num_gold']==0, 0, worker_info_frame['num_gold_correct']/worker_info_frame['num_gold'])
good_workers = worker_info_frame.loc[(worker_info_frame['pct_gold_correct']>0.8) & (worker_info_frame['num_gold'] > 2)]
print('% of accepted answers: ' + str(sum(good_workers['num_questions'])/sum(worker_info_frame['num_questions'])))

gold_quality_frame = gold_quality_frame.groupby(['index']).agg(num_seen=('num_seen', sum), num_correct=('num_correct', sum))



consolidated_responses_frame.to_csv('../experimental_data_clean/consolidated_responses_all_workers.csv', index=False)
consolidated_responses_high_quality = consolidated_responses_frame.loc[consolidated_responses_frame['worker'].isin(good_workers.index)]
consolidated_responses_high_quality.to_csv('../experimental_data_clean/consildated_responses_high_quality.csv', index=False)


worker_info_frame.to_csv('../experimental_data_clean/worker_info_clean.csv')



          
         