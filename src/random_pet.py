import pymongo, pandas as pd, numpy as np

def random_pets(db, coll, num=30):
    rand_df = None
    temp_df = pd.DataFrame(list(coll.aggregate([{'$sample':{'size':num}}])))

    if rand_df is None:
        rand_df = temp_df
    else:
        for i in range(len(temp_df)):
            if temp_df.loc[i, 'pet_id'] not in rand_df['pet_id'].tolist():
                rand_df = pd.concat([rand_df, temp_df], axis=0, ignore_index=True,\
                                    sort=False)
    return rand_df