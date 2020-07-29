#!/usr/bin/env python3

from time import sleep

from lib_pybar.args import args
from lib_pybar.helpers import make_meter_values, uuid


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
        # The function data is recieved from
        self.source = source

        # An optional label for the block
        self.label = label

        # Time in ms to sleep, between 0.5 ... 20 seconds
        self.sleep_ms = max(500, min(20000, sleep_ms))

        # Used to determine order of blocks
        self.weight = str(weight).zfill(8)

        # Unique key to store data
        self.uuid = f'{self.weight}-{uuid()}'

    def __update(self):
        value = self.source()
        if value is not None:
            if self.label is not None:
                self.data[self.uuid] = f'{self.label.upper()}: {value}'
            else:
                self.data[self.uuid] = value

    def __remove_block(self):
        self.data.pop(self.uuid, None)

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
                self.data[self.uuid] = f'ERROR: "{e}"'
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
