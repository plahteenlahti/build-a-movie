from lib.bom_scraper import get_first_search_data, get_search_data
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
from os import getenv
from os.path import exists
from difflib import SequenceMatcher

def get_bom_result(df):

    # just to know at which point the script has arrived
    total = len(df)

    # for incremental filling of the final result as csv
    final = pd.DataFrame(columns = ['tconst', 'original_title', 'worldwide_lifetime_gross', 'budget'])
    final.to_csv('final.csv', index=False)
    lines_written = len(final.index)
    
    for index, row in df.iterrows():
        print('Processing entry', index+1, '/', total, ':', row['original_title'])
        try:
            search_data = get_first_search_data(row['original_title'])
            if (not search_data.empty):
                final = final.append({'tconst': row['tconst'], 'original_title': row['original_title'],
                                    'worldwide_lifetime_gross': search_data['worldwide_lifetime_gross'].values[0],
                                    'budget': search_data['budget'].values[0]}, ignore_index=True)
                final.iloc[lines_written:].to_csv('final.csv', mode='a', header=False, index=False)
                lines_written = len(final.index)
        except Exception as e:
            print('Error', e)
    
    return final
    
def add_bom_db():
    load_dotenv()
    DB_URI = getenv("DATABASE_URI")
    connection = create_engine(DB_URI)

    file_exists = exists('titles.csv')
    if not file_exists: # if file doesn't exist, gather data from postgres
        sql = """SELECT tb.tconst, original_title 
                FROM title_basics AS tb JOIN title_ratings AS tr ON tb.tconst = tr.tconst 
                WHERE runtime_minutes > 80.0 AND num_votes > 10000
                AND (title_type='movie' OR title_type='tvMovie')
                AND average_rating > 5.0
                """
        df = pd.read_sql_query(sql, con=connection)
        df.to_csv('titles.csv', index=False) # checkpoint (to avoid downloading too many times from postgres)
    else: # if file exists, just load it
        print('file exists, loading')
        df = pd.read_csv('titles.csv')

    final_exists = exists('final.csv')
    if not final_exists:
        final = get_bom_result(df)
    else:
        print('file exists, loading')
        final = pd.read_csv('final.csv')
    
    final.to_sql(name='movie_boxoffice', con=connection, index=False)

if __name__=="__main__":
    add_bom_db()
