from flask import Flask, request, render_template
import requests, json, numpy as np, pandas as pd
import pymongo
from src.api_data import download_data
from src.data_cleanup import cleanup_data
from src.random_pet import random_pets
from src.feature_matrix import make_pet_feature, make_user_feature

app = Flask(__name__)

# initialize database
my_client = pymongo.MongoClient('mongodb://localhost:27017/')

if 'petfinder' in my_client.list_database_names():
    my_db = my_client.petfinder
    my_coll = my_db.dogs
else:
    # create database if database does not exists
    my_db = my_client.petfinder
    my_coll = my_db.dogs

    # load data to save to database
    pet_data = download_data()
    pet_df = pd.DataFrame(pet_data)
    pet_df = cleanup_data(pet_df)
    save_cols = ['pet_id', 'age', 'breeds', 'description', 'media', 'sex',
                 'size', 'status']
    for i in range(len(pet_df)):
        # convert single row to json format to save to database
        data_json = json.loads(pet_df[save_cols].loc[i].to_json())

        # set examination to avoid save duplicate data to database
        key = {'pet_id': int(pet_df.loc[i, 'pet_id'])}
        my_coll.update_one(key, {'$setOnInsert': data_json}, upsert=True)


# -------------routes----------------

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/mainproject', methods=['GET', 'POST'])
def mainproject():
    random_df = random_pets(db=my_db, coll=my_coll, num=30)
    random_ids = random_df['pet_id'].tolist()
    image_list = random_df['media'].tolist()
    selection = dict()

    return render_template('capstone.html', random_pets=zip(random_ids,
                                                            image_list))


@app.route('/recommresult', methods=['GET', 'POST'])
def recomm_result():
    if request.method == 'POST':
        selection = request.form
        selected_ids = set(selection.values())
        user_feature_df = make_user_feature(df, selected_ids)

        recomm_mat = np.dot(user_feature_df.iloc[:, 1:],
                            pet_feature_df.iloc[:, 1:].T)
        # return 10 highest number ids, names, breeds
        max_idx_10 = recomm_mat.argsort(axis=1)[:, :-11:-1]
        recomm_id = list()

        for idx in max_idx_10[0]:
            recomm_id.append(pet_feature_df.loc[idx, 'pet_id'].tolist())

        recomm_names = list()
        recomm_breeds = list()
        recomm_images = list()
        for id in recomm_id:
            recomm_names.append(df[df['pet_id'] == id]['name'].values[0])
            recomm_breeds.append(df[df['pet_id'] == id]['breeds'].values[0])
            recomm_images.append(df[df['pet_id'] == id]['media'].values[0])

    return render_template('recom_result.html', top10=zip(recomm_id,
                                                          recomm_names,
                                                          recomm_breeds,
                                                          recomm_images))

# -------------main------------------
if __name__ == "__main__":

    # load database to dataframe
    df = pd.DataFrame(list(my_coll.find()))
    pet_feature_df = make_pet_feature(df)

    app.run(host='0.0.0.0', port=8080, debug=True)
