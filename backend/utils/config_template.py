import os
import sys
from pathlib import Path

MOVEUP_COUNT = 2 # When you use the config, specify the number of directiores to move up to the root directory.
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = Path(CURRENT_DIR).parents[MOVEUP_COUNT - 1]

util_dir = ROOT_DIR / 'backend' / 'utils'
# Or to make things cleaner, use util_dir as below. Just each .parent. takes you one directory up.
util_dir = Path(os.path.join(os.path.dirname(__file__))).parent.joinpath('utils')
sys.path.append(str(util_dir))

from AppConfig import AppConfig
config = AppConfig()

# Print all config values
config.print_config()

# Get a specific configuration value
print(config.get("frontend", "host"))

# Set a new configuration value
config.set("frontend", "host", "localhost")