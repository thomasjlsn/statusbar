'''Weather condition & temperature.'''

import json
import posixpath
from os import getenv

from lib_pybar.core import Block
from requests import get

# These environment variables are used to
# set your location for the weather block.
# Currently defaults to LA.
PYBAR_LATT = getenv('PYBAR_LATT', 34.409211)
PYBAR_LONG = getenv('PYBAR_LONG', -118.914837)

_weather_conditions = {
    # key: (show?, 'name')   # original condition name
    # ====================================================
    'sn':  (1, 'snow'),      # Snow
    'sl':  (1, 'sleet'),     # Sleet
    'h':   (1, 'hail'),      # Hail
    't':   (1, 'storm'),     # Thunderstorm
    'hr':  (1, 'rain'),      # Heavy Rain
    'lr':  (1, 'rain'),      # Light Rain
    's':   (1, 'rain'),      # Showers
    'hc':  (1, 'overcast'),  # Heavy Cloud
    'lc':  (0, 'overcast'),  # Light Cloud
    'c':   (0, 'clear'),     # Clear
}


def fahrenheit(celsius):
    return (celsius * 9/5) + 32


def getjson(url):
    return json.loads(get(url).text)


class MetaWeatherSearchAPI:
    api_base = 'https://www.metaweather.com/api/location'

    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def coords(self):
        return getjson(posixpath.join(
            self.api_base, f'search/?lattlong={self.lat},{self.lon}'
        ))

    def weather(self):
        return getjson(posixpath.join(
            self.api_base, str(self.coords()[0]['woeid'])
        ))

    def consolidated(self):
        return self.weather()['consolidated_weather']


search = MetaWeatherSearchAPI(PYBAR_LATT, PYBAR_LONG)


def check_weather():
    today = search.consolidated()[0]

    _temp = int(fahrenheit(today['the_temp']))

    temp = f'{_temp}°F'

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
