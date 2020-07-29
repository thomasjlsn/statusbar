#!/usr/bin/env python3

from time import sleep
from uuid import uuid4

from lib_pybar.args import args
from lib_pybar.helpers import make_meter_values

PYBAR_SOCKET = '/tmp/pybar.sock'


class SharedData:
    """Data shared between blocks and the statusbar."""
    data = {}


class RemoveBlock(Exception):
    """
    Blocks may raise this from their source function to cleanly remove
    themselves from the statusbar.
    """
    pass


class Block(SharedData):
    def __init__(self, source=None, label=None, sleep_ms=1000, weight=0):
        self.source: callable = source
        self.label = label
        self.sleep_ms = sleep_ms
        self.weight = str(weight).zfill(8)  # Determines order of blocks
        self.key = f'{self.weight}-{uuid4()}'

    def __update(self):
        if self.label is not None:
            self.data[self.key] = f'{self.label.upper()}: {self.source()}'
        else:
            self.data[self.key] = self.source()

    def __remove_block(self):
        self.data.pop(self.key, None)

    def run(self):
        while True:
            try:
                self.__update()
                sleep(self.sleep_ms / 1000)

            except RemoveBlock:
                self.__remove_block()
                break

            except Exception as e:
                # Display the error briefly
                self.data[self.key] = f'ERROR: "{e}"'
                sleep(10)
                self.__remove_block()
                break


class StatusBar(SharedData):
    @property
    def active_blocks(self):
        return [
            self.data[block] for block in sorted(self.data.keys())
            if self.data[block] is not None
        ]

    def statusbar(self):
        return ''.join([f' {block} ' for block in self.active_blocks])


meter_values = make_meter_values(int(args.width))


def meter(percentage):
    return meter_values[int(percentage)]
