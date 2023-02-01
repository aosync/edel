import sys
import os
from pkg import perms

perms.drop()

from pkg import package
from pkg import consts
from pkg.exceptions import *
from cli import debug
from cli import install
from cli import remove
from cli import autoremove
from cli import checksums
from cli import listpkg

try:
    if sys.argv[1] == 'debug':
        debug.debug(sys.argv[1:])
    elif sys.argv[1] == 'install':
        install.install(sys.argv[1:])
    elif sys.argv[1] == 'remove':
        remove.remove(sys.argv[1:])
    elif sys.argv[1] == 'autoremove':
        autoremove.autoremove(sys.argv[1:])
    elif sys.argv[1] == 'checksums':
        checksums.checksums(sys.argv[1:])
    elif sys.argv[1] == 'list':
        listpkg.packages(sys.argv[1:])
    elif sys.argv[1] == 'explicit':
        listpkg.explicit(sys.argv[1:])
    elif sys.argv[1] == 'orphaned':
        listpkg.orphaned(sys.argv[1:])
except PkgException as e:
    print('edel: %s' % e)
    sys.exit(1)
