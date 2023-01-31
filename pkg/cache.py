from urllib.request import urlretrieve
from pathlib import Path

from . import consts

def get(src, cache_name):
    cached = consts.CACHE_SOURCES / cache_name
    
    if cached.exists():
        return cached

    urlretrieve(src, cached)

    return cached
    
    
