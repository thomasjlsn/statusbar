'''Main pybar configuration file.'''


class config:
    # Global statusbar settings. ===========================================
    PYBAR_STATUSBAR_DATE_FORMAT = '%a, %b %d %k:%M'
    PYBAR_STATUSBAR_METERS = True
    PYBAR_STATUSBAR_METER_WIDTH = 10

    # Enable or disable blocks. ============================================
    PYBAR_BLOCKS_BACKLIGHT = False
    PYBAR_BLOCKS_BATTERY = True
    PYBAR_BLOCKS_CPU = True
    PYBAR_BLOCKS_DISKS = True
    PYBAR_BLOCKS_MEMORY = True
    PYBAR_BLOCKS_NETWORK = True
    PYBAR_BLOCKS_PACMAN = True
    PYBAR_BLOCKS_WEATHER = True

    # Modify server behavior. ==============================================
    PYBAR_SERVER_MAX_CONNECTIONS = 5
    PYBAR_SERVER_MTU = 1024
    PYBAR_SERVER_SOCKET = '/tmp/pybar.sock'
    PYBAR_SERVER_ENCODING = 'utf-8'

    # Settings for the temperature block. ==================================
    PYBAR_TEMPERATURE_LATLON = (34.408, -118.915)
    PYBAR_TEMPERATURE_UNITS = 'both'  # 'c', 'f', or 'both'
