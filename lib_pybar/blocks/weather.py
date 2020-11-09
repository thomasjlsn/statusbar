'''Weather condition & temperature.'''

import json
import posixpath
from functools import lru_cache
from os import getenv

from lib_pybar.core import Block
from requests import get

# These environment variables are used to
# set your location for the weather block.
# Currently defaults to LA.
PYBAR_LATT = getenv('PYBAR_LATT', 34.409211)
PYBAR_LONG = getenv('PYBAR_LONG', -118.914837)

# To specify celsius or fahrenheit
PYBAR_TEMP_UNITS = getenv('PYBAR_UNITS', 'f').lower()[0]

_weather_conditions = {
    # key: (show?, 'name')   # original condition name
    # ====================================================
    'sn':  (1, 'snow'),    # Snow
    'sl':  (1, 'sleet'),   # Sleet
    'h':   (1, 'hail'),    # Hail
    't':   (1, 'storm'),   # Thunderstorm
    'hr':  (1, 'rain'),    # Heavy Rain
    'lr':  (1, 'rain'),    # Light Rain
    's':   (1, 'rain'),    # Showers
    'hc':  (1, 'cloudy'),  # Heavy Cloud
    'lc':  (0, 'cloudy'),  # Light Cloud
    'c':   (0, 'clear'),   # Clear
}


def getjson(url):
    '''Get JSON from a given url.'''
    return json.loads(get(url).text)


def celsius(C):
    '''MetaWeather returns its data in celsius.'''
    return f'{C}°C'


def fahrenheit(temp):
    '''Convert to fahrenheit and format.'''
    F = int((temp * 9/5) + 32)
    return f'{F}°F'


class MetaWeatherSearchAPI:
    api_base = 'https://www.metaweather.com/api/location'

    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    @lru_cache(maxsize=1)
    def woeid(self):
        return getjson(posixpath.join(
            self.api_base, f'search/?lattlong={self.lat},{self.lon}'
        ))[0]['woeid']

    def weather(self):
        return getjson(posixpath.join(
            self.api_base, str(self.woeid())
        ))['consolidated_weather']


search = MetaWeatherSearchAPI(PYBAR_LATT, PYBAR_LONG)

preferred_units = {
    'c': celsius,
    'f': fahrenheit,
}[PYBAR_TEMP_UNITS]


def check_weather():
    today = search.weather()[0]

    temp = preferred_units(today['the_temp'])

    condition_is_noteworthy, condition = _weather_conditions[
        today['weather_state_abbr']
    ]

    if condition_is_noteworthy:
        return f'[{condition}] {temp}'

    return temp


def main():
    return Block(
        source=check_weather,
        sleep_ms=1000 * (60 * 30),  # 30 mins
        weight=100,
    )
