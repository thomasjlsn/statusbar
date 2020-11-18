'''Temperature.'''

from re import search
from sys import stderr
from time import strftime

from lib_pybar import Block
from lib_pybar.config import config
from requests import RequestException, get

lat, lon = config.PYBAR_TEMPERATURE_LATLON
url = f'https://darksky.net/forecast/{lat},{lon}/us12/en'
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
            temperature.was_last_checked = int(strftime('%s'))

            if response.status_code == 200:
                temperature.raw = search(
                    r'(?<=summary swap">)[0-9]+(?=˚)', response.text
                )[0]

        except RequestException as e:
            temperature.raw = None
            stderr.write(f'RequestException: {e}\n')

    if config.PYBAR_TEMPERATURE_UNITS == 'both':
        if int(strftime('%S')[0]) % 2 == 0:
            return f'{temperature.C()}°C'
        return f'{temperature.F()}°F'

    elif config.PYBAR_TEMPERATURE_UNITS == 'f':
        return f'{temperature.F()}°F'

    elif config.PYBAR_TEMPERATURE_UNITS == 'c':
        return f'{temperature.C()}°C'


def main():
    return Block(
        source=get_temp,
        sleep_ms=1500,
        weight=100,
    )
