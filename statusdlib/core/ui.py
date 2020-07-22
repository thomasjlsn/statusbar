#!/usr/bin/env python3
"""Functions that make a unicode meter for the statusbar."""

def make_meter_values(meter_width):
    """Assign unicode bars to percentages."""
    meter = {0: ' ' * meter_width}
    bar_chars = []
    cell_chars = [' ', '▏', '▎', '▍', '▌', '▋', '▊', '▉', '█']
    full = cell_chars[-1]

    fill = ''
    for _ in range(meter_width):
        for char in cell_chars:
            bar = fill + char
            bar_chars.append(bar.ljust(meter_width))
        fill += full

    for percent in range(1, 101):
        end = 0
        for i, char in enumerate(bar_chars):
            start = end
            end = (100 / len(bar_chars)) * i
            if start < percent > end:
                meter[percent] = bar_chars[i]

    return meter


meter_values = make_meter_values(10)


def meter(percentage=None, current=None, maximum=None):
    """
    A Unicode 'meter'.

    A meter needs either:
        * a percentage
        * the current and maximum values

    """
    if percentage is None:
        val = ((100 / maximum) * current)
    else:
        val = percentage

    return meter_values[int(val)]
