from pkg import consts

def orphaned(argv):
    orphaned = consts.INSTALLED.orphaned()
    for pkg in orphaned:
        print(pkg)
