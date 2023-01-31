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
INSTALLED_PATH = os.environ.get('EDEL_INSTALLED', '/usr/installed')

# Repository of installed packages
INSTALLED = repository.Repository([INSTALLED_PATH])

# List of paths to the user specified repositories
REPOS_PATHS = os.environ.get('EDEL_REPOS', '/usr/ports').split(':')

# Repositories
REPOS = repository.Repository(
    REPOS_PATHS + [INSTALLED_PATH]
)

# Path to the cache, this is hardcoded (bad) because I don't
# know how to properly manage the different users involved in
# building, and for example knowing if a variable is defined for
# that user
CACHE = Path(
    os.environ['HOME'] + '/.cache/edel'
).resolve()

# Path the directory holding sources
CACHE_SOURCES = CACHE / 'sources'

# Create the cache and cache sources
CACHE_SOURCES.mkdir(parents=True, exist_ok=True)
