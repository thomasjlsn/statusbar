"""'UI' components."""


def make_meter(meter_width):
    """Assign unicode bars to percentages to make meters."""
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


meter = make_meter(10)


def fancy_meter(percentage=None, current=None, maximum=None):
    if percentage is None:
        val = ((100 / maximum) * current)
    else:
        val = percentage

    return meter[int(val)]
