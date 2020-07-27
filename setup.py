#!/usr/bin/env python3

from setuptools import setup

setup(
    name='pybar',
    version='0.1',
    packages=[
        'lib_pybar',
        'lib_pybar.blocks',
    ],
    scripts=['pybard', 'pybar'],
)
