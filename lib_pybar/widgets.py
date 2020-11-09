'''widgets.py'''

from os import getenv

PYBAR_METER_WIDTH = getenv('PYBAR_METER_WIDTH', 10)


def label(label_text, string):
    return ': '.join((label_text.upper(), string))


def __make_meter_values(meter_width):
    '''Assign unicode bars to percentages.'''
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


__meter_values = __make_meter_values(int(PYBAR_METER_WIDTH))


def meter(percentage):
    return __meter_values[int(percentage)]
