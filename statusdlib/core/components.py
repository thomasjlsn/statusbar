#!/usr/bin/env python3
"""
'Components' are the main abstraction used in statusd.

A Component is any part of the statusbar that:
    * has a source of data (a function that returns a string)
    * has access to SharedData
    * sleeps for some period of time

"""

import time

from statusdlib.core.data import SharedData
from statusdlib.helpers import laptop_open, uuid


class Component(SharedData):
    def __init__(self, source=None, label=None, sleep_ms=1000, weight=0):
        # The function data is recieved from
        self.source = source

        # An optional label for the component
        self.label = label

        # Time in ms to sleep, between 0.5 ... 20 seconds
        self.sleep_ms = max(500, min(20000, sleep_ms))

        # Used to determine order of components
        self.weight = str(weight).zfill(8)

        # Unique key to store data
        self.uuid = f'{self.weight}-{uuid()}'

    def update(self):
        component = self.source()
        if component is not None:
            if self.label is not None:
                self.data[self.uuid] = f'{self.label.upper()}: {component}'
            else:
                self.data[self.uuid] = component

    def sleep(self):
        if laptop_open():
            time.sleep(self.sleep_ms / 1000)
        else:
            # Sleep longer.
            time.sleep((self.sleep_ms * 3) / 1000)

    def run(self):
        while True:
            try:
                self.update()
                self.sleep()

            except Exception as e:
                # Display the error briefly
                self.data[self.uuid] = f'ERROR: "{e}"'
                time.sleep(10)

                # Set data to None, effectively removing the component,
                # allowing the status bar to continue running without it.
                self.data[self.uuid] = None
                break


class Segment(Component):
    """One segment of the status bar."""
    pass
