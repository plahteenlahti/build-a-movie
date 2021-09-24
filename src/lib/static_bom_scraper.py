from bs4 import BeautifulSoup
import urllib.request
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def fetch_htmldata(url):
    try:
        data = urllib.request.urlopen(url)
    except:
        print("An error occured.")
    soup = BeautifulSoup(data, "html.parser")
    return soup

def fetch_summary(soup):
    mydivs = soup.findAll("div", {"class": "a-section a-spacing-none mojo-summary-values mojo-hidden-from-mobile"})
    for div in mydivs:
        txt = div.text

    nolines = txt.replace(" ","")
    nolines = nolines.replace("\n","")

    dist = re.search('Distributor(.*)Seefull', nolines).group(1)
    opening = re.search('Opening(.*)Budget', nolines).group(1)
    budget = re.search('Budget(.*)Earliest', nolines).group(1)
    date = re.search('ReleaseDate(.*)MPAA', nolines).group(1)
    rtime = re.search('RunningTime(.*)Genres', nolines).group(1)
    genres = re.search('Genres(.*)IMDbProSee', nolines).group(1)

    return dist, opening, budget, date, rtime, genres

def get_movies(soup):
    table = soup.find_all('table')[0]

    all_movies = pd.DataFrame(columns=['rank','title','worldwide_lifetime_gross','domestic_lifetime_gross',
                                       'domestic_percent', 'foreign_lifetime_gross','foreign_percent','year'], index = [0])
    counter = 0

    for row in table.find_all('tr'):

        columns = row.find_all('td')
        column_list = []
        for column in columns:
            column_list.append(column.get_text())

        if counter > 0:
            all_movies.loc[len(all_movies)] = column_list

        counter += 1

    return all_movies.iloc[1:]

def get_urls(soup):
    table = soup.find_all('table')[0]
    links = table.findAll('a')[0]
    all_links = []

    for link in table.findAll('a'):
        if 'title' in link.get('href'):
            all_links.append(link.get('href'))

    #append to complete link
    complete_urls = []
    for url in all_links:
        complete_urls.append('https://www.boxofficemojo.com' + url)

    return complete_urls

def get_from_one_page(page):
    movies_url = page
    soup = fetch_htmldata(movies_url)

    complete_urls = get_urls(soup)
    movie_data = get_movies(soup)


    summary = pd.DataFrame(columns = ["distributor","opening","budget","date","runtime","genres"])
    counter = 0

    for url in complete_urls:
        print('Processing "' + movie_data['Title'].iloc[counter]+'".')
        soup = fetch_htmldata(url)
        try:
            dist, opening, budget, date, rtime, genres = fetch_summary(soup)
            #make table
            summary = summary.append({'distributor' : dist , "opening" : opening,
                            "budget" : budget, "date" : date, "runtime" : rtime,
                            "genres" : genres} , ignore_index=True)
        except:
            print('    --Missing data')
            summary = summary.append({'distributor' : np.nan , "opening" : '$0',
                            "budget" : '$0', "date" : np.nan, "runtime" : np.nan,
                            "genres" : np.nan} , ignore_index=True)
        counter += 1


    movie_data = movie_data.reset_index(drop=True)
    data = pd.concat([movie_data,summary],axis = 1)

    return data

def get_bom_top_data():
    urls = [
        'https://www.boxofficemojo.com/chart/ww_top_lifetime_gross/?area=XWW',
        'https://www.boxofficemojo.com/chart/ww_top_lifetime_gross/?area=XWW&offset=200',
        'https://www.boxofficemojo.com/chart/ww_top_lifetime_gross/?area=XWW&offset=400',
        'https://www.boxofficemojo.com/chart/ww_top_lifetime_gross/?area=XWW&offset=600',
        'https://www.boxofficemojo.com/chart/ww_top_lifetime_gross/?area=XWW&offset=800'
        ]

    df = pd.DataFrame(columns=['rank','title','worldwide_lifetime_gross','domestic_lifetime_gross',
                                       'domestic_percent', 'foreign_lifetime_gross','foreign_percent','year','distributor','opening','budget','date','runtime', 'genres'])
    df.to_csv('bom.csv', index=False)
    for url in urls:
        d = get_from_one_page(url)

        # TODO: clean data (remove $ and commas and delete uncomplete data)
        d.to_csv('bom.csv', mode='a', header=False, index=False)

if __name__=="__main__":
    get_bom_top_data()
