'''Main pybar configuration file.'''


class config:
    # Enable or disable blocks. ============================================

    # Backlight brightness as percentage.
    PYBAR_BLOCKS_BACKLIGHT = False

    # Battery percentage + charge state.
    PYBAR_BLOCKS_BATTERY = True

    # CPU frequency as percentage.
    PYBAR_BLOCKS_CPU = True

    # Disk usage per disk / partition as percentage.
    PYBAR_BLOCKS_DISKS = True

    # Memory usage as percentage.
    PYBAR_BLOCKS_MEMORY = True

    # Network usage, up and down.
    PYBAR_BLOCKS_NETWORK = True

    # Number of available updates, *.pacnew files, and orphaned packages.
    PYBAR_BLOCKS_PACMAN = True

    # Current temperature.
    PYBAR_BLOCKS_WEATHER = True

    # Statusbar settings. ==================================================

    # How the date / time is formatted.
    # See `man date` for all formatting options.
    PYBAR_STATUSBAR_DATE_FORMAT = '%a, %b %d %k:%M'

    # Whether to display percentages as Unicode meters, or as is.
    PYBAR_STATUSBAR_METERS = True

    # How many characters wide these meters should be.
    PYBAR_STATUSBAR_METER_WIDTH = 10

    # Modify server behavior. ==============================================

    # Maximum number of concurrent connections to the server.
    PYBAR_SERVER_MAX_CONNECTIONS = 5

    # Maximum amount of data the server should transmit in each response.
    # (in bytes)
    PYBAR_SERVER_MTU = 256

    # Location of the socket.
    PYBAR_SERVER_SOCKET = '/tmp/pybar.sock'

    # How the server should encode the data.
    PYBAR_SERVER_ENCODING = 'utf-8'

    # Settings for the temperature block. ==================================

    # Your current latitude and longitude, used to look up the temperature.
    # Find out what it is at https://darksky.net/forecast/.
    # (this is the website used to get the temp)
    #
    # The default value is near L.A.
    PYBAR_TEMPERATURE_LATLON = (34.408, -118.915)

    # Preferred units to display temperature in.
    # 'c', 'f', or 'both'
    # 'both' toggles between the two every ~10 seconds
    PYBAR_TEMPERATURE_UNITS = 'both'
