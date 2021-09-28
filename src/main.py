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
    aggregation_functions = {"primary_name": lambda x: x.tolist()}
    actorsdf = actorsdf.groupby(actorsdf.index).aggregate(aggregation_functions)
    actors = actorsdf["primary_name"]
    distinct_actors = set(list(np.concatenate(actors.values)))

    for actor in distinct_actors:
        actorsdf[actor] = actors.map(lambda x: int(actor in x))
    return actorsdf.drop("primary_name", axis=1)

def get_actors():
    load_dotenv()
    DB_URI = getenv("DATABASE_URI")
    connection = create_engine(DB_URI)
    sql = "SELECT DISTINCT primary_name FROM title_principals INNER JOIN name_basics ON name_basics.nconst = title_principals.nconst WHERE category='actor'"
    df = pd.read_sql_query(sql, con=connection)
    df.to_csv("actors.csv")

def get_genres():
    load_dotenv()
    DB_URI = getenv("DATABASE_URI")
    connection = create_engine(DB_URI)
    sql = "SELECT DISTINCT genres FROM title_basics"
    df = pd.read_sql_query(sql, con=connection)
    df["genres"] = df["genres"].str.split(",")
    df = df.explode("genres")
    genres = df["genres"].drop_duplicates()
    genres.to_csv("genres.csv")

def get_directors():
    load_dotenv()
    DB_URI = getenv("DATABASE_URI")
    connection = create_engine(DB_URI)
    sql = "SELECT DISTINCT primary_name FROM title_principals INNER JOIN name_basics ON name_basics.nconst = title_principals.nconst WHERE category='director'"
    df = pd.read_sql_query(sql, con=connection)
    df.to_csv("directors.csv")

def main():

    ## Some messy code to prototype Random forest with limited data only from IMDb and small subset. Uses genres and actors.
    ## Since actors are one-hot-encoded might not scale that well
    load_dotenv()
    DB_URI = getenv("DATABASE_URI")
    connection = create_engine(DB_URI)
    sql = "SELECT genres, name_basics.primary_name, title_basics.tconst, average_rating FROM title_basics INNER JOIN title_ratings ON title_ratings.tconst = title_basics.tconst LEFT JOIN title_principals ON title_principals.tconst = title_basics.tconst INNER JOIN name_basics ON name_basics.nconst = title_principals.nconst WHERE title_principals.category='actor' OR title_principals.category='director' LIMIT 20"
    df = pd.read_sql_query(sql, con=connection)
    df.set_index("tconst", inplace=True)
    genres = df[["genres"]]
    dummy_genres = get_dummy_genres(genres[~genres.index.duplicated(keep='first')])
    ## dummy_people includes actors and directors
    dummy_people = get_dummy_actors(df[["primary_name"]])
    
    X = pd.concat([dummy_genres, dummy_people], axis=1)
    avg_ratings = df[["average_rating"]]
    Y = avg_ratings[~avg_ratings.index.duplicated(keep='first')]
    regr = RandomForestRegressor(max_depth=2, random_state=0)
    regr.fit(X, Y)
    joblib.dump(regr, "./random_forest.joblib")
    loaded_rf = joblib.load("./random_forest.joblib")
    print(loaded_rf.predict([X.iloc[0,:]]))

    get_directors()

if __name__=="__main__":
    main()
