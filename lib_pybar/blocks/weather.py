'''Temperature.'''

from re import search

from lib_pybar.core import Block
from requests import get


def get_temp():
    url = 'https://darksky.net/forecast/34.408,-118.915/us12/en'
    temp = search(r'(?<=summary swap">)[0-9]+(?=˚)', get(url).text)[0]
    return f'{temp}°F'


def main():
    return Block(
        source=get_temp,
        sleep_ms=1000 * (60 * 15),  # 15 mins
        weight=100,
    )
