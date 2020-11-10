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
PYBAR_WEATHER_LATTITUDE = getenv('PYBAR_WEATHER_LATTITUDE', 34.409211)
PYBAR_WEATHER_LONGITUDE = getenv('PYBAR_WEATHER_LONGITUDE', -118.914837)

# To specify celsius or fahrenheit
PYBAR_WEATHER_UNITS = getenv('PYBAR_WEATHER_UNITS', 'fahrenheit').lower()[0]

weather_conditions = {
    # key: (show?, 'name') # original condition name
    # ======================================================================
    'c':   (0, 'clear'),   # Clear
    'lc':  (1, 'cloudy'),  # Light Cloud
    'hc':  (1, 'cloudy'),  # Heavy Cloud
    's':   (1, 'rain'),    # Showers
    'lr':  (1, 'rain'),    # Light Rain
    'hr':  (1, 'rain'),    # Heavy Rain
    't':   (1, 'storm'),   # Thunderstorm
    'h':   (1, 'hail'),    # Hail
    'sl':  (1, 'sleet'),   # Sleet
    'sn':  (1, 'snow'),    # Snow
}

wind_conditions = [
    # (range, show?, 'name')
    # ======================================================================
    ([*range(0, 2)],     0, 'still'),
    ([*range(2, 7)],     0, 'calm'),
    ([*range(7, 11)],    0, 'light breeze'),
    ([*range(11, 15)],   1, 'moderate breeze'),
    ([*range(15, 19)],   1, 'strong breeze'),
    ([*range(19, 24)],   1, 'light wind'),
    ([*range(24, 29)],   1, 'moderate wind'),
    ([*range(29, 35)],   1, 'strong wind'),
    ([*range(35, 45)],   1, 'gale'),
    ([*range(45, 55)],   1, 'strong gale'),
    ([*range(55, 65)],   1, 'whole gale'),
    ([*range(65, 74)],   1, 'extreme wind'),
    ([*range(74, 96)],   1, 'catagory 1 hurricane'),
    ([*range(96, 112)],  1, 'catagory 2 hurricane'),
    ([*range(112, 130)], 1, 'catagory 3 hurricane'),
    ([*range(130, 157)], 1, 'catagory 4 hurricane'),
    ([*range(157, 200)], 1, 'catagory 5 hurricane'),
    ([*range(201, 500)], 1, 'may god have mercy on your soul'),
]


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


search = MetaWeatherSearchAPI(
    PYBAR_WEATHER_LATTITUDE,
    PYBAR_WEATHER_LONGITUDE,
)

preferred_units = {
    'c': celsius,
    'f': fahrenheit,
}[PYBAR_WEATHER_UNITS]


def check_weather():
    today = search.weather()[0]

    temp = preferred_units(today['the_temp'])

    weather_is_noteworthy, weather_condition = weather_conditions[
        today['weather_state_abbr']
    ]

    wind_speed = int(today['wind_speed'])

    wind_is_noteworthy, wind_condition = 0, 'calm'

    for condition in wind_conditions:
        if wind_speed in condition[0]:
            wind_is_noteworthy, wind_condition = condition[1:]
            break

    report = temp

    if weather_is_noteworthy:
        report += f', {weather_condition}'

    if wind_is_noteworthy:
        report += f', {wind_condition}'

    return report


def main():
    return Block(
        source=check_weather,
        sleep_ms=1000 * (60 * 15),  # 15 mins
        weight=100,
    )
