import pandas as pd, numpy as np
import requests
import json
import random
import csv

import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'


#breed_list = dog_breed_list()
with open('data/breed_list.csv', 'r') as f:
    reader = csv.reader(f)
    breed_list = list(reader)[0]
feature_list = ['size_S', 'size_M', 'size_L', 'size_XL', *sorted(breed_list)]


def breed_percentage(df):
    '''
    count for each breed
    '''
    for i in range(len(df)):
        temp = list()
        temp = df['breeds'][i].split(', ') # breeds included in one record
        for item in temp:
            df.loc[i, item] = 1/ len(temp)
    return df


def make_pet_feature(df, breedlist=list(breed_list)):
    '''
    process to create pet-feature matrix
    '''
    df = pd.get_dummies(df, columns=['size'])

    temp = pd.DataFrame(None, columns=sorted(breedlist))
    all_df = pd.concat((df, temp), axis=1, join='outer')
    all_df[breedlist] = all_df[breedlist].fillna(0)

    all_df = breed_percentage(all_df)

    pet_features = ['pet_id', *feature_list]
    return all_df[pet_features]

def make_user_feature(df, selection):
    #input is a set containing pet_id selections
    '''
    convert user input list to create user-feature matrix
    selection contains set of pet selection(pet_id)
    df is the all data in database
    '''
    current_user_id = random.randint(1000001, 2000000)
    temp_list = list()
    for pet_id in selection:
        temp_list.append((current_user_id, pet_id))
    input_df = pd.DataFrame(temp_list, columns = ['user_id', 'pet_id'] ,index=range(len(selection)))
    user_df = pd.DataFrame(None, columns=['user_id',*feature_list])

    users = set(input_df['user_id'].tolist()) # users list
    for idx, usr in enumerate(users):
        user_df.loc[idx, 'user_id'] = usr
        user_df.fillna(0, inplace=True)
        pet_id_list = set(input_df[input_df['user_id']==usr]['pet_id'].tolist())
        cnt_s, cnt_m, cnt_l, cnt_xl = 0, 0, 0, 0
        for pet in pet_id_list:
            pet_size = df[df['pet_id']==pet]['size'].values
            if pet_size == 'S':
                cnt_s += 1
            elif pet_size == 'M':
                cnt_m += 1
            elif pet_size == 'L':
                cnt_l += 1
            elif pet_size == 'XL':
                cnt_xl += 1
            total_cnt = cnt_s + cnt_m + cnt_l + cnt_xl

            user_df.loc[idx, 'size_S'] = cnt_s / total_cnt
            user_df.loc[idx, 'size_M'] = cnt_m / total_cnt
            user_df.loc[idx, 'size_L'] = cnt_l / total_cnt
            user_df.loc[idx, 'size_XL'] = cnt_xl / total_cnt

            selected_breeds = ''.join(df[df['pet_id']==pet]['breeds'].tolist()).split(', ')
            for breed in selected_breeds:
                user_df.loc[idx, breed] += 1
    current_user_id += 1
    return user_df

def make_user_feature_120(df, selection):
    #input is a set containing pet_id selections
    '''
    convert user input list to create user-feature matrix
    selection contains set of pet selection(pet_id)
    df is the all data in database
    '''
    current_user_id = random.randint(1000001, 2000000)
    temp_list = list()
    for pet_id in selection:
        temp_list.append((current_user_id, pet_id))
    input_df = pd.DataFrame(temp_list, columns = ['user_id', 'pet_id'] ,index=range(len(selection)))
    user_df = pd.DataFrame(None, columns=['user_id',*feature_list_120])

    users = set(input_df['user_id'].tolist()) # users list
    for idx, usr in enumerate(users):
        user_df.loc[idx, 'user_id'] = usr
        user_df.fillna(0, inplace=True)
        pet_id_list = set(input_df[input_df['user_id']==usr]['pet_id'].tolist())
        cnt_s, cnt_m, cnt_l, cnt_xl = 0, 0, 0, 0
        for pet in pet_id_list:
            pet_size = df[df['pet_id']==pet]['size'].values
            if pet_size == 'S':
                cnt_s += 1
            elif pet_size == 'M':
                cnt_m += 1
            elif pet_size == 'L':
                cnt_l += 1
            elif pet_size == 'XL':
                cnt_xl += 1
            total_cnt = cnt_s + cnt_m + cnt_l + cnt_xl

            user_df.loc[idx, 'size_S'] = cnt_s / total_cnt
            user_df.loc[idx, 'size_M'] = cnt_m / total_cnt
            user_df.loc[idx, 'size_L'] = cnt_l / total_cnt
            user_df.loc[idx, 'size_XL'] = cnt_xl / total_cnt

            #
            for breed in list(breeds_120):
                user_df.loc[idx, breed] += df[df['pet_id']==pet][breed]
    return user_df
