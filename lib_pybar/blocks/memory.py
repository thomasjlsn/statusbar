'''Memory usage.'''

from lib_pybar import Block, label, meter, readint

swap_percent = 100 - readint('/proc/sys/vm/swappiness')


def memory_usage():
    mem = {}

    with open('/proc/meminfo', 'r') as f:
        for line in f.readlines():
            line = line.strip().split()

            if len(line) == 3:
                key, val, _ = line
                key = key[:-1]

            elif len(line) == 2:
                key, val = line
                key = key[:-1]

            mem[key] = int(val)

    # memory usage as calculated by `free(1)`
    percent = (100 / mem['MemTotal']) * (
        mem['MemTotal'] - mem['Buffers'] - mem['Cached'] - mem['MemFree']
    )

    # Only show memory usage when we are more than halfway to swapping
    if percent > (swap_percent / 2):
        return label('ram', meter(percent))
    else:
        return None


def main():
    return Block(
        source=memory_usage,
        sleep_ms=1000,
        weight=70,
    )
