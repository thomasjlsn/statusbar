#!/usr/bin/env python3
"""args.py"""

from argparse import ArgumentParser

argparser = ArgumentParser()

argparser.add_argument('run', nargs='?', help='start the pybar daemon')

argparser.add_argument('-w', '--width', dest='width', default=10, type=int, help='width of meters')

args = argparser.parse_args()
