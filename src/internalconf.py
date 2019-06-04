import os
import re

SCHEME_FILTERS = ["slug"]
CONFIG_TYPES = {
    "paths"                : {
        "renamed": {
            "videos"       : str,
            "audios"       : str,
            "covers"       : str,
            "covers-lowres": str,
            "project-files": str,
            "descriptions" : str,
        },
        "files"  : {
            "videos"       : str,
            "audios"       : str,
            "covers"       : str,
            "covers-lowres": str,
            "project-files": str,
            "descriptions" : str,
        },
        "misc"   : {
            "track_data_file": str
        },
        "ftp"    : {
            "videos": str,
            "audios": str,
            "covers": str
        }
    },
    "titles"               : {
        "track" : str,
        "single": str,
        "remix" : str,
        "ep"    : str,
        "album" : str,
        "videos": str
    },
    "defaults"             : {
        "artist"            : str,
        "covers-description": str
    },
    "options"              : {
        "automatic"          : {
            "recover"    : bool,
            "open-dirs"  : bool,
            "create-dirs": bool,
        },
        "show-help"          : bool,
        "contract-rename-map": bool,
        "confirm"            : {
            "track-title"   : bool,
            "track-number"  : bool,
            'rename-tracks' : bool,
            "apply-metadata": bool,
        }
    },
    "description-languages": list,
    "various-artists"      : {
        "threshold"   : str,
        "separator"   : str,
        "default-name": str,
        "ask"         : bool
    }
}

# cfgwiz = config wizard
CFGWIZ_TRUES = 'True true yes on'.split(' ')
CFGWIZ_FALSES = 'False false no off'.split(' ')
CFGWIZ_LISTS = re.compile('\[?(?:([^,]+,))+\]?')

LOG_FORMATS = {
    'extended': "[{levelname:>8}@{module}.{funcName}:{lineno}] {message}",
    'basic'   : "[{levelname:^8}] {message}"
}

COVER_ART_FORMATS = ['wide', 'square']

NUMERIC_LOG_LEVELS = {
    0:'FATAL',
    1:'ERROR',
    2:'WARNING',
    3:'INFO',
    4:'DEBUG',
}

LATEST_TRACKDATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'latest.json')