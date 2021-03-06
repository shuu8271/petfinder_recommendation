import json
import requests
import pandas as pd
import csv
import pymongo
from src.data_cleanup import cleanup_data
from data.api_key import api_key

api_url = f'http://api.petfinder.com/pet.find?key={api_key}'

# -----------initial data------------
def download_data(locations, offset=0):
    if offset == 0:
        init_parameters = {'animal': 'dog', 'format': 'json',
                           'output': 'full', 'location': locations,
                           'count': 1000}
        pet_result = requests.get(api_url, params=init_parameters)
        offset = pet_result.json()['petfinder']['lastOffset'].get('$t', 0)
        data = pet_result.json()['petfinder']['pets']['pet']
    else:
        parameters = {'animal': 'dog', 'format': 'json', 'output': 'full',
                      'offset': str(offset), 'location': locations,
                      'count': 200}
        pet_result = requests.get(api_url, params=parameters)
#        offset = pet_result.json()['petfinder']['lastOffset'].get('$t',0)
        data = pet_result.json()['petfinder']['pets']['pet']
    return data


def dog_breed_list():
    breed_parameters = {'animal': 'dog', 'format': 'json'}
    dog_breeds = requests.get(api_url, params=breed_parameters)

    dog_breeds_json = dog_breeds.json()['petfinder']['breeds']['breed']
    breed_set = set()
    for d in dog_breeds_json:
        breed_list.add(d.get('$t'))
    with open('data/breed_list.csv', 'w') as breed_file:
        wr = csv.writer(breed_file)
        wr.writerow(breed_set)


if __name__ == '__main__':
    my_client = pymongo.MongoClient('mongodb://localhost:27017/')
    # create database if database does not exists
    my_db = my_client.petfinder
    my_coll = my_db.dogs

    city_locations = ['New York, NY', 'Manhattan, NY', 'Astoria, NY',
                      'Flushing, NY', 'Brooklyn, NY', 'Jersey City, NJ']

    # load data to save to database
    for num in [0, 1000, 1200, 1400, 1600, 1800, 2000]:
        pet_data = download_data(locations=city_locations, offset=num)
        pet_df = pd.DataFrame(pet_data)
        pet_df = cleanup_data(pet_df)
        save_cols = ['pet_id', 'name', 'age', 'breeds', 'description',
                     'media', 'sex', 'size', 'status']
        for i in range(len(pet_df)):
            # convert single row to json format to save to database
            data_json = json.loads(pet_df[save_cols].loc[i].to_json())

            # set examination to avoid save duplicate data to database
            key = {'pet_id': int(pet_df.loc[i, 'pet_id'])}
            my_coll.update_one(key, {'$setOnInsert': data_json}, upsert=True)
        print(my_coll.count_documents({}))
