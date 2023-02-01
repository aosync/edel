from pkg import package
from pkg import consts
def checksums(argv):
    path = argv[1] if len(argv) >= 2 else '.'

    # Resolve the package
    pkg = consts.REPOS.resolve(path)
    
    # Make the checksums
    pkg.make_checksums()
