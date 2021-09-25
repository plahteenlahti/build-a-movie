from bs4 import BeautifulSoup
import urllib.request
import re
from matplotlib.pyplot import title
import pandas as pd
import numpy as np

def fetch_htmldata(url):
    try:
        data = urllib.request.urlopen(url)
    except:
        print("An error occured.")
    soup = BeautifulSoup(data, "html.parser")
    return soup

def get_urls(soup):
    searchResults = soup.find_all('main')
    titleUrls = []
    for div in searchResults:
        links = div.findAll('a')
        for a in links:
            if 'title' in a.get('href'):
                titleUrls.append(a.get('href'))
    
    urls = []

    for url in titleUrls:
        urls.append('https://www.boxofficemojo.com'+url)

    return urls

def fetch_movie_data(soup):
    # Header data
    header = soup.find('h1', {'class': 'a-size-extra-large'})
    titleY = header.getText()
    titleY = re.sub('[^0-9a-zA-Z\s]+', '', titleY)
    title = (re.search('[a-zA-Z\s]+', titleY).group(0)).strip()
    year = re.search('[0-9]+', titleY).group(0)

    # Left div data
    leftDiv = soup.findAll('div', {'class': 'a-section a-spacing-none mojo-performance-summary'})
    for div in leftDiv:
        txt = div.text
    nolines = txt.replace(' ', '')
    nolines = nolines.replace('\n', '')
    worldwide_lifetime_gross = re.search('Worldwide(.*)', nolines).group(1)
    dlg = (re.search('Domestic(.*)International', nolines).group(1)).split('$',1)
    domestic_lifetime_gross = '$' + dlg[1]
    domestic_percent = dlg[0].replace('(', '').replace(')', '')
    flg = (re.search('International(.*)Worldwide', nolines).group(1)).split('$',1)
    foreign_lifetime_gross = '$' + flg[1]
    foreign_percent = flg[0].replace('(', '').replace(')', '')

    # Right div data
    rightDiv = soup.findAll('div', {'class': 'a-section a-spacing-none mojo-summary-values mojo-hidden-from-mobile'})
    for div in rightDiv:
        txt = div.text
    nolines = txt.replace(' ', '')
    nolines = nolines.replace('\n', '')
    dist = re.search('Distributor(.*)Seefull', nolines).group(1)
    opening = re.search('Opening(.*)Budget', nolines).group(1)
    budget = re.search('Budget(.*)Earliest', nolines).group(1)
    date = re.search('ReleaseDate(.*)MPAA', nolines).group(1)
    rtime = re.search('RunningTime(.*)Genres', nolines).group(1)
    genres = re.search('Genres(.*)IMDbProSee', nolines).group(1)

    return title, worldwide_lifetime_gross,\
        domestic_lifetime_gross, domestic_percent,\
        foreign_lifetime_gross, foreign_percent, year,\
        dist, opening, budget, date, rtime, genres

def clean_data(df):
    df = df.drop_duplicates()
    df = df.dropna()
    df['worldwide_lifetime_gross'] = df['worldwide_lifetime_gross'].apply(lambda x: int(''.join(s for s in x if s.isdigit())))
    df['domestic_lifetime_gross'] = df['domestic_lifetime_gross'].apply(lambda x: int(''.join(s for s in x if s.isdigit())))
    df['foreign_lifetime_gross'] = df['foreign_lifetime_gross'].apply(lambda x: int(''.join(s for s in x if s.isdigit())))
    df['opening'] = df['opening'].apply(lambda x: int(''.join(s for s in x if s.isdigit())))
    df['budget'] = df['budget'].apply(lambda x: int(''.join(s for s in x if s.isdigit())))
    return df

def get_title_data(titleName):
    searchUrl = 'https://www.boxofficemojo.com/search/?q=' + (titleName.replace(' ', '+')).lower()

    soup = fetch_htmldata(searchUrl)
    complete_urls = get_urls(soup)

    movieData = pd.DataFrame(columns = ['title', 'worldwide_lifetime_gross',
                                        'domestic_lifetime_gross', 'domestic_percent',
                                        'foreign_lifetime_gross', 'foreign_percent',
                                        'year','distributor',
                                        'opening','budget',
                                        'date','runtime','genres'])
    counter = 0

    for url in complete_urls:
        soup = fetch_htmldata(url)
        try:
            title, wlg, dlg, dp, flg, fp, year, dist, opening, budget, date, rtime, genres = fetch_movie_data(soup)
            #make table
            movieData = movieData.append({'title' : title, 'worldwide_lifetime_gross' : wlg,
                            'domestic_lifetime_gross' : dlg, 'domestic_percent' : dp,
                            'foreign_lifetime_gross' : flg, 'foreign_percent' : fp,
                            'year' : year, 'distributor' : dist , 'opening' : opening,
                            'budget' : budget, 'date' : date, 'runtime' : rtime,
                            'genres' : genres} , ignore_index=True)
        except:
            print('    --Missing data')
            movieData = movieData.append({
                            'title' : np.nan, 'worldwide_lifetime_gross' : np.nan,
                            'domestic_lifetime_gross' : np.nan, 'domestic_percent' : np.nan,
                            'foreign_lifetime_gross' : np.nan, 'foreign_percent' : np.nan,
                            'year' : np.nan, 'distributor' : np.nan , 'opening' : np.nan,
                            'budget' : np.nan, 'date' : np.nan, 'runtime' : np.nan,
                            'genres' : np.nan} , ignore_index=True)
        counter += 1

    movieData = clean_data(movieData)
    movieData.to_csv('search_results.csv', index=False)

if __name__=="__main__":
    get_title_data('Harry Potter')
