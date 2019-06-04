import sys

from src import configurator, shared, steps
from src.steps import files, covers, publish
from src import data as _data

def help():
    message = """You'll be asked about several things.
The format used to ask stuff is the following:
    property[=default]: (enter a value here)
(The [=default] may be ommitted)
If a default value exists, simply press enter without typing anything
to use the default value.

Off you go!
"""
    print(message)

def main(args):
    # getting config
    config = configurator.wizard(configfile=args.config, write=True, no_auto_json=args.no_auto_json)
    # showing help
    if config.get('options/show-help'):
        help()
    # getting user data, initiating Utils & Schemer
    utils = shared.Utils(config)
    data = _data.get(config, utils)
    schemes = shared.Schemer(config, data)

    # renaming (obligatory step)
    renamed = files.rename(config, data)
    if not renamed:
        sys.exit()

    # metadata
    files.metadata(config, data)
