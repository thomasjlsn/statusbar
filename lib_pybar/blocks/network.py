#!/usr/bin/env python3
"""Network usage."""

from os import listdir

from lib_pybar.components import Block
from lib_pybar.helpers import bytes_to_largest_units, readint


class Network:
    interfaces = [d for d in listdir('/sys/class/net/') if d != 'lo']
    usage = (0, 0)


network = Network()


def usage():
    tx_bytes, rx_bytes = 0, 0

    for interface in network.interfaces:
        tx_bytes += readint(f'/sys/class/net/{interface}/statistics/tx_bytes')
        rx_bytes += readint(f'/sys/class/net/{interface}/statistics/rx_bytes')

    tx_old, rx_old = network.usage

    tx_rate = (tx_bytes - tx_old)
    rx_rate = (rx_bytes - rx_old)

    network.usage = (tx_bytes, rx_bytes)

    return ' '.join([
        f'↑ {bytes_to_largest_units(tx_rate)}',
        f'↓ {bytes_to_largest_units(rx_rate)}',
    ])


def main():
    return Block(
        source=usage,
        sleep_ms=1000,
        weight=5,
    )
