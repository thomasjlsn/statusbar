#!/usr/bin/env python3
"""args.py"""

from argparse import ArgumentParser

argparser = ArgumentParser()

argparser.add_argument('start', nargs='?', help='start the pybar daemon')
argparser.add_argument('stop',  nargs='?', help='stop the pybar daemon')

argparser.add_argument('--abort', dest='abort',     default=False, action='store_true', help='do not try to restart threads that die')
argparser.add_argument('--width', dest='width',     default=10,    type=int,            help='width of meters')

args = argparser.parse_args()
