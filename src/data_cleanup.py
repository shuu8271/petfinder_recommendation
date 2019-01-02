import numpy as np, pandas as pd, re

def sep_breeds(x):
    '''
    separate all breeds mentioned in breed type for 
    breed type in dataframe
    '''
    if len(x['breed']) == 1:
        x = x['breed'].get('$t')
    elif len(x['breed']) > 1:
        breed_lst = set()
        for d in x['breed']:
            breed_lst.add(d.get('$t'))
        x = ', '.join(breed_lst)
    else:
        x = None
    return x


def extract_image_url(x):
    '''
    split all image urls in dataframe
    '''
    url_pattern = 'http://photos.petfinder.com/photos/pets/[0-9]*/[0-9]/\?bust=[0-9]*'

    # exclude issue with no image included at all by using
    # x.get('photos',{'photo':[{'$t':'n/a'}]}).get('photo')
    num_url = len(x.get('photos',{'photo':[{'$t':'n/a'}]}).get('photo'))

    url_set = set()
    for i in range(num_url):
        url_set.add(''.join(re.findall(url_pattern, x.get('photos',{'photo':[{'$t':'n/a'}]}).get('photo')[i].get('$t'))))
    return sorted(url_set)

def cleanup_data(df):
    '''
    cleanup datafram store raw format of pet_data
    '''
    # set columns to extract dictionary data
    map_col = ['animal', 'age', 'description','id', 'lastUpdate','mix', \
            'name', 'sex', 'shelterId', 'shelterPetId', 'size', 'status']

    for col in map_col:
        df[col] = df[col].apply(lambda x: x.get('$t'))

    # use formula to clean up breeds with multiple breeds
    df['breeds'] = df['breeds'].apply(sep_breeds)

    # set pet_id with integer type
    df['pet_id'] = df['id'].astype('int')
    df.drop(columns = ['id'], inplace = True)

    # extract all images urls
    df['media'] = df['media'].apply(extract_image_url)
    return df
