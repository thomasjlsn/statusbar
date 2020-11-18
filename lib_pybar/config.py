'''Import the global config file.'''

import importlib.util

spec = importlib.util.spec_from_file_location(
    'pybar_config',
    '/etc/pybar_config.py'
)

pybar_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pybar_config)

config = pybar_config.config
