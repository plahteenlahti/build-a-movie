from flask import Flask, request
import json
from os.path import dirname, abspath, join
import numpy as np
import pandas as pd
import joblib

dir = dirname(abspath(__file__))
app = Flask(__name__)

def _get_dummy_vector(filename, indexes):
    df = pd.read_csv(join(dir, 'data', filename))
    df = df.drop("tconst", axis=1)
    for col in df.columns:
        df[col].values[:] = 0
    row = df.iloc[0,:]
    row[indexes] = 1
    return row.to_numpy()

def _turn_to_vector(genres, people, budget):
    dummy_genres = _get_dummy_vector("dummy_genres.csv", genres)
    dummy_people = _get_dummy_vector("dummy_people.csv", people)
    budget = np.array([budget])
    vector = np.hstack((dummy_genres, dummy_people, budget)).reshape(1,-1)
    return vector

def _predict_forest(genres, people, budget, forest_name):
    x = _turn_to_vector(genres, people, budget)
    loaded_rf = joblib.load(join(dir, 'data', forest_name))
    return loaded_rf.predict(x)

@app.route("/predict-rating", methods=['POST'])
def post_rating_result():
    message = request.get_json()
    genres, people, budget = message['genres'], message['people'], message['budget']
    
    rating = _predict_forest(genres, people, budget, "rating_forest.joblib")
    rating = rating.tolist()
    rating = {"result": round(rating[0],1)}
    rating = json.dumps(rating)

    return rating

@app.route("/predict-wlg", methods=['POST'])
def post_wlg_result():
    message = request.get_json()
    genres, people, budget = message['genres'], message['people'], message['budget']
    
    wlg = _predict_forest(genres, people, budget, "worldwide_lifetime_gross.joblib")
    wlg = wlg.tolist()
    wlg = {"result": round(wlg[0],1)}
    wlg = json.dumps(wlg)

    return wlg

if __name__ == "__main__":
    app.run(host='0.0.0.0')
