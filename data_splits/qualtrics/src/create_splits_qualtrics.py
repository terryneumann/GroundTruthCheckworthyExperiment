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
import math
import random


def shuffle_indices(dataframe):
    # Get the indices of the DataFrame and shuffle them randomly
    indices = list(dataframe.reset_index(drop=True).index)
    random.shuffle(indices)
    return indices


def get_non_overlapping_indices(dataframe, X):
    shuffled_indices = shuffle_indices(dataframe)
    # Get the total number of rows (N) in the DataFrame
    N = len(dataframe)
    
    # Calculate the size of each group (rounded up)
    group_size = math.ceil(N / X)
    
    # Initialize the list to store lists of indices
    index_lists = []
    
    # Generate the list of indices for each group
    for i in range(X):
        start_index = i * group_size
        end_index = min(start_index + group_size, N)
        indices = shuffled_indices[start_index:end_index]
        index_lists.append(indices)
    
    return index_lists

def shuffle_dataframes(df1, df2):
    # Making a copy of the dataframes to avoid modifying the original dataframes
    df1_copy = df1.copy().reset_index(drop=True)
    df2_copy = df2.copy().reset_index(drop=True)

    # Checking if df1 has more rows than df2
    if len(df1_copy) < len(df2_copy):
        print('Error: df1 has fewer rows than df2')
        return

    # Creating a new dataframe to store the shuffled data
    shuffled_df = pd.DataFrame()

    # Adding rows alternately from df1 and df2
    for i in range(len(df2_copy)):
        shuffled_df = shuffled_df.append(df1_copy.loc[i], ignore_index=True)
        shuffled_df = shuffled_df.append(df2_copy.loc[i], ignore_index=True)

    # Adding the remaining rows from df1 if any
    if len(df1_copy) > len(df2_copy):
        shuffled_df = shuffled_df.append(df1_copy.loc[len(df2_copy):], ignore_index=True)
        
    return shuffled_df


def save_dataframes_as_csv(gold, non_gold, gold_index_lists, non_gold_index_lists, X):
    # Create and save X DataFrames using the index_lists
    for i in range(X):
        subset_gold = gold.iloc[gold_index_lists[i]]
        subset_non_gold = non_gold.iloc[non_gold_index_lists[i]]
        subset_df = shuffle_dataframes(subset_non_gold, subset_gold)
        subset_df.to_csv(f'GroundTruthCheckworthyExperiment/GroundTruthCheckworthyExperiment/data_splits/qualtrics/output/split_{i}.csv', index=False)



X = 4
os.chdir('/Users/tdn897/Desktop/Misinformation Detection Paper/')
gt_raw = pd.read_excel('GroundTruthPreExperiment.xlsx')
gt_raw['source'] = 'Claim: ' + gt_raw['source']

non_gold = gt_raw.loc[~gt_raw.topic.str.contains('Gold')].reset_index().drop(columns=['index'])
gold = gt_raw.loc[gt_raw.topic.str.contains('Gold')]

gold_split_indices = get_non_overlapping_indices(gold, X)
non_gold_split_indices = get_non_overlapping_indices(non_gold, X)
save_dataframes_as_csv(gold = gold,
                       non_gold = non_gold, 
                       gold_index_lists = gold_split_indices, 
                       non_gold_index_lists = non_gold_split_indices, 
                       X = X)

