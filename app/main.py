from fastapi import FastAPI, Request, HTTPException
from enum import Enum
from pytrends.request import TrendReq
from typing import Union
from datetime import datetime, timedelta
from pathlib import Path

import urllib.request
import json
import urllib.parse
import xmltodict
import urllib3
import asyncio
import os

import pandas as pd

app = FastAPI()


class SexName(str, Enum):
    both = 'Both Sexes'
    female = 'Female'
    male = 'Male'


class RaceName(str, Enum):
    all = 'All Races'
    black = 'Black'
    white =  'White'


class StateName(str, Enum):
    alabama = 'Alabama',
    alaska = 'Alaska',
    arizona = 'Arizona',
    arkansas = 'Arkansas',
    california = 'California',
    colorado = 'Colorado',
    connecticut = 'Connecticut',
    delaware = 'Delaware',
    district_of_columbia = 'District of Columbia',
    florida = 'Florida',
    georgia = 'Georgia',
    hawaii = 'Hawaii',
    idaho = 'Idaho',
    illinois = 'Illinois',
    indiana = 'Indiana',
    iowa = 'Iowa',
    kansas = 'Kansas',
    kentucky = 'Kentucky',
    louisiana = 'Louisiana',
    maine = 'Maine',
    maryland = 'Maryland',
    massachusetts = 'Massachusetts',
    michigan = 'Michigan',
    minnesota = 'Minnesota',
    mississippi = 'Mississippi',
    missouri = 'Missouri',
    montana = 'Montana',
    nebraska = 'Nebraska',
    nevada = 'Nevada',
    new_hampshire = 'New Hampshire',
    new_jersey = 'New Jersey',
    new_mexico = 'New Mexico',
    new_york = 'New York',
    north_carolina = 'North Carolina',
    north_dakota = 'North Dakota',
    ohio = 'Ohio',
    oklahoma = 'Oklahoma',
    oregon = 'Oregon',
    pennsylvania = 'Pennsylvania',
    rhode_island = 'Rhode Island',
    south_carolina = 'South Carolina',
    south_dakota = 'South Dakota',
    tennessee = 'Tennessee',
    texas = 'Texas',
    utah = 'Utah',
    vermont = 'Vermont',
    virginia = 'Virginia',
    washington = 'Washington',
    west_virginia = 'West Virginia',
    wisconsin = 'Wisconsin',
    wyoming = 'Wyoming',

YEAR_MOTH_DAY_FORMAT_MASK = '%Y-%m-%d'

def get_start_minus_today_end_dates(days_minus_i):
    """
    Given a days_minus_i parameter, this function returns:
    (today - days_minus_i) and today date as strings. Both in yyyy-mm-dd format
    """

    start_date = (datetime.now() - timedelta(days = days_minus_i)).strftime(YEAR_MOTH_DAY_FORMAT_MASK)
    end_date = datetime.now().strftime(YEAR_MOTH_DAY_FORMAT_MASK)
    return start_date, end_date


@app.get("/life_expectancy/{sex}/{race}/{year}")
async def life_expentancy(sex: SexName, race: RaceName, year):

    to_return = None

    base_url = "https://data.cdc.gov/resource/w9j2-ggv5.json"
    filtered_url = "{}?sex={}&race={}&year={}".format(base_url, urllib.parse.quote(sex), urllib.parse.quote(race), year)

    df = pd.read_json(filtered_url)

    if df.shape[0] > 0:
        to_return = df['average_life_expectancy'].mean()

    return {"average_life_expectancy": to_return}


@app.get("/unemployment/{state}")
async def unemployment(state: StateName, request: Request):

    url = 'https://www.bls.gov/web/laus/lauhsthl.htm'

    tables = pd.read_html(url)
    df = tables[0]
    df.columns = ['State', 'Rate', 'HistoricalHighRate', 'HistoricalHighDate', 'HistoricalLowRate', 'HistoricalLowDate']

    return {"rate": df.loc[df.State == state].squeeze()['Rate']}


@app.get("/trends")
async def trends(
    phrase: str, start_date: Union[str, None]=None, end_date: Union[str, None]=None):

    if (start_date is None) | (end_date is None):
        start_date, end_date = get_start_minus_today_end_dates(14)
    
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date later than end date")
    
    pytrends = TrendReq(hl='en-US', tz=120)
    kw_list = [phrase]
    pytrends.build_payload(
        kw_list, cat=0, timeframe='{} {}'.format(start_date, end_date), geo='', gprop='')
    df = pytrends.interest_over_time()

    return {"interest": df[phrase].to_list()}


@app.get("/weather")
async def weather(request: Request):

    client_ip = request.client.host

    if ('testclient' in client_ip) or (client_ip.startswith('127'))  or (client_ip.startswith('172')):
        # Tests, dev or Docker requests
        loc = "Malaga"
    else:
        with urllib.request.urlopen('https://ipinfo.io/{}/json'.format(client_ip)) as response:
            data = json.loads(response.read().decode())
            if 'loc' in data:
                loc = data['loc']

    if "loc" not in locals():
        raise HTTPException(status_code=400, detail="Imposible to geolocate {}".format(client_ip))

    weatherapi_base_url = "https://api.weatherapi.com/v1/history.xml"
    key = Path(os.path.join(os.path.dirname(__file__), 'weatherapi_key')).read_text()
    dt, end_dt = get_start_minus_today_end_dates(7)
    url = '{}?key={}&q={}&dt={}&end_dt={}'.format(weatherapi_base_url, key, loc, dt, end_dt)

    print(url)
    with urllib.request.urlopen(url) as response:
        my_dict = xmltodict.parse(response.read().decode())
        to_returns = [forecastday['day']['condition']['text']
            for forecastday in my_dict['root']['forecast']['forecastday']]

    return {"weather": to_returns}


@app.get("/trends_weather")
async def trends_weather(phrase: str, request: Request):

    trends_res, weather_res = await asyncio.gather(
        trends(phrase), weather(request))

    return {**trends_res, **weather_res}
