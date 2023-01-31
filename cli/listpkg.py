from pkg import consts

def packages(argv):
    pkgs = consts.INSTALLED.packages()
    for pkg in pkgs:
        print(pkg.name)

def explicit(argv):
    pkgs = consts.INSTALLED.packages()

    # Filter out only explicitly installed packages
    pkgs = [pkg for pkg in pkgs if pkg.explicit()]
    
    # Print them
    for pkg in pkgs:
        print(pkg.name)

def orphaned(argv):
    orphaned = consts.INSTALLED.orphaned()
    for pkg in orphaned:
        print(pkg)
