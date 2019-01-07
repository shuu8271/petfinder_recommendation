from flask import Flask, request, render_template, url_for
import requests, json, numpy as np, pandas as pd
import pymongo
from src.api_data import download_data
from src.data_cleanup import cleanup_data
from src.feature_matrix import make_user_feature_120
from src.form import SelectionForm
from data.api_key import form_key


app = Flask(__name__)

app.config['SECRET_KEY'] = form_key

# -------------routes----------------
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/mainproject', methods=['GET'])
def mainproject():
    random_df = df.sample(n=35)
    random_ids = random_df['pet_id'].tolist()
    image_list = random_df['media'].tolist()
    selection_form = SelectionForm()

    # if selection_form.validate_on_submit():
    #     return redirect(url_for('recomm_result'), selected_ids=selection_form.value.data)

    return render_template('capstone.html',
                           random_pets = zip(random_ids, image_list),
                           form = selection_form)


@app.route('/recommresult', methods=['POST'])
def recomm_result():
    selected_ids = set([SelectionForm(request.form).selection1.data,
                       SelectionForm(request.form).selection2.data,
                       SelectionForm(request.form).selection3.data,
                       SelectionForm(request.form).selection4.data,
                       SelectionForm(request.form).selection5.data])
    if None in selected_ids:
        selected_ids.remove(None)

    user_feature_df = make_user_feature_120(df, pet_feature_df, selected_ids)

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

    return render_template('recom_result.html', selection=selected_ids,\
                           top10=zip(recomm_id, recomm_names, recomm_breeds,
                                     recomm_images))

# -------------main------------------
if __name__ == "__main__":
    # load pre converted data
    df = pd.read_csv('data/pet_data.csv', index_col=0)
    df['media'] =df['media'].apply(lambda x: str(x).split(' '))
    pet_feature_df = pd.read_csv('data/pet_feature.csv', index_col=0)


    app.run(host='0.0.0.0', port=8080, debug=True)
