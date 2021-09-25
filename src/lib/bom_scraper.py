from bs4 import BeautifulSoup
import urllib.request
import re
import pandas as pd
import numpy as np

"""
EXPOSED METHODS
Public API methods
"""

# Returns movie data results given a query to the website
def get_search_data(titleName):
    searchUrl = 'https://www.boxofficemojo.com/search/?q=' + (titleName.replace(' ', '+')).lower()

    soup = __fetch_htmldata(searchUrl)
    complete_urls = __get_search_urls(soup)

    movieData = pd.DataFrame(columns = ['title', 'worldwide_lifetime_gross',
                                        'domestic_lifetime_gross', 'domestic_percent',
                                        'foreign_lifetime_gross', 'foreign_percent',
                                        'year','distributor',
                                        'opening','budget',
                                        'date','runtime','genres'])
    counter = 0

    for url in complete_urls:
        soup = __fetch_htmldata(url)
        try:
            title, wlg, dlg, dp, flg, fp, year, dist, opening, budget, date, rtime, genres = __fetch_movie_search_data(soup)
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

    movieData = __clean_data(movieData)
    movieData.to_csv('downloaded/search_results.csv', index=False)

# Returns top 1000 selling movies data
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
    df.to_csv('downloaded/bom.csv', index=False)
    for url in urls:
        d = __get_top_from_one_page(url)
        d = __clean_data(d)
        d.to_csv('downloaded/bom.csv', mode='a', header=False, index=False)

"""
PRIVATE METHODS
Private utility methods, not to be used outside of this file.
"""
def __fetch_htmldata(url):
    try:
        data = urllib.request.urlopen(url)
    except:
        print('Cannot reach url', url)
    soup = BeautifulSoup(data, 'html.parser')
    return soup

def __get_search_urls(soup):
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

def __get_top_urls(soup):
    table = soup.find_all('table')[0]
    links = table.findAll('a')[0]
    all_links = []

    for link in table.findAll('a'):
        if 'title' in link.get('href'):
            all_links.append(link.get('href'))

    complete_urls = []
    for url in all_links:
        complete_urls.append('https://www.boxofficemojo.com' + url)

    return complete_urls

def __fetch_top_summary(soup):
    mydivs = soup.findAll('div', {'class': 'a-section a-spacing-none mojo-summary-values mojo-hidden-from-mobile'})
    for div in mydivs:
        txt = div.text

    nolines = txt.replace(' ','')
    nolines = nolines.replace('\n','')

    dist = re.search('Distributor(.*)Seefull', nolines).group(1)
    opening = re.search('Opening(.*)Budget', nolines).group(1)
    budget = re.search('Budget(.*)Earliest', nolines).group(1)
    date = re.search('ReleaseDate(.*)MPAA', nolines).group(1)
    rtime = re.search('RunningTime(.*)Genres', nolines).group(1)
    genres = re.search('Genres(.*)IMDbProSee', nolines).group(1)

    return dist, opening, budget, date, rtime, genres

def __fetch_movie_search_data(soup):
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

def __get_top_movies_data(soup):
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

def __get_top_from_one_page(page):
    movies_url = page
    soup = __fetch_htmldata(movies_url)

    complete_urls = __get_top_urls(soup)
    movie_data = __get_top_movies_data(soup)


    summary = pd.DataFrame(columns = ['distributor','opening','budget','date','runtime','genres'])
    counter = 0

    for url in complete_urls:
        soup = __fetch_htmldata(url)
        try:
            dist, opening, budget, date, rtime, genres = __fetch_top_summary(soup)
            #make table
            summary = summary.append({'distributor' : dist , 'opening' : opening,
                            'budget' : budget, 'date' : date, 'runtime' : rtime,
                            'genres' : genres} , ignore_index=True)
        except:
            print('Missing data')
            summary = summary.append({'distributor' : np.nan , 'opening' : np.nan,
                            'budget' : np.nan, 'date' : np.nan, 'runtime' : np.nan,
                            'genres' : np.nan} , ignore_index=True)
        counter += 1


    movie_data = movie_data.reset_index(drop=True)
    data = pd.concat([movie_data,summary],axis = 1)

    return data

def __clean_data(df):
    df = df.drop_duplicates()
    df = df.dropna()
    df['worldwide_lifetime_gross'] = df['worldwide_lifetime_gross'].apply(lambda x: int(''.join(s for s in x if s.isdigit())))
    df['domestic_lifetime_gross'] = df['domestic_lifetime_gross'].apply(lambda x: int(''.join(s for s in x if s.isdigit())))
    df['foreign_lifetime_gross'] = df['foreign_lifetime_gross'].apply(lambda x: int(''.join(s for s in x if s.isdigit())))
    df['opening'] = df['opening'].apply(lambda x: int(''.join(s for s in x if s.isdigit())))
    df['budget'] = df['budget'].apply(lambda x: int(''.join(s for s in x if s.isdigit())))
    return df

# Just to start
if __name__=="__main__":
    #get_search_data('Harry Potter')
    get_bom_top_data()
