# isort:skip_file
# from os import chdir, getcwd

# oldcwd = getcwd()
# chdir('/')

# from etc import pybar_config as config
# from lib_pybar.signals import flags

# chdir(oldcwd)

import importlib.util

spec = importlib.util.spec_from_file_location(
    'pybar_config',
    '/etc/pybar_config.py'
)

pybar_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pybar_config)

# print(pybar_config.config)
config = pybar_config.config
