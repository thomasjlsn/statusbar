#!/usr/bin/env python3

from time import sleep
from uuid import uuid4

from lib_pybar.widgets import label

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
    def __init__(self, source=None, sleep_ms=1000, weight=0):
        self.source: callable = source
        self.sleep_ms = sleep_ms
        self.weight = str(weight).zfill(8)  # Determines order of blocks
        self.key = f'{self.weight}-{uuid4()}'

    def run(self):
        while True:
            try:
                self.data[self.key] = self.source()
                sleep(self.sleep_ms / 1000)

            except RemoveBlock:
                self.data.pop(self.key, None)
                break

            except Exception as e:
                # Display the error briefly
                self.data[self.key] = label('error', f'"{e}"')
                sleep(10)
                self.data.pop(self.key, None)
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
