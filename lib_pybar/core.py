#!/usr/bin/env python3

from time import sleep
from uuid import uuid4

from lib_pybar.widgets import label

PYBAR_SOCKET = '/tmp/pybar.sock'


class SharedData:
    """Data shared between blocks and the statusbar."""
    data = {}


class Block(SharedData):
    def __init__(self,
                 prerequisites: bool = True,
                 source: callable = None,
                 sleep_ms: int = 1000,
                 weight: int = 0):

        self.prerequisites = prerequisites
        self.source = source
        self.sleep_ms = sleep_ms
        self.weight = str(weight).zfill(8)  # Determines order of blocks
        self.key = f'{self.weight}-{uuid4()}'

    def run(self):
        if not self.prerequisites:
            return

        while True:
            try:
                self.data[self.key] = self.source()
                sleep(self.sleep_ms / 1000)

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
