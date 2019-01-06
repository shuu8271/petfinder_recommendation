import pandas as pd, numpy as np
import requests
import json
import random
import csv
from src.inference.classify import classify


import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'

allbreeds = pd.read_csv('data/breeds.csv', header=0, index_col=0)
breed_list = allbreeds['breed'].tolist()
feature_list = ['size_S', 'size_M', 'size_L', 'size_XL', *sorted(list(breed_list))]


def make_pet_feature_120(df, breedlist=breed_list):
    '''
    create pet-feature matrix
    '''
    df = pd.get_dummies(df, columns=['size'])

    temp = pd.DataFrame(None, columns=sorted(breedlist))
    all_df = pd.concat((df, temp), axis=1, join='outer')
    all_df[breedlist] = all_df[breedlist].fillna(0)
    for i in range(len(all_df)):
        url_count = len(all_df.loc[i, 'media']) # how many urls included
        if all_df.loc[i, 'media'][0] == '': # no images url
            pass
        else:
            # assign breed probability
            for key in range(url_count):
                max_prob = float(0)
                max_key = int(0)
                # use try/except to skip error when read in image urls
                try:
                    temp_prob_df = classify('uri', all_df.loc[i, 'media'][key])
                    if temp_prob_df['prob'].max() > max_prob:
                        max_prob_df = temp_prob_df.copy()
                except:
                    print(f"Error at {all_df.loc[i, 'pet_id']}, url: {all_df.loc[i, 'media'][key]}")
            for breed in breedlist:
                all_df.loc[i, breed] = max_prob_df[max_prob_df['breed']==breed]['prob'].tolist()[0]
    
    pet_features = ['pet_id', *feature_list]
    return all_df[pet_features]


def make_user_feature_120(data_df, pet_feature_df, select_list, breedlist=breed_list):
    '''
    convert user input list to create user-feature matrix
    selection contains set of pet selection(pet_id)
    df is the all data in database
    '''
    current_user_id = random.randint(1000001, 2000000)
    user_df = pd.DataFrame(None, columns=['user_id',*feature_list])

    user_df.loc[0, 'user_id'] = current_user_id
    user_df.fillna(0, inplace=True)

    cnt_s, cnt_m, cnt_l, cnt_xl = 0, 0, 0, 0
    for pet in select_list:
        pet_size = data_df[data_df['pet_id']==pet]['size'].values
        if pet_size == 'S':
            cnt_s += 1
        elif pet_size == 'M':
            cnt_m += 1
        elif pet_size == 'L':
            cnt_l += 1
        elif pet_size == 'XL':
            cnt_xl += 1
        total_cnt = cnt_s + cnt_m + cnt_l + cnt_xl

        user_df.loc[0, 'size_S'] = cnt_s / total_cnt
        user_df.loc[0, 'size_M'] = cnt_m / total_cnt
        user_df.loc[0, 'size_L'] = cnt_l / total_cnt
        user_df.loc[0, 'size_XL'] = cnt_xl / total_cnt

        for breed in breedlist:
            user_df.loc[0, breed] += float(pet_feature_df[pet_feature_df['pet_id']==pet][breed])
    
    return user_df
