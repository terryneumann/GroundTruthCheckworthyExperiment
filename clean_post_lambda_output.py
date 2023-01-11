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


survey_responses = data1 + data2


worker_info = {}
consolidated_responses = {}

for item in range(len(survey_responses)):
    dataObjectId = survey_responses[item]['datasetObjectId']
    dataObject = survey_responses[item]['dataObject']['content']
    annotations = survey_responses[item]['annotations']
    for worker in range(len(annotations)):
        worker_response = annotations[worker]
        worker_id = worker_response['workerId']
        content_json = json.loads(worker_response['annotationData']['content'])
        if content_json['survey-complete'] == 'Yes':
            worker_info.update({worker_id:
                                {'Demog - Gender':content_json['demog-gender'],
                                 'Demog - Race':content_json['demog-race'],
                                 'Demog - Age':content_json['demog-age'],
                                 'Demog - Education':content_json['demog-educ'],
                                 #'Demog - Sexual Orientation':content_json['demog-sexual'],
                                 'Ideology - Abortion':content_json['ideology-abortion'],
                                 'Ideology - Limited Government':content_json['ideology-limited-government'],
                                 'Ideology - Military': content_json['ideology-military'],
                                 'Ideology - Religion': content_json['ideology-religion'],
                                 'Ideology - Welfare': content_json['ideology-welfare'],
                                 'Ideology - Gun Ownership':content_json['ideology-gun-ownership'],
                                 'Ideology - Marriage Equality': content_json['ideology-marriage'],
                                 'Ideology - Fiscal': content_json['ideology-fiscal'],
                                 'Ideology - Corporations': content_json['ideology-corporations'],
                                 'Ideology - Transgendered': content_json['ideology-transgendered'],
                                 'Ideology - Speech':content_json['ideology-speech'],
                                 'Ideology - Science':content_json['ideology-science'],
                                 'Ideology - Immigration':content_json['ideology-immigration'],
                                 'Identification - Fake 1':content_json['identification-fake-1'],
                                 'Identification - Fake 2':content_json['identification-fake-2'],
                                 'Identification - Fake 3':content_json['identification-fake-3'],
                                 'Identification - Fake 4':content_json['identification-fake-4'],
                                 'Identification - Real 1':content_json['identification-real-1'],
                                 'Identification - Real 2':content_json['identification-real-2'],
                                 'Identification - Real 3':content_json['identification-real-3'],
                                 'Identification - Real 4':content_json['identification-real-4']}})
        if dataObjectId in consolidated_responses:
            consolidated_responses[dataObjectId]['responses'].update({worker_id:content_json['checkworthy-assessment']['label']})
        elif dataObjectId not in consolidated_responses:
            consolidated_responses.update({dataObjectId:{'content': dataObject, 'responses': {worker_id:content_json['checkworthy-assessment']['label']}}})
            
        
        
            
                
                        