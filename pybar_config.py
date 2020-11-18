config = {
    'statusbar': {
        # Global statusbar settings.
        'date_format': '%a, %b %d %k:%M',
        'max_width': None,
        'meters': True,
        'meter_width': 10,
    },
    'blocks': {
        # Enable or disable blocks.
        'backlight': False,
        'battery': True,
        'cpu': True,
        'disks': True,
        'memory': True,
        'network': True,
        'pacman': True,
        'weather': True,
    },
    'server': {
        # Modify server behavior.
        'max_connections': 5,
        'socket': '/tmp/pybar.sock',
    }
}
