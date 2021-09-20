from pickle import TRUE
from sqlalchemy import create_engine
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import numpy as np
from dotenv import load_dotenv
from os import getenv

def get_dummy_genres(genresdf):
    genres = genresdf["genres"].apply(lambda x: x.split(","))
    distinct_genres = set(list(np.concatenate(genres.values)))
    for genre in distinct_genres:
        genresdf[genre] = genres.map(lambda x: int(genre in x))
    return genresdf.drop("genres", axis=1)

def get_dummy_actors(actorsdf):
    aggregation_functions = {"nconst": lambda x: x.tolist()}
    actorsdf = actorsdf.groupby(actorsdf.index).aggregate(aggregation_functions)
    actors = actorsdf["nconst"]
    distinct_actors = set(list(np.concatenate(actors.values)))

    for actor in distinct_actors:
        actorsdf[actor] = actors.map(lambda x: int(actor in x))
    return actorsdf.drop("nconst", axis=1)

def main():

    ## Some messy code to prototype Random forest with limited data only from IMDb and small subset. Uses genres and actors.
    ## Since actors are one-hot-encoded might not scale that well
    load_dotenv()
    DB_URI = getenv("DATABASE_URI")
    connection = create_engine(DB_URI)
    sql = 'SELECT genres, title_principals.nconst, title_basics.tconst, average_rating FROM title_basics INNER JOIN title_ratings ON title_ratings.tconst = title_basics.tconst LEFT JOIN title_principals ON title_principals.tconst = title_basics.tconst LIMIT 20'
    df = pd.read_sql_query(sql, con=connection)
    df.set_index("tconst", inplace=True)
    genres = df[["genres"]]
    dummy_genres = get_dummy_genres(genres[~genres.index.duplicated(keep='first')])
    dummy_actors = get_dummy_actors(df[["nconst"]])
    X = pd.concat([dummy_genres, dummy_actors], axis=1)
    avg_ratings = df[["average_rating"]]
    Y = avg_ratings[~avg_ratings.index.duplicated(keep='first')]
    regr = RandomForestRegressor(max_depth=2, random_state=0)
    regr.fit(X, Y)
    joblib.dump(regr, "./random_forest.joblib")
    loaded_rf = joblib.load("./random_forest.joblib")
    print(loaded_rf.predict([X.iloc[0,:]]))

if __name__=="__main__":
    main()
