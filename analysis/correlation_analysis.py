#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 10:26:21 2023

@author: tdn897
"""
import json
import os
import pandas as pd
import numpy as np
from plotnine import *


os.chdir('/Users/tdn897/Desktop/Misinformation Detection Paper/GroundTruthCheckworthyExperiment/GroundTruthCheckworthyExperiment/experimental_data_clean/')
consolidated_responses_frame = pd.read_csv('consolidated_responses_clean.csv')
original_data = pd.read_excel('../../../GroundTruthPreExperiment.xlsx', usecols=['source', 'topic'])



###############################
############## Simple Correlation Analysis
###############################


response_frame_summary = consolidated_responses_frame\
    .groupby(['claim'])\
        .agg(mean_checkworthy = ('assessment_checkworthy', np.mean),
             mean_truth = ('assessment_truth', np.mean),
             mean_general_public = ('assessment_general_public', np.mean),
             mean_group_harm = ('assessment_group_harm', np.mean),
             mean_group_interest = ('assessment_group_interest', np.mean))\
            .reset_index()
        
        
response_frame_summary = response_frame_summary.merge(original_data, left_on='claim', right_on='source')
response_frame_summary = response_frame_summary.loc[response_frame_summary['topic'] != 'Gold']        


print('correlation between truth and checkworthiness:')
np.corrcoef(response_frame_summary['mean_checkworthy'], response_frame_summary['mean_truth'])[0,1]
print('correlation between checkworthiness and interest to general public:')
np.corrcoef(response_frame_summary['mean_checkworthy'], response_frame_summary['mean_general_public'])[0,1]              
print('correlation between checkworthiness and interest to general public:')
np.corrcoef(response_frame_summary['mean_checkworthy'], response_frame_summary['mean_group_harm'])[0, 1]      
print('correlation between truth and interest to general public:')
np.corrcoef(response_frame_summary['mean_truth'], response_frame_summary['mean_group_harm'])[0, 1]    
print('correlation between general public and group harm:')
np.corrcoef(response_frame_summary['mean_general_public'], response_frame_summary['mean_group_harm'])[0, 1]                
print('correlation between group interest and group harm:')
np.corrcoef(response_frame_summary['mean_group_interest'], response_frame_summary['mean_group_harm'])[0, 1]                


##################################
############### Topic Analysis
##################################
     

by_topic = response_frame_summary\
    .groupby(['topic'])\
        .agg(Checkworthiness = ('mean_checkworthy', np.mean),
             FalsehoodRating = ('mean_truth', np.mean),
             InterestGeneralPublic = ('mean_general_public', np.mean),
             GroupHarm = ('mean_group_harm', np.mean),
             GroupInterest = ('mean_group_interest', np.mean))\
            .reset_index()
            
by_topic = pd.melt(by_topic, id_vars = 'topic')


g = (ggplot(by_topic)
     + geom_bar(aes(x = 'variable', y = 'value', fill='topic'),color='black', stat = 'identity', position = 'dodge')
     + coord_flip()
     + theme_seaborn()
     + xlab('Survey Variable')
     + ylab('Mean Survey Rating')
     + ggtitle('Mean Survey Ratings - All Workers'))

g.save(filename = 'mean_survey_responses_all_workers.png', width=12, height = 7, dpi=700)


