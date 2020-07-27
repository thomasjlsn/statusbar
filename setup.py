#!/usr/bin/env python3

from setuptools import setup

setup(
    name='statusd',
    version='0.1',
    packages=[
        'statusdlib',
        'statusdlib.blocks',
    ],
    scripts=['statusd', 'statusbar'],
)
