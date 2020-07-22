#!/usr/bin/env python3

import os

from statusdlib.core.components import Segment
from statusdlib.helpers import bytes_to_largest_units, readint


class Network:
    interfaces = [d for d in os.listdir('/sys/class/net/') if d != 'lo']
    usage = (0, 0)


network = Network()


# ==========================================================================
# Active network interfaces
# ==========================================================================

def interfaces():
    """Returns state of network interfaces"""
    up = []

    for interface in network.interfaces:
        with open(f'/sys/class/net/{interface}/operstate', 'r') as s:
            if s.readline().strip() == 'up':
                up.append(interface)

    if not up:
        return 'offline'

    if int(strftime('%S')[0]) % 2 == 0:
        return os.popen('ip route get 1.1.1.1').readlines()[0].split()[6]
    return ' '.join(up)


operstate = Segment(
    source=interfaces,
    label='net',
    sleep_ms=1000,
    weight=10,
)


# ==========================================================================
# Network usage.
# ==========================================================================

def net_usage():
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


usage = Segment(
    source=net_usage,
    sleep_ms=1000,
    weight=5,
)
