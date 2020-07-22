#!/usr/bin/env python3

from setuptools import setup

setup(
    name='statusd',
    version='0.0',
    packages=[
        'statusdlib',
        'statusdlib.core',
        'statusdlib.stats',
    ],
    scripts=['statusd', 'statusbar'],
)
