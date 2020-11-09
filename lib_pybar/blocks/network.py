'''Network usage.'''

from os import listdir

from lib_pybar.core import Block
from lib_pybar.helpers import human_readable, readint


class Network:
    interfaces = [d for d in listdir('/sys/class/net/') if d != 'lo']
    usage = (0, 0)

    # number of iterations in which network is idle before hiding the block
    idle_cycle_max = 2
    idle_cycle_cur = 0


network = Network()


def usage():
    tx_bytes, rx_bytes = 0, 0

    for i in network.interfaces:
        tx_bytes += readint(f'/sys/class/net/{i}/statistics/tx_bytes')
        rx_bytes += readint(f'/sys/class/net/{i}/statistics/rx_bytes')

    tx_old, rx_old = network.usage

    tx_rate = (tx_bytes - tx_old)
    rx_rate = (rx_bytes - rx_old)

    network.usage = (tx_bytes, rx_bytes)

    if (tx_rate == 0) and (rx_rate == 0):
        network.idle_cycle_cur += 1
        return None
    else:
        network.idle_cycle_cur = 0

    if network.idle_cycle_cur == network.idle_cycle_max:
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
