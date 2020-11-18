'''Temperature.'''

from re import search
from sys import stderr
from time import sleep, strftime

from lib_pybar import Block
from requests import RequestException, get

url = 'https://darksky.net/forecast/34.408,-118.915/us12/en'
rate_limit = 60 * 10


class Temperature:
    was_last_checked = int(strftime('%s'))
    raw = None

    def F(self):
        return (str(self.raw)
                if self.raw is not None else '--')

    def C(self):
        return (str(int((int(self.raw) - 32) * (5 / 9)))
                if self.raw is not None else '--')


temperature = Temperature()


def get_temp():
    now = int(strftime('%s'))

    if now - temperature.was_last_checked > rate_limit or temperature.raw is None:
        stderr.write('checking the weather\n')

        try:
            response = get(url)
            if response.status_code == 200:
                temperature.raw = search(
                    r'(?<=summary swap">)[0-9]+(?=˚)', response.text
                )[0]

        except RequestException as e:
            temperature.raw = None
            stderr.write(f'RequestException: {e}\n')

    if int(strftime('%S')[0]) % 2 == 0:
        return f'{temperature.C()}°C'
    return f'{temperature.F()}°F'


def main():
    return Block(
        source=get_temp,
        sleep_ms=1500,
        weight=100,
    )
