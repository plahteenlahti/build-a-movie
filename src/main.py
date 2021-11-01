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
    genresdf =genresdf.drop("genres", axis=1)
    genresdf.to_csv("dummy_genres.csv")
    return genresdf

def get_dummy_actors(actorsdf):
    aggregation_functions = {"primary_name": lambda x: x.tolist()}
    actorsdf = actorsdf.groupby(actorsdf.index).aggregate(aggregation_functions)
    actors = actorsdf["primary_name"]
    distinct_actors = set(list(np.concatenate(actors.values)))

    for actor in distinct_actors:
        actorsdf[actor] = actors.map(lambda x: int(actor in x))
    actorsdf = actorsdf.drop("primary_name", axis=1)
    actorsdf.to_csv("dummy_people.csv")
    return actorsdf

def get_actors():
    load_dotenv()
    DB_URI = getenv("DATABASE_URI")
    connection = create_engine(DB_URI)
    sql = "SELECT DISTINCT primary_name FROM my_table WHERE category='actor'"
    df = pd.read_sql_query(sql, con=connection)
    df.to_csv("actors.csv")

def get_genres():
    load_dotenv()
    DB_URI = getenv("DATABASE_URI")
    connection = create_engine(DB_URI)
    sql = "SELECT DISTINCT genres FROM my_table"
    df = pd.read_sql_query(sql, con=connection)
    df["genres"] = df["genres"].str.split(",")
    df = df.explode("genres")
    genres = df["genres"].drop_duplicates()
    genres.to_csv("genres.csv")

def get_directors():
    load_dotenv()
    DB_URI = getenv("DATABASE_URI")
    connection = create_engine(DB_URI)
    sql = "SELECT DISTINCT primary_name FROM my_table WHERE category='director'"
    df = pd.read_sql_query(sql, con=connection)
    df.to_csv("directors.csv")

def get_data():
    load_dotenv()
    DB_URI = getenv("DATABASE_URI")
    connection = create_engine(DB_URI)
    sql = "SELECT genres, title_principals.category, movie_boxoffice.original_title, movie_boxoffice.worldwide_lifetime_gross, movie_boxoffice.budget, name_basics.primary_name, title_basics.tconst, average_rating FROM title_basics INNER JOIN title_ratings ON title_ratings.tconst = title_basics.tconst LEFT JOIN title_principals ON title_principals.tconst = title_basics.tconst INNER JOIN name_basics ON name_basics.nconst = title_principals.nconst INNER JOIN movie_boxoffice ON movie_boxoffice.tconst = title_basics.tconst WHERE title_principals.category='actor' OR title_principals.category='director';"
    df = pd.read_sql_query(sql, con=connection)
    print(df.shape)
    df.to_sql("my_table", con=connection)

def create_csvs():
    load_dotenv()
    DB_URI = getenv("DATABASE_URI")
    connection = create_engine(DB_URI)
    sql = "SELECT genres, primary_name, tconst, budget, worldwide_lifetime_gross, budget, average_rating FROM my_table"
    df = pd.read_sql_query(sql, con=connection)
    df.set_index("tconst", inplace=True)
    genres = df[["genres"]]
    dummy_genres = get_dummy_genres(genres[~genres.index.duplicated(keep='first')])
    dummy_people = get_dummy_actors(df[["primary_name"]])
    budget = df[["budget"]]
    budget = budget[~budget.index.duplicated(keep="first")]
    budget = budget.loc[:,~budget.columns.duplicated()]
    X = pd.concat([dummy_genres, dummy_people, budget], axis=1)
    X.to_csv("train_data.csv")
    avg_ratings = df[["average_rating"]]
    avg_ratings = avg_ratings[~avg_ratings.index.duplicated(keep='first')]
    avg_ratings.to_csv("average_ratings.csv")
    world_wide_gross = df[["worldwide_lifetime_gross"]]
    world_wide_gross = world_wide_gross[~world_wide_gross.index.duplicated(keep='first')]
    world_wide_gross.to_csv("worldwide_lifetime_gross.csv")


def train_rating_forest():
    train_random_forest("average_ratings.csv", "rating_forest.joblib")

def train_worldwide_gross_forest():
    train_random_forest("worldwide_lifetime_gross.csv", "worldwide_lifetime_gross.joblib")

def train_random_forest(target_name, forest_name):
    X = pd.read_csv("train_data.csv")
    X.drop("tconst", axis=1, inplace=True)
    Y = pd.read_csv(target_name)
    Y.drop("tconst", axis=1, inplace=True)
    regr = RandomForestRegressor()
    regr.fit(X, Y)
    joblib.dump(regr, forest_name)

def predict_forest(genres, people, budget, forest_name):
    x = turn_to_vector(genres, people, budget)
    loaded_rf = joblib.load(forest_name)
    return loaded_rf.predict(x)

def predict_rating(genres, people, budget):
    return predict_forest(genres, people, budget, "rating_forest.joblib")

def predict_worldwide_lifetime_gross(genres, people, budget):
    return predict_forest(genres, people, budget, "worldwide_lifetime_gross.joblib")

def turn_to_vector(genres, people, budget):
    dummy_genres = get_dummy_vector("dummy_genres.csv", genres)
    dummy_people = get_dummy_vector("dummy_people.csv", people)
    budget = np.array([budget])
    vector = np.hstack((dummy_genres, dummy_people, budget)).reshape(1,-1)
    return vector

def get_dummy_vector(filename, indexes):
    df = pd.read_csv(filename)
    df = df.drop("tconst", axis=1)
    for col in df.columns:
        df[col].values[:] = 0
    row = df.iloc[0,:]
    row[indexes] = 1
    return row.to_numpy()
    






    
def main():
    rating= predict_worldwide_lifetime_gross(["News"], ["Tom Cruise"], 20000)
    print(rating)



if __name__=="__main__":
    main()


