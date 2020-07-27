#!/usr/bin/env python3
"""args.py"""

from argparse import ArgumentParser

argparser = ArgumentParser()

argparser.add_argument('-a', '--abort',      dest='abort',     action='store_true', help='do not try to restart threads that die')
argparser.add_argument('-b', '--battery',    dest='battery',   action='store_true', help='battery percentage')
argparser.add_argument('-B', '--backlight',  dest='backlight', action='store_true', help='screen backlighting')
argparser.add_argument('-c', '--clock',      dest='clock',     action='store_true', help='a clock')
argparser.add_argument('-C', '--cpu',        dest='cpu',       action='store_true', help='cpu percentage')
argparser.add_argument('-d', '--disk-usage', dest='disks',     action='store_true', help='disk usage')
argparser.add_argument('-m', '--memory',     dest='mem',       action='store_true', help='memory usage')
argparser.add_argument('-n', '--net-usage',  dest='net',       action='store_true', help='network usage')
argparser.add_argument('-w', '--width',      dest='width',     type=int,            help='width of meters')

args = argparser.parse_args()
