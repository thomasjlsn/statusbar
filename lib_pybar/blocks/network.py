'''Network usage.'''

from os import listdir

from lib_pybar import Block, human_readable, readint


class network:
    interfaces = [d for d in listdir('/sys/class/net/') if d != 'lo']
    usage = (0, 0)


def usage():
    tx_bytes, rx_bytes = 0, 0

    for i in network.interfaces:
        tx_bytes += readint(f'/sys/class/net/{i}/statistics/tx_bytes')
        rx_bytes += readint(f'/sys/class/net/{i}/statistics/rx_bytes')

    tx_old, rx_old = network.usage

    rx_rate = rx_bytes - rx_old
    tx_rate = tx_bytes - tx_old

    network.usage = (tx_bytes, rx_bytes)

    if not any((tx_rate, rx_rate)):
        return None

    return ' '.join([
        f'↑ {human_readable(tx_rate)}',
        f'↓ {human_readable(rx_rate)}',
    ])


def main():
    return Block(
        source=usage,
        sleep_ms=1000,
        weight=5,
    )
