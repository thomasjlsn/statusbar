#!/usr/bin/env python3
"""args.py"""

from argparse import ArgumentParser

argparser = ArgumentParser()

argparser.add_argument('--daemon',           dest='daemon',    default=False, action='store_true', help='start the pybar daemon')
argparser.add_argument('--abort',            dest='abort',     default=False, action='store_true', help='do not try to restart threads that die')
argparser.add_argument('--width',            dest='width',     default=10,    type=int,            help='width of meters')
argparser.add_argument('-b', '--battery',    dest='battery',   default=False, action='store_true', help='battery percentage')
argparser.add_argument('-B', '--backlight',  dest='backlight', default=False, action='store_true', help='screen backlighting')
argparser.add_argument('-c', '--clock',      dest='clock',     default=False, action='store_true', help='a clock')
argparser.add_argument('-C', '--cpu',        dest='cpu',       default=False, action='store_true', help='cpu percentage')
argparser.add_argument('-d', '--disk-usage', dest='disks',     default=False, action='store_true', help='disk usage')
argparser.add_argument('-m', '--memory',     dest='mem',       default=False, action='store_true', help='memory usage')
argparser.add_argument('-n', '--net-usage',  dest='net',       default=False, action='store_true', help='network usage')

args = argparser.parse_args()
