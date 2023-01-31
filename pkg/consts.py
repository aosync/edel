from . import repository

import os
from pathlib import Path

# PID of the program instance, used to create build paths
PID = os.getpid()

def bldid():
    """Gives the build id of the next build, this
       can be used to prevent collisions between build
       names"""

    i = bldid.i

    bldid.i += 1

    return i
bldid.i = 0

# Path to the root into which packages should be managed
# setting this to a non-default value is useful to bootstrap
# a system for example
ROOT = Path(os.environ.get('EDEL_ROOT', '/')).resolve()

# Path to the installed package repository
INSTALLED_PATH = os.environ.get('EDEL_INSTALLED', '/var/installed')

# Repository of installed packages
INSTALLED = repository.Repository([INSTALLED_PATH])

# List of paths to the user specified repositories
REPOS_PATHS = os.environ.get('EDEL_REPOS', '').split(':')

# Repositories
REPOS = repository.Repository(
    REPOS_PATHS + [INSTALLED_PATH]
)

# Path to the cache
CACHE = Path(
    os.environ.get('XDG_CACHE_HOME', os.environ['HOME'] + '/.cache/edel')
).resolve()

# Path the directory holding sources
CACHE_SOURCES = CACHE / 'sources'

# Create the cache and cache sources
CACHE_SOURCES.mkdir(parents=True, exist_ok=True)
