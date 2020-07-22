#!/usr/bin/env python3
"""Main entrypoint to statusd."""

from argparse import ArgumentParser

argparser = ArgumentParser()

argparser.add_argument('-b', '--battery',    dest='battery',   action='store_true', help='battery percentage')
argparser.add_argument('-B', '--backlight',  dest='backlight', action='store_true', help='screen backlighting')
argparser.add_argument('-c', '--clock',      dest='clock',     action='store_true', help='a clock')
argparser.add_argument('-C', '--cpu',        dest='cpu',       action='store_true', help='cpu percentage')
argparser.add_argument('-d', '--disk-usage', dest='disks',     action='store_true', help='disk usage')
argparser.add_argument('-m', '--memory',     dest='mem',       action='store_true', help='memory usage')
argparser.add_argument('-n', '--net-usage',  dest='net',       action='store_true', help='network usage')

args = argparser.parse_args()


def main():
    # Import Components after args are processed. This way, if the user
    # runs --help, it will not require root or try to restart the server.
    from threading import Thread

    from statusdlib.core.server import statusbar
    from statusdlib.stats import (backlight, battery, cpu, date, disks,
            memory, network)

    # Main thread
    target_threads = [statusbar]

    # Optional threads
    if args.battery:   target_threads += [battery.life]
    if args.backlight: target_threads += [backlight.level]
    if args.clock:     target_threads += [date.clock]
    if args.cpu:       target_threads += [cpu.usage]
    if args.disks:     target_threads += [disks.usage]
    if args.mem:       target_threads += [memory.usage]
    if args.net:       target_threads += [network.usage]

    threads = [
        Thread(target=thread.run)
        for thread in target_threads
    ]

    try:
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        return 0

    except KeyboardInterrupt:
        return 1

    finally:
        for thread in threads:
            thread.join()
