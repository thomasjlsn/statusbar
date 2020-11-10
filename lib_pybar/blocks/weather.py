'''Temperature.'''

from re import search
from sys import stderr

from lib_pybar import Block
from requests import RequestException, get


def get_temp():
    try:
        url = 'https://darksky.net/forecast/34.408,-118.915/us12/en'
        temp = '--'
        stderr.write('checking the weather\n')
        response = get(url)

        if response.status_code == 200:
            temp = search(r'(?<=summary swap">)[0-9]+(?=˚)', response.text)[0]

    except RequestException as e:
        stderr.write(f'RequestException: {e}\n')
        pass

    finally:
        return f'{temp}°F'


def main():
    return Block(
        source=get_temp,
        sleep_ms=1000 * (60 * 10),  # 10 mins
        weight=100,
    )
